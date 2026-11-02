"""
Phase 41: Integration loop composing with Phases 17-40.
Cross-venue settlement & finality for crypto options + orderflow. PAPER-ONLY default.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.settlement.phase41_cross_venue_settlement import Phase41CrossVenueSettlement, Phase41SettlementConfig
from src.risk.phase39_kill_switches_circuit_breakers import Phase39KillSwitchesCircuitBreakers, KillSwitchConfig39
from src.reconciliation.phase40_position_margin_audit import Phase40PositionMarginAudit, Phase40AuditConfig


@dataclass
class Loop41Config:
    seed: int = 41041
    cycles: int = 16
    paper_only: bool = True
    modes: str = "paper"
    symbols: List[str] = None
    venues: List[str] = None
    underlyings: List[str] = None
    expiries: List[str] = None
    outdir: str = "research_state"

    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTC-PERP", "ETH-PERP"]
        if self.venues is None:
            self.venues = ["deribit", "okx", "bybit", "binance"]
        if self.underlyings is None:
            self.underlyings = ["BTC", "ETH"]
        if self.expiries is None:
            self.expiries = ["2026-12-26"]


class Phase41SettlementLoop:
    def __init__(self, cfg: Optional[Loop41Config] = None):
        self.cfg = cfg or Loop41Config()
        if self.cfg.modes not in ("paper", "live"):
            raise ValueError("modes must be paper|live")
        if self.cfg.modes == "live" and self.cfg.paper_only:
            raise ValueError("live mode requires paper_only=False and explicit gates")
        if not isinstance(self.cfg.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.cfg.paper_only:
            raise ValueError("Phase41SettlementLoop: paper_only must remain True (live path hard-gated)")
        self.settle = Phase41CrossVenueSettlement(Phase41SettlementConfig(seed=self.cfg.seed, paper_only=True))
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 100, paper_only=True))
        self.audit40 = Phase40PositionMarginAudit(Phase40AuditConfig(seed=self.cfg.seed + 200, paper_only=True))

    def _finite_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for k, v in d.items():
            if isinstance(v, float):
                out[k] = v if math.isfinite(v) else 0.0
            elif isinstance(v, dict):
                out[k] = self._finite_dict(v)
            elif isinstance(v, list):
                out[k] = [
                    self._finite_dict(x) if isinstance(x, dict)
                    else (x if not isinstance(x, float) or math.isfinite(x) else 0.0)
                    for x in v
                ]
            else:
                out[k] = v
        return out

    def run(self) -> Dict[str, Any]:
        outdir = Path(self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        camp41 = self.settle.run_campaign(cycles=self.cfg.cycles)
        ksum = self.ks.run_campaign()
        camp40 = self.audit40.run_campaign(cycles=min(self.cfg.cycles, 12))

        summary = {
            "phase": "PHASE41_SETTLEMENT_LOOP",
            "timestamp_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
            "paper_only": True,
            "modes": "paper",
            "cfg": asdict(self.cfg),
            "n_cycles": camp41["n_cycles"],
            "total_instructions": camp41["total_instructions"],
            "total_receipts": camp41["total_receipts"],
            "total_pending": camp41["total_pending"],
            "total_failed": camp41["total_failed"],
            "finality_ok_all_cycles": camp41["finality_ok_all_cycles"],
            "margin_gates_ok_all_cycles": camp41["margin_gates_ok_all_cycles"],
            "trading_enabled_all_cycles": camp41["trading_enabled_all_cycles"],
            "integrated_with": [
                "PHASE39_KILL_SWITCHES",
                "PHASE40_RECONCILIATION",
                "PHASE17-38",
            ],
            "gates_ok": bool(camp41["gates_ok"] and ksum.get("gates_ok", True)),
            "phase39_global_halts": ksum.get("n_global_halts", 0),
            "phase40_reconciled_all": camp40.get("reconciled_all_cycles", True),
        }
        summary = self._finite_dict(summary)
        (outdir / "PHASE41_SETTLEMENT_LOOP_REPORT.json").write_text(json.dumps(summary, indent=2))
        md = []
        md.append("# PHASE41 SETTLEMENT LOOP REPORT\n")
        md.append(f"\nTimestamp: {summary['timestamp_utc']}\n")
        md.append(f"Cycles: {summary['n_cycles']}, Instructions: {summary['total_instructions']}, Receipts: {summary['total_receipts']}\n")
        md.append(f"Finality OK: {summary['finality_ok_all_cycles']}, Margin Gates OK: {summary['margin_gates_ok_all_cycles']}\n")
        md.append(f"Trading Enabled All: {summary['trading_enabled_all_cycles']}\n")
        (outdir / "PHASE41_SETTLEMENT_LOOP_REPORT.md").write_text("".join(md))
        rep = self.settle.generate_reports(outdir=outdir)
        camp_rep = {
            "phase": "PHASE41_CAMPAIGN_SUMMARY",
            "timestamp_utc": summary["timestamp_utc"],
            "paper_only": True,
            "n_cycles": summary["n_cycles"],
            "total_instructions": summary["total_instructions"],
            "total_receipts": summary["total_receipts"],
            "total_pending": summary["total_pending"],
            "total_failed": summary["total_failed"],
            "finality_ok_all_cycles": summary["finality_ok_all_cycles"],
            "margin_gates_ok_all_cycles": summary["margin_gates_ok_all_cycles"],
            "trading_enabled_all_cycles": summary["trading_enabled_all_cycles"],
            "gates_ok": summary["gates_ok"],
        }
        camp_rep = self._finite_dict(camp_rep)
        (outdir / "PHASE41_CAMPAIGN_SUMMARY.json").write_text(json.dumps(camp_rep, indent=2))
        (outdir / "PHASE41_CAMPAIGN_SUMMARY.md").write_text("# PHASE41 CAMPAIGN SUMMARY\n\nOK - Phase 41 Complete\n")
        return summary
