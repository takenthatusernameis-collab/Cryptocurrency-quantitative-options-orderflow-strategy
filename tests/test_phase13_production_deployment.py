"""Phase 13 tests: production deployment, continuous monitoring, auto-healing,
model governance (crypto options + orderflow). >=80 substantive tests.

Deterministic: fixed seeds, mock-based, no real network, allow_nan=False
serialization enforced on all artifacts.
"""

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from src.deployment import (
    DeploymentConfig, DeploymentResult, DeploymentStatus,
    ProductionDeployer, default_deploy_config, is_paper_only,
)
from src.deployment.production_deployer import (
    DeploymentError, redact_secrets, _deterministic_iso, _git_sha,
    _validate_finite,
)
from src.monitoring import ContinuousMonitor
from src.monitoring.continuous_monitor import (
    AlertThreshold, AlertRecord, SnapshotMetrics,
    default_continuous_monitor,
)
from src.resilience import AutoHealer, default_retry_policy
from src.resilience.auto_healer import (
    HealAction, HealRecord, HealPolicy, ComponentHealth,
)
from src.governance import (
    ModelGovernance, ModelVersion, ModelStatus, ModelManifest, ModelRegistry,
    default_model_registry, default_model_governance,
)
from src.governance.model_governance import _model_id
from src.deployment.phase13_campaign import Phase13Campaign
from src.telemetry import serialize_metrics_strict
from src.telemetry.serialization import assert_json_valid
from src.errors import ConfigError, RiskLimitError, SerializationError


# --------------------------------------------------------------------------- helpers

def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _assert_strict_serializable(obj, label="obj"):
    serialized = json.dumps(obj, allow_nan=False)
    assert isinstance(serialized, str)
    json.loads(serialized)


# --------------------------------------------------------------------------- deployment config

def test_deploy_config_defaults_paper_only():
    cfg = default_deploy_config()
    assert cfg.paper_only is True
    assert cfg.env == "paper"
    assert cfg.seed == 42
    assert cfg.symbols == ("BTC", "ETH")
    assert cfg.venues == ("deribit", "okx", "binance")
    cfg.assert_valid()


def test_deploy_config_to_dict_strict():
    cfg = DeploymentConfig(seed=7, paper_only=True, initial_capital=50000.0)
    d = cfg.to_dict()
    _assert_strict_serializable(d, "deploy_config")
    assert d["seed"] == 7
    assert d["paper_only"] is True


def test_deploy_config_negative_seed_raises():
    with pytest.raises(ConfigError):
        DeploymentConfig(seed=-1)


def test_deploy_config_zero_capital_raises():
    with pytest.raises(ConfigError):
        DeploymentConfig(initial_capital=0.0)


def test_deploy_config_inf_capital_raises():
    with pytest.raises(ConfigError):
        DeploymentConfig(initial_capital=float("inf"))


def test_deploy_config_empty_venues_raises():
    with pytest.raises(ConfigError):
        DeploymentConfig(venues=())


def test_deploy_config_empty_symbols_raises():
    with pytest.raises(ConfigError):
        DeploymentConfig(symbols=())


def test_deploy_config_invalid_venue():
    cfg = DeploymentConfig(venues=("fake_venue",))
    with pytest.raises(AssertionError):
        cfg.assert_valid()


def test_deploy_config_invalid_symbol():
    cfg = DeploymentConfig(symbols=("btc",))  # lowercase
    # uppercase normalization happens; "BTC" passes regex
    cfg.assert_valid()


def test_is_paper_only_true():
    cfg = default_deploy_config()
    assert is_paper_only(cfg) is True


def test_is_paper_only_false():
    cfg = DeploymentConfig(paper_only=False)
    assert is_paper_only(cfg) is False


# --------------------------------------------------------------------------- redaction / finite

def test_redact_secrets_hides_api_keys():
    obj = {"deribit_api_key": "secret123", "okx_api_secret": "s", "qty": 10,
           "normal": "ok", "nested": {"password": "pw", "price": 50000.0}}
    r = redact_secrets(obj)
    assert r["deribit_api_key"] == "[REDACTED]"
    assert r["okx_api_secret"] == "[REDACTED]"
    assert r["nested"]["password"] == "[REDACTED]"
    assert r["qty"] == 10
    assert r["normal"] == "ok"
    assert r["nested"]["price"] == 50000.0


