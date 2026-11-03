from src.risk.phase75_cross_venue_options_execution_quality_tca_engine import (
    Phase75CrossVenueOptionsExecutionQualityTCAEngine,
    Phase75CrossVenueOptionsExecutionQualityTCAConfig,
)


def test_phase75_cross_venue_options_execution_quality_tca_engine_smoke():
    eng = Phase75CrossVenueOptionsExecutionQualityTCAEngine(
        Phase75CrossVenueOptionsExecutionQualityTCAConfig(seed=7571, cycles=40)
    )
    rep = eng.run_cross_venue_options_execution_quality_tca(cycles=40)
    assert rep["phase"] == "PHASE75_CROSS_VENUE_OPTIONS_EXECUTION_QUALITY_TCA_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
