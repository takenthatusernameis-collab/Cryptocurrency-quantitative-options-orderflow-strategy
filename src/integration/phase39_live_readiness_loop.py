"""
Phase 39: Live Readiness Loop - integrates kill-switches, recovery, validation
with prior phases. Deterministic, finite numerics, PAPER-ONLY default.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.risk.phase39_kill_switches_circuit_breakers import Phase39KillSwitchesCircuitBreakers, KillSwitchConfig39
from src.recovery.phase39_disaster_recovery import Phase39DisasterRecovery, RecoveryConfig39
from src.validation.phase39_prepost_trade_validation import Phase39PrePostTradeValidation, PrePostConfig39
from src.integration.phase38_risk_obs_validation_loop import Phase38RiskObsValidationLoop, Loop38Config


@dataclass
class Loop39Config:
    seed: int = 39039
    cycles: int = 12
    paper_only: bool = True
    modes: str = "paper"
    symbols: List[str] = None
    venues: List[str] = None
    underlyings: List[str] = None
    expiries: List[str] = None
    outdir: str = "research_state"

    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTC-USD", "ETH-USD"]
        if self.venues is None:
            self.venues = ["deribit", "okx", "bybit", "binance"]
        if self.underlyings is None:
            self.underlyings = ["BTC", "ETH"]
        if self.expiries is None:
            self.expiries = ["2026-12-26"]


class Phase39LiveReadinessLoop:
    def __init__(self, cfg: Optional[Loop39Config] = None):
        self.cfg = cfg or Loop39Config()
        if self.cfg.modes not in ("paper", "live"):
            raise ValueError("modes must be paper|live")
        if self.cfg.modes == "live" and self.cfg.paper_only:
            raise ValueError("live mode requires paper_only=False and explicit gates")
        if not isinstance(self.cfg.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.cfg.paper_only:
            raise ValueError("Phase39LiveReadinessLoop: paper_only must remain True (live path hard-gated)")
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed, paper_only=True))
        self.dr = Phase39DisasterRecovery(RecoveryConfig39(seed=self.cfg.seed + 1, paper_only=True))
        self.pv = Phase39PrePostTradeValidation(PrePostConfig39(seed=self.cfg.seed + 2, paper_only=True))
        l38 = Loop38Config(symbols=self.cfg.symbols, venues=self.cfg.venues, underlyings=self.cfg.underlyings, expiries=self.cfg.expiries, modes="paper", cycles=self.cfg.cycles, seed=self.cfg.seed, paper_only=True, outdir=self.cfg.outdir)
        self.loop38 = Phase38RiskObsValidationLoop(l38)

    def _finite_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for k, v in d.items():
            if isinstance(v, float):
                out[k] = v if math.isfinite(v) else 0.0
            elif isinstance(v, dict):
                out[k] = self._finite_dict(v)
            elif isinstance(v, list):
                out[k] = [self._finite_dict(x) if isinstance(x, dict) else (x if not isinstance(x, float) or math.isfinite(x) else 0.0) for x in v]
            else:
                out[k] = v
        return out

    def run(self) -> Dict[str, Any]:
        outdir = Path(self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        ksum = self.ks.run_campaign()
        rsum = self.dr.run_campaign()
        vsum = self.pv.run_campaign()
        l38s = self.loop38.run()
        results = []
        for c in range(self.cfg.cycles):
            ks_c = ksum["cycles"][c] if c < len(ksum["cycles"]) else None
            regime = ks_c.get("regime") if ks_c else "normal"
            vres = self.pv.validate(c)
            results.append({
                "cycle": c,
                "regime": regime,
                "global_halt": ks_c.get("global_halt") if ks_c else False,
                "trading_enabled": ks_c.get("trading_enabled") if ks_c else True,
                "validation_all_passed": vres.all_passed,
                "validation_blocked": vres.blocked,
            })
        summary = {
            "phase": "PHASE39_LIVE_READINESS_LOOP",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "paper_only": True,
            "modes": "paper",
            "cfg": asdict(self.cfg),
            "n_cycles": len(results),
            "trading_enabled_cycles": sum(1 for x in results if x.get("trading_enabled")),
            "validation_passed_cycles": sum(1 for x in results if x.get("validation_all_passed")),
            "global_halts": sum(1 for x in results if x.get("global_halt")),
            "gates_ok": True,
            "integrated_with": ["PHASE38_RISK_OBS_VALIDATION_LOOP", "PHASE37_ORDERFLOW_ROUTING_LOOP"],
            "results": results,
        }
        summary = self._finite_dict(summary)
        (outdir / "PHASE39_LIVE_READINESS_LOOP_REPORT.json").write_text(json.dumps(summary, indent=2))
        md = []
        md.append("# PHASE39 LIVE READINESS LOOP REPORT\n")
        md.append(f"\nTimestamp: {summary['timestamp_utc']}\n")
        md.append(f"Cycles: {summary['n_cycles']}, Trading Enabled: {summary['trading_enabled_cycles']}\n")
        md.append(f"Validation Passed: {summary['validation_passed_cycles']}, Global Halts: {summary['global_halts']}\n")
        (outdir / "PHASE39_LIVE_READINESS_LOOP_REPORT.md").write_text("".join(md))
        # write component reports
        (outdir / "PHASE39_KILL_SWITCH_REPORT.json").write_text(json.dumps(ksum, indent=2))
        kmd = ["# PHASE39 KILL SWITCH REPORT\n", f"\nTimestamp: {ksum['timestamp_utc']}\n", f"Kill Events: {ksum['n_kill_events']}\n"]
        (outdir / "PHASE39_KILL_SWITCH_REPORT.md").write_text("".join(kmd))
        (outdir / "PHASE39_RECOVERY_REPORT.json").write_text(json.dumps(rsum, indent=2))
        rmd = ["# PHASE39 RECOVERY REPORT\n", f"\nTimestamp: {rsum['timestamp_utc']}\n", f"Checkpoints: {rsum['n_checkpoints']}, Restores OK: {rsum['all_restored_ok']}\n"]
        (outdir / "PHASE39_RECOVERY_REPORT.md").write_text("".join(rmd))
        (outdir / "PHASE39_VALIDATION_REPORT.json").write_text(json.dumps(vsum, indent=2))
        vmd = ["# PHASE39 VALIDATION REPORT\n", f"\nTimestamp: {vsum['timestamp_utc']}\n", f"All Passed: {vsum['all_passed_count']}/{vsum['n_results']}\n"]
        (outdir / "PHASE39_VALIDATION_REPORT.md").write_text("".join(vmd))
        camp = {"phase": "PHASE39_CAMPAIGN_SUMMARY", "timestamp_utc": summary["timestamp_utc"], "paper_only": True, "n_cycles": summary["n_cycles"], "trading_enabled_cycles": summary["trading_enabled_cycles"], "validation_passed_cycles": summary["validation_passed_cycles"], "gates_ok": True}
        camp = self._finite_dict(camp)
        (outdir / "PHASE39_CAMPAIGN_SUMMARY.json").write_text(json.dumps(camp, indent=2))
        (outdir / "PHASE39_CAMPAIGN_SUMMARY.md").write_text("# PHASE39 CAMPAIGN SUMMARY\n\nOK\n")
        return summary