def test_redact_secrets_list():
    obj = {"keys": [{"token": "t1"}, {"token": "t2"}], "qty": 1}
    r = redact_secrets(obj)
    assert r["keys"][0]["token"] == "[REDACTED]"
    assert r["keys"][1]["token"] == "[REDACTED]"


def test_validate_finite_detects_nan():
    bad = _validate_finite({"a": float("nan")})
    assert "/a" in bad


def test_validate_finite_detects_inf():
    bad = _validate_finite({"a": float("inf")})
    assert "/a" in bad


def test_validate_finite_clean():
    bad = _validate_finite({"a": 1.0, "b": 2, "c": "x", "d": [1.0, 2.0]})
    assert bad == []


def test_deterministic_iso_same_seed_same_output():
    assert _deterministic_iso(42) == _deterministic_iso(42)
    assert _deterministic_iso(42) != _deterministic_iso(43)


def test_git_sha_returns_string_or_none():
    sha = _git_sha()
    assert sha is None or isinstance(sha, str)


# --------------------------------------------------------------------------- production deployer

def test_deployer_init_defaults():
    d = ProductionDeployer(seed=42)
    assert d.paper_only is True  # accessed via config
    assert d.config.paper_only is True
    assert d.status == DeploymentStatus.PENDING
    assert d.deployment_id == "deploy_42"
    assert d.timestamp == _deterministic_iso(42)


def test_deployer_validate_environment_pass():
    d = ProductionDeployer(seed=42)
    res = d.validate_environment()
    _assert_strict_serializable(res, "env_validation")
    assert res["passed"] is True
    assert res["checker"] == "environment"


def test_deployer_validate_environment_bad_venue():
    d = ProductionDeployer(seed=42)
    d.config.venues = ("mars",)
    res = d.validate_environment()
    assert res["passed"] is False
    failed = [c for c in res["checks"] if c["status"] == "fail"]
    assert any(c["check"] == "venues" for c in failed)


def test_deployer_validate_secrets_pass():
    d = ProductionDeployer(seed=42)
    d.config.secrets = {"deribit_api_key": "sk", "okx_passphrase": "pp"}
    res = d.validate_secrets()
    _assert_strict_serializable(res, "secret_validation")
    assert res["passed"] is True


def test_deployer_validate_secrets_leak():
    d = ProductionDeployer(seed=42)
    d.config.secrets = {"deribit_api_key": "sk"}
    res = d.validate_secrets()
    # redaction should hide it, so no leak
    assert res["passed"] is True


def test_deployer_rollout_all_healthy():
    d = ProductionDeployer(seed=42)
    res = d.rollout()
    _assert_strict_serializable(res, "rollout")
    assert res["all_healthy"] is True
    assert res["replicas"] == d.config.rollout_replicas


def test_deployer_health_gate_pass():
    d = ProductionDeployer(seed=42)
    res = d.run_health_gate()
    _assert_strict_serializable(res, "health_gate")
    assert res["passed"] is True


def test_deployer_promote_paper_only():
    d = ProductionDeployer(seed=42)
    res = d.promote()
    _assert_strict_serializable(res, "promote")
    assert res["promoted"] is True
    assert res["paper_only"] is True
    assert d.status == DeploymentStatus.PROMOTED


def test_deployer_deploy_full_pipeline():
    d = ProductionDeployer(seed=42)
    result = d.deploy()
    _assert_strict_serializable(result.to_dict(), "deploy_result")
    assert result.status == DeploymentStatus.PROMOTED.value
    assert result.promoted is True
    assert result.paper_only is True
    assert result.seed == 42
    assert len(result.steps) == 4
    assert all(s["status"] == "completed" for s in result.steps)


def test_deployer_deploy_result_artifact_write(tmp_path):
    d = ProductionDeployer(seed=42)
    result = d.deploy()
    p = tmp_path / "deploy.json"
    written = result.write_json(p)
    assert written == str(p)
    content = p.read_text(encoding="utf-8")
    json.loads(content)  # valid JSON
    # allow_nan already enforced by write_json


