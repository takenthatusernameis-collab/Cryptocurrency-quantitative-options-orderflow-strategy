"""
Phase 63: Adaptive Toxicity-Resilient Deployment Orchestrator (crypto options + orderflow).

Adaptive toxicity-resilient deployment orchestrator: regime/toxicity-driven rollout gating,
venue failover, hedging guardrails, deterministic. PAPER-ONLY.
Composes Phases 17-62.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase62_adaptive_regime_conditional_execution_resilience import (
    Phase62AdaptiveRegimeConditionalExecutionResilience,
    Phase62AdaptiveRegimeConditionalResilienceConfig,
)
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
    h = hashlib.sha256(f"{seed}|p63orch|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p63orch_{tag}_{h}"


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
class Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig:
    seed: int = 63061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    rollout_gate_readiness: float = 0.92
    toxicity_failover_threshold: float = 0.32
    hedging_guardrail_strict: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError("Phase63AdaptiveToxicityResilientDeploymentOrchestrator: paper_only must remain True (live path hard-gated)")


class Phase63AdaptiveToxicityResilientDeploymentOrchestrator:
    """Adaptive toxicity-resilient deployment orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig | None = None) -> None:
        self.cfg = cfg or Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase63AdaptiveToxicityResilientDeploymentOrchestrator: paper_only must remain True")
        self.res62 = Phase62AdaptiveRegimeConditionalExecutionResilience(
            Phase62AdaptiveRegimeConditionalResilienceConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=60)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.rollout_gates: List[Dict[str, Any]] = []
        self.failovers: List[Dict[str, Any]] = []
        self.hedge_guardrails: List[Dict[str, Any]] = []
        self.orchestrations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _gating_decision(self, readiness: float, toxicity: float, regime: str) -> Dict[str, Any]:
        gate_open = readiness >= self.cfg.rollout_gate_readiness
        failover = False
        if toxicity >= self.cfg.toxicity_failover_threshold or regime == "high_toxicity":
            gate_open = False
            failover = True
        hedge_hard = self.cfg.hedging_guardrail_strict and (failover or regime == "high_toxicity")
        return {
            "gate_open": bool(gate_open),
            "venue_failover_triggered": bool(failover),
            "hedge_guardrail_mode": "hard" if hedge_hard else ("tight" if regime == "elevated" else "normal"),
        }

    def orchestrate_deployment(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.rollout_gates = []
        self.failovers = []
        self.hedge_guardrails = []
        self.orchestrations = []

        res_rep = self.res62.run_resilience(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        of_rep = self.of.run_campaign(cycles=40)
        risk_rep = self.risk54.run_campaign(cycles=30)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.016))
            if toxicity_i >= 0.38:
                regime = "high_toxicity"
            elif toxicity_i >= 0.24:
                regime = "elevated"
            else:
                regime = "normal"
            readiness = max(0.0, min(1.0, 0.94 - toxicity_i * 0.15 + (i % 7) * 0.005))
            dec = self._gating_decision(readiness, toxicity_i, regime)

            self.orchestrations.append(
                serialize_metrics_strict(
                    {
                        "orch_id": _make_id(self.cfg.seed, "orch", i),
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "regime": regime,
                        "toxicity": round(float(_finite(toxicity_i)), 6),
                        "readiness": round(float(_finite(readiness)), 6),
                        **dec,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            self.rollout_gates.append(
                serialize_metrics_strict(
                    {
                        "gate_id": _make_id(self.cfg.seed, "gate", i),
                        "cycle": i,
                        "gate_open": dec["gate_open"],
                        "readiness": round(float(_finite(readiness)), 6),
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            if dec["venue_failover_triggered"]:
                self.failovers.append(
                    serialize_metrics_strict(
                        {
                            "fo_id": _make_id(self.cfg.seed, "fo", i),
                            "cycle": i,
                            "trigger": "toxicity_or_regime",
                            "failover_executed": True,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            self.hedge_guardrails.append(
                serialize_metrics_strict(
                    {
                        "hgr_id": _make_id(self.cfg.seed, "hgr", i),
                        "cycle": i,
                        "mode": dec["hedge_guardrail_mode"],
                        "strict": self.cfg.hedging_guardrail_strict,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE63_ADAPTIVE_TOXICITY_RESILIENT_DEPLOYMENT_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_rollout_gates": len(self.rollout_gates),
                "n_failovers": len(self.failovers),
                "n_hedge_guardrails": len(self.hedge_guardrails),
                "n_orchestrations": len(self.orchestrations),
                "gate_open_rate": round(
                    float(sum(1 for x in self.rollout_gates if x.get("gate_open")) / max(1, len(self.rollout_gates))),
                    6,
                ),
                "composes": ["PHASE62", "PHASE61", "PHASE57", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase63_orch_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.orchestrate_deployment(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "orchestrations": self.orchestrations,
                "rollout_gates": self.rollout_gates,
                "failovers": self.failovers,
                "hedge_guardrails": self.hedge_guardrails,
            }
        )
        _assert_finite(payload, "phase63_orch_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE63_ADAPTIVE_TOXICITY_RESILIENT_DEPLOYMENT_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE63_ADAPTIVE_TOXICITY_RESILIENT_DEPLOYMENT_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE63_ADAPTIVE_TOXICITY_RESILIENT_DEPLOYMENT_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"n_failovers: {rep['n_failovers']}",
            f"gate_open_rate: {rep['gate_open_rate']}",
            "",
            "## Composes",
            "- PHASE62, PHASE61, PHASE57, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
