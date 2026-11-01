"""
Phase 29: Vol Arb Paper Loop (crypto options + orderflow).
Integrates vol arb engine + hedge engine + router/healer/observability.
Production-grade, deterministic, paper-only gated.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
from pathlib import Path

from src.arbitrage.phase29_vol_arb import OptionsVolArbEngine, VolArbConfig
from src.risk.phase29_delta_neutral_hedge import DeltaNeutralHedgeEngine, HedgeConfig
from src.execution.phase24_cross_venue_router import CrossVenueRouter
from src.monitoring.phase18_observability import Phase18Observability
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _assert_finite(obj: Any, label: str = "obj") -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p29l|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p29l_{tag}_{h}"


@dataclass(frozen=True)
class VolArbLoopConfig:
    seed: int = 42
    paper_only: bool = True
    cycles: int = 5
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    enforce_gates: bool = True


class VolArbPaperLoop:
    def __init__(self, config: Optional[VolArbLoopConfig] = None, seed: int = 42):
        self.config = config or VolArbLoopConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("VolArbPaperLoop: paper_only must remain True (live path hard-gated)")
        self.config = VolArbLoopConfig(
            seed=int(self.config.seed),
            paper_only=True,
            cycles=int(self.config.cycles),
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.vol_arb = OptionsVolArbEngine(VolArbConfig(seed=self.seed + 100), seed=self.seed + 100)
        self.hedge = DeltaNeutralHedgeEngine(HedgeConfig(seed=self.seed + 200), seed=self.seed + 200)
        self.router = CrossVenueRouter(seed=self.seed + 30000)
        self.obs = Phase18Observability(seed=self.seed + 40000, paper_only=True)
        self.cycles: List[Dict[str, Any]] = []
        self.fills: List[Dict[str, Any]] = []
        self.tca: List[Dict[str, Any]] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _gen_iv_quotes(self) -> List[Dict[str, Any]]:
        quotes = []
        spots = {"BTC": 65000.0, "ETH": 3500.0, "SOL": 150.0, "XRP": 0.6}
        for und in self.config.underlyings:
            spot = spots[und]
            for exp in ("7D", "30D", "90D"):
                for strike in [spot * 0.9, spot, spot * 1.1]:
                    for opt in ("call", "put"):
                        for vi, v in enumerate(self.config.venues):
                            base_iv = 0.6 if und == "BTC" else 0.8 if und == "ETH" else 1.0
                            # create dislocation
                            bump = (vi - 1) * 0.015  # some venues richer
                            bid_iv = base_iv + bump - 0.01
                            ask_iv = base_iv + bump + 0.01
                            quotes.append(
                                {
                                    "quote_id": self._next_id("q"),
                                    "underlying": und,
                                    "expiry": exp,
                                    "strike": float(strike),
                                    "option_type": opt,
                                    "venue": v,
                                    "bid_iv": float(bid_iv),
                                    "ask_iv": float(ask_iv),
                                    "mid_iv": float((bid_iv + ask_iv) / 2.0),
                                    "volume": float(10 + vi * 5),
                                    "oi": float(100 + vi * 20),
                                    "timestamp": _utc_now(),
                                }
                            )
        return quotes

    def run_cycle(self, cycle_idx: int) -> Dict[str, Any]:
        if cycle_idx < 0:
            raise ValueError("cycle_idx must be >=0")
        quotes = self._gen_iv_quotes()
        self.vol_arb.ingest_iv_quotes(quotes)
        dislocs = self.vol_arb.detect_dislocations()
        sigs = self.vol_arb.build_signals()
        # aggregate greeks
        greeks = {}
        for und in self.config.underlyings:
            greeks[und] = {"delta": float((cycle_idx % 3) - 1) * 10.0, "gamma": float(cycle_idx % 2) * 2.0, "vega": float(cycle_idx % 4) * 100.0}
        self.hedge.update_positions(greeks)
        self.hedge.compute_hedge_state()
        hedges = self.hedge.generate_hedge_orders()
        # route some
        routed = []
        for s in sigs[:2]:
            rd = self.router.route(
                venue_list=list(self.config.venues),
                symbol=f"{s.underlying}-OPTION",
                notional_usd=float(s.expected_pnl_usd * 10),
                urgency="high",
            )
            routed.append(rd)
        # fills/tca
        for s in sigs[:2]:
            self.fills.append({"cycle": cycle_idx, "signal_id": s.signal_id, "filled": True, "paper_only": True})
            self.tca.append({"cycle": cycle_idx, "signal_id": s.signal_id, "slippage_bps": 1.2, "fill_rate": 0.95})
        self.hedge.attribute_pnl(arb_pnl=float(sum(s.expected_pnl_usd for s in sigs[:3])), hedge_pln=0.0, slippage=float(len(self.tca) * 1.2))
        # fix typo
        self.hedge.pnl_attribution = {"arb_pnl": float(sum(s.expected_pnl_usd for s in sigs[:3])), "hedge_pnl": 0.0, "slippage": float(len(self.tca) * 1.2), "net_pnl": float(sum(s.expected_pnl_usd for s in sigs[:3]) - len(self.tca) * 1.2)}
        for k, v in self.hedge.pnl_attribution.items():
            if not math.isfinite(v):
                raise ValueError(f"non-finite pnl {k}")
        res = {
            "cycle": cycle_idx,
            "dislocations": len(dislocs),
            "signals": len(sigs),
            "hedge_orders": len(hedges),
            "routed": len(routed),
            "fills": len([f for f in self.fills if f["cycle"] == cycle_idx]),
            "tca_entries": len([t for t in self.tca if t["cycle"] == cycle_idx]),
            "net_pnl": self.hedge.pnl_attribution["net_pnl"],
            "paper_only": True,
            "timestamp": _utc_now(),
        }
        _assert_finite(res, f"cycle_{cycle_idx}")
        self.cycles.append(res)
        self.obs.record_metric("phase29_cycle", res)
        return res

    def run(self) -> Dict[str, Any]:
        results = []
        for i in range(int(self.config.cycles)):
            results.append(self.run_cycle(i))
        rep = {
            "phase": "29_vol_arb_paper_loop",
            "timestamp": _utc_now(),
            "config": asdict(self.config),
            "cycles": results,
            "totals": {
                "dislocations": sum(r["dislocations"] for r in results),
                "signals": sum(r["signals"] for r in results),
                "hedge_orders": sum(r["hedge_orders"] for r in results),
                "fills": len(self.fills),
                "tca": len(self.tca),
                "net_pnl": float(self.hedge.pnl_attribution.get("net_pnl", 0.0)),
            },
            "status": "ok",
            "paper_only": True,
        }
        _assert_finite(rep, "loop_report")
        return rep

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        rep = self.run()
        pjson = Path(outdir) / "PHASE29_VOL_ARB_PAPER_LOOP_REPORT.json"
        pmd = Path(outdir) / "PHASE29_VOL_ARB_PAPER_LOOP_REPORT.md"
        pjson.write_text(json.dumps(rep, indent=2))
        pmd.write_text(f"# PHASE29_VOL_ARB_PAPER_LOOP_REPORT\n\nTimestamp: {rep['timestamp']}\nCycles: {len(rep['cycles'])}\nSignals: {rep['totals']['signals']}\nFills: {rep['totals']['fills']}\nNet PnL: {rep['totals']['net_pnl']}\nStatus: {rep['status']}\n")
        return rep
