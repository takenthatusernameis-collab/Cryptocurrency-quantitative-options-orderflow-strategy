from __future__ import annotations

from pathlib import Path

from src.integration.phase56_autonomous_production_rollout_drills_loop import (
    Phase56AutonomousProductionRolloutDrillsLoop,
    Phase56RolloutConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase56_rollout_init_paper_only() -> None:
    cfg = Phase56RolloutConfig(seed=3)
    loop = Phase56AutonomousProductionRolloutDrillsLoop(cfg)
    assert loop.cfg.paper_only is True


def test_phase56_rollout_rejects_live() -> None:
    try:
        Phase56RolloutConfig(seed=3, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase56_rollout_drills_ok(tmp_path: Path) -> None:
    loop = Phase56AutonomousProductionRolloutDrillsLoop(Phase56RolloutConfig(seed=13))
    rep = loop.run_drills()
    assert rep["phase"] == "PHASE56_AUTONOMOUS_PRODUCTION_ROLLOUT_DRILLS_LOOP"
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["all_health_ok"] is True
    assert rep["auto_rollback_triggered"] is False
    assert rep["composed_phases"] == "17-55"
    assert rep["integration"] == "Phase44+Phase45+Phase54+Phase55"
    art = loop.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    ss = serialize_metrics_strict(rep)
    assert ss["deterministic"] is True


def test_phase56_rollout_drills_rollback_on_breach(tmp_path: Path) -> None:
    loop = Phase56AutonomousProductionRolloutDrillsLoop(Phase56RolloutConfig(seed=17))
    rep = loop.run_drills(health={"connectivity_ok": False, "risk_limits_ok": True, "kill_switch_tested": True, "recon_clean": True, "drift_within_bounds": True, "failover_ready": True})
    assert rep["all_health_ok"] is False
    assert rep["auto_rollback_triggered"] is True
    assert any(s.get("rolled_back") for s in rep["stages"])
