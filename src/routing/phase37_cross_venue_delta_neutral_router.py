from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RouterConfig:
    seed: int = 525252
    paper_only: bool = True
    max_slippage_bps: float = 30.0
    fee_bps: float = 5.0
    delta_neutral_tol: float = 0.01
    max_venue_alloc_pct: float = 0.4


@dataclass
class RouteOrder:
    venue: str
    side: str
    qty: float
    notional_usd: float
    slippage_bps: float
    fee_usd: float
    valid: bool = True


@dataclass
class RoutePlan:
    ok: bool
    orders: List[RouteOrder]
    total_notional: float
    net_delta_est: float
    delta_neutral_ok: bool
    metrics: Dict[str, float]
    warnings: List[str]


class CrossVenueDeltaNeutralRouter:
    def __init__(self, cfg: RouterConfig | None = None):
        self.cfg = cfg or RouterConfig()
        if not self.cfg.paper_only:
            raise ValueError("live routing paths must be explicitly gated; default paper_only True")

    def _finite(self, x: float) -> bool:
        return math.isfinite(x)

    def route(self, target_qty: float, spot: float, venues: List[str], regime: str = "normal", stress_score: float = 0.0, inventory_delta: float = 0.0) -> RoutePlan:
        if not math.isfinite(target_qty):
            target_qty = 0.0
        if not math.isfinite(spot) or spot <= 0:
            spot = 50000.0
        if not math.isfinite(stress_score):
            stress_score = 0.0
        if not math.isfinite(inventory_delta):
            inventory_delta = 0.0
        warnings: List[str] = []
        orders: List[RouteOrder] = []
        if target_qty == 0:
            metrics = {"n_orders": 0.0, "total_notional": 0.0}
            return RoutePlan(ok=True, orders=[], total_notional=0.0, net_delta_est=0.0, delta_neutral_ok=True, metrics=metrics, warnings=warnings)
        side = "buy" if target_qty > 0 else "sell"
        qty_remain = abs(target_qty)
        # Split across venues with caps
        n = max(1, len(venues))
        base_alloc = 1.0 / n
        stress_mult_slip = 1.0 + max(0.0, stress_score) * 0.05
        for i, v in enumerate(venues):
            alloc = min(self.cfg.max_venue_alloc_pct, base_alloc * (1.0 + (i % 2) * 0.05))
            if i == n - 1:
                alloc = qty_remain / max(qty_remain / spot if spot > 0 else 1.0, 1e-12) / (qty_remain / spot) if False else 1.0  # adjust
            # simpler
            alloc_usd_cap = qty_remain * spot * alloc
            qty_v = alloc_usd_cap / spot if spot > 0 else 0.0
            if qty_v <= 0:
                continue
            slippage_bps = min(self.cfg.max_slippage_bps, self.cfg.fee_bps + 2.0 * stress_mult_slip)
            fee_usd = qty_v * spot * (self.cfg.fee_bps * 1e-4)
            notional = qty_v * spot
            if not math.isfinite(notional):
                warnings.append(f"finite_notional_{v}")
                continue
            orders.append(RouteOrder(venue=v, side=side, qty=qty_v, notional_usd=notional, slippage_bps=slippage_bps, fee_usd=fee_usd, valid=True))
            qty_remain -= qty_v
            if qty_remain < 1e-18:
                break
        total_notional = sum(o.notional_usd for o in orders)
        # delta neutral estimate (simplified)
        net_delta_est = inventory_delta + target_qty * 0.01  # small residual
        delta_neutral_ok = abs(net_delta_est) <= self.cfg.delta_neutral_tol * max(1.0, abs(target_qty))
        if not delta_neutral_ok:
            warnings.append("delta_neutral_tolerance_exceeded")
        metrics = {
            "n_orders": float(len(orders)),
            "total_notional": total_notional,
            "avg_slippage_bps": sum(o.slippage_bps for o in orders) / max(1, len(orders)),
            "total_fees_usd": sum(o.fee_usd for o in orders),
            "stress_mult_slip": stress_mult_slip,
        }
        for k, v in metrics.items():
            if isinstance(v, float) and not math.isfinite(v):
                metrics[k] = 0.0
        return RoutePlan(ok=True, orders=orders, total_notional=total_notional, net_delta_est=net_delta_est, delta_neutral_ok=delta_neutral_ok, metrics=metrics, warnings=warnings)
