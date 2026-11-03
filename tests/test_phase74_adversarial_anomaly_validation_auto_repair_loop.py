from src.integration.phase74_autonomous_adversarial_anomaly_validation_auto_repair_loop import (
    Phase74AutonomousAdversarialAnomalyValidationAutoRepairLoop,
    Phase74AutonomousAdversarialAnomalyValidationAutoRepairLoopConfig,
)


def test_phase74_adversarial_anomaly_validation_auto_repair_loop_smoke():
    eng = Phase74AutonomousAdversarialAnomalyValidationAutoRepairLoop(
        Phase74AutonomousAdversarialAnomalyValidationAutoRepairLoopConfig(seed=7472, cycles=40)
    )
    rep = eng.run_adversarial_anomaly_validation_auto_repair_loop(cycles=40)
    assert rep["phase"] == "PHASE74_AUTONOMOUS_ADVERSARIAL_ANOMALY_VALIDATION_AUTO_REPAIR_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