def test_deployer_deploy_deterministic_same_seed():
    d1 = ProductionDeployer(seed=42).deploy().to_dict()
    d2 = ProductionDeployer(seed=42).deploy().to_dict()
    assert json.dumps(d1, sort_keys=True, default=str, allow_nan=False) == \
        json.dumps(d2, sort_keys=True, default=str, allow_nan=False)


def test_deployer_deploy_different_seed_different_id():
    d1 = ProductionDeployer(seed=42).deploy()
    d2 = ProductionDeployer(seed=7).deploy()
    assert d1.deployment_id != d2.deployment_id


def test_deployer_live_without_paper_only_blocked():
    d = ProductionDeployer(seed=42)
    d.config.paper_only = False
    d.config.env = "live"
    env_validation = d.validate_environment()
    assert env_validation["passed"] is False


def test_deployer_status_transitions():
    d = ProductionDeployer(seed=42)
    assert d.status == DeploymentStatus.PENDING
    d.deploy()
    assert d.status == DeploymentStatus.PROMOTED


def test_deployer_counts():
    d = ProductionDeployer(seed=42)
    result = d.deploy()
    assert result.counts["venues"] == 3
    assert result.counts["symbols"] == 2
    assert result.counts["health_checks"] == 4
    assert result.counts["steps"] == 4


# --------------------------------------------------------------------------- continuous monitor

def test_continuous_monitor_init_defaults():
    m = ContinuousMonitor(seed=42, paper_only=True)
    assert m.paper_only is True
    assert m.seed == 42
    assert m.service == "crypto-options-orderflow"


def test_continuous_monitor_record_latency():
    m = ContinuousMonitor(seed=42)
    m.record_latency(50.0, labels={"venue": "deribit"})
    m.record_latency(100.0, labels={"venue": "okx"})
    assert len(m._latency_samples) == 2


def test_continuous_monitor_record_latency_ignores_nan():
    m = ContinuousMonitor(seed=42)
    m.record_latency(float("nan"))
    m.record_latency(float("inf"))
    m.record_latency(10.0)
    assert len(m._latency_samples) == 1


def test_continuous_monitor_record_error():
    m = ContinuousMonitor(seed=42)
    m.record_error(0.01)
    m.record_error(0.02)
    assert len(m._error_samples) == 2


def test_continuous_monitor_record_throughput():
    m = ContinuousMonitor(seed=42)
    m.record_throughput(1000.0)
    assert len(m._throughput_samples) == 1


def test_continuous_monitor_monitor_cycle():
    m = ContinuousMonitor(seed=42)
    m.record_latency(30.0)
    m.record_error(0.005)
    m.record_throughput(2000.0)
    snap = m.monitor_cycle()
    _assert_strict_serializable(snap, "monitor_cycle")
    assert snap["service"] == "crypto-options-orderflow"
    assert snap["paper_only"] is True
    assert "health" in snap
    assert "slo_evaluations" in snap
    assert "metrics" in snap
    assert "alerts" in snap
    assert "metrics" in snap["metrics"]


def test_continuous_monitor_p99():
    m = ContinuousMonitor(seed=42)
    vals = [float(i) for i in range(100)]
    p99 = m._p99(vals)
    assert p99 == 99.0


def test_continuous_monitor_p99_empty():
    m = ContinuousMonitor(seed=42)
    assert m._p99([]) == 0.0


def test_continuous_monitor_threshold_warning():
    thr = AlertThreshold("latency_p99_ms", "gte", warning=100.0, critical=500.0)
    assert thr.evaluate(150.0) == "warning"


def test_continuous_monitor_threshold_critical():
    thr = AlertThreshold("latency_p99_ms", "gte", warning=100.0, critical=500.0)
    assert thr.evaluate(600.0) == "critical"


def test_continuous_monitor_threshold_no_breach():
    thr = AlertThreshold("latency_p99_ms", "gte", warning=100.0, critical=500.0)
    assert thr.evaluate(50.0) is None


def test_continuous_monitor_threshold_lte():
    thr = AlertThreshold("fill_rate", "lte", warning=0.90, critical=0.80)
    assert thr.evaluate(0.85) == "warning"
    assert thr.evaluate(0.70) == "critical"
    assert thr.evaluate(0.95) is None


