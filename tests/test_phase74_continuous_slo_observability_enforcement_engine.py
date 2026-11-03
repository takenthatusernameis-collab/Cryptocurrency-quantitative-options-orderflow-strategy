from src.risk.phase74_continuous_slo_observability_enforcement_engine import (
    Phase74ContinuousSloObservabilityEnforcementEngine,
    Phase74ContinuousSloObservabilityEnforcementConfig,
)


def test_phase74_continuous_slo_observability_enforcement_engine_smoke():
    eng = Phase74ContinuousSloObservabilityEnforcementEngine(Phase74ContinuousSloObservabilityEnforcementConfig(seed=7472, cycles=40))
    rep = eng.run_continuous_slo_observability_enforcement(cycles=40)
    assert rep["phase"] == "PHASE74_CONTINUOUS_SLO_OBSERVABILITY_ENFORCEMENT_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
