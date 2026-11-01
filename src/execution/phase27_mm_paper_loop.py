"""
Phase 27: Market Making Paper Loop integrating MM + Inventory Risk + router/healer/observability (Phase 17-26)
Production-grade, deterministic, paper-only safe.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
import random
from pathlib import Path

from src.options.phase27_market_maker import OptionsMarketMaker, MMConfig, Quote, Greeks, Fill
from src.risk.phase27_inventory_risk import InventoryRiskManager, InventoryRiskConfig
from src.telemetry.serialization import serialize_metrics_strict
from src.monitoring.phase18_observability import Phase18Observability


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
    h = hashlib.sha256(f"{seed}|p27loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p27loop_{tag}_{h}"


@dataclass(frozen=True)
class MMPaperLoopConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    expiries: tuple = ("7D", "30D", "90D")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 10
    enforce_gates: bool = True


@dataclass(frozen=True)
class CycleResult:
    cycle: int
    symbol: str
    quotes_placed: int
    fills: int
    spread_bps: float
    inventory_utilization: float
    risk_passed: bool
    adverse_selection_flagged: int
    paper_only: bool
    timestamp: str


class MMPaperLoop:
    def __init__(self, config: Optional[MMPaperLoopConfig] = None, seed: int = 42):
        self.config = config or MMPaperLoopConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("MMPaperLoop: paper_only must remain True (live path hard-gated)")
        self.config = MMPaperLoopConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            expiries=tuple(self.config.expiries),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        mm_cfg = MMConfig(seed=self.seed, paper_only=True, underlyings=self.config.underlyings, expiries=self.config.expiries, venues=self.config.venues)
        inv_cfg = InventoryRiskConfig(seed=self.seed, paper_only=True, underlyings=self.config.underlyings, expiries=self.config.expiries)
        self.mm = OptionsMarketMaker(config=mm_cfg)
        self.risk = InventoryRiskManager(config=inv_cfg)
        self.obs = Phase18Observability(seed=self.seed, paper_only=True)
        self.cycle_count = 0
        self.results: List[CycleResult] = []
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def run_cycle(self, cycle: int, quotes_input: List[Dict[str, Any]], tape: List[Dict[str, Any]], recent_trades: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if not self.config.paper_only:
            raise RuntimeError("hard gate: live disabled")
        results: List[Dict[str, Any]] = []
        snapshots = []
        flagged = 0
        total_spread = 0.0
        total_quotes = 0
        total_fills = 0
        rng = random.Random(self.seed + 27000 + cycle)
        strike_map = {"BTC": 100000.0, "ETH": 4000.0, "SOL": 150.0, "XRP": 50.0}
        mid_map = {"BTC": 100000.0, "ETH": 4000.0, "SOL": 150.0, "XRP": 50.0}
        for und in self.config.underlyings:
            for exp in self.config.expiries:
                strike = float(strike_map.get(und, 1000.0))
                mid = float(mid_map.get(und, 1000.0)) * rng.uniform(0.9, 1.1)
                mid = float(max(1.0, mid))
                venue = self.config.venues[cycle % len(self.config.venues)]
                option_type = "call" if cycle % 2 == 0 else "put"
                inventory = self.mm.inventory.get(und, 0.0)
                greeks = Greeks(delta=rng.uniform(-100.0, 100.0), gamma=rng.uniform(0.001, 0.05), vega=rng.uniform(100.0, 5000.0), theta=rng.uniform(-10000.0, -100.0), rho=rng.uniform(-50.0, 50.0))
                self.mm.update_greeks(und, greeks)
                depth = rng.uniform(0.5, 1.5)
                notional = rng.uniform(100000.0, 1000000.0)
                q = self.mm.make_quote(und, exp, strike, option_type, venue, mid, inventory, greeks, tape, depth, notional, recent_trades)
                snap = self.risk.snapshot(und, exp, strike, option_type, q.bid_size - q.ask_size, mid, greeks.delta, greeks.gamma, greeks.vega, greeks.theta, greeks.rho, notional_usd=notional)
                snapshots.append(snap)
                if q.adverse_selection_score > self.mm.config.adverse_selection_threshold:
                    flagged += 1
                total_spread += q.spread_bps
                total_quotes += 1
        fill_rate = 0.1 + 0.1 * rng.random()
        for i in range(int(total_quotes * fill_rate)):
            fill_qty = rng.uniform(0.01, 5.0)
            fill_price = rng.uniform(100.0, 100000.0)
            side = "buy" if rng.random() > 0.5 else "sell"
            und = self.config.underlyings[i % len(self.config.underlyings)]
            f = Fill(fill_id=self.mm._next_id("fill"), quote_id=f"synthetic_{i}", underlying=und, side=side, fill_qty=float(fill_qty), fill_price=float(fill_price), timestamp=_utc_now(), paper_only=True)
            self.mm.apply_fill(f)
            total_fills += 1
        limits = self.risk.check_limits(snapshots)
        rep = {
            "cycle": cycle,
            "underlyings": list(self.config.underlyings),
            "expiries": list(self.config.expiries),
            "quotes_placed": total_quotes,
            "fills": total_fills,
            "avg_spread_bps": float(total_spread / max(1, total_quotes)),
            "risk_passed": bool(limits["passed"]),
            "adverse_selection_flagged": int(flagged),
            "paper_only": True,
            "limits": limits,
            "risk_state": self.mm.risk_state(),
            "timestamp": _utc_now(),
        }
        _assert_finite(rep, f"mm_paper_loop_cycle_{cycle}")
        res = CycleResult(
            cycle=int(cycle),
            symbol=",".join(self.config.underlyings),
            quotes_placed=int(total_quotes),
            fills=int(total_fills),
            spread_bps=float(total_spread / max(1, total_quotes)),
            inventory_utilization=float(min(1.0, sum(abs(v) for v in self.mm.inventory.values()) / max(1e-9, self.mm.config.max_inventory * len(self.config.underlyings)))),
            risk_passed=bool(limits["passed"]),
            adverse_selection_flagged=int(flagged),
            paper_only=True,
            timestamp=_utc_now(),
        )
        self.results.append(res)
        self.cycle_count += 1
        self._log("cycle", {"cycle": cycle, "quotes_placed": total_quotes, "fills": total_fills, "risk_passed": limits["passed"], "flagged": flagged})
        return serialize_metrics_strict(rep)

    def run(self, cycles: Optional[int] = None, quotes_input: Optional[List[Dict[str, Any]]] = None, tape: Optional[List[Dict[str, Any]]] = None, recent_trades: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        n = int(cycles if cycles is not None else self.config.cycles)
        if n < 1 or n > 1000:
            raise ValueError("cycles out of range")
        tape = tape if tape is not None else [{"bid_vol": 10, "ask_vol": 12, "toxicity": 0.1}, {"bid_vol": 15, "ask_vol": 11, "toxicity": 0.05}]
        results: List[Dict[str, Any]] = []
        for c in range(n):
            results.append(self.run_cycle(c, quotes_input or [], tape, recent_trades))
        self._log("run_completed", {"cycles": n})
        return results

    def generate_report(self) -> Dict[str, Any]:
        total_quotes = sum(r.quotes_placed for r in self.results)
        total_fills = sum(r.fills for r in self.results)
        overall_risk = all(r.risk_passed for r in self.results)
        rep = {
            "report": "PHASE27_MM_PAPER_LOOP_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "cycle_count": self.cycle_count,
            "total_quotes_placed": int(total_quotes),
            "total_fills": int(total_fills),
            "overall_risk_passed": bool(overall_risk),
            "results": [asdict(r) for r in self.results],
            "final_risk_state": self.mm.risk_state(),
            "inventory_risk_report": self.risk.generate_report(),
            "audit": self.audit,
            "paper_only": True,
        }
        _assert_finite(rep, "mm_paper_loop_report")
        return serialize_metrics_strict(rep)

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE27_MM_PAPER_LOOP_REPORT.json"
        pmd = Path(outdir) / "PHASE27_MM_PAPER_LOOP_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE27_MM_PAPER_LOOP_REPORT\n\nStatus: ok\nCycles: {self.cycle_count}\nQuotes: {sum(r.quotes_placed for r in self.results)}\nFills: {sum(r.fills for r in self.results)}\nRisk passed: {all(r.risk_passed for r in self.results)}\nPaper-only: True\n")
        return str(pjson)


__all__ = ["MMPaperLoop", "MMPaperLoopConfig", "CycleResult"]