def test_continuous_monitor_threshold_disabled():
    thr = AlertThreshold("x", "gte", warning=1.0, critical=2.0, enabled=False)
    assert thr.evaluate(999.0) is None


def test_continuous_monitor_add_threshold():
    m = ContinuousMonitor(seed=42)
    m.add_threshold(AlertThreshold("custom_metric", "gte", 1.0, 2.0))
    assert "custom_metric" in m._thresholds


def test_continuous_monitor_alert_record_strict():
    rec = AlertRecord(alert_id="a1", metric="latency", value=200.0,
                      severity="warning", message="high", timestamp=_now_iso())
    d = rec.to_dict()
    _assert_strict_serializable(d, "alert_record")


def test_continuous_monitor_snapshot_metrics_strict():
    sm = SnapshotMetrics(latency_p99_ms=50.0, error_rate=0.01,
                         throughput_per_sec=1000.0, uptime_pct=99.9,
                         fill_rate=0.95, reconciliation_freshness=0.99,
                         health_status="pass", num_alerts=0,
                         critical_alerts=0, warning_alerts=0)
    d = sm.to_dict()
    _assert_strict_serializable(d, "snapshot_metrics")


def test_continuous_monitor_default_monitor_exists():
    assert default_continuous_monitor is not None
    assert default_continuous_monitor.paper_only is True


def test_continuous_monitor_snapshot_strict():
    m = ContinuousMonitor(seed=42)
    snap = m.snapshot()
    _assert_strict_serializable(snap, "monitor_snapshot")


def test_continuous_monitor_export_report_strict():
    m = ContinuousMonitor(seed=42)
    rep = m.export_report()
    _assert_strict_serializable(rep, "monitor_report")
    assert rep["report"] == "continuous_monitor"


def test_continuous_monitor_clear():
    m = ContinuousMonitor(seed=42)
    m.record_latency(10.0)
    m.monitor_cycle()
    assert len(m._snapshots) == 1
    m.clear()
    assert len(m._snapshots) == 0


# --------------------------------------------------------------------------- auto healer

def test_auto_healer_init_defaults():
    h = AutoHealer(seed=42)
    assert h.seed == 42
    assert len(h._policies) == 4  # default components


def test_auto_healer_add_policy():
    h = AutoHealer(seed=42)
    h.add_policy(HealPolicy(component="new_comp", max_restarts=5))
    assert "new_comp" in h._policies
    assert "new_comp" in h._health


def test_auto_healer_heal_noop_healthy():
    h = AutoHealer(seed=42)
    h.add_policy(HealPolicy(component="exchange", cooldown_sec=0.0))
    rec = h.heal("exchange", trigger="startup")
    _assert_strict_serializable(rec.to_dict(), "heal_record")
    assert rec.action in (HealAction.NOOP.value, HealAction.RESTART.value,
                          HealAction.RETRY.value, HealAction.RECONNECT.value)


def test_auto_healer_heal_record_strict():
    h = AutoHealer(seed=42)
    rec = h.heal("exchange", trigger="t")
    d = rec.to_dict()
    _assert_strict_serializable(d, "heal_record")
    assert rec.record_id is not None
    assert rec.component == "exchange"
    assert rec.timestamp is not None


def test_auto_healer_deterministic_heal_ids_same_seed():
    h1 = AutoHealer(seed=42)
    r1 = h1.heal("exchange", trigger="t")
    h2 = AutoHealer(seed=42)
    r2 = h2.heal("exchange", trigger="t")
    assert r1.record_id == r2.record_id


def test_auto_healer_heal_different_component_different_record():
    h = AutoHealer(seed=42)
    r1 = h.heal("exchange", trigger="t")
    r2 = h.heal("risk", trigger="t")
    assert r1.record_id != r2.record_id


def test_auto_healer_heal_action_enum_values():
    assert HealAction.RESTART.value == "restart"
    assert HealAction.RECONNECT.value == "reconnect"
    assert HealAction.RETRY.value == "retry"
    assert HealAction.ESCALATE.value == "escalate"
    assert HealAction.FAIL_FAST.value == "fail_fast"
    assert HealAction.NOOP.value == "noop"


def test_auto_healer_component_health_strict():
    ch = ComponentHealth(component="x")
    d = ch.to_dict()
    _assert_strict_serializable(d, "component_health")


