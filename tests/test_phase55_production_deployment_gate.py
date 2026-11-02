from __future__ import annotations

from pathlib import Path

from src.deployment.phase55_production_deployment_gate import (
    Phase55DeploymentGateConfig,
    Phase55ProductionDeploymentGate,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase55_deploygate_init_paper_only() -> None:
    cfg = Phase55DeploymentGateConfig(seed=123, paper_only=True)
    g = Phase55ProductionDeploymentGate(cfg)
    assert g.cfg.paper_only is True


def test_phase55_deploygate_init_rejects_live() -> None:
    try:
        Phase55DeploymentGateConfig(seed=123, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase55_deploygate_campaign_and_artifacts(tmp_path: Path) -> None:
    g = Phase55ProductionDeploymentGate(
        Phase55DeploymentGateConfig(seed=777)
    )
    rep = g.run_campaign(cycles=5, state={
        "connectivity_ok": True,
        "risk_limits_ok": True,
        "compliance_ok": True,
        "drift_within_bounds": True,
        "recon_clean": True,
        "auto_recovery_ready": True,
        "equity": 150000.0,
        "drawdown_pct": 0.02,
    })
    assert rep["gates_ok"] is True
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["paper_to_live_hard_gate_tested"] is True
    assert rep["kill_switch_circuit_test_ok"] is True
    assert rep["integration"] == "Phase20+Phase39+Phase40"
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    art = g.generate_artifacts(outdir=str(tmp_path))
    assert art is not None
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s["phase"] == "PHASE55_PRODUCTION_DEPLOYMENT_GATE"
    assert s["paper_only"] is True


def test_phase55_deploygate_blocks_live_and_bad_state() -> None:
    g = Phase55ProductionDeploymentGate(Phase55DeploymentGateConfig(seed=42))
    rep_bad = g.run_campaign(cycles=3, state={
        "connectivity_ok": False,
        "risk_limits_ok": True,
        "compliance_ok": True,
        "drift_within_bounds": True,
        "recon_clean": True,
        "auto_recovery_ready": True,
        "equity": 50000.0,
        "drawdown_pct": 0.02,
    })
    assert rep_bad["gates_ok"] is False
    assert len(rep_bad["blocked_reasons"]) > 0
    assert rep_bad["live_allowed"] is False


def test_phase55_deploygate_finite_numerics(tmp_path: Path) -> None:
    g = Phase55ProductionDeploymentGate(Phase55DeploymentGateConfig(seed=555))
    rep = g.run_campaign(cycles=4, state={
        "connectivity_ok": True, "risk_limits_ok": True, "compliance_ok": True,
        "drift_within_bounds": True, "recon_clean": True, "auto_recovery_ready": True,
        "equity": 200000.0, "drawdown_pct": 0.03,
    })
    s = serialize_metrics_strict(rep)
    assert "gates_ok" in s
    assert s["paper_only"] is True
    assert Path(s["json_path"]).exists()
