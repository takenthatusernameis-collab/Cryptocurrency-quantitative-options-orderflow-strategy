from src.settlement.phase73_continuous_attestation_anomaly_detection_engine import (
    Phase73ContinuousAttestationAnomalyDetectionEngine,
    Phase73ContinuousAttestationAnomalyDetectionConfig,
)


def test_phase73_continuous_attestation_anomaly_detection_engine_smoke():
    eng = Phase73ContinuousAttestationAnomalyDetectionEngine(Phase73ContinuousAttestationAnomalyDetectionConfig(seed=7371, cycles=40))
    rep = eng.run_continuous_attestation_anomaly_detection(cycles=40)
    assert rep["phase"] == "PHASE73_CONTINUOUS_ATTESTATION_ANOMALY_DETECTION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
