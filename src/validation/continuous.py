"""Continuous validation for crypto options + orderflow production.

Shadow mode vs live/paper comparison, data quality checks (NaN/Inf/stale/corruption),
feature validation, model sanity, drift detection, canary gates, automated
regression checks against golden artifacts. Deterministic: fixed seeds,
allow_nan=False serialization on all artifacts, mock-based test harnesses.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

from ..errors import SerializationError, get_logger
from ..utils.numerical_guards import validate_finite
from ..telemetry import serialize_metrics_strict
from ..telemetry.observability import observability_logger, redact


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return time.time()


def _make_id(prefix: str, *parts: str) -> str:
    payload = f"{prefix}|{'|'.join(parts)}|{time.time_ns()}|{threading.get_ident()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


@dataclass
class DataQualityIssue:
    """A detected data quality issue."""

    issue_id: str
    check: str
    severity: str  # info/warning/error/critical
    symbol: Optional[str]
    message: str
    detected_at: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "issue_id": self.issue_id,
            "check": self.check,
            "severity": self.severity,
            "symbol": self.symbol,
            "message": self.message,
            "detected_at": self.detected_at,
            "details": redact(self.details),
        })


@dataclass
class DataQualityReport:
    """Result of a data quality validation run."""

    run_id: str
    symbol: str
    venue: str
    total_points: int
    nan_count: int
    inf_count: int
    stale_count: int
    corruption_count: int
    issues: List[DataQualityIssue] = field(default_factory=list)
    passed: bool = False
    validated_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "run_id": self.run_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "total_points": int(self.total_points),
            "nan_count": int(self.nan_count),
            "inf_count": int(self.inf_count),
            "stale_count": int(self.stale_count),
            "corruption_count": int(self.corruption_count),
            "issues": [i.to_dict() for i in self.issues],
            "passed": bool(self.passed),
            "validated_at": self.validated_at,
        })


class DataQualityValidator:
    """Validates market data quality: NaN/Inf/stale/corruption detection."""

    def __init__(self, max_stale_sec: float = 300.0):
        self.max_stale_sec = float(max_stale_sec) if isfinite(float(max_stale_sec)) else 300.0

    def validate_quote(self, symbol: str, venue: str, bid: float, ask: float,
                       timestamp: float, last_seen_ts: Optional[float] = None,
                       run_id: Optional[str] = None) -> DataQualityReport:
        run_id = run_id or _make_id("dq", symbol, venue, str(timestamp))
        issues: List[DataQualityIssue] = []
        nan_count = 0
        inf_count = 0
        stale_count = 0
        corruption_count = 0
        total_points = 2  # bid + ask

        def _add_issue(sev: str, check: str, msg: str, details: Optional[Dict[str, Any]] = None):
            nonlocal issues
            issues.append(DataQualityIssue(
                issue_id=_make_id("dq_issue", symbol, check, str(_now_ts())),
                check=check,
                severity=sev,
                symbol=symbol,
                message=msg,
                detected_at=_now_iso(),
                details=details or {},
            ))

        # NaN check
        if not isfinite(bid):
            nan_count += 1
            _add_issue("error", "nan_bid", f"bid is non-finite for {symbol}",
                       {"bid": str(bid)})
        if not isfinite(ask):
            nan_count += 1
            _add_issue("error", "nan_ask", f"ask is non-finite for {symbol}",
                       {"ask": str(ask)})

        # Inf check
        if math.isinf(bid):
            inf_count += 1
            _add_issue("error", "inf_bid", f"bid is infinite for {symbol}", {})
        if math.isinf(ask):
            inf_count += 1
            _add_issue("error", "inf_ask", f"ask is infinite for {symbol}", {})

        # Stale check
        now_ts = _now_ts()
        check_ts = last_seen_ts if last_seen_ts is not None else timestamp
        age = now_ts - check_ts
        if age > self.max_stale_sec:
            stale_count += 1
            _add_issue("warning", "stale_quote",
                       f"quote for {symbol} is {age:.1f}s stale (max {self.max_stale_sec}s)",
                       {"age_sec": age, "max_stale_sec": self.max_stale_sec})

        # Corruption check: bid > ask (inverted spread)
        if isfinite(bid) and isfinite(ask) and bid > ask:
            corruption_count += 1
            _add_issue("critical", "inverted_spread",
                       f"bid ({bid}) > ask ({ask}) for {symbol}",
                       {"bid": bid, "ask": ask})

        # Negative price
        if isfinite(bid) and bid < 0:
            corruption_count += 1
            _add_issue("critical", "negative_bid", f"negative bid for {symbol}", {"bid": bid})
        if isfinite(ask) and ask < 0:
            corruption_count += 1
            _add_issue("critical", "negative_ask", f"negative ask for {symbol}", {"ask": ask})

        passed = (nan_count == 0 and inf_count == 0 and stale_count == 0
                  and corruption_count == 0 and len(issues) == 0)
        report = DataQualityReport(
            run_id=run_id, symbol=symbol, venue=venue,
            total_points=total_points, nan_count=nan_count, inf_count=inf_count,
            stale_count=stale_count, corruption_count=corruption_count,
            issues=issues, passed=passed, validated_at=_now_iso(),
        )
        observability_logger.info("data_quality_validated", symbol=symbol, venue=venue,
                                  passed=passed, nan_count=nan_count,
                                  inf_count=inf_count, stale_count=stale_count,
                                  corruption_count=corruption_count)
        return report


@dataclass
class DriftResult:
    """Result of a drift detection check."""

    check_id: str
    metric: str
    reference_value: float
    current_value: float
    drift_pct: float
    drift_threshold: float
    drift_detected: bool
    severity: str
    detected_at: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "check_id": self.check_id,
            "metric": self.metric,
            "reference_value": float(self.reference_value) if isfinite(float(self.reference_value)) else 0.0,
            "current_value": float(self.current_value) if isfinite(float(self.current_value)) else 0.0,
            "drift_pct": float(self.drift_pct) if isfinite(float(self.drift_pct)) else 0.0,
            "drift_threshold": float(self.drift_threshold) if isfinite(float(self.drift_threshold)) else 0.0,
            "drift_detected": bool(self.drift_detected),
            "severity": self.severity,
            "detected_at": self.detected_at,
            "details": redact(self.details),
        })


class DriftDetector:
    """Detects drift in features, models, and distributions."""

    def __init__(self, default_threshold_pct: float = 5.0):
        self.default_threshold_pct = float(default_threshold_pct)

    def detect_drift(self, metric: str, reference_value: float,
                     current_value: float,
                     threshold_pct: Optional[float] = None,
                     labels: Optional[Dict[str, str]] = None) -> DriftResult:
        thr = float(threshold_pct) if (threshold_pct is not None and isfinite(float(threshold_pct))) else self.default_threshold_pct
        ref = float(reference_value) if isfinite(float(reference_value)) else 0.0
        cur = float(current_value) if isfinite(float(current_value)) else 0.0
        if abs(ref) > 1e-12:
            drift_pct = abs((cur - ref) / ref) * 100.0
        else:
            drift_pct = abs(cur - ref) * 100.0
        drift_pct = float(drift_pct) if isfinite(float(drift_pct)) else 0.0
        drift_detected = drift_pct > thr
        severity = "info"
        if drift_detected:
            if drift_pct > thr * 3:
                severity = "critical"
            elif drift_pct > thr * 2:
                severity = "error"
            elif drift_pct > thr * 1.5:
                severity = "warning"
        result = DriftResult(
            check_id=_make_id("drift", metric, str(_now_ts())),
            metric=metric,
            reference_value=ref,
            current_value=cur,
            drift_pct=drift_pct,
            drift_threshold=thr,
            drift_detected=drift_detected,
            severity=severity,
            detected_at=_now_iso(),
            details=dict(labels or {}),
        )
        if drift_detected:
            observability_logger.warning("drift_detected", metric=metric,
                                         drift_pct=drift_pct, threshold=thr,
                                         severity=severity)
        return result


@dataclass
class ShadowComparison:
    """Shadow mode vs live/paper comparison result."""

    comparison_id: str
    symbol: str
    venue: str
    shadow_signal: float
    live_signal: float
    agreement: bool
    delta: float
    threshold: float
    compared_at: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "comparison_id": self.comparison_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "shadow_signal": float(self.shadow_signal) if isfinite(float(self.shadow_signal)) else 0.0,
            "live_signal": float(self.live_signal) if isfinite(float(self.live_signal)) else 0.0,
            "agreement": bool(self.agreement),
            "delta": float(self.delta) if isfinite(float(self.delta)) else 0.0,
            "threshold": float(self.threshold) if isfinite(float(self.threshold)) else 0.0,
            "compared_at": self.compared_at,
            "details": redact(self.details),
        })


class ShadowValidator:
    """Shadow mode validation: compare shadow strategy signals vs live/paper."""

    def __init__(self, agreement_threshold: float = 0.05):
        self.agreement_threshold = float(agreement_threshold)

    def compare(self, symbol: str, venue: str, shadow_signal: float,
                live_signal: float,
                labels: Optional[Dict[str, str]] = None) -> ShadowComparison:
        ss = float(shadow_signal) if isfinite(float(shadow_signal)) else 0.0
        ls = float(live_signal) if isfinite(float(live_signal)) else 0.0
        delta = abs(ss - ls)
        agreement = delta <= self.agreement_threshold
        comparison = ShadowComparison(
            comparison_id=_make_id("shadow", symbol, venue, str(_now_ts())),
            symbol=symbol, venue=venue,
            shadow_signal=ss, live_signal=ls,
            agreement=bool(agreement), delta=delta,
            threshold=self.agreement_threshold,
            compared_at=_now_iso(),
            details=dict(labels or {}),
        )
        if not agreement:
            observability_logger.warning("shadow_disagreement", symbol=symbol,
                                         shadow_signal=ss, live_signal=ls,
                                         delta=delta, threshold=self.agreement_threshold)
        return comparison


@dataclass
class CanaryGateResult:
    """Canary gate evaluation result."""

    gate_id: str
    canary_version: str
    baseline_version: str
    metric: str
    canary_value: float
    baseline_value: float
    improvement_pct: float
    gate_passed: bool
    threshold_pct: float
    evaluated_at: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "gate_id": self.gate_id,
            "canary_version": self.canary_version,
            "baseline_version": self.baseline_version,
            "metric": self.metric,
            "canary_value": float(self.canary_value) if isfinite(float(self.canary_value)) else 0.0,
            "baseline_value": float(self.baseline_value) if isfinite(float(self.baseline_value)) else 0.0,
            "improvement_pct": float(self.improvement_pct) if isfinite(float(self.improvement_pct)) else 0.0,
            "gate_passed": bool(self.gate_passed),
            "threshold_pct": float(self.threshold_pct) if isfinite(float(self.threshold_pct)) else 0.0,
            "evaluated_at": self.evaluated_at,
            "details": redact(self.details),
        })


class CanaryGate:
    """Canary deployment gate: promote only if canary beats baseline by threshold."""

    def __init__(self, min_improvement_pct: float = 1.0):
        self.min_improvement_pct = float(min_improvement_pct)

    def evaluate(self, canary_version: str, baseline_version: str,
                 metric: str, canary_value: float, baseline_value: float,
                 labels: Optional[Dict[str, str]] = None) -> CanaryGateResult:
        cv = float(canary_value) if isfinite(float(canary_value)) else 0.0
        bv = float(baseline_value) if isfinite(float(baseline_value)) else 0.0
        if abs(bv) > 1e-12:
            improvement_pct = ((cv - bv) / abs(bv)) * 100.0
        else:
            improvement_pct = 0.0 if cv == bv else 100.0
        improvement_pct = float(improvement_pct) if isfinite(float(improvement_pct)) else 0.0
        gate_passed = improvement_pct >= self.min_improvement_pct
        result = CanaryGateResult(
            gate_id=_make_id("canary", canary_version, baseline_version, metric, str(_now_ts())),
            canary_version=canary_version,
            baseline_version=baseline_version,
            metric=metric,
            canary_value=cv,
            baseline_value=bv,
            improvement_pct=improvement_pct,
            gate_passed=bool(gate_passed),
            threshold_pct=self.min_improvement_pct,
            evaluated_at=_now_iso(),
            details=dict(labels or {}),
        )
        observability_logger.info("canary_gate_evaluated", canary=canary_version,
                                  baseline=baseline_version, metric=metric,
                                  improvement_pct=improvement_pct,
                                  gate_passed=gate_passed)
        return result


@dataclass
class GoldenArtifact:
    """A golden artifact for regression comparison."""

    artifact_id: str
    name: str
    content_hash: str
    content: Dict[str, Any]
    created_at: str
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "artifact_id": self.artifact_id,
            "name": self.name,
            "content_hash": self.content_hash,
            "content": redact(self.content),
            "created_at": self.created_at,
            "labels": dict(self.labels),
        })


@dataclass
class RegressionCheckResult:
    """Result of a regression check against a golden artifact."""

    check_id: str
    artifact_id: str
    artifact_name: str
    current_hash: str
    matches: bool
    diff: Dict[str, Any]
    checked_at: str

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "check_id": self.check_id,
            "artifact_id": self.artifact_id,
            "artifact_name": self.artifact_name,
            "current_hash": self.current_hash,
            "matches": bool(self.matches),
            "diff": redact(self.diff),
            "checked_at": self.checked_at,
        })


class GoldenArtifactStore:
    """Store and compare against golden artifacts for regression detection."""

    def __init__(self):
        self._lock = threading.RLock()
        self._artifacts: Dict[str, GoldenArtifact] = {}

    def store(self, name: str, content: Dict[str, Any],
              labels: Optional[Dict[str, str]] = None) -> GoldenArtifact:
        content_serialized = serialize_metrics_strict(content)
        content_hash = hashlib.sha256(
            json.dumps(content_serialized, sort_keys=True, allow_nan=False).encode("utf-8")
        ).hexdigest()[:16]
        artifact = GoldenArtifact(
            artifact_id=_make_id("golden", name, str(_now_ts())),
            name=name,
            content_hash=content_hash,
            content=content_serialized,
            created_at=_now_iso(),
            labels=dict(labels or {}),
        )
        with self._lock:
            self._artifacts[artifact.artifact_id] = artifact
        observability_logger.info("golden_artifact_stored", name=name,
                                  artifact_id=artifact.artifact_id,
                                  content_hash=content_hash)
        return artifact

    def get(self, artifact_id: str) -> Optional[GoldenArtifact]:
        with self._lock:
            return self._artifacts.get(artifact_id)

    def get_by_name(self, name: str) -> Optional[GoldenArtifact]:
        with self._lock:
            for a in self._artifacts.values():
                if a.name == name:
                    return a
        return None

    def list_names(self) -> List[str]:
        with self._lock:
            return sorted({a.name for a in self._artifacts.values()})

    def check_regression(self, artifact_name: str,
                         current_content: Dict[str, Any]) -> RegressionCheckResult:
        artifact = self.get_by_name(artifact_name)
        current_serialized = serialize_metrics_strict(current_content)
        current_hash = hashlib.sha256(
            json.dumps(current_serialized, sort_keys=True, allow_nan=False).encode("utf-8")
        ).hexdigest()[:16]
        if artifact is None:
            return RegressionCheckResult(
                check_id=_make_id("regression", artifact_name, str(_now_ts())),
                artifact_id="",
                artifact_name=artifact_name,
                current_hash=current_hash,
                matches=False,
                diff={"error": "artifact_not_found"},
                checked_at=_now_iso(),
            )
        matches = current_hash == artifact.content_hash
        diff = {}
        if not matches:
            diff = {
                "expected_hash": artifact.content_hash,
                "current_hash": current_hash,
                "expected_keys": sorted(artifact.content.keys()),
                "current_keys": sorted(current_serialized.keys()),
            }
        result = RegressionCheckResult(
            check_id=_make_id("regression", artifact_name, str(_now_ts())),
            artifact_id=artifact.artifact_id,
            artifact_name=artifact_name,
            current_hash=current_hash,
            matches=bool(matches),
            diff=diff,
            checked_at=_now_iso(),
        )
        if not matches:
            observability_logger.warning("regression_detected", artifact=artifact_name,
                                         expected_hash=artifact.content_hash,
                                         current_hash=current_hash)
        return result


class ContinuousValidator:
    """Orchestrates continuous validation: data quality, drift, shadow, canary, regression."""

    def __init__(self, seed: int = 42):
        self.seed = int(seed)
        self.data_quality = DataQualityValidator()
        self.drift_detector = DriftDetector()
        self.shadow_validator = ShadowValidator()
        self.canary_gate = CanaryGate()
        self.golden_store = GoldenArtifactStore()
        self._lock = threading.RLock()
        self._dq_reports: List[DataQualityReport] = []
        self._drift_results: List[DriftResult] = []
        self._shadow_comparisons: List[ShadowComparison] = []
        self._canary_results: List[CanaryGateResult] = []
        self._regression_results: List[RegressionCheckResult] = []

    # ---- data quality
    def validate_data_quality(self, symbol: str, venue: str, bid: float,
                              ask: float, timestamp: float,
                              last_seen_ts: Optional[float] = None) -> Dict[str, Any]:
        report = self.data_quality.validate_quote(symbol, venue, bid, ask,
                                                  timestamp, last_seen_ts)
        with self._lock:
            self._dq_reports.append(report)
        return report.to_dict()

    # ---- drift
    def check_drift(self, metric: str, reference_value: float,
                    current_value: float,
                    threshold_pct: Optional[float] = None,
                    labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        result = self.drift_detector.detect_drift(metric, reference_value,
                                                  current_value, threshold_pct, labels)
        with self._lock:
            self._drift_results.append(result)
        return result.to_dict()

    # ---- shadow
    def compare_shadow(self, symbol: str, venue: str, shadow_signal: float,
                       live_signal: float,
                       labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        comparison = self.shadow_validator.compare(symbol, venue, shadow_signal,
                                                   live_signal, labels)
        with self._lock:
            self._shadow_comparisons.append(comparison)
        return comparison.to_dict()

    # ---- canary
    def evaluate_canary(self, canary_version: str, baseline_version: str,
                        metric: str, canary_value: float, baseline_value: float,
                        labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        result = self.canary_gate.evaluate(canary_version, baseline_version,
                                           metric, canary_value, baseline_value, labels)
        with self._lock:
            self._canary_results.append(result)
        return result.to_dict()

    # ---- regression / golden
    def store_golden(self, name: str, content: Dict[str, Any],
                     labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        artifact = self.golden_store.store(name, content, labels)
        return artifact.to_dict()

    def check_regression(self, artifact_name: str,
                         current_content: Dict[str, Any]) -> Dict[str, Any]:
        result = self.golden_store.check_regression(artifact_name, current_content)
        with self._lock:
            self._regression_results.append(result)
        return result.to_dict()

    # ---- snapshot
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            dq = [r.to_dict() for r in self._dq_reports]
            drift = [r.to_dict() for r in self._drift_results]
            shadow = [c.to_dict() for c in self._shadow_comparisons]
            canary = [c.to_dict() for c in self._canary_results]
            regression = [c.to_dict() for c in self._regression_results]
            golden_names = self.golden_store.list_names()
        return serialize_metrics_strict({
            "seed": int(self.seed),
            "num_dq_reports": len(dq),
            "num_drift_results": len(drift),
            "num_shadow_comparisons": len(shadow),
            "num_canary_results": len(canary),
            "num_regression_results": len(regression),
            "num_golden_artifacts": len(golden_names),
            "dq_reports": dq,
            "drift_results": drift,
            "shadow_comparisons": shadow,
            "canary_results": canary,
            "regression_results": regression,
            "golden_artifact_names": golden_names,
            "timestamp": _now_iso(),
        })

    def clear(self) -> None:
        with self._lock:
            self._dq_reports.clear()
            self._drift_results.clear()
            self._shadow_comparisons.clear()
            self._canary_results.clear()
            self._regression_results.clear()
            self.golden_store._artifacts.clear()


default_continuous_validator = ContinuousValidator(seed=42)


__all__ = [
    "DataQualityIssue", "DataQualityReport", "DataQualityValidator",
    "DriftResult", "DriftDetector",
    "ShadowComparison", "ShadowValidator",
    "CanaryGateResult", "CanaryGate",
    "GoldenArtifact", "RegressionCheckResult", "GoldenArtifactStore",
    "ContinuousValidator", "default_continuous_validator",
]
