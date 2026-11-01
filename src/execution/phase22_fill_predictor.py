#!/usr/bin/env python3
import hashlib
import math
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _det_ts(seed: int, idx: int = 0) -> str:
    h = hashlib.sha256(f"{seed}|p22fill|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p22_{tag}_{h}"


def _assert_no_nan_inf(obj: Any, label: str) -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


@dataclass(frozen=True)
class FillConfig:
    seed: int = 42
    paper_only: bool = True
    base_fill_prob: float = 0.85
    spread_sensitivity: float = 0.04
    depth_sensitivity: float = 0.03
    latency_sensitivity: float = 0.02
    orderflow_weight: float = 0.25
    enforce_hard_limits: bool = True
    min_fill_prob: float = 0.05


@dataclass(frozen=True)
class FillSignal:
    signal_id: str
    symbol: str
    venue: str
    side: str
    qty: float
    notional_usd: float
    spread_bps: float
    depth_usd: float
    latency_ms: float
    orderflow_confirmed: bool
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class FillPrediction:
    prediction_id: str
    signal_id: str
    symbol: str
    venue: str
    fill_probability: float
    expected_fill_price: float
    expected_fill_qty: float
    expected_time_ms: float
    confidence: float
    paper_only: bool
    timestamp: str


class FillPredictor:
    def __init__(self, config: Optional[FillConfig] = None, seed: int = 42):
        self.config = config or FillConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("FillPredictor: paper_only must remain True")
        self.config = FillConfig(
            seed=int(self.config.seed),
            paper_only=True,
            base_fill_prob=float(self.config.base_fill_prob),
            spread_sensitivity=float(self.config.spread_sensitivity),
            depth_sensitivity=float(self.config.depth_sensitivity),
            latency_sensitivity=float(self.config.latency_sensitivity),
            orderflow_weight=float(self.config.orderflow_weight),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
            min_fill_prob=float(self.config.min_fill_prob),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _sid(self, idx: int) -> str:
        return _make_id(self.seed, "sig", idx)

    def _pid(self, idx: int) -> str:
        return _make_id(self.seed, "pred", idx)

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def make_signal(self, symbol: str, venue: str, side: str, qty: float, notional_usd: float, spread_bps: float, depth_usd: float, latency_ms: float, orderflow_confirmed: bool, idx: int = 0) -> FillSignal:
        import random

        rng = random.Random(self.seed + 5000 + idx)
        symbol = str(symbol).upper()
        venue = str(venue).lower()
        side = str(side).lower()
        mid = rng.uniform(80000.0, 120000.0) if symbol == "BTC" else rng.uniform(2000.0, 4000.0)
        return FillSignal(
            signal_id=self._sid(idx),
            symbol=symbol,
            venue=venue,
            side=side,
            qty=float(qty),
            notional_usd=float(notional_usd),
            spread_bps=float(spread_bps),
            depth_usd=float(depth_usd),
            latency_ms=float(latency_ms),
            orderflow_confirmed=bool(orderflow_confirmed),
            paper_only=True,
            timestamp=_det_ts(self.seed, idx),
        )

    def predict(self, signal: FillSignal, idx: int = 0) -> FillPrediction:
        self._log("predict", {"signal_id": signal.signal_id, "symbol": signal.symbol})
        spread_pen = min(0.5, signal.spread_bps * self.config.spread_sensitivity)
        depth_pen = min(0.3, max(0.0, (1000000.0 - signal.depth_usd) / 1000000.0) * self.config.depth_sensitivity)
        lat_pen = min(0.2, signal.latency_ms / 1000.0 * self.config.latency_sensitivity)
        of_bonus = self.config.orderflow_weight if signal.orderflow_confirmed else -self.config.orderflow_weight
        fill_prob = self.config.base_fill_prob - spread_pen - depth_pen - lat_pen + of_bonus
        fill_prob = float(max(self.config.min_fill_prob, min(0.99, fill_prob)))
        mid = 90000.0 if signal.symbol == "BTC" else 3000.0
        side_mult = 1.0 + (signal.spread_bps / 20000.0) if signal.side == "buy" else 1.0 - (signal.spread_bps / 20000.0)
        expected_price = mid * side_mult
        expected_qty = signal.qty * fill_prob
        expected_time_ms = signal.latency_ms * (1.0 / fill_prob)
        confidence = 1.0 - abs(fill_prob - 0.5)
        rep = {
            "prediction_id": self._pid(idx),
            "signal_id": signal.signal_id,
            "symbol": signal.symbol,
            "venue": signal.venue,
            "fill_probability": float(fill_prob),
            "expected_fill_price": float(expected_price),
            "expected_fill_qty": float(expected_qty),
            "expected_time_ms": float(expected_time_ms),
            "confidence": float(confidence),
            "paper_only": True,
            "timestamp": _det_ts(self.seed, idx),
        }
        _assert_no_nan_inf(rep, "p22_fill_prediction")
        return FillPrediction(
            prediction_id=rep["prediction_id"],
            signal_id=rep["signal_id"],
            symbol=rep["symbol"],
            venue=rep["venue"],
            fill_probability=rep["fill_probability"],
            expected_fill_price=rep["expected_fill_price"],
            expected_fill_qty=rep["expected_fill_qty"],
            expected_time_ms=rep["expected_time_ms"],
            confidence=rep["confidence"],
            paper_only=True,
            timestamp=rep["timestamp"],
        )

    def generate_report(self, signals: List[FillSignal], predictions: List[FillPrediction]) -> Dict[str, Any]:
        avg_prob = float(sum(p.fill_probability for p in predictions) / len(predictions)) if predictions else 0.0
        avg_price = float(sum(p.expected_fill_price for p in predictions) / len(predictions)) if predictions else 0.0
        rep = {
            "report": "PHASE22_FILL_PREDICTION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "signal_count": len(signals),
            "prediction_count": len(predictions),
            "signals": [asdict(s) for s in signals],
            "predictions": [asdict(p) for p in predictions],
            "summary": {
                "avg_fill_probability": float(avg_prob),
                "avg_expected_fill_price": float(avg_price),
                "paper_only": True,
            },
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p22_fill_report")
        return rep
