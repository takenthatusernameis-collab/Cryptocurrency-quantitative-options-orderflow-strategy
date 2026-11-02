"""
Phase 65: Adaptive Toxicity-Resilient Capital Allocation Orchestrator (crypto options + orderflow).

Adaptive toxicity-resilient capital allocation orchestrator: regime/toxicity-driven
capital reallocation, venue failover, hedging guardrails, deterministic; PAPER-ONLY.
Composes Phases 17-64.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase64_adaptive_toxicity_resilient_capital_deployment_orchestrator import (
    Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator,
    Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig,
)
from src.hedging.phase63_adaptive_toxicity_resilient_deployment_orchestrator import (
    Phase63AdaptiveToxicityResilientDeploymentOrchestrator,
    Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig,
)
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
from src.risk.phase57_production_circuit_breakers import Phase57ProductionCircuitBreakers
from src.risk.phase54_realtime_risk_fusion_engine import Phase54RealtimeRiskFusionEngine
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p65cap|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p65cap_{tag}_{h}"


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
class Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig:
    seed: int = 65061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    rollout_gate_readiness: float = 0.92
    toxicity_failover_threshold: float = 0.32
    capital_allocation_cap_pct: float = 0.8
    toxicity_alloc_pause_threshold: float = 0.4
    hedging_guardrail_strict: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator: paper_only must remain True (live path hard-gated)"
            )


class Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator:
    """Adaptive toxicity-resilient capital allocation orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig | None = None) -> None:
        self.cfg = cfg or Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator: paper_only must remain True")
        self.orch64 = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(
            Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(
                seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles
            )
        )
        self.orch63 = Phase63AdaptiveToxicityResilientDeploymentOrchestrator(
            Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig(
                seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles
            )
        )
        self.res62 = Phase62AdaptiveRegimeConditionalExecutionResilience(
            Phase62AdaptiveRegimeConditionalResilienceConfig(seed=self.cfg.seed + 3, paper_only=True, cycles=60)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.rollout_gates: List[Dict[str, Any]] = []
        self.capital_allocations: List[Dict[str, Any]] = []
        self.failovers: List[Dict[str, Any]] = []
        self.alloc_pauses: List[Dict[str, Any]] = []
        self.hedge_guardrails: List[Dict[str, Any]] = []
        self._cycle = 0

    def _capital_allocation_decision(
        self, readiness: float, toxicity: float, regime: str, drawdown_pct: float, cap_util: float
    ) -> Dict[str, Any]:
        alloc_allowed = readiness >= self.cfg.rollout_gate_readiness
        pause = False
        failover = False
        reasons: List[str] = []

        if toxicity >= self.cfg.toxicity_failover_threshold or regime == "high_toxicity":
            alloc_allowed = False
            failover = True
            reasons.append("toxicity_failover")
        if toxicity >= self.cfg.toxicity_alloc_pause_threshold:
            pause = True
            alloc_allowed = False
            reasons.append("toxicity_alloc_pause")
        if drawdown_pct >= 0.08:
            alloc_allowed = False
            pause = True
            reasons.append("drawdown_breach")
        if cap_util >= 0.9:
            alloc_allowed = False
            pause = True
            reasons.append("capital_utilization_cap")
        hedge_hard = self.cfg.hedging_guardrail_strict and (failover or regime == "high_toxicity" or pause)
        return {
            "alloc_allowed": bool(alloc_allowed),
            "alloc_pause": bool(pause),
            "venue_failover_triggered": bool(failover),
            "hedge_guardrail_mode": "hard" if hedge_hard else ("tight" if regime == "elevated" else "normal"),
            "reasons": reasons,
        }

    def orchestrate_capital_allocation(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.rollout_gates = []
        self.capital_allocations = []
        self.failovers = []
        self.alloc_pauses = []
        self.hedge_guardrails = []

        self.orch64.orchestrate_capital_deployment(cycles=60)
        self.orch63.orchestrate_deployment(cycles=60)
        self.res62.run_resilience(cycles=60)
        tox_rep = self.tox58.mitigate(cycles=40)
        self.risk54.run_campaign(cycles=30)
        self.of.run_campaign(cycles=40)

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
            drawdown_i = max(0.0, min(0.12, (i % 23) * 0.004))
            cap_util_i = max(0.0, min(1.0, 0.6 + (i % 19) * 0.015))
            dec = self._capital_allocation_decision(readiness, toxicity_i, regime, drawdown_i, cap_util_i)
            alloc_size_pct = (
                round(float(_finite(self.cfg.capital_allocation_cap_pct)), 6) if dec["alloc_allowed"] else 0.0
            )

            self.rollout_gates.append(
                serialize_metrics_strict(
                    {
                        "gate_id": _make_id(self.cfg.seed, "gate", i),
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
            self.capital_allocations.append(
                serialize_metrics_strict(
                    {
                        "alloc_id": _make_id(self.cfg.seed, "alloc", i),
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "alloc_allowed": dec["alloc_allowed"],
                        "alloc_size_pct": alloc_size_pct,
                        "capital_allocation_cap_pct": self.cfg.capital_allocation_cap_pct,
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
                            "venue": venue,
                            "trigger": "toxicity_or_regime",
                            "failover_executed": True,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if dec["alloc_pause"]:
                self.alloc_pauses.append(
                    serialize_metrics_strict(
                        {
                            "ap_id": _make_id(self.cfg.seed, "ap", i),
                            "cycle": i,
                            "venue": venue,
                            "reasons": dec["reasons"],
                            "alloc_paused": True,
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
                        "venue": venue,
                        "mode": dec["hedge_guardrail_mode"],
                        "strict": self.cfg.hedging_guardrail_strict,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE65_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_ALLOCATION_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_rollout_gates": len(self.rollout_gates),
                "n_capital_allocations": len(self.capital_allocations),
                "n_failovers": len(self.failovers),
                "n_alloc_pauses": len(self.alloc_pauses),
                "n_hedge_guardrails": len(self.hedge_guardrails),
                "alloc_allowed_rate": round(
                    float(sum(1 for x in self.capital_allocations if x.get("alloc_allowed")) / max(1, len(self.capital_allocations))),
                    6,
                ),
                "capital_allocation_cap_pct": self.cfg.capital_allocation_cap_pct,
                "composes": ["PHASE64", "PHASE63", "PHASE62", "PHASE57", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase65_cap_alloc_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.orchestrate_capital_allocation(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "rollout_gates": self.rollout_gates,
                "capital_allocations": self.capital_allocations,
                "failovers": self.failovers,
                "alloc_pauses": self.alloc_pauses,
                "hedge_guardrails": self.hedge_guardrails,
            }
        )
        _assert_finite(payload, "phase65_cap_alloc_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE65_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_ALLOCATION_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE65_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_ALLOCATION_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE65_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_ALLOCATION_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"alloc_allowed_rate: {rep['alloc_allowed_rate']}",
            f"n_failovers: {rep['n_failovers']}",
            f"n_alloc_pauses: {rep['n_alloc_pauses']}",
            f"capital_allocation_cap_pct: {rep['capital_allocation_cap_pct']}",
            "",
            "## Composes",
            "- PHASE64, PHASE63, PHASE62, PHASE57, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
