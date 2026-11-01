"""PnL attribution by strategy/venue/instrument with deterministic reports.

Phase 14.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict


def _det_ts(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    from datetime import timedelta
    return (base + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


@dataclass
class AttributionConfig:
    include_fees: bool = True
    include_slippage: bool = True
    benchmark: str = "btc_spot"
    paper_only: bool = True


def default_attribution_config() -> AttributionConfig:
    return AttributionConfig()


class PerformanceAttributor:
    def __init__(self, config: Optional[AttributionConfig] = None, seed: int = 42):
        self.config = config or default_attribution_config()
        self.seed = int(seed)
        self.config.paper_only = True

    def attribute(
        self,
        by_strategy: Dict[str, float],
        by_venue: Dict[str, float],
        by_instrument: Dict[str, float],
        fees: float = 0.0,
        slippage: float = 0.0,
    ) -> Dict[str, Any]:
        for k, v in list(by_strategy.items()) + list(by_venue.items()) + list(by_instrument.items()):
            if not math.isfinite(v):
                raise ValueError(f"Non-finite pnl for {k}")
        fees_f = float(fees)
        slip_f = float(slippage)
        if fees_f < 0 or slip_f < 0 or not math.isfinite(fees_f) or not math.isfinite(slip_f):
            raise ValueError("fees/slippage must be non-negative finite")

        total_pnl = sum(by_strategy.values())
        net_pnl = total_pnl - fees_f - slip_f if self.config.include_fees or self.config.include_slippage else total_pnl
        if not math.isfinite(net_pnl):
            raise ValueError("net_pnl must be finite")

        rep = {
            "timestamp": _det_ts(self.seed),
            "by_strategy": {k: float(v) for k, v in by_strategy.items()},
            "by_venue": {k: float(v) for k, v in by_venue.items()},
            "by_instrument": {k: float(v) for k, v in by_instrument.items()},
            "fees": float(fees_f) if self.config.include_fees else 0.0,
            "slippage": float(slip_f) if self.config.include_slippage else 0.0,
            "total_pnl": float(total_pnl),
            "net_pnl": float(net_pnl),
            "benchmark": self.config.benchmark,
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)

    def generate_report(
        self,
        by_strategy: Dict[str, float],
        by_venue: Dict[str, float],
        by_instrument: Dict[str, float],
        fees: float = 0.0,
        slippage: float = 0.0,
    ) -> Dict[str, Any]:
        attr = self.attribute(by_strategy, by_venue, by_instrument, fees, slippage)
        rep = {
            "report": "PERFORMANCE_ATTRIBUTION_REPORT",
            "timestamp": _det_ts(self.seed),
            "seed": self.seed,
            "config": asdict(self.config),
            "attribution": attr,
            "counts": {
                "strategies": len(by_strategy),
                "venues": len(by_venue),
                "instruments": len(by_instrument),
            },
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
