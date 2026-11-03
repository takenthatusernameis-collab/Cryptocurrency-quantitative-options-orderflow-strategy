"""Phase 66 tests: Adaptive Toxicity-Resilient Capital Rebalance Orchestrator."""
from src.hedging.phase66_adaptive_toxicity_resilient_capital_rebalance_orchestrator import (
    Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator,
    Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig,
)


def test_phase66_adaptive_toxicity_resilient_capital_rebalance_basic():
    cfg = Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig(seed=66061, cycles=40)
    e = Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator(cfg)
    rep = e.orchestrate_capital_rebalance(cycles=40)
    assert rep["phase"] == "PHASE66_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_REBALANCE_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_rebalance_triggers"], int)
    assert isinstance(rep["n_rebalance_actions"], int)


def test_phase66_adaptive_toxicity_resilient_capital_rebalance_artifacts(tmp_path):
    e = Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator(
        Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig(seed=66161, cycles=20)
    )
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase66_adaptive_toxicity_resilient_capital_rebalance_metrics_finite():
    e = Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator(
        Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig(seed=66261, cycles=30)
    )
    rep = e.orchestrate_capital_rebalance(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["rebalance_trigger_rate"], float)
    assert isinstance(rep["rebalance_cap_pct"], float)


def test_phase66_adaptive_toxicity_resilient_capital_rebalance_live_path_gated():
    try:
        Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestrator(
            Phase66AdaptiveToxicityResilientCapitalRebalanceOrchestratorConfig(seed=66061, paper_only=False)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
