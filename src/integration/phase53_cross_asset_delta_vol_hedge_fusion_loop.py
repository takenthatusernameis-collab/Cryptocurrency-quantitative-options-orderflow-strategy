"""
Phase 53: Cross-asset delta-vol hedge fusion loop (crypto options + orderflow).

Compose Phases 17-52 into production-grade fragmentation arb + adaptive
inventory skewing + cross-asset delta-vol hedge fusion. PAPER-ONLY.
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
from src.execution.phase52_realtime_liquidity_allocator import (
    Phase52AllocatorConfig,
    Phase52RealtimeLiquidityAllocator,
)
from src.hedging.phase49_orderflow_driven_delta_hedge import (
    Phase49HedgeConfig,
    Phase49OrderflowDrivenDeltaHedge,
)
from src.integration.phase42_risk_hedge_loop import Loop42Config, Phase42RiskHedgeLoop
from src.integration.phase45_resilience_validation_loop import Phase45ResilienceValidationLoop
from src.liquidity.phase53_fragmentation_arb_engine import (
    Phase53FragmentationArbEngine,
    Phase53FragmentationConfig,
)
from src.marketmaking.phase50_toxicity_aware_options_mm import (
    Phase50MMConfig,
    Phase50ToxicityAwareOptionsMM,
)
from src.marketmaking.phase53_adaptive_inventory_skew_engine import (
    Phase53InventorySkewConfig,
    Phase53AdaptiveInventorySkewEngine,
)
from src.monitoring.slo import SLOMonitor, register_default_slos
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrator,
)
from src.orderflow.phase52_toxicity_resilient_flow_optimizer import (
    Phase52FlowOptimizerConfig,
    Phase52ToxicityResilientFlowOptimizer,
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


class Phase53CrossAssetDeltaVolHedgeFusionLoop:
    """Cross-asset delta-vol hedge fusion loop composing Phases 17-52."""

    def __init__(self, seed: int = 53053, cycles: int = 60, paper_only: bool = True, outdir: str = "research_state") -> None:
        if not isinstance(paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not paper_only:
            raise ValueError("Phase53CrossAssetDeltaVolHedgeFusionLoop: paper_only must remain True (live path hard-gated)")
        self.seed = int(seed)
        self.cycles = int(cycles)
        self.paper_only = True
        self.outdir = outdir

        self.frag = Phase53FragmentationArbEngine(Phase53FragmentationConfig(seed=self.seed + 530, paper_only=True, cycles=self.cycles, outdir=outdir))
        self.skew = Phase53AdaptiveInventorySkewEngine(Phase53InventorySkewConfig(seed=self.seed + 531, paper_only=True, cycles=self.cycles, outdir=outdir))
        self.flow_opt = Phase52ToxicityResilientFlowOptimizer(Phase52FlowOptimizerConfig(seed=self.seed + 52, paper_only=True, cycles=self.cycles, outdir=outdir))
        self.allocator = Phase52RealtimeLiquidityAllocator(Phase52AllocatorConfig(seed=self.seed + 53, paper_only=True, cycles=self.cycles, outdir=outdir))
        self.alpha51 = Phase51AdaptiveOrderflowAlphaFusion(Phase51AlphaFusionConfig(seed=self.seed + 51, paper_only=True, outdir=outdir))
        self.sor51 = Phase51LatencyAwareOptionsSOR(Phase51SORConfig(seed=self.seed + 54, paper_only=True, outdir=outdir))
        self.mm50 = Phase50ToxicityAwareOptionsMM(Phase50MMConfig(seed=self.seed + 50, paper_only=True, outdir=outdir))
        self.rv50 = Phase50CrossVenueRelativeValueExecutor(Phase50RVConfig(seed=self.seed + 55, paper_only=True, outdir=outdir))
        self.volarb49 = Phase49VolSurfaceArbEngine(Phase49VolSurfConfig(seed=self.seed + 49, paper_only=True, outdir=outdir))
        self.ofhedge49 = Phase49OrderflowDrivenDeltaHedge(Phase49HedgeConfig(seed=self.seed + 56, paper_only=True, outdir=outdir))
        self.alpha48 = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=self.seed + 48, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.arb47 = Phase47CrossVenueArbitrageEngine(Phase47Config(seed=self.seed + 47, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.mm46 = Phase46AdaptiveMM(AdaptiveMMConfig(seed=self.seed + 46, paper_only=True, cycles=self.cycles, outdir=self.outdir))
        self.deployment = Phase44LiveCapitalDeployment(seed=self.seed, paper_only=True)
        self.risk_hedge = Phase42RiskHedgeLoop(Loop42Config(seed=self.seed + 42, cycles=self.cycles, paper_only=True, modes="paper"))
        self.resilience = Phase45ResilienceValidationLoop(seed=self.seed + 45, cycles=self.cycles, paper_only=True, outdir=self.outdir)
        self.ks = Phase39KillSwitchesCircuitBreakers(KillSwitchConfig39(seed=self.seed + 39, paper_only=True))
        self.of = OrderflowAlphaIntegrator(OrderflowAlphaIntegrationConfig32(seed=self.seed + 32, paper_only=True, cycles=self.cycles))
        self.recon = Phase40PositionMarginAudit(Phase40AuditConfig(seed=self.seed + 40, paper_only=True))
        self.settlement = Phase41CrossVenueSettlement(Phase41SettlementConfig(seed=self.seed + 41, paper_only=True))
        self.slo = SLOMonitor()
        register_default_slos(self.slo)
        self.halt_events: List[Dict[str, Any]] = []
        self._halt_ctr = 0

    def _halt_id(self) -> str:
        self._halt_ctr += 1
        h = hashlib.sha256(f"{self.seed}|p53halt|{self._halt_ctr}".encode()).hexdigest()[:12]
        return f"p53_halt_{h}"

    def run(self) -> Dict[str, Any]:
        outdir_p = Path(self.outdir)
        outdir_p.mkdir(parents=True, exist_ok=True)

        frag_rep = self.frag.generate_artifacts(self.outdir)
        skew_rep = self.skew.generate_artifacts(self.outdir)
        flow_rep = self.flow_opt.generate_artifacts(self.outdir)
        alloc_rep = self.allocator.generate_artifacts(self.outdir)
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
            not frag_rep.get("gates_ok", True)
            or not skew_rep.get("gates_ok", True)
            or not flow_rep.get("gates_ok", True)
            or not alloc_rep.get("gates_ok", True)
            or not mm50_rep.get("gates_ok", True)
            or not rv50_rep.get("gates_ok", True)
            or not alpha_rep.get("gates_ok", True)
            or not sor_rep.get("gates_ok", True)
            or not rh_rep.get("gates_ok", True)
            or not res_rep.get("gates_ok", True)
        )
        if breach:
            self.halt_events.append({
                "trigger_id": self._halt_id(),
                "cycle": self.cycles,
                "timestamp": _utc_now(),
                "reason": "phase53_breach_fragmentation_skew_flow_alloc_hedge_mm_rv_alpha_risk_resilience",
                "severity": "critical",
                "action": "halt_cross_asset_delta_vol_hedge_fusion_and_roll_back",
                "auto_executed": True,
                "paper_only": True,
            })

        slo_evals = self.slo.evaluate_all()
        slo_alerts_fired = sum(1 for e in slo_evals if not e.get("met", True))
        gates_ok = bool(
            frag_rep.get("gates_ok", False)
            and skew_rep.get("gates_ok", False)
            and flow_rep.get("gates_ok", False)
            and alloc_rep.get("gates_ok", False)
            and mm50_rep.get("gates_ok", False)
            and rv50_rep.get("gates_ok", False)
            and alpha_rep.get("gates_ok", False)
            and sor_rep.get("gates_ok", False)
        )

        rep = serialize_metrics_strict({
            "phase": "PHASE53_CROSS_ASSET_DELTA_VOL_HEDGE_FUSION_LOOP",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "modes": "paper",
            "cycles": self.cycles,
            "gates_ok": bool(gates_ok),
            "phase53_fragmentation_arb": {"gates_ok": frag_rep.get("gates_ok"), "n_opps": frag_rep.get("n_opps"), "avg_basis_bps": frag_rep.get("avg_basis_bps")},
            "phase53_adaptive_inventory_skew": {"gates_ok": skew_rep.get("gates_ok"), "avg_skew_bps": skew_rep.get("avg_skew_bps"), "n_quotes": skew_rep.get("n_quotes")},
            "phase52_flow_optimizer": {"gates_ok": flow_rep.get("gates_ok"), "avg_toxicity": flow_rep.get("avg_toxicity")},
            "phase52_liquidity_allocator": {"gates_ok": alloc_rep.get("gates_ok"), "n_allocations": alloc_rep.get("n_allocations"), "total_alloc_usd": alloc_rep.get("total_alloc_usd")},
            "phase51_alpha_fusion": {"gates_ok": alpha_rep.get("gates_ok"), "n_alphas": alpha_rep.get("n_alphas")},
            "phase51_sor": {"gates_ok": sor_rep.get("gates_ok"), "n_orders": sor_rep.get("n_orders")},
            "phase50_mm": {"gates_ok": mm50_rep.get("gates_ok"), "n_quotes": mm50_rep.get("n_quotes")},
            "phase50_rv": {"gates_ok": rv50_rep.get("gates_ok"), "n_opps": rv50_rep.get("n_opps")},
            "phase49_vol_arb": {"gates_ok": vol_rep.get("gates_ok")},
            "phase49_hedge": {"gates_ok": hedge_rep.get("gates_ok")},
            "phase48_alpha": {"gates_ok": alpha48_rep.get("gates_ok")},
            "phase47_arb": {"gates_ok": arb47_rep.get("gates_ok")},
            "phase46_mm": {"gates_ok": mm46_rep.get("gates_ok")},
            "risk_hedge": {"gates_ok": rh_rep.get("gates_ok")},
            "resilience": {"gates_ok": res_rep.get("gates_ok")},
            "kill_switches": {"halted": bool(ksum.get("halted", False))},
            "deployment": {"paper_only": bool(dep_rep.get("paper_only", True)), "gates_ok": bool(dep_rep.get("gates_ok", True))},
            "recon": {"gates_ok": bool(recon_rep.get("gates_ok", True))},
            "settlement": {"gates_ok": bool(settle_rep.get("gates_ok", True))},
            "slo": {"alerts_fired": int(slo_alerts_fired), "evaluations": len(slo_evals)},
            "halt_events": self.halt_events,
            "halt_count": len(self.halt_events),
            "integration": "Phases17-52+Phase53",
            "domain_focus": "crypto_options_orderflow_liquidity_fragmentation_adaptive_inventory_skew_cross_asset_delta_vol_hedge_fusion",
        })

        def _walk(v: Any, p: str, bad: List[str]) -> None:
            if isinstance(v, dict):
                for k, val in v.items():
                    _walk(val, f"{p}/{k}", bad)
            elif isinstance(v, (list, tuple)):
                for i, val in enumerate(v):
                    _walk(val, f"{p}[{i}]", bad)
            elif isinstance(v, float) and not isinstance(v, bool):
                if not isfinite(v):
                    bad.append(p)

        bad: List[str] = []
        _walk(rep, "$", bad)
        if bad:
            raise ValueError(f"Non-finite in phase53 loop report: {bad[:10]}")

        out = Path(self.outdir)
        out.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jpath = out / f"PHASE53_CROSS_ASSET_DELTA_VOL_HEDGE_FUSION_LOOP_{ts}.json"
        mpath = out / f"PHASE53_CROSS_ASSET_DELTA_VOL_HEDGE_FUSION_LOOP_{ts}.md"
        with jpath.open("w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, sort_keys=True)
        with mpath.open("w", encoding="utf-8") as f:
            f.write(f"# PHASE53 Cross-Asset Delta-Vol Hedge Fusion Loop\n\n- Timestamp: {rep['timestamp']}\n- Gates OK: {rep['gates_ok']}\n- Fragmentation Opps: {rep['phase53_fragmentation_arb']['n_opps']}\n- Avg |Skew| (bps): {rep['phase53_adaptive_inventory_skew']['avg_skew_bps']:.4f}\n- Halts: {rep['halt_count']}\n- SLO Alerts: {rep['slo']['alerts_fired']}\n")
        rep["json_path"] = str(jpath)
        rep["md_path"] = str(mpath)
        return rep
