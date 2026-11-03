"""Phase 66 tests: Execution Alpha Audit & Integrity Engine."""
from src.alpha.phase66_execution_alpha_audit_integrity_engine import (
    Phase66ExecutionAlphaAuditIntegrityEngine,
    Phase66ExecutionAlphaAuditIntegrityConfig,
)


def test_phase66_execution_alpha_audit_integrity_basic():
    cfg = Phase66ExecutionAlphaAuditIntegrityConfig(seed=66060, cycles=40)
    e = Phase66ExecutionAlphaAuditIntegrityEngine(cfg)
    rep = e.run_audit_integrity(cycles=40)
    assert rep["phase"] == "PHASE66_EXECUTION_ALPHA_AUDIT_INTEGRITY_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles"] == 40
    assert isinstance(rep["n_audit_trails"], int)
    assert isinstance(rep["n_kill_switch_audits"], int)


def test_phase66_execution_alpha_audit_integrity_artifacts(tmp_path):
    e = Phase66ExecutionAlphaAuditIntegrityEngine(Phase66ExecutionAlphaAuditIntegrityConfig(seed=66160, cycles=20))
    rep = e.generate_artifacts(outdir=str(tmp_path))
    assert rep["gates_ok"] is True
    assert rep["json_path"].endswith(".json")
    assert rep["md_path"].endswith(".md")


def test_phase66_execution_alpha_audit_integrity_finite():
    e = Phase66ExecutionAlphaAuditIntegrityEngine(Phase66ExecutionAlphaAuditIntegrityConfig(seed=66260, cycles=30))
    rep = e.run_audit_integrity(cycles=30)
    assert rep["paper_only"] is True
    assert isinstance(rep["avg_integrity_score"], float)
    assert isinstance(rep["audit_pass_rate"], float)


def test_phase66_execution_alpha_audit_integrity_live_path_gated():
    try:
        Phase66ExecutionAlphaAuditIntegrityEngine(Phase66ExecutionAlphaAuditIntegrityConfig(seed=66060, paper_only=False))
    except ValueError:
        pass
    else:
        raise AssertionError("live path must be hard-gated")
