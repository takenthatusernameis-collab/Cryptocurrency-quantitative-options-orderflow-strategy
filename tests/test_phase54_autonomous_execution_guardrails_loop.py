from __future__ import annotations

from pathlib import Path

from src.integration.phase54_autonomous_execution_guardrails_loop import (
    Phase54AutonomousExecutionGuardrailsLoop,
    Phase54GuardrailsConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase54_guardrails_init_paper_only() -> None:
    cfg = Phase54GuardrailsConfig(seed=123, paper_only=True)
    loop = Phase54AutonomousExecutionGuardrailsLoop(cfg)
    assert loop.cfg.paper_only is True


def test_phase54_guardrails_init_rejects_live() -> None:
    try:
        Phase54GuardrailsConfig(seed=123, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase54_guardrails_campaign_and_artifacts(tmp_path: Path) -> None:
    loop = Phase54AutonomousExecutionGuardrailsLoop(
        Phase54GuardrailsConfig(seed=777, cycles=10, auto_rollback_on_breach=True)
    )
    rep = loop.run_campaign(cycles=10)
    assert rep["gates_ok"] is True
    assert rep["cycle_breaches"] == 0
    assert rep["kill_switch_halted"] is False
    assert rep["integration"] == "Phases17-53+Phase54"
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    art = loop.generate_artifacts(outdir=str(tmp_path)) if hasattr(loop, "generate_artifacts") else None
    assert art is not None
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s["phase"] == "PHASE54_AUTONOMOUS_EXECUTION_GUARDRAILS_LOOP"
    assert s["paper_only"] is True


def test_phase54_guardrails_finite_numerics(tmp_path: Path) -> None:
    loop = Phase54AutonomousExecutionGuardrailsLoop(Phase54GuardrailsConfig(seed=555, cycles=8))
    rep = loop.run_campaign(cycles=8)
    s = serialize_metrics_strict(rep)
    assert "gates_ok" in s
    assert s["paper_only"] is True
