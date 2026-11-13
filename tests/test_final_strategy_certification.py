"""Numeric-invariant tests for src/analytics/final_strategy_certification.py (EVAL-13)."""

from __future__ import annotations

import copy
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from src.analytics.final_strategy_certification import (
    REPORT_ID,
    build_guardrails,
    compute_certification_verdict,
    compute_net_of_cost_metrics,
    evaluate_final_strategy_certification,
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


def test_certification_runs_and_certifies_go() -> None:
    report = evaluate_final_strategy_certification(write=False)
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] == "GO"
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["never_valid_true"] is True
    assert report != {"valid": True}
    assert "evidence" in report
    assert "net_of_cost_metrics" in report
    assert "guardrails" in report
    assert "verdict_checks" in report
    assert "deployment_authorization" in report
    assert report["deployment_authorization"]["mode"] == "paper_only"
    assert report["verdict_checks"]["all_checks_pass"] is True
    assert report["verdict_checks"]["verdict"] == "GO"
    assert report["verdict_checks"]["n_passed"] == report["verdict_checks"]["n_checks"]
    assert len(report["evidence"]["evidence_sources"]) >= 2
    _assert_no_nonfinite(report)


def test_determinism_after_timestamp_normalization() -> None:
    first = evaluate_final_strategy_certification(write=False)
    second = evaluate_final_strategy_certification(write=False)
    first.pop("generated_at", None)
    second.pop("generated_at", None)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_verdict_function_go_and_no_go_paths() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_net_of_cost_metrics(evidence)
    guardrails = __import__("src.analytics.final_strategy_certification", fromlist=["build_guardrails"]).build_guardrails(evidence)  # noqa: E501

    go = compute_certification_verdict(evidence, metrics, guardrails)
    assert go["verdict"] == "GO"
    assert go["all_checks_pass"] is True

    # Flipping the sealed EVAL-12 verdict to NO-GO must flip the certification.
    bad = copy.deepcopy(evidence)
    bad["eval12"]["verdict"] = "NO-GO"
    metrics_bad = compute_net_of_cost_metrics(bad)
    no_go = compute_certification_verdict(bad, metrics_bad, guardrails)
    assert no_go["verdict"] == "NO-GO"
    assert no_go["all_checks_pass"] is False
    failed = [c["name"] for c in no_go["checks"] if not c["pass"]]
    assert "eval12_walkforward_go" in failed

    # Failing a guardrail must flip the certification.
    bad_guardrails = copy.deepcopy(guardrails)
    bad_guardrails[0]["pass"] = False
    no_go2 = compute_certification_verdict(evidence, metrics, bad_guardrails)
    assert no_go2["verdict"] == "NO-GO"


def test_net_of_cost_metrics_are_finite_and_consistent() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_net_of_cost_metrics(evidence)
    assert math.isfinite(metrics["eval11_best_mean_net_sharpe"])
    assert metrics["eval11_best_mean_net_sharpe"] > 0.0
    assert metrics["eval11_best_mean_net_sharpe"] > metrics["eval11_no_hedge_control_sharpe"]
    assert metrics["eval11_best_mean_net_sharpe"] > metrics["eval10_default_mean_net_sharpe"]
    assert metrics["eval11_best_mean_net_sharpe_gt_eval10"] is True
    assert metrics["dsr_all_finite"] is True
    assert metrics["permutation_significant"] is True
    assert 0.0 < metrics["permutation_eval11_vs_eval10"]["p_value"] < 0.05
    assert math.isfinite(metrics["bootstrap_ci_mean_net_return"]["point"])
    assert math.isfinite(metrics["bootstrap_ci_mean_net_sharpe"]["point"])
    for name, check in metrics["dsr_consistency"].items():
        assert check["consistent"] is True, f"DSR recompute inconsistent for {name}: {check}"
        assert math.isfinite(check["recomputed_dsr"])
        assert math.isfinite(check["sealed_dsr"])
    assert metrics["pbo_overall"] >= 0.0
    assert len(metrics["bh_surviving_configs"]) >= 1


def test_guardrails_are_numeric_and_pass() -> None:
    evidence = load_sealed_evidence()
    metrics = compute_net_of_cost_metrics(evidence)
    guardrails = __import__("src.analytics.final_strategy_certification", fromlist=["build_guardrails"]).build_guardrails(evidence)  # noqa: E501
    assert len(guardrails) >= 2
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
    names = {g["name"] for g in guardrails}
    for required in (
        "max_notional_cap_usd",
        "delta_band_usd",
        "toxicity_gate_threshold",
        "cost_budget_bps",
        "kill_switch_max_drawdown",
        "kill_switch_toxicity",
        "kill_switch_cost_bps",
        "live_trading_disabled",
    ):
        assert required in names, f"missing guardrail {required}"


def test_certification_cli_writes_artifacts(tmp_path: Path) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path.cwd())
    proc = subprocess.run(
        [
            sys.executable,
            "src/analytics/final_strategy_certification.py",
            "--out-dir",
            str(tmp_path),
            "--timestamp",
            "2026-11-13T014500Z",
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
    json_files = sorted(tmp_path.glob("FINAL_STRATEGY_CERTIFICATION_*.json"))
    md_files = sorted(tmp_path.glob("FINAL_STRATEGY_CERTIFICATION_*.md"))
    assert len(json_files) == 1 and len(md_files) == 1
    assert json_files[0].name == "FINAL_STRATEGY_CERTIFICATION_20261113T014500Z.json"
    assert md_files[0].name == "FINAL_STRATEGY_CERTIFICATION_20261113T014500Z.md"
    artifact = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert artifact["report_id"] == REPORT_ID
    assert artifact["verdict"] == "GO"
    assert artifact["never_valid_true"] is True
    assert artifact != {"valid": True}
    assert "net_of_cost_metrics" in artifact
    assert "guardrails" in artifact
    assert "verdict_checks" in artifact
    assert "artifact_paths" in artifact
    _assert_no_nonfinite(artifact)
    md_text = md_files[0].read_text(encoding="utf-8")
    assert "FINAL STRATEGY CERTIFICATION" in md_text
    assert "GO" in md_text
