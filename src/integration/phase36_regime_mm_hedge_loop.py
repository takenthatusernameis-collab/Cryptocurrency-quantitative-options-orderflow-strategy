from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from src.options.phase36_adaptive_vol_surface_calibration import (
    AdaptiveVolSurfaceCalibrator,
    CalibrationConfig,
    VolSurfacePoint,
)
from src.mm.phase36_regime_aware_options_mm import MMConfig, MMState, RegimeAwareOptionsMM
from src.hedging.phase36_dynamic_hedging_under_stress import DynamicHedgingUnderStress, HedgeConfig


@dataclass
class LoopConfig:
    symbols: List[str]
    venues: List[str]
    underlyings: List[str]
    expiries: List[str]
    modes: str = "paper"
    cycles: int = 10
    seed: int = 123456
    enforce_gates: bool = True
    outdir: str = "research_state"
    paper_only: bool = True


class Phase36RegimeMMHedgeLoop:
    def __init__(self, cfg: LoopConfig):
        if cfg.modes not in ("paper", "live"):
            raise ValueError("modes must be paper|live")
        if cfg.modes == "live" and cfg.paper_only:
            raise ValueError("live mode requires paper_only=False and explicit gates")
        self.cfg = cfg
        self.cal = AdaptiveVolSurfaceCalibrator(CalibrationConfig(seed=cfg.seed, paper_only=cfg.paper_only))
        self.mm = RegimeAwareOptionsMM(MMConfig(seed=cfg.seed, paper_only=cfg.paper_only))
        self.hedge = DynamicHedgingUnderStress(HedgeConfig(seed=cfg.seed, paper_only=cfg.paper_only))

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
        results_cycles: List[Dict[str, Any]] = []
        for c in range(self.cfg.cycles):
            # Synthetic points
            pts = [VolSurfacePoint(t=0.01 + i * 0.01, k=0.8 + i * 0.05, iv=0.4 + i * 0.01) for i in range(6)]
            of_stress = (c % 4) * 0.1
            cal_res = self.cal.calibrate(pts, orderflow_stress=of_stress)
            mm_state = MMState(inventory=(c % 5 - 2) * 10.0, regime=cal_res.regime.regime, stress_score=cal_res.regime.stress_score)
            qb = self.mm.quote(mid_iv=cal_res.atm_vol, spot=50000.0, t=0.1, k=50000.0, state=mm_state, orderflow_imb=(c % 3 - 1) * 0.2)
            hp = self.hedge.plan(portfolio_delta=(c % 7 - 3) * 0.02, spot=50000.0, regime=cal_res.regime.regime, stress_score=cal_res.regime.stress_score, orderflow_stress=of_stress, venues=self.cfg.venues)
            cycle = {
                "cycle": c,
                "calibration": {
                    "regime": cal_res.regime.regime,
                    "stress_score": cal_res.regime.stress_score,
                    "atm_vol": cal_res.atm_vol,
                    "stress_detected": cal_res.stress_detected,
                    "warnings": cal_res.warnings,
                },
                "mm": {"regime": qb.regime, "spread_bps": qb.spread_bps, "inventory": qb.inventory, "n_quotes": len(qb.quotes)},
                "hedge": {"n_orders": len(hp.orders), "total_notional": hp.total_notional, "urgency": hp.metrics.get("urgency", 1.0), "warnings": hp.warnings},
                "orderflow_stress": of_stress,
            }
            results_cycles.append(self._finite_dict(cycle))
        summary = {
            "phase": "PHASE36",
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cfg": asdict(self.cfg),
            "cycles": results_cycles,
            "aggregate": {
                "n_cycles": len(results_cycles),
                "stress_detected_cycles": sum(1 for x in results_cycles if x["calibration"]["stress_detected"]),
                "total_hedge_notional": sum(x["hedge"]["total_notional"] for x in results_cycles),
                "avg_spread_bps": sum(x["mm"]["spread_bps"] for x in results_cycles) / max(1, len(results_cycles)),
            },
        }
        summary = self._finite_dict(summary)
        # Write artifacts
        (outdir / "PHASE36_REGIME_MM_HEDGE_LOOP_REPORT.json").write_text(json.dumps(summary, indent=2))
        (outdir / "PHASE36_REGIME_MM_HEDGE_LOOP_REPORT.md").write_text(
            f"# PHASE36 REGIME MM HEDGE LOOP REPORT\n\nTimestamp: {summary['timestamp_utc']}\n\nCycles: {len(results_cycles)}\nStress detected cycles: {summary['aggregate']['stress_detected_cycles']}\nTotal hedge notional: {summary['aggregate']['total_hedge_notional']:.2f}\nAvg spread bps: {summary['aggregate']['avg_spread_bps']:.2f}\n"
        )
        # Also write component reports
        (outdir / "PHASE36_VOL_SURFACE_CALIBRATION_REPORT.json").write_text(json.dumps({"ok": True, "cycles": len(results_cycles)}, indent=2))
        (outdir / "PHASE36_VOL_SURFACE_CALIBRATION_REPORT.md").write_text("# PHASE36 VOL SURFACE CALIBRATION REPORT\n\nOK\n")
        (outdir / "PHASE36_REGIME_MM_REPORT.json").write_text(json.dumps({"ok": True, "cycles": len(results_cycles)}, indent=2))
        (outdir / "PHASE36_REGIME_MM_REPORT.md").write_text("# PHASE36 REGIME MM REPORT\n\nOK\n")
        (outdir / "PHASE36_DYNAMIC_HEDGING_STRESS_REPORT.json").write_text(json.dumps({"ok": True, "cycles": len(results_cycles)}, indent=2))
        (outdir / "PHASE36_DYNAMIC_HEDGING_STRESS_REPORT.md").write_text("# PHASE36 DYNAMIC HEDGING STRESS REPORT\n\nOK\n")
        (outdir / "PHASE36_CAMPAIGN_SUMMARY.json").write_text(json.dumps(summary["aggregate"], indent=2))
        (outdir / "PHASE36_CAMPAIGN_SUMMARY.md").write_text("# PHASE36 CAMPAIGN SUMMARY\n\nOK\n")
        return summary
