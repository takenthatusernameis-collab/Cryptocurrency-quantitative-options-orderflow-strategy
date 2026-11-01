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
class AlphaDecayConfig:
    seed: int = 42
    paper_only: bool = True
    decay_halflife_bars: int = 12
    ic_threshold: float = 0.02
    monitor_window: int = 50
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class AlphaDecayState:
    decay_id: str
    symbol: str
    strategy: str
    timestamp: str
    alpha_level: float
    half_life_bars: float
    ic_current: float
    ic_decay_rate: float
    alpha_quality: str  # good|degraded|poor
    decay_factor: float
    time_to_decay: float
    paper_only: bool


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p23_{tag}_{h}"


class AlphaDecay:
    def __init__(self, config: Optional[AlphaDecayConfig] = None, seed: int = 42):
        self.config = config or AlphaDecayConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("AlphaDecay: paper_only must remain True")
        self.config = AlphaDecayConfig(
            seed=int(self.config.seed),
            paper_only=True,
            decay_halflife_bars=int(self.config.decay_halflife_bars),
            ic_threshold=float(self.config.ic_threshold),
            monitor_window=int(self.config.monitor_window),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def compute_half_life(self, ic_series: List[float]) -> float:
        if not ic_series or len(ic_series) < 2:
            return float(self.config.decay_halflife_bars)
        # approximate exponential decay fit
        # use log of absolute IC
        vals = []
        for i, ic in enumerate(ic_series):
            if abs(ic) > 1e-12:
                vals.append((i, math.log(abs(ic))))
        if len(vals) < 2:
            return float(self.config.decay_halflife_bars)
        # linear fit
        n = len(vals)
        sumx = sum(v[0] for v in vals)
        sumy = sum(v[1] for v in vals)
        sumxy = sum(v[0] * v[1] for v in vals)
        sumx2 = sum(v[0] * v[0] for v in vals)
        slope = (n * sumxy - sumx * sumy) / (n * sumx2 - sumx * sumx + 1e-18)
        if slope >= 0:  # not decaying
            return float(self.config.decay_halflife_bars) * 2.0
        half_life = math.log(0.5) / slope  # slope negative
        if half_life <= 0 or not math.isfinite(half_life):
            half_life = float(self.config.decay_halflife_bars)
        return float(max(1.0, min(200.0, half_life)))

    def monitor(self, symbol: str, strategy: str, alpha_level: float, ic_series: Optional[List[float]] = None, idx: int = 0) -> AlphaDecayState:
        symbol = str(symbol).upper()
        strategy = str(strategy)
        alpha_level = float(alpha_level)
        ic_series = list(ic_series) if ic_series is not None else []
        if not ic_series:
            import random
            rng = random.Random(self.seed + 24000 + idx)
            ic_series = [rng.gauss(0.05, 0.01) * (0.9 ** i) for i in range(self.config.monitor_window)]
        ic_current = float(ic_series[-1]) if ic_series else 0.0
        if len(ic_series) >= 2:
            ic_decay_rate = float(ic_series[0] - ic_series[-1]) / len(ic_series) if ic_series[0] != 0 else 0.0
        else:
            ic_decay_rate = 0.0
        half_life = self.compute_half_life(ic_series)
        decay_factor = float(math.exp(-1.0 / (half_life + 1e-12)))
        time_to_decay = float(half_life * (math.log(self.config.ic_threshold / (abs(ic_current) + 1e-12)) / math.log(decay_factor + 1e-12))) if abs(ic_current) > self.config.ic_threshold and decay_factor < 1.0 else float(half_life * 2.0)
        if time_to_decay < 0 or not math.isfinite(time_to_decay):
            time_to_decay = float(half_life)
        if ic_current >= self.config.ic_threshold and alpha_level >= 0.2:
            alpha_quality = "good"
        elif ic_current >= self.config.ic_threshold * 0.5:
            alpha_quality = "degraded"
        else:
            alpha_quality = "poor"
        st = AlphaDecayState(
            decay_id=_make_id(self.seed, "decay", idx),
            symbol=symbol,
            strategy=strategy,
            timestamp=_utc_now(),
            alpha_level=float(max(-1.0, min(1.0, alpha_level))),
            half_life_bars=float(half_life),
            ic_current=float(ic_current),
            ic_decay_rate=float(ic_decay_rate),
            alpha_quality=alpha_quality,
            decay_factor=float(decay_factor),
            time_to_decay=float(time_to_decay),
            paper_only=True,
        )
        _assert_no_nan_inf(asdict(st), "AlphaDecayState")
        self._log("monitor", asdict(st))
        return st

    def generate_report(self, states: List[AlphaDecayState]) -> Dict[str, Any]:
        rep = {
            "report": "PHASE23_ALPHA_DECAY_REPORT",
            "timestamp": _utc_now(),
            "seed": int(self.seed),
            "config": asdict(self.config),
            "decay_count": len(states),
            "decay_states": [asdict(s) for s in states],
            "paper_only": True,
        }
        if states:
            rep["summary"] = {
                "avg_half_life_bars": float(sum(s.half_life_bars for s in states) / len(states)),
                "avg_ic_current": float(sum(s.ic_current for s in states) / len(states)),
                "good_count": sum(1 for s in states if s.alpha_quality == "good"),
                "degraded_count": sum(1 for s in states if s.alpha_quality == "degraded"),
                "poor_count": sum(1 for s in states if s.alpha_quality == "poor"),
                "avg_time_to_decay": float(sum(s.time_to_decay for s in states) / len(states)),
            }
        else:
            rep["summary"] = {}
        _assert_no_nan_inf(rep, "PHASE23_ALPHA_DECAY_REPORT")
        return rep
