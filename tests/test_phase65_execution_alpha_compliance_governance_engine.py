"""Phase 65 tests: Execution Alpha Compliance Governance Engine."""
from src.alpha.phase65_execution_alpha_compliance_governance_engine import (
    Phase65ExecutionAlphaComplianceGovernanceEngine,
    Phase65ExecutionAlphaComplianceGovernanceConfig,
)


def test_phase65_execution_alpha_compliance_governance_basic():
    cfg = Phase65ExecutionAlphaComplianceGovernanceConfig(seed=65060, cycles=40)
    e = Phase65ExecutionAlphaComplianceGovernanceEngine(cfg)
    rep = e.enforce_compliance_governance(cycles=40)
    assert rep["phase"] == "PHASE65_EXECUTION_ALPHA_COMPLIANCE_GOVERNANCE_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_attestations"], int)
    assert isinstance(rep["n_kill_switch_events"], int)


def test_phase65_execution_alpha_compliance_governance_artifacts(tmp_path):
    e = Phase65ExecutionAlphaComplianceGovernanceEngine(Phase65ExecutionAlphaComplianceGovernanceConfig(seed=65160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase65_execution_alpha_compliance_governance_regulatory_cap_finite():
    e = Phase65ExecutionAlphaComplianceGovernanceEngine(Phase65ExecutionAlphaComplianceGovernanceConfig(seed=65260, cycles=30))
    rep = e.enforce_compliance_governance(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["regulatory_cap_pct"], float)
    assert isinstance(rep["avg_allowed_allocation"], float)


def test_phase65_execution_alpha_compliance_governance_live_path_gated():
    try:
        Phase65ExecutionAlphaComplianceGovernanceEngine(Phase65ExecutionAlphaComplianceGovernanceConfig(seed=65060, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
