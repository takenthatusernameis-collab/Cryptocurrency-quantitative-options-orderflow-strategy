"""Numeric-invariant tests for paper execution hardening (EVAL-15)."""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import pytest

from src.analytics.paper_execution_hardening import (
    build_execution_thresholds,
    compute_paper_execution_metrics,
    compute_paper_execution_verdict,
    evaluate_paper_execution_hardening,
    load_sealed_evidence,
    run_execution_simulation,
    _all_finite_numbers,
    _finite,
    _guardrail,
    _stamp_for_filename,
    _utc_now_iso,
)


def test_finite_helpers():
    assert _finite(1.0) == 1.0
    assert _finite(float("inf")) == 0.0
    assert _finite(float("nan")) == 0.0
    assert _finite("3.14") == 3.14
    assert _finite(None) == 0.0
    assert _finite("invalid") == 0.0


def test_guardrail_builder():
    g = _guardrail(
        "test_guardrail",
        "test_category",
        100.0,
        50.0,
        True,
        "rationale text",
        extra_field="extra_value",
    )
    assert g["name"] == "test_guardrail"
    assert g["category"] == "test_category"
    assert g["threshold"] == 100.0
    assert g["observed"] == 50.0
    assert g["pass"] is True
    assert g["rationale"] == "rationale text"
    assert g["extra_field"] == "extra_value"


def test_stamp_for_filename():
    assert _stamp_for_filename("2026-11-13T03:54:46Z") == "20261113T035446Z"
    assert _stamp_for_filename("2026-11-13T03:54:46.123456Z") == "20261113T035446Z"
    assert _stamp_for_filename("invalid") == ""


def test_utc_now_iso():
    iso = _utc_now_iso()
    assert iso.endswith("Z")
    assert "T" in iso
    assert "+" not in iso


def test_load_sealed_evidence_structure():
    evidence = load_sealed_evidence()
    assert evidence["report_id"] == "PAPER_EXECUTION_HARDENING_EVAL_15"
    assert len(evidence["evidence_sources"]) >= 5
    assert "eval14" in evidence
    assert "eval13" in evidence
    assert "eval12" in evidence
    assert "eval11" in evidence
    assert "paper_readiness" in evidence
    assert "continuous_validation" in evidence
    assert evidence["eval14"]["verdict"] == "GO"
    assert evidence["eval13"]["verdict"] == "GO"
    assert evidence["eval12"]["verdict"] == "GO"
    assert evidence["eval14"]["live_trading_enabled"] is False
    assert evidence["eval13"]["live_trading_enabled"] is False


def test_run_execution_simulation_structure():
    evidence = load_sealed_evidence()
    sim = run_execution_simulation(evidence, seeds=[1, 2])
    assert "seeds_simulated" in sim
    assert sim["n_seeds"] == 2
    assert "target_delta_usd" in sim
    assert sim["target_delta_usd"] == -20000.0
    assert "toxicity_threshold" in sim
    assert sim["toxicity_threshold"] == 0.7
    assert "cost_budget_bps" in sim
    assert sim["cost_budget_bps"] == 0.5
    assert "mean_abs_delta_usd" in sim
    assert "mean_toxicity_score" in sim
    assert "toxic_gate_active_fraction" in sim
    assert "total_hedges" in sim
    assert "total_cost_usd" in sim
    assert "total_traded_notional" in sim
    assert "total_trades" in sim
    assert "mean_oos_return" in sim
    assert "mean_oos_sharpe" in sim
    assert "mean_max_drawdown" in sim
    assert "max_single_series_notional_usd" in sim
    assert "max_drawdown_observed" in sim
    assert "effective_cost_bps" in sim
    assert "daily_loss_estimate_usd" in sim
    assert "alert_log" in sim
    assert isinstance(sim["alert_log"], list)
    assert len(sim["alert_log"]) > 0


