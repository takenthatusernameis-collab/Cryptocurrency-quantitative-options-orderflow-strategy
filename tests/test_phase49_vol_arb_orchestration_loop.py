from src.integration.phase49_vol_arb_orchestration_loop import Phase49VolArbOrchestrationLoop


def test_p49_orchestration_paper_only_and_gates():
    loop = Phase49VolArbOrchestrationLoop(seed=49049, cycles=5, paper_only=True)
    rep = loop.run()
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert "PHASE49_VOL_SURFACE_ARB" in " ".join(rep["integrated_with"])
    assert "PHASE49_ORDERFLOW_DRIVEN_DELTA_HEDGE" in " ".join(rep["integrated_with"])
    assert rep["phase"] == "PHASE49_VOL_ARB_ORCHESTRATION_LOOP"
