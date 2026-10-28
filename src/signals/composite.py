"""Composite signal generation combining multiple features."""

from dataclasses import dataclass
from typing import Dict, Optional

import math


@dataclass
class Signal:
    symbol: str
    direction: str  # 'long', 'short', 'neutral'
    strength: float  # -1 to 1
    confidence: float  # 0 to 1
    components: Dict[str, float]


class CompositeSignalGenerator:
    def __init__(self):
        self.weights = {
            "gamma": 0.25,
            "orderflow": 0.30,
            "vol_skew": 0.25,
            "put_call": 0.20,
        }

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
        """Generate composite trading signal."""
        components = {}

        # Gamma exposure signal (negative GEX can lead to volatility expansion)
        if total_gex != 0 and math.isfinite(total_gex):
            gamma_signal = -np_sign(total_gex) * min(abs(total_gex) / 1e9, 1.0)
        else:
            gamma_signal = 0.0
        components["gamma"] = gamma_signal

        # Orderflow signal
        of_signal = (cum_delta / 10000.0 + float(of_imbalance)) / 2.0
        if math.isfinite(of_signal):
            of_signal = max(-1.0, min(1.0, of_signal))
        else:
            of_signal = 0.0
        components["orderflow"] = of_signal

        # Volatility skew signal (steep put skew often bearish)
        skew_signal = -max(-1.0, min(1.0, float(iv_skew) * 10))
        if not math.isfinite(skew_signal):
            skew_signal = 0.0
        components["vol_skew"] = skew_signal

        # Put/call ratio signal
        pcr = float(put_call_ratio)
        if not math.isfinite(pcr) or pcr <= 0:
            pc_signal = 0.0
        elif pcr > 1.0:
            pc_signal = -min((pcr - 1.0) / 2.0, 1.0)
        elif pcr < 1.0:
            pc_signal = min((1.0 - pcr) / 0.5, 1.0) * 0.5
        else:
            pc_signal = 0.0
        if not math.isfinite(pc_signal):
            pc_signal = 0.0
        components["put_call"] = pc_signal

        # Weighted composite
        composite = sum(self.weights[k] * components.get(k, 0.0) for k in components)
        if not math.isfinite(composite):
            composite = 0.0
        composite = max(-1.0, min(1.0, composite))

        # Determine direction
        if composite > 0.3:
            direction = "long"
        elif composite < -0.3:
            direction = "short"
        else:
            direction = "neutral"

        confidence = abs(composite)
        if not math.isfinite(confidence):
            confidence = 0.0

        return Signal(
            symbol=symbol,
            direction=direction,
            strength=float(composite),
            confidence=float(confidence),
            components=components,
        )


def np_sign(x):
    if x > 0:
        return 1.0
    elif x < 0:
        return -1.0
    return 0.0
