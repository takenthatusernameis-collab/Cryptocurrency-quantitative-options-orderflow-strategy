"""Model governance for crypto options + orderflow.

Model versioning, registry, promotion/demotion gates, backtest/OOS validation
gates, audit trail, and deterministic model manifest. Default paper-only aware.
All artifacts strictly serialized with allow_nan=False.
"""

from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.errors import ConfigError, RiskLimitError, SerializationError, get_logger
from src.telemetry import serialize_metrics_strict
from src.telemetry.serialization import assert_json_valid

_logger = get_logger(__name__)


def _utc_iso(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def _deterministic_iso(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    return _utc_iso(base + timedelta(seconds=int(seed)))


class ModelStatus(str, Enum):
    """Model lifecycle status."""

    DRAFT = "draft"
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    PROMOTED = "promoted"
    DEMOTED = "demoted"
    ARCHIVED = "archived"
    REJECTED = "rejected"


def _model_id(name: str, version: str, seed: int) -> str:
    payload = f"{name}|{version}|{seed}"
    return f"model_{hashlib.sha256(payload.encode()).hexdigest()[:12]}"


@dataclass
class ModelVersion:
    """A versioned model entry."""

    name: str
    version: str
    status: str = ModelStatus.DRAFT.value
    seed: int = 42
    created_at: str = ""
    promoted_at: Optional[str] = None
    demoted_at: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    oos_metrics: Dict[str, float] = field(default_factory=dict)
    backtest_metrics: Dict[str, float] = field(default_factory=dict)
    validation_gates: Dict[str, bool] = field(default_factory=dict)
    artifact_path: Optional[str] = None
    checksum: Optional[str] = None
    paper_only: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    audit_note: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = _deterministic_iso(self.seed)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "seed": int(self.seed),
            "created_at": self.created_at,
            "promoted_at": self.promoted_at,
            "demoted_at": self.demoted_at,
            "metrics": {k: float(v) for k, v in self.metrics.items()},
            "oos_metrics": {k: float(v) for k, v in self.oos_metrics.items()},
            "backtest_metrics": {k: float(v) for k, v in self.backtest_metrics.items()},
            "validation_gates": self.validation_gates,
            "artifact_path": self.artifact_path,
            "checksum": self.checksum,
            "paper_only": bool(self.paper_only),
            "tags": dict(self.tags),
            "audit_note": self.audit_note,
        })


@dataclass
class ModelManifest:
    """Deterministic model manifest for audit and reproducibility."""

    model_id: str
    name: str
    version: str
    status: str
    seed: int
    timestamp: str
    paper_only: bool
    validation_passed: bool
    gates: Dict[str, bool]
    metrics: Dict[str, float]
    oos_metrics: Dict[str, float]
    backtest_metrics: Dict[str, float]
    checksum: Optional[str]
    artifact_path: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "seed": int(self.seed),
            "timestamp": self.timestamp,
            "paper_only": bool(self.paper_only),
            "validation_passed": bool(self.validation_passed),
            "gates": self.gates,
            "metrics": {k: float(v) for k, v in self.metrics.items()},
            "oos_metrics": {k: float(v) for k, v in self.oos_metrics.items()},
            "backtest_metrics": {k: float(v) for k, v in self.backtest_metrics.items()},
            "checksum": self.checksum,
            "artifact_path": self.artifact_path,
        })