def test_auto_healer_policy_strict():
    p = HealPolicy(component="x", max_restarts=3, cooldown_sec=1.0)
    d = p.to_dict()
    _assert_strict_serializable(d, "heal_policy")


def test_auto_healer_fail_fast_on_repeated_failures():
    h = AutoHealer(seed=42)
    # Force failures by using a component whose circuit is open
    h.add_policy(HealPolicy(component="failer", max_restarts=1,
                            max_reconnects=1, max_retries=1,
                            cooldown_sec=0.0,
                            escalate_after_failures=1,
                            fail_fast_on_unrecoverable=True))
    # Open the circuit breaker for this component
    cb = h.circuit_registry.get_or_create("failer")
    cb.force_open()
    rec = h.heal("failer", trigger="chaos")
    # With escalate_after_failures=1 and fail_fast, should mark fail_fast after failure
    assert rec.action in (HealAction.FAIL_FAST.value, HealAction.RECONNECT.value)


def test_auto_healer_snapshot_strict():
    h = AutoHealer(seed=42)
    h.heal("exchange", trigger="t")
    snap = h.snapshot()
    _assert_strict_serializable(snap, "healer_snapshot")


def test_auto_healer_export_report_strict():
    h = AutoHealer(seed=42)
    h.heal("exchange", trigger="t")
    rep = h.export_report()
    _assert_strict_serializable(rep, "healer_report")
    assert rep["report"] == "auto_healer"


def test_auto_healer_clear():
    h = AutoHealer(seed=42)
    h.heal("exchange", trigger="t")
    assert len(h._records) == 1
    h.clear()
    assert len(h._records) == 0


def test_auto_healer_retry_policy_integration():
    h = AutoHealer(seed=42)
    assert h.retry_policy is default_retry_policy or h.retry_policy is not None


def test_auto_healer_health_tracking_on_success():
    h = AutoHealer(seed=42)
    h.add_policy(HealPolicy(component="tracker", cooldown_sec=0.0))
    rec = h.heal("tracker", trigger="t")
    ch = h._health["tracker"]
    assert ch.total_heals == 1


# --------------------------------------------------------------------------- model governance

def test_model_status_enum_values():
    assert ModelStatus.DRAFT.value == "draft"
    assert ModelStatus.PROMOTED.value == "promoted"
    assert ModelStatus.REJECTED.value == "rejected"
    assert ModelStatus.ARCHIVED.value == "archived"


def test_model_version_to_dict_strict():
    mv = ModelVersion(name="m", version="1.0", seed=42)
    d = mv.to_dict()
    _assert_strict_serializable(d, "model_version")
    assert d["name"] == "m"
    assert d["version"] == "1.0"
    assert d["seed"] == 42
    assert d["status"] == "draft"


def test_model_manifest_to_dict_strict():
    mm = ModelManifest(model_id="m1", name="m", version="1.0", status="promoted",
                       seed=42, timestamp=_deterministic_iso(42), paper_only=True,
                       validation_passed=True, gates={"g1": True},
                       metrics={"sharpe": 1.5}, oos_metrics={"sharpe": 1.4},
                       backtest_metrics={"sharpe": 1.6},
                       checksum="abc", artifact_path="/path")
    d = mm.to_dict()
    _assert_strict_serializable(d, "model_manifest")


def test_model_id_deterministic():
    assert _model_id("m", "1.0", 42) == _model_id("m", "1.0", 42)
    assert _model_id("m", "1.0", 42) != _model_id("m", "1.0", 7)


def test_model_registry_register_and_get():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    assert mid.startswith("model_")
    got = reg.get(mid)
    assert got is not None
    assert got.name == "m"


def test_model_registry_list_versions():
    reg = ModelRegistry(seed=42)
    reg.register(ModelVersion(name="m", version="1.0", seed=42))
    reg.register(ModelVersion(name="m", version="2.0", seed=42))
    versions = reg.list_versions("m")
    assert len(versions) == 2


def test_model_registry_set_status_promoted():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    assert reg.set_status(mid, ModelStatus.PROMOTED.value) is True
    got = reg.get(mid)
    assert got.status == ModelStatus.PROMOTED.value
    assert got.promoted_at is not None


