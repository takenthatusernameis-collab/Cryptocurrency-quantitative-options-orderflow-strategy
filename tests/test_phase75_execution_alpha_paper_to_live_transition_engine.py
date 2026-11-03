from src.alpha.phase75_execution_alpha_paper_to_live_transition_engine import (
    Phase75ExecutionAlphaPaperToLiveTransitionEngine,
    Phase75ExecutionAlphaPaperToLiveTransitionConfig,
)


def test_phase75_execution_alpha_paper_to_live_transition_engine_smoke():
    eng = Phase75ExecutionAlphaPaperToLiveTransitionEngine(
        Phase75ExecutionAlphaPaperToLiveTransitionConfig(seed=7570, cycles=40)
    )
    rep = eng.run_paper_to_live_transition_gates(cycles=40)
    assert rep["phase"] == "PHASE75_EXECUTION_ALPHA_PAPER_TO_LIVE_TRANSITION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
