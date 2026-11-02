"""
Phase 50: Options+Orderflow Execution Loop - toxicity-aware MM +
cross-venue relative-value execution for crypto options + orderflow quant.

Composes Phases 17-49 with Phase 50 engines under kill-switch gates.
PAPER-ONLY. Deterministic artifacts.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase48_regime_conditional_options_engine import Phase48Config, Phase48RegimeConditionalOptionsEngine
from src.deployment.phase44_live_capital_deployment import Phase44LiveCapitalDeployment
from src.execution.phase46_adaptive_mm_engine import AdaptiveMMConfig, Phase46AdaptiveMM
from src.execution.phase47_cross_venue_arbitrage_engine import Phase47Config, Phase47CrossVenueArbitrageEngine
from src.execution.phase50_cross_venue_relative_value_executor import Phase50CrossVenueRelativeValueExecutor, Phase50RVConfig
from src.hedging.phase49_orderflow_driven_delta_hedge import Phase49HedgeConfig, Phase49OrderflowDrivenDeltaHedge
from src.integration.phase42_risk_hedge_loop import Loop42Config, Phase42RiskHedgeLoop
from src.integration.phase45_resilience_validation_loop import Phase45ResilienceValidationLoop
from src.marketmaking.phase50_toxicity_aware_options_mm import Phase50MMConfig, Phase50ToxicityAwareOptionsMM
from src.monitoring.slo import SLOMonitor, register_default_slos
from src.orderflow.phase32_orderflow_alpha_integration import OrderflowAlphaIntegrationConfig32, OrderflowAlphaIntegrator
from src.risk.phase39_kill_switches_circuit_breakers import KillSwitchConfig39, Phase39KillSwitchesCircuitBreakers
from src.telemetry.serialization import serialize_metrics_strict
from src.volatility.phase49_vol_surface_arb_engine import Phase49VolSurfConfig, Phase49VolSurfaceArbEngine


class Phase50OptionsOrderflowExecutionLoop:
    def __init__(self, seed: int = 50050, cycles: int = 60, paper_only: bool = True, outdir: str = "research_state") -> None:
        if not isinstance(paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not paper_only:
            raise ValueError("Phase50OptionsOrderflowExecutionLoop: paper_only must remain True (live path hard-gated)")
        self.seed = int(seed)
        self.cycles = int(cycles)
        self.paper_only = True
        self.outdir = outdir
        self.mm50 = Phase50ToxicityAwareOptionsMM(Phase50MMConfig(seed=self.seed, paper_only=True, outdir=outdir))
        self.rv50 = Phase50CrossVenueRelativeValueExecutor(Phase50RVConfig(seed=self.seed + 1, paper_only=True, outdir=outdir))
        self.volarb49 = Phase49VolSurfaceArbEngine(Phase49VolSurfConfig(seed=self.seed + 49, paper_only=True, outdir=outdir))
        self.ofhedge49 = Phase49OrderflowDrivenDeltaHedge(Phase49HedgeConfig(seed=self.seed + 50, paper_only=True, outdir=outdir))
        self.alpha48 = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=self.seed + 48, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.arb47 = Phase47CrossVenueArbitrageEngine(Phase47Config(seed=self.seed + 47, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.mm46 = Phase46AdaptiveMM(AdaptiveMMConfig(seed=self.seed + 46, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.deployment = Phase44LiveCapitalDeployment(seed=self.seed, paper_only=True)
        self.risk_hedge = Phase42RiskHedgeLoop(Loop42Config(seed=self.seed + 42, cycles=self.cycles, paper_only=True, modes="paper"))
        self.resilience = Phase45ResilienceValidationLoop(seed=self.seed + 45, cycles=self.cycles, paper_only=True, outdir=self.outdir)
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.of = OrderflowAlphaIntegrator(OrderflowAlphaIntegrationConfig32(seed=self.seed + 32, paper_only=True, cycles=self.cycles))
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.halt_events: List[Dict[str, Any]] = []
        self._halt_ctr = 0

    def _halt_id(self) -> str:
        self._halt_ctr += 1
        h = hashlib.sha256(f"{self.seed}|p50halt|{self._halt_ctr}".encode()).hexdigest()[:12]
        return f"p50_halt_{h}"

    def _utc_now(self) -> str:
        import time as _time
        return _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())

    def run(self) -> Dict[str, Any]:
        outdir_p = Path(self.outdir)
        outdir_p.mkdir(parents=True, exist_ok=True)

        mm50_rep = self.mm50.run_campaign(cycles=self.cycles)
        self.mm50.generate_artifacts(self.outdir)
        rv50_rep = self.rv50.run_campaign(cycles=self.cycles)
        self.rv50.generate_artifacts(self.outdir)
        vol_rep = self.volarb49.run_campaign(cycles=self.cycles)
        self.volarb49.generate_artifacts(self.outdir)
        hedge_rep = self.ofhedge49.run_campaign(cycles=self.cycles)
        self.ofhedge49.generate_artifacts(self.outdir)
        alpha_rep = self.alpha48.run_campaign(cycles=self.cycles)
        self.alpha48.generate_reports(self.outdir)
        arb47_rep = self.arb47.run_campaign(cycles=self.cycles)
        self.arb47.generate_reports(self.outdir)
        mm46_rep = self.mm46.run_campaign(cycles=self.cycles)
        self.mm46.generate_reports(self.outdir)
        of_rep = self.of.run_campaign(cycles=self.cycles)
        rh_rep = self.risk_hedge.run()
        res_rep = self.resilience.run()
        ksum = self.ks.run_campaign()

        halt_executed = bool(
            not mm50_rep.get("gates_ok", True)
            or not rv50_rep.get("gates_ok", True)
            or not vol_rep.get("gates_ok", True)
            or not hedge_rep.get("gates_ok", True)
            or not alpha_rep.get("gates_ok", True)
            or not arb47_rep.get("gates_ok", True)
            or not rh_rep.get("gates_ok", True)
            or not res_rep.get("gates_ok", True)
        )
        if halt_executed:
            self.halt_events.append({
                "trigger_id": self._halt_id(),
                "cycle": self.cycles,
                "timestamp": self._utc_now(),
                "reason": "phase50_or_phase49_or_alpha_or_arb_or_risk_or_resilience_breach",
                "severity": "critical",
                "action": "halt_options_orderflow_execution_and_roll_back",
                "auto_executed": True,
                "paper_only": True,
            })

        slo_evals = self.slo.evaluate_all()
        slo_alerts_fired = sum(1 for e in slo_evals if not e.get("met", True))
        gates_ok = bool(mm50_rep.get("gates_ok", False) and rv50_rep.get("gates_ok", False))

        rep = serialize_metrics_strict({
            "phase": "PHASE50_OPTIONS_ORDERFLOW_EXECUTION_LOOP",
            "timestamp": self._utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "modes": "paper",
            "cycles": self.cycles,
            "gates_ok": bool(gates_ok),
            "toxicity_mm50": {"gates_ok": mm50_rep.get("gates_ok"), "n_quotes": mm50_rep.get("n_quotes"), "avg_spread_bps": mm50_rep.get("avg_spread_bps")},
            "cross_venue_rv50": {"gates_ok": rv50_rep.get("gates_ok"), "n_opps": rv50_rep.get("n_opps"), "n_exploitable": rv50_rep.get("n_exploitable")},
            "vol_surface_arb49": {"gates_ok": vol_rep.get("gates_ok"), "n_signals": vol_rep.get("n_signals"), "n_exploitable": vol_rep.get("n_exploitable")},
            "orderflow_delta_hedge49": {"gates_ok": hedge_rep.get("gates_ok"), "n_hedge_actions": hedge_rep.get("n_hedge_actions")},
            "alpha48_campaign": {"gates_ok": alpha_rep.get("gates_ok"), "n_qualified_alphas": alpha_rep.get("n_qualified_alphas")},
            "arb47_campaign": {"gates_ok": arb47_rep.get("gates_ok"), "n_exploitable": arb47_rep.get("n_exploitable")},
            "mm46_campaign": {"gates_ok": mm46_rep.get("gates_ok")},
            "orderflow_alpha_campaign": {"paper_only": of_rep.get("paper_only"), "gates_ok": of_rep.get("gates_ok", True)},
            "risk_hedge_campaign": {"gates_ok": rh_rep.get("gates_ok"), "halted": rh_rep.get("halted", False)},
            "resilience_campaign": {"gates_ok": res_rep.get("gates_ok")},
            "phase39_kill_switches": {"paper_only": ksum.get("paper_only"), "gates_ok": ksum.get("gates_ok", True)},
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
                "PHASE49_VOL_SURFACE_ARB",
                "PHASE49_ORDERFLOW_DRIVEN_DELTA_HEDGE",
                "PHASE50_TOXICITY_AWARE_OPTIONS_MM",
                "PHASE50_CROSS_VENUE_RELATIVE_VALUE_EXECUTOR",
                "MONITORING_SLO",
            ],
        })
        json_path = outdir_p / f"phase50_options_orderflow_execution_loop_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        md_path = outdir_p / f"phase50_options_orderflow_execution_loop_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
        with open(json_path, "w") as f:
            json.dump(rep, f, indent=2, allow_nan=False)
        with open(md_path, "w") as f:
            f.write("# Phase 50 - Options+Orderflow Execution Loop\n\n")
            f.write(f"- Timestamp: {rep['timestamp']}\n")
            f.write(f"- Seed: {self.seed}\n")
            f.write(f"- Paper-only: true | Gates OK: {rep['gates_ok']}\n")
            f.write(f"- Phase50 MM quotes: {mm50_rep['n_quotes']} (avg spread {mm50_rep['avg_spread_bps']:.2f} bps) | RV opps: {rv50_rep['n_opps']} (exploitable {rv50_rep['n_exploitable']})\n")
            f.write(f"- Phase49 Vol arb exploitable: {vol_rep.get('n_exploitable')} | Hedge actions: {hedge_rep.get('n_hedge_actions')}\n")
            f.write(f"- Halt executed: {rep['halt_executed']}\n\n")
            f.write("## Integrated\n- " + "\n- ".join(rep['integrated_with']) + "\n")
        return rep
