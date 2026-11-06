from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..data.schemas import OrderflowSnapshot
from ..features.orderflow import (
    calculate_cumulative_delta,
    calculate_orderflow_imbalance,
    detect_large_trades,
)


@dataclass
class OrderflowSignal:
    direction: int
    strength: float
    cumulative_delta: float
    imbalance: float
    large_trade_count: int
    confidence: float


class OrderflowSignalGenerator:
    def __init__(
        self,
        imbalance_threshold: float = 0.001,
        large_trade_size: float = 10.0,
        min_confidence: float = 0.1,
    ) -> None:
        self.imbalance_threshold = imbalance_threshold
        self.large_trade_size = large_trade_size
        self.min_confidence = min_confidence

    def generate(self, snapshot: OrderflowSnapshot) -> OrderflowSignal:
        cum_delta = float(calculate_cumulative_delta(snapshot.trades))
        imbalance = float(calculate_orderflow_imbalance(snapshot.trades))
        large = detect_large_trades(snapshot.trades, size_threshold=self.large_trade_size)
        large_count = len(large)
        direction = 0
        if imbalance > self.imbalance_threshold:
            direction = 1
        elif imbalance < -self.imbalance_threshold:
            direction = -1
        strength = min(1.0, abs(imbalance))
        confidence = min(1.0, self.min_confidence + strength + (0.05 if large_count else 0.0))
        return OrderflowSignal(
            direction=direction,
            strength=strength,
            cumulative_delta=cum_delta,
            imbalance=imbalance,
            large_trade_count=large_count,
            confidence=confidence,
        )
