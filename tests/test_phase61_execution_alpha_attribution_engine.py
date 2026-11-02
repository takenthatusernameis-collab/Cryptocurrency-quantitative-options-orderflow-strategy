from src.alpha.phase61_execution_alpha_attribution_engine import (
    Phase61ExecutionAlphaAttributionEngine,
    Phase61ExecutionAlphaAttributionConfig,
)


def test_phase61_execution_alpha_attribution_basic():
    cfg = Phase61ExecutionAlphaAttributionConfig(seed=61060, cycles=40)
    e = Phase61ExecutionAlphaAttributionEngine(cfg)
    rep = e.run_attribution(cycles=40)
    assert rep["phase"] == "PHASE61_EXECUTION_ALPHA_ATTRIBUTION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_attribution"], int)
    assert isinstance(rep["sharpe"], float)
    assert isinstance(rep["information_ratio"], float)


def test_phase61_execution_alpha_attribution_artifacts(tmp_path):
    e = Phase61ExecutionAlphaAttributionEngine(Phase61ExecutionAlphaAttributionConfig(seed=61160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase61_execution_alpha_attribution_finite_and_paper_only():
    e = Phase61ExecutionAlphaAttributionEngine(Phase61ExecutionAlphaAttributionConfig(seed=61260, cycles=30))
    rep = e.run_attribution(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_venue_pnl"], int)
    assert isinstance(rep["n_strategy_pnl"], int)
    assert isinstance(rep["n_regime_pnl"], int)
    assert isinstance(rep["n_signal_pnl"], int)
    assert isinstance(rep["n_sharpe_ir"], int)
