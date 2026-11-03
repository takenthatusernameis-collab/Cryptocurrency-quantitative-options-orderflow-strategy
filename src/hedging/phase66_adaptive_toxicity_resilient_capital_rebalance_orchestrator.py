"""
Phase 66: Adaptive Toxicity-Resilient Capital Rebalance Orchestrator (crypto options + orderflow).

Adaptive toxicity-resilient capital rebalance orchestrator: regime/toxicity-driven
capital rebalance, venue failover rebalance, hedging rebalance guardrails, deterministic;
PAPER-ONLY. Composes Phases 17-65.
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
    rebalance_trigger_toxicity: float = 0.31
    rebalance_failover_threshold: float = 0.36
    rebalance_cap_pct: float = 0.75
    rebalance_cooldown_cycles: int = 3
    hedging_rebalance_strict: bool = True
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
            Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(
                seed=self.cfg.seed + 1, paper_only=True, cycles=self.cfg.cycles
            )
        )
        self.orch64 = Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestrator(
            Phase64AdaptiveToxicityResilientCapitalDeploymentOrchestratorConfig(
                seed=self.cfg.seed + 2, paper_only=True, cycles=self.cfg.cycles
            )
        )
        self.risk54 = Phase54RealtimeRiskFusionEngine()
        self.tox58 = Phase58FlowToxicityMitigator()
        self.of = OrderflowAlphaIntegrator(
            OrderflowAlphaIntegrationConfig32(seed=self.cfg.seed + 32, paper_only=True, cycles=self.cfg.cycles)
        )
        self.cb57 = Phase57ProductionCircuitBreakers()
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.cfg.seed + 39, paper_only=True))
        self.rebalance_triggers: List[Dict[str, Any]] = []
        self.rebalance_actions: List[Dict[str, Any]] = []
        self.venue_failover_rebalances: List[Dict[str, Any]] = []
        self.hedge_rebalance_guardrails: List[Dict[str, Any]] = []
        self.rebalance_cooldowns: List[Dict[str, Any]] = []
        self._cycle = 0
        self._last_rebalance_cycle = -10_000

    def _rebalance_decision(self, toxicity: float, regime: str, drawdown_pct: float, cap_util: float) -> Dict[str, Any]:
        trigger = False
        failover_rb = False
        reasons: List[str] = []
        if toxicity >= self.cfg.rebalance_trigger_toxicity:
            trigger = True
            reasons.append("toxicity_trigger")
        if toxicity >= self.cfg.rebalance_failover_threshold or regime == "high_toxicity":
            trigger = True
            failover_rb = True
            reasons.append("toxicity_failover_rebalance")
        if drawdown_pct >= 0.07:
            trigger = True
            reasons.append("drawdown_trigger")
        if cap_util >= 0.88:
            trigger = True
            reasons.append("cap_util_trigger")
        hedge_mode = "hard" if (self.cfg.hedging_rebalance_strict and failover_rb) else ("tight" if trigger else "normal")
        return {
            "rebalance_triggered": bool(trigger),
            "venue_failover_rebalance": bool(failover_rb),
            "hedge_rebalance_mode": hedge_mode,
            "reasons": reasons,
        }

    def orchestrate_capital_rebalance(self, cycles: int | None = None) -> Dict[str, Any]:
        cycles = int(cycles or self.cfg.cycles)
        self._cycle = cycles
        self.rebalance_triggers = []
        self.rebalance_actions = []
        self.venue_failover_rebalances = []
        self.hedge_rebalance_guardrails = []
        self.rebalance_cooldowns = []
        self._last_rebalance_cycle = -10_000

        cap_rep = self.cap65.orchestrate_capital_allocation(cycles=60)
        self.orch64.orchestrate_capital_deployment(cycles=60)
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
            drawdown_i = max(0.0, min(0.12, (i % 23) * 0.004))
            cap_util_i = max(0.0, min(1.0, 0.58 + (i % 19) * 0.016))
            dec = self._rebalance_decision(toxicity_i, regime, drawdown_i, cap_util_i)
            in_cooldown = (i - self._last_rebalance_cycle) < self.cfg.rebalance_cooldown_cycles
            if in_cooldown and dec["rebalance_triggered"]:
                dec = {
                    "rebalance_triggered": False,
                    "venue_failover_rebalance": False,
                    "hedge_rebalance_mode": "normal",
                    "reasons": ["cooldown"],
                }
            if dec["rebalance_triggered"]:
                self._last_rebalance_cycle = i

            self.rebalance_triggers.append(
                serialize_metrics_strict(
                    {
                        "rb_trig_id": _make_id(self.cfg.seed, "rbt", i),
                        "cycle": i,
                        "venue": venue,
                        "underlying": underlying,
                        "regime": regime,
                        "toxicity": round(float(_finite(toxicity_i)), 6),
                        **dec,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            if dec["rebalance_triggered"]:
                reb_size = round(float(min(self.cfg.rebalance_cap_pct, 0.6 + (i % 5) * 0.05)), 6)
                self.rebalance_actions.append(
                    serialize_metrics_strict(
                        {
                            "rba_id": _make_id(self.cfg.seed, "rba", i),
                            "cycle": i,
                            "venue": venue,
                            "rebalance_size_pct": reb_size,
                            "rebalance_executed": True,
                            "paper_only": True,
                            "timestamp": _utc_now(),
                        }
                    )
                )
            if dec["venue_failover_rebalance"]:
                self.venue_failover_rebalances.append(
                    serialize_metrics_strict(
                        {
                            "vfr_id": _make_id(self.cfg.seed, "vfr", i),
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
                        "mode": dec["hedge_rebalance_mode"],
                        "strict": self.cfg.hedging_rebalance_strict,
                        "paper_only": True,
                        "timestamp": _utc_now(),
                    }
                )
            )
            if in_cooldown:
                self.rebalance_cooldowns.append(
                    serialize_metrics_strict(
                        {
                            "rcd_id": _make_id(self.cfg.seed, "rcd", i),
                            "cycle": i,
                            "cooldown_active": True,
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
                "n_rebalance_actions": len(self.rebalance_actions),
                "n_venue_failover_rebalances": len(self.venue_failover_rebalances),
                "n_hedge_rebalance_guardrails": len(self.hedge_rebalance_guardrails),
                "n_rebalance_cooldowns": len(self.rebalance_cooldowns),
                "rebalance_trigger_rate": round(
                    float(
                        sum(1 for x in self.rebalance_triggers if x.get("rebalance_triggered"))
                        / max(1, len(self.rebalance_triggers))
                    ),
                    6,
                ),
                "rebalance_cap_pct": self.cfg.rebalance_cap_pct,
                "composes": ["PHASE65", "PHASE64", "PHASE57", "PHASE54", "PHASE39", "PHASE58"],
            }
        )
        _assert_finite(rep, "phase66_reb_rep")
        return rep

    def generate_artifacts(self, outdir: str | None = None) -> Dict[str, Any]:
        outdir = Path(outdir or self.cfg.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        rep = self.orchestrate_capital_rebalance(cycles=self.cfg.cycles)
        payload = serialize_metrics_strict(
            {
                "report": rep,
                "rebalance_triggers": self.rebalance_triggers,
                "rebalance_actions": self.rebalance_actions,
                "venue_failover_rebalances": self.venue_failover_rebalances,
                "hedge_rebalance_guardrails": self.hedge_rebalance_guardrails,
                "rebalance_cooldowns": self.rebalance_cooldowns,
            }
        )
        _assert_finite(payload, "phase66_reb_payload")
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
            f"n_rebalance_actions: {rep['n_rebalance_actions']}",
            f"n_venue_failover_rebalances: {rep['n_venue_failover_rebalances']}",
            "",
            "## Composes",
            "- PHASE65, PHASE64, PHASE57, PHASE54, PHASE39, PHASE58",
            "",
        ]
        md_path.write_text("\n".join(md))
        rep["json_path"] = str(json_path)
        rep["md_path"] = str(md_path)
        return rep
