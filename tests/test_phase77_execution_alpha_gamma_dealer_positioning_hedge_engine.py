from src.alpha.phase77_execution_alpha_gamma_dealer_positioning_hedge_engine import (
    Phase77ExecutionAlphaGammaDealerPositioningHedgeEngine,
    Phase77ExecutionAlphaGammaDealerPositioningHedgeConfig,
)


def test_phase77_execution_alpha_gamma_dealer_positioning_hedge_engine_smoke():
    eng = Phase77ExecutionAlphaGammaDealerPositioningHedgeEngine(
        Phase77ExecutionAlphaGammaDealerPositioningHedgeConfig(seed=7701, cycles=40)
    )
    rep = eng.run_gamma_dealer_positioning_hedge(cycles=40)
    assert rep["phase"] == "PHASE77_EXECUTION_ALPHA_GAMMA_DEALER_POSITIONING_HEDGE_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
