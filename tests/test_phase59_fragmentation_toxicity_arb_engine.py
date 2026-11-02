from src.liquidity.phase59_fragmentation_toxicity_arb_engine import Phase59FragmentationToxicityArbEngine, Phase59FragmentationToxicityArbConfig


def test_phase59_fragmentation_toxicity_arb_basic():
    cfg = Phase59FragmentationToxicityArbConfig(seed=59059, cycles=40)
    e = Phase59FragmentationToxicityArbEngine(cfg)
    rep = e.run_arb(cycles=40)
    assert rep["phase"] == "PHASE59_FRAGMENTATION_TOXICITY_ARB_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_opportunities"], int)
    assert isinstance(rep["avg_edge_bps"], float)


def test_phase59_fragmentation_toxicity_arb_artifacts(tmp_path):
    e = Phase59FragmentationToxicityArbEngine(Phase59FragmentationToxicityArbConfig(seed=59159, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase59_fragmentation_toxicity_arb_finite_and_paper_only():
    e = Phase59FragmentationToxicityArbEngine(Phase59FragmentationToxicityArbConfig(seed=59259, cycles=30))
    rep = e.run_arb(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_filters"], int)
    assert isinstance(rep["n_venue_quarantines"], int)