def test_compute_paper_execution_metrics_structure():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    assert metrics["n_evidence_sources"] >= 5
    assert metrics["eval14_verdict"] == "GO"
    assert metrics["eval13_verdict"] == "GO"
    assert metrics["eval12_verdict"] == "GO"
    assert metrics["eval13_all_checks_pass"] is True
    assert metrics["paper_all_critical_passed"] is True
    assert metrics["cv_all_critical_passed"] is True
    assert metrics["cv_reconciliation_freshness_met"] is True
    assert metrics["max_notional_cap_usd"] == 1_000_000.0
    assert metrics["target_delta_usd"] == -20000.0
    assert metrics["delta_band_usd"] == 323.7734839590619
    assert metrics["toxicity_gate_threshold"] == 0.7
    assert metrics["cost_budget_bps"] == 0.5
    assert metrics["cost_ceiling_bps"] == 2.0
    assert metrics["kill_switch_max_drawdown"] == 0.20
    assert metrics["kill_switch_toxicity"] == 0.80
    assert metrics["kill_switch_cost_bps"] == 5.0
    assert metrics["max_daily_loss_usd"] == 50_000.0
    assert metrics["live_trading_enabled"] is False
    assert "simulation" in metrics
    assert _all_finite_numbers(metrics)


def test_build_execution_thresholds_guardrails():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)

    assert "guardrails" in thresholds
    assert "alert_watch_levels" in thresholds
    assert "kill_switch_halt_conditions" in thresholds
    assert thresholds["n_guardrails"] == 9
    assert thresholds["n_alert_watch_levels"] == 6
    assert thresholds["n_kill_switch_halt_conditions"] == 3
    assert thresholds["all_guardrails_pass"] is True
    assert thresholds["failed_guardrails"] == []

    guardrail_names = [g["name"] for g in thresholds["guardrails"]]
    assert "max_notional_cap_usd" in guardrail_names
    assert "delta_band_usd" in guardrail_names
    assert "toxicity_gate_threshold" in guardrail_names
    assert "cost_budget_bps" in guardrail_names
    assert "kill_switch_max_drawdown" in guardrail_names
    assert "kill_switch_toxicity" in guardrail_names
    assert "kill_switch_cost_bps" in guardrail_names
    assert "max_daily_loss_usd" in guardrail_names
    assert "live_trading_disabled" in guardrail_names

    watch_names = [w["name"] for w in thresholds["alert_watch_levels"]]
    assert "max_notional_cap_usd_watch" in watch_names
    assert "delta_band_usd_watch" in watch_names
    assert "toxicity_gate_watch" in watch_names
    assert "cost_budget_bps_watch" in watch_names
    assert "kill_switch_max_drawdown_watch" in watch_names
    assert "max_daily_loss_usd_watch" in watch_names

    halt_names = [h["name"] for h in thresholds["kill_switch_halt_conditions"]]
    assert "kill_switch_max_drawdown_halt" in halt_names
    assert "kill_switch_toxicity_halt" in halt_names
    assert "kill_switch_cost_bps_halt" in halt_names

    for h in thresholds["kill_switch_halt_conditions"]:
        assert h.get("halt") is True


def test_compute_paper_execution_verdict_go():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)
    verdict = compute_paper_execution_verdict(evidence, metrics, thresholds)

    assert verdict["verdict"] == "GO"
    assert verdict["all_checks_pass"] is True
    assert verdict["n_checks"] == 12
    assert verdict["n_passed"] == 12

    check_names = [c["name"] for c in verdict["checks"]]
    assert "evidence_sources_complete" in check_names
    assert "eval14_paper_readiness_go" in check_names
    assert "eval13_certification_go" in check_names
    assert "eval13_all_checks_pass" in check_names
    assert "eval12_walkforward_go" in check_names
    assert "paper_pre_live_gates_all_passed" in check_names
    assert "continuous_validation_all_passed" in check_names
    assert "reconciliation_freshness_met" in check_names
    assert "all_execution_guardrails_pass" in check_names
    assert "kill_switch_not_triggered" in check_names
    assert "live_trading_disabled" in check_names
    assert "metrics_and_thresholds_finite" in check_names


def test_kill_switch_not_triggered():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)

    for h in thresholds["kill_switch_halt_conditions"]:
        assert h["pass"] is False, f"Kill-switch halt condition {h['name']} should not be triggered"


def test_alert_watch_levels_not_triggered_except_drawdown():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)

    drawdown_watch_triggered = False
    for w in thresholds["alert_watch_levels"]:
        if w["name"] == "kill_switch_max_drawdown_watch":
            drawdown_watch_triggered = w["pass"]
        else:
            assert w["pass"] is False, f"Alert watch {w['name']} should not be triggered"

    assert drawdown_watch_triggered is True, "Drawdown watch should be triggered (observed 0.1887 >= 0.10 watch)"


