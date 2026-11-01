"""Sizing & Portfolio Construction."""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


@dataclass
class SizedPosition:
    intent_id: str
    symbol: str
    side: str
    qty: float
    notional_usd: float
    delta_usd: float
    vega_usd: float
    gamma_usd: float
    weight: float
    reason: str


class PositionSizer:
    def __init__(self, capital: float = 100000.0, seed: int = 42,
                 kelly_frac: float = 0.25,
                 drawdown_penalty: float = 0.5,
                 max_notional_pct: float = 0.02,
                 max_vega_pct: float = 0.01,
                 max_delta_abs: float = 5000.0,
                 corr_dedup: bool = True):
        self.capital = float(capital)
        self.seed = int(seed)
        self.kelly_frac = float(kelly_frac)
        self.drawdown_penalty = float(drawdown_penalty)
        self.max_notional_pct = float(max_notional_pct)
        self.max_vega_pct = float(max_vega_pct)
        self.max_delta_abs = float(max_delta_abs)
        self.corr_dedup = bool(corr_dedup)

    def size(self, intents: List[Any]) -> List[SizedPosition]:
        sized: List[SizedPosition] = []
        # simple correlation-aware dedup by symbol
        seen = set()
        for it in intents:
            sym = getattr(it, "symbol")
            if self.corr_dedup and sym in seen:
                continue  # de-dup
            seen.add(sym)
            conf = _finite(getattr(it, "confidence", 0.1))
            kelly = self.kelly_frac * conf
            kelly = max(0.0, min(0.1, kelly))  # cap
            dd_adj = kelly * (1.0 - self.drawdown_penalty * 0.1)
            dd_adj = max(0.0, dd_adj)
            notional = self.capital * dd_adj
            notional = min(notional, self.capital * self.max_notional_pct)
            qty = notional / 1000.0  # simplified
            qty = max(0.001, qty)
            delta_est = _finite(getattr(it, "delta_est", 0.0))
            vega_est = _finite(getattr(it, "vega_est", 0.0))
            gamma_est = _finite(getattr(it, "gamma_est", 0.0))
            delta_usd = delta_est * notional
            vega_usd = vega_est * notional
            gamma_usd = gamma_est * notional
            if abs(delta_usd) > self.max_delta_abs:
                continue  # risk cap
            if abs(vega_usd) > self.capital * self.max_vega_pct:
                continue
            sized.append(SizedPosition(
                intent_id=getattr(it, "intent_id"),
                symbol=sym,
                side=getattr(it, "side"),
                qty=float(qty),
                notional_usd=float(notional),
                delta_usd=float(delta_usd),
                vega_usd=float(vega_usd),
                gamma_usd=float(gamma_usd),
                weight=float(notional / self.capital),
                reason="kelly_lite_dd_corr_dedup",
            ))
        sized.sort(key=lambda x: (-x.weight, x.symbol))
        return sized

    def generate_report(self, sized: List[SizedPosition]) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "git_sha": None,
            "seed": self.seed,
            "count": len(sized),
            "total_notional": sum(s.notional_usd for s in sized),
            "total_weight": sum(s.weight for s in sized),
            "positions": [asdict(s) for s in sized],
        }
        return serialize_metrics_strict(report)
