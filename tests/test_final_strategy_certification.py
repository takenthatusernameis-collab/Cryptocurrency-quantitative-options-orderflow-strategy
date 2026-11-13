"""Numeric-invariant tests for src/analytics/final_strategy_certification.py (EVAL-13).

All tests are deterministic (fixed timestamps, fixed seeds) and target only
EVAL-13. They do not touch the full 865-file suite.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

from src.analytics.final_strategy_certification import (
    REPORT_ID,
    compute_certification_verdict,
    compute_guardrails,
    evaluate_final_strategy_certification,
    write_artifacts,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL11 = REPO_ROOT / "research_state" / "HEDGE_COST_OPTIMIZER_20261113T004000Z.json"
EVAL12 = REPO_ROOT / "research_state" / "REAL_WF_CERTIFICATION_20261113T010508Z.json"
EVAL10 = REPO_ROOT / "research_state" / "STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.json"


def _has_valid_true_shortcut(obj) -> bool:
    if isinstance(obj, dict):
        if obj.get("valid") is True:
            return True
        return any(_has_valid_true_shortcut(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_valid_true_shortcut(v) for v in obj)
    return False


def _assert_no_nonfinite(obj) -> None:
    bad: list[str] = []

    def walk(o, p: str) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{p}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{p}[{i}]")
        elif isinstance(o, float) and not isinstance(o, bool) and not math.isfinite(o):
            bad.append(p)

    walk(obj, "$")
    assert not bad, f"non-finite values at {bad[:5]}"


# ---------------------------------------------------------------------------
# End-to-end report
# ---------------------------------------------------------------------------

def test_certification_runs_and_produces_valid_report() -> None:
    report = evaluate_final_strategy_certification(timestamp="2026-11-13T01:18:00Z")
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] in ("GO", "NO-GO")
    assert report["never_valid_true"] is True
    assert isinstance(report["verdict_reasons"], list) and len(report["verdict_reasons"]) > 0
    assert report["verdict_reasons"][0].startswith(f"verdict: {report['verdict']}")
    assert report["non_degeneracy"]["non_degenerate"] is True
    assert report["non_degeneracy"]["evidence_sources_compared"] >= 2
    assert _has_valid_true_shortcut(report) is False
    _assert_no_nonfinite(report)

    e11 = report["evidence"]["eval11"]
    e12 = report["evidence"]["eval12"]
    e10 = report["evidence"]["eval10"]
    assert e11["mean_net_sharpe"] == 13.188322401914279
    assert e11["mean_net_return"] == 0.39999544362288453
    assert e11["mean_abs_delta_usd"] == 161.88674197953094
    assert e11["total_hedges"] == 3800
    assert e11["total_cost_usd"] == 646.4230312530128
    assert e11["no_hedge_control_sharpe"] == 5.590936162120627
    assert e11["config"]["target_delta_usd"] == -20000.0
    assert e11["config"]["toxicity_threshold"] == 0.7
    assert e11["config"]["cost_budget_bps"] == 0.5
    assert e12["verdict_artifact"] == "GO"
    assert e12["surviving_configs"] == ["EVAL11_best", "EVAL10_default"]
    assert e12["pbo_best"] == 0.46875
    assert e12["pbo_default"] == 0.5234375
    assert e12["pbo_overall"] == 0.5
    assert e10["verdict"] == "NO-GO"
    assert e10["pass_fraction"] == 0.0
    assert e10["mean_net_sharpe"] == -22.765929562035716
    assert e10["mean_net_return"] == -0.5580107668605527
    assert e10["bootstrap_sharpe_point"] == -22.765929562035716
    assert e10["bootstrap_return_point"] == -0.5580107668605527

    gr = report["guardrails"]
    assert gr["max_notional_cap_usd"] > 0
    assert gr["toxicity_gate_threshold"] == 0.7
    assert gr["cost_budget_bps"] == 0.5
    db = gr["delta_band_usd"]
    assert db["lo"] < db["hi"]
    assert db["lo"] <= db["target_delta_usd"] <= db["hi"]
    assert db["lo"] <= e11["mean_abs_delta_usd"] <= db["hi"]
    assert gr["paper_only"] is True
    assert gr["live_trading_authorization"] is False

    rec = report["recomputed"]
    assert all(0.0 <= v <= 1.0 for v in rec["dsr_by_config"].values())
    assert all(0.0 <= v <= 1.0 for v in rec["pbo_by_config"].values())
    assert 0.0 <= rec["pbo_overall"] <= 1.0
    assert _assert_no_nonfinite(rec) is None
    assert _assert_no_nonfinite(report["guardrail_checks"]) is None


# ---------------------------------------------------------------------------
# Determinism after timestamp normalization
# ---------------------------------------------------------------------------

def test_determinism_after_timestamp_normalization() -> None:
    a = evaluate_final_strategy_certification(timestamp="2026-11-13T01:18:00Z")
    b = evaluate_final_strategy_certification(timestamp="2026-11-13T02:19:00Z")
    a_norm = {k: v for k, v in a.items() if k != "generated_at"}
    b_norm = {k: v for k, v in b.items() if k != "generated_at"}
    assert json.dumps(a_norm, sort_keys=True) == json.dumps(b_norm, sort_keys=True)
    assert a["generated_at"] != b["generated_at"]


# ---------------------------------------------------------------------------
# Deterministic verdict function behavior
# ---------------------------------------------------------------------------

def _base_inputs() -> tuple[dict, dict, dict]:
    evidence = {
        "eval11": {
            "mean_net_sharpe": 13.188322401914279,
            "mean_net_return": 0.39999544362288453,
            "mean_abs_delta_usd": 161.88674197953094,
            "total_cost_usd": 646.4230312530128,
            "total_traded_notional": 6073398.34,
        },
        "eval12": {
            "verdict_artifact": "GO",
            "surviving_configs": ["EVAL11_best", "EVAL10_default"],
            "bh_alpha": 0.1,
            "pbo_best": 0.46875,
            "pbo_default": 0.5234375,
            "pbo_overall": 0.5,
        },
        "eval10": {
            "verdict": "NO-GO",
            "pass_fraction": 0.0,
            "mean_net_sharpe": -22.765929562035716,
        },
        "recomputed": {
            "dsr_by_config": {"EVAL11_best": 0.0, "EVAL10_default": 0.0},
            "pbo_by_config": {"EVAL11_best": 0.46875, "EVAL10_default": 0.5234375},
        },
    }
    guardrail_checks = {
        "all_guardrail_checks_pass": True,
        "max_notional_cap_positive_finite": True,
        "delta_band_hi_gt_lo": True,
        "target_delta_within_band": True,
        "mean_abs_delta_within_band": True,
        "toxicity_threshold_in_unit_interval": True,
        "cost_budget_bps_positive": True,
        "kill_switch_drawdown_in_unit_interval": True,
        "kill_switch_toxicity_in_unit_interval": True,
        "kill_switch_cost_multiplier_gt_one": True,
        "kill_switch_reconciliation_error_positive": True,
        "kill_switch_sharpe_floor_negative": True,
        "guardrails_all_numeric": True,
    }
    non_degeneracy = {
        "evidence_sources_compared": 3,
        "evidence_sources_at_least_two": True,
        "key_metrics_finite": True,
        "ci_pbo_dsr_finite": True,
        "explicit_pass_fail_reasons": True,
        "non_degenerate": True,
    }
    return evidence, guardrail_checks, non_degeneracy


def test_verdict_function_go_with_valid_evidence() -> None:
    evidence, gc, nd = _base_inputs()
    verdict, reasons = compute_certification_verdict(evidence, gc, nd)
    assert verdict == "GO"
    assert not any(r.startswith("fail:") for r in reasons if r != f"verdict: {verdict} ({sum(1 for x in reasons if x.startswith('pass:'))} passed, 0 failed)")


def test_verdict_function_nogo_when_best_sharpe_not_positive() -> None:
    evidence, gc, nd = _base_inputs()
    evidence["eval11"]["mean_net_sharpe"] = -1.0
    verdict, _ = compute_certification_verdict(evidence, gc, nd)
    assert verdict == "NO-GO"


def test_verdict_function_nogo_when_no_bh_survivors() -> None:
    evidence, gc, nd = _base_inputs()
    evidence["eval12"]["surviving_configs"] = []
    verdict, _ = compute_certification_verdict(evidence, gc, nd)
    assert verdict == "NO-GO"


def test_verdict_function_nogo_when_degenerate() -> None:
    evidence, gc, nd = _base_inputs()
    nd["evidence_sources_at_least_two"] = False
    nd["evidence_sources_compared"] = 1
    verdict, _ = compute_certification_verdict(evidence, gc, nd)
    assert verdict == "NO-GO"


def test_verdict_function_nogo_when_guardrail_checks_fail() -> None:
    evidence, gc, nd = _base_inputs()
    gc["all_guardrail_checks_pass"] = False
    verdict, _ = compute_certification_verdict(evidence, gc, nd)
    assert verdict == "NO-GO"


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------

def test_guardrail_thresholds_present_and_numeric() -> None:
    report = evaluate_final_strategy_certification(timestamp="2026-11-13T01:18:00Z")
    gr = report["guardrails"]
    ks = gr["kill_switch"]
    assert isinstance(gr["max_notional_cap_usd"], (int, float)) and gr["max_notional_cap_usd"] > 0
    assert isinstance(gr["toxicity_gate_threshold"], (int, float)) and 0.0 < gr["toxicity_gate_threshold"] < 1.0
    assert isinstance(gr["cost_budget_bps"], (int, float)) and gr["cost_budget_bps"] > 0
    assert isinstance(gr["total_cost_usd_observed"], (int, float))
    assert isinstance(gr["total_hedges_observed"], int)
    assert isinstance(ks["max_drawdown"], (int, float)) and 0.0 < ks["max_drawdown"] <= 1.0
    assert isinstance(ks["toxic_gate_active_fraction_max"], (int, float)) and 0.0 < ks["toxic_gate_active_fraction_max"] <= 1.0
    assert isinstance(ks["cost_budget_breach_multiplier"], (int, float)) and ks["cost_budget_breach_multiplier"] > 1.0
    assert isinstance(ks["reconciliation_max_abs_error"], (int, float)) and ks["reconciliation_max_abs_error"] > 0.0
    assert isinstance(ks["mean_net_sharpe_floor"], (int, float)) and ks["mean_net_sharpe_floor"] < 0.0
    # rationale fields present and non-empty
    for k in ("max_notional_cap_rationale", "delta_band_rationale", "toxicity_gate_threshold_rationale", "cost_budget_bps_rationale", "live_trading_authorization_rationale"):
        assert isinstance(gr[k], str) and len(gr[k]) > 0
    for k in ("max_drawdown_rationale", "toxic_gate_active_fraction_max_rationale", "cost_budget_breach_multiplier_rationale", "reconciliation_max_abs_error_rationale", "mean_net_sharpe_floor_rationale"):
        assert isinstance(ks[k], str) and len(ks[k]) > 0


# ---------------------------------------------------------------------------
# Recomputed net-of-cost evidence via code paths
# ---------------------------------------------------------------------------

def test_recomputed_evidence_finite_and_consistent() -> None:
    report = evaluate_final_strategy_certification(timestamp="2026-11-13T01:18:00Z")
    rec = report["recomputed"]
    assert set(rec["dsr_by_config"].keys()) == {"EVAL11_best", "EVAL10_default"}
    assert set(rec["pbo_by_config"].keys()) == {"EVAL11_best", "EVAL10_default"}
    # DSR recomputed matches artifact DSR (both 0.0 for these sealed returns)
    for name in ("EVAL11_best", "EVAL10_default"):
        assert rec["dsr_by_config"][name] == report["evidence"]["eval12"]["dsr_by_config_artifact"][name]
    assert rec["permutation_best_vs_default"]["n_permutations"] == 2000
    assert 0.0 < rec["permutation_best_vs_default"]["p_value"] <= 1.0
    assert rec["bootstrap_ci_mean_net_return_best"]["n_bootstrap"] == 2000
    assert rec["bootstrap_ci_mean_net_return_best"]["lo"] <= rec["bootstrap_ci_mean_net_return_best"]["hi"]


# ---------------------------------------------------------------------------
# Artifact writing
# ---------------------------------------------------------------------------

def test_write_artifacts_creates_strict_json_and_md(tmp_path) -> None:
    report = evaluate_final_strategy_certification(timestamp="2026-11-13T01:18:00Z")
    json_path, md_path = write_artifacts(report, out_dir=tmp_path, timestamp="2026-11-13T01:18:00Z")
    assert json_path.exists() and md_path.exists()
    assert json_path.name.startswith("FINAL_STRATEGY_CERTIFICATION_") and json_path.suffix == ".json"
    assert md_path.suffix == ".md"
    written = json.loads(json_path.read_text(encoding="utf-8"))
    assert written["report_id"] == REPORT_ID
    assert written["verdict"] == report["verdict"]
    assert _has_valid_true_shortcut(written) is False
    _assert_no_nonfinite(written)
    md_text = md_path.read_text(encoding="utf-8")
    assert "FINAL STRATEGY CERTIFICATION" in md_text
    assert f"Verdict: {report['verdict']}" in md_text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_cli_runs_and_exits_zero() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    completed = subprocess.run(
        [sys.executable, "src/analytics/final_strategy_certification.py",
         "--timestamp", "2026-11-13T01:18:00Z"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )
    assert completed.returncode == 0, completed.stderr
    out = json.loads(completed.stdout.splitlines()[0])
    assert out["report_id"] == REPORT_ID
    assert out["verdict"] in ("GO", "NO-GO")
    assert out["never_valid_true"] is True
    assert out["non_degenerate"] is True
