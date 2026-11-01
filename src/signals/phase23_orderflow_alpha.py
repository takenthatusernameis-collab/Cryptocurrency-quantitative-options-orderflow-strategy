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
    h = hashlib.sha256(f"{seed}|p23of|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T15:{h[:2]}:{h[2:4]}Z"


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
class OrderflowAlphaConfig:
    seed: int = 42
    paper_only: bool = True
    imbalance_threshold: float = 0.15
    toxic_flow_z: float = 2.5
    tape_window_ms: int = 100
    enable_tape_reading: bool = True
    enable_toxic_detection: bool = True
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class OrderflowSignal:
    signal_id: str
    symbol: str
    venue: str
    timestamp: str
    bid_volume: float
    ask_volume: float
    imbalance: float
    tape_pressure: float
    toxic_score: float
    is_toxic: bool
    alpha_score: float
    direction: str
    confidence: float
    paper_only: bool


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p23_{tag}_{h}"


class OrderflowAlpha:
    def __init__(self, config: Optional[OrderflowAlphaConfig] = None, seed: int = 42):
        self.config = config or OrderflowAlphaConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("OrderflowAlpha: paper_only must remain True")
        self.config = OrderflowAlphaConfig(
            seed=int(self.config.seed),
            paper_only=True,
            imbalance_threshold=float(self.config.imbalance_threshold),
            toxic_flow_z=float(self.config.toxic_flow_z),
            tape_window_ms=int(self.config.tape_window_ms),
            enable_tape_reading=bool(self.config.enable_tape_reading),
            enable_toxic_detection=bool(self.config.enable_toxic_detection),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def compute_imbalance(self, bid_vol: float, ask_vol: float) -> float:
        bid_vol = float(max(0.0, bid_vol))
        ask_vol = float(max(0.0, ask_vol))
        total = bid_vol + ask_vol
        if total <= 0.0:
            return 0.0
        imb = (bid_vol - ask_vol) / total
        return float(max(-1.0, min(1.0, imb)))

    def detect_toxic_flow(self, imbalance: float, trade_intensity: float, z: float = 0.0) -> tuple:
        imb = float(imbalance)
        tint = float(max(0.0, trade_intensity))
        score = abs(imb) * math.log1p(tint) + abs(float(z))
        thr = float(self.config.toxic_flow_z)
        is_toxic = score >= thr
        score = float(max(0.0, min(10.0, score)))
        return is_toxic, score

    def tape_pressure(self, recent_imbalance: List[float], weights: Optional[List[float]] = None) -> float:
        if not recent_imbalance:
            return 0.0
        n = len(recent_imbalance)
        if weights is None:
            weights = [math.exp(-i * 0.2) for i in range(n)]
        ws = sum(weights)
        if ws <= 0.0:
            weights = [1.0 / n] * n
            ws = 1.0
        else:
            weights = [w / ws for w in weights]
        pres = sum(w * float(v) for w, v in zip(weights, recent_imbalance))
        return float(max(-1.0, min(1.0, pres)))

    def generate_signal(self, symbol: str, venue: str, bid_vol: float, ask_vol: float, trade_intensity: float, recent_imbalance: Optional[List[float]] = None, idx: int = 0) -> OrderflowSignal:
        symbol = str(symbol).upper()
        venue = str(venue).lower()
        imb = self.compute_imbalance(bid_vol, ask_vol)
        recent_imbalance = list(recent_imbalance) if recent_imbalance is not None else []
        pres = self.tape_pressure(recent_imbalance + [imb], None) if self.config.enable_tape_reading else imb
        import random
        rng = random.Random(self.seed + 23000 + idx)
        z = rng.gauss(0.0, 1.0)
        is_toxic, tox_score = self.detect_toxic_flow(pres, trade_intensity, z) if self.config.enable_toxic_detection else (False, 0.0)
        if is_toxic:
            alpha = float(abs(imb)) * 0.3 - tox_score * 0.1
        else:
            alpha = float(abs(imb)) * 0.8 + abs(pres) * 0.4
        alpha = float(max(-1.0, min(1.0, alpha)))
        if imb > self.config.imbalance_threshold:
            direction = "buy"
        elif imb < -self.config.imbalance_threshold:
            direction = "sell"
        else:
            direction = "neutral"
        conf = float(min(1.0, max(0.0, abs(imb) + abs(pres) * 0.2 - tox_score * 0.05)))
        sig = OrderflowSignal(
            signal_id=_make_id(self.seed, "of", idx),
            symbol=symbol,
            venue=venue,
            timestamp=_det_ts(self.seed, idx),
            bid_volume=float(bid_vol),
            ask_volume=float(ask_vol),
            imbalance=float(imb),
            tape_pressure=float(pres),
            toxic_score=float(tox_score),
            is_toxic=bool(is_toxic),
            alpha_score=float(alpha),
            direction=direction,
            confidence=float(conf),
            paper_only=True,
        )
        _assert_no_nan_inf(asdict(sig), "OrderflowSignal")
        self._log("generate_signal", asdict(sig))
        return sig

    def generate_report(self, signals: List[OrderflowSignal]) -> Dict[str, Any]:
        rep = {
            "report": "PHASE23_ORDERFLOW_ALPHA_REPORT",
            "timestamp": _utc_now(),
            "seed": int(self.seed),
            "config": asdict(self.config),
            "signal_count": len(signals),
            "signals": [asdict(s) for s in signals],
            "paper_only": True,
        }
        if signals:
            imbs = [s.imbalance for s in signals]
            alphas = [s.alpha_score for s in signals]
            tox = sum(1 for s in signals if s.is_toxic)
            rep["summary"] = {
                "avg_imbalance": float(sum(imbs) / len(imbs)),
                "avg_alpha_score": float(sum(alphas) / len(alphas)),
                "toxic_count": int(tox),
                "toxic_rate": float(tox / len(signals)),
                "buy_count": sum(1 for s in signals if s.direction == "buy"),
                "sell_count": sum(1 for s in signals if s.direction == "sell"),
                "neutral_count": sum(1 for s in signals if s.direction == "neutral"),
            }
        else:
            rep["summary"] = {}
        _assert_no_nan_inf(rep, "PHASE23_ORDERFLOW_ALPHA_REPORT")
        return rep
