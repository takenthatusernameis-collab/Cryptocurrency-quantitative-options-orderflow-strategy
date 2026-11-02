from src.execution.phase58_adaptive_options_smart_order_router import Phase58AdaptiveOptionsSmartOrderRouter, Phase58AdaptiveOptionsSORConfig


def test_phase58_adaptive_options_smart_order_router_basic():
    cfg = Phase58AdaptiveOptionsSORConfig(seed=58059, cycles=40)
    r = Phase58AdaptiveOptionsSmartOrderRouter(cfg)
    rep = r.route_adaptive(cycles=40)
    assert rep["phase"] == "PHASE58_ADAPTIVE_OPTIONS_SMART_ORDER_ROUTER"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["avg_route_score"], float)
    assert isinstance(rep["avg_fill_pred"], float)


def test_phase58_adaptive_options_smart_order_router_artifacts(tmp_path):
    r = Phase58AdaptiveOptionsSmartOrderRouter(Phase58AdaptiveOptionsSORConfig(seed=58159, cycles=20))
    rep = r.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")
