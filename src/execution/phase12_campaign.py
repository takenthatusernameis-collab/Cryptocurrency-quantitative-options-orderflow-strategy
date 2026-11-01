"""Phase 12 Campaign Orchestrator for live readiness."""
from __future__ import annotations

import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.ingestion.live_adapters import LiveAdapterManager
from src.execution.oms import OMS
from src.execution.reconciliation import ReconciliationEngine
from src.risk.live_capital_gate import LiveCapitalGatekeeper
from src.risk.pre_post_trade_risk import PrePostTradeRisk
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> Optional[str]:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


class Phase12Campaign:
    def __init__(self, symbols: Tuple[str, ...] = ("BTC", "ETH"), seed: int = 42,
                 venues: Tuple[str, ...] = ("deribit", "okx", "binance"),
                 paper_only: bool = True):
        self.symbols = tuple(symbols)
        self.seed = int(seed)
        self.venues = tuple(venues)
        self.paper_only = bool(paper_only)
        self.outdir = Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)

    def run(self) -> Dict[str, Any]:
        sha = _git_sha()
        # Adapters
        mgr = LiveAdapterManager(venues=list(self.venues), paper_only=self.paper_only)
        mgr.connect_all()
        mgr.heartbeat_all()
        ad_rep = mgr.generate_report()
        ad_rep["git_sha"] = sha
        ad_rep["symbols"] = list(self.symbols)
        ad_rep["seed"] = int(self.seed)

        # OMS
        oms = OMS()
        orders = []
        for i, sym in enumerate(self.symbols):
            o = oms.create_order(venue=self.venues[i % len(self.venues)], symbol=sym, side="buy", qty=0.01, price=65000.0)
            orders.append(o)
            oms.accept(o.client_order_id, f"v-{o.client_order_id}")
            oms.fill(o.client_order_id, 0.01, 65000.5, partial=False)
        oms_rep = oms.generate_report()
        oms_rep["git_sha"] = sha
        oms_rep["symbols"] = list(self.symbols)
        oms_rep["seed"] = int(self.seed)

        # Reconciliation
        rec = ReconciliationEngine(tolerance=1e-6)
        internal_trades = [{"fill_id": "f1"}] * len(orders)
        venue_trades = [{"fill_id": "f1"}] * len(orders)
        rec_rep = rec.generate_report(internal_trades=internal_trades, venue_trades=venue_trades)
        rec_rep["git_sha"] = sha
        rec_rep["symbols"] = list(self.symbols)
        rec_rep["seed"] = int(self.seed)

        # Capital gate
        cap = LiveCapitalGatekeeper(paper_only=self.paper_only)
        for sym in self.symbols:
            cap.check_allocation({"symbol": sym, "notional": 50000.0}, {"total_notional": 100000.0, "drawdown_pct": 0.01, "leverage": 1.2})
        cap_rep = cap.generate_report()
        cap_rep["git_sha"] = sha
        cap_rep["symbols"] = list(self.symbols)
        cap_rep["seed"] = int(self.seed)

        # Pre/post trade risk
        ppr = PrePostTradeRisk()
        for sym in self.symbols:
            ppr.pre_trade({"delta": 0.1, "vega": 10, "gamma": 1, "liquidity": 0.5, "dte": 30}, {})
            ppr.post_trade({"slippage_bps": 2.0}, {})
        ppr.heartbeat_latency_check(50.0)
        ppr_rep = ppr.generate_report()
        ppr_rep["git_sha"] = sha
        ppr_rep["symbols"] = list(self.symbols)
        ppr_rep["seed"] = int(self.seed)

        paths = []
        for name, rep in [
            ("LIVE_ADAPTERS_REPORT", ad_rep),
            ("OMS_LIFECYCLE_REPORT", oms_rep),
            ("RECONCILIATION_REPORT", rec_rep),
            ("LIVE_CAPITAL_GATE_REPORT", cap_rep),
            ("PREPOST_TRADE_RISK_REPORT", ppr_rep),
        ]:
            p_json = self.outdir / f"{name}.json"
            p_md = self.outdir / f"{name}.md"
            assert_json_valid(rep)
            p_json.write_text(json.dumps(rep, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
            md = f"# {name}\n\n- Timestamp: {rep.get('timestamp')}\n- Seed: {rep.get('seed')}\n- Git SHA: {rep.get('git_sha')}\n- Symbols: {rep.get('symbols')}\n- Paper Only: {self.paper_only}\n"
            p_md.write_text(md, encoding="utf-8")
            paths.extend([str(p_json), str(p_md)])

        master = {
            "timestamp": _utc_now(),
            "git_sha": sha,
            "seed": int(self.seed),
            "symbols": list(self.symbols),
            "venues": list(self.venues),
            "paper_only": bool(self.paper_only),
            "counts": {
                "orders_created": len(orders),
                "adapters_connected": len(mgr.adapters),
            },
            "artifacts": paths,
        }
        master = serialize_metrics_strict(master)
        assert_json_valid(master)
        (self.outdir / "PHASE12_LIVE_READINESS_REPORT.json").write_text(json.dumps(master, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        (self.outdir / "PHASE12_LIVE_READINESS_REPORT.md").write_text(f"# PHASE12_LIVE_READINESS_REPORT\n\n{json.dumps(master, indent=2)}\n", encoding="utf-8")
        paths.extend([str(self.outdir / "PHASE12_LIVE_READINESS_REPORT.json"), str(self.outdir / "PHASE12_LIVE_READINESS_REPORT.md")])
        return {"artifacts": paths, "master": master}
