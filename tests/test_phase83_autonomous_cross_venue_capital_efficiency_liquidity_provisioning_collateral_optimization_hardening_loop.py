import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.capital.phase83_autonomous_cross_venue_capital_efficiency_liquidity_provisioning_collateral_optimization_hardening_loop import (
    Phase83AutonomousCrossVenueCapitalEfficiencyLiquidityProvisioningCollateralOptimizationLoop,
    Phase83AutonomousCrossVenueCapitalEfficiencyLiquidityProvisioningCollateralOptimizationConfig,
)


def test_phase83_capital_efficiency_liquidity_collateral_smoke():
    eng = Phase83AutonomousCrossVenueCapitalEfficiencyLiquidityProvisioningCollateralOptimizationLoop(
        Phase83AutonomousCrossVenueCapitalEfficiencyLiquidityProvisioningCollateralOptimizationConfig(seed=83011, cycles=40)
    )
    rep = eng.run_autonomous_cross_venue_capital_efficiency_liquidity_provisioning_collateral_optimization(cycles=40)
    assert rep["phase"] == "PHASE83_AUTONOMOUS_CROSS_VENUE_CAPITAL_EFFICIENCY_LIQUIDITY_PROVISIONING_COLLATERAL_OPTIMIZATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["capital_efficiency_target_met"] is True
    assert rep["gates"]["liquidity_provisioning_ok"] is True
    assert rep["gates"]["collateral_optimization_ok"] is True
    assert rep["gates"]["margin_collateral_reconciliation_ok"] is True
    assert rep["gates"]["risk_fusion_ok"] is True
    assert rep["gates"]["kill_switch_ok"] is True
