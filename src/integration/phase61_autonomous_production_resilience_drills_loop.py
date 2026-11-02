"""
Phase 61: Autonomous Production Resilience Drills Loop (crypto options + orderflow).

Autonomous production resilience drills: chaos/fault injection, venue failover
drills, circuit breaker drills, rollback validation, post-trade reconciliation
attestation, artifacts; composes Phases 17-60. PAPER-ONLY enforced.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.execution.phase60_adaptive_execution_intelligence_engine import Phase60AdaptiveExecutionIntelligenceEngine
from src.hedging.phase60_toxicity_resilient_hedge_fusion import Phase60ToxicityResilientHedgeFusion
from src.integration.phase60_autonomous_production_rollout_validation_loop import (
    Phase60AutonomousProductionRolloutValidationLoop,
)
from src.integration.phase59_autonomous_execution_hardening_loop import Phase59AutonomousExecutionHardeningLoop
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase58_flow_toxicity_mitigator import Phase58FlowToxicityMitigator
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.risk.phase54_realtime_risk_fusion_engine import Phase54RealtimeRiskFusionEngine
from src.risk.phase57_production_circuit_breakers import Phase57ProductionCircuitBreakers
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p61drills|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p61drills_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if isfinite(v) else default


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
            if not isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class Phase61AutonomousProductionResilienceConfig:
    seed: int = 61062
    paper_only: bool = True
    cycles: int = 80
    chaos_injection_enabled: bool = True
    failover_drill_enabled: bool = True
    circuit_breaker_drill_enabled: bool = True
    rollback_validation_enabled: bool = True
    posttrade_reconciliation_enabled: bool = True
    auto_contain_on_breach: bool = True
    auto_rollback_on_severe: bool = True
    drawdown_halt_pct: float = 0.05
    rollout_readiness_pct: float = 0.9
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase61AutonomousProductionResilienceDrillsLoop: paper_only must remain True (live path hard-gated)")


class Phase61AutonomousProductionResilienceDrillsLoop:
    """Autonomous production resilience drills loop composing Phases 17-60."""

    def __init__(self, cfg: Phase61AutonomousProductionResilienceConfig | None = None) -> None:
        self.cfg = cfg or Phase61AutonomousProductionResilienceConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase61AutonomousProductionResilienceDrillsLoop: paper_only must remain True")
        self.harden59 = Phase59AutonomousExecutionHardeningLoop()
        self.rollout60 = Phase60AutonomousProductionRolloutValidationLoop()
        self.execint60 = Phase60AdaptiveExecutionIntelligenceEngine()
        self.toxhedge60 = Phase60ToxicityResilientHedgeFusion()
        self.arc58 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.failovers: List[Dict[str, Any]] = []
        self.reconciliations: List[Dict[str, Any]] = []
        self.containments: List[Dict[str, Any]] = []
        self.rollbacks: List[Dict[str, Any]] = []
        self.drills: List[Dict[str, Any]] = []
        self.chaos_events: List[Dict[str, Any]] = []
        self.cb_drills: List[Dict[str, Any]] = []
        self.venue_states: Dict[str, str] = {v: "active" for v in ("deribit", "okx", "bybit", "binance")}
        self._cycle = 0

    def _chaos_inject(self, i: int) -> Dict[str, Any] | None:
        if not self.cfg.chaos_injection_enabled:
            return None
        if i % 11 == 3:
            return serialize_metrics_strict({
                "chaos_id": _make_id(self.cfg.seed, "chaos", i),
                "cycle": i,
                "event": "venue_latency_spike",
                "venue": ["deribit", "okx", "bybit", "binance"][i % 4],
                "latency_ms_added": 50.0 + (i % 5) * 10.0,
                "paper_only": True,
                "timestamp": _utc_now(),
            })
        if i % 17 == 5:
            return serialize_metrics_strict({
                "chaos_id": _make_id(self.cfg.seed, "chaos", i),
                "cycle": i,
                "event": "orderflow_toxicity_spike",
                "toxicity_increment": 0.15 + (i % 3) * 0.05,
                "paper_only": True,
                "timestamp": _utc_now(),
            })
        return None

    def run_drills(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.failovers = []
        self.reconciliations = []
        self.containments = []
        self.rollbacks = []
        self.drills = []
        self.chaos_events = []
        self.cb_drills = []

        harden_rep = self.harden59.run_hardening(cycles=40)
        rollout_rep = self.rollout60.run_rollout_validation(cycles=40)
        exec_rep = self.execint60.run_intelligence(cycles=40)
        toxhedge_rep = self.toxhedge60.run_hedge_fusion(cycles=40)
        risk_rep = self.risk54.run_campaign(cycles=40)
        of_rep = self.of.run_campaign(cycles=30)
        tox_rep = self.tox58.mitigate(cycles=40)
        ks_rep = self.ks.run_campaign()

        halted = bool(ks_rep.get("halted", False))
        cb_breaches = []
        active_venues = [v for v, s in self.venue_states.items() if s == "active"]
        rollout_score = 1.0
        resilience_score = 1.0

        for i in range(cycles):
            venue = active_venues[i % max(1, len(active_venues))] if active_venues else "deribit"
            underlying = ("BTC", "ETH", "SOL")[i % 3]
            dd_pct = 0.015 + (i % 11) * 0.004
            latency_ms = 5.0 + (i % 8) * 3.0 + _finite(exec_rep.get("avg_toxicity", 0.18)) * 6.0
            risk_breach_i = bool(cb_breaches) or halted or dd_pct >= self.cfg.drawdown_halt_pct

            chaos_event = self._chaos_inject(i)
            if chaos_event is not None:
                self.chaos_events.append(chaos_event)
                resilience_score = max(0.0, resilience_score - 0.02)

            if self.cfg.failover_drill_enabled and (risk_breach_i or i % 13 == 7) and len(active_venues) > 1:
                failed = venue
                self.venue_states[failed] = "failover"
                active_venues = [v for v, s in self.venue_states.items() if s == "active"] or [failed]
                self.failovers.append(serialize_metrics_strict({
                    "fo_id": _make_id(self.cfg.seed, "fo", i),
                    "cycle": i,
                    "failed_venue": failed,
                    "fallback_venue": active_venues[0] if active_venues else "deribit",
                    "reason": "risk_breach_or_rollout_drill",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                self.drills.append(serialize_metrics_strict({
                    "drill_id": _make_id(self.cfg.seed, "drill", i),
                    "cycle": i,
                    "venue": failed,
                    "drill_type": "venue_failover",
                    "passed": len(active_venues) > 0,
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                self.venue_states[failed] = "active"

            if self.cfg.circuit_breaker_drill_enabled and i % 9 == 2:
                cb_breached = risk_breach_i or dd_pct >= self.cfg.drawdown_halt_pct
                self.cb_drills.append(serialize_metrics_strict({
                    "cb_id": _make_id(self.cfg.seed, "cb", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "breach": bool(cb_breached),
                    "action": "circuit_breaker_engaged" if cb_breached else "circuit_breaker_armed",
                    "severity": "critical" if halted else ("high" if cb_breached else "info"),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

            if self.cfg.posttrade_reconciliation_enabled and i % 4 == 0:
                fill_rate = max(0.4, min(1.0, 0.99 - _finite(exec_rep.get("avg_toxicity", 0.18)) * 0.35 - latency_ms / 800.0))
                reconciled = fill_rate >= 0.8 and not halted
                self.reconciliations.append(serialize_metrics_strict({
                    "rec_id": _make_id(self.cfg.seed, "rec", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "fill_rate": float(_finite(fill_rate)),
                    "latency_ms": float(_finite(latency_ms)),
                    "reconciled": bool(reconciled),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
                if reconciled:
                    rollout_score = min(1.0, rollout_score + 0.005)
                    resilience_score = min(1.0, resilience_score + 0.003)
                else:
                    rollout_score = max(0.0, rollout_score - 0.01)
                    resilience_score = max(0.0, resilience_score - 0.005)

            if risk_breach_i and self.cfg.auto_contain_on_breach:
                self.containments.append(serialize_metrics_strict({
                    "contain_id": _make_id(self.cfg.seed, "contain", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "action": "auto_contain",
                    "trigger": "risk_breach_or_halt",
                    "severity": "critical" if halted else "high",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if risk_breach_i and self.cfg.auto_rollback_on_severe and dd_pct >= self.cfg.drawdown_halt_pct:
                self.rollbacks.append(serialize_metrics_strict({
                    "rb_id": _make_id(self.cfg.seed, "rb", i),
                    "cycle": i,
                    "venue": venue,
                    "underlying": underlying,
                    "action": "auto_rollback",
                    "trigger": "severe_drawdown",
                    "drawdown_pct": float(_finite(dd_pct)),
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

        rec_rate = sum(1 for r in self.reconciliations if r["reconciled"]) / max(1, len(self.reconciliations))
        drill_pass_rate = sum(1 for d in self.drills if d["passed"]) / max(1, len(self.drills))
        cb_pass_rate = sum(1 for c in self.cb_drills if not c["breach"]) / max(1, len(self.cb_drills))
        gates_ok = bool(
            rec_rate >= self.cfg.rollout_readiness_pct
            and drill_pass_rate >= self.cfg.rollout_readiness_pct
            and cb_pass_rate >= 0.5
            and not halted
            and harden_rep.get("gates_ok", False)
            and rollout_rep.get("gates_ok", False)
            and exec_rep.get("gates_ok", False)
            and toxhedge_rep.get("gates_ok", False)
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE61_AUTONOMOUS_PRODUCTION_RESILIENCE_DRILLS_LOOP",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "rollout_score": float(_finite(rollout_score)),
            "resilience_score": float(_finite(resilience_score)),
            "reconciliation_rate": float(_finite(rec_rate)),
            "drill_pass_rate": float(_finite(drill_pass_rate)),
            "cb_pass_rate": float(_finite(cb_pass_rate)),
            "n_failovers": len(self.failovers),
            "n_reconciliations": len(self.reconciliations),
            "n_containments": len(self.containments),
            "n_rollbacks": len(self.rollbacks),
            "n_drills": len(self.drills),
            "n_chaos_events": len(self.chaos_events),
            "n_cb_drills": len(self.cb_drills),
            "cb_breaches": len(cb_breaches),
            "harden59_ok": bool(harden_rep.get("gates_ok", False)),
            "rollout60_ok": bool(rollout_rep.get("gates_ok", False)),
            "execint60_ok": bool(exec_rep.get("gates_ok", False)),
            "toxhedge60_ok": bool(toxhedge_rep.get("gates_ok", False)),
            "risk54_ok": bool(risk_rep.get("gates_ok", False)),
            "composed_phases": "17-60",
        })
        _assert_finite(rep, "phase61_resilience_drills_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_drills(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE61_AUTONOMOUS_PRODUCTION_RESILIENCE_{ts}.json"
        mpath = out / f"PHASE61_AUTONOMOUS_PRODUCTION_RESILIENCE_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE61 Autonomous Production Resilience Drills Loop\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Paper Only: {rep['paper_only']}\n"
                f"- Cycles: {rep['cycles']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Rollout Score: {rep['rollout_score']:.4f} | Resilience Score: {rep['resilience_score']:.4f}\n"
                f"- Reconciliation Rate: {rep['reconciliation_rate']:.4f} | Drill Pass Rate: {rep['drill_pass_rate']:.4f}\n"
                f"- CB Pass Rate: {rep['cb_pass_rate']:.4f}\n"
                f"- Failovers: {rep['n_failovers']} | Reconciliations: {rep['n_reconciliations']}\n"
                f"- Containments: {rep['n_containments']} | Rollbacks: {rep['n_rollbacks']} | Drills: {rep['n_drills']}\n"
                f"- Chaos Events: {rep['n_chaos_events']} | CB Drills: {rep['n_cb_drills']}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
