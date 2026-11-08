from src.hedging.phase75_adaptive_toxicity_resilient_post_finality_attribution_closeout_orchestrator import (
    Phase75AdaptiveToxicityResilientPostFinalityAttributionCloseoutOrchestrator,
    Phase75AdaptiveToxicityResilientPostFinalityAttributionCloseoutConfig,
)


def test_phase75_post_finality_attribution_closeout_orchestrator_smoke():
    orch = Phase75AdaptiveToxicityResilientPostFinalityAttributionCloseoutOrchestrator(
        Phase75AdaptiveToxicityResilientPostFinalityAttributionCloseoutConfig(seed=7575, cycles=40)
    )
    rep = orch.run_post_finality_attribution_closeout_orchestration(cycles=40)
    assert rep["phase"] == "PHASE75_ADAPTIVE_TOXICITY_RESILIENT_POST_FINALITY_ATTRIBUTION_CLOSEOUT_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["closeout_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