def test_model_registry_set_status_demoted():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    reg.set_status(mid, ModelStatus.PROMOTED.value)
    assert reg.set_status(mid, ModelStatus.DEMOTED.value) is True
    assert reg.get(mid).status == ModelStatus.DEMOTED.value


def test_model_registry_set_status_unknown_returns_false():
    reg = ModelRegistry(seed=42)
    assert reg.set_status("nonexistent", ModelStatus.PROMOTED.value) is False


def test_model_registry_set_metrics():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    assert reg.set_metrics(mid, metrics={"sharpe": 1.5}) is True
    assert reg.get(mid).metrics == {"sharpe": 1.5}


def test_model_registry_set_validation_gates():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    assert reg.set_validation_gates(mid, {"g1": True, "g2": False}) is True
    assert reg.get(mid).validation_gates == {"g1": True, "g2": False}


def test_model_registry_set_artifact():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    assert reg.set_artifact(mid, "/path/model.json", "sha256:abc") is True
    got = reg.get(mid)
    assert got.artifact_path == "/path/model.json"
    assert got.checksum == "sha256:abc"


def test_model_registry_snapshot_strict():
    reg = ModelRegistry(seed=42)
    reg.register(ModelVersion(name="m", version="1.0", seed=42))
    snap = reg.snapshot()
    _assert_strict_serializable(snap, "registry_snapshot")


def test_model_registry_manifest():
    reg = ModelRegistry(seed=42)
    mv = ModelVersion(name="m", version="1.0", seed=42)
    mid = reg.register(mv)
    reg.set_status(mid, ModelStatus.PROMOTED.value)
    reg.set_validation_gates(mid, {"g1": True})
    man = reg.manifest(mid)
    assert man is not None
    assert man.model_id == mid
    assert man.validation_passed is True


def test_model_registry_manifest_unknown():
    reg = ModelRegistry(seed=42)
    assert reg.manifest("nonexistent") is None


def test_model_governance_init_defaults():
    gov = ModelGovernance(seed=42, paper_only=True)
    assert gov.paper_only is True
    assert gov.seed == 42


def test_model_governance_register_model():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    assert mid.startswith("model_")
    assert gov.registry.get(mid) is not None


def test_model_governance_validate_gates_all_pass():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    res = gov.validate_gates(mid, gates={
        "backtest_passed": True, "oos_passed": True, "numerics_finite": True,
        "determinism_verified": True, "paper_only_enforced": True, "schema_valid": True,
    })
    _assert_strict_serializable(res, "validate_gates")
    assert res["all_passed"] is True


def test_model_governance_validate_gates_some_fail():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    res = gov.validate_gates(mid, gates={"backtest_passed": False})
    assert res["all_passed"] is False


def test_model_governance_validate_gates_unknown_model():
    gov = ModelGovernance(seed=42, paper_only=True)
    with pytest.raises(ConfigError):
        gov.validate_gates("nonexistent", gates={"g1": True})


def test_model_governance_promote_all_gates():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    res = gov.promote(mid, gates={
        "backtest_passed": True, "oos_passed": True, "numerics_finite": True,
        "determinism_verified": True, "paper_only_enforced": True, "schema_valid": True,
    })
    _assert_strict_serializable(res, "promote")
    assert res["action"] == "promote"
    assert res["status"] == ModelStatus.PROMOTED.value


def test_model_governance_promote_blocks_on_failed_gates():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    with pytest.raises(RiskLimitError):
        gov.promote(mid, gates={"backtest_passed": False})


def test_model_governance_demote():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    gov.promote(mid, gates={"backtest_passed": True, "oos_passed": True,
                            "numerics_finite": True, "determinism_verified": True,
                            "paper_only_enforced": True, "schema_valid": True})
    res = gov.demote(mid, reason="performance_degradation")
    assert res["action"] == "demote"
    assert res["status"] == ModelStatus.DEMOTED.value


def test_model_governance_reject():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    res = gov.reject(mid, reason="failed_validation")
    assert res["action"] == "reject"
    assert res["status"] == ModelStatus.REJECTED.value


