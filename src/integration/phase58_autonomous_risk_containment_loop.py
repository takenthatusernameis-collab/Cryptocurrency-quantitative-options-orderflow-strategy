"""
Phase 58: Autonomous Risk Containment Loop (crypto options + orderflow).

Autonomous risk containment loop: pre-trade/post-trade gates, dynamic throttles,
venue quarantine, auto-contain/rollback, artifacts (JSON/MD), composes Phases 17-57.
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

from src.execution.phase58_adaptive_options_smart_order_router import Phase58AdaptiveOptionsSmartOrderRouter
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
    h = hashlib.sha256(f"{seed}|p58arc|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p58arc_{tag}_{h}"


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
class Phase58AutonomousRiskContainmentConfig:
    seed: int = 58060
    paper_only: bool = True
    cycles: int = 80
    pretrade_breach_threshold: float = 0.35
    posttrade_breach_threshold: float = 0.42
    dynamic_throttle_high: float = 0.5
    dynamic_throttle_low: float = 0.8
    auto_contain_on_breach: bool = True
    auto_rollback_on_severe: bool = True
    venue_quarantine_enabled: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase58AutonomousRiskContainmentLoop: paper_only must remain True (live path hard-gated)")


class Phase58AutonomousRiskContainmentLoop:
    """Autonomous risk containment loop composing Phases 17-57."""

    def __init__(self, cfg: Phase58AutonomousRiskContainmentConfig | None = None) -> None:
        self.cfg = cfg or Phase58AutonomousRiskContainmentConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase58AutonomousRiskContainmentLoop: paper_only must remain True")
        self.tox = Phase58FlowToxicityMitigator()
        self.sor = Phase58AdaptiveOptionsSmartOrderRouter()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.pretrade_gates: List[Dict[str, Any]] = []
        self.posttrade_gates: List[Dict[str, Any]] = []
        self.containment_actions: List[Dict[str, Any]] = []
        self.venue_quarantine: List[Dict[str, Any]] = []
        self.rollback_events: List[Dict[str, Any]] = []
        self._cycle = 0

    def run_containment(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.pretrade_gates = []
        self.posttrade_gates = []
        self.containment_actions = []
        self.venue_quarantine = []
        self.rollback_events = []

        tox_rep = self.tox.mitigate(cycles=40)
        sor_rep = self.sor.route_adaptive(cycles=40)
        of_rep = self.of.run_campaign(cycles=30)
        ks_rep = self.ks.run_campaign()
        risk54_rep = self.risk54.run_fusion(cycles=30)
        cb57_rep = self.cb57.run_monitor(cycles=30)

        halted = bool(ks_rep.get("halted", False)) or bool(cb57_rep.get("halted", False))
        tox_breach = _finite(tox_rep.get("avg_vpin", 0.2))
        risk_breach = _finite(risk54_rep.get("max_greeks_notional_usd", 0.0)) / 10_000_000.0

        for i in range(cycles):
            pre_breach = (tox_breach * (1.0 + i * 1e-4)) >= self.cfg.pretrade_breach_threshold or halted
            post_breach = (risk_breach * (1.0 + i * 2e-4)) >= self.cfg.posttrade_breach_threshold
            pre_ok = not pre_breach
            post_ok = not post_breach
            self.pretrade_gates.append(serialize_metrics_strict({
                "gate_id": _make_id(self.cfg.seed, "pre", i),
                "cycle": i,
                "passed": bool(pre_ok),
                "breach": bool(pre_breach),
                "throttle_mult": float(self.cfg.dynamic_throttle_low if pre_ok else self.cfg.dynamic_throttle_high),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            self.posttrade_gates.append(serialize_metrics_strict({
                "gate_id": _make_id(self.cfg.seed, "post", i),
                "cycle": i,
                "passed": bool(post_ok),
                "breach": bool(post_breach),
                "paper_only": True,
                "timestamp": _utc_now(),
            }))
            if pre_breach and self.cfg.auto_contain_on_breach:
                self.containment_actions.append(serialize_metrics_strict({
                    "action_id": _make_id(self.cfg.seed, "contain", i),
                    "cycle": i,
                    "action": "contain_pretrade",
                    "severity": "high" if pre_breach else "med",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if post_breach and self.cfg.venue_quarantine_enabled and i % 4 == 0:
                self.venue_quarantine.append(serialize_metrics_strict({
                    "q_id": _make_id(self.cfg.seed, "vq", i),
                    "cycle": i,
                    "venue": ["deribit", "okx", "bybit", "binance"][i % 4],
                    "reason": "posttrade_breach",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))
            if post_breach and self.cfg.auto_rollback_on_severe and tox_breach > 0.3:
                self.rollback_events.append(serialize_metrics_strict({
                    "rb_id": _make_id(self.cfg.seed, "rb", i),
                    "cycle": i,
                    "action": "auto_rollback",
                    "trigger": "severe_posttrade_breach",
                    "paper_only": True,
                    "timestamp": _utc_now(),
                }))

        pre_pass_rate = sum(1 for g in self.pretrade_gates if g["passed"]) / max(1, len(self.pretrade_gates))
        post_pass_rate = sum(1 for g in self.posttrade_gates if g["passed"]) / max(1, len(self.posttrade_gates))
        gates_ok = bool(pre_pass_rate >= 0.7 and post_pass_rate >= 0.7) and not halted
        rep = serialize_metrics_strict({
            "phase": "PHASE58_AUTONOMOUS_RISK_CONTAINMENT_LOOP",
            "timestamp": _utc_now(),
            "seed": self.cfg.seed,
            "paper_only": True,
            "cycles": cycles,
            "gates_ok": bool(gates_ok),
            "pretrade_pass_rate": float(pre_pass_rate),
            "posttrade_pass_rate": float(post_pass_rate),
            "n_containment_actions": len(self.containment_actions),
            "n_venue_quarantines": len(self.venue_quarantine),
            "n_rollback_events": len(self.rollback_events),
            "halted": bool(halted),
            "composed_phases": "17-57",
            "tox58_ok": bool(tox_rep.get("gates_ok", False)),
            "sor58_ok": bool(sor_rep.get("gates_ok", False)),
            "risk54_ok": bool(risk54_rep.get("gates_ok", False)),
            "cb57_ok": bool(cb57_rep.get("gates_ok", False)),
        })
        _assert_finite(rep, "phase58_arc_report")
        return rep

    def generate_artifacts(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        rep = self.run_containment(cycles=self.cfg.cycles)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE58_AUTONOMOUS_RISK_CONTAINMENT_{ts}.json"
        mpath = out / f"PHASE58_AUTONOMOUS_RISK_CONTAINMENT_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE58 Autonomous Risk Containment Loop\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Pretrade Pass: {rep['pretrade_pass_rate']}\n- Posttrade Pass: {rep['posttrade_pass_rate']}\n- Containment: {rep['n_containment_actions']} | Quarantines: {rep['n_venue_quarantines']} | Rollbacks: {rep['n_rollback_events']}\n- Composed: {rep['composed_phases']}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep


# Compatibility: allow run_fusion alias
try:
    from src.risk.phase54_realtime_risk_fusion_engine import Phase54RealtimeRiskFusionEngine
    if not hasattr(Phase54RealtimeRiskFusionEngine, "run_fusion"):
        Phase54RealtimeRiskFusionEngine.run_fusion = Phase54RealtimeRiskFusionEngine.run_campaign  # type: ignore
except Exception:
    pass


# Compatibility: Phase57 circuit breakers may not have run_monitor
try:
    from src.risk.phase57_production_circuit_breakers import Phase57ProductionCircuitBreakers
    if not hasattr(Phase57ProductionCircuitBreakers, "run_monitor"):
        def _run_monitor(self, cycles: int = 30, **kwargs):
            rep = self.evaluate()
            # return in expected shape
            return {
                "phase": rep.get("phase"),
                "paper_only": rep.get("paper_only", True),
                "halted": bool(rep.get("halted", False)),
                "gates_ok": not bool(rep.get("halted", False)),
                "cycles": cycles,
            }
        Phase57ProductionCircuitBreakers.run_monitor = _run_monitor  # type: ignore
    if not hasattr(Phase57ProductionCircuitBreakers, "run_campaign"):
        Phase57ProductionCircuitBreakers.run_campaign = Phase57ProductionCircuitBreakers.run_monitor  # type: ignore
except Exception:
    pass
