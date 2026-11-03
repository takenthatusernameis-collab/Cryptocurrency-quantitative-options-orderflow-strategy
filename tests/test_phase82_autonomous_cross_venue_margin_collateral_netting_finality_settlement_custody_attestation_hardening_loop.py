import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.integration.phase82_autonomous_cross_venue_margin_collateral_netting_finality_settlement_custody_attestation_hardening_loop import (
    Phase82AutonomousCrossVenueMarginCollateralNettingFinalitySettlementCustodyAttestationHardeningLoop,
    Phase82AutonomousCrossVenueMarginCollateralNettingFinalitySettlementCustodyAttestationHardeningConfig,
)


def test_phase82_autonomous_cross_venue_margin_collateral_netting_finality_settlement_custody_attestation_hardening_loop_smoke():
    eng = Phase82AutonomousCrossVenueMarginCollateralNettingFinalitySettlementCustodyAttestationHardeningLoop(
        Phase82AutonomousCrossVenueMarginCollateralNettingFinalitySettlementCustodyAttestationHardeningConfig(seed=82072, cycles=50)
    )
    rep = eng.run_autonomous_cross_venue_margin_collateral_netting_finality_settlement_custody_attestation_hardening(cycles=50)
    assert rep["phase"] == "PHASE82_AUTONOMOUS_CROSS_VENUE_MARGIN_COLLATERAL_NETTING_FINALITY_SETTLEMENT_CUSTODY_ATTESTATION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["margin_enforced"] is True
    assert rep["gates"]["collateral_coverage_enforced"] is True
    assert rep["gates"]["cross_venue_netting_ok"] is True
    assert rep["gates"]["settlement_attestation_ok"] is True
    assert rep["gates"]["finality_enforced"] is True
    assert rep["gates"]["custody_attestation_ok"] is True
