import os

os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase90_live_production_readiness_sor_fragmentation_gamma_inventory_hedging_regime_mm_margin_collateral_liquidation_buffer_stress_autonomous_failover_compliance_post_trade_hardening_loop import (
    Phase90LiveProductionReadinessSorFragmentationGammaInventoryHedgingRegimeMmMarginCollateralLiquidationBufferStressAutonomousFailoverCompliancePostTradeHardeningLoop,
)


def test_phase90_live_production_readiness_sor_fragmentation_gamma_inventory_hedging_regime_mm_margin_collateral_liquidation_buffer_stress_autonomous_failover_compliance_post_trade_hardening_loop_green():
    eng = Phase90LiveProductionReadinessSorFragmentationGammaInventoryHedgingRegimeMmMarginCollateralLiquidationBufferStressAutonomousFailoverCompliancePostTradeHardeningLoop()
    rep = eng.run_live_production_readiness_sor_fragmentation_gamma_inventory_hedging_regime_mm_margin_collateral_liquidation_buffer_stress_autonomous_failover_compliance_post_trade_hardening(cycles=42)
    assert isinstance(rep, dict)
    assert rep.get("ok") is True
    gates = rep.get("gates", {})
    assert gates.get("paper_only_enforced") is True
    assert gates.get("evidence_chain") is True
    assert gates.get("custody_clearing") is True
    assert gates.get("settlement_finality") is True
    assert gates.get("margin_collateral") is True
    assert gates.get("liquidation_buffer_stress_hardening") is True
    assert gates.get("live_readiness") is True
    assert gates.get("post_trade") is True
    assert gates.get("stress_gate") is True
    assert gates.get("autonomous_failover") is True
    assert gates.get("compliance_governance") is True
    assert gates.get("reconciliation_post_trade_attestation") is True
    assert gates.get("orderflow_toxicity_aware") is True
    assert gates.get("cross_venue_sor_routing") is True
    assert gates.get("gamma_dealer_positioning") is True
    assert gates.get("gamma_inventory_hedging_orchestrator") is True
    assert gates.get("options_iv_greeks_surface") is True
    assert gates.get("fragmentation_routing") is True
    assert gates.get("regime_aware_mm_hedging") is True
    assert gates.get("orderflow_aware_execution") is True
    assert gates.get("live_production_readiness") is True
    assert gates.get("finite_numerics") is True
    assert gates.get("no_placeholders") is True
