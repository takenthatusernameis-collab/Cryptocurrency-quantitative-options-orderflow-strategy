"""
Phase 48: Alpha Orchestration Loop - regime-conditional options strategies
& orderflow signal fusion for crypto options + orderflow quant.

Composes Phase 48 alpha engine with Phases 17-47 (orderflow, vol surface,
execution alpha, risk/hedge, resilience, deployment) under kill-switch gates.
PAPER-ONLY. Deterministic artifacts.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.alpha.phase48_regime_conditional_options_engine import (
    Phase48Config,
    Phase48RegimeConditionalOptionsEngine,
)
from src.deployment.phase44_live_capital_deployment import Phase44LiveCapitalDeployment
from src.execution.phase47_cross_venue_arbitrage_engine import (
    Phase47Config,
    Phase47CrossVenueArbitrageEngine,
)
from src.integration.phase42_risk_hedge_loop import Loop42Config, Phase42RiskHedgeLoop
from src.integration.phase45_resilience_validation_loop import Phase45ResilienceValidationLoop
from src.monitoring.slo import SLOMonitor, register_default_slos
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


class Phase48AlphaOrchestrationLoop:
    """End-to-end alpha orchestration: regime-conditional options + orderflow fusion."""

    def __init__(self, seed: int = 48048, cycles: int = 60, paper_only: bool = True,
                 outdir: str = "research_state") -> None:
        if not isinstance(paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not paper_only:
            raise ValueError("Phase48AlphaOrchestrationLoop: paper_only must remain True (live path hard-gated)")
        self.seed = int(seed)
        self.cycles = int(cycles)
        self.paper_only = True
        self.outdir = outdir
        self.alpha = Phase48RegimeConditionalOptionsEngine(Phase48Config(
            seed=self.seed, paper_only=True, cycles=self.cycles, outdir=self.outdir,
        ))
        self.arb47 = Phase47CrossVenueArbitrageEngine(Phase47Config(
            seed=self.seed + 47, paper_only=True, cycles=self.cycles, outdir=self.outdir,
        ))
        self.deployment = Phase44LiveCapitalDeployment(seed=self.seed, paper_only=True)
        self.risk_hedge = Phase42RiskHedgeLoop(Loop42Config(seed=self.seed + 42, cycles=self.cycles,
                                                            paper_only=True, modes="paper"))
        self.resilience = Phase45ResilienceValidationLoop(seed=self.seed + 45, cycles=self.cycles,
                                                          paper_only=True, outdir=self.outdir)
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.of = OrderflowAlphaIntegrator(OrderflowAlphaIntegrationConfig32(
            seed=self.seed + 32, paper_only=True, cycles=self.cycles,
        ))
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.halt_events: List[Dict[str, Any]] = []
        self._halt_ctr = 0

    def _halt_id(self) -> str:
        self._halt_ctr += 1
        h = hashlib.sha256(f"{self.seed}|p48halt|{self._halt_ctr}".encode()).hexdigest()[:12]
        return f"p48_halt_{h}"

    def _utc_now(self) -> str:
        import time as _time
        return _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())

    def run(self) -> Dict[str, Any]:
        outdir_p = Path(self.outdir)
        outdir_p.mkdir(parents=True, exist_ok=True)

        alpha_rep = self.alpha.run_campaign(cycles=self.cycles)
        self.alpha.generate_reports(self.outdir)
        arb_rep = self.arb47.run_campaign(cycles=self.cycles)
        self.arb47.generate_reports(self.outdir)
        of_rep = self.of.run_campaign(cycles=self.cycles)
        rh_rep = self.risk_hedge.run()
        res_rep = self.resilience.run()
        ksum = self.ks.run_campaign()

        halt_executed = bool(
            not alpha_rep.get("gates_ok", True)
            or not arb_rep.get("gates_ok", True)
            or not rh_rep.get("gates_ok", True)
            or not res_rep.get("gates_ok", True)
        )
        if halt_executed:
            self.halt_events.append({
                "trigger_id": self._halt_id(),
                "cycle": self.cycles,
                "timestamp": self._utc_now(),
                "reason": "alpha_or_arb_or_risk_or_resilience_breach",
                "severity": "critical",
                "action": "halt_alpha_orchestration_and_roll_back",
                "auto_executed": True,
                "paper_only": True,
            })

        slo_evals = self.slo.evaluate_all()
        slo_alerts_fired = sum(1 for e in slo_evals if not e.get("met", True))
        gates_ok = bool(alpha_rep.get("gates_ok", False) and arb_rep.get("gates_ok", False))
        if gates_ok:
            gates_ok = True

        rep = serialize_metrics_strict({
            "phase": "PHASE48_ALPHA_ORCHESTRATION_LOOP",
            "timestamp": self._utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "modes": "paper",
            "cycles": self.cycles,
            "gates_ok": bool(gates_ok),
            "alpha_campaign": alpha_rep,
            "arb47_campaign": {"gates_ok": arb_rep.get("gates_ok"), "n_exploitable": arb_rep.get("n_exploitable")},
            "orderflow_alpha_campaign": {"paper_only": of_rep.get("paper_only"), "gates_ok": of_rep.get("gates_ok", True)},
            "risk_hedge_campaign": {"gates_ok": rh_rep.get("gates_ok"), "halted": rh_rep.get("halted", False)},
            "resilience_campaign": {"gates_ok": res_rep.get("gates_ok")},
            "phase39_kill_switches": {"paper_only": ksum.get("paper_only"), "gates_ok": ksum.get("gates_ok", True)},
            "n_regime_alphas": alpha_rep.get("n_alphas", 0),
            "n_qualified_alphas": alpha_rep.get("n_qualified_alphas", 0),
            "total_notional_allocated": alpha_rep.get("total_notional_allocated", 0.0),
            "n_arbitrage_opps": arb_rep.get("n_opps", 0),
            "halt_executed": bool(halt_executed),
            "halt_events": self.halt_events,
            "slo_evaluations": len(slo_evals),
            "slo_alerts_fired": slo_alerts_fired,
            "integrated_with": [
                "PHASE17-31_OPTIONS_VOL_SURFACE_ORDERFLOW",
                "PHASE32_ORDERFLOW_ALPHA",
                "PHASE39_KILL_SWITCHES",
                "PHASE42_RISK_HEDGE",
                "PHASE44_LIVE_CAPITAL_DEPLOYMENT",
                "PHASE45_RESILIENCE_CHAOS_FAILOVER",
                "PHASE46_ADAPTIVE_MM",
                "PHASE47_CROSS_VENUE_ARBITRAGE",
                "PHASE48_REGIME_CONDITIONAL_OPTIONS",
                "MONITORING_SLO",
            ],
        })
        json_path = outdir_p / f"phase48_alpha_orchestration_loop_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        md_path = outdir_p / f"phase48_alpha_orchestration_loop_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
        with open(json_path, "w") as f:
            json.dump(rep, f, indent=2, allow_nan=False)
        with open(md_path, "w") as f:
            f.write("# Phase 48 - Alpha Orchestration Loop\n\n")
            f.write(f"- Timestamp: {rep['timestamp']}\n")
            f.write(f"- Seed: {self.seed}\n")
            f.write(f"- Paper-only: true | Gates OK: {rep['gates_ok']}\n")
            f.write(f"- Regime alphas: {rep['n_regime_alphas']} (qualified: {rep['n_qualified_alphas']}) | Notional: ${rep['total_notional_allocated']:,.0f}\n")
            f.write(f"- Arb opps: {rep['n_arbitrage_opps']}\n")
            f.write(f"- Halt executed: {rep['halt_executed']}\n\n")
            f.write("## Integrated\n- " + "\n- ".join(rep['integrated_with']) + "\n")
        return rep
