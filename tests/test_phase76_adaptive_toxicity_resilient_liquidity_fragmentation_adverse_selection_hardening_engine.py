from src.hedging.phase76_adaptive_toxicity_resilient_liquidity_fragmentation_adverse_selection_hardening_engine import (
    Phase76AdaptiveToxicityResilientLiquidityFragmentationAdverseSelectionHardeningEngine,
    Phase76AdaptiveToxicityResilientLiquidityFragmentationAdverseSelectionHardeningConfig,
)


def test_phase76_adaptive_toxicity_resilient_liquidity_fragmentation_adverse_selection_hardening_engine_smoke():
    eng = Phase76AdaptiveToxicityResilientLiquidityFragmentationAdverseSelectionHardeningEngine(
        Phase76AdaptiveToxicityResilientLiquidityFragmentationAdverseSelectionHardeningConfig(seed=7671, cycles=40)
    )
    rep = eng.run_liquidity_fragmentation_adverse_selection_hardening(cycles=40)
    assert rep["phase"] == "PHASE76_ADAPTIVE_TOXICITY_RESILIENT_LIQUIDITY_FRAGMENTATION_ADVERSE_SELECTION_HARDENING_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
