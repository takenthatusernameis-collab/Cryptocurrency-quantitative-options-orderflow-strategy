import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.integration.phase81_autonomous_cross_venue_margin_collateral_finality_settlement_attestation_hardening_loop import (
    Phase81AutonomousCrossVenueMarginCollateralFinalitySettlementAttestationHardeningLoop,
    Phase81AutonomousCrossVenueMarginCollateralFinalitySettlementAttestationHardeningConfig,
)


def test_phase81_autonomous_cross_venue_margin_collateral_finality_settlement_attestation_hardening_loop_smoke():
    eng = Phase81AutonomousCrossVenueMarginCollateralFinalitySettlementAttestationHardeningLoop(
        Phase81AutonomousCrossVenueMarginCollateralFinalitySettlementAttestationHardeningConfig(seed=81072, cycles=50)
    )
    rep = eng.run_autonomous_cross_venue_margin_collateral_finality_settlement_attestation_hardening(cycles=50)
    assert rep["phase"] == "PHASE81_AUTONOMOUS_CROSS_VENUE_MARGIN_COLLATERAL_FINALITY_SETTLEMENT_ATTESTATION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["margin_enforced"] is True
    assert rep["gates"]["collateral_coverage_enforced"] is True
    assert rep["gates"]["cross_venue_netting_ok"] is True
    assert rep["gates"]["settlement_attestation_ok"] is True
    assert rep["gates"]["finality_enforced"] is True
