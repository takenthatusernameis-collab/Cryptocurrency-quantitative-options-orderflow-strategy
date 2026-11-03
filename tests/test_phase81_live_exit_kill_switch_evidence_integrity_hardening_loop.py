import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase81_live_exit_kill_switch_evidence_integrity_hardening_loop import (
    Phase81LiveExitKillSwitchEvidenceIntegrityHardeningLoop,
    Phase81LiveExitKillSwitchEvidenceIntegrityHardeningConfig,
)


def test_phase81_live_exit_kill_switch_evidence_integrity_hardening_loop_smoke():
    eng = Phase81LiveExitKillSwitchEvidenceIntegrityHardeningLoop(
        Phase81LiveExitKillSwitchEvidenceIntegrityHardeningConfig(seed=81039, cycles=50)
    )
    rep = eng.run_live_exit_kill_switch_evidence_integrity_hardening(cycles=50)
    assert rep["phase"] == "PHASE81_LIVE_EXIT_KILL_SWITCH_EVIDENCE_INTEGRITY_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["tamper_evident_chain_ok"] is True
    assert rep["gates"]["attestation_integrity_ok"] is True
    assert rep["gates"]["tamper_detection_ok"] is True
    assert rep["gates"]["live_exit_attested"] is True
