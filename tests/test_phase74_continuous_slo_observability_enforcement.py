from src.monitoring.phase74_continuous_slo_observability_enforcement_engine import (
    Phase74ContinuousSLOObservabilityEnforcementEngine,
    Phase74ContinuousSLOObservabilityEnforcementConfig,
)


def test_phase74_continuous_slo_observability_enforcement_smoke():
    eng = Phase74ContinuousSLOObservabilityEnforcementEngine(
        Phase74ContinuousSLOObservabilityEnforcementConfig(seed=7471, cycles=40)
    )
    rep = eng.run_continuous_slo_observability_enforcement(cycles=40)
    assert rep["phase"] == "PHASE74_CONTINUOUS_SLO_OBSERVABILITY_ENFORCEMENT_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
