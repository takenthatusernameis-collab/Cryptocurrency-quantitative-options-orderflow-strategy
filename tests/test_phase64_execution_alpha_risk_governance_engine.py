"""Phase 64 tests: Execution Alpha Risk Governance Engine."""
from src.alpha.phase64_execution_alpha_risk_governance_engine import (
    Phase64ExecutionAlphaRiskGovernanceEngine,
    Phase64ExecutionAlphaRiskGovernanceConfig,
)


def test_phase64_execution_alpha_risk_governance_basic():
    cfg = Phase64ExecutionAlphaRiskGovernanceConfig(seed=64060, cycles=40)
    e = Phase64ExecutionAlphaRiskGovernanceEngine(cfg)
    rep = e.enforce_risk_governance(cycles=40)
    assert rep["phase"] == "PHASE64_EXECUTION_ALPHA_RISK_GOVERNANCE_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_policies"], int)
    assert isinstance(rep["n_kill_switch_events"], int)


def test_phase64_execution_alpha_risk_governance_artifacts(tmp_path):
    e = Phase64ExecutionAlphaRiskGovernanceEngine(Phase64ExecutionAlphaRiskGovernanceConfig(seed=64160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase64_execution_alpha_risk_governance_var_es_finite():
    e = Phase64ExecutionAlphaRiskGovernanceEngine(Phase64ExecutionAlphaRiskGovernanceConfig(seed=64260, cycles=30))
    rep = e.enforce_risk_governance(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["var_95_pct"], float)
    assert isinstance(rep["es_975_pct"], float)


def test_phase64_execution_alpha_risk_governance_live_path_gated():
    try:
        Phase64ExecutionAlphaRiskGovernanceEngine(Phase64ExecutionAlphaRiskGovernanceConfig(seed=64060, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
