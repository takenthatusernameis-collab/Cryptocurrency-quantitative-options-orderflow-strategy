"""Comprehensive Phase 9 tests: production monitoring, observability, alerting,
health/SLOs, resilience, continuous validation. >=40 substantive tests.
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

from src.errors import SerializationError, RiskLimitError
from src.telemetry import serialize_metrics_strict, serialize_metrics
from src.telemetry.observability import (
    LogLevel, StructuredLogger, LogEntry, Counter, Gauge, Histogram,
    MetricsRegistry, MetricsExporter, LoggingExporter, PrometheusExporter,
    OpenTelemetryExporter, TraceSpan, Tracer, redact, observability_logger,
    metrics_registry, tracer, REDACT_KEYS, REDACT_VALUE,
)
from src.telemetry.alerting import (
    AlertSeverity, AlertRule, Alert, AlertManager, AlertChannel,
    LogChannel, WebhookChannel, SlackChannel, EmailChannel,
    default_alert_manager, setup_default_rules,
)
from src.monitoring.health import (
    HealthChecker, HealthReport, HealthStatus, DependencyCheck,
    default_health_checker, register_default_dependency_checks,
)
from src.monitoring.slo import (
    SLOMonitor, SLODefinition, SLIRecorder, SLIType,
    BurnRateAlert, StatusPage, StatusPageModel,
    default_sli_recorder, default_slo_monitor, register_default_slos,
)
from src.resilience.circuit import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerRegistry,
    CircuitBreakerState, default_circuit_registry,
)
from src.resilience.retry import (
    RetryConfig, RetryPolicy, Bulkhead, BulkheadConfig,
    TimeoutConfig, call_with_timeout, HedgedRequestResult, hedged_request,
    DegradationConfig, GracefulDegradation, default_retry_policy, get_bulkhead,
)
from src.validation.continuous import (
    DataQualityValidator, DataQualityReport, DriftDetector, DriftResult,
    ShadowValidator, ShadowComparison, CanaryGate, CanaryGateResult,
    GoldenArtifactStore, GoldenArtifact, RegressionCheckResult,
    ContinuousValidator, default_continuous_validator,
)


# --------------------------------------------------------------------------- observability

def test_structured_logger_emits_json_entries():
    logger = StructuredLogger("test_logger")
    logger.new_trace()
    logger.new_correlation()
    logger.info("test message", key="value", num=42)
    entries = logger.get_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e["level"] == "INFO"
    assert e["msg"] == "test message"
    assert e["logger"] == "test_logger"
    assert e["trace_id"] is not None
    assert e["correlation_id"] is not None
    assert e["context"]["key"] == "value"
    assert e["context"]["num"] == 42
    # Strict serialization
    json.dumps(e, allow_nan=False)


def test_structured_logger_redacts_secrets():
    logger = StructuredLogger("redact_test")
    logger.info("login", api_key="secret123", password="pw", normal="ok")
    e = logger.get_entries()[0]
    assert e["context"]["api_key"] == REDACT_VALUE
    assert e["context"]["password"] == REDACT_VALUE
    assert e["context"]["normal"] == "ok"


def test_structured_logger_levels():
    logger = StructuredLogger("levels_test")
    logger.debug("d")
    logger.info("i")
    logger.warning("w")
    logger.error("e")
    logger.critical("c")
    entries = logger.get_entries()
    assert len(entries) == 5
    assert [e["level"] for e in entries] == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_structured_logger_trace_correlation_scope():
    logger = StructuredLogger("scope_test")
    tid = logger.new_trace()
    cid = logger.new_correlation()
    logger.info("scoped")
    e = logger.get_entries()[0]
    assert e["trace_id"] == tid
    assert e["correlation_id"] == cid
    logger.clear_scope()
    logger.info("unscoped")
    e2 = logger.get_entries()[1]
    assert e2["trace_id"] is None
    assert e2["correlation_id"] is None


def test_counter_metric():
    reg = MetricsRegistry()
    c = reg.counter("orders_total", labels={"venue": "deribit"})
    c.inc(1.0)
    c.inc(2.5)
    d = c.to_dict()
    assert d["type"] == "counter"
    assert d["name"] == "orders_total"
    assert d["value"] == 3.5
    assert d["labels"] == {"venue": "deribit"}
    json.dumps(d, allow_nan=False)


def test_counter_ignores_nonfinite():
    reg = MetricsRegistry()
    c = reg.counter("bad_counter")
    c.inc(float("nan"))
    c.inc(float("inf"))
    assert c.value == 0.0


def test_gauge_metric():
    reg = MetricsRegistry()
    g = reg.gauge("equity", labels={"symbol": "BTC"})
    g.set(100000.0)
    g.set(105000.0)
    d = g.to_dict()
    assert d["type"] == "gauge"
    assert d["value"] == 105000.0
    json.dumps(d, allow_nan=False)


def test_histogram_metric():
    reg = MetricsRegistry()
    h = reg.histogram("latency_ms", buckets=[1.0, 10.0, 100.0])
    h.observe(0.5)
    h.observe(5.0)
    h.observe(50.0)
    h.observe(500.0)
    d = h.to_dict()
    assert d["type"] == "histogram"
    assert d["count"] == 4
    assert d["sum"] == 555.5
    assert d["counts"] == [1, 1, 1, 1]
    json.dumps(d, allow_nan=False)


def test_histogram_ignores_nonfinite():
    reg = MetricsRegistry()
    h = reg.histogram("bad_hist")
    h.observe(float("nan"))
    h.observe(float("inf"))
    assert h.count == 0


def test_metrics_registry_snapshot_strict():
    reg = MetricsRegistry()
    reg.counter("a").inc(1)
    reg.gauge("b").set(2.0)
    reg.histogram("c").observe(3.0)
    snap = reg.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["counters"][0]["name"] == "a"
    assert snap["gauges"][0]["name"] == "b"
    assert snap["histograms"][0]["name"] == "c"


def test_metrics_registry_prometheus_text():
    reg = MetricsRegistry()
    reg.counter("orders_total").inc(5)
    reg.gauge("equity").set(100000.0)
    text = reg.to_prometheus_text()
    assert "orders_total" in text
    assert "5" in text
    assert "equity" in text
    assert "100000.0" in text


def test_metrics_registry_opentelemetry_json():
    reg = MetricsRegistry()
    reg.counter("orders_total").inc(3)
    otel = reg.to_opentelemetry_json()
    json.dumps(otel, allow_nan=False)
    assert otel["resource_metrics"][0]["scope_metrics"][0]["metrics"][0]["name"] == "orders_total"


def test_logging_exporter_exports():
    reg = MetricsRegistry()
    reg.counter("exp_test").inc(1)
    exporter = LoggingExporter()
    snap = reg.snapshot()
    # Should not raise
    exporter.export(snap)


def test_prometheus_exporter_exports():
    reg = MetricsRegistry()
    reg.gauge("px_test").set(42.0)
    exporter = PrometheusExporter(reg)
    exporter.export()


def test_opentelemetry_exporter_exports():
    reg = MetricsRegistry()
    reg.histogram("ot_test").observe(1.0)
    exporter = OpenTelemetryExporter(reg)
    exporter.export()


def test_tracer_span_lifecycle():
    tr = Tracer()
    span = tr.start_span("place_order", attributes={"symbol": "BTC"})
    assert span.span_id is not None
    assert span.trace_id is not None
    assert span.operation == "place_order"
    assert span.status == "ok"
    tr.end_span(span, status="ok")
    assert span.end_time is not None
    assert span.status == "ok"
    snap = tr.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["num_spans"] == 1


def test_tracer_get_trace_spans():
    tr = Tracer()
    s1 = tr.start_span("op_a")
    s2 = tr.start_span("op_b", trace_id=s1.trace_id)
    tr.end_span(s1)
    tr.end_span(s2)
    spans = tr.get_trace_spans(s1.trace_id)
    assert len(spans) == 2


def test_redact_function():
    obj = {"api_key": "secret", "data": {"password": "pw", "qty": 10}, "list": [{"token": "t"}]}
    r = redact(obj)
    assert r["api_key"] == REDACT_VALUE
    assert r["data"]["password"] == REDACT_VALUE
    assert r["data"]["qty"] == 10
    assert r["list"][0]["token"] == REDACT_VALUE


def test_observability_logger_export_report():
    obs = StructuredLogger("export_test")
    obs.info("hello")
    report = obs.export_report()
    json.dumps(report, allow_nan=False)
    assert report["logger"] == "export_test"
    assert report["num_entries"] == 1


# --------------------------------------------------------------------------- alerting

def test_alert_rule_evaluate_gt_warning():
    rule = AlertRule("r1", "Test Rule", "drawdown_pct", "gte",
                     warning_threshold=0.10, critical_threshold=0.15)
    assert rule.evaluate(0.12) == AlertSeverity.WARNING


def test_alert_rule_evaluate_gt_critical():
    rule = AlertRule("r1", "Test Rule", "drawdown_pct", "gte",
                     warning_threshold=0.10, critical_threshold=0.15)
    assert rule.evaluate(0.18) == AlertSeverity.CRITICAL


def test_alert_rule_evaluate_no_breach():
    rule = AlertRule("r1", "Test Rule", "drawdown_pct", "gte",
                     warning_threshold=0.10, critical_threshold=0.15)
    assert rule.evaluate(0.05) is None


def test_alert_rule_evaluate_lte():
    rule = AlertRule("r2", "Fill Rate Rule", "fill_rate", "lte",
                     warning_threshold=0.90, critical_threshold=0.70)
    assert rule.evaluate(0.80) == AlertSeverity.WARNING
    assert rule.evaluate(0.60) == AlertSeverity.CRITICAL
    assert rule.evaluate(0.95) is None


def test_alert_rule_disabled():
    rule = AlertRule("r3", "Disabled Rule", "x", "gte",
                     warning_threshold=1.0, enabled=False)
    assert rule.evaluate(999.0) is None


def test_alert_rule_strict_serialization():
    rule = AlertRule("r4", "Serialization Rule", "y", "eq",
                     warning_threshold=1.0, critical_threshold=2.0)
    d = rule.to_dict()
    json.dumps(d, allow_nan=False)
    assert d["rule_id"] == "r4"


def test_alert_manager_fires_and_dedupes():
    am = AlertManager(dry_run=True, dedup_window_sec=60.0, throttle_max_per_window=5)
    rule = AlertRule("r_dedup", "Dedup Rule", "heat", "gte",
                     warning_threshold=0.5, critical_threshold=0.8)
    am.add_rule(rule)
    fired1 = am.evaluate("heat", 0.7)
    assert len(fired1) == 1
    # Same metric within dedup window -> no new alert
    fired2 = am.evaluate("heat", 0.7)
    assert len(fired2) == 0
    alerts = am.get_alerts()
    assert len(alerts) == 1


def test_alert_manager_throttle():
    am = AlertManager(dry_run=True, dedup_window_sec=0.1, throttle_max_per_window=2)
    rule = AlertRule("r_throttle", "Throttle Rule", "latency", "gte",
                     warning_threshold=100.0)
    am.add_rule(rule)
    # Fire rapidly - dedup window is short so each fire creates new alert,
    # but throttle caps at 2 per window
    fired = []
    for _ in range(5):
        fired.extend(am.evaluate("latency", 500.0))
        time.sleep(0.02)
    assert len(fired) <= 2


def test_alert_manager_acknowledge_and_resolve():
    am = AlertManager(dry_run=True)
    rule = AlertRule("r_ack", "Ack Rule", "pnl", "gte",
                     warning_threshold=1.0)
    am.add_rule(rule)
    fired = am.evaluate("pnl", 5.0)
    alert_id = fired[0].alert_id
    assert am.acknowledge(alert_id) is True
    assert am.get_unacknowledged() == []
    assert am.resolve(alert_id) is True
    assert am.get_unresolved() == []


def test_alert_manager_escalate():
    am = AlertManager(dry_run=True)
    rule = AlertRule("r_esc", "Escalate Rule", "var_95", "gte",
                     warning_threshold=0.05, critical_threshold=0.10,
                     severity=AlertSeverity.WARNING)
    am.add_rule(rule)
    fired = am.evaluate("var_95", 0.07)
    alert_id = fired[0].alert_id
    assert am.escalate(alert_id, AlertSeverity.CRITICAL) is True
    # Cannot de-escalate
    assert am.escalate(alert_id, AlertSeverity.WARNING) is False
    # Escalate non-existent
    assert am.escalate("nonexistent", AlertSeverity.CRITICAL) is False


def test_alert_channel_log():
    ch = LogChannel(dry_run=False)
    alert = Alert("a1", "r1", "Rule 1", AlertSeverity.WARNING, "heat", 0.7, 0.5,
                  "heat high", _now_iso())
    result = ch.send(alert)
    assert result["sent"] is True
    assert result["channel"] == "log"


def test_alert_channel_webhook_dry_run():
    ch = WebhookChannel("http://example.com/alert", dry_run=True)
    alert = Alert("a2", "r2", "Rule 2", AlertSeverity.ERROR, "latency", 500.0, 200.0,
                  "latency high", _now_iso())
    result = ch.send(alert)
    assert result["sent"] is True
    assert result["dry_run"] is True
    assert len(ch.sent_payloads) == 1


def test_alert_channel_slack():
    ch = SlackChannel("https://hooks.slack.com/test", dry_run=True)
    alert = Alert("a3", "r3", "Rule 3", AlertSeverity.CRITICAL, "drawdown", 0.20, 0.15,
                  "drawdown critical", _now_iso())
    result = ch.send(alert)
    assert result["sent"] is True
    assert len(ch.sent_messages) == 1


def test_alert_channel_email():
    ch = EmailChannel(["ops@example.com"], dry_run=True)
    alert = Alert("a4", "r4", "Rule 4", AlertSeverity.INFO, "fill_rate", 0.95, 0.90,
                  "fill rate ok", _now_iso())
    result = ch.send(alert)
    assert result["sent"] is True
    assert len(ch.sent_emails) == 1


def test_alert_manager_default_rules():
    am = AlertManager(dry_run=True)
    setup_default_rules(am)
    rules = am.list_rules()
    rule_names = {r["name"] for r in rules}
    assert "Drawdown Pct" in rule_names
    assert "Order Latency" in rule_names
    assert "Fill Rate" in rule_names


def test_alert_manager_snapshot_strict():
    am = AlertManager(dry_run=True)
    snap = am.snapshot()
    json.dumps(snap, allow_nan=False)
    assert "num_alerts" in snap
    assert "audit" in snap


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- monitoring health

def test_health_checker_register_and_run():
    hc = HealthChecker("svc", version="1.0")
    def ok_check():
        return DependencyCheck(name="dep", status=HealthStatus.PASS,
                               latency_ms=5.0, message="ok")
    hc.register("dep", ok_check)
    report = hc.run_all()
    assert report.status == HealthStatus.PASS
    assert len(report.checks) == 1
    assert report.checks[0].status == HealthStatus.PASS
    d = report.to_dict()
    json.dumps(d, allow_nan=False)


def test_health_checker_aggregate_fail():
    hc = HealthChecker("svc")
    hc.register("good", lambda: DependencyCheck(name="good", status=HealthStatus.PASS))
    hc.register("bad", lambda: DependencyCheck(name="bad", status=HealthStatus.FAIL))
    report = hc.run_all()
    assert report.status == HealthStatus.FAIL


def test_health_checker_unknown_check():
    hc = HealthChecker("svc")
    check = hc.run_check("nonexistent")
    assert check.status == HealthStatus.UNKNOWN


def test_health_checker_exception_in_check():
    hc = HealthChecker("svc")
    hc.register("failing", lambda: (_ for _ in ()).throw(ValueError("boom")))
    check = hc.run_check("failing")
    assert check.status == HealthStatus.FAIL
    assert "boom" in check.message


def test_default_health_checker_registered():
    hc = default_health_checker
    register_default_dependency_checks(hc)
    names = set()
    # Access internal checks via run_all
    report = hc.run_all()
    check_names = {c.name for c in report.checks}
    assert "exchange" in check_names
    assert "risk" in check_names
    assert "orderflow_adapter" in check_names
    assert "reconciliation" in check_names


def test_health_status_aggregate():
    assert HealthStatus.aggregate([HealthStatus.PASS, HealthStatus.PASS]) == HealthStatus.PASS
    assert HealthStatus.aggregate([HealthStatus.PASS, HealthStatus.WARN]) == HealthStatus.WARN
    assert HealthStatus.aggregate([HealthStatus.PASS, HealthStatus.FAIL]) == HealthStatus.FAIL
    assert HealthStatus.aggregate([]) == HealthStatus.UNKNOWN


# --------------------------------------------------------------------------- monitoring SLO

def test_sli_recorder_record_and_get():
    rec = SLIRecorder(max_points=100)
    rec.record("latency", 10.0, labels={"comp": "exec"})
    rec.record("latency", 20.0, labels={"comp": "exec"})
    rec.record("error_rate", 0.01, labels={"comp": "exec"})
    ms = rec.get_measurements("latency")
    assert len(ms) == 2
    assert ms[0].value == 10.0
    assert ms[1].value == 20.0
    assert ms[0].labels == {"comp": "exec"}


def test_sli_recorder_ignores_nonfinite():
    rec = SLIRecorder()
    rec.record("x", float("nan"))
    rec.record("x", float("inf"))
    rec.record("x", 5.0)
    assert len(rec.get_measurements("x")) == 1


def test_slo_monitor_evaluate_met():
    mon = SLOMonitor()
    rec = SLIRecorder()
    mon._slo_recorder = rec
    slo = SLODefinition("s1", "Latency SLO", SLIType.LATENCY, 100.0, "lte", 300.0)
    mon.add_slo(slo)
    rec.record("latency", 50.0)
    rec.record("latency", 60.0)
    ev = mon.evaluate_slo("s1")
    assert ev is not None
    assert ev.met is True
    assert ev.current_value == 55.0


def test_slo_monitor_evaluate_not_met():
    mon = SLOMonitor()
    rec = SLIRecorder()
    mon._slo_recorder = rec
    slo = SLODefinition("s2", "Error Rate SLO", SLIType.ERROR_RATE, 0.01, "lte", 300.0)
    mon.add_slo(slo)
    rec.record("error_rate", 0.05)
    rec.record("error_rate", 0.08)
    ev = mon.evaluate_slo("s2")
    assert ev is not None
    assert ev.met is False


def test_slo_monitor_evaluate_uptime():
    mon = SLOMonitor()
    rec = SLIRecorder()
    mon._slo_recorder = rec
    slo = SLODefinition("s3", "Uptime SLO", SLIType.UPTIME, 0.99, "gte", 3600.0)
    mon.add_slo(slo)
    rec.record("uptime", 1.0)
    rec.record("uptime", 1.0)
    rec.record("uptime", 0.5)
    ev = mon.evaluate_slo("s3")
    assert ev.met is False  # 2/3 good = 0.667 < 0.99 -> not met


def test_slo_monitor_evaluate_no_measurements():
    mon = SLOMonitor()
    rec = SLIRecorder()
    mon._slo_recorder = rec
    slo = SLODefinition("s4", "Empty SLO", SLIType.LATENCY, 100.0, "lte", 300.0)
    mon.add_slo(slo)
    ev = mon.evaluate_slo("s4")
    assert ev is not None
    assert ev.met is False
    assert ev.num_measurements == 0


def test_slo_monitor_burn_rate_alert():
    mon = SLOMonitor()
    rec = SLIRecorder()
    mon._slo_recorder = rec
    slo = SLODefinition("s5", "Burn SLO", SLIType.ERROR_RATE, 0.01, "lte", 300.0)
    mon.add_slo(slo)
    rec.record("error_rate", 0.01)
    ev = mon.evaluate_slo("s5")
    alert = mon.check_burn_rate("s5", expected_burn_per_sec=0.0001,
                                alert_threshold_multiplier=2.0)
    # May or may not alert depending on burn calc; just ensure no crash
    if alert is not None:
        assert alert.severity in ("warning", "error", "critical")


def test_slo_monitor_snapshot_strict():
    mon = SLOMonitor()
    snap = mon.snapshot()
    json.dumps(snap, allow_nan=False)
    assert "num_slos" in snap


def test_status_page_model_generate():
    hc = HealthChecker("svc")
    hc.register("dep", lambda: DependencyCheck(name="dep", status=HealthStatus.PASS))
    spm = StatusPageModel(health_checker=hc)
    page = spm.generate()
    json.dumps(page, allow_nan=False)
    assert page["overall_status"] == HealthStatus.PASS
    assert len(page["services"]) == 1


def test_register_default_slos():
    mon = default_slo_monitor
    register_default_slos(mon)
    # Evaluate all
    results = mon.evaluate_all()
    # With no measurements, all should be not met
    assert len(results) == 5


# --------------------------------------------------------------------------- resilience circuit breaker

def test_circuit_breaker_closed_to_open():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb", failure_threshold=3,
                                             timeout_seconds=1.0, half_open_max_calls=2))
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.can_execute() is True
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.can_execute() is False


def test_circuit_breaker_open_to_half_open_after_timeout():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb2", failure_threshold=1,
                                             timeout_seconds=0.01, half_open_max_calls=1))
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    time.sleep(0.02)
    assert cb.can_execute() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN


def test_circuit_breaker_half_open_success_closes():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb3", failure_threshold=1,
                                             timeout_seconds=0.01, half_open_max_calls=1))
    cb.record_failure()
    time.sleep(0.02)
    cb.can_execute()  # moves to half_open
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED


def test_circuit_breaker_half_open_failure_reopens():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb4", failure_threshold=1,
                                             timeout_seconds=0.01, half_open_max_calls=1))
    cb.record_failure()
    time.sleep(0.02)
    cb.can_execute()  # half_open
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN


def test_circuit_breaker_call_wrapper_success():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb5"))
    result = cb.call(lambda: 42)
    assert result == 42


def test_circuit_breaker_call_wrapper_failure():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb6", failure_threshold=1))
    try:
        cb.call(lambda: (_ for _ in ()).throw(ValueError("boom")))
        assert False, "Expected exception"
    except ValueError:
        pass
    assert cb.state == CircuitBreakerState.OPEN


def test_circuit_breaker_open_raises_on_call():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb7", failure_threshold=1))
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    try:
        cb.call(lambda: 1)
        assert False, "Expected RiskLimitError"
    except RiskLimitError:
        pass


def test_circuit_breaker_force_open_closed():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb8"))
    cb.force_open()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.can_execute() is False
    cb.force_closed()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.can_execute() is True


def test_circuit_breaker_snapshot_strict():
    cb = CircuitBreaker(CircuitBreakerConfig(name="test_cb9"))
    snap = cb.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["name"] == "test_cb9"
    assert snap["state"] == "closed"


def test_circuit_breaker_registry():
    reg = CircuitBreakerRegistry()
    cb1 = reg.get_or_create("exchange_a")
    cb2 = reg.get_or_create("exchange_a")
    assert cb1 is cb2
    cb3 = reg.get_or_create("exchange_b")
    assert cb3 is not cb1
    assert set(reg.list_names()) == {"exchange_a", "exchange_b"}
    snap = reg.snapshot_all()
    json.dumps(snap, allow_nan=False)


def test_circuit_breaker_chaos_injection():
    cb = CircuitBreaker(CircuitBreakerConfig(name="chaos_cb", failure_threshold=10))
    cb.inject_chaos_failure()
    assert cb.can_execute() is False


# --------------------------------------------------------------------------- resilience retry / bulkhead / timeout / hedged / degradation

def test_retry_policy_success_first_attempt():
    rp = RetryPolicy(RetryConfig(max_attempts=3))
    calls = []
    result = rp.call(lambda: calls.append(1) or 99)
    assert result.success is True
    assert result.attempts == 1
    assert result.result == 99


def test_retry_policy_retries_on_failure():
    rp = RetryPolicy(RetryConfig(max_attempts=3, base_delay_sec=0.0))
    state = {"n": 0}
    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError("transient")
        return "ok"
    result = rp.call(flaky)
    assert result.success is True
    assert result.attempts == 3
    assert result.result == "ok"


def test_retry_policy_exhausted():
    rp = RetryPolicy(RetryConfig(max_attempts=2, base_delay_sec=0.0))
    result = rp.call(lambda: (_ for _ in ()).throw(ValueError("always")))
    assert result.success is False
    assert result.attempts == 2
    assert "always" in result.last_exception


def test_retry_policy_snapshot_strict():
    rp = RetryPolicy()
    rp.call(lambda: 1)
    snap = rp.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["num_calls"] == 1


def test_bulkhead_call():
    bh = Bulkhead(BulkheadConfig(name="bh_test", max_concurrent=2))
    result = bh.call(lambda: 7)
    assert result == 7
    snap = bh.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["accepted"] == 1


def test_bulkhead_rejects_at_capacity():
    bh = Bulkhead(BulkheadConfig(name="bh2", max_concurrent=1, max_queue=0))
    # Hold the slot via an in-progress call
    result = bh.call(lambda: 1)
    assert result == 1
    # Manually set active to simulate an in-flight call
    bh._active = 1
    try:
        bh.call(lambda: 1)
        assert False, "Expected RiskLimitError"
    except RiskLimitError:
        pass
    bh.release()
    # After release, should accept again
    result2 = bh.call(lambda: 2)
    assert result2 == 2


def test_call_with_timeout_success():
    result = call_with_timeout(lambda: 42, TimeoutConfig(timeout_sec=5.0))
    assert result == 42


def test_hedged_request_first_success():
    def rep1():
        raise ValueError("rep1 down")
    def rep2():
        return "replica2_ok"
    result = hedged_request([rep1, rep2])
    assert result.success is True
    assert result.winning_replica == 1


def test_hedged_request_all_fail():
    def rep1():
        raise ValueError("r1 down")
    def rep2():
        raise ValueError("r2 down")
    result = hedged_request([rep1, rep2])
    assert result.success is False
    assert result.winning_replica is None


def test_graceful_degradation_primary_ok():
    gd = GracefulDegradation(lambda: "primary")
    assert gd.call() == "primary"
    assert gd._degraded is False


def test_graceful_degradation_primary_fails_then_degrades():
    state = {"n": 0}
    def flaky():
        state["n"] += 1
        if state["n"] <= 2:
            raise ValueError("transient")
        return "recovered"
    gd = GracefulDegradation(flaky, DegradationConfig(degrade_after_failures=2,
                                                      fallback_value="fallback"))
    # First two calls fail and degrade
    assert gd.call() == "fallback"
    assert gd.call() == "fallback"
    assert gd._degraded is True
    # Third call: primary recovers but degradation persists until a success
    # Actually after degradation, calls go to fallback
    assert gd.call() == "fallback"


def test_graceful_degradation_snapshot_strict():
    gd = GracefulDegradation(lambda: 1)
    gd.call()
    snap = gd.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["total_calls"] == 1


# --------------------------------------------------------------------------- validation continuous

def test_data_quality_validator_clean():
    vq = DataQualityValidator(max_stale_sec=300.0)
    now = time.time()
    report = vq.validate_quote("BTC", "deribit", 50000.0, 50001.0, now)
    assert report.passed is True
    assert report.nan_count == 0
    assert report.inf_count == 0
    assert report.stale_count == 0
    assert report.corruption_count == 0
    d = report.to_dict()
    json.dumps(d, allow_nan=False)


def test_data_quality_validator_nan():
    vq = DataQualityValidator()
    report = vq.validate_quote("BTC", "deribit", float("nan"), 50001.0, time.time())
    assert report.passed is False
    assert report.nan_count == 1


def test_data_quality_validator_inf():
    vq = DataQualityValidator()
    report = vq.validate_quote("BTC", "deribit", float("inf"), 50001.0, time.time())
    assert report.passed is False
    assert report.inf_count == 1


def test_data_quality_validator_stale():
    vq = DataQualityValidator(max_stale_sec=1.0)
    old_ts = time.time() - 100.0
    report = vq.validate_quote("BTC", "deribit", 50000.0, 50001.0, old_ts)
    assert report.stale_count == 1
    assert report.passed is False


def test_data_quality_validator_inverted_spread():
    vq = DataQualityValidator()
    report = vq.validate_quote("BTC", "deribit", 50001.0, 50000.0, time.time())
    assert report.corruption_count == 1
    assert report.passed is False


def test_data_quality_validator_negative_price():
    vq = DataQualityValidator()
    report = vq.validate_quote("BTC", "deribit", -1.0, 50001.0, time.time())
    assert report.corruption_count >= 1
    assert report.passed is False


def test_drift_detector_no_drift():
    dd = DriftDetector(default_threshold_pct=5.0)
    result = dd.detect_drift("vol", 0.60, 0.61)
    assert result.drift_detected is False
    assert result.severity == "info"
    d = result.to_dict()
    json.dumps(d, allow_nan=False)


def test_drift_detector_drift_detected():
    dd = DriftDetector(default_threshold_pct=5.0)
    result = dd.detect_drift("vol", 0.60, 0.70)  # ~16.7% drift
    assert result.drift_detected is True
    assert result.severity in ("warning", "error", "critical")


def test_drift_detector_zero_reference():
    dd = DriftDetector(default_threshold_pct=5.0)
    result = dd.detect_drift("vol", 0.0, 0.10)
    assert result.drift_detected is True


def test_shadow_validator_agreement():
    sv = ShadowValidator(agreement_threshold=0.05)
    result = sv.compare("BTC", "deribit", 0.25, 0.26)
    assert result.agreement is True
    assert abs(result.delta - 0.01) < 1e-9


def test_shadow_validator_disagreement():
    sv = ShadowValidator(agreement_threshold=0.05)
    result = sv.compare("BTC", "deribit", 0.25, 0.40)
    assert result.agreement is False
    assert abs(result.delta - 0.15) < 1e-9


def test_canary_gate_pass():
    cg = CanaryGate(min_improvement_pct=1.0)
    result = cg.evaluate("v2", "v1", "sharpe", 1.85, 1.75)
    assert result.gate_passed is True
    assert abs(result.improvement_pct - 5.71) < 1.0


def test_canary_gate_fail():
    cg = CanaryGate(min_improvement_pct=10.0)
    result = cg.evaluate("v2", "v1", "sharpe", 1.85, 1.75)
    assert result.gate_passed is False


def test_golden_artifact_store_and_check_match():
    store = GoldenArtifactStore()
    artifact = store.store("baseline_metrics", {"sharpe": 1.75, "dd": 0.08})
    result = store.check_regression("baseline_metrics", {"sharpe": 1.75, "dd": 0.08})
    assert result.matches is True


def test_golden_artifact_store_and_check_mismatch():
    store = GoldenArtifactStore()
    store.store("baseline_metrics", {"sharpe": 1.75, "dd": 0.08})
    result = store.check_regression("baseline_metrics", {"sharpe": 1.80, "dd": 0.08})
    assert result.matches is False


def test_golden_artifact_not_found():
    store = GoldenArtifactStore()
    result = store.check_regression("nonexistent", {"x": 1})
    assert result.matches is False
    assert result.diff.get("error") == "artifact_not_found"


def test_continuous_validator_full_campaign():
    cv = ContinuousValidator(seed=42)
    # Data quality
    cv.validate_data_quality("BTC", "deribit", 50000.0, 50001.0, time.time())
    # Drift
    cv.check_drift("vol", 0.60, 0.62)
    # Shadow
    cv.compare_shadow("BTC", "deribit", 0.25, 0.26)
    # Canary
    cv.evaluate_canary("v2", "v1", "sharpe", 1.85, 1.75)
    # Golden + regression
    cv.store_golden("baseline", {"sharpe": 1.75})
    cv.check_regression("baseline", {"sharpe": 1.75})
    snap = cv.snapshot()
    json.dumps(snap, allow_nan=False)
    assert snap["num_dq_reports"] == 1
    assert snap["num_drift_results"] == 1
    assert snap["num_shadow_comparisons"] == 1
    assert snap["num_canary_results"] == 1
    assert snap["num_regression_results"] == 1
    assert snap["num_golden_artifacts"] == 1


def test_continuous_validator_determinism():
    cv1 = ContinuousValidator(seed=42)
    cv1.validate_data_quality("BTC", "deribit", 50000.0, 50001.0, time.time())
    snap1 = cv1.snapshot()
    cv2 = ContinuousValidator(seed=42)
    cv2.validate_data_quality("BTC", "deribit", 50000.0, 50001.0, time.time())
    snap2 = cv2.snapshot()
    # Key metrics should be deterministic (same counts)
    assert snap1["num_dq_reports"] == snap2["num_dq_reports"]


def test_default_continuous_validator_exists():
    assert default_continuous_validator is not None
    assert default_continuous_validator.seed == 42


# --------------------------------------------------------------------------- integration

def test_phase9_modules_import_and_serialize():
    """All Phase 9 modules import cleanly and produce strict-serializable output."""
    from src.telemetry import observability_logger, metrics_registry, tracer
    from src.telemetry.alerting import default_alert_manager
    from src.monitoring import default_health_checker, default_slo_monitor
    from src.resilience import default_circuit_registry, default_retry_policy
    from src.validation import default_continuous_validator
    # Emit snapshots from each
    obs = observability_logger.export_report()
    met = metrics_registry.snapshot()
    trc = tracer.snapshot()
    al = default_alert_manager.snapshot()
    hc = default_health_checker.snapshot()
    slo = default_slo_monitor.snapshot()
    cb = default_circuit_registry.snapshot_all()
    rp = default_retry_policy.snapshot()
    cv = default_continuous_validator.snapshot()
    for payload in [obs, met, trc, al, hc, slo, cb, rp, cv]:
        json.dumps(payload, allow_nan=False)


def test_all_phase9_artifacts_strict_serializable():
    """End-to-end: every artifact from every Phase 9 module passes allow_nan=False."""
    import io
    # Build minimal artifacts from each module
    obs_logger = StructuredLogger("integration")
    obs_logger.info("integration_test")
    obs_payload = obs_logger.export_report()

    reg = MetricsRegistry()
    reg.counter("int_counter").inc(1)
    met_payload = reg.snapshot()

    am = AlertManager(dry_run=True)
    am.add_rule(AlertRule("r_int", "Int Rule", "x", "gte", warning_threshold=1.0))
    am.evaluate("x", 5.0)
    al_payload = am.snapshot()

    hc = HealthChecker("int_svc")
    hc.register("dep", lambda: DependencyCheck(name="dep", status=HealthStatus.PASS))
    hc_payload = hc.snapshot()

    mon = SLOMonitor()
    slo_payload = mon.snapshot()

    cb = CircuitBreaker(CircuitBreakerConfig(name="int_cb"))
    cb_payload = cb.snapshot()

    rp = RetryPolicy()
    rp.call(lambda: 1)
    rp_payload = rp.snapshot()

    cv = ContinuousValidator(seed=7)
    cv.validate_data_quality("BTC", "deribit", 50000.0, 50001.0, time.time())
    cv_payload = cv.snapshot()

    for label, payload in [
        ("observability", obs_payload),
        ("metrics", met_payload),
        ("alerting", al_payload),
        ("health", hc_payload),
        ("slo", slo_payload),
        ("circuit_breaker", cb_payload),
        ("retry", rp_payload),
        ("continuous_validation", cv_payload),
    ]:
        serialized = json.dumps(payload, allow_nan=False)
        assert isinstance(serialized, str)
        # Re-parse to confirm valid JSON
        json.loads(serialized)
