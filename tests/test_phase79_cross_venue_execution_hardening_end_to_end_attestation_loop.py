import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.integration.phase79_cross_venue_execution_hardening_end_to_end_attestation_loop import (
    Phase79CrossVenueExecutionHardeningEndToEndAttestationLoop,
    Phase79CrossVenueExecutionHardeningEndToEndAttestationConfig,
)


def test_phase79_cross_venue_execution_hardening_end_to_end_attestation_loop_smoke():
    eng = Phase79CrossVenueExecutionHardeningEndToEndAttestationLoop(
        Phase79CrossVenueExecutionHardeningEndToEndAttestationConfig(seed=7902, cycles=40)
    )
    rep = eng.run_cross_venue_execution_hardening_attestation(cycles=40)
    assert rep["phase"] == "PHASE79_CROSS_VENUE_EXECUTION_HARDENING_END_TO_END_ATTESTATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["cross_venue_hardening_ok"] is True
    assert rep["gates"]["end_to_end_attestation_ok"] is True
    assert rep["gates"]["routing_sor_ok"] is True
    assert rep["gates"]["finality_reconciliation_ok"] is True
    assert rep["counts"]["executions"] > 0
    assert rep["counts"]["attestations"] > 0
    assert rep["counts"]["reconciliations"] > 0
