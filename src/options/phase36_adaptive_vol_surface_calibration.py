from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CalibrationConfig:
    seed: int = 123456
    max_iter: int = 200
    min_points: int = 5
    stress_z_thresh: float = 2.0
    stability_eps: float = 1e-8
    paper_only: bool = True


@dataclass
class VolSurfacePoint:
    t: float
    k: float
    iv: float
    bid_iv: float | None = None
    ask_iv: float | None = None


@dataclass
class RegimeState:
    regime: str  # calm|normal|stressed|crisis
    stress_score: float
    vol_of_vol: float
    skew_slope: float


@dataclass
class CalibrationResult:
    ok: bool
    regime: RegimeState
    svi_params: Dict[str, float]
    atm_vol: float
    term_structure: Dict[float, float]
    skew_fit: Dict[str, float]
    stress_detected: bool
    warnings: List[str]
    metrics: Dict[str, float]


class AdaptiveVolSurfaceCalibrator:
    def __init__(self, cfg: CalibrationConfig | None = None):
        self.cfg = cfg or CalibrationConfig()
        if not self.cfg.paper_only:
            raise ValueError("live calibration paths must be explicitly gated; default paper_only True")

    def _finite(self, x: float) -> bool:
        return math.isfinite(x)

    def detect_regime(self, points: List[VolSurfacePoint]) -> RegimeState:
        if not points:
            return RegimeState("calm", 0.0, 0.0, 0.0)
        ivs = [p.iv for p in points if self._finite(p.iv)]
        if not ivs:
            return RegimeState("calm", 0.0, 0.0, 0.0)
        m = sum(ivs) / len(ivs)
        var = sum((v - m) ** 2 for v in ivs) / max(1, len(ivs))
        vov = math.sqrt(max(0.0, var)) / max(m, 1e-12)
        # rough skew proxy via two ends if possible
        sorted_pts = sorted(points, key=lambda p: p.k)
        if len(sorted_pts) >= 2:
            skew_slope = (sorted_pts[-1].iv - sorted_pts[0].iv) / max(
                sorted_pts[-1].k - sorted_pts[0].k, 1e-12
            )
        else:
            skew_slope = 0.0
        stress_score = min(10.0, vov * 5.0 + abs(skew_slope) * 2.0)
        if stress_score >= self.cfg.stress_z_thresh * 1.5:
            regime = "crisis"
        elif stress_score >= self.cfg.stress_z_thresh:
            regime = "stressed"
        elif stress_score >= 0.8:
            regime = "normal"
        else:
            regime = "calm"
        return RegimeState(regime=regime, stress_score=stress_score, vol_of_vol=vov, skew_slope=skew_slope)

    def calibrate(self, points: List[VolSurfacePoint], orderflow_stress: float = 0.0) -> CalibrationResult:
        regime = self.detect_regime(points)
        warnings: List[str] = []
        if len(points) < self.cfg.min_points:
            warnings.append("insufficient_points")
        if not math.isfinite(orderflow_stress):
            orderflow_stress = 0.0
        # Deterministic SVI-like params (robust)
        atm_vol = 0.5
        if points:
            atm_cands = [p.iv for p in points if abs(p.k - 1.0) < 0.1 and self._finite(p.iv)]
            if atm_cands:
                atm_vol = sum(atm_cands) / len(atm_cands)
            else:
                atm_vol = sum(p.iv for p in points if self._finite(p.iv)) / len(points)
        if not self._finite(atm_vol) or atm_vol <= 0:
            atm_vol = 0.5
            warnings.append("atm_fallback")
        # Inflate under stress
        stress_mult = 1.0 + max(0.0, regime.stress_score / 10.0) + max(0.0, orderflow_stress) * 0.2
        atm_vol_adj = atm_vol * stress_mult
        if not self._finite(atm_vol_adj) or atm_vol_adj <= 0:
            atm_vol_adj = atm_vol
            warnings.append("atm_adj_finite")
        # Term structure simple
        terms = sorted(set(p.t for p in points if self._finite(p.t)))
        term_structure: Dict[float, float] = {}
        for t in terms:
            term_structure[round(t, 6)] = max(1e-6, atm_vol_adj * (1.0 + 0.05 * math.sqrt(max(t, 1e-12))))
        # Skew fit
        skew_fit = {"a": 0.01, "b": 0.1 * regime.skew_slope, "rho": -0.3, "m": 0.0, "sigma": 0.1}
        # SVI params (dummy but finite)
        svi_params = {
            "a": (atm_vol_adj ** 2) * 0.01,
            "b": max(1e-6, 0.2 * atm_vol_adj),
            "rho": max(-0.99, min(0.99, -0.2 - 0.1 * regime.stress_score / 10.0)),
            "m": 0.0,
            "sigma": max(1e-6, 0.1 + 0.05 * regime.stress_score / 10.0),
        }
        for k, v in svi_params.items():
            if not self._finite(v):
                svi_params[k] = 1e-6
                warnings.append(f"svi_finite_{k}")
        stress_detected = regime.regime in ("stressed", "crisis")
        metrics = {
            "n_points": float(len(points)),
            "atm_vol_raw": atm_vol,
            "atm_vol_adj": atm_vol_adj,
            "stress_score": regime.stress_score,
            "vol_of_vol": regime.vol_of_vol,
        }
        return CalibrationResult(
            ok=True,
            regime=regime,
            svi_params=svi_params,
            atm_vol=atm_vol_adj,
            term_structure=term_structure,
            skew_fit=skew_fit,
            stress_detected=stress_detected,
            warnings=warnings,
            metrics=metrics,
        )
