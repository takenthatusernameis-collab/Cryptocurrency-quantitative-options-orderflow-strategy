from src.integration.phase51_execution_alpha_fusion_loop import Phase51ExecutionAlphaFusionLoop


def test_p51_execution_alpha_fusion_loop_paper_only_and_gates():
    loop = Phase51ExecutionAlphaFusionLoop(seed=51051, cycles=40)
    rep = loop.run()
    assert rep["paper_only"] is True
    assert rep["phase"] == "PHASE51_EXECUTION_ALPHA_FUSION_LOOP"
    assert rep["gates_ok"] is True
    assert "phase51_alpha_fusion" in rep
    assert "phase51_latency_aware_sor" in rep
    assert rep["halt_executed"] in (True, False)


def test_p51_execution_alpha_fusion_loop_composition():
    loop = Phase51ExecutionAlphaFusionLoop(seed=99, cycles=30)
    rep = loop.run()
    assert rep["phase51_alpha_fusion"]["n_alphas"] == 30
    assert rep["phase51_latency_aware_sor"]["n_routes"] == 30
    assert rep["toxicity_mm50"]["gates_ok"] is True
    assert rep["cross_venue_rv50"]["gates_ok"] is True
    assert rep["vol_surface_arb49"]["gates_ok"] is True
    assert rep["orderflow_delta_hedge49"]["gates_ok"] is True
    assert rep["alpha48_campaign"]["gates_ok"] is True
    assert rep["arb47_campaign"]["gates_ok"] is True
    assert rep["mm46_campaign"]["gates_ok"] is True
    assert rep["risk_hedge_campaign"]["gates_ok"] is True
    assert rep["resilience_campaign"]["gates_ok"] is True
    assert rep["phase39_kill_switches"]["gates_ok"] is True
    assert rep["capital_deployment"]["paper_only"] is True
    assert rep["post_trade_reconciliation"]["paper_only"] is True
    assert rep["cross_venue_settlement"]["paper_only"] is True


def test_p51_execution_alpha_fusion_loop_artifacts():
    loop = Phase51ExecutionAlphaFusionLoop(seed=5, cycles=20)
    rep = loop.run()
    import json

    json.dumps(rep, allow_nan=False)
    assert len(rep["halt_events"]) >= 0
    assert rep["slo_evaluations"] >= 0
    assert len(rep["integrated_with"]) >= 10


def test_p51_execution_alpha_fusion_loop_halt_on_breach_monotonic():
    loop = Phase51ExecutionAlphaFusionLoop(seed=4, cycles=25)
    rep1 = loop.run()
    rep2 = loop.run()
    assert rep1["phase"] == rep2["phase"] == "PHASE51_EXECUTION_ALPHA_FUSION_LOOP"
    assert rep1["paper_only"] is True and rep2["paper_only"] is True
