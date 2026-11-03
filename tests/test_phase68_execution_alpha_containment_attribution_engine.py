from src.alpha.phase68_execution_alpha_containment_attribution_engine import (
    Phase68ExecutionAlphaContainmentAttributionEngine,
    Phase68ExecutionAlphaContainmentAttributionConfig,
)


def test_phase68_containment_attribution_deterministic_artifacts():
    eng = Phase68ExecutionAlphaContainmentAttributionEngine(
        Phase68ExecutionAlphaContainmentAttributionConfig(seed=68060, cycles=40)
    )
    rep = eng.run_containment_attribution(cycles=40)
    assert rep["phase"] == "PHASE68_EXECUTION_ALPHA_CONTAINMENT_ATTRIBUTION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_containments"] >= 0
    assert rep["n_recovery_verifications"] > 0
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
