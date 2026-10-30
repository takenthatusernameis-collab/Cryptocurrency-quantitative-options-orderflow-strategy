"""Execution algorithms: TWAP, VWAP, Implementation Shortfall with guards."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import isfinite
from typing import Any, Dict, List, Optional, Tuple

from ..errors import OrderError, get_logger
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, clamp
from .orders import Order, OrderSide, OrderType, TimeInForce


_logger = get_logger(__name__)


@dataclass
class SlippageModel:
    """Slippage model with participation and adverse selection guards."""

    base_bps: float = 1.0
    impact_coefficient: float = 0.1  # temporary impact coefficient
    permanent_impact_coeff: float = 0.05
    max_slippage_bps: float = 10.0
    adverse_selection_bps: float = 2.0
    participation_cap: float = 0.1  # max 10% of volume

    def __post_init__(self) -> None:
        for name, val in [
            ("base_bps", self.base_bps),
            ("impact_coefficient", self.impact_coefficient),
            ("permanent_impact_coeff", self.permanent_impact_coeff),
            ("max_slippage_bps", self.max_slippage_bps),
            ("adverse_selection_bps", self.adverse_selection_bps),
            ("participation_cap", self.participation_cap),
        ]:
            if not isfinite(float(val)):
                raise OrderError(f"{name} must be finite", context={"module": "execution.algorithms"})
        if self.participation_cap < 0 or self.participation_cap > 1.0:
            raise OrderError("participation_cap must be in [0,1]", context={"participation_cap": self.participation_cap})
        if self.max_slippage_bps < 0:
            raise OrderError("max_slippage_bps must be >= 0", context={"max_slippage_bps": self.max_slippage_bps})

    def estimate_slippage_bps(self, side: OrderSide, qty: float, adv: float, participation_rate: float,
                              volatility: float = 0.02) -> float:
        """Estimate slippage in bps with guards."""
        if qty <= 0 or adv <= 0 or not isfinite(qty) or not isfinite(adv):
            return clamp(self.base_bps, 0.0, self.max_slippage_bps)
        pr = clamp(participation_rate, 0.0, self.participation_cap)
        vol = clamp(volatility, 0.0, 1.0)
        # Temporary impact
        impact = self.impact_coefficient * (pr ** 0.5) * vol * 10000.0  # rough scale
        impact += self.base_bps
        # Adverse selection
        if pr > self.participation_cap * 0.5:  # higher participation -> more adverse selection
            impact += self.adverse_selection_bps * (pr / max(self.participation_cap, 1e-18))
        impact = clamp(impact, 0.0, self.max_slippage_bps)
        return float(impact)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "base_bps": float(self.base_bps),
            "impact_coefficient": float(self.impact_coefficient),
            "permanent_impact_coeff": float(self.permanent_impact_coeff),
            "max_slippage_bps": float(self.max_slippage_bps),
            "adverse_selection_bps": float(self.adverse_selection_bps),
            "participation_cap": float(self.participation_cap),
        })


@dataclass
class Slice:
    """Execution slice."""

    slice_id: str
    quantity: float
    target_time: datetime
    limit_price: Optional[float] = None
    participation_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "slice_id": self.slice_id,
            "quantity": float(self.quantity),
            "target_time": self.target_time.isoformat(),
            "limit_price": float(self.limit_price) if self.limit_price is not None else None,
            "participation_rate": float(self.participation_rate),
        })


class ExecutionAlgorithm(ABC):
    """Base execution algorithm."""

    def __init__(self, name: str, slippage_model: Optional[SlippageModel] = None, seed: int = 42):
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise OrderError("seed must be integer for determinism", context={"algorithm": name})
        self.name = name
        self.slippage_model = slippage_model or SlippageModel()
        self.rng = random.Random(int(seed))

    @abstractmethod
    def generate_slices(
        self,
        order: Order,
        start_time: datetime,
        end_time: datetime,
        price_history: Optional[List[Tuple[datetime, float, float]]] = None,  # (time, price, volume)
        adv: float = 0.0,
    ) -> List[Slice]:
        """Generate execution slices."""
        raise NotImplementedError


class TWAPAlgorithm(ExecutionAlgorithm):
    """Time-Weighted Average Price algorithm."""

    def __init__(self, num_slices: int = 10, **kwargs):
        super().__init__("twap", **kwargs)
        if num_slices < 1:
            raise OrderError("num_slices must be >= 1", context={"num_slices": num_slices})
        self.num_slices = int(num_slices)

    def generate_slices(
        self,
        order: Order,
        start_time: datetime,
        end_time: datetime,
        price_history: Optional[List[Tuple[datetime, float, float]]] = None,
        adv: float = 0.0,
    ) -> List[Slice]:
        total_qty = float(order.quantity)
        if total_qty <= 0 or not isfinite(total_qty):
            return []
        duration = (end_time - start_time).total_seconds()
        if duration < 0:
            duration = 0.0
        slices: List[Slice] = []
        base_qty = total_qty / float(self.num_slices)
        for i in range(self.num_slices):
            # Even time distribution
            frac = (i + 1) / float(self.num_slices) if self.num_slices > 0 else 1.0
            target_time = start_time + timedelta(seconds=duration * frac)
            qty = base_qty
            if i == self.num_slices - 1:
                # Put remainder in last slice
                qty = total_qty - sum(s.quantity for s in slices)
            if qty <= 0:
                continue
            pr = 0.0
            if adv > 0 and isfinite(adv):
                pr = clamp(qty / adv, 0.0, self.slippage_model.participation_cap)
            # Adverse selection guard
            if pr > self.slippage_model.participation_cap:
                # Split if exceeds cap
                pass
            slices.append(Slice(slice_id=f"{order.order_id}_twap_{i:03d}", quantity=float(qty), target_time=target_time, participation_rate=float(pr)))
        # Enforce participation caps
        capped_slices: List[Slice] = []
        for s in slices:
            if adv > 0 and isfinite(adv) and s.quantity / adv > self.slippage_model.participation_cap:
                # Reduce to cap
                max_qty = adv * self.slippage_model.participation_cap
                if max_qty > 0:
                    s.quantity = float(max_qty)
            if s.quantity > 0:
                capped_slices.append(s)
        return capped_slices


class VWAPAlgorithm(ExecutionAlgorithm):
    """Volume-Weighted Average Price algorithm."""

    def __init__(self, num_slices: int = 10, **kwargs):
        super().__init__("vwap", **kwargs)
        if num_slices < 1:
            raise OrderError("num_slices must be >= 1", context={"num_slices": num_slices})
        self.num_slices = int(num_slices)

    def generate_slices(
        self,
        order: Order,
        start_time: datetime,
        end_time: datetime,
        price_history: Optional[List[Tuple[datetime, float, float]]] = None,
        adv: float = 0.0,
    ) -> List[Slice]:
        total_qty = float(order.quantity)
        if total_qty <= 0 or not isfinite(total_qty):
            return []
        duration = (end_time - start_time).total_seconds()
        if duration < 0:
            duration = 0.0
        slices: List[Slice] = []
        # Use price_history volumes if available
        volumes = []
        if price_history and len(price_history) > 0:
            for _, _, vol in price_history:
                v = float(vol)
                if isfinite(v) and v > 0:
                    volumes.append(v)
        if not volumes or len(volumes) < self.num_slices:
            # Uniform distribution as fallback
            volumes = [1.0] * self.num_slices
        # Normalize
        total_vol = sum(volumes[: self.num_slices])
        if total_vol <= 0:
            volumes = [1.0] * self.num_slices
            total_vol = float(self.num_slices)
        cum_qty = 0.0
        for i in range(min(self.num_slices, len(volumes))):
            frac = volumes[i] / total_vol
            qty = total_qty * frac
            if i == min(self.num_slices, len(volumes)) - 1:
                qty = total_qty - cum_qty
            if qty <= 0:
                continue
            frac_time = (i + 1) / float(min(self.num_slices, len(volumes)))
            target_time = start_time + timedelta(seconds=duration * frac_time)
            pr = 0.0
            if adv > 0 and isfinite(adv):
                pr = clamp(qty / adv, 0.0, self.slippage_model.participation_cap)
            if adv > 0 and isfinite(adv) and qty / adv > self.slippage_model.participation_cap:
                qty = adv * self.slippage_model.participation_cap
            if qty <= 0:
                continue
            cum_qty += qty
            slices.append(Slice(slice_id=f"{order.order_id}_vwap_{i:03d}", quantity=float(qty), target_time=target_time, participation_rate=float(pr)))
        return slices


class ImplementationShortfallAlgorithm(ExecutionAlgorithm):
    """Implementation Shortfall style algorithm with urgency and adverse selection guards."""

    def __init__(self, urgency: float = 0.5, risk_aversion: float = 0.3, **kwargs):
        super().__init__("implementation_shortfall", **kwargs)
        if not isfinite(urgency) or urgency < 0 or urgency > 1:
            raise OrderError("urgency must be in [0,1]", context={"urgency": urgency})
        if not isfinite(risk_aversion) or risk_aversion < 0:
            raise OrderError("risk_aversion must be >= 0", context={"risk_aversion": risk_aversion})
        self.urgency = float(urgency)
        self.risk_aversion = float(risk_aversion)

    def generate_slices(
        self,
        order: Order,
        start_time: datetime,
        end_time: datetime,
        price_history: Optional[List[Tuple[datetime, float, float]]] = None,
        adv: float = 0.0,
    ) -> List[Slice]:
        total_qty = float(order.quantity)
        if total_qty <= 0 or not isfinite(total_qty):
            return []
        duration = (end_time - start_time).total_seconds()
        if duration < 0:
            duration = 0.0
        # Front-load based on urgency, but respect participation caps and adverse selection
        num_slices = max(5, int(10 * (0.5 + self.urgency)))
        slices: List[Slice] = []
        cum_qty = 0.0
        weights = []
        for i in range(num_slices):
            # Frontload: higher weight earlier
            weights.append((num_slices - i) ** (1.0 + self.urgency))
        total_w = sum(weights)
        if total_w <= 0:
            weights = [1.0] * num_slices
            total_w = float(num_slices)
        for i in range(num_slices):
            frac = weights[i] / total_w
            qty = total_qty * frac
            if i == num_slices - 1:
                qty = total_qty - cum_qty
            if qty <= 0:
                continue
            frac_time = (i + 1) / float(num_slices)
            target_time = start_time + timedelta(seconds=duration * frac_time)
            pr = 0.0
            if adv > 0 and isfinite(adv):
                pr = clamp(qty / adv, 0.0, self.slippage_model.participation_cap)
            if adv > 0 and isfinite(adv) and qty / adv > self.slippage_model.participation_cap:
                qty = adv * self.slippage_model.participation_cap
            if qty <= 0:
                continue
            # Adverse selection guard - reduce if very aggressive
            if pr > self.slippage_model.participation_cap * 0.8:
                qty = qty * 0.9  # scale down
            cum_qty += qty
            slices.append(Slice(slice_id=f"{order.order_id}_is_{i:03d}", quantity=float(qty), target_time=target_time, participation_rate=float(pr)))
        return slices


def create_algorithm(algo_type: str, **kwargs) -> ExecutionAlgorithm:
    algo_type = str(algo_type).lower()
    if algo_type == "twap":
        return TWAPAlgorithm(**kwargs)
    elif algo_type == "vwap":
        return VWAPAlgorithm(**kwargs)
    elif algo_type in ("is", "implementation_shortfall", "implementation shortfall"):
        return ImplementationShortfallAlgorithm(**kwargs)
    else:
        raise OrderError(f"Unknown algorithm type: {algo_type}", context={"algo_type": algo_type})
