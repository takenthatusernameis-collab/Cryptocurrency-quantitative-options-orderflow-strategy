from src.hedging.phase61_adaptive_regime_switching_hedge_orchestrator import (
    Phase61AdaptiveRegimeSwitchingHedgeOrchestrator,
    Phase61AdaptiveRegimeSwitchingHedgeConfig,
)


def test_phase61_adaptive_regime_switching_hedge_basic():
    cfg = Phase61AdaptiveRegimeSwitchingHedgeConfig(seed=61061, cycles=40)
    o = Phase61AdaptiveRegimeSwitchingHedgeOrchestrator(cfg)
    rep = o.run_orchestration(cycles=40)
    assert rep["phase"] == "PHASE61_ADAPTIVE_REGIME_SWITCHING_HEDGE_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_hedges"], int)
    assert isinstance(rep["n_switches"], int)


def test_phase61_adaptive_regime_switching_hedge_artifacts(tmp_path):
    o = Phase61AdaptiveRegimeSwitchingHedgeOrchestrator(Phase61AdaptiveRegimeSwitchingHedgeConfig(seed=61161, cycles=20))
    rep = o.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase61_adaptive_regime_switching_hedge_finite_and_paper_only():
    o = Phase61AdaptiveRegimeSwitchingHedgeOrchestrator(Phase61AdaptiveRegimeSwitchingHedgeConfig(seed=61261, cycles=30))
    rep = o.run_orchestration(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["n_limit_clips"], int)
    assert isinstance(rep["n_regime_high"], int)
    assert isinstance(rep["n_regime_elevated"], int)
    assert isinstance(rep["n_regime_normal"], int)
