#!/usr/bin/env python3
import hashlib
import json
import math
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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
    h = hashlib.sha256(f"{seed}|p21agg|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


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
class AggregationConfig:
    seed: int = 42
    paper_only: bool = True
    max_delta_total: float = 2000.0
    max_gamma_total: float = 500.0
    max_vega_total: float = 50000.0
    max_theta_total: float = -150000.0
    max_notional_total: float = 5000000.0
    max_notional_per_symbol: float = 1000000.0
    max_notional_per_venue: float = 2000000.0
    max_concentration_pct: float = 0.35
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class ExposureSnapshot:
    snapshot_id: str
    strategy: str
    venue: str
    symbol: str
    notional_usd: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    open_qty: float
    paper_only: bool
    timestamp: str


class Phase21RiskAggregator:
    def __init__(self, config: Optional[AggregationConfig] = None, seed: int = 42):
        self.config = config or AggregationConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("Phase21RiskAggregator: paper_only must remain True")
        self.config = AggregationConfig(
            seed=int(self.config.seed),
            paper_only=True,
            max_delta_total=float(self.config.max_delta_total),
            max_gamma_total=float(self.config.max_gamma_total),
            max_vega_total=float(self.config.max_vega_total),
            max_theta_total=float(self.config.max_theta_total),
            max_notional_total=float(self.config.max_notional_total),
            max_notional_per_symbol=float(self.config.max_notional_per_symbol),
            max_notional_per_venue=float(self.config.max_notional_per_venue),
            max_concentration_pct=float(self.config.max_concentration_pct),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.breaches: List[Dict[str, Any]] = []
        self.audit: List[Dict[str, Any]] = []

    def _sid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p21agg|{self._counter}".encode()).hexdigest()[:12]
        return f"p21_snp_{h}"

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def aggregate_exposures(
        self,
        strategies: List[str],
        venues: List[str],
        symbols: List[str],
        seed_offset: int = 0,
    ) -> List[ExposureSnapshot]:
        self._log("aggregate_exposures", {"strategies": strategies, "venues": venues, "symbols": symbols})
        snaps: List[ExposureSnapshot] = []
        import random

        rng = random.Random(self.seed + seed_offset)
        idx = 0
        for strat in strategies:
            for venue in venues:
                for sym in symbols:
                    idx += 1
                    base_notional = rng.uniform(10000.0, 200000.0)
                    delta = rng.uniform(-0.4, 0.4)
                    gamma = rng.uniform(0.0005, 0.02)
                    vega = rng.uniform(500.0, 8000.0)
                    theta = rng.uniform(-12000.0, -500.0)
                    rho = rng.uniform(-100.0, 100.0)
                    qty = base_notional / 50000.0
                    snaps.append(
                        ExposureSnapshot(
                            snapshot_id=self._sid(),
                            strategy=str(strat),
                            venue=str(venue).lower(),
                            symbol=str(sym).upper(),
                            notional_usd=float(base_notional),
                            delta=float(delta * base_notional / 100000.0),
                            gamma=float(gamma * base_notional / 100000.0),
                            vega=float(vega * base_notional / 100000.0),
                            theta=float(theta * base_notional / 100000.0),
                            rho=float(rho),
                            open_qty=float(qty),
                            paper_only=True,
                            timestamp=_det_ts(self.seed, idx),
                        )
                    )
        _assert_no_nan_inf([asdict(s) for s in snaps], "phase21_exposures")
        return snaps

    def check_limits(self, snapshots: List[ExposureSnapshot]) -> Dict[str, Any]:
        self._log("check_limits", {"count": len(snapshots)})
        total_notional = sum(s.notional_usd for s in snapshots)
        total_delta = sum(s.delta for s in snapshots)
        total_gamma = sum(s.gamma for s in snapshots)
        total_vega = sum(s.vega for s in snapshots)
        total_theta = sum(s.theta for s in snapshots)

        by_symbol: Dict[str, float] = {}
        by_venue: Dict[str, float] = {}
        by_strategy: Dict[str, float] = {}
        for s in snapshots:
            by_symbol[s.symbol] = by_symbol.get(s.symbol, 0.0) + s.notional_usd
            by_venue[s.venue] = by_venue.get(s.venue, 0.0) + s.notional_usd
            by_strategy[s.strategy] = by_strategy.get(s.strategy, 0.0) + s.notional_usd

        breaches: List[Dict[str, Any]] = []
        if total_notional > self.config.max_notional_total + 1e-9:
            breaches.append({"type": "total_notional", "value": total_notional, "limit": self.config.max_notional_total, "severity": "block"})
        if abs(total_delta) > self.config.max_delta_total + 1e-9:
            breaches.append({"type": "total_delta", "value": total_delta, "limit": self.config.max_delta_total, "severity": "block"})
        if abs(total_gamma) > self.config.max_gamma_total + 1e-9:
            breaches.append({"type": "total_gamma", "value": total_gamma, "limit": self.config.max_gamma_total, "severity": "block"})
        if total_vega > self.config.max_vega_total + 1e-9:
            breaches.append({"type": "total_vega", "value": total_vega, "limit": self.config.max_vega_total, "severity": "block"})
        if total_theta < self.config.max_theta_total - 1e-9:  # more negative
            breaches.append({"type": "total_theta", "value": total_theta, "limit": self.config.max_theta_total, "severity": "block"})

        for sym, notional in by_symbol.items():
            if notional > self.config.max_notional_per_symbol + 1e-9:
                breaches.append({"type": "symbol_notional", "symbol": sym, "value": notional, "limit": self.config.max_notional_per_symbol, "severity": "block"})
            if total_notional > 0 and notional / total_notional > self.config.max_concentration_pct + 1e-9:
                breaches.append({"type": "symbol_concentration", "symbol": sym, "value": notional / total_notional, "limit": self.config.max_concentration_pct, "severity": "warn"})

        for venue, notional in by_venue.items():
            if notional > self.config.max_notional_per_venue + 1e-9:
                breaches.append({"type": "venue_notional", "venue": venue, "value": notional, "limit": self.config.max_notional_per_venue, "severity": "block"})

        self.breaches.extend(breaches)
        passed = len([b for b in breaches if b.get("severity") == "block"]) == 0 or not self.config.enforce_hard_limits
        if self.config.enforce_hard_limits and len([b for b in breaches if b.get("severity") == "block"]) > 0:
            passed = False

        rep = {
            "timestamp": _utc_now(),
            "totals": {
                "notional_usd": float(total_notional),
                "delta": float(total_delta),
                "gamma": float(total_gamma),
                "vega": float(total_vega),
                "theta": float(total_theta),
            },
            "by_symbol": {k: float(v) for k, v in by_symbol.items()},
            "by_venue": {k: float(v) for k, v in by_venue.items()},
            "by_strategy": {k: float(v) for k, v in by_strategy.items()},
            "breaches": breaches,
            "passed": bool(passed),
            "enforce_hard_limits": bool(self.config.enforce_hard_limits),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "phase21_agg_limits")
        return rep

    def generate_report(self, snapshots: List[ExposureSnapshot]) -> Dict[str, Any]:
        limits = self.check_limits(snapshots)
        rep = {
            "report": "PHASE21_RISK_AGGREGATION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "snapshot_count": len(snapshots),
            "snapshots": [asdict(s) for s in snapshots],
            "limits": limits,
            "audit": self.audit,
            "breaches_count": len(self.breaches),
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "phase21_agg_report")
        return rep
