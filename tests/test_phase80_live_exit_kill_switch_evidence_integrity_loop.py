import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.risk.phase80_live_exit_kill_switch_evidence_integrity_loop import (
    Phase80LiveExitKillSwitchEvidenceIntegrityLoop,
    Phase80LiveExitKillSwitchEvidenceIntegrityConfig,
)


def test_phase80_live_exit_kill_switch_evidence_integrity_loop_smoke():
    eng = Phase80LiveExitKillSwitchEvidenceIntegrityLoop(
        Phase80LiveExitKillSwitchEvidenceIntegrityConfig(seed=80039, cycles=40)
    )
    rep = eng.run_live_exit_kill_switch_evidence_integrity(cycles=40)
    assert rep["phase"] == "PHASE80_LIVE_EXIT_KILL_SWITCH_EVIDENCE_INTEGRITY_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["kill_switch_enabled"] is True
    assert rep["gates"]["live_exit_enforced"] is True
    assert rep["gates"]["evidence_chain_integrity_ok"] is True
    assert rep["gates"]["attestation_quorum_ok"] is True
    assert rep["gates"]["tamper_evident_audit_ok"] is True
    assert rep["gates"]["trigger_provenance_ok"] is True
