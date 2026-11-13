"""Numeric-invariant tests for src/analytics/paper_deployment_readiness.py (EVAL-14)."""

from __future__ import annotations

import copy
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from src.analytics.paper_deployment_readiness import (
    REPORT_ID,
    build_deployment_thresholds,
    compute_paper_readiness_metrics,
    compute_paper_readiness_verdict,
    evaluate_paper_deployment_readiness,
    load_sealed_evidence,
)


def _drop_timestamps(obj: object) -> object:
    if isinstance(obj, dict):
        return {k: _drop_timestamps(v) for k, v in obj.items() if k != "generated_at"}
    if isinstance(obj, list):
        return [_drop_timestamps(v) for v in obj]
    return obj


def _assert_no_nonfinite(obj: object, path: str = "$") -> None:
    if isinstance(obj, float):
        assert math.isfinite(obj), f"non-finite float at {path}: {obj!r}"
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _assert_no_nonfinite(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _assert_no_nonfinite(v, f"{path}[{i}]")


def test_paper_readiness_runs_and_certifies_go() -> None:
    report = evaluate_paper_deployment_readiness(write=False)
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] == "GO"
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["never_valid_true"] is True
    assert report != {"valid": True}
    assert "evidence" in report
    assert "paper_readiness_metrics" in report
    assert "deployment_thresholds" in report
    assert "evidence_matrix" in report
    assert "verdict_checks" in report
    assert "deployment_authorization" in report
    assert report["deployment_authorization"]["mode"] == "paper_only"
    assert report["verdict_checks"]["all_checks_pass"] is True
    assert report["verdict_checks"]["verdict"] == "GO"
    assert report["verdict_checks"]["n_passed"] == report["verdict_checks"]["n_checks"]
    assert len(report["evidence"]["evidence_sources"]) >= 1
    assert report["evidence_matrix"]["eval13_sealed_artifact_present"] is True
    assert report["evidence_matrix"]["eval12_sealed_artifact_present"] is True
    assert report["evidence_matrix"]["paper_readiness_checkpoint_present"] is True
    assert report["evidence_matrix"]["continuous_validation_checkpoint_present"] is True
    _assert_no_nonfinite(report)


def test_determinism_after_timestamp_normalization() -> None:
    first = evaluate_paper_deployment_readiness(write=False)
    second = evaluate_paper_deployment_readiness(write=False)
    first.pop("generated_at", None)
    second.pop("generated_at", None)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_verdict_function_go_and_no_go_paths() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_paper_readiness_metrics(evidence)
    thresholds = build_deployment_thresholds(evidence, metrics)

    go = compute_paper_readiness_verdict(evidence, metrics, thresholds)
    assert go["verdict"] == "GO"
    assert go["all_checks_pass"] is True

    # Flipping the sealed EVAL-13 verdict to NO-GO must flip the readiness verdict.
    bad = copy.deepcopy(evidence)
    bad["eval13"]["verdict"] = "NO-GO"
    metrics_bad = compute_paper_readiness_metrics(bad)
    thresholds_bad = build_deployment_thresholds(bad, metrics_bad)
    no_go = compute_paper_readiness_verdict(bad, metrics_bad, thresholds_bad)
    assert no_go["verdict"] == "NO-GO"
    assert no_go["all_checks_pass"] is False
    failed = [c["name"] for c in no_go["checks"] if not c["pass"]]
    assert "eval13_certification_go" in failed

    # Flipping EVAL-12 verdict to NO-GO must flip the readiness verdict.
    bad2 = copy.deepcopy(evidence)
    bad2["eval12"]["verdict"] = "NO-GO"
    metrics_bad2 = compute_paper_readiness_metrics(bad2)
    thresholds_bad2 = build_deployment_thresholds(bad2, metrics_bad2)
    no_go2 = compute_paper_readiness_verdict(bad2, metrics_bad2, thresholds_bad2)
    assert no_go2["verdict"] == "NO-GO"
    assert "eval12_walkforward_go" in [c["name"] for c in no_go2["checks"] if not c["pass"]]


def test_metrics_are_finite_and_cite_sealed_numbers() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_paper_readiness_metrics(evidence)
    assert metrics["n_evidence_sources"] >= 1
    assert math.isfinite(metrics["eval11_best_mean_net_sharpe"])
    assert metrics["eval11_best_mean_net_sharpe"] > 0.0
    assert metrics["eval11_best_mean_net_sharpe"] > metrics["eval11_no_hedge_control_sharpe"]
    assert metrics["eval11_best_mean_net_sharpe"] > metrics["eval10_default_mean_net_sharpe"]
    assert math.isfinite(metrics["eval12_pbo_overall"])
    assert 0.0 <= metrics["eval12_pbo_overall"] <= 1.0
    assert len(metrics["eval12_bh_survivors"]) >= 1
    assert metrics["eval13_all_checks_pass"] is True
    assert metrics["paper_all_critical_passed"] is True
    assert metrics["paper_live_trading_enabled"] is False
    assert metrics["cv_all_critical_passed"] is True
    assert metrics["cv_reconciliation_freshness_met"] is True
    assert metrics["cv_reconciliation_target_gte"] == 0.99
    assert metrics["live_trading_enabled"] is False


