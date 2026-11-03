from src.alpha.phase70_execution_alpha_autonomous_recovery_engine import (
    Phase70ExecutionAlphaAutonomousRecoveryEngine,
    Phase70ExecutionAlphaAutonomousRecoveryConfig,
)


def test_phase70_autonomous_recovery_engine_smoke():
    eng = Phase70ExecutionAlphaAutonomousRecoveryEngine(Phase70ExecutionAlphaAutonomousRecoveryConfig(seed=7070, cycles=40))
    rep = eng.run_autonomous_recovery(cycles=40)
    assert rep["phase"] == "PHASE70_EXECUTION_ALPHA_AUTONOMOUS_RECOVERY_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["recovery_pass_rate"] >= 0.0
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
