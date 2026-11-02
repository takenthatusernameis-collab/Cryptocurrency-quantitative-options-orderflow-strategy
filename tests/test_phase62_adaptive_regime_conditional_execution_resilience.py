from src.hedging.phase62_adaptive_regime_conditional_execution_resilience import (
    Phase62AdaptiveRegimeConditionalExecutionResilience,
    Phase62AdaptiveRegimeConditionalResilienceConfig,
)


def test_phase62_adaptive_regime_conditional_resilience_basic():
    cfg = Phase62AdaptiveRegimeConditionalResilienceConfig(seed=62061, cycles=40)
    e = Phase62AdaptiveRegimeConditionalExecutionResilience(cfg)
    rep = e.run_resilience(cycles=40)
    assert rep["phase"] == "PHASE62_ADAPTIVE_REGIME_CONDITIONAL_EXECUTION_RESILIENCE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_params"], int)


def test_phase62_adaptive_regime_conditional_resilience_artifacts(tmp_path):
    e = Phase62AdaptiveRegimeConditionalExecutionResilience(Phase62AdaptiveRegimeConditionalResilienceConfig(seed=62161, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase62_adaptive_regime_conditional_resilience_finite_and_paper_only():
    e = Phase62AdaptiveRegimeConditionalExecutionResilience(Phase62AdaptiveRegimeConditionalResilienceConfig(seed=62261, cycles=30))
    rep = e.run_resilience(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_adjustments"], int)
    assert isinstance(rep["n_guardrails"], int)
