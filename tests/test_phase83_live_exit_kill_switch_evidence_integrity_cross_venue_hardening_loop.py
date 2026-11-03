import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase83_live_exit_kill_switch_evidence_integrity_cross_venue_hardening_loop import (
    Phase83LiveExitKillSwitchEvidenceIntegrityCrossVenueLoop,
    Phase83LiveExitKillSwitchEvidenceIntegrityCrossVenueConfig,
)


def test_phase83_live_exit_kill_switch_evidence_integrity_cross_venue_smoke():
    eng = Phase83LiveExitKillSwitchEvidenceIntegrityCrossVenueLoop(
        Phase83LiveExitKillSwitchEvidenceIntegrityCrossVenueConfig(seed=83039, cycles=40)
    )
    rep = eng.run_live_exit_kill_switch_evidence_integrity_cross_venue(cycles=40)
    assert rep["phase"] == "PHASE83_LIVE_EXIT_KILL_SWITCH_EVIDENCE_INTEGRITY_CROSS_VENUE_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["evidence_chain_ok"] is True
    assert rep["gates"]["attestation_quorum_ok"] is True
    assert rep["gates"]["tamper_evident_ok"] is True
    assert rep["gates"]["manual_reset_enforced"] is True
    assert rep["gates"]["live_exit_hard_gated_paper_only"] is True
    assert rep["gates"]["cross_venue_kill_switch_ok"] is True
