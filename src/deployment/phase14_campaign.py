"""Phase 14 Campaign Orchestrator for live-capital deployment, multi-strategy
portfolio orchestration & real exchange execution (crypto options + orderflow).

Default PAPER-ONLY. Live capital hard-gated.
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.capital import CapitalAllocator, default_allocation_config
from src.portfolio import PortfolioOrchestrator, default_orchestration_config
from src.execution.live_execution_router import LiveExecutionRouter, default_router_config
from src.attribution import PerformanceAttributor, default_attribution_config
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _deterministic_iso(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    return (base + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _write_json_artifact(path: Path, data: Dict[str, Any]) -> str:
    serialized = serialize_metrics_strict(data)
    content = json.dumps(serialized, ensure_ascii=False, indent=2, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


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


class Phase14Campaign:
    def __init__(
        self,
        symbols: Tuple[str, ...] = ("BTC", "ETH"),
        seed: int = 42,
        venues: Tuple[str, ...] = ("deribit", "okx", "binance"),
        paper_only: bool = True,
        outdir: Optional[Path] = None,
    ) -> None:
        if not paper_only:
            raise ValueError("Phase14Campaign: paper_only must remain True (live capital hard-gated)")
        self.symbols = tuple(str(s).upper() for s in symbols)
        self.seed = int(seed)
        self.venues = tuple(str(v).lower() for v in venues)
        self.paper_only = True  # enforce
        self.outdir = outdir or Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)
        self.campaign_id = f"phase14_{self.seed}"
        self.timestamp = _deterministic_iso(self.seed)
        self.artifacts: List[str] = []

    def run(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        git_sha = os.environ.get("GIT_SHA") or "unknown"
        spot = {s: 65000.0 + (1000.0 if s == "ETH" else 0.0) for s in self.symbols}

        # 1) Capital allocator
        alloc_cfg = default_allocation_config()
        alloc_cfg.paper_only = True
        allocator = CapitalAllocator(config=alloc_cfg, seed=self.seed)
        strategies = ["options_vol", "orderflow_momentum", "basis_carry"]
        allocations = allocator.allocate(list(strategies), list(self.venues), list(self.symbols), current_drawdown_pct=0.02)
        alloc_rep = allocator.generate_report(allocations)
        _assert_no_nan_inf(alloc_rep, "capital_allocation_report")
        assert_json_valid(alloc_rep)
        alloc_path = _write_json_artifact(self.outdir / "CAPITAL_ALLOCATION_REPORT.json", alloc_rep)
        self.artifacts.append(alloc_path)
        results["capital_allocation"] = alloc_rep
        results["capital_allocation_artifact"] = alloc_path

        # 2) Portfolio orchestrator
        orch_cfg = default_orchestration_config()
        orch_cfg.paper_only = True
        orchestrator = PortfolioOrchestrator(config=orch_cfg, seed=self.seed)
        strat_positions = {
            "options_vol": [{"symbol": "BTC", "venue": "deribit", "side": "long", "quantity": 0.5}],
            "orderflow_momentum": [{"symbol": "ETH", "venue": "okx", "side": "long", "quantity": 10.0}],
            "basis_carry": [{"symbol": "BTC", "venue": "binance", "side": "short", "quantity": 0.2}],
        }
        positions = orchestrator.aggregate_positions(strat_positions, spot)
        port_rep = orchestrator.generate_report(positions, spot)
        _assert_no_nan_inf(port_rep, "portfolio_orchestration_report")
        assert_json_valid(port_rep)
        port_path = _write_json_artifact(self.outdir / "PORTFOLIO_ORCHESTRATION_REPORT.json", port_rep)
        self.artifacts.append(port_path)
        results["portfolio_orchestration"] = port_rep
        results["portfolio_orchestration_artifact"] = port_path

        # 3) Live execution router (paper-only)
        rtr_cfg = default_router_config()
        rtr_cfg.paper_only = True
        rtr_cfg.enable_live = False
        router = LiveExecutionRouter(config=rtr_cfg, seed=self.seed)
        intents = [
            {"symbol": "BTC", "side": "buy", "quantity": 0.1, "venue": "deribit"},
            {"symbol": "ETH", "side": "buy", "quantity": 2.0, "venue": "okx"},
            {"symbol": "BTC", "side": "sell", "quantity": 0.05, "venue": "binance"},
        ]
        routes = router.route_orders(intents, spot)
        exec_rep = router.generate_report(routes)
        _assert_no_nan_inf(exec_rep, "live_execution_report")
        assert_json_valid(exec_rep)
        exec_path = _write_json_artifact(self.outdir / "LIVE_EXECUTION_REPORT.json", exec_rep)
        self.artifacts.append(exec_path)
        results["live_execution"] = exec_rep
        results["live_execution_artifact"] = exec_path

        # 4) Performance attribution
        attr_cfg = default_attribution_config()
        attr_cfg.paper_only = True
        attributor = PerformanceAttributor(config=attr_cfg, seed=self.seed)
        attr_rep = attributor.generate_report(
            by_strategy={"options_vol": 12500.0, "orderflow_momentum": 8200.0, "basis_carry": 3400.0},
            by_venue={"deribit": 9800.0, "okx": 9200.0, "binance": 5100.0},
            by_instrument={"BTC_OPTION": 14200.0, "ETH_PERP": 8200.0, "BTC_FUTURE": 1700.0},
            fees=245.0,
            slippage=156.0,
        )
        _assert_no_nan_inf(attr_rep, "performance_attribution_report")
        assert_json_valid(attr_rep)
        attr_path = _write_json_artifact(self.outdir / "PERFORMANCE_ATTRIBUTION_REPORT.json", attr_rep)
        self.artifacts.append(attr_path)
        results["performance_attribution"] = attr_rep
        results["performance_attribution_artifact"] = attr_path

        # 5) Master report
        master = {
            "report": "PHASE14_LIVE_CAPITAL_REPORT",
            "campaign_id": self.campaign_id,
            "timestamp": self.timestamp,
            "seed": self.seed,
            "symbols": list(self.symbols),
            "venues": list(self.venues),
            "paper_only": True,
            "git_sha": git_sha,
            "status": "completed",
            "counts": {
                "allocations": len(allocations),
                "positions": len(positions),
                "routes": len(routes),
                "artifacts": len(self.artifacts),
            },
            "artifacts": [os.path.basename(a) for a in self.artifacts],
            "capital_allocation": alloc_rep,
            "portfolio_orchestration": port_rep,
            "live_execution": exec_rep,
            "performance_attribution": attr_rep,
        }
        master = serialize_metrics_strict(master)
        _assert_no_nan_inf(master, "phase14_master_report")
        assert_json_valid(master)
        master_path = _write_json_artifact(self.outdir / "PHASE14_LIVE_CAPITAL_REPORT.json", master)
        self.artifacts.append(master_path)

        # MD summary
        md_path = self.outdir / "PHASE14_LIVE_CAPITAL_REPORT.md"
        lines = []
        lines.append("# PHASE14_LIVE_CAPITAL_REPORT")
        lines.append(f"Timestamp (UTC): {self.timestamp}")
        lines.append(f"Campaign ID: {self.campaign_id}")
        lines.append(f"Seed: {self.seed}")
        lines.append(f"Symbols: {', '.join(self.symbols)}")
        lines.append(f"Venues: {', '.join(self.venues)}")
        lines.append(f"Paper-only: {self.paper_only}")
        lines.append(f"Git SHA: {git_sha}")
        lines.append(f"Status: completed")
        lines.append("")
        lines.append("## Artifacts")
        for a in self.artifacts:
            lines.append(f"- {os.path.basename(a)}")
        lines.append("")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.artifacts.append(str(md_path))
        results["master_report"] = master
        results["master_report_artifact"] = master_path
        results["md_artifact"] = str(md_path)
        results["artifacts"] = [str(a) for a in self.artifacts]
        results["status"] = "completed"
        return results
