from __future__ import annotations

from pathlib import Path

from src.execution.phase55_cross_venue_orderflow_execution_validator import (
    Phase55CrossVenueOrderflowExecutionValidator,
    Phase55ExecutionValidationConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase55_execval_init_paper_only() -> None:
    cfg = Phase55ExecutionValidationConfig(seed=123, paper_only=True)
    v = Phase55CrossVenueOrderflowExecutionValidator(cfg)
    assert v.cfg.paper_only is True


def test_phase55_execval_init_rejects_live() -> None:
    try:
        Phase55ExecutionValidationConfig(seed=123, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase55_execval_campaign_and_artifacts(tmp_path: Path) -> None:
    v = Phase55CrossVenueOrderflowExecutionValidator(
        Phase55ExecutionValidationConfig(seed=777, cycles=10)
    )
    rep = v.run_campaign(cycles=10)
    assert rep["gates_ok"] is True
    assert rep["fill_rate_vs_model_ok"] is True
    assert rep["slippage_tca_reconciliation_ok"] is True
    assert rep["per_venue_latency_scoring_ok"] is True
    assert rep["toxicity_adjusted_quality_ok"] is True
    assert rep["venue_gates_ok"] is True
    assert rep["paper_only"] is True
    assert rep["integration"] == "Phase51+Phase32+Phase52"
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    art = v.generate_artifacts(outdir=str(tmp_path))
    assert art is not None
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s["phase"] == "PHASE55_CROSS_VENUE_ORDERFLOW_EXECUTION_VALIDATOR"
    assert s["paper_only"] is True


def test_phase55_execval_finite_numerics(tmp_path: Path) -> None:
    v = Phase55CrossVenueOrderflowExecutionValidator(Phase55ExecutionValidationConfig(seed=555, cycles=8))
    rep = v.run_campaign(cycles=8)
    s = serialize_metrics_strict(rep)
    assert "gates_ok" in s
    assert s["paper_only"] is True
    assert Path(s["json_path"]).exists()


def test_phase55_execval_venue_summaries_finite() -> None:
    v = Phase55CrossVenueOrderflowExecutionValidator(Phase55ExecutionValidationConfig(seed=42, cycles=6))
    rep = v.run_campaign(cycles=6)
    for venue, summ in rep["venue_summaries"].items():
        assert summ["fill_rate_vs_model"] >= 0.0
        assert summ["avg_slippage_bps"] >= 0.0
        assert summ["avg_latency_ms"] >= 0.0
        assert summ["avg_toxicity"] >= 0.0
        assert 0.0 <= summ["avg_quality_score"] <= 1.0
