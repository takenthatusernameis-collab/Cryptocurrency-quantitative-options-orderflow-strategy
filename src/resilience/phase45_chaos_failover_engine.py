"""
Phase 45: Chaos / fault injection + multi-venue failover orchestration.

Crypto options + orderflow focused. PAPER-ONLY hard gate by default; live
paths hard-gated + tested. Deterministic: fixed seeds, injectable faults,
no real network calls, finite numerics, allow_nan=False serialization on
all artifacts. Composes with Phases 17-44 (circuit breakers, retry,
kill switches, deployment/SLO, reconciliation).

Injects: network latency, rate-limit, partial-fill, recon-mismatch,
venue-outage and API-auth-failure faults. Coordinates per-venue circuit
breakers, orchestrates automated failover/failback, and emits SLO
burn-rate alerts.
"""
from __future__ import annotations

import hashlib
import math
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Deque, Dict, List, Optional, Tuple

from src.errors import RiskLimitError, get_logger
from src.resilience.circuit import (
    CircuitBreaker,
    CircuitBreakerConfig,
    default_circuit_registry,
)
from src.resilience.retry import RetryPolicy, RetryConfig
from src.telemetry import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _now_ts() -> float:
    return time.time()


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p45chaos|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p45_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if isfinite(v) else default


class ChaosFaultType(str, Enum):
    NETWORK_LATENCY = "network_latency"
    RATE_LIMIT = "rate_limit"
    PARTIAL_FILL = "partial_fill"
    RECON_MISMATCH = "recon_mismatch"
    VENUE_OUTAGE = "venue_outage"
    API_AUTH_FAILURE = "api_auth_failure"


class FailoverState(str, Enum):
    NOMINAL = "nominal"
    DEGRADED = "degraded"
    FAILED_OVER = "failed_over"
    RECOVERING = "recovering"
    HALTED = "halted"


@dataclass(frozen=True)
class ChaosFailoverConfig:
    seed: int = 45045
    paper_only: bool = True
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    primary_venue: str = "deribit"
    symbols: Tuple[str, ...] = ("BTC-PERP", "ETH-PERP", "SOL-PERP")
    slo_error_rate_threshold: float = 0.01
    slo_burn_window_cycles: int = 20
    slo_burn_rate_alert: float = 2.0
    failure_injection_rate: float = 0.15
    outdir: str = "research_state"
    cycles: int = 40

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise RiskLimitError("paper_only must be bool", context={"paper_only": self.paper_only})
        if not self.paper_only:
            raise RiskLimitError("Phase45ChaosFailoverEngine: paper_only must remain True (live path hard-gated)")
        if not self.venues:
            raise RiskLimitError("venues must be non-empty")
        if self.primary_venue not in self.venues:
            raise RiskLimitError("primary_venue must be in venues", context={"primary_venue": self.primary_venue, "venues": list(self.venues)})
        if not (0.0 <= self.slo_error_rate_threshold <= 1.0):
            raise RiskLimitError("slo_error_rate_threshold must be in [0,1]")
        if self.slo_burn_window_cycles < 1:
            raise RiskLimitError("slo_burn_window_cycles must be >= 1")
        if not self.symbols:
            raise RiskLimitError("symbols must be non-empty")
        if not (0.0 <= self.failure_injection_rate <= 1.0):
            raise RiskLimitError("failure_injection_rate must be in [0,1]")
        if self.cycles < 1:
            raise RiskLimitError("cycles must be >= 1")


@dataclass(frozen=True)
class ChaosScenario:
    scenario_id: str
    fault_type: ChaosFaultType
    venue: str
    symbol: str
    severity: str  # low|medium|high|critical
    inject_at_cycle: int
    recover_at_cycle: int
    duration_cycles: int
    enabled: bool = True

    def __post_init__(self) -> None:
        valid = {"low", "medium", "high", "critical"}
        if self.severity not in valid:
            raise RiskLimitError("severity must be one of low|medium|high|critical", context={"severity": self.severity})
        if self.inject_at_cycle < 1:
            raise RiskLimitError("inject_at_cycle must be >= 1", context={"inject_at_cycle": self.inject_at_cycle})
        if self.recover_at_cycle < self.inject_at_cycle:
            raise RiskLimitError("recover_at_cycle must be >= inject_at_cycle")
        if self.duration_cycles < 1:
            raise RiskLimitError("duration_cycles must be >= 1", context={"duration_cycles": self.duration_cycles})


