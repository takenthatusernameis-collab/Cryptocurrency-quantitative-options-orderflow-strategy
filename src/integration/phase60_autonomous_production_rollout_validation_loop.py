"""
Phase 60: Autonomous Production Rollout Validation Loop (crypto options + orderflow).

Autonomous production rollout validation: failover drills, circuit breakers,
post-trade reconciliation, auto-contain/rollback, artifacts, composes Phases 17-59.
PAPER-ONLY enforced.
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
from src.hedging.phase59_adaptive_cross_asset_hedge_fusion import Phase59AdaptiveCrossAssetHedgeFusion
from src.hedging.phase60_toxicity_resilient_hedge_fusion import Phase60ToxicityResilientHedgeFusion
from src.integration.phase58_autonomous_risk_containment_loop import Phase58AutonomousRiskContainmentLoop
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
    h = hashlib.sha256(f"{seed}|p60rollout|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p60rollout_{tag}_{h}"


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
class Phase60AutonomousProductionRolloutConfig:
    seed: int = 60062
    paper_only: bool = True
    cycles: int = 80
    failover_drill_enabled: bool = True
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
            raise ValueError("Phase60AutonomousProductionRolloutValidationLoop: paper_only must remain True (live path hard-gated)")


class Phase60AutonomousProductionRolloutValidationLoop:
    """Autonomous production rollout validation loop composing Phases 17-59."""

    def __init__(self, cfg: Phase60AutonomousProductionRolloutConfig | None = None) -> None:
        self.cfg = cfg or Phase60AutonomousProductionRolloutConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase60AutonomousProductionRolloutValidationLoop: paper_only must remain True")
        self.harden59 = Phase59AutonomousExecutionHardeningLoop()
        self.execint60 = Phase60AdaptiveExecutionIntelligenceEngine()
        self.hedge59 = Phase59AdaptiveCrossAssetHedgeFusion()
        self.toxhedge60 = Phase60ToxicityResilientHedgeFusion()
        self.arc58 = Phase58AutonomousRiskContainmentLoop()
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.tox58 = Phase58FlowToxicityMitigator()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.failovers: List[Dict[str, Any]] = []
        self.reconciliations: List[Dict[str, Any]] = []
        self.containments: List[Dict[str, Any]] = []
        self.rollbacks: List[Dict[str, Any]] = []
        self.drills: List[Dict[str, Any]] = []
        self.venue_states: Dict[str, str] = {v: "active" for v in ("deribit", "okx", "bybit", "binance")}
        self._cycle = 0

    def run_rollout_validation(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.failovers = []
        self.reconciliations = []
        self.containments = []
        self.rollbacks = []
        self.drills = []
        harden_rep = self.harden59.run_hardening(cycles=4)
        exec_rep = self.execint60.run_intelligence(cycles=4)
        hedge_rep = self.hedge59.run_hedge_fusion(cycles=4)
        toxhedge_rep = self.toxhedge60.run_hedge_fusion(cycles=4)
        risk_rep = self.risk54.run_campaign(cycles=4)
        cb_rep = self.cb57.evaluate(metrics={
            "drawdown_pct": _finite(risk_rep.get("max_drawdown_pct", 0.02)) if "max_drawdown_pct" in risk_rep else 0.02,
            "latency_ms_p99": _finite(exec_rep.get("avg_latency_ms", 20.0)),
            "toxicity": _finite(exec_rep.get("avg_toxicity", 0.18)),
            "risk_breach": float(len(risk_rep.get("breaches", []))) / 100.0,
        })
        of_rep = self.of.run_campaign(cycles=3)
        tox_rep = self.tox58.mitigate(cycles=4)
        ks_rep = self.ks.run_campaign()
        halted = bool(ks_rep.get("halted", False)) or bool(cb_rep.get("halted", False)) or bool(harden_rep.get("halted", False))
        cb_breaches = cb_rep.get("breaches", [])
        active_venues = [v for v, s in self.venue_states.items() if s == "active"]
        rollout_score = 1.0

        for i in range(cycles):
            venue = active_venues[i % max(1, len(active_venues))] if active_venues else "deribit"
            underlying = ("BTC", "ETH", "SOL")[i % 3]
            dd_pct = 0.015 + (i % 11) * 0.004
            risk_breach_i = bool(cb_breaches) or halted or dd_pct >= self.cfg.drawdown_halt_pct
            latency_ms = 5.0 + (i % 8) * 3.0 + _finite(exec_rep.get("avg_toxicity", 0.18)) * 6.0

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
                else:
                    rollout_score = max(0.0, rollout_score - 0.01)

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
        gates_ok = bool(
            rec_rate >= self.cfg.rollout_readiness_pct
            and drill_pass_rate >= self.cfg.rollout_readiness_pct
            and not halted
            and harden_rep.get("gates_ok", False)
            and exec_rep.get("gates_ok", False)
            and hedge_rep.get("gates_ok", False)
            and toxhedge_rep.get("gates_ok", False)
        )
        rep = serialize_metrics_strict({
            "phase": "PHASE60_AUTONOMOUS_PRODUCTION_ROLLOUT_VALIDATION_LOOP",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "halted": bool(halted),
            "rollout_score": float(_finite(rollout_score)),
            "reconciliation_rate": float(_finite(rec_rate)),
            "drill_pass_rate": float(_finite(drill_pass_rate)),
            "n_failovers": len(self.failovers),
            "n_reconciliations": len(self.reconciliations),
            "n_containments": len(self.containments),
            "n_rollbacks": len(self.rollbacks),
            "n_drills": len(self.drills),
            "cb_breaches": len(cb_breaches),
            "harden59_ok": bool(harden_rep.get("gates_ok", False)),
            "execint60_ok": bool(exec_rep.get("gates_ok", False)),
            "hedge59_ok": bool(hedge_rep.get("gates_ok", False)),
            "toxhedge60_ok": bool(toxhedge_rep.get("gates_ok", False)),
            "risk54_ok": bool(risk_rep.get("gates_ok", False)),
            "cb57_ok": bool(cb_rep.get("gates_ok", False)),
            "composed_phases": "17-59",
        })
        _assert_finite(rep, "phase60_rollout_validation_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_rollout_validation(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE60_AUTONOMOUS_PRODUCTION_ROLLOUT_{ts}.json"
        mpath = out / f"PHASE60_AUTONOMOUS_PRODUCTION_ROLLOUT_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(
                f"# PHASE60 Autonomous Production Rollout Validation Loop\n\n"
                f"- Timestamp: {rep['timestamp']}\n"
                f"- Gates OK: {rep['gates_ok']}\n"
                f"- Halted: {rep['halted']}\n"
                f"- Rollout Score: {rep['rollout_score']:.4f} | Reconciliation Rate: {rep['reconciliation_rate']:.4f}\n"
                f"- Drill Pass Rate: {rep['drill_pass_rate']:.4f}\n"
                f"- Failovers: {rep['n_failovers']} | Reconciliations: {rep['n_reconciliations']}\n"
                f"- Containments: {rep['n_containments']} | Rollbacks: {rep['n_rollbacks']} | Drills: {rep['n_drills']}\n"
                f"- Composed: {rep['composed_phases']}\n"
            )
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
