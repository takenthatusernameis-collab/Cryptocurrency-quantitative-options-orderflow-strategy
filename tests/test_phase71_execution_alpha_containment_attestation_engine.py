from src.alpha.phase71_execution_alpha_containment_attestation_engine import (
    Phase71ExecutionAlphaContainmentAttestationEngine,
    Phase71ExecutionAlphaContainmentAttestationConfig,
)


def test_phase71_containment_attestation_engine_smoke():
    eng = Phase71ExecutionAlphaContainmentAttestationEngine(Phase71ExecutionAlphaContainmentAttestationConfig(seed=7170, cycles=40))
    rep = eng.run_containment_attestation(cycles=40)
    assert rep["phase"] == "PHASE71_EXECUTION_ALPHA_CONTAINMENT_ATTESTATION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["containment_attestation_pass_rate"] >= 0.0
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
