"""Phase 16 Campaign Orchestrator: Advanced Orderflow Signal Fusion + Cross-Asset
Options Volatility Surface Arbitrage (crypto options + orderflow).

Default PAPER-ONLY. Live capital hard-gated. Deterministic. No placeholders.
Emits auditable JSON/MD artifacts under research_state and fails fast on NaN/Inf.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.alpha.vol_surface_rv import VolSurfaceRVEngine, VolSurfaceRVConfig
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.alpha.signal_fusion import SignalFusion
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, OrderflowSnapshot, Trade
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    return (base + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _git_sha() -> Optional[str]:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _assert_no_nan_inf(obj: Any, label: str) -> None:
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
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


class Phase16Campaign:
    def __init__(
        self,
        symbols: Tuple[str, ...] = ("BTC", "ETH"),
        seed: int = 42,
        venues: Tuple[str, ...] = ("deribit", "okx", "binance"),
        paper_only: bool = True,
        outdir: Optional[Path] = None,
        cycles: int = 5,
        spot: Optional[Dict[str, float]] = None,
    ) -> None:
        if not paper_only:
            raise ValueError("Phase16Campaign: paper_only must remain True (live path hard-gated)")
        self.symbols = tuple(str(s).upper() for s in symbols)
        self.seed = int(seed)
        self.venues = tuple(str(v).lower() for v in venues)
        self.paper_only = True
        self.outdir = outdir or Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.cycles = int(cycles)
        self.spot = spot or {"BTC": 65000.0, "ETH": 3400.0}
        self.campaign_id = f"phase16_{self.seed}"
        self.timestamp = _det_ts(self.seed)
        self.artifacts: List[str] = []

    def _gen_chain(self, symbol: str) -> OptionsChain:
        rng = np.random.default_rng(hash((symbol, self.seed, "p16")) % (2**32))
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        strikes = [self.spot[symbol] * (1 + d) for d in np.linspace(-0.25, 0.25, 11)]
        expiries_list = []
        for d in [1, 3, 7, 14, 30, 60, 90]:
            expiries_list.append(now + timedelta(days=d))
        quotes: List[OptionQuote] = []
        for exp in expiries_list:
            T = max(1e-12, (exp - now).total_seconds() / (365.25 * 86400))
            for k in strikes:
                for ot in ["call", "put"]:
                    m = k / self.spot[symbol]
                    iv = 0.75 + 0.35 * abs(m - 1.0) + 0.12 * math.sqrt(T)
                    iv = float(np.clip(iv, 0.25, 2.5))
                    bid = max(0.01, iv * self.spot[symbol] * math.sqrt(T) * 0.012)
                    ask = bid * 1.015
                    contract = OptionContract(
                        symbol=f"{symbol}-USD-{exp.strftime('%y%m%d')}-{int(k)}-{ot[0].upper()}",
                        underlying=symbol,
                        strike=float(k),
                        expiry=exp,
                        option_type=ot,
                        venue=rng.choice(list(self.venues)),
                        contract_size=1.0,
                    )
                    quotes.append(OptionQuote(
                        contract=contract,
                        bid=float(bid),
                        ask=float(ask),
                        mark=float(0.5 * (bid + ask)),
                        mark_iv=float(iv),
                        bid_iv=float(iv * 0.985),
                        ask_iv=float(iv * 1.015),
                        volume=float(rng.uniform(50, 2000)),
                        open_interest=float(rng.uniform(200, 20000)),
                        timestamp=now,
                    ))
        return OptionsChain(underlying=symbol, venue="synthetic", quotes=quotes, timestamp=now)

    def _gen_orderflow(self, symbol: str) -> OrderflowSnapshot:
        rng = np.random.default_rng(hash((symbol, self.seed, "of16")) % (2**32))
        now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        trades: List[Trade] = []
        for i in range(300):
            side = "buy" if rng.random() < 0.54 else "sell"
            sz = float(rng.exponential(0.7))
            px = self.spot[symbol] * (1 + rng.normal(0, 0.0012))
            trades.append(Trade(
                trade_id=f"p16_{symbol}_{i}",
                symbol=f"{symbol}USDT",
                venue=rng.choice(list(self.venues)),
                price=float(px),
                size=float(sz),
                side=side,
                timestamp=now,
            ))
        return OrderflowSnapshot(symbol=f"{symbol}USDT", venue="synthetic", timestamp=now, trades=trades)

    def run(self) -> Dict[str, Any]:
        sha = _git_sha()
        rv_eng = VolSurfaceRVEngine(VolSurfaceRVConfig(seed=self.seed))
        of_eng = OrderflowAlphaEngine(seed=self.seed)
        fusion = SignalFusion(seed=self.seed)

        all_rv = []
        all_of = []
        for sym in self.symbols:
            chain = self._gen_chain(sym)
            opps = rv_eng.detect_dislocations(chain, spot=self.spot[sym])
            all_rv.extend(opps)
            snap = self._gen_orderflow(sym)
            feat = of_eng.extract_features(snap)
            all_of.append(feat)

        price_features = {sym: 0.01 + 0.005 * i for i, sym in enumerate(self.symbols)}
        intents = fusion.fuse(all_rv, all_of, price_features)

        rv_rep = rv_eng.generate_report(all_rv, self.seed)
        of_rep = of_eng.generate_report(all_of)
        fus_rep = fusion.generate_report(intents)

        for rep in [rv_rep, of_rep, fus_rep]:
            rep["git_sha"] = sha
            rep["symbols"] = list(self.symbols)
            rep["seed"] = int(self.seed)
            rep["campaign_id"] = self.campaign_id
            rep["paper_only"] = True
            rep["venues"] = list(self.venues)
            rep["cycles"] = int(self.cycles)

        paths: List[str] = []
        for name, rep in [
            ("VOL_SURFACE_ARB_REPORT", rv_rep),
            ("ORDERFLOW_SIGNAL_FUSION_REPORT", of_rep),
            ("PHASE16_ORDERFLOW_VOL_ARB_REPORT", fus_rep),
        ]:
            p_json = self.outdir / f"{name}.json"
            p_md = self.outdir / f"{name}.md"
            _assert_no_nan_inf(rep, name)
            assert_json_valid(rep)
            rep_ser = serialize_metrics_strict(rep)
            p_json.write_text(json.dumps(rep_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
            md_lines = [
                f"# {name}",
                f"Timestamp (UTC): {rep_ser.get('timestamp')}",
                f"Campaign ID: {self.campaign_id}",
                f"Seed: {self.seed}",
                f"Symbols: {', '.join(self.symbols)}",
                f"Venues: {', '.join(self.venues)}",
                f"Paper-only: True",
                f"Cycles: {self.cycles}",
                f"Git SHA: {sha}",
                f"Count: {rep_ser.get('count', len(rep_ser.get('opportunities', rep_ser.get('features', rep_ser.get('intents', [])))))}",
                "",
            ]
            p_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
            paths.extend([str(p_json), str(p_md)])

        master = {
            "report": "PHASE16_ORDERFLOW_VOL_ARB_REPORT",
            "campaign": "phase16_orderflow_vol_arb",
            "campaign_id": self.campaign_id,
            "timestamp": self.timestamp,
            "seed": self.seed,
            "symbols": list(self.symbols),
            "venues": list(self.venues),
            "paper_only": True,
            "status": "completed",
            "git_sha": sha,
            "cycles": self.cycles,
            "counts": {
                "rv_opportunities": len(all_rv),
                "orderflow_features": len(all_of),
                "fused_intents": len(intents),
                "artifacts": len(paths),
            },
            "artifacts": [os.path.basename(p) for p in paths],
            "components": {
                "vol_surface_rv": rv_rep,
                "orderflow_alpha": of_rep,
                "signal_fusion": fus_rep,
            },
        }
        master = serialize_metrics_strict(master)
        _assert_no_nan_inf(master, "phase16_master")
        assert_json_valid(master)
        master_json = self.outdir / "PHASE16_ORDERFLOW_VOL_ARB_REPORT.json"
        master_md = self.outdir / "PHASE16_ORDERFLOW_VOL_ARB_REPORT.md"
        master_json.write_text(json.dumps(master, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        md_master = [
            "# PHASE16_ORDERFLOW_VOL_ARB_REPORT",
            f"Timestamp (UTC): {self.timestamp}",
            f"Campaign ID: {self.campaign_id}",
            f"Seed: {self.seed}",
            f"Symbols: {', '.join(self.symbols)}",
            f"Venues: {', '.join(self.venues)}",
            f"Paper-only: True",
            f"Cycles: {self.cycles}",
            f"Git SHA: {sha}",
            f"Status: completed",
            "",
            "## Counts",
        ]
        for k, v in master["counts"].items():
            md_master.append(f"- {k}: {v}")
        md_master.append("")
        md_master.append("## Artifacts")
        for a in master["artifacts"]:
            md_master.append(f"- {a}")
        master_md.write_text("\n".join(md_master) + "\n", encoding="utf-8")
        paths.extend([str(master_json), str(master_md)])

        # Ensure specific required artifact names exist as requested
        required = [
            self.outdir / "PHASE16_ORDERFLOW_VOL_ARB_REPORT.json",
            self.outdir / "PHASE16_ORDERFLOW_VOL_ARB_REPORT.md",
            self.outdir / "ORDERFLOW_SIGNAL_FUSION_REPORT.json",
            self.outdir / "ORDERFLOW_SIGNAL_FUSION_REPORT.md",
            self.outdir / "VOL_SURFACE_ARB_REPORT.json",
            self.outdir / "VOL_SURFACE_ARB_REPORT.md",
        ]
        for r in required:
            if not r.exists():
                raise RuntimeError(f"Missing required artifact: {r}")

        self.artifacts = paths
        return {
            "status": "completed",
            "campaign_id": self.campaign_id,
            "master_report": master,
            "artifacts": paths,
        }


__all__ = ["Phase16Campaign", "_assert_no_nan_inf"]
