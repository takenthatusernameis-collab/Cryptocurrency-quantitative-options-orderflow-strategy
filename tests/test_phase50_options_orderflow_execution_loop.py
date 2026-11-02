from src.integration.phase50_options_orderflow_execution_loop import Phase50OptionsOrderflowExecutionLoop


def test_p50_options_orderflow_execution_loop_paper_only():
    loop = Phase50OptionsOrderflowExecutionLoop(seed=50050, cycles=40)
    rep = loop.run()
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["phase"] == "PHASE50_OPTIONS_ORDERFLOW_EXECUTION_LOOP"
    assert "toxicity_mm50" in rep
    assert "cross_venue_rv50" in rep
