"""Phase 67 tests: Execution Alpha Resilience & Stress Engine."""
from src.alpha.phase67_execution_alpha_resilience_stress_engine import (
    Phase67ExecutionAlphaResilienceStressEngine,
    Phase67ExecutionAlphaResilienceStressConfig,
)


def test_phase67_execution_alpha_resilience_stress_basic():
    cfg = Phase67ExecutionAlphaResilienceStressConfig(seed=67060, cycles=40)
    e = Phase67ExecutionAlphaResilienceStressEngine(cfg)
    rep = e.run_resilience_stress(cycles=40)
    assert rep["phase"] == "PHASE67_EXECUTION_ALPHA_RESILIENCE_STRESS_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_stress_scenarios"], int)
    assert isinstance(rep["n_anomalies"], int)


def test_phase67_execution_alpha_resilience_stress_artifacts(tmp_path):
    e = Phase67ExecutionAlphaResilienceStressEngine(Phase67ExecutionAlphaResilienceStressConfig(seed=67160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase67_execution_alpha_resilience_stress_finite():
    e = Phase67ExecutionAlphaResilienceStressEngine(Phase67ExecutionAlphaResilienceStressConfig(seed=67260, cycles=30))
    rep = e.run_resilience_stress(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["avg_recovery_readiness"], float)
    assert isinstance(rep["resilience_pass_rate"], float)


def test_phase67_execution_alpha_resilience_stress_live_path_gated():
    try:
        Phase67ExecutionAlphaResilienceStressEngine(Phase67ExecutionAlphaResilienceStressConfig(seed=67060, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
