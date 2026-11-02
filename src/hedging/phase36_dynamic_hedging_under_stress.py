from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class HedgeConfig:
    seed: int = 123456
    base_delta_band: float = 0.01
    stress_band_mult: float = 2.0
    urgency_factor: float = 1.5
    max_hedge_notional: float = 10_000_000.0
    paper_only: bool = True


@dataclass
class HedgeOrder:
    venue: str
    symbol: str
    side: str  # buy|sell
    qty: float
    urgency: float
    reason: str
    valid: bool = True


@dataclass
class HedgePlan:
    ok: bool
    orders: List[HedgeOrder]
    total_notional: float
    regime: str
    stress_score: float
    of_stress: float
    metrics: Dict[str, float]
    warnings: List[str]


class DynamicHedgingUnderStress:
    def __init__(self, cfg: HedgeConfig | None = None):
        self.cfg = cfg or HedgeConfig()
        if not self.cfg.paper_only:
            raise ValueError("live hedging paths must be explicitly gated; default paper_only True")

    def _finite(self, x: float) -> bool:
        return math.isfinite(x)

    def plan(self, portfolio_delta: float, spot: float, regime: str, stress_score: float, orderflow_stress: float, venues: List[str]) -> HedgePlan:
        warnings: List[str] = []
        if not self._finite(portfolio_delta):
            portfolio_delta = 0.0
            warnings.append("delta_finite")
        if not self._finite(spot) or spot <= 0:
            spot = 100.0
            warnings.append("spot_finite")
        if not math.isfinite(stress_score):
            stress_score = 0.0
        if not math.isfinite(orderflow_stress):
            orderflow_stress = 0.0
        regime_mult_band = 1.0
        if regime == "stressed":
            regime_mult_band = 1.4
        elif regime == "crisis":
            regime_mult_band = 1.8
        band = self.cfg.base_delta_band * regime_mult_band * (1.0 + stress_score * 0.05)
        urgency = 1.0 + self.cfg.urgency_factor * max(0.0, stress_score / 10.0) + orderflow_stress * 0.8
        if urgency > 3.0:
            urgency = 3.0
        orders: List[HedgeOrder] = []
        if abs(portfolio_delta) > band:
            # Hedge to reduce delta magnitude
            need_notional = abs(portfolio_delta) * spot * (1.0 + urgency * 0.1)
            if need_notional > self.cfg.max_hedge_notional:
                need_notional = self.cfg.max_hedge_notional
                warnings.append("hedge_capped")
            side = "sell" if portfolio_delta > 0 else "buy"
            qty = need_notional / max(spot, 1e-12)
            # Route across venues
            vlist = venues or ["venue_a", "venue_b"]
            for i, v in enumerate(vlist[:3]):
                frac = 1.0 / min(3, len(vlist))
                orders.append(
                    HedgeOrder(
                        venue=v,
                        symbol=f"PERP_{i}",
                        side=side,
                        qty=qty * frac,
                        urgency=urgency,
                        reason=f"delta_hedge_{regime}_ofstress_{orderflow_stress:.2f}",
                    )
                )
        total_notional = sum(o.qty * spot for o in orders)
        if not self._finite(total_notional):
            total_notional = 0.0
        metrics = {
            "portfolio_delta": portfolio_delta,
            "band": band,
            "urgency": urgency,
            "regime_mult_band": regime_mult_band,
            "n_orders": float(len(orders)),
            "total_notional": total_notional,
        }
        return HedgePlan(ok=True, orders=orders, total_notional=total_notional, regime=regime, stress_score=stress_score, of_stress=orderflow_stress, metrics=metrics, warnings=warnings)
