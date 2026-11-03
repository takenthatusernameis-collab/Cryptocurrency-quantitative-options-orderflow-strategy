"""Phase 67 tests: Adaptive Toxicity-Resilient Recovery Orchestrator."""
from src.hedging.phase67_adaptive_toxicity_resilient_recovery_orchestrator import (
    Phase67AdaptiveToxicityResilientRecoveryOrchestrator,
    Phase67AdaptiveToxicityResilientRecoveryConfig,
)


def test_phase67_adaptive_toxicity_resilient_recovery_basic():
    cfg = Phase67AdaptiveToxicityResilientRecoveryConfig(seed=67160, cycles=40)
    e = Phase67AdaptiveToxicityResilientRecoveryOrchestrator(cfg)
    rep = e.orchestrate_recovery(cycles=40)
    assert rep["phase"] == "PHASE67_ADAPTIVE_TOXICITY_RESILIENT_RECOVERY_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_venue_failovers"], int)
    assert isinstance(rep["n_hedging_recoveries"], int)


def test_phase67_adaptive_toxicity_resilient_recovery_artifacts(tmp_path):
    e = Phase67AdaptiveToxicityResilientRecoveryOrchestrator(Phase67AdaptiveToxicityResilientRecoveryConfig(seed=67260, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase67_adaptive_toxicity_resilient_recovery_finite():
    e = Phase67AdaptiveToxicityResilientRecoveryOrchestrator(Phase67AdaptiveToxicityResilientRecoveryConfig(seed=67360, cycles=30))
    rep = e.orchestrate_recovery(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["avg_failover_readiness"], float)
    assert isinstance(rep["recovery_pass_rate"], float)


def test_phase67_adaptive_toxicity_resilient_recovery_live_path_gated():
    try:
        Phase67AdaptiveToxicityResilientRecoveryOrchestrator(Phase67AdaptiveToxicityResilientRecoveryConfig(seed=67160, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