class ModelRegistry:
    """Thread-safe model registry with versioning and audit trail."""

    def __init__(self, seed: int = 42, outdir: Optional[Path] = None) -> None:
        self.seed = int(seed)
        self.timestamp = _deterministic_iso(self.seed)
        self.outdir = outdir or Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._models: Dict[str, ModelVersion] = {}
        self._by_name: Dict[str, List[str]] = {}
        self._audit: List[Dict[str, Any]] = []
        self._current: Optional[str] = None  # promoted model_id

    def register(self, model: ModelVersion) -> str:
        mid = _model_id(model.name, model.version, self.seed)
        with self._lock:
            self._models[mid] = model
            self._by_name.setdefault(model.name, []).append(mid)
        self._audit.append({
            "action": "register",
            "model_id": mid,
            "name": model.name,
            "version": model.version,
            "timestamp": _deterministic_iso(self.seed),
        })
        return mid

    def get(self, model_id: str) -> Optional[ModelVersion]:
        with self._lock:
            return self._models.get(model_id)

    def list_versions(self, name: str) -> List[str]:
        with self._lock:
            return list(self._by_name.get(name, []))

    def set_status(self, model_id: str, status: str,
                   note: Optional[str] = None) -> bool:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                return False
            old = model.status
            model.status = status
            now = _deterministic_iso(self.seed)
            if status == ModelStatus.PROMOTED.value:
                model.promoted_at = now
                self._current = model_id
            elif status == ModelStatus.DEMOTED.value:
                model.demoted_at = now
                if self._current == model_id:
                    self._current = None
            self._audit.append({
                "action": "set_status",
                "model_id": model_id,
                "name": model.name,
                "from": old,
                "to": status,
                "note": note,
                "timestamp": now,
            })
        return True

    def set_metrics(self, model_id: str, metrics: Optional[Dict[str, float]] = None,
                    oos_metrics: Optional[Dict[str, float]] = None,
                    backtest_metrics: Optional[Dict[str, float]] = None) -> bool:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                return False
            if metrics is not None:
                model.metrics = {k: float(v) for k, v in metrics.items()}
            if oos_metrics is not None:
                model.oos_metrics = {k: float(v) for k, v in oos_metrics.items()}
            if backtest_metrics is not None:
                model.backtest_metrics = {k: float(v) for k, v in backtest_metrics.items()}
            self._audit.append({
                "action": "set_metrics",
                "model_id": model_id,
                "name": model.name,
                "timestamp": _deterministic_iso(self.seed),
            })
        return True

    def set_validation_gates(self, model_id: str, gates: Dict[str, bool]) -> bool:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                return False
            model.validation_gates = dict(gates)
            self._audit.append({
                "action": "set_validation_gates",
                "model_id": model_id,
                "name": model.name,
                "gates": dict(gates),
                "timestamp": _deterministic_iso(self.seed),
            })
        return True

    def set_artifact(self, model_id: str, artifact_path: str,
                     checksum: Optional[str] = None) -> bool:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                return False
            model.artifact_path = artifact_path
            model.checksum = checksum
            self._audit.append({
                "action": "set_artifact",
                "model_id": model_id,
                "name": model.name,
                "artifact_path": artifact_path,
                "checksum": checksum,
                "timestamp": _deterministic_iso(self.seed),
            })
        return True

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            models = {k: m.to_dict() for k, m in self._models.items()}
            audit = list(self._audit)
        payload = serialize_metrics_strict({
            "seed": self.seed,
            "timestamp": _deterministic_iso(self.seed),
            "paper_only": True,
            "num_models": len(models),
            "current_model_id": self._current,
            "models": models,
            "audit": audit,
        })
        assert_json_valid(payload)
        return payload

    def manifest(self, model_id: str) -> Optional[ModelManifest]:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                return None
        return ModelManifest(
            model_id=model_id,
            name=model.name,
            version=model.version,
            status=model.status,
            seed=model.seed,
            timestamp=_deterministic_iso(self.seed),
            paper_only=model.paper_only,
            validation_passed=all(model.validation_gates.values()) if model.validation_gates else False,
            gates=dict(model.validation_gates),
            metrics=dict(model.metrics),
            oos_metrics=dict(model.oos_metrics),
            backtest_metrics=dict(model.backtest_metrics),
            checksum=model.checksum,
            artifact_path=model.artifact_path,
        )


