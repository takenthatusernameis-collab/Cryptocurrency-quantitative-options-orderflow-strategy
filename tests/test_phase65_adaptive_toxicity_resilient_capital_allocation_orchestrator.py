"""Phase 65 tests: Adaptive Toxicity-Resilient Capital Allocation Orchestrator."""
from src.hedging.phase65_adaptive_toxicity_resilient_capital_allocation_orchestrator import (
    Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator,
    Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig,
)


def test_phase65_adaptive_toxicity_resilient_capital_allocation_basic():
    cfg = Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(seed=65061, cycles=40)
    o = Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator(cfg)
    rep = o.orchestrate_capital_allocation(cycles=40)
    assert rep["phase"] == "PHASE65_ADAPTIVE_TOXICITY_RESILIENT_CAPITAL_ALLOCATION_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_capital_allocations"], int)
    assert isinstance(rep["n_failovers"], int)


def test_phase65_adaptive_toxicity_resilient_capital_allocation_artifacts(tmp_path):
    o = Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator(
        Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(seed=65161, cycles=20)
    )
    rep = o.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase65_adaptive_toxicity_resilient_capital_allocation_finite_and_paper_only():
    o = Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator(
        Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(seed=65261, cycles=30)
    )
    rep = o.orchestrate_capital_allocation(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["alloc_allowed_rate"], float)


def test_phase65_adaptive_toxicity_resilient_capital_allocation_live_path_gated():
    try:
        Phase65AdaptiveToxicityResilientCapitalAllocationOrchestrator(
            Phase65AdaptiveToxicityResilientCapitalAllocationOrchestratorConfig(seed=65061, paper_only=False)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
