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
class SignalFusionConfig:
    seed: int = 42
    paper_only: bool = True
    base_weights: tuple = (0.4, 0.3, 0.2, 0.1)  # orderflow, vol, flow_toxicity_adjusted, other
    regime_adaptive: bool = True
    normalize_weights: bool = True
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class FusedSignal:
    fusion_id: str
    symbol: str
    regime: str
    timestamp: str
    raw_signals: Dict[str, float]
    weights: Dict[str, float]
    fused_score: float
    direction: str
    conviction: float
    risk_adjusted: float
    paper_only: bool


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p23_{tag}_{h}"


class SignalFusion:
    def __init__(self, config: Optional[SignalFusionConfig] = None, seed: int = 42):
        self.config = config or SignalFusionConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("SignalFusion: paper_only must remain True")
        self.config = SignalFusionConfig(
            seed=int(self.config.seed),
            paper_only=True,
            base_weights=tuple(float(w) for w in self.config.base_weights),
            regime_adaptive=bool(self.config.regime_adaptive),
            normalize_weights=bool(self.config.normalize_weights),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def adaptive_weights(self, regime: str) -> Dict[str, float]:
        regime = str(regime).lower()
        if regime == "trend":
            w = {"orderflow": 0.5, "vol": 0.2, "cross_asset": 0.2, "other": 0.1}
        elif regime == "mean_reversion":
            w = {"orderflow": 0.3, "vol": 0.3, "cross_asset": 0.2, "other": 0.2}
        elif regime == "vol":
            w = {"orderflow": 0.25, "vol": 0.4, "cross_asset": 0.25, "other": 0.1}
        elif regime == "range":
            w = {"orderflow": 0.35, "vol": 0.25, "cross_asset": 0.25, "other": 0.15}
        else:
            w = {"orderflow": 0.4, "vol": 0.3, "cross_asset": 0.2, "other": 0.1}
        if self.config.normalize_weights:
            s = sum(w.values())
            if s > 0:
                w = {k: v / s for k, v in w.items()}
        return w

    def fuse(self, symbol: str, regime: str, raw_signals: Dict[str, float], idx: int = 0) -> FusedSignal:
        symbol = str(symbol).upper()
        regime = str(regime).lower()
        weights = self.adaptive_weights(regime) if self.config.regime_adaptive else {"orderflow": 0.4, "vol": 0.3, "cross_asset": 0.2, "other": 0.1}
        fused = 0.0
        for k, v in raw_signals.items():
            wk = weights.get(k, 0.1)
            fused += float(v) * wk
        fused = float(max(-1.0, min(1.0, fused)))
        if fused > 0.15:
            direction = "long"
        elif fused < -0.15:
            direction = "short"
        else:
            direction = "neutral"
        conviction = float(min(1.0, max(0.0, abs(fused) * 1.5)))
        risk_adj = float(fused / (1.0 + abs(fused) * 0.3))
        fs = FusedSignal(
            fusion_id=_make_id(self.seed, "fus", idx),
            symbol=symbol,
            regime=regime,
            timestamp=_utc_now(),
            raw_signals={k: float(v) for k, v in raw_signals.items()},
            weights={k: float(v) for k, v in weights.items()},
            fused_score=float(fused),
            direction=direction,
            conviction=float(conviction),
            risk_adjusted=float(risk_adj),
            paper_only=True,
        )
        _assert_no_nan_inf(asdict(fs), "FusedSignal")
        self._log("fuse", asdict(fs))
        return fs

    def generate_report(self, fused_list: List[FusedSignal]) -> Dict[str, Any]:
        rep = {
            "report": "PHASE23_SIGNAL_FUSION_REPORT",
            "timestamp": _utc_now(),
            "seed": int(self.seed),
            "config": asdict(self.config),
            "fused_count": len(fused_list),
            "fused_signals": [asdict(f) for f in fused_list],
            "paper_only": True,
        }
        if fused_list:
            rep["summary"] = {
                "avg_fused_score": float(sum(f.fused_score for f in fused_list) / len(fused_list)),
                "avg_conviction": float(sum(f.conviction for f in fused_list) / len(fused_list)),
                "long_count": sum(1 for f in fused_list if f.direction == "long"),
                "short_count": sum(1 for f in fused_list if f.direction == "short"),
                "neutral_count": sum(1 for f in fused_list if f.direction == "neutral"),
                "regimes": list(set(f.regime for f in fused_list)),
            }
        else:
            rep["summary"] = {}
        _assert_no_nan_inf(rep, "PHASE23_SIGNAL_FUSION_REPORT")
        return rep
