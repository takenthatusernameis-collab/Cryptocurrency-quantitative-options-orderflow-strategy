from src.hedging.phase59_adaptive_cross_asset_hedge_fusion import Phase59AdaptiveCrossAssetHedgeFusion, Phase59AdaptiveCrossAssetHedgeConfig


def test_phase59_adaptive_cross_asset_hedge_fusion_basic():
    cfg = Phase59AdaptiveCrossAssetHedgeConfig(seed=59060, cycles=40)
    h = Phase59AdaptiveCrossAssetHedgeFusion(cfg)
    rep = h.run_hedge_fusion(cycles=40)
    assert rep["phase"] == "PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_hedges"], int)
    assert isinstance(rep["avg_latency_ms"], float)


def test_phase59_adaptive_cross_asset_hedge_fusion_artifacts(tmp_path):
    h = Phase59AdaptiveCrossAssetHedgeFusion(Phase59AdaptiveCrossAssetHedgeConfig(seed=59160, cycles=20))
    rep = h.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase59_adaptive_cross_asset_hedge_fusion_limits_and_paper_only():
    h = Phase59AdaptiveCrossAssetHedgeFusion(Phase59AdaptiveCrossAssetHedgeConfig(seed=59260, cycles=30))
    rep = h.run_hedge_fusion(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_limit_clips"], int)
    assert isinstance(rep["n_regime_high"], int)
