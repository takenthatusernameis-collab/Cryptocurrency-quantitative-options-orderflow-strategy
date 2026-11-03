from src.alpha.phase76_execution_alpha_production_go_live_certification_engine import (
    Phase76ExecutionAlphaProductionGoLiveCertificationEngine,
    Phase76ExecutionAlphaProductionGoLiveCertificationConfig,
)


def test_phase76_execution_alpha_production_go_live_certification_engine_smoke():
    eng = Phase76ExecutionAlphaProductionGoLiveCertificationEngine(
        Phase76ExecutionAlphaProductionGoLiveCertificationConfig(seed=7670, cycles=40)
    )
    rep = eng.run_production_go_live_certification(cycles=40)
    assert rep["phase"] == "PHASE76_EXECUTION_ALPHA_PRODUCTION_GO_LIVE_CERTIFICATION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
