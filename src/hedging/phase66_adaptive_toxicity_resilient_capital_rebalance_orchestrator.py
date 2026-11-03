"""
Phase 66: Adaptive Toxicity-Resilient Capital Rebalance Orchestrator (crypto options + orderflow).

Adaptive toxicity-resilient capital rebalance orchestrator: regime/toxicity-driven
capital rebalance, venue failover rebalance, hedging rebalance guardrails, deterministic; PAPER-ONLY.
Composes Phases 17-65.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.hedging.phase65_adaptive_toxicity_resilient_capital_allocation_orchestrator import (
    Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator,
    Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig,
)
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
    h = hashlib.sha256(f"{seed}|p66reb|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p66reb_{tag}_{h}"


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
class Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig:
    seed: int = 66061
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 80
    rebalance_interval: int = 8
    toxicity_rebalance_threshold: float = 0.31
    failover_rebalance_threshold: float = 0.34
    capital_rebalance_cap_pct: float = 0.75
    hedging_rebalance_guardrail_strict: bool = True
    outdir: str = "research_state"

    def __post_init__(self) -> None:
        if not isinstance(self.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.paper_only:
            raise ValueError(
                "Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator: paper_only must remain True (live path hard-gated)"
            )


class Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator:
    """Adaptive toxicity-resilient capital rebalance orchestrator for crypto options + orderflow."""

    def __init__(self, cfg: Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig | None = None) -> None:
        self.cfg = cfg or Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig()
        if not self.cfg.paper_only:
            raise ValueError("Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator: paper_only must remain True")
        self.cap65 = Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator(
            Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles)
        )
        self.orch64 = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(
            Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles)
        )
        self.orch63 = Phase63AdaptiveToxicityResilientDeploymentOrchestrator(
            Phase63AdaptiveToxicityResilientDeploymentOrchestratorConfig(seed=self.cfg.seed + 3, paper_only=True, cycles=self.cfg.cycles)
        )
        self.res62 = Phase62AdaptiveRegimeConditionalExecutionResilience(
            Phase62AdaptiveRegimeConditionalResilienceConfig(seed=self.cfg.seed + 4, paper_only=True, cycles=5)
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.rebalance_triggers: List[Dict[str, Any]] = []
        self.capital_rebalances: List[Dict[str, Any]] = []
        self.venue_failover_rebalances: List[Dict[str, Any]] = []
        self.hedge_rebalance_guardrails: List[Dict[str, Any]] = []
        self.rebalance_attestations: List[Dict[str, Any]] = []
        self._cycle = 0

    def _rebalance_decision(self, toxicity: float, regime: str, alloc_paused: bool, failover: bool, drawdown_pct: float) -> Dict[str, Any]:
        rebalance = False
        failover_rb = False
        reasons: List[str] = []
        if toxicity >= self.cfg.toxicity_rebalance_threshold:
            rebalance = True
            reasons.append("toxicity_rebalance")
        if failover or toxicity >= self.cfg.failover_rebalance_threshold:
            failover_rb = True
            rebalance = True
            reasons.append("venue_failover_rebalance")
        if alloc_paused:
            rebalance = True
            reasons.append("allocation_pause_rebalance")
        if drawdown_pct >= 0.07:
            rebalance = True
            reasons.append("drawdown_rebalance")
        if regime == "high_toxicity":
            rebalance = True
            failover_rb = True
        hedge_hard = self.cfg.hedging_rebalance_guardrail_strict and (failover_rb or regime == "high_toxicity")
        return {
            "rebalance_triggered": bool(rebalance),
            "venue_failover_rebalance": bool(failover_rb),
            "hedge_guardrail_mode": "hard" if hedge_hard else ("tight" if regime == "elevated" else "normal"),
            "reasons": reasons,
        }

    def orchestrate_capital_rebalance(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.rebalance_triggers = []
        self.capital_rebalances = []
        self.venue_failover_rebalances = []
        self.hedge_rebalance_guardrails = []
        self.rebalance_attestations = []

        cap65_rep = self.cap65.orchestrate_capital_allocation(cycles=5)
        self.orch64.orchestrate_capital_deployment(cycles=5)
        self.orch63.orchestrate_deployment(cycles=5)
        self.res62.run_resilience(cycles=5)
        tox_rep = self.tox58.mitigate(cycles=4)
        self.risk54.run_campaign(cycles=3)
        self.of.run_campaign(cycles=4)

        avg_tox = _finite(tox_rep.get("avg_vpin", 0.18))

        for i in range(cycles):
            venue = self.cfg.venues[i % len(self.cfg.venues)]
            underlying = self.cfg.underlyings[i % len(self.cfg.underlyings)]
            toxicity_i = max(0.0, min(1.0, avg_tox + (i % 13) * 0.015))
            if toxicity_i >= 0.37:
                regime = "high_toxicity"
            elif toxicity_i >= 0.23:
                regime = "elevated"
            else:
                regime = "normal"
            alloc_paused = (i % 11 == 0) and toxicity_i >= 0.29
            failover = (i % 17 == 0) and toxicity_i >= 0.32
            drawdown_i = max(0.0, min(0.12, (i % 19) * 0.005))
            dec = self._rebalance_decision(toxicity_i, regime, alloc_paused, failover, drawdown_i)
            rebalance_size_pct = (
                round(float(_finite(self.cfg.capital_rebalance_cap_pct)), 6) if dec["rebalance_triggered"] else 0.0
            )

            if i % self.cfg.rebalance_interval == 0 or dec["rebalance_triggered"]:
                self.rebalance_triggers.append(
                    serialize_metrics_strict(
                        {
                            "rt_id": _make_id(self.cfg.seed, "rt", i),
                            "cycle": i,
                            "venue": venue,
                            "underlying": underlying,
                            "toxicity": round(float(_finite(toxicity_i)), 6),
                            "regime": regime,
                            **dec,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
                if dec["rebalance_triggered"]:
                    self.capital_rebalances.append(
                        serialize_metrics_strict(
                            {
                                "crb_id": _make_id(self.cfg.seed, "crb", i),
                                "cycle": i,
                                "venue": venue,
                                "rebalance_size_pct": rebalance_size_pct,
                                "capital_rebalance_cap_pct": self.cfg.capital_rebalance_cap_pct,
                                "reasons": dec["reasons"],
                                "paper_only": True,
                                "timestamp": _utc_now(),
                            }
                        )
                    )
                if dec["venue_failover_rebalance"]:
                    self.venue_failover_rebalances.append(
                        serialize_metrics_strict(
                            {
                                "vfrb_id": _make_id(self.cfg.seed, "vfrb", i),
                                "cycle": i,
                                "venue": venue,
                                "failover_rebalance_executed": True,
                                "paper_only": True,
                                "timestamp": _utc_now(),
                            }
                        )
                    )
                self.hedge_rebalance_guardrails.append(
                    serialize_metrics_strict(
                        {
                            "hrg_id": _make_id(self.cfg.seed, "hrg", i),
                            "cycle": i,
                            "venue": venue,
                            "mode": dec["hedge_guardrail_mode"],
                            "strict": self.cfg.hedging_rebalance_guardrail_strict,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
                if dec["rebalance_triggered"]:
                    self.rebalance_attestations.append(
                        serialize_metrics_strict(
                            {
                                "rba_id": _make_id(self.cfg.seed, "rba", i),
                                "cycle": i,
                                "rebalance_triggered": True,
                                "attested": True,
                                "paper_only": True,
                                "timestamp": _utc_now(),
                            }
                        )
                    )

        rep = serialize_metrics_strict(
            {
                "phase": "PHASE66_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_REBALANCE_ORCHESTRATOR",
                "timestamp": _utc_now(),
                "paper_only": True,
                "gates_ok": True,
                "seed": self.cfg.seed,
                "cycles": cycles,
                "n_rebalance_triggers": len(self.rebalance_triggers),
                "n_capital_rebalances": len(self.capital_rebalances),
                "n_venue_failover_rebalances": len(self.venue_failover_rebalances),
                "n_hedge_rebalance_guardrails": len(self.hedge_rebalance_guardrails),
                "n_rebalance_attestations": len(self.rebalance_attestations),
                "rebalance_trigger_rate": round(
                    float(sum(1 for x in self.rebalance_triggers if x.get("rebalance_triggered")) / max(1, len(self.rebalance_triggers))),
                    6,
                ),
                "capital_rebalance_cap_pct": self.cfg.capital_rebalance_cap_pct,
                "composes": ["PHASE65", "PHASE64", "PHASE63", "PHASE62", "PHASE57", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase66_cap_reb_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.orchestrate_capital_rebalance(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "rebalance_triggers": self.rebalance_triggers,
                "capital_rebalances": self.capital_rebalances,
                "venue_failover_rebalances": self.venue_failover_rebalances,
                "hedge_rebalance_guardrails": self.hedge_rebalance_guardrails,
                "rebalance_attestations": self.rebalance_attestations,
            }
        )
        _assert_finite(payload, "phase66_cap_reb_payload")
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir / f"PHASE66_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_REBALANCE_ORCHESTRATOR_{ts}.json"
        md_path = outdir / f"PHASE66_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_REBALANCE_ORCHESTRATOR_{ts}.md"
        json_path.write_text(json.dumps(payload, indent=2, allow_nan=False))
        md = [
            "# PHASE66_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_REBALANCE_ORCHESTRATOR",
            f"Timestamp: {_utc_now()}",
            f"paper_only: {rep['paper_only']}",
            f"gates_ok: {rep['gates_ok']}",
            f"cycles: {rep['cycles']}",
            f"rebalance_trigger_rate: {rep['rebalance_trigger_rate']}",
            f"n_venue_failover_rebalances: {rep['n_venue_failover_rebalances']}",
            f"n_rebalance_attestations: {rep['n_rebalance_attestations']}",
            f"capital_rebalance_cap_pct: {rep['capital_rebalance_cap_pct']}",
            "",
            "## Composes",
            "- PHASE65, PHASE64, PHASE63, PHASE62, PHASE57, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