def test_guardrails_are_numeric_and_pass() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_paper_readiness_metrics(evidence)
    thresholds = build_deployment_thresholds(evidence, metrics)
    guardrails = thresholds["guardrails"]
    assert len(guardrails) >= 1
    assert thresholds["all_guardrails_pass"] is True
    names = {g["name"] for g in guardrails}
    for required in (
        "max_notional_cap_usd",
        "delta_band_usd",
        "toxicity_gate_threshold",
        "cost_budget_bps",
        "kill_switch_max_drawdown",
        "kill_switch_toxicity",
        "kill_switch_cost_bps",
        "max_daily_loss_usd",
        "live_trading_disabled",
    ):
        assert required in names, f"missing guardrail {required}"
    for g in guardrails:
        assert "name" in g and "category" in g
        assert "threshold" in g and "observed" in g
        assert "pass" in g and "rationale" in g
        assert isinstance(g["threshold"], (int, float))
        assert isinstance(g["observed"], (int, float))
        assert math.isfinite(float(g["threshold"]))
        assert math.isfinite(float(g["observed"]))
        assert isinstance(g["rationale"], str) and len(g["rationale"]) > 0
        assert g["pass"] is True, f"guardrail {g['name']} did not pass: {g['rationale']}"

    # Specific EVAL-13 wired values.
    by_name = {g["name"]: g for g in guardrails}
    assert by_name["max_notional_cap_usd"]["threshold"] == 1_000_000.0
    assert by_name["delta_band_usd"]["threshold"] == 323.7734839590619
    assert by_name["toxicity_gate_threshold"]["threshold"] == 0.7
    assert by_name["cost_budget_bps"]["threshold"] == 2.0
    assert by_name["kill_switch_max_drawdown"]["threshold"] == 0.20
    assert by_name["kill_switch_toxicity"]["threshold"] == 0.80
    assert by_name["kill_switch_cost_bps"]["threshold"] == 5.00
    assert by_name["max_daily_loss_usd"]["threshold"] == 50_000.0
    assert by_name["live_trading_disabled"]["pass"] is True


def test_alert_watch_levels_and_kill_switch_halt_conditions_present() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_paper_readiness_metrics(evidence)
    thresholds = build_deployment_thresholds(evidence, metrics)
    assert len(thresholds["alert_watch_levels"]) >= 1
    assert len(thresholds["kill_switch_halt_conditions"]) >= 1
    for w in thresholds["alert_watch_levels"]:
        assert "name" in w and "threshold" in w and "observed" in w and "pass" in w
        assert math.isfinite(float(w["threshold"])) and math.isfinite(float(w["observed"]))
    for h in thresholds["kill_switch_halt_conditions"]:
        assert "name" in h and "threshold" in h and "observed" in h and "pass" in h
        assert h.get("halt") is True
        assert math.isfinite(float(h["threshold"])) and math.isfinite(float(h["observed"]))
    halt_names = {h["name"] for h in thresholds["kill_switch_halt_conditions"]}
    for required in (
        "kill_switch_max_drawdown_halt",
        "kill_switch_toxicity_halt",
        "kill_switch_cost_bps_halt",
    ):
        assert required in halt_names, f"missing kill-switch halt condition {required}"


def test_verdict_matches_function_and_finite_thresholds() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_paper_readiness_metrics(evidence)
    thresholds = build_deployment_thresholds(evidence, metrics)
    verdict = compute_paper_readiness_verdict(evidence, metrics, thresholds)
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert all(
        math.isfinite(g["threshold"]) and math.isfinite(g["observed"])
        for g in thresholds["guardrails"]
    )
    assert all(
        math.isfinite(g["threshold"]) and math.isfinite(g["observed"])
        for g in thresholds["alert_watch_levels"]
    )
    assert all(
        math.isfinite(g["threshold"]) and math.isfinite(g["observed"])
        for g in thresholds["kill_switch_halt_conditions"]
    )


def test_paper_readiness_cli_writes_artifacts(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(
        [
            sys.executable,
            "src/analytics/paper_deployment_readiness.py",
            "--out-dir",
            str(tmp_path),
            "--timestamp",
            "2026-11-13T030000Z",
        ],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["verdict"] == "GO"
    assert out["all_checks_pass"] is True
    assert out["live_trading_enabled"] is False
    json_files = sorted(tmp_path.glob("PAPER_DEPLOYMENT_READINESS_*.json"))
    md_files = sorted(tmp_path.glob("PAPER_DEPLOYMENT_READINESS_*.md"))
    assert len(json_files) == 1 and len(md_files) == 1
    assert json_files[0].name == "PAPER_DEPLOYMENT_READINESS_20261113T030000Z.json"
    assert md_files[0].name == "PAPER_DEPLOYMENT_READINESS_20261113T030000Z.md"
    artifact = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert artifact["report_id"] == REPORT_ID
    assert artifact["verdict"] == "GO"
    assert artifact["never_valid_true"] is True
    assert artifact != {"valid": True}
    assert "paper_readiness_metrics" in artifact
    assert "deployment_thresholds" in artifact
    assert "evidence_matrix" in artifact
    assert "verdict_checks" in artifact
    assert "artifact_paths" in artifact
    _assert_no_nonfinite(artifact)
    md_text = md_files[0].read_text(encoding="utf-8")
    assert "PAPER DEPLOYMENT READINESS" in md_text
    assert "GO" in md_text
    assert "KILL-SWITCH HALT CONDITIONS" in md_text
    assert "ALERT WATCH LEVELS" in md_text
