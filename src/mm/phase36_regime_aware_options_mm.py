from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MMConfig:
    seed: int = 123456
    base_spread_bps: float = 12.0
    inv_skew_factor: float = 0.5
    max_inv_abs: float = 100.0
    regime_spread_mult: Dict[str, float] = field(
        default_factory=lambda: {"calm": 0.8, "normal": 1.0, "stressed": 1.6, "crisis": 2.5}
    )
    paper_only: bool = True


@dataclass
class Quote:
    side: str  # bid|ask
    px: float
    sz: float
    iv_quote: float
    valid: bool = True


@dataclass
class MMState:
    inventory: float
    regime: str
    stress_score: float
    pnl: float = 0.0


@dataclass
class QuoteBook:
    quotes: List[Quote]
    regime: str
    spread_bps: float
    inventory: float
    metrics: Dict[str, float]


class RegimeAwareOptionsMM:
    def __init__(self, cfg: MMConfig | None = None):
        self.cfg = cfg or MMConfig()
        if not self.cfg.paper_only:
            raise ValueError("live MM paths must be explicitly gated; default paper_only True")

    def _finite(self, x: float) -> bool:
        return math.isfinite(x)

    def quote(self, mid_iv: float, spot: float, t: float, k: float, state: MMState, orderflow_imb: float = 0.0) -> QuoteBook:
        if not self._finite(mid_iv) or mid_iv <= 0:
            mid_iv = 0.5
        if not self._finite(spot) or spot <= 0:
            spot = 100.0
        if not self._finite(t) or t <= 0:
            t = 0.01
        if not self._finite(k) or k <= 0:
            k = spot
        if not self._finite(state.inventory):
            state.inventory = 0.0
        inv_clip = max(-self.cfg.max_inv_abs, min(self.cfg.max_inv_abs, state.inventory))
        regime_mult = self.cfg.regime_spread_mult.get(state.regime, 1.0)
        stress_mult = 1.0 + max(0.0, state.stress_score) * 0.1
        of_mult = 1.0 + abs(orderflow_imb) * 0.3
        spread_bps = self.cfg.base_spread_bps * regime_mult * stress_mult * of_mult
        if not self._finite(spread_bps) or spread_bps < 1.0:
            spread_bps = self.cfg.base_spread_bps
        half = spread_bps * 1e-4 * 0.5
        # Inventory skew
        inv_skew = (inv_clip / max(self.cfg.max_inv_abs, 1e-12)) * self.cfg.inv_skew_factor * half
        # Orderflow skew
        of_skew = orderflow_imb * 0.2 * half
        bid_iv = mid_iv * (1.0 - half - inv_skew - of_skew)
        ask_iv = mid_iv * (1.0 + half - inv_skew - of_skew)  # keep inventory effect
        if not self._finite(bid_iv) or bid_iv <= 1e-6:
            bid_iv = max(1e-6, mid_iv * 0.9)
        if not self._finite(ask_iv) or ask_iv <= 1e-6:
            ask_iv = max(1e-6, mid_iv * 1.1)
        # Simple size
        base_sz = max(1.0, 10.0 * (1.0 / max(spread_bps / 10.0, 1.0)))
        inv_adj = max(0.2, 1.0 - abs(inv_clip) / (self.cfg.max_inv_abs * 2.0))
        bid_sz = base_sz * inv_adj * (1.0 - min(0.5, max(0.0, orderflow_imb)))
        ask_sz = base_sz * inv_adj * (1.0 + min(0.5, max(0.0, orderflow_imb)))
        if bid_sz <= 0:
            bid_sz = 0.1
        if ask_sz <= 0:
            ask_sz = 0.1
        bid_px = spot * math.exp(-0.5 * bid_iv * bid_iv * t)
        ask_px = spot * math.exp(-0.5 * ask_iv * ask_iv * t)
        if not (bid_px < ask_px):
            # enforce ordering
            mid_px = spot * math.exp(-0.5 * mid_iv * mid_iv * t)
            adj = max(1e-10, spread_bps * 1e-4 * spot * 0.01)
            bid_px = mid_px - adj
            ask_px = mid_px + adj
        quotes = [
            Quote(side="bid", px=bid_px, sz=bid_sz, iv_quote=bid_iv),
            Quote(side="ask", px=ask_px, sz=ask_sz, iv_quote=ask_iv),
        ]
        metrics = {
            "spread_bps": spread_bps,
            "inv_clip": inv_clip,
            "regime_mult": regime_mult,
            "stress_mult": stress_mult,
            "of_mult": of_mult,
            "half_iv_adj": half,
        }
        return QuoteBook(quotes=quotes, regime=state.regime, spread_bps=spread_bps, inventory=state.inventory, metrics=metrics)
