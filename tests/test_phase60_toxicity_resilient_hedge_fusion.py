from src.hedging.phase60_toxicity_resilient_hedge_fusion import Phase60ToxicityResilientHedgeFusion, Phase60ToxicityResilientHedgeConfig


def test_phase60_toxicity_resilient_hedge_basic():
    cfg = Phase60ToxicityResilientHedgeConfig(seed=60061, cycles=40)
    e = Phase60ToxicityResilientHedgeFusion(cfg)
    rep = e.run_hedge_fusion(cycles=40)
    assert rep["phase"] == "PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_hedges"], int)
    assert isinstance(rep["n_adjustments"], int)


def test_phase60_toxicity_resilient_hedge_artifacts(tmp_path):
    e = Phase60ToxicityResilientHedgeFusion(Phase60ToxicityResilientHedgeConfig(seed=60161, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase60_toxicity_resilient_hedge_finite_and_paper_only():
    e = Phase60ToxicityResilientHedgeFusion(Phase60ToxicityResilientHedgeConfig(seed=60261, cycles=30))
    rep = e.run_hedge_fusion(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_limit_clips"], int)
    assert isinstance(rep["n_regime_high"], int)
