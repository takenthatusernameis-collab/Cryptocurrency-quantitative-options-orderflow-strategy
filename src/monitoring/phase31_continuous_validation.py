"""
Phase 31: Continuous Validation Engine for Crypto Options Vol Surface Arbitrage + Orderflow.

Real-time invariant checks, drift detection, alerting.
Production-grade, deterministic, finite numerics. PAPER-ONLY by default.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p31val|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p31_{tag}_{h}"


def _assert_finite(obj: Any, label: str = "obj") -> None:
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
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class ValidationConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    max_drawdown_pct: float = 0.08
    max_var_pct: float = 0.04
    max_iv_skew_bps: float = 25.0
    min_sharpe: float = 0.5
    max_fill_reject_rate: float = 0.15
    max_latency_p95_ms: float = 200.0
    drift_zscore_threshold: float = 3.0
    enforce_gates: bool = True


@dataclass(frozen=True)
class InvariantCheck:
    name: str
    passed: bool
    value: float
    threshold: float
    direction: str  # "lte" or "gte"
    detail: str


@dataclass(frozen=True)
class DriftCheck:
    metric: str
    baseline: float
    current: float
    drift_pct: float
    zscore: float
    drifted: bool


@dataclass(frozen=True)
class Alert:
    alert_id: str
    severity: str  # "info", "warn", "critical"
    message: str
    metric: str
    value: float
    threshold: float
    timestamp: str


@dataclass(frozen=True)
class ValidationResult:
    cycle: int
    timestamp: str
    all_ok: bool
    invariants: Tuple[InvariantCheck, ...]
    drift: Tuple[DriftCheck, ...]
    alerts: Tuple[Alert, ...]
    paper_only: bool


class ContinuousValidationEngine:
    def __init__(self, config: Optional[ValidationConfig] = None, seed: int = 42) -> None:
        self.config = config or ValidationConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "ContinuousValidationEngine: paper_only must remain True (live path hard-gated)"
            )
        self.config = ValidationConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            max_drawdown_pct=float(self.config.max_drawdown_pct),
            max_var_pct=float(self.config.max_var_pct),
            max_iv_skew_bps=float(self.config.max_iv_skew_bps),
            min_sharpe=float(self.config.min_sharpe),
            max_fill_reject_rate=float(self.config.max_fill_reject_rate),
            max_latency_p95_ms=float(self.config.max_latency_p95_ms),
            drift_zscore_threshold=float(self.config.drift_zscore_threshold),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.baselines: Dict[str, float] = {}
        self.results: List[ValidationResult] = []
        self.alerts: List[Alert] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def set_baseline(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        self.baselines = {str(k): float(v) for k, v in metrics.items()}
        _assert_finite(self.baselines, "validation_baselines")
        return {"baselines": dict(self.baselines), "count": len(self.baselines), "status": "ok"}

    def reset_baselines(self, metrics: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Reset drift baselines to ``metrics`` (or empty). Drift is measured against a
        stable baseline established once at campaign start, not against the immediately
        preceding cycle's values."""
        if metrics is None:
            self.baselines = {}
        else:
            self.baselines = {str(k): float(v) for k, v in metrics.items()}
            _assert_finite(self.baselines, "validation_baselines")
        return {"baselines": dict(self.baselines), "count": len(self.baselines), "status": "ok"}

    def check_invariants(self, state: Dict[str, Any]) -> Tuple[InvariantCheck, ...]:
        state = {str(k): v for k, v in state.items()}
        checks: List[InvariantCheck] = []

        dd = float(state.get("drawdown_pct", 0.0))
        checks.append(
            InvariantCheck(
                name="max_drawdown",
                passed=dd <= self.config.max_drawdown_pct,
                value=dd,
                threshold=self.config.max_drawdown_pct,
                direction="lte",
                detail=f"drawdown {dd:.4f} {'<=' if dd <= self.config.max_drawdown_pct else '>'} {self.config.max_drawdown_pct:.4f}",
            )
        )

        var = float(state.get("var_pct", 0.0))
        checks.append(
            InvariantCheck(
                name="max_var",
                passed=var <= self.config.max_var_pct,
                value=var,
                threshold=self.config.max_var_pct,
                direction="lte",
                detail=f"var {var:.4f} {'<=' if var <= self.config.max_var_pct else '>'} {self.config.max_var_pct:.4f}",
            )
        )

        skew = float(state.get("iv_skew_bps", 0.0))
        checks.append(
            InvariantCheck(
                name="max_iv_skew",
                passed=skew <= self.config.max_iv_skew_bps,
                value=skew,
                threshold=self.config.max_iv_skew_bps,
                direction="lte",
                detail=f"iv_skew {skew:.1f}bps {'<=' if skew <= self.config.max_iv_skew_bps else '>'} {self.config.max_iv_skew_bps:.1f}bps",
            )
        )

        sharpe = float(state.get("sharpe", 1.0))
        checks.append(
            InvariantCheck(
                name="min_sharpe",
                passed=sharpe >= self.config.min_sharpe,
                value=sharpe,
                threshold=self.config.min_sharpe,
                direction="gte",
                detail=f"sharpe {sharpe:.3f} {'>=' if sharpe >= self.config.min_sharpe else '<'} {self.config.min_sharpe:.3f}",
            )
        )

        reject = float(state.get("fill_reject_rate", 0.0))
        checks.append(
            InvariantCheck(
                name="max_fill_reject_rate",
                passed=reject <= self.config.max_fill_reject_rate,
                value=reject,
                threshold=self.config.max_fill_reject_rate,
                direction="lte",
                detail=f"fill_reject {reject:.3f} {'<=' if reject <= self.config.max_fill_reject_rate else '>'} {self.config.max_fill_reject_rate:.3f}",
            )
        )

        latency = float(state.get("latency_p95_ms", 0.0))
        checks.append(
            InvariantCheck(
                name="max_latency_p95",
                passed=latency <= self.config.max_latency_p95_ms,
                value=latency,
                threshold=self.config.max_latency_p95_ms,
                direction="lte",
                detail=f"latency_p95 {latency:.1f}ms {'<=' if latency <= self.config.max_latency_p95_ms else '>'} {self.config.max_latency_p95_ms:.1f}ms",
            )
        )

        for c in checks:
            _assert_finite({"value": c.value, "threshold": c.threshold}, f"invariant_{c.name}")
        return tuple(checks)

    def detect_drift(self, current: Dict[str, float]) -> Tuple[DriftCheck, ...]:
        current = {str(k): float(v) for k, v in current.items()}
        _assert_finite(current, "drift_current")
        checks: List[DriftCheck] = []
        for name, cur in current.items():
            base = self.baselines.get(name, cur)
            base = float(base)
            drift_pct = 0.0 if base == 0.0 else abs(cur - base) / abs(base) * 100.0
            zscore = drift_pct / max(1.0, self.config.drift_zscore_threshold)
            drifted = drift_pct > (self.config.drift_zscore_threshold * 10.0)
            checks.append(
                DriftCheck(
                    metric=name,
                    baseline=base,
                    current=cur,
                    drift_pct=float(drift_pct),
                    zscore=float(zscore),
                    drifted=bool(drifted),
                )
            )
        return tuple(checks)

    def _alert(self, severity: str, message: str, metric: str, value: float, threshold: float) -> Alert:
        al = Alert(
            alert_id=self._next_id("alert"),
            severity=severity,
            message=message,
            metric=metric,
            value=float(value),
            threshold=float(threshold),
            timestamp=_utc_now(),
        )
        _assert_finite({"value": al.value, "threshold": al.threshold}, f"alert_{al.alert_id}")
        self.alerts.append(al)
        return al

    def validate_cycle(
        self,
        cycle: int,
        state: Dict[str, Any],
        current_metrics: Optional[Dict[str, float]] = None,
    ) -> ValidationResult:
        state = {str(k): v for k, v in state.items()}
        invariants = self.check_invariants(state)
        drift = self.detect_drift(current_metrics or {})
        alerts: List[Alert] = []

        for c in invariants:
            if not c.passed:
                sev = "critical" if c.name in ("max_drawdown", "max_var") else "warn"
                alerts.append(
                    self._alert(
                        sev,
                        f"Invariant breach: {c.detail}",
                        c.name,
                        c.value,
                        c.threshold,
                    )
                )
        for d in drift:
            if d.drifted:
                alerts.append(
                    self._alert(
                        "warn",
                        f"Drift detected: {d.metric} drifted {d.drift_pct:.1f}% (z={d.zscore:.2f})",
                        d.metric,
                        d.current,
                        d.baseline,
                    )
                )

        all_ok = all(c.passed for c in invariants) and not any(d.drifted for d in drift)
        res = ValidationResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            all_ok=bool(all_ok),
            invariants=invariants,
            drift=drift,
            alerts=tuple(alerts),
            paper_only=True,
        )
        _assert_finite(
            {"cycle": float(res.cycle), "all_ok": float(1.0 if res.all_ok else 0.0)},
            "validation_result",
        )
        self.results.append(res)
        return res

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE31_CONTINUOUS_VALIDATION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles_validated": int(len(self.results)),
            "last_all_ok": bool(last.all_ok) if last else True,
            "last_cycle": int(last.cycle) if last else 0,
            "invariants": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "value": c.value,
                    "threshold": c.threshold,
                    "direction": c.direction,
                    "detail": c.detail,
                }
                for c in (last.invariants if last else [])
            ],
            "drift": [
                {
                    "metric": d.metric,
                    "baseline": d.baseline,
                    "current": d.current,
                    "drift_pct": d.drift_pct,
                    "zscore": d.zscore,
                    "drifted": d.drifted,
                }
                for d in (last.drift if last else [])
            ],
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "message": a.message,
                    "metric": a.metric,
                    "value": a.value,
                    "threshold": a.threshold,
                    "timestamp": a.timestamp,
                }
                for a in self.alerts[-50:]
            ],
            "baselines": dict(self.baselines),
        }
        _assert_finite(report, "phase31_continuous_validation_report")
        rep_json = Path(outdir) / "PHASE31_CONTINUOUS_VALIDATION_REPORT.json"
        rep_md = Path(outdir) / "PHASE31_CONTINUOUS_VALIDATION_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE31_CONTINUOUS_VALIDATION_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Cycles validated: {report['cycles_validated']}\n"
            f"Last all_ok: {report['last_all_ok']}\n"
            f"Active alerts: {len(report['alerts'])}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
        }


__all__ = [
    "ContinuousValidationEngine",
    "ValidationConfig",
    "InvariantCheck",
    "DriftCheck",
    "Alert",
    "ValidationResult",
]