class ModelGovernance:
    """Model governance: promotion/demotion gates, backtest/OOS validation, audit."""

    # Gates required for promotion
    PROMOTION_GATES = (
        "backtest_passed",
        "oos_passed",
        "numerics_finite",
        "determinism_verified",
        "paper_only_enforced",
        "schema_valid",
    )

    def __init__(self, seed: int = 42, registry=None,
                 outdir: Optional[Path] = None, paper_only: bool = True) -> None:
        self.seed = int(seed)
        self.timestamp = _deterministic_iso(self.seed)
        self.paper_only = bool(paper_only)
        self.outdir = outdir or Path("research_state")
        self.outdir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.registry = registry or ModelRegistry(seed=self.seed, outdir=self.outdir)
        self._promotions: List[Dict[str, Any]] = []
        self._demotions: List[Dict[str, Any]] = []
        self._rejections: List[Dict[str, Any]] = []

    def register_model(self, name: str, version: str,
                       metrics: Optional[Dict[str, float]] = None,
                       oos_metrics: Optional[Dict[str, float]] = None,
                       backtest_metrics: Optional[Dict[str, float]] = None,
                       artifact_path: Optional[str] = None,
                       checksum: Optional[str] = None,
                       tags: Optional[Dict[str, str]] = None) -> str:
        model = ModelVersion(
            name=name,
            version=version,
            status=ModelStatus.DRAFT.value,
            seed=self.seed,
            metrics=metrics or {},
            oos_metrics=oos_metrics or {},
            backtest_metrics=backtest_metrics or {},
            artifact_path=artifact_path,
            checksum=checksum,
            paper_only=self.paper_only,
            tags=tags or {},
        )
        mid = self.registry.register(model)
        return mid

    def validate_gates(self, model_id: str,
                       gates: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """Validate promotion gates for a model. Returns gate results."""
        with self._lock:
            model = self.registry.get(model_id)
        if model is None:
            raise ConfigError("Model not found", context={"model_id": model_id})
        required = set(self.PROMOTION_GATES)
        provided = dict(gates or {})
        results: Dict[str, bool] = {}
        all_passed = True
        for gate in required:
            passed = bool(provided.get(gate, False))
            results[gate] = passed
            if not passed:
                all_passed = False
        # numeric finiteness gate
        for label, m in [("metrics", model.metrics),
                         ("oos_metrics", model.oos_metrics),
                         ("backtest_metrics", model.backtest_metrics)]:
            for k, v in m.items():
                if not isfinite(float(v)):
                    results["numerics_finite"] = False
                    all_passed = False
        self.registry.set_validation_gates(model_id, results)
        now = _deterministic_iso(self.seed)
        outcome = {
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "gates": results,
            "all_passed": bool(all_passed),
            "paper_only": bool(model.paper_only),
            "validated_at": now,
        }
        return serialize_metrics_strict(outcome)

    def promote(self, model_id: str, gates: Optional[Dict[str, bool]] = None,
                note: Optional[str] = None) -> Dict[str, Any]:
        """Promote a model only if all gates pass (paper-only enforced)."""
        validation = self.validate_gates(model_id, gates)
        if not validation["all_passed"]:
            self._record_rejection(model_id, "gates_not_passed", validation)
            raise RiskLimitError(
                f"Model {model_id} promotion blocked: gates not all passed",
                context={"model_id": model_id, "validation": validation},
            )
        model = self.registry.get(model_id)
        if model is None:
            raise ConfigError("Model not found", context={"model_id": model_id})
        if not model.paper_only and not self.paper_only:
            raise RiskLimitError("Live-capital promotion is disallowed by default gate",
                                 context={"model_id": model_id, "paper_only": model.paper_only})
        self.registry.set_status(model_id, ModelStatus.PROMOTED.value, note=note)
        now = _deterministic_iso(self.seed)
        self._promotions.append({
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "note": note,
            "timestamp": now,
        })
        return serialize_metrics_strict({
            "action": "promote",
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "status": ModelStatus.PROMOTED.value,
            "paper_only": bool(model.paper_only),
            "gates": validation["gates"],
            "timestamp": now,
        })

    def demote(self, model_id: str, reason: str,
               note: Optional[str] = None) -> Dict[str, Any]:
        """Demote a model."""
        model = self.registry.get(model_id)
        if model is None:
            raise ConfigError("Model not found", context={"model_id": model_id})
        self.registry.set_status(model_id, ModelStatus.DEMOTED.value, note=note)
        now = _deterministic_iso(self.seed)
        self._demotions.append({
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "reason": reason,
            "note": note,
            "timestamp": now,
        })
        return serialize_metrics_strict({
            "action": "demote",
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "status": ModelStatus.DEMOTED.value,
            "reason": reason,
            "timestamp": now,
        })

    def reject(self, model_id: str, reason: str,
               note: Optional[str] = None) -> Dict[str, Any]:
        """Reject a model."""
        model = self.registry.get(model_id)
        if model is None:
            raise ConfigError("Model not found", context={"model_id": model_id})
        self.registry.set_status(model_id, ModelStatus.REJECTED.value, note=note)
        now = _deterministic_iso(self.seed)
        self._rejections.append({
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "reason": reason,
            "note": note,
            "timestamp": now,
        })
        return serialize_metrics_strict({
            "action": "reject",
            "model_id": model_id,
            "name": model.name,
            "version": model.version,
            "status": ModelStatus.REJECTED.value,
            "reason": reason,
            "timestamp": now,
        })

    def _record_rejection(self, model_id: str, reason: str,
                          validation: Dict[str, Any]) -> None:
        model = self.registry.get(model_id)
        now = _deterministic_iso(self.seed)
        self._rejections.append({
            "model_id": model_id,
            "name": model.name if model else None,
            "version": model.version if model else None,
            "reason": reason,
            "validation": validation,
            "timestamp": now,
        })

    def manifest(self, model_id: str) -> Optional[Dict[str, Any]]:
        m = self.registry.manifest(model_id)
        if m is None:
            return None
        return m.to_dict()

    def snapshot(self) -> Dict[str, Any]:
        reg = self.registry.snapshot()
        with self._lock:
            promotions = list(self._promotions)
            demotions = list(self._demotions)
            rejections = list(self._rejections)
        payload = serialize_metrics_strict({
            "seed": self.seed,
            "timestamp": _deterministic_iso(self.seed),
            "paper_only": self.paper_only,
            "registry": reg,
            "num_promotions": len(promotions),
            "num_demotions": len(demotions),
            "num_rejections": len(rejections),
            "promotions": promotions,
            "demotions": demotions,
            "rejections": rejections,
        })
        assert_json_valid(payload)
        return payload

    def export_report(self) -> Dict[str, Any]:
        snap = self.snapshot()
        report = serialize_metrics_strict({
            "report": "model_governance",
            "seed": self.seed,
            "timestamp": _deterministic_iso(self.seed),
            "paper_only": self.paper_only,
            "num_models": snap["registry"]["num_models"],
            "current_model_id": snap["registry"]["current_model_id"],
            "num_promotions": snap["num_promotions"],
            "num_demotions": snap["num_demotions"],
            "num_rejections": snap["num_rejections"],
            "promotion_gates": list(self.PROMOTION_GATES),
            "registry": snap["registry"],
            "promotions": snap["promotions"],
            "demotions": snap["demotions"],
            "rejections": snap["rejections"],
        })
        assert_json_valid(report)
        return report


# Default governance (paper-only).
default_model_registry = ModelRegistry(seed=42)
default_model_governance = ModelGovernance(seed=42, paper_only=True)


__all__ = [
    "ModelStatus", "ModelVersion", "ModelManifest", "ModelRegistry",
    "ModelGovernance", "default_model_registry", "default_model_governance",
    "_model_id", "_deterministic_iso",
]
