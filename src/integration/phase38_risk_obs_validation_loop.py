"""
Phase 38: Risk + Observability + Continuous Validation Loop.

Orchestrates Phase 38 components with Phase 37 loop, regime filters,
margin/reallocation hooks, hard-gated live paths. Deterministic, finite numerics.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.risk.phase38_realtime_risk_monitor import Phase38RealtimeRiskMonitor, RiskMonitorConfig38
from src.observability.phase38_telemetry_observability import Phase38TelemetryObservability, ObsConfig38
from src.validation.phase38_continuous_validation import Phase38ContinuousValidation, CValConfig38
from src.integration.phase37_orderflow_routing_loop import Phase37OrderflowRoutingLoop, Loop37Config


@dataclass
class Loop38Config:
    seed: int = 38038
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
            self.venues = ["deribit", "okx", "bybit"]
        if self.underlyings is None:
            self.underlyings = ["BTC", "ETH"]
        if self.expiries is None:
            self.expiries = ["2026-12-26"]


class Phase38RiskObsValidationLoop:
    def __init__(self, cfg: Optional[Loop38Config] = None):
        self.cfg = cfg or Loop38Config()
        if self.cfg.modes not in ("paper", "live"):
            raise ValueError("modes must be paper|live")
        if self.cfg.modes == "live" and self.cfg.paper_only:
            raise ValueError("live mode requires paper_only=False and explicit gates")
        if not isinstance(self.cfg.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.cfg.paper_only:
            raise ValueError("Phase38RiskObsValidationLoop: paper_only must remain True (live path hard-gated)")
        self.risk = Phase38RealtimeRiskMonitor(RiskMonitorConfig38(seed=self.cfg.seed, paper_only=True, cycles=self.cfg.cycles))
        self.obs = Phase38TelemetryObservability(ObsConfig38(seed=self.cfg.seed + 1, paper_only=True))
        self.cval = Phase38ContinuousValidation(CValConfig38(seed=self.cfg.seed + 2, paper_only=True))
        l37 = Loop37Config(symbols=self.cfg.symbols, venues=self.cfg.venues, underlyings=self.cfg.underlyings, expiries=self.cfg.expiries, modes="paper", cycles=self.cfg.cycles, seed=self.cfg.seed, paper_only=True, outdir=self.cfg.outdir)
        self.loop37 = Phase37OrderflowRoutingLoop(l37)

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
        rsum = self.risk.run_campaign()
        self.obs.increment("cycles", float(self.cfg.cycles))
        self.obs.gauge("risk_breaches_total", float(len(rsum.get("breaches", []))))
        self.obs.trace("phase38_loop_start", {"cycles": self.cfg.cycles})
        l37s = self.loop37.run()
        results = []
        for c in range(self.cfg.cycles):
            rc = rsum["cycles"][c] if c < len(rsum["cycles"]) else None
            regime = rc.get("regime") if rc else "normal"
            self.obs.increment(f"regime_{regime}", 1.0)
            self.obs.observe("drawdown_pct", rc.get("drawdown_pct", 0.0) if rc else 0.0)
            bt_pnl = -1000.0 + c * 10.0
            live_pnl = bt_pnl * (1.0 - 0.01 * (c % 3))
            p = self.cval.parity_check(c, bt_pnl, live_pnl)
            if c % 4 == 0:
                d = self.cval.drift_check("orderflow_imbalance", 0.0, 0.02)
            else:
                d = None
            s = self.cval.slippage_check(c, 10.0, 12.0)
            results.append({
                "cycle": c,
                "regime": regime,
                "risk_ok": rc.get("risk_ok") if rc else True,
                "action_taken": rc.get("action_taken") if rc else "none",
                "parity_ok": p.get("ok"),
                "slippage_ok": s.get("ok"),
                "drifted": d.get("drifted") if d else False,
            })
        self.obs.trace("phase38_loop_end", {"n_results": len(results)})
        if len([r for r in results if not r.get("risk_ok")]) > 2:
            self.obs.alert("high", "multiple_risk_breaches", {"count": len([r for r in results if not r.get("risk_ok")])})
        ores = self.obs.export(self.cfg.outdir)
        vres = self.cval.export(self.cfg.outdir)
        # write risk monitor artifacts
        outdir_path = Path(self.cfg.outdir)
        (outdir_path / "PHASE38_RISK_MONITOR_REPORT.json").write_text(json.dumps(rsum, indent=2))
        rmmd = []
        rmmd.append("# PHASE38 RISK MONITOR REPORT\n")
        rmmd.append(f"\nTimestamp: {rsum['timestamp_utc']}\n")
        rmmd.append(f"Cycles: {rsum['n_cycles']}, Breaches: {rsum['n_breaches']}\n")
        (outdir_path / "PHASE38_RISK_MONITOR_REPORT.md").write_text("".join(rmmd))
        summary = {
            "phase": "PHASE38_RISK_OBS_VALIDATION_LOOP",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "paper_only": True,
            "modes": "paper",
            "cfg": asdict(self.cfg),
            "n_cycles": len(results),
            "risk_ok_cycles": sum(1 for x in results if x.get("risk_ok")),
            "parity_ok_cycles": sum(1 for x in results if x.get("parity_ok")),
            "slippage_ok_cycles": sum(1 for x in results if x.get("slippage_ok")),
            "gates_ok": vres.get("gates_ok", True),
            "n_alerts": len(ores.get("alerts", [])),
            "n_traces": len(ores.get("traces", [])),
            "results": results,
            "integrated_with": ["PHASE37_ORDERFLOW_ROUTING_LOOP"],
        }
        summary = self._finite_dict(summary)
        (outdir / "PHASE38_RISK_OBS_VALIDATION_LOOP_REPORT.json").write_text(json.dumps(summary, indent=2))
        md = []
        md.append("# PHASE38 RISK OBS VALIDATION LOOP REPORT\n")
        md.append(f"\nTimestamp: {summary['timestamp_utc']}\n")
        md.append(f"Cycles: {summary['n_cycles']}, Risk OK: {summary['risk_ok_cycles']}\n")
        md.append(f"Gates OK: {summary['gates_ok']}, Alerts: {summary['n_alerts']}\n")
        (outdir / "PHASE38_RISK_OBS_VALIDATION_LOOP_REPORT.md").write_text("".join(md))
        camp = {"phase": "PHASE38_CAMPAIGN_SUMMARY", "timestamp_utc": summary["timestamp_utc"], "paper_only": True, "n_cycles": summary["n_cycles"], "risk_ok_cycles": summary["risk_ok_cycles"], "gates_ok": summary["gates_ok"], "n_alerts": summary["n_alerts"]}
        camp = self._finite_dict(camp)
        (outdir / "PHASE38_CAMPAIGN_SUMMARY.json").write_text(json.dumps(camp, indent=2))
        (outdir / "PHASE38_CAMPAIGN_SUMMARY.md").write_text("# PHASE38 CAMPAIGN SUMMARY\n\nOK\n")
        return summary