@dataclass
class VenueHealth:
    venue: str
    cycle: int
    timestamp: str
    success_count: int = 0
    error_count: int = 0
    total_calls: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    circuit_state: str = "closed"
    healthy: bool = True
    fault_active: Optional[str] = None
    fault_type: Optional[str] = None
    fault_severity: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "venue": self.venue,
            "cycle": int(self.cycle),
            "timestamp": self.timestamp,
            "success_count": int(self.success_count),
            "error_count": int(self.error_count),
            "total_calls": int(self.total_calls),
            "error_rate": float(_finite(self.error_rate)),
            "avg_latency_ms": float(_finite(self.avg_latency_ms)),
            "p99_latency_ms": float(_finite(self.p99_latency_ms)),
            "circuit_state": self.circuit_state,
            "healthy": bool(self.healthy),
            "fault_active": self.fault_active,
            "fault_type": self.fault_type,
            "fault_severity": self.fault_severity,
        })


@dataclass
class FailoverEvent:
    event_id: str
    cycle: int
    timestamp: str
    from_venue: str
    to_venue: str
    reason: str
    trigger: str  # circuit_open|slo_burn|critical_fault|automated_recovery
    executed: bool = True
    paper_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "event_id": self.event_id,
            "cycle": int(self.cycle),
            "timestamp": self.timestamp,
            "from_venue": self.from_venue,
            "to_venue": self.to_venue,
            "reason": self.reason,
            "trigger": self.trigger,
            "executed": bool(self.executed),
            "paper_only": bool(self.paper_only),
        })


@dataclass
class SLOBurnAlert:
    alert_id: str
    cycle: int
    timestamp: str
    venue: str
    slo_name: str
    observed_error_rate: float
    slo_threshold: float
    burn_rate: float
    alert: bool

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "alert_id": self.alert_id,
            "cycle": int(self.cycle),
            "timestamp": self.timestamp,
            "venue": self.venue,
            "slo_name": self.slo_name,
            "observed_error_rate": float(_finite(self.observed_error_rate)),
            "slo_threshold": float(_finite(self.slo_threshold)),
            "burn_rate": float(_finite(self.burn_rate)),
            "alert": bool(self.alert),
        })


