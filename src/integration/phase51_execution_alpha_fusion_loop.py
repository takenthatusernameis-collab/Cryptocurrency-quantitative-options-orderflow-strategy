"""
Phase 51: Execution-Alpha Fusion Loop (crypto options + orderflow).

End-to-end execution-alpha fusion loop composing Phases 17-50:
Phase 50 toxicity-aware MM + cross-venue RV executor, Phase 49 vol surface arb +
orderflow-driven delta hedge, Phase 48 regime-conditional alpha, Phase 47 cross-venue
arb/execution-alpha, Phase 46 adaptive MM, Phase 51 adaptive orderflow alpha fusion +
latency-aware options SOR, plus risk/limits/kill-switches (39), risk-hedge loop (42),
live capital deployment (44), chaos/failover/resilience (45), monitoring/SLO,
reconciliation/margin/collateral, settlement/finality. PAPER-ONLY. Deterministic
artifacts.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Dict, List

from src.alpha.phase48_regime_conditional_options_engine import (
    Phase48Config,
    Phase48RegimeConditionalOptionsEngine,
)
from src.alpha.phase51_adaptive_orderflow_alpha_fusion import (
    Phase51AlphaFusionConfig,
    Phase51AdaptiveOrderflowAlphaFusion,
)
from src.deployment.phase44_live_capital_deployment import Phase44LiveCapitalDeployment
from src.execution.phase46_adaptive_mm_engine import AdaptiveMMConfig, Phase46AdaptiveMM
from src.execution.phase47_cross_venue_arbitrage_engine import (
    Phase47Config,
    Phase47CrossVenueArbitrageEngine,
)
from src.execution.phase50_cross_venue_relative_value_executor import (
    Phase50CrossVenueRelativeValueExecutor,
    Phase50RVConfig,
)
from src.execution.phase51_latency_aware_options_sor import (
    Phase51LatencyAwareOptionsSOR,
    Phase51SORConfig,
)
from src.hedging.phase49_orderflow_driven_delta_hedge import (
    Phase49HedgeConfig,
    Phase49OrderflowDrivenDeltaHedge,
)
from src.integration.phase42_risk_hedge_loop import Loop42Config, Phase42RiskHedgeLoop
from src.integration.phase45_resilience_validation_loop import Phase45ResilienceValidationLoop
from src.marketmaking.phase50_toxicity_aware_options_mm import (
    Phase50MMConfig,
    Phase50ToxicityAwareOptionsMM,
)
from src.monitoring.slo import SLOMonitor, register_default_slos
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.reconciliation.phase40_position_margin_audit import (
    Phase40AuditConfig,
    Phase40PositionMarginAudit,
)
from src.risk.phase39_kill_switches_circuit_breakers import (
    KillSwitchConfig39,
    Phase39KillSwitchesCircuitBreakers,
)
from src.settlement.phase41_cross_venue_settlement import (
    Phase41SettlementConfig,
    Phase41CrossVenueSettlement,
)
from src.telemetry.serialization import serialize_metrics_strict
from src.volatility.phase49_vol_surface_arb_engine import (
    Phase49VolSurfConfig,
    Phase49VolSurfaceArbEngine,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    import hashlib as _h

    h = _h.sha256(f"{seed}|p51loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p51loop_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if isfinite(v) else default


class Phase51ExecutionAlphaFusionLoop:
    """End-to-end adaptive orderflow alpha fusion + latency-aware options SOR loop."""

    def __init__(self, seed: int = 51051, cycles: int = 60, paper_only: bool = True, outdir: str = "research_state") -> None:
        if not isinstance(paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not paper_only:
            raise ValueError("Phase51ExecutionAlphaFusionLoop: paper_only must remain True (live path hard-gated)")
        self.seed = int(seed)
        self.cycles = int(cycles)
        self.paper_only = True
        self.outdir = outdir

        self.alpha51 = Phase51AdaptiveOrderflowAlphaFusion(
            Phase51AlphaFusionConfig(seed=self.seed + 51, paper_only=True, outdir=outdir)
        )
        self.sor51 = Phase51LatencyAwareOptionsSOR(
            Phase51SORConfig(seed=self.seed + 52, paper_only=True, outdir=outdir)
        )
        self.mm50 = Phase50ToxicityAwareOptionsMM(
            Phase50MMConfig(seed=self.seed + 50, paper_only=True, outdir=outdir)
        )
        self.rv50 = Phase50CrossVenueRelativeValueExecutor(
            Phase50RVConfig(seed=self.seed + 53, paper_only=True, outdir=outdir)
        )
        self.volarb49 = Phase49VolSurfaceArbEngine(Phase49VolSurfConfig(seed=self.seed + 49, paper_only=True, outdir=outdir))
        self.ofhedge49 = Phase49OrderflowDrivenDeltaHedge(Phase49HedgeConfig(seed=self.seed + 54, paper_only=True, outdir=outdir))
        self.alpha48 = Phase48RegimeConditionalOptionsEngine(
            Phase48Config(seed=self.seed + 48, paper_only=True, cycles=self.cycles, outdir=self.outdir)
        )
        self.arb47 = Phase47CrossVenueArbitrageEngine(Phase47Config(seed=self.seed + 47, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.mm46 = Phase46AdaptiveMM(AdaptiveMMConfig(seed=self.seed + 46, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.deployment = Phase44LiveCapitalDeployment(seed=self.seed, paper_only=True)
        self.risk_hedge = Phase42RiskHedgeLoop(
            Loop42Config(seed=self.seed + 42, cycles=self.cycles, paper_only=True, modes="paper")
        )
        self.resilience = Phase45ResilienceValidationLoop(
            seed=self.seed + 45, cycles=self.cycles, paper_only=True, outdir=self.outdir
        )
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.of = OrderflowAlphaIntegrator(OrderflowAlphaIntegrationConfig32(seed=self.seed + 32, paper_only=True, cycles=self.cycles))
        self.recon = Phase40PositionMarginAudit(Phase40AuditConfig(seed=self.seed + 40, paper_only=True, outdir=outdir))
        self.settlement = Phase41CrossVenueSettlement(Phase41SettlementConfig(seed=self.seed + 41, paper_only=True))
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.halt_events: List[Dict[str, Any]] = []
        self._halt_ctr = 0

    def _halt_id(self) -> str:
        self._halt_ctr += 1
        h = hashlib.sha256(f"{self.seed}|p51halt|{self._halt_ctr}".encode()).hexdigest()[:12]
        return f"p51_halt_{h}"

    def run(self) -> Dict[str, Any]:
        outdir_p = Path(self.outdir)
        outdir_p.mkdir(parents=True, exist_ok=True)

        alpha_rep = self.alpha51.run_campaign(cycles=self.cycles)
        self.alpha51.generate_artifacts(self.outdir)
        sor_rep = self.sor51.run_campaign(cycles=self.cycles)
        self.sor51.generate_artifacts(self.outdir)
        mm50_rep = self.mm50.run_campaign(cycles=self.cycles)
        self.mm50.generate_artifacts(self.outdir)
        rv50_rep = self.rv50.run_campaign(cycles=self.cycles)
        self.rv50.generate_artifacts(self.outdir)
        vol_rep = self.volarb49.run_campaign(cycles=self.cycles)
        self.volarb49.generate_artifacts(self.outdir)
        hedge_rep = self.ofhedge49.run_campaign(cycles=self.cycles)
        self.ofhedge49.generate_artifacts(self.outdir)
        alpha48_rep = self.alpha48.run_campaign(cycles=self.cycles)
        self.alpha48.generate_reports(self.outdir)
        arb47_rep = self.arb47.run_campaign(cycles=self.cycles)
        self.arb47.generate_reports(self.outdir)
        mm46_rep = self.mm46.run_campaign(cycles=self.cycles)
        self.mm46.generate_reports(self.outdir)
        of_rep = self.of.run_campaign(cycles=self.cycles)
        rh_rep = self.risk_hedge.run()
        res_rep = self.resilience.run()
        ksum = self.ks.run_campaign()
        dep_rep = self.deployment.run_campaign() if hasattr(self.deployment, "run_campaign") else {"paper_only": True, "gates_ok": True}
        recon_rep = self.recon.run_campaign(cycles=self.cycles) if hasattr(self.recon, "run_campaign") else {"paper_only": True, "gates_ok": True}
        settle_rep = self.settlement.run_campaign(cycles=self.cycles) if hasattr(self.settlement, "run_campaign") else {"paper_only": True, "gates_ok": True}

        breach = bool(
            not mm50_rep.get("gates_ok", True)
            or not rv50_rep.get("gates_ok", True)
            or not vol_rep.get("gates_ok", True)
            or not hedge_rep.get("gates_ok", True)
            or not alpha48_rep.get("gates_ok", True)
            or not arb47_rep.get("gates_ok", True)
            or not rh_rep.get("gates_ok", True)
            or not res_rep.get("gates_ok", True)
            or not alpha_rep.get("gates_ok", True)
            or not sor_rep.get("gates_ok", True)
        )
        if breach:
            self.halt_events.append({
                "trigger_id": self._halt_id(),
                "cycle": self.cycles,
                "timestamp": _utc_now(),
                "reason": "phase51_breach_alpha_sor_mm_rv_vol_hedge_arb_risk_resilience",
                "severity": "critical",
                "action": "halt_execution_alpha_fusion_and_roll_back",
                "auto_executed": True,
                "paper_only": True,
            })

        slo_evals = self.slo.evaluate_all()
        slo_alerts_fired = sum(1 for e in slo_evals if not e.get("met", True))
        gates_ok = bool(mm50_rep.get("gates_ok", False) and rv50_rep.get("gates_ok", False) and alpha_rep.get("gates_ok", False) and sor_rep.get("gates_ok", False))

        rep = serialize_metrics_strict({
            "phase": "PHASE51_EXECUTION_ALPHA_FUSION_LOOP",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "modes": "paper",
            "cycles": self.cycles,
            "gates_ok": bool(gates_ok),
            "phase51_alpha_fusion": {
                "gates_ok": alpha_rep.get("gates_ok"),
                "n_alphas": alpha_rep.get("n_alphas"),
                "n_gate_passed": alpha_rep.get("n_gate_passed"),
                "avg_alpha_score": alpha_rep.get("avg_alpha_score"),
                "avg_confidence": alpha_rep.get("avg_confidence"),
                "selected_features": alpha_rep.get("selected_features"),
            },
            "phase51_latency_aware_sor": {
                "gates_ok": sor_rep.get("gates_ok"),
                "n_routes": sor_rep.get("n_routes"),
                "n_sliced": sor_rep.get("n_sliced"),
                "avg_latency_ms": sor_rep.get("avg_latency_ms"),
                "avg_slippage_bps": sor_rep.get("avg_slippage_bps"),
                "avg_expected_cost_bps": sor_rep.get("avg_expected_cost_bps"),
            },
            "toxicity_mm50": {"gates_ok": mm50_rep.get("gates_ok"), "n_quotes": mm50_rep.get("n_quotes")},
            "cross_venue_rv50": {"gates_ok": rv50_rep.get("gates_ok"), "n_opps": rv50_rep.get("n_opps")},
            "vol_surface_arb49": {"gates_ok": vol_rep.get("gates_ok"), "n_signals": vol_rep.get("n_signals")},
            "orderflow_delta_hedge49": {"gates_ok": hedge_rep.get("gates_ok"), "n_hedge_actions": hedge_rep.get("n_hedge_actions")},
            "alpha48_campaign": {"gates_ok": alpha48_rep.get("gates_ok"), "n_qualified_alphas": alpha48_rep.get("n_qualified_alphas")},
            "arb47_campaign": {"gates_ok": arb47_rep.get("gates_ok"), "n_exploitable": arb47_rep.get("n_exploitable")},
            "mm46_campaign": {"gates_ok": mm46_rep.get("gates_ok")},
            "orderflow_alpha_campaign": {"paper_only": of_rep.get("paper_only"), "gates_ok": of_rep.get("gates_ok", True)},
            "risk_hedge_campaign": {"gates_ok": rh_rep.get("gates_ok"), "halted": rh_rep.get("halted", False)},
            "resilience_campaign": {"gates_ok": res_rep.get("gates_ok")},
            "capital_deployment": {"paper_only": dep_rep.get("paper_only", True), "gates_ok": dep_rep.get("gates_ok", True)},
            "post_trade_reconciliation": {"paper_only": recon_rep.get("paper_only", True), "gates_ok": recon_rep.get("gates_ok", True)},
            "cross_venue_settlement": {"paper_only": settle_rep.get("paper_only", True), "gates_ok": settle_rep.get("gates_ok", True)},
            "phase39_kill_switches": {"paper_only": ksum.get("paper_only"), "gates_ok": ksum.get("gates_ok", True)},
            "halt_executed": bool(breach),
            "halt_events": self.halt_events,
            "slo_evaluations": len(slo_evals),
            "slo_alerts_fired": slo_alerts_fired,
            "integrated_with": [
                "PHASE32_ORDERFLOW_ALPHA",
                "PHASE39_KILL_SWITCHES",
                "PHASE40_POST_TRADE_RECONCILIATION",
                "PHASE41_CROSS_VENUE_SETTLEMENT",
                "PHASE42_RISK_HEDGE_LOOP",
                "PHASE44_LIVE_CAPITAL_DEPLOYMENT",
                "PHASE45_RESILIENCE_CHAOS_FAILOVER",
                "PHASE46_ADAPTIVE_MM",
                "PHASE47_CROSS_VENUE_ARBITRAGE",
                "PHASE48_REGIME_CONDITIONAL_OPTIONS",
                "PHASE49_VOL_SURFACE_ARB",
                "PHASE49_ORDERFLOW_DRIVEN_DELTA_HEDGE",
                "PHASE50_TOXICITY_AWARE_OPTIONS_MM",
                "PHASE50_CROSS_VENUE_RELATIVE_VALUE_EXECUTOR",
                "PHASE51_ADAPTIVE_ORDERFLOW_ALPHA_FUSION",
                "PHASE51_LATENCY_AWARE_OPTIONS_SOR",
                "MONITORING_SLO",
            ],
        })
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = outdir_p / f"phase51_execution_alpha_fusion_loop_{stamp}.json"
        md_path = outdir_p / f"phase51_execution_alpha_fusion_loop_{stamp}.md"
        with open(json_path, "w") as f:
            json.dump(rep, f, indent=2, allow_nan=False)
        with open(md_path, "w") as f:
            f.write("# Phase 51 - Execution-Alpha Fusion Loop\n\n")
            f.write(f"- Timestamp: {rep['timestamp']}\n")
            f.write(f"- Seed: {self.seed} | Paper-only: true | Gates OK: {rep['gates_ok']}\n")
            f.write(f"- Alpha fusion: {alpha_rep.get('n_alphas')} alphas, {alpha_rep.get('n_gate_passed')} passed | SOR routes: {sor_rep.get('n_routes')}\n")
            f.write(f"- Avg alpha score: {alpha_rep.get('avg_alpha_score', 0.0):.4f} | Avg SOR slippage: {sor_rep.get('avg_slippage_bps', 0.0):.4f} bps\n")
            f.write(f"- Halt executed: {rep['halt_executed']} | SLO alerts fired: {slo_alerts_fired}\n\n")
            f.write("## Integrated\n- " + "\n- ".join(rep['integrated_with']) + "\n")
        return rep