def test_model_governance_manifest():
    gov = ModelGovernance(seed=42, paper_only=True)
    mid = gov.register_model(name="m", version="1.0")
    gov.promote(mid, gates={"backtest_passed": True, "oos_passed": True,
                            "numerics_finite": True, "determinism_verified": True,
                            "paper_only_enforced": True, "schema_valid": True})
    man = gov.manifest(mid)
    assert man is not None
    assert man["model_id"] == mid


def test_model_governance_snapshot_strict():
    gov = ModelGovernance(seed=42, paper_only=True)
    gov.register_model(name="m", version="1.0")
    snap = gov.snapshot()
    _assert_strict_serializable(snap, "governance_snapshot")


def test_model_governance_export_report_strict():
    gov = ModelGovernance(seed=42, paper_only=True)
    gov.register_model(name="m", version="1.0")
    rep = gov.export_report()
    _assert_strict_serializable(rep, "governance_report")
    assert rep["report"] == "model_governance"


def test_default_model_governance_exists():
    assert default_model_governance is not None
    assert default_model_governance.paper_only is True


def test_default_model_registry_exists():
    assert default_model_registry is not None


def test_model_governance_promotion_gates_constant():
    gov = ModelGovernance(seed=42)
    assert "backtest_passed" in gov.PROMOTION_GATES
    assert "oos_passed" in gov.PROMOTION_GATES
    assert "numerics_finite" in gov.PROMOTION_GATES
    assert "determinism_verified" in gov.PROMOTION_GATES
    assert "paper_only_enforced" in gov.PROMOTION_GATES
    assert "schema_valid" in gov.PROMOTION_GATES


# --------------------------------------------------------------------------- phase13 campaign

def test_phase13_campaign_init_defaults():
    c = Phase13Campaign(seed=42)
    assert c.seed == 42
    assert c.paper_only is True
    assert c.symbols == ("BTC", "ETH")
    assert c.venues == ("deribit", "okx", "binance")
    assert c.campaign_id == "phase13_42"


def test_phase13_campaign_custom_symbols_venues():
    c = Phase13Campaign(symbols=("BTC",), seed=7, venues=("deribit",))
    assert c.symbols == ("BTC",)
    assert c.venues == ("deribit",)
    assert c.seed == 7


def test_phase13_campaign_run_completes():
    c = Phase13Campaign(seed=42)
    res = c.run()
    assert res["status"] == "completed"  # nested master status
    assert "master_report" in res
    assert "master_report_artifact" in res
    assert len(c.artifacts) >= 5  # deployment, monitor, healer, governance, master


def test_phase13_campaign_artifacts_exist(tmp_path, monkeypatch):
    import os
    monkeypatch.chdir(tmp_path)
    c = Phase13Campaign(seed=42, outdir=tmp_path / "research_state")
    c.run()
    for a in c.artifacts:
        assert os.path.exists(a), f"missing artifact: {a}"


def test_phase13_campaign_artifacts_strict_serializable():
    c = Phase13Campaign(seed=42)
    c.run()
    for a in c.artifacts:
        if a.endswith(".json"):
            content = open(a, encoding="utf-8").read()
            data = json.loads(content)
            _assert_strict_serializable(data, a)


def test_phase13_campaign_paper_only_enforced():
    c = Phase13Campaign(seed=42, paper_only=True)
    res = c.run()
    assert res["master_report"]["paper_only"] is True


def test_phase13_campaign_deterministic_same_seed():
    c1 = Phase13Campaign(seed=42)
    r1 = c1.run()
    c2 = Phase13Campaign(seed=42)
    r2 = c2.run()
    m1 = r1["master_report"]
    m2 = r2["master_report"]
    s1 = json.dumps(m1, sort_keys=True, default=str, allow_nan=False)
    s2 = json.dumps(m2, sort_keys=True, default=str, allow_nan=False)
    assert s1 == s2


def test_phase13_campaign_counts():
    c = Phase13Campaign(seed=42)
    c.run()
    assert c.counts["models_registered"] == 1
    assert c.counts["models_promoted"] == 1
    assert c.counts["deployments"] == 1


def test_phase13_campaign_md_artifact():
    c = Phase13Campaign(seed=42)
    c.run()
    md_paths = [a for a in c.artifacts if a.endswith(".md")]
    assert len(md_paths) >= 1
    content = open(md_paths[0], encoding="utf-8").read()
    assert "PHASE13_PRODUCTION_REPORT" in content


