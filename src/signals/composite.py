"""Composite signal generation with regime awareness and confidence calibration."""

from dataclasses import dataclass
from math import isfinite
from typing import Dict, Optional


@dataclass
class Signal:
    symbol: str
    direction: str  # 'long', 'short', 'neutral'
    strength: float  # -1 to 1
    confidence: float  # 0 to 1
    components: Dict[str, float]
    regime: str = "unknown"


def _sign(x: float) -> float:
    if x > 0:
        return 1.0
    elif x < 0:
        return -1.0
    return 0.0


class CompositeSignalGenerator:
    """Regime-aware composite signal generator.

    Detects market regime from GEX sign/magnitude and skew, then adjusts
    component weights accordingly. Confidence reflects component agreement
    (dispersion), not just |composite|.
    """

    def __init__(self):
        self.base_weights = {
            "gamma": 0.25,
            "orderflow": 0.30,
            "vol_skew": 0.25,
            "put_call": 0.20,
        }
        # Regime-specific weight overrides
        self.regime_weights = {
            "high_vol_negative_gex": {"gamma": 0.45, "orderflow": 0.30, "vol_skew": 0.15, "put_call": 0.10},
            "low_vol_positive_gex": {"gamma": 0.15, "orderflow": 0.25, "vol_skew": 0.30, "put_call": 0.30},
            "skew_bearish": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.35, "put_call": 0.10},
            "skew_bullish": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.10, "put_call": 0.35},
            "neutral": {"gamma": 0.25, "orderflow": 0.30, "vol_skew": 0.25, "put_call": 0.20},
        }

    def _detect_regime(self, total_gex: float, iv_skew: float, put_call_ratio: float) -> str:
        """Detect market regime from GEX, skew, and PCR."""
        # Negative GEX => high vol regime (dealers short gamma, vol expansion)
        if total_gex < -1e8:
            return "high_vol_negative_gex"
        # Positive GEX => low vol regime (dealers long gamma, vol compression)
        if total_gex > 1e8:
            return "low_vol_positive_gex"
        # Skew-driven regimes
        if iv_skew > 0.05:
            return "skew_bearish"
        if iv_skew < -0.05:
            return "skew_bullish"
        return "neutral"

    def _get_weights(self, regime: str) -> Dict[str, float]:
        return self.regime_weights.get(regime, self.regime_weights["neutral"])

    def generate_signal(
        self,
        symbol: str,
        spot_price: float = 0.0,
        total_gex: float = 0.0,
        cum_delta: float = 0.0,
        of_imbalance: float = 0.0,
        iv_skew: float = 0.0,
        put_call_ratio: float = 1.0,
        **kwargs,
    ) -> Signal:
        """Generate regime-aware composite trading signal."""
        components = {}

        # Gamma exposure signal (negative GEX can lead to volatility expansion)
        if total_gex != 0 and isfinite(total_gex):
            gamma_signal = -_sign(total_gex) * min(abs(total_gex) / 1e9, 1.0)
        else:
            gamma_signal = 0.0
        if not isfinite(gamma_signal):
            gamma_signal = 0.0
        components["gamma"] = gamma_signal

        # Orderflow signal
        of_signal = (cum_delta / 10000.0 + float(of_imbalance)) / 2.0
        if isfinite(of_signal):
            of_signal = max(-1.0, min(1.0, of_signal))
        else:
            of_signal = 0.0
        components["orderflow"] = of_signal

        # Volatility skew signal (steep put skew often bearish)
        skew_signal = -max(-1.0, min(1.0, float(iv_skew) * 10))
        if not isfinite(skew_signal):
            skew_signal = 0.0
        components["vol_skew"] = skew_signal

        # Put/call ratio signal
        pcr = float(put_call_ratio)
        if not isfinite(pcr) or pcr <= 0:
            pc_signal = 0.0
        elif pcr > 1.0:
            pc_signal = -min((pcr - 1.0) / 2.0, 1.0)
        elif pcr < 1.0:
            pc_signal = min((1.0 - pcr) / 0.5, 1.0) * 0.5
        else:
            pc_signal = 0.0
        if not isfinite(pc_signal):
            pc_signal = 0.0
        components["put_call"] = pc_signal

        # Detect regime and get adjusted weights
        regime = self._detect_regime(total_gex, iv_skew, put_call_ratio)
        weights = self._get_weights(regime)

        # Weighted composite
        composite = sum(weights[k] * components.get(k, 0.0) for k in components)
        if not isfinite(composite):
            composite = 0.0
        composite = max(-1.0, min(1.0, composite))

        # Determine direction
        if composite > 0.3:
            direction = "long"
        elif composite < -0.3:
            direction = "short"
        else:
            direction = "neutral"

        # Confidence calibration: reflect component agreement (low dispersion => high confidence)
        # Also scale by magnitude of composite
        comp_values = list(components.values())
        if comp_values:
            # Mean absolute deviation as dispersion measure
            mean_abs = sum(abs(v) for v in comp_values) / len(comp_values)
            # Agreement: how many components agree in sign with composite
            if composite != 0:
                comp_sign = _sign(composite)
                agreements = sum(1 for v in comp_values if _sign(v) == comp_sign)
                agreement_ratio = agreements / len(comp_values)
            else:
                agreement_ratio = 0.0
            # Dispersion-based confidence (lower dispersion => higher confidence)
            dispersion = sum((abs(v) - mean_abs) ** 2 for v in comp_values) / len(comp_values)
            dispersion = max(0.0, dispersion) ** 0.5
            max_dispersion = 1.0
            agreement_confidence = agreement_ratio
            dispersion_confidence = max(0.0, 1.0 - dispersion / max_dispersion)
            magnitude_confidence = abs(composite)
            # Blend: 40% agreement, 30% dispersion, 30% magnitude
            confidence = 0.4 * agreement_confidence + 0.3 * dispersion_confidence + 0.3 * magnitude_confidence
        else:
            confidence = 0.0

        confidence = max(0.0, min(1.0, confidence))
        if not isfinite(confidence):
            confidence = 0.0

        return Signal(
            symbol=symbol,
            direction=direction,
            strength=float(composite),
            confidence=float(confidence),
            components=components,
            regime=regime,
        )