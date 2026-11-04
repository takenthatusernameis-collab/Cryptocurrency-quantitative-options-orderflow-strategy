from __future__ import annotations

import json
import os
from pathlib import Path


def test_phase100_live_gate_hardening(tmp_path: Path) -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    from src.risk.phase100_live_gate_hardening_cross_margin_finality_adv_liq_ins_fund_sor_toxic_adaptive_frag_regime_shift_gamma_inv_hedge_liq_cross_margin_paper_to_live_gate_quorum_settle_finality_hash_custody_clearing_recon_failover_chaos_compliance_post_trade_stress import (
        Phase100LiveGateHardeningDeepCrossMarginNettingFinalityEdgeCasesAdversarialLiquidationBufferInsuranceFundStressSorOptimalRoutingToxicFlowGuardsAdaptiveFragmentationRegimeShiftGammaInventoryHedgeRegimeAwareLiquidityProvisionCrossMarginPaperToLiveGateAttestationQuorumDefenseInDepthDeterministicCrossVenueSettlementFinalityHashChainPrimeBrokerCustodyClearingReconciliationAutonomousFailoverChaosComplianceGovernancePostTradeDeepeningLoop,
        Phase100Cfg,
    )

    cfg = Phase100Cfg(outdir=str(tmp_path), cycles=24)
    loop = Phase100LiveGateHardeningDeepCrossMarginNettingFinalityEdgeCasesAdversarialLiquidationBufferInsuranceFundStressSorOptimalRoutingToxicFlowGuardsAdaptiveFragmentationRegimeShiftGammaInventoryHedgeRegimeAwareLiquidityProvisionCrossMarginPaperToLiveGateAttestationQuorumDefenseInDepthDeterministicCrossVenueSettlementFinalityHashChainPrimeBrokerCustodyClearingReconciliationAutonomousFailoverChaosComplianceGovernancePostTradeDeepeningLoop(cfg)
    res = loop.run_live_gate_hardening_deep()
    assert res["phase"] == 100
    assert res["paper_only"] is True
    gates = res["gates"]
    assert gates["evidence_chain"] is True
    assert gates["custody_clearing"] is True
    assert gates["settlement/finality"] is True
    assert gates["margin/collateral"] is True
    assert gates["live_readiness"] is True
    assert gates["post_trade"] is True
    assert gates["stress_gate"] is True
    assert gates["autonomous_failover"] is True
    assert gates["compliance_governance"] is True
    assert gates["orderflow_toxicity_aware"] is True
    assert gates["cross_venue_sor_routing"] is True
    assert gates["gamma_dealer_positioning/inventory_hedging"] is True
    assert gates["gamma_inventory_hedging_regime_aware_liquidity_provision_stress_cross_margin"] is True
    assert gates["options_iv_greeks_surface"] is True
    assert gates["regime_aware_mm_hedging"] is True
    assert gates["fragmentation_routing"] is True
    assert gates["finality_settlement_reconciliation_post_trade_attestation"] is True
    assert gates["cross_venue_netting_finality_edge_cases"] is True
    assert gates["liquidation_buffer_stress_adversarial_fragmentation_insurance_fund"] is True
    assert gates["sor_optimal_routing_toxic_flow_guards_adaptive_fragmentation_regime_shift"] is True
    assert gates["paper_to_live_gate_attestation_quorum_defense_in_depth"] is True
    assert gates["deterministic_cross_venue_settlement_finality_hash_chain"] is True
    assert gates["atomic_recon_custody_clearing"] is True
    assert gates["real_time_recon"] is True
    assert gates["slo_hardening"] is True
    assert gates["finite_numerics"] is True
    assert gates["no_placeholders"] is True
    assert gates["custody_clearing_reconciliation"] is True
    assert gates["settlement_finality_edge_stress"] is True
    assert gates["autonomous_failover_compliance_governance"] is True
    assert gates["cross_venue_settlement_netting"] is True
    assert gates["cross_margin_netting_finality_edge_cases"] is True
    assert gates["prime_broker_custody_clearing_reconciliation"] is True
    assert gates["chaos_autonomous_failover_compliance_post_trade"] is True
    # Phase 100 deepening gates.
    assert gates["phase100_deepening"] is True
    assert gates["phase100_cross_margin_netting_finality_edge_cases_deep"] is True
    assert gates["phase100_liquidation_buffer_stress_adversarial_fragmentation_insurance_fund_deep"] is True
    assert gates["phase100_sor_optimal_routing_toxic_flow_guards_adaptive_fragmentation_regime_shift_deep"] is True
    assert gates["phase100_gamma_inventory_hedging_regime_aware_liquidity_provision_stress_cross_margin_deep"] is True
    assert gates["phase100_paper_to_live_gate_attestation_quorum_defense_in_depth_deep"] is True
    assert gates["phase100_deterministic_cross_venue_settlement_finality_hash_chain_deep"] is True
    assert gates["phase100_prime_broker_custody_clearing_reconciliation_deep"] is True
    assert gates["phase100_chaos_autonomous_failover_compliance_post_trade_deep"] is True
    assert gates["all_ok"] is True
    # Composition: Phase 99 gates carried through.
    assert any(k.startswith("p99/") for k in gates)
    outdir = Path(tmp_path) / "phase100_live_gate_hardening_cross_margin_finality_adv_liq_ins_fund_sor_toxic_adaptive_frag_regime_shift_gamma_inv_hedge_liq_cross_margin_paper_to_live_gate_quorum_settle_finality_hash_custody_clearing_recon_failover_chaos_compliance_post_trade_stress"
    assert (outdir / "PHASE100_RES_LATEST.json").exists()
    assert (outdir / "PHASE100_RES_LATEST.md").exists()
    data = json.loads((outdir / "PHASE100_RES_LATEST.json").read_text())
    assert data["phase"] == 100
    assert data["paper_only"] is True
    assert data["gates"]["all_ok"] is True
