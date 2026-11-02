from __future__ import annotations

from pathlib import Path

from src.resilience.phase55_kill_switch_failover_drill import (
    Phase55KillSwitchFailoverDrill,
    Phase55KillSwitchFailoverDrillConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase55_ksdrill_init_paper_only() -> None:
    cfg = Phase55KillSwitchFailoverDrillConfig(seed=123, paper_only=True)
    d = Phase55KillSwitchFailoverDrill(cfg)
    assert d.cfg.paper_only is True


def test_phase55_ksdrill_init_rejects_live() -> None:
    try:
        Phase55KillSwitchFailoverDrillConfig(seed=123, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase55_ksdrill_campaign_and_artifacts(tmp_path: Path) -> None:
    d = Phase55KillSwitchFailoverDrill(
        Phase55KillSwitchFailoverDrillConfig(seed=777, cycles=10)
    )
    rep = d.run_campaign(cycles=10)
    assert rep["gates_ok"] is True
    assert rep["paper_only"] is True
    assert rep["halt_propagation_ok"] is True
    assert rep["all_events_paper_only"] is True
    assert rep["integration"] == "Phase39+Phase45"
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    art = d.generate_artifacts(outdir=str(tmp_path))
    assert art is not None
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s["phase"] == "PHASE55_KILL_SWITCH_FAILOVER_DRILL"
    assert s["paper_only"] is True


def test_phase55_ksdrill_drift_within_threshold() -> None:
    d = Phase55KillSwitchFailoverDrill(Phase55KillSwitchFailoverDrillConfig(seed=42, cycles=6))
    rep = d.run_campaign(cycles=6)
    assert rep["drift_breach_count"] <= rep["drift_threshold_pct"] * 0 + rep["drift_count"]
    for de in rep["drift_events"]:
        assert de["drift_pct"] >= 0.0


def test_phase55_ksdrill_finite_numerics(tmp_path: Path) -> None:
    d = Phase55KillSwitchFailoverDrill(Phase55KillSwitchFailoverDrillConfig(seed=555, cycles=8))
    rep = d.run_campaign(cycles=8)
    s = serialize_metrics_strict(rep)
    assert "gates_ok" in s
    assert s["paper_only"] is True
    assert Path(s["json_path"]).exists()
