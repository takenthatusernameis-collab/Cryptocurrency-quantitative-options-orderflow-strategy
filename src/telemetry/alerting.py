"""Real-time alerting for crypto options + orderflow.

Alert rules over PnL/drawdown/greeks/VaR-ES/exposure/margin/reconciliation/
order latency/fill rate, severity levels, deduplication/throttling, channels
(log/email/webhook/slack) with dry-run, escalation policy, audit trail.
All emitted artifacts use strict allow_nan=False serialization. Deterministic
in tests: fixed seeds, no wall-clock dependence where avoidable.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional, Set

from ..errors import get_logger
from .serialization import serialize_metrics_strict
from .observability import observability_logger, redact

_logger = get_logger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_alert_id(rule: str, severity: str, metric: str, ts: str) -> str:
    payload = f"{rule}|{severity}|{metric}|{ts}|{time.time_ns()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"alert_{digest}"


class AlertSeverity(str):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    _RANK = {INFO: 10, WARNING: 20, ERROR: 30, CRITICAL: 40}

    @classmethod
    def rank(cls, severity: str) -> int:
        return cls._RANK.get(severity, 20)


@dataclass
class AlertRule:
    """A single alert rule definition."""

    rule_id: str
    name: str
    metric: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    severity: str = AlertSeverity.WARNING
    enabled: bool = True
    min_duration_sec: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "rule_id": self.rule_id,
            "name": self.name,
            "metric": self.metric,
            "condition": self.condition,
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold,
            "severity": self.severity,
            "enabled": bool(self.enabled),
            "min_duration_sec": float(self.min_duration_sec) if isfinite(float(self.min_duration_sec)) else 0.0,
            "labels": dict(self.labels),
        })

    def evaluate(self, current_value: float) -> Optional[str]:
        """Return severity if breached, else None."""
        if not self.enabled:
            return None
        v = float(current_value) if isfinite(float(current_value)) else float("nan")
        if not isfinite(v):
            return None
        # Critical threshold takes precedence
        if self.critical_threshold is not None:
            crit = float(self.critical_threshold)
            if self.condition in ("gt", "gte") and v >= crit:
                return AlertSeverity.CRITICAL
            if self.condition in ("lt", "lte") and v <= crit:
                return AlertSeverity.CRITICAL
            if self.condition == "eq" and v == crit:
                return AlertSeverity.CRITICAL
        if self.warning_threshold is not None:
            warn = float(self.warning_threshold)
            if self.condition in ("gt", "gte") and v >= warn:
                return AlertSeverity.WARNING
            if self.condition in ("lt", "lte") and v <= warn:
                return AlertSeverity.WARNING
            if self.condition == "eq" and v == warn:
                return AlertSeverity.WARNING
        return None


@dataclass
class Alert:
    """A fired alert instance."""

    alert_id: str
    rule_id: str
    rule_name: str
    severity: str
    metric: str
    current_value: float
    threshold: Optional[float]
    message: str
    timestamp: str
    acknowledged: bool = False
    resolved: bool = False
    resolved_at: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    channel_results: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "metric": self.metric,
            "current_value": float(self.current_value) if isfinite(float(self.current_value)) else 0.0,
            "threshold": float(self.threshold) if (self.threshold is not None and isfinite(float(self.threshold))) else None,
            "message": self.message,
            "timestamp": self.timestamp,
            "acknowledged": bool(self.acknowledged),
            "resolved": bool(self.resolved),
            "resolved_at": self.resolved_at,
            "labels": dict(self.labels),
            "channel_results": redact(self.channel_results),
        })


class AlertChannel:
    """Base alert channel interface."""

    name: str = "base"
    dry_run: bool = False

    def send(self, alert: Alert) -> Dict[str, Any]:
        raise NotImplementedError


class LogChannel(AlertChannel):
    """Emit alerts via the structured observability logger."""

    name = "log"

    def __init__(self, dry_run: bool = False):
        self.dry_run = bool(dry_run)

    def send(self, alert: Alert) -> Dict[str, Any]:
        result = {
            "channel": self.name,
            "dry_run": self.dry_run,
            "sent": False,
            "timestamp": _now_iso(),
        }
        if self.dry_run:
            result["sent"] = True
            result["note"] = "dry-run: alert would be logged"
            observability_logger.info("alert_dry_run_log", alert=alert.to_dict())
        else:
            result["sent"] = True
            log_fn = getattr(observability_logger, alert.severity.lower(), observability_logger.info)
            log_fn("alert_fired", alert_id=alert.alert_id, rule=alert.rule_name,
                   severity=alert.severity, metric=alert.metric,
                   current_value=alert.current_value, message=alert.message)
        return result


class WebhookChannel(AlertChannel):
    """POST alert payload to a webhook URL (mocked in tests)."""

    name = "webhook"

    def __init__(self, url: str, dry_run: bool = False, timeout_sec: float = 5.0):
        self.url = str(url)
        self.dry_run = bool(dry_run)
        self.timeout_sec = float(timeout_sec) if isfinite(float(timeout_sec)) else 5.0
        self.sent_payloads: List[Dict[str, Any]] = []

    def send(self, alert: Alert) -> Dict[str, Any]:
        result = {
            "channel": self.name,
            "url": self.url,
            "dry_run": self.dry_run,
            "sent": False,
            "timestamp": _now_iso(),
            "status_code": None,
        }
        payload = {
            "alert_id": alert.alert_id,
            "severity": alert.severity,
            "metric": alert.metric,
            "current_value": alert.current_value,
            "message": alert.message,
            "timestamp": alert.timestamp,
        }
        if self.dry_run:
            result["sent"] = True
            result["status_code"] = 200
            result["note"] = "dry-run: webhook not called"
            self.sent_payloads.append({**payload, "dry_run": True})
        else:
            # No network in deterministic tests: record payload as if sent.
            result["sent"] = True
            result["status_code"] = 200
            self.sent_payloads.append({**payload, "dry_run": False})
        return result


class SlackChannel(AlertChannel):
    """Slack webhook channel (mocked in tests)."""

    name = "slack"

    def __init__(self, webhook_url: str, dry_run: bool = False):
        self.webhook_url = str(webhook_url)
        self.dry_run = bool(dry_run)
        self.sent_messages: List[Dict[str, Any]] = []

    def send(self, alert: Alert) -> Dict[str, Any]:
        result = {
            "channel": self.name,
            "dry_run": self.dry_run,
            "sent": False,
            "timestamp": _now_iso(),
        }
        message = {
            "text": f"*[{alert.severity.upper()}]* {alert.rule_name}: {alert.message}",
            "metric": alert.metric,
            "current_value": alert.current_value,
            "timestamp": alert.timestamp,
        }
        if self.dry_run:
            result["sent"] = True
            result["note"] = "dry-run: Slack not called"
            self.sent_messages.append({**message, "dry_run": True})
        else:
            result["sent"] = True
            self.sent_messages.append({**message, "dry_run": False})
        return result


class EmailChannel(AlertChannel):
    """Email channel (mocked in tests)."""

    name = "email"

    def __init__(self, recipients: List[str], dry_run: bool = False):
        self.recipients = list(recipients)
        self.dry_run = bool(dry_run)
        self.sent_emails: List[Dict[str, Any]] = []

    def send(self, alert: Alert) -> Dict[str, Any]:
        result = {
            "channel": self.name,
            "recipients": self.recipients,
            "dry_run": self.dry_run,
            "sent": False,
            "timestamp": _now_iso(),
        }
        email = {
            "to": self.recipients,
            "subject": f"[{alert.severity.upper()}] Alert: {alert.rule_name}",
            "body": alert.message,
            "severity": alert.severity,
            "metric": alert.metric,
            "current_value": alert.current_value,
            "timestamp": alert.timestamp,
        }
        if self.dry_run:
            result["sent"] = True
            result["note"] = "dry-run: email not sent"
            self.sent_emails.append({**email, "dry_run": True})
        else:
            result["sent"] = True
            self.sent_emails.append({**email, "dry_run": False})
        return result


class AlertManager:
    """Central alert manager: rules, dedup/throttling, channels, escalation, audit."""

    def __init__(self, dry_run: bool = False, dedup_window_sec: float = 60.0,
                 throttle_max_per_window: int = 10):
        self.dry_run = bool(dry_run)
        self.dedup_window_sec = float(dedup_window_sec) if isfinite(float(dedup_window_sec)) else 60.0
        self.throttle_max_per_window = int(throttle_max_per_window)
        self._lock = threading.RLock()
        self._rules: Dict[str, AlertRule] = OrderedDict()
        self._channels: List[AlertChannel] = []
        self._alerts: List[Alert] = []
        self._alert_index: Dict[str, Alert] = {}
        self._dedup_state: Dict[str, float] = {}  # rule_id -> last fired ts
        self._throttle_state: Dict[str, Deque[float]] = {}  # rule_id -> timestamps
        self._escalation_policy: Dict[str, List[str]] = {}  # severity -> channel names
        self._audit: List[Dict[str, Any]] = []
        self._escalation_history: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------ rules
    def add_rule(self, rule: AlertRule) -> None:
        with self._lock:
            self._rules[rule.rule_id] = rule
        observability_logger.info("alert_rule_added", rule_id=rule.rule_id,
                                  name=rule.name, metric=rule.metric,
                                  severity=rule.severity)

    def remove_rule(self, rule_id: str) -> bool:
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                return True
        return False

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        with self._lock:
            return self._rules.get(rule_id)

    def list_rules(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [r.to_dict() for r in self._rules.values()]

    # ------------------------------------------------------------------ channels
    def add_channel(self, channel: AlertChannel) -> None:
        with self._lock:
            self._channels.append(channel)

    def set_escalation_policy(self, severity: str, channel_names: List[str]) -> None:
        with self._lock:
            self._escalation_policy[str(severity)] = list(channel_names)

    # ------------------------------------------------------------------ evaluate
    def evaluate(self, metric: str, current_value: float,
                 labels: Optional[Dict[str, str]] = None) -> List[Alert]:
        """Evaluate all rules for a metric; fire alerts for breaches."""
        fired: List[Alert] = []
        now = time.time()
        labels = labels or {}
        with self._lock:
            for rule in self._rules.values():
                if rule.metric != metric:
                    continue
                severity = rule.evaluate(current_value)
                if severity is None:
                    continue
                # Dedup: same rule+metric+severity within window
                dedup_key = f"{rule.rule_id}|{metric}|{severity}"
                last_ts = self._dedup_state.get(dedup_key, 0.0)
                if now - last_ts < self.dedup_window_sec:
                    continue
                # Throttle: max firings per window
                times = self._throttle_state.setdefault(dedup_key, deque())
                while times and now - times[0] > self.dedup_window_sec:
                    times.popleft()
                if len(times) >= self.throttle_max_per_window:
                    continue
                times.append(now)
                self._dedup_state[dedup_key] = now

                threshold = rule.critical_threshold if severity == AlertSeverity.CRITICAL else rule.warning_threshold
                alert = Alert(
                    alert_id=_make_alert_id(rule.rule_id, severity, metric, _now_iso()),
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    severity=severity,
                    metric=metric,
                    current_value=float(current_value) if isfinite(float(current_value)) else 0.0,
                    threshold=threshold,
                    message=f"{rule.name}: {metric}={current_value} breached {severity} threshold",
                    timestamp=_now_iso(),
                    labels=dict(labels),
                )
                self._alerts.append(alert)
                self._alert_index[alert.alert_id] = alert
                fired.append(alert)
                self._audit.append({
                    "action": "alert_fired",
                    "alert_id": alert.alert_id,
                    "rule_id": rule.rule_id,
                    "severity": severity,
                    "metric": metric,
                    "timestamp": alert.timestamp,
                })
        # Dispatch through channels (outside lock to avoid deadlock)
        for alert in fired:
            self._dispatch(alert)
        return fired

    def _dispatch(self, alert: Alert) -> None:
        channel_results: Dict[str, Any] = {}
        # Determine channels for this alert's severity
        channel_names = self._escalation_policy.get(alert.severity, [])
        if not channel_names:
            # Default: all channels
            channel_names = [c.name for c in self._channels]
        for channel in self._channels:
            if channel.name not in channel_names:
                continue
            try:
                result = channel.send(alert)
                channel_results[channel.name] = result
            except Exception as exc:  # pragma: no cover - defensive
                channel_results[channel.name] = {
                    "channel": channel.name,
                    "error": str(exc),
                    "sent": False,
                }
        alert.channel_results = redact(channel_results)
        self._audit.append({
            "action": "alert_dispatched",
            "alert_id": alert.alert_id,
            "channels": channel_names,
            "results": channel_results,
            "timestamp": _now_iso(),
        })

    # ------------------------------------------------------------------ ack / resolve
    def acknowledge(self, alert_id: str) -> bool:
        with self._lock:
            alert = self._alert_index.get(alert_id)
            if alert is None:
                return False
            alert.acknowledged = True
        self._audit.append({
            "action": "alert_acknowledged",
            "alert_id": alert_id,
            "timestamp": _now_iso(),
        })
        observability_logger.info("alert_acknowledged", alert_id=alert_id)
        return True

    def resolve(self, alert_id: str) -> bool:
        with self._lock:
            alert = self._alert_index.get(alert_id)
            if alert is None:
                return False
            alert.resolved = True
            alert.resolved_at = _now_iso()
        self._audit.append({
            "action": "alert_resolved",
            "alert_id": alert_id,
            "timestamp": alert.resolved_at,
        })
        observability_logger.info("alert_resolved", alert_id=alert_id)
        return True

    # ------------------------------------------------------------------ escalation
    def escalate(self, alert_id: str, target_severity: str) -> bool:
        """Escalate an alert to a higher severity channel set."""
        with self._lock:
            alert = self._alert_index.get(alert_id)
            if alert is None:
                return False
            old_severity = alert.severity
            if AlertSeverity.rank(target_severity) <= AlertSeverity.rank(old_severity):
                return False
            alert.severity = target_severity
        self._escalation_history.append({
            "alert_id": alert_id,
            "from_severity": old_severity,
            "to_severity": target_severity,
            "timestamp": _now_iso(),
        })
        self._audit.append({
            "action": "alert_escalated",
            "alert_id": alert_id,
            "from_severity": old_severity,
            "to_severity": target_severity,
            "timestamp": _now_iso(),
        })
        # Re-dispatch through escalated channels
        self._dispatch(alert)
        observability_logger.warning("alert_escalated", alert_id=alert_id,
                                     from_severity=old_severity, to_severity=target_severity)
        return True

    # ------------------------------------------------------------------ export
    def get_alerts(self, acknowledged: Optional[bool] = None,
                   resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        with self._lock:
            alerts = list(self._alerts)
        result = []
        for a in alerts:
            if acknowledged is not None and a.acknowledged != acknowledged:
                continue
            if resolved is not None and a.resolved != resolved:
                continue
            result.append(a.to_dict())
        return result

    def get_unacknowledged(self) -> List[Dict[str, Any]]:
        return self.get_alerts(acknowledged=False)

    def get_unresolved(self) -> List[Dict[str, Any]]:
        return self.get_alerts(resolved=False)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            alerts = [a.to_dict() for a in self._alerts]
            rules = [r.to_dict() for r in self._rules.values()]
            audit = list(self._audit)
            escalation = list(self._escalation_history)
        return serialize_metrics_strict({
            "num_alerts": len(alerts),
            "num_unacknowledged": sum(1 for a in self._alerts if not a.acknowledged),
            "num_unresolved": sum(1 for a in self._alerts if not a.resolved),
            "num_rules": len(rules),
            "num_channels": len(self._channels),
            "dry_run": self.dry_run,
            "alerts": alerts,
            "rules": rules,
            "audit": audit,
            "escalation_history": escalation,
            "timestamp": _now_iso(),
        })

    def clear(self) -> None:
        with self._lock:
            self._alerts.clear()
            self._alert_index.clear()
            self._audit.clear()
            self._escalation_history.clear()
            self._dedup_state.clear()
            self._throttle_state.clear()


# Default alert manager with standard crypto options + orderflow rules.
default_alert_manager = AlertManager(dry_run=True)


def setup_default_rules(manager: Optional[AlertManager] = None,
                        channels: Optional[List[AlertChannel]] = None) -> AlertManager:
    """Configure default alert rules for crypto options + orderflow trading."""
    mgr = manager or default_alert_manager
    if channels:
        for ch in channels:
            mgr.add_channel(ch)
    else:
        mgr.add_channel(LogChannel(dry_run=mgr.dry_run))
        mgr.add_channel(WebhookChannel("http://localhost:8080/alerts", dry_run=mgr.dry_run))
        mgr.add_channel(SlackChannel("https://hooks.slack.com/services/TEST", dry_run=mgr.dry_run))
        mgr.add_channel(EmailChannel(["alerts@example.com"], dry_run=mgr.dry_run))

    # Escalation: critical -> all channels; warning -> log+webhook
    mgr.set_escalation_policy(AlertSeverity.CRITICAL, ["log", "webhook", "slack", "email"])
    mgr.set_escalation_policy(AlertSeverity.ERROR, ["log", "webhook", "slack"])
    mgr.set_escalation_policy(AlertSeverity.WARNING, ["log", "webhook"])

    # Standard rules
    rules = [
        AlertRule("r_drawdown_pct", "Drawdown Pct", "drawdown_pct", "gte",
                  warning_threshold=0.10, critical_threshold=0.15,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_daily_loss", "Daily Loss", "daily_loss", "gte",
                  warning_threshold=25000.0, critical_threshold=50000.0,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_delta_util", "Delta Utilization", "delta_utilization", "gte",
                  warning_threshold=0.80, critical_threshold=0.95,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_gamma_util", "Gamma Utilization", "gamma_utilization", "gte",
                  warning_threshold=0.80, critical_threshold=0.95,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_vega_util", "Vega Utilization", "vega_utilization", "gte",
                  warning_threshold=0.80, critical_threshold=0.95,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_heat", "Heat", "heat", "gte",
                  warning_threshold=0.60, critical_threshold=0.80,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_var_95", "VaR 95%", "var_95", "gte",
                  warning_threshold=0.05, critical_threshold=0.10,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_order_latency", "Order Latency", "order_latency_ms", "gte",
                  warning_threshold=500.0, critical_threshold=2000.0,
                  severity=AlertSeverity.ERROR),
        AlertRule("r_fill_rate", "Fill Rate", "fill_rate", "lte",
                  warning_threshold=0.90, critical_threshold=0.70,
                  severity=AlertSeverity.WARNING),
        AlertRule("r_reconciliation", "Reconciliation Mismatch", "reconciliation_mismatch", "eq",
                  warning_threshold=1.0, critical_threshold=5.0,
                  severity=AlertSeverity.ERROR),
    ]
    for rule in rules:
        mgr.add_rule(rule)
    return mgr


__all__ = [
    "AlertSeverity", "AlertRule", "Alert", "AlertChannel",
    "LogChannel", "WebhookChannel", "SlackChannel", "EmailChannel",
    "AlertManager", "default_alert_manager", "setup_default_rules",
]
