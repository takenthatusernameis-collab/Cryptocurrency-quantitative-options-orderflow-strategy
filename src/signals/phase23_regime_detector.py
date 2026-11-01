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
class RegimeDetectorConfig:
    seed: int = 42
    paper_only: bool = True
    vol_window: int = 20
    trend_threshold: float = 0.02
    mr_threshold: float = 0.01
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class RegimeState:
    state_id: str
    symbol: str
    timestamp: str
    regime: str  # vol|trend|mean_reversion|range
    vol_regime: str  # low|med|high
    trend_strength: float
    mr_score: float
    confidence: float
    features: Dict[str, float]
    paper_only: bool


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p23_{tag}_{h}"


class RegimeDetector:
    def __init__(self, config: Optional[RegimeDetectorConfig] = None, seed: int = 42):
        self.config = config or RegimeDetectorConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("RegimeDetector: paper_only must remain True")
        self.config = RegimeDetectorConfig(
            seed=int(self.config.seed),
            paper_only=True,
            vol_window=int(self.config.vol_window),
            trend_threshold=float(self.config.trend_threshold),
            mr_threshold=float(self.config.mr_threshold),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def classify_regime(self, symbol: str, returns: List[float], price_level: float, idx: int = 0) -> RegimeState:
        symbol = str(symbol).upper()
        rets = [float(r) for r in returns]
        if not rets:
            rets = [0.0]
        n = len(rets)
        mean_r = sum(rets) / n
        var = sum((r - mean_r) ** 2 for r in rets) / n if n > 0 else 0.0
        vol = math.sqrt(max(0.0, var))
        trend_strength = float(abs(mean_r) / (vol + 1e-12))
        # mean reversion score: negative autocorr-ish proxy
        if n >= 2:
            mr_score = float(abs(sum(rets[i] * rets[i - 1] for i in range(1, n))) / n)
        else:
            mr_score = 0.0
        if vol < 0.01:
            vol_regime = "low"
        elif vol < 0.03:
            vol_regime = "med"
        else:
            vol_regime = "high"
        if trend_strength > self.config.trend_threshold and vol_regime != "low":
            regime = "trend"
        elif mr_score > self.config.mr_threshold:
            regime = "mean_reversion"
        elif vol_regime == "low":
            regime = "range"
        else:
            regime = "vol"
        conf = float(min(1.0, max(0.0, trend_strength + mr_score + (0.3 if vol_regime == "high" else 0.1))))
        st = RegimeState(
            state_id=_make_id(self.seed, "reg", idx),
            symbol=symbol,
            timestamp=_utc_now(),
            regime=regime,
            vol_regime=vol_regime,
            trend_strength=float(trend_strength),
            mr_score=float(mr_score),
            confidence=float(conf),
            features={
                "mean_return": float(mean_r),
                "volatility": float(vol),
                "n_obs": float(n),
                "price_level": float(price_level),
            },
            paper_only=True,
        )
        _assert_no_nan_inf(asdict(st), "RegimeState")
        self._log("classify_regime", asdict(st))
        return st

    def generate_report(self, states: List[RegimeState]) -> Dict[str, Any]:
        rep = {
            "report": "PHASE23_REGIME_DETECTION_REPORT",
            "timestamp": _utc_now(),
            "seed": int(self.seed),
            "config": asdict(self.config),
            "state_count": len(states),
            "states": [asdict(s) for s in states],
            "paper_only": True,
        }
        if states:
            rep["summary"] = {
                "trend_count": sum(1 for s in states if s.regime == "trend"),
                "mean_reversion_count": sum(1 for s in states if s.regime == "mean_reversion"),
                "range_count": sum(1 for s in states if s.regime == "range"),
                "vol_count": sum(1 for s in states if s.regime == "vol"),
                "low_vol": sum(1 for s in states if s.vol_regime == "low"),
                "med_vol": sum(1 for s in states if s.vol_regime == "med"),
                "high_vol": sum(1 for s in states if s.vol_regime == "high"),
                "avg_confidence": float(sum(s.confidence for s in states) / len(states)),
            }
        else:
            rep["summary"] = {}
        _assert_no_nan_inf(rep, "PHASE23_REGIME_DETECTION_REPORT")
        return rep
