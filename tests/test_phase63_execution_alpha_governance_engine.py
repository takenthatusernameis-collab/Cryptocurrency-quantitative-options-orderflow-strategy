"""Phase 63 tests: Execution Alpha Governance Engine."""
from src.alpha.phase63_execution_alpha_governance_engine import (
    Phase63ExecutionAlphaGovernanceEngine,
    Phase63ExecutionAlphaGovernanceConfig,
)


def test_phase63_execution_alpha_governance_basic():
    cfg = Phase63ExecutionAlphaGovernanceConfig(seed=63060, cycles=40)
    e = Phase63ExecutionAlphaGovernanceEngine(cfg)
    rep = e.enforce_governance(cycles=40)
    assert rep["phase"] == "PHASE63_EXECUTION_ALPHA_GOVERNANCE_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_policies"], int)
    assert isinstance(rep["n_kill_switch_events"], int)


def test_phase63_execution_alpha_governance_artifacts(tmp_path):
    e = Phase63ExecutionAlphaGovernanceEngine(Phase63ExecutionAlphaGovernanceConfig(seed=63160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase63_execution_alpha_governance_finite_and_paper_only():
    e = Phase63ExecutionAlphaGovernanceEngine(Phase63ExecutionAlphaGovernanceConfig(seed=63260, cycles=30))
    rep = e.enforce_governance(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["avg_allowed_allocation"], float)