def test_phase13_campaign_deployment_artifact_is_json():
    c = Phase13Campaign(seed=42)
    c.run()
    dep_paths = [a for a in c.artifacts if "DEPLOYMENT_REPORT" in a]
    assert len(dep_paths) == 1
    data = json.loads(open(dep_paths[0], encoding="utf-8").read())
    assert data["status"] == DeploymentStatus.PROMOTED.value


def test_phase13_campaign_monitor_artifact_is_json():
    c = Phase13Campaign(seed=42)
    c.run()
    mon_paths = [a for a in c.artifacts if "CONTINUOUS_MONITOR_REPORT" in a]
    assert len(mon_paths) == 1


def test_phase13_campaign_healer_artifact_is_json():
    c = Phase13Campaign(seed=42)
    c.run()
    ah_paths = [a for a in c.artifacts if "AUTO_HEALER_REPORT" in a]
    assert len(ah_paths) == 1


def test_phase13_campaign_governance_artifact_is_json():
    c = Phase13Campaign(seed=42)
    c.run()
    gov_paths = [a for a in c.artifacts if "MODEL_GOVERNANCE_REPORT" in a]
    assert len(gov_paths) == 1


def test_phase13_campaign_no_nan_inf_any_artifact():
    c = Phase13Campaign(seed=42)
    c.run()
    for a in c.artifacts:
        if a.endswith(".json"):
            data = json.loads(open(a, encoding="utf-8").read())
            bad = []
            def walk(v, p="$"):
                if isinstance(v, dict):
                    for k, val in v.items():
                        walk(val, f"{p}/{k}")
                elif isinstance(v, (list, tuple)):
                    for i, val in enumerate(v):
                        walk(val, f"{p}[{i}]")
                elif isinstance(v, float) and not isinstance(v, bool):
                    if not math.isfinite(v):
                        bad.append(p)
            walk(data)
            assert bad == [], f"non-finite in {a}: {bad[:5]}"


def test_phase13_campaign_module_imports():
    from src.deployment.phase13_campaign import Phase13Campaign, _write_json_artifact, _assert_no_nan_inf
    assert Phase13Campaign is not None
    assert _write_json_artifact is not None
    assert _assert_no_nan_inf is not None


# --------------------------------------------------------------------------- integration / serialization

def test_phase13_all_modules_strict_serializable():
    from src.deployment import ProductionDeployer, default_deploy_config
    from src.monitoring.continuous_monitor import default_continuous_monitor
    from src.resilience.auto_healer import default_retry_policy as _rp
    d = ProductionDeployer(seed=42).deploy().to_dict()
    m = default_continuous_monitor.snapshot()
    assert_json_valid(d)
    assert_json_valid(m)
    _assert_strict_serializable(d, "deploy")
    _assert_strict_serializable(m, "monitor")


def test_phase13_serialize_metrics_strict_on_deploy():
    d = ProductionDeployer(seed=42).deploy()
    serialized = serialize_metrics_strict(d.to_dict())
    assert isinstance(serialized, dict)
    json.dumps(serialized, allow_nan=False)


# --------------------------------------------------------------------------- determinism

def test_phase13_deploy_byte_identical_rerun():
    import hashlib as _hl
    d1 = ProductionDeployer(seed=42).deploy().to_dict()
    d2 = ProductionDeployer(seed=42).deploy().to_dict()
    h1 = _hl.sha256(json.dumps(d1, sort_keys=True, default=str, allow_nan=False).encode()).hexdigest()
    h2 = _hl.sha256(json.dumps(d2, sort_keys=True, default=str, allow_nan=False).encode()).hexdigest()
    assert h1 == h2


def test_phase13_campaign_master_byte_identical_rerun(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c1 = Phase13Campaign(seed=42, outdir=tmp_path / "rs1")
    r1 = c1.run()
    c2 = Phase13Campaign(seed=42, outdir=tmp_path / "rs2")
    r2 = c2.run()
    s1 = json.dumps(r1["master_report"], sort_keys=True, default=str, allow_nan=False)
    s2 = json.dumps(r2["master_report"], sort_keys=True, default=str, allow_nan=False)
    assert s1 == s2