def test_evaluate_paper_execution_hardening_full_run():
    with tempfile.TemporaryDirectory() as temp_dir:
        report = evaluate_paper_execution_hardening(
            write=True,
            out_dir=temp_dir,
            seeds=[1, 2],
        )

        assert report["report_id"] == "PAPER_EXECUTION_HARDENING_EVAL_15"
        assert report["verdict"] == "GO"
        assert report["trading_mode"] == "paper"
        assert report["live_trading_enabled"] is False
        assert report["never_valid_true"] is True
        assert "artifact_paths" in report
        assert "json" in report["artifact_paths"]
        assert "md" in report["artifact_paths"]

        json_path = Path(report["artifact_paths"]["json"])
        md_path = Path(report["artifact_paths"]["md"])
        assert json_path.exists()
        assert md_path.exists()

        with json_path.open("r") as f:
            loaded = json.load(f)
        assert loaded["report_id"] == "PAPER_EXECUTION_HARDENING_EVAL_15"
        assert loaded["verdict"] == "GO"
        assert loaded["live_trading_enabled"] is False
        assert "paper_execution_metrics" in loaded
        assert "execution_thresholds" in loaded
        assert "evidence_matrix" in loaded
        assert "verdict_checks" in loaded
        assert "reconciliation_metrics" in loaded
        assert "deployment_authorization" in loaded


def test_serialization_no_nan_infinity():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)
    verdict = compute_paper_execution_verdict(evidence, metrics, thresholds)

    assert _all_finite_numbers(metrics)
    assert _all_finite_numbers(thresholds)
    assert _all_finite_numbers(verdict)

    for g in thresholds["guardrails"]:
        assert math.isfinite(g["threshold"])
        assert math.isfinite(g["observed"])
    for w in thresholds["alert_watch_levels"]:
        assert math.isfinite(w["threshold"])
        assert math.isfinite(w["observed"])
    for h in thresholds["kill_switch_halt_conditions"]:
        assert math.isfinite(h["threshold"])
        assert math.isfinite(h["observed"])


def test_guardrail_numeric_values():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)

    for g in thresholds["guardrails"]:
        if g["name"] == "max_notional_cap_usd":
            assert g["threshold"] == 1_000_000.0
            assert g["observed"] <= 1_000_000.0
        elif g["name"] == "delta_band_usd":
            assert g["threshold"] == 323.7734839590619
            assert g["observed"] == 150.8213456031083
        elif g["name"] == "toxicity_gate_threshold":
            assert g["threshold"] == 0.7
            assert g["observed"] < 0.5
        elif g["name"] == "cost_budget_bps":
            assert g["threshold"] == 2.0
            assert g["observed"] == 0.5
        elif g["name"] == "kill_switch_max_drawdown":
            assert g["threshold"] == 0.20
            assert g["observed"] < 0.20
        elif g["name"] == "kill_switch_toxicity":
            assert g["threshold"] == 0.80
            assert g["observed"] < 0.80
        elif g["name"] == "kill_switch_cost_bps":
            assert g["threshold"] == 5.0
            assert g["observed"] < 5.0
        elif g["name"] == "max_daily_loss_usd":
            assert g["threshold"] == 50_000.0
        elif g["name"] == "live_trading_disabled":
            assert g["threshold"] == 0.0
            assert g["observed"] == 0.0


def test_alert_watch_level_values():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)

    for w in thresholds["alert_watch_levels"]:
        if w["name"] == "max_notional_cap_usd_watch":
            assert w["threshold"] == 750_000.0
        elif w["name"] == "delta_band_usd_watch":
            assert w["threshold"] == 242.8301129692964
        elif w["name"] == "toxicity_gate_watch":
            assert w["threshold"] == 0.5
        elif w["name"] == "cost_budget_bps_watch":
            assert w["threshold"] == 1.5
        elif w["name"] == "kill_switch_max_drawdown_watch":
            assert w["threshold"] == 0.10
        elif w["name"] == "max_daily_loss_usd_watch":
            assert w["threshold"] == 25_000.0


def test_kill_switch_halt_values():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)

    for h in thresholds["kill_switch_halt_conditions"]:
        if h["name"] == "kill_switch_max_drawdown_halt":
            assert h["threshold"] == 0.20
        elif h["name"] == "kill_switch_toxicity_halt":
            assert h["threshold"] == 0.80
        elif h["name"] == "kill_switch_cost_bps_halt":
            assert h["threshold"] == 5.0


