from src.execution.phase60_adaptive_execution_intelligence_engine import Phase60AdaptiveExecutionIntelligenceEngine, Phase60AdaptiveExecutionIntelligenceConfig


def test_phase60_adaptive_execution_intelligence_basic():
    cfg = Phase60AdaptiveExecutionIntelligenceConfig(seed=60060, cycles=40)
    e = Phase60AdaptiveExecutionIntelligenceEngine(cfg)
    rep = e.run_intelligence(cycles=40)
    assert rep["phase"] == "PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_routes"], int)
    assert isinstance(rep["avg_execution_quality"], float)


def test_phase60_adaptive_execution_intelligence_artifacts(tmp_path):
    e = Phase60AdaptiveExecutionIntelligenceEngine(Phase60AdaptiveExecutionIntelligenceConfig(seed=60160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase60_adaptive_execution_intelligence_finite_and_paper_only():
    e = Phase60AdaptiveExecutionIntelligenceEngine(Phase60AdaptiveExecutionIntelligenceConfig(seed=60260, cycles=30))
    rep = e.run_intelligence(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_limit_rejects"], int)
    assert isinstance(rep["n_venue_scores"], int)