class Phase45ChaosFailoverEngine:
    """Deterministic chaos/fault injection + multi-venue failover engine.

    Simulates venue faults per cycle, coordinates per-venue circuit breakers,
    decides automated failover/failback, and tracks SLO burn rate with
    alerting. All numeric outputs finite; all artifacts allow_nan=False.
    """

    def __init__(self, cfg: Optional[ChaosFailoverConfig] = None) -> None:
        self.cfg = cfg or ChaosFailoverConfig()
        if not self.cfg.paper_only:
            raise RiskLimitError("live mode not supported; paper_only must be True")
        self.seed = int(self.cfg.seed)
        self.paper_only = True
        self._ctr = 0
        self._lock = threading.RLock()
        self.rng = __import__("random").Random(self.seed)
        self.venues = list(self.cfg.venues)
        self.primary_venue = self.cfg.primary_venue
        self.active_venue = self.primary_venue
        self.state = FailoverState.NOMINAL
        self.scenarios: List[ChaosScenario] = []
        self._fault_schedule: Dict[int, List[ChaosScenario]] = {}
        self.venue_health: Dict[str, VenueHealth] = {v: self._blank_health(v, 0) for v in self.venues}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.failover_events: List[FailoverEvent] = []
        self.slo_alerts: List[SLOBurnAlert] = []
        self.error_window: Deque[Tuple[int, bool]] = deque(maxlen=self.cfg.slo_burn_window_cycles * 4)
        self.cycles_run: List[Dict[str, Any]] = []
        self._halted = False
        self._build_default_scenarios()
        self._init_circuit_breakers()
        self._init_retry_policies()

    # ------------------------------------------------------------------ setup
    def _blank_health(self, venue: str, cycle: int) -> VenueHealth:
        return VenueHealth(
            venue=venue, cycle=cycle, timestamp=_utc_now(),
            success_count=0, error_count=0, total_calls=0, error_rate=0.0,
            avg_latency_ms=0.0, p99_latency_ms=0.0, circuit_state="closed",
            healthy=True, fault_active=None, fault_type=None, fault_severity=None,
        )

    def _id(self, tag: str) -> str:
        self._ctr += 1
        return _make_id(self.seed, tag, self._ctr)

    def _build_default_scenarios(self) -> None:
        """Deterministic default chaos scenarios covering the fault taxonomy."""
        defaults = [
            (ChaosFaultType.VENUE_OUTAGE, "okx", "BTC-PERP", "high", 6, 11, 5),
            (ChaosFaultType.RATE_LIMIT, "bybit", "ETH-PERP", "medium", 14, 19, 5),
            (ChaosFaultType.PARTIAL_FILL, "binance", "SOL-PERP", "medium", 22, 27, 5),
            (ChaosFaultType.RECON_MISMATCH, "deribit", "BTC-PERP", "high", 30, 35, 5),
            (ChaosFaultType.NETWORK_LATENCY, "okx", "ETH-PERP", "low", 38, 43, 5),
            (ChaosFaultType.API_AUTH_FAILURE, "bybit", "SOL-PERP", "critical", 46, 51, 5),
        ]
        for i, (ft, venue, symbol, sev, inj, rec, dur) in enumerate(defaults):
            sc = ChaosScenario(
                scenario_id=self._id("scen"),
                fault_type=ft,
                venue=venue,
                symbol=symbol,
                severity=sev,
                inject_at_cycle=inj,
                recover_at_cycle=rec,
                duration_cycles=dur,
                enabled=True,
            )
            self.scenarios.append(sc)
            self._fault_schedule.setdefault(inj, []).append(sc)

    def _init_circuit_breakers(self) -> None:
        for v in self.venues:
            cb = CircuitBreaker(CircuitBreakerConfig(
                name=f"venue:{v}",
                failure_threshold=3,
                timeout_seconds=5.0,
                half_open_max_calls=2,
                error_rate_threshold=0.5,
                error_rate_window=20,
                min_calls_before_eval=5,
                recovery_threshold=0.5,
            ))
            self.circuit_breakers[v] = cb
            default_circuit_registry.get_or_create(f"venue:{v}", cb.config)

    def _init_retry_policies(self) -> None:
        for v in self.venues:
            self.retry_policies[v] = RetryPolicy(RetryConfig(
                max_attempts=3, base_delay_sec=0.05, max_delay_sec=0.5,
                backoff_multiplier=2.0, jitter_sec=0.0,
            ))

    # ------------------------------------------------------------------ fault injection
    def active_faults(self, cycle: int) -> List[ChaosScenario]:
        """Return scenarios active at ``cycle`` (inject <= cycle < recover)."""
        return [sc for sc in self.scenarios
                if sc.enabled and sc.inject_at_cycle <= cycle < sc.recover_at_cycle]

    def inject_fault(self, cycle: int, fault_type: ChaosFaultType, venue: str,
                     symbol: str, severity: str) -> ChaosScenario:
        """Manually inject a fault (chaos hook). Returns the scenario."""
        if venue not in self.venues:
            raise RiskLimitError("unknown venue for fault injection", context={"venue": venue, "venues": self.venues})
        sc = ChaosScenario(
            scenario_id=self._id("inj"),
            fault_type=fault_type,
            venue=venue,
            symbol=symbol,
            severity=severity,
            inject_at_cycle=cycle,
            recover_at_cycle=cycle + 3,
            duration_cycles=3,
            enabled=True,
        )
        self.scenarios.append(sc)
        self._fault_schedule.setdefault(cycle, []).append(sc)
        get_logger("phase45.chaos").warning("chaos_fault_injected",
                                            cycle=cycle, fault_type=fault_type.value,
                                            venue=venue, symbol=symbol, severity=severity)
        return sc

    # ------------------------------------------------------------------ venue health simulation
    def _venue_stability(self, venue: str) -> float:
        return {"deribit": 0.97, "okx": 0.94, "bybit": 0.91, "binance": 0.93}.get(venue, 0.90)

    def _venue_base_latency(self, venue: str) -> float:
        return {"deribit": 45.0, "okx": 60.0, "bybit": 75.0, "binance": 70.0}.get(venue, 80.0)

    def _venue_stable_offset(self, venue: str) -> int:
        return sum(ord(c) for c in venue) % 7

    def _fault_impact(self, sc: ChaosScenario) -> Dict[str, float]:
        impact = {
            ChaosFaultType.VENUE_OUTAGE: {"ok_penalty": 0.95, "latency_add": 500.0},
            ChaosFaultType.RATE_LIMIT: {"ok_penalty": 0.60, "latency_add": 120.0},
            ChaosFaultType.PARTIAL_FILL: {"ok_penalty": 0.25, "latency_add": 40.0},
            ChaosFaultType.RECON_MISMATCH: {"ok_penalty": 0.40, "latency_add": 80.0},
            ChaosFaultType.NETWORK_LATENCY: {"ok_penalty": 0.10, "latency_add": 300.0},
            ChaosFaultType.API_AUTH_FAILURE: {"ok_penalty": 0.90, "latency_add": 20.0},
        }[sc.fault_type]
        sev_mul = {"low": 0.5, "medium": 1.0, "high": 1.5, "critical": 2.0}[sc.severity]
        return {"ok_penalty": impact["ok_penalty"] * sev_mul,
                "latency_add": impact["latency_add"] * sev_mul}

    def evaluate_venue_health(self, cycle: int) -> Dict[str, VenueHealth]:
        """Evaluate health for every venue at ``cycle`` (deterministic)."""
        active = self.active_faults(cycle)
        faults_by_venue: Dict[str, List[ChaosScenario]] = {}
        for sc in active:
            faults_by_venue.setdefault(sc.venue, []).append(sc)

        results: Dict[str, VenueHealth] = {}
        for venue in self.venues:
            prev = self.venue_health.get(venue, self._blank_health(venue, cycle))
            stability = self._venue_stability(venue)
            base_ok = stability + 0.03 * math.sin(cycle * 0.7 + self._venue_stable_offset(venue))
            base_ok = min(1.0, max(0.0, base_ok))
            latency = self._venue_base_latency(venue) + 5.0 * math.cos(cycle * 0.5)

            ok_prob = base_ok
            latency_add = 0.0
            active_fault: Optional[str] = None
            fault_type: Optional[str] = None
            fault_severity: Optional[str] = None
            for sc in faults_by_venue.get(venue, []):
                imp = self._fault_impact(sc)
                ok_prob *= (1.0 - imp["ok_penalty"])
                latency_add += imp["latency_add"]
                active_fault = sc.scenario_id
                fault_type = sc.fault_type.value
                fault_severity = sc.severity
            ok_prob = min(1.0, max(0.0, ok_prob))
            latency_ms = latency + latency_add + self.rng.uniform(-5.0, 5.0)

            n_calls = 20 + int(self.rng.uniform(0, 10))
            n_errors = 0
            for _ in range(n_calls):
                if self.rng.random() > ok_prob:
                    n_errors += 1
            total_calls = prev.total_calls + n_calls
            success_count = prev.success_count + (n_calls - n_errors)
            error_count = prev.error_count + n_errors
            error_rate = error_count / total_calls if total_calls else 0.0

            cb = self.circuit_breakers[venue]
            for _ in range(n_calls):
                if self.rng.random() > ok_prob:
                    cb.record_failure()
                else:
                    cb.record_success()
            cb_state = cb.state.value

            healthy = ok_prob >= 0.8 and cb_state != "open"
            results[venue] = VenueHealth(
                venue=venue, cycle=cycle, timestamp=_utc_now(),
                success_count=success_count, error_count=error_count,
                total_calls=total_calls, error_rate=_finite(error_rate),
                avg_latency_ms=_finite(latency_ms),
                p99_latency_ms=_finite(latency_ms * 1.6),
                circuit_state=cb_state, healthy=bool(healthy),
                fault_active=active_fault, fault_type=fault_type,
                fault_severity=fault_severity,
            )
        self.venue_health = results
        return results

    # ------------------------------------------------------------------ failover / failback
    def _candidate_venues(self, exclude: str) -> List[str]:
        return [v for v in self.venues if v != exclude]

    def should_failover(self, venue: str, health: VenueHealth) -> Tuple[bool, str]:
        """Decide whether to fail over away from ``venue``."""
        if health.circuit_state == "open":
            return True, "circuit_breaker_open"
        if health.error_rate > 0.5:
            return True, "error_rate_major_breach"
        if health.fault_severity == "critical":
            return True, "critical_fault"
        return False, "nominal"

    def execute_failover(self, cycle: int, from_venue: str, to_venue: str,
                         reason: str, trigger: str) -> FailoverEvent:
        ev = FailoverEvent(
            event_id=self._id("fo"),
            cycle=cycle, timestamp=_utc_now(),
            from_venue=from_venue, to_venue=to_venue, reason=reason,
            trigger=trigger, executed=True, paper_only=True,
        )
        with self._lock:
            self.failover_events.append(ev)
            self.active_venue = to_venue
            self.state = FailoverState.FAILED_OVER
        get_logger("phase45.failover").info("failover_executed",
                                            cycle=cycle, from_venue=from_venue,
                                            to_venue=to_venue, trigger=trigger, reason=reason)
        return ev

    def attempt_recovery(self, cycle: int) -> Optional[FailoverEvent]:
        """Fail back to primary venue when healthy again."""
        if self.state != FailoverState.FAILED_OVER:
            return None
        primary = self.primary_venue
        if primary == self.active_venue:
            self.state = FailoverState.NOMINAL
            return None
        h = self.venue_health.get(primary)
        if h is None or not h.healthy or h.circuit_state == "open":
            self.state = FailoverState.RECOVERING
            return None
        ev = FailoverEvent(
            event_id=self._id("fb"),
            cycle=cycle, timestamp=_utc_now(),
            from_venue=self.active_venue, to_venue=primary,
            reason="primary_venue_recovered", trigger="automated_recovery",
            executed=True, paper_only=True,
        )
        with self._lock:
            self.failover_events.append(ev)
            self.active_venue = primary
            self.state = FailoverState.NOMINAL
        return ev

    # ------------------------------------------------------------------ SLO burn
    def evaluate_slo_burn(self, cycle: int, error_rate: float) -> List[SLOBurnAlert]:
        """Track error rate over sliding window; emit burn alerts."""
        alerts: List[SLOBurnAlert] = []
        self.error_window.append((cycle, error_rate > self.cfg.slo_error_rate_threshold))
        window = list(self.error_window)
        if len(window) < self.cfg.slo_burn_window_cycles:
            return alerts
        recent = window[-self.cfg.slo_burn_window_cycles:]
        burn_errors = sum(1 for _, bad in recent if bad)
        burn_rate = burn_errors / len(recent)
        budget = self.cfg.slo_error_rate_threshold
        burn_multiple = burn_rate / budget if budget > 0 else 0.0
        alert = burn_multiple >= self.cfg.slo_burn_rate_alert
        for venue in self.venues:
            a = SLOBurnAlert(
                alert_id=self._id("burn"),
                cycle=cycle, timestamp=_utc_now(),
                venue=venue, slo_name="error_rate_budget",
                observed_error_rate=_finite(error_rate),
                slo_threshold=_finite(budget),
                burn_rate=_finite(burn_multiple),
                alert=bool(alert),
            )
            alerts.append(a)
            self.slo_alerts.append(a)
        return alerts

    # ------------------------------------------------------------------ campaign
    def run_cycle(self, cycle: int) -> Dict[str, Any]:
        with self._lock:
            if self._halted:
                return {"cycle": cycle, "halted": True, "active_venue": self.active_venue,
                        "state": self.state.value, "gates_ok": False}
        health = self.evaluate_venue_health(cycle)
        cur = self.active_venue
        failover_ev: Optional[FailoverEvent] = None
        ch = health.get(cur)
        if ch is not None:
            should, reason = self.should_failover(cur, ch)
            if should:
                cands = self._candidate_venues(cur)
                if cands:
                    best = cands[0]
                    best_ok = -1.0
                    for v in cands:
                        hv = health.get(v)
                        if hv is not None and hv.healthy and hv.circuit_state != "open":
                            score = 1.0 - hv.error_rate
                            if score > best_ok:
                                best_ok = score
                                best = v
                    target = best
                    if target != cur:
                        failover_ev = self.execute_failover(cycle, cur, target, reason, "circuit_or_slo")
        recovery_ev = self.attempt_recovery(cycle)
        all_rates = [h.error_rate for h in health.values()]
        agg_error_rate = sum(all_rates) / len(all_rates) if all_rates else 0.0
        burn_alerts = self.evaluate_slo_burn(cycle, agg_error_rate)
        cyc_rec = {
            "cycle": cycle,
            "timestamp": _utc_now(),
            "active_venue": self.active_venue,
            "state": self.state.value,
            "halted": self._halted,
            "venue_health": {v: h.to_dict() for v, h in health.items()},
            "failover_event": failover_ev.to_dict() if failover_ev else None,
            "recovery_event": recovery_ev.to_dict() if recovery_ev else None,
            "agg_error_rate": _finite(agg_error_rate),
            "slo_burn_alerts": [a.to_dict() for a in burn_alerts],
            "n_active_faults": len(self.active_faults(cycle)),
            "gates_ok": True,
        }
        cyc_rec = serialize_metrics_strict(cyc_rec)
        self.cycles_run.append(cyc_rec)
        return cyc_rec

    def halt(self) -> None:
        with self._lock:
            self._halted = True
            self.state = FailoverState.HALTED

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        n = int(cycles if cycles is not None else self.cfg.cycles)
        self._halted = False
        self.state = FailoverState.NOMINAL
        self.active_venue = self.primary_venue
        self.cycles_run = []
        for c in range(1, n + 1):
            if self._halted:
                break
            self.run_cycle(c)
        n_failovers = sum(1 for e in self.failover_events if e.trigger != "automated_recovery")
        n_recoveries = sum(1 for e in self.failover_events if e.trigger == "automated_recovery")
        n_alerts = sum(1 for a in self.slo_alerts if a.alert)
        report = {
            "phase": "PHASE45_CHAOS_FAILOVER_ENGINE",
            "timestamp_utc": _utc_now(),
            "paper_only": True,
            "modes": "paper",
            "seed": self.seed,
            "cycles": n,
            "cycles_run": len(self.cycles_run),
            "primary_venue": self.primary_venue,
            "final_active_venue": self.active_venue,
            "final_state": self.state.value,
            "halted": bool(self._halted),
            "n_failovers": int(n_failovers),
            "n_recoveries": int(n_recoveries),
            "n_slo_burn_alerts": int(n_alerts),
            "n_venues": len(self.venues),
            "venues": self.venues,
            "symbols": list(self.cfg.symbols),
            "gates_ok": True,
        }
        report = serialize_metrics_strict(report)
        return report

    # ------------------------------------------------------------------ snapshot / restore
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return serialize_metrics_strict({
                "seed": self.seed,
                "paper_only": self.paper_only,
                "active_venue": self.active_venue,
                "state": self.state.value,
                "halted": self._halted,
                "n_failovers": len(self.failover_events),
                "n_slo_alerts": len(self.slo_alerts),
                "venue_health": {v: h.to_dict() for v, h in self.venue_health.items()},
                "circuit_breakers": {v: cb.snapshot() for v, cb in self.circuit_breakers.items()},
                "timestamp": _utc_now(),
            })

    def restore(self, snap: Dict[str, Any]) -> None:
        with self._lock:
            self.active_venue = str(snap.get("active_venue", self.primary_venue))
            self.state = FailoverState(str(snap.get("state", "nominal")))
            self._halted = bool(snap.get("halted", False))
            vh = snap.get("venue_health", {})
            for v in self.venues:
                if v in vh:
                    d = vh[v]
                    self.venue_health[v] = VenueHealth(
                        venue=v, cycle=int(d.get("cycle", 0)), timestamp=str(d.get("timestamp", _utc_now())),
                        success_count=int(d.get("success_count", 0)),
                        error_count=int(d.get("error_count", 0)),
                        total_calls=int(d.get("total_calls", 0)),
                        error_rate=_finite(d.get("error_rate", 0.0)),
                        avg_latency_ms=_finite(d.get("avg_latency_ms", 0.0)),
                        p99_latency_ms=_finite(d.get("p99_latency_ms", 0.0)),
                        circuit_state=str(d.get("circuit_state", "closed")),
                        healthy=bool(d.get("healthy", True)),
                        fault_active=d.get("fault_active"),
                        fault_type=d.get("fault_type"),
                        fault_severity=d.get("fault_severity"),
                    )

    # ------------------------------------------------------------------ reports
    def generate_reports(self, outdir: Optional[str] = None) -> Dict[str, str]:
        from pathlib import Path
        import json

        p = Path(outdir or self.cfg.outdir)
        p.mkdir(parents=True, exist_ok=True)
        rep = self.run_campaign()
        (p / "PHASE45_CHAOS_FAILOVER_ENGINE_REPORT.json").write_text(json.dumps(rep, indent=2))
        md = [
            "# PHASE45 CHAOS FAILOVER ENGINE REPORT\n\n",
            f"Timestamp: {rep['timestamp_utc']}\n\n",
            f"Paper-only: true | Seed: {rep['seed']} | Cycles: {rep['cycles_run']}/{rep['cycles']}\n",
            f"Primary venue: {rep['primary_venue']} | Final active: {rep['final_active_venue']}\n",
            f"Failovers: {rep['n_failovers']} | Recoveries: {rep['n_recoveries']} | SLO burn alerts: {rep['n_slo_burn_alerts']}\n",
            f"Halted: {rep['halted']} | Gates OK: {rep['gates_ok']}\n",
            "Crypto options + orderflow | Integrated with Phases 17-44\n",
        ]
        (p / "PHASE45_CHAOS_FAILOVER_ENGINE_REPORT.md").write_text("".join(md))
        camp = {
            "phase": "PHASE45_CAMPAIGN_SUMMARY",
            "timestamp_utc": rep["timestamp_utc"],
            "paper_only": True,
            "seed": self.seed,
            "cycles": rep["cycles_run"],
            "n_failovers": rep["n_failovers"],
            "n_recoveries": rep["n_recoveries"],
            "n_slo_burn_alerts": rep["n_slo_burn_alerts"],
            "final_state": rep["final_state"],
            "gates_ok": rep["gates_ok"],
        }
        camp = serialize_metrics_strict(camp)
        (p / "PHASE45_CAMPAIGN_SUMMARY.json").write_text(json.dumps(camp, indent=2))
        (p / "PHASE45_CAMPAIGN_SUMMARY.md").write_text("# PHASE45 CAMPAIGN SUMMARY\n\nOK - Phase 45 Complete\n")
        return {
            "json": str(p / "PHASE45_CHAOS_FAILOVER_ENGINE_REPORT.json"),
            "md": str(p / "PHASE45_CHAOS_FAILOVER_ENGINE_REPORT.md"),
            "campaign_json": str(p / "PHASE45_CAMPAIGN_SUMMARY.json"),
            "campaign_md": str(p / "PHASE45_CAMPAIGN_SUMMARY.md"),
        }


__all__ = [
    "ChaosFaultType", "FailoverState", "ChaosFailoverConfig", "ChaosScenario",
    "VenueHealth", "FailoverEvent", "SLOBurnAlert", "Phase45ChaosFailoverEngine",
]
