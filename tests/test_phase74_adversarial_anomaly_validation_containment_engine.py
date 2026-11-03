from src.settlement.phase74_adversarial_anomaly_validation_containment_engine import (
    Phase74AdversarialAnomalyValidationContainmentEngine,
    Phase74AdversarialAnomalyValidationContainmentConfig,
)


def test_phase74_adversarial_anomaly_validation_containment_engine_smoke():
    eng = Phase74AdversarialAnomalyValidationContainmentEngine(Phase74AdversarialAnomalyValidationContainmentConfig(seed=7473, cycles=40))
    rep = eng.run_adversarial_anomaly_validation_containment(cycles=40)
    assert rep["phase"] == "PHASE74_ADVERSARIAL_ANOMALY_VALIDATION_CONTAINMENT_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