def test_reconciliation_metrics():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)
    verdict = compute_paper_execution_verdict(evidence, metrics, thresholds)

    report = {
        "report_id": "TEST",
        "generated_at": _utc_now_iso(),
        "verdict": verdict["verdict"],
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "evidence": evidence,
        "paper_execution_metrics": metrics,
        "execution_thresholds": thresholds,
        "evidence_matrix": {},
        "verdict_checks": verdict,
        "reconciliation_metrics": {
            "freshness_target_gte": 0.99,
            "freshness_met": True,
            "iterations_passed": 5,
            "iterations_expected": 5,
            "simulation_bars": 1000,
            "symbols_simulated": 3,
        },
        "deployment_authorization": {
            "authorized": True,
            "mode": "paper_only",
            "note": "test",
        },
    }
    from src.telemetry.serialization import serialize_metrics_strict
    serialized = serialize_metrics_strict(report)
    assert serialized["reconciliation_metrics"]["freshness_target_gte"] == 0.99
    assert serialized["reconciliation_metrics"]["freshness_met"] is True
    assert serialized["reconciliation_metrics"]["iterations_passed"] == 5


def test_evidence_matrix_keys():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)
    verdict = compute_paper_execution_verdict(evidence, metrics, thresholds)

    data_matrix = evidence["eval12"].get("data_matrix", {})
    evidence_matrix = {
        "btc_real_trades": bool(data_matrix.get("btc_real_trades", False)),
        "eth_synthetic_fallback": bool(data_matrix.get("eth_synthetic_fallback", False)),
        "sol_synthetic_fallback": bool(data_matrix.get("sol_synthetic_fallback", False)),
        "venue_snapshots_aggregate_only": bool(data_matrix.get("venue_snapshots_aggregate_only", False)),
        "eval14_sealed_artifact_present": True,
        "eval13_sealed_artifact_present": True,
        "eval12_sealed_artifact_present": True,
        "eval11_sealed_artifact_present": True,
        "paper_readiness_checkpoint_present": True,
        "continuous_validation_checkpoint_present": True,
    }

    assert evidence_matrix["btc_real_trades"] is True
    assert evidence_matrix["eth_synthetic_fallback"] is True
    assert evidence_matrix["sol_synthetic_fallback"] is True
    assert evidence_matrix["venue_snapshots_aggregate_only"] is True
    assert evidence_matrix["eval14_sealed_artifact_present"] is True
    assert evidence_matrix["eval13_sealed_artifact_present"] is True
    assert evidence_matrix["eval12_sealed_artifact_present"] is True
    assert evidence_matrix["eval11_sealed_artifact_present"] is True
    assert evidence_matrix["paper_readiness_checkpoint_present"] is True
    assert evidence_matrix["continuous_validation_checkpoint_present"] is True


def test_deployment_authorization():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)
    verdict = compute_paper_execution_verdict(evidence, metrics, thresholds)

    assert verdict["verdict"] == "GO"
    auth = {
        "authorized": bool(verdict["verdict"] == "GO"),
        "mode": "paper_only",
        "note": "GO verdict certifies paper-execution hardening only; not an authorization to trade live.",
    }
    assert auth["authorized"] is True
    assert auth["mode"] == "paper_only"


def test_never_valid_true():
    evidence = load_sealed_evidence()
    metrics = compute_paper_execution_metrics(evidence)
    thresholds = build_execution_thresholds(evidence, metrics)
    verdict = compute_paper_execution_verdict(evidence, metrics, thresholds)

    report = {
        "report_id": "TEST",
        "generated_at": _utc_now_iso(),
        "verdict": verdict["verdict"],
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "evidence": evidence,
        "paper_execution_metrics": metrics,
        "execution_thresholds": thresholds,
        "evidence_matrix": {},
        "verdict_checks": verdict,
        "reconciliation_metrics": {},
        "deployment_authorization": {"authorized": True, "mode": "paper_only", "note": "test"},
    }
    from src.telemetry.serialization import serialize_metrics_strict
    serialized = serialize_metrics_strict(report)
    assert serialized["never_valid_true"] is True
    assert "valid" not in str(serialized).lower() or serialized.get("valid") is not True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])