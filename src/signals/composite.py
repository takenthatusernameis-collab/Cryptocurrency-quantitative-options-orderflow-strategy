"""Composite signal generation combining multiple features."""

from dataclasses import dataclass
from typing import Dict, Optional

from ..features.gamma_exposure import calculate_total_gex
from ..features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance
from ..features.volatility import calculate_put_call_ratio, calculate_iv_skew


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
        spot_price: float,
        total_gex: float = 0.0,
        cum_delta: float = 0.0,
        of_imbalance: float = 0.0,
        iv_skew: float = 0.0,
        put_call_ratio: float = 1.0,
    ) -> Signal:
        """Generate composite trading signal."""
        components = {}
        
        # Gamma exposure signal (negative GEX can lead to volatility expansion)
        gamma_signal = -np_sign(total_gex) * min(abs(total_gex) / 1e9, 1.0) if total_gex != 0 else 0.0
        components["gamma"] = gamma_signal
        
        # Orderflow signal
        of_signal = (cum_delta / 1000.0 + of_imbalance) / 2.0
        of_signal = max(-1.0, min(1.0, of_signal))
        components["orderflow"] = of_signal
        
        # Volatility skew signal (steep put skew often bearish)
        skew_signal = -max(-1.0, min(1.0, iv_skew * 10))
        components["vol_skew"] = skew_signal
        
        # Put/call ratio signal
        if put_call_ratio > 1.0:
            pc_signal = -min((put_call_ratio - 1.0) / 2.0, 1.0)
        elif put_call_ratio < 1.0:
            pc_signal = min((1.0 - put_call_ratio) / 0.5, 1.0) * 0.5
        else:
            pc_signal = 0.0
        components["put_call"] = pc_signal
        
        # Weighted composite
        composite = sum(self.weights[k] * components[k] for k in components)
        composite = max(-1.0, min(1.0, composite))
        
        # Determine direction
        if composite > 0.3:
            direction = "long"
        elif composite < -0.3:
            direction = "short"
        else:
            direction = "neutral"
        
        confidence = abs(composite)
        
        return Signal(
            symbol=symbol,
            direction=direction,
            strength=composite,
            confidence=confidence,
            components=components,
        )


def np_sign(x):
    if x > 0:
        return 1.0
    elif x < 0:
        return -1.0
    return 0.0
