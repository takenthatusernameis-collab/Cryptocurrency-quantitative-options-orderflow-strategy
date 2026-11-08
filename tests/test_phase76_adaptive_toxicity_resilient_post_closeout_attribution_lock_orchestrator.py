from src.hedging.phase76_adaptive_toxicity_resilient_post_closeout_attribution_lock_orchestrator import (
    Phase76AdaptiveToxicityResilientPostCloseoutAttributionLockOrchestrator,
    Phase76AdaptiveToxicityResilientPostCloseoutAttributionLockConfig,
)


def test_phase76_post_closeout_attribution_lock_orchestrator_smoke():
    orch = Phase76AdaptiveToxicityResilientPostCloseoutAttributionLockOrchestrator(
        Phase76AdaptiveToxicityResilientPostCloseoutAttributionLockConfig(seed=7676, cycles=40)
    )
    rep = orch.run_post_closeout_attribution_lock_orchestration(cycles=40)
    assert rep["phase"] == "PHASE76_ADAPTIVE_TOXICITY_RESILIENT_POST_CLOSEOUT_ATTRIBUTION_LOCK_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["lock_pass_rate"] >= 0.0
    arts = orch.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
