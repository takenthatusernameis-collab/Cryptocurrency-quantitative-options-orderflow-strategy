import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase82_live_exit_kill_switch_evidence_integrity_hardening_loop import (
    Phase82LiveExitKillSwitchEvidenceIntegrityHardeningLoop,
    Phase82LiveExitKillSwitchEvidenceIntegrityHardeningConfig,
)


def test_phase82_live_exit_kill_switch_evidence_integrity_hardening_loop_smoke():
    eng = Phase82LiveExitKillSwitchEvidenceIntegrityHardeningLoop(
        Phase82LiveExitKillSwitchEvidenceIntegrityHardeningConfig(seed=82039, cycles=50)
    )
    rep = eng.run_live_exit_kill_switch_evidence_integrity_hardening(cycles=50)
    assert rep["phase"] == "PHASE82_LIVE_EXIT_KILL_SWITCH_EVIDENCE_INTEGRITY_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["evidence_chain_ok"] is True
    assert rep["gates"]["attestation_quorum_ok"] is True
    assert rep["gates"]["tamper_evident_ok"] is True
    assert rep["gates"]["manual_reset_enforced"] is True
    assert rep["gates"]["live_exit_hard_gated_paper_only"] is True
