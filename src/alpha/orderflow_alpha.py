"""Orderflow Alpha Features for crypto options context."""
from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.data.schemas import OrderflowSnapshot
from src.telemetry.serialization import serialize_metrics_strict


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


@dataclass
class OrderflowAlphaFeatures:
    symbol: str
    venue: str
    timestamp: str
    cumulative_delta: float
    delta_divergence: float
    absorption_score: float
    sweep_score: float
    vpin_lite: float
    liquidity_vacuum_score: float
    footprint_imbalance: float
    net_aggression: float
    large_trade_ratio: float
    valid: bool


class OrderflowAlphaEngine:
    def __init__(self, seed: int = 42):
        self.seed = int(seed)

    def extract_features(self, snap: OrderflowSnapshot) -> OrderflowAlphaFeatures:
        trades = snap.trades or []
        total_vol = 0.0
        buy_vol = 0.0
        sell_vol = 0.0
        large = 0.0
        for t in trades:
            sz = abs(_finite(t.size))
            total_vol += sz
            if str(t.side).lower() == "buy":
                buy_vol += sz
            elif str(t.side).lower() == "sell":
                sell_vol += sz
            if sz >= 1.0:
                large += sz
        cum_delta = buy_vol - sell_vol
        imb = (buy_vol - sell_vol) / total_vol if total_vol > 1e-18 else 0.0
        # divergence: delta vs recent price move proxy not directly available; use imbalance pattern
        delta_divergence = _finite(cum_delta / (total_vol + 1e-18))
        # absorption: large passive absorption vs aggression
        absorption_score = _finite(min(1.0, max(0.0, 1.0 - abs(imb))))
        # sweep detection heuristic
        sweep_score = _finite(min(1.0, max(0.0, large / (total_vol + 1e-18) * (1.0 if abs(imb) > 0.3 else 0.0))))
        # VPIN-lite
        vpin_lite = _finite(min(1.0, max(0.0, abs(imb))))
        # liquidity vacuum
        lv = 1.0 - min(1.0, total_vol / 1000.0) if total_vol >= 0 else 1.0
        liquidity_vacuum_score = _finite(min(1.0, max(0.0, lv)))
        footprint_imbalance = _finite(imb)
        net_aggression = _finite(imb)
        large_trade_ratio = _finite(large / (total_vol + 1e-18))
        valid = math.isfinite(cum_delta) and math.isfinite(vpin_lite)
        ts = snap.timestamp.isoformat().replace("+00:00", "Z") if hasattr(snap.timestamp, "isoformat") else str(snap.timestamp)
        return OrderflowAlphaFeatures(
            symbol=snap.symbol,
            venue=snap.venue,
            timestamp=ts,
            cumulative_delta=float(cum_delta),
            delta_divergence=float(delta_divergence),
            absorption_score=float(absorption_score),
            sweep_score=float(sweep_score),
            vpin_lite=float(vpin_lite),
            liquidity_vacuum_score=float(liquidity_vacuum_score),
            footprint_imbalance=float(footprint_imbalance),
            net_aggression=float(net_aggression),
            large_trade_ratio=float(large_trade_ratio),
            valid=bool(valid),
        )

    def generate_report(self, features_list: List[OrderflowAlphaFeatures]) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "git_sha": None,
            "seed": self.seed,
            "symbols": sorted(list({f.symbol for f in features_list})),
            "count": len(features_list),
            "features": [],
        }
        for f in features_list:
            report["features"].append({
                "symbol": f.symbol,
                "venue": f.venue,
                "timestamp": f.timestamp,
                "cumulative_delta": f.cumulative_delta,
                "delta_divergence": f.delta_divergence,
                "absorption_score": f.absorption_score,
                "sweep_score": f.sweep_score,
                "vpin_lite": f.vpin_lite,
                "liquidity_vacuum_score": f.liquidity_vacuum_score,
                "footprint_imbalance": f.footprint_imbalance,
                "net_aggression": f.net_aggression,
                "large_trade_ratio": f.large_trade_ratio,
                "valid": f.valid,
            })
        return serialize_metrics_strict(report)
