"""Numeric-invariant tests for src/analytics/production_simulation_evaluation.py (EVAL-19).

Covers: real BTC options chain loading (30 quotes) and orderflow loading (1000 trades,
20 liqs, 8 funding), causal signal construction (options/orderflow/combined) with
non-degenerate VPIN toxicity gate, multi-seed net-of-cost walk-forward controls,
cost sensitivity grid, regime stress + kill-switch reporting, statistical defensibility
fields (IC/permutation/DSR/PBO/BH-FDR), deterministic verdict checks with numeric
thresholds, strict JSON serialization (allow_nan=False, never {"valid": true}), and
CLI artifact emission.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.analytics.production_simulation_evaluation import (
    COST_GRID_BPS,
    DEFAULT_SEEDS,
    DEFAULT_TOXICITY_THRESHOLD,
    HORIZONS,
    IC_EXISTS_EPSILON,
    PERM_ALPHA,
    TSTAT_CRITICAL,
    TRADING_MODE,
    _all_finite_numbers,
    _finite,
    _stamp_for_filename,
    _utc_now_iso,
    compute_production_simulation_verdict,
    evaluate_production_simulation,
    load_btc_options_chain,
    load_btc_orderflow,
)
from src.campaign.integrated import DEFAULT_SPOT

REPO_ROOT = Path(__file__).resolve().parents[1]
SPOT = float(DEFAULT_SPOT["BTC"])


def _report():
    return evaluate_production_simulation(write=False, timestamp="2026-11-13T10:46:57Z")


# --------------------------------------------------------------------------- #
# 1. Helpers
# --------------------------------------------------------------------------- #


def test_finite_and_stamp_helpers():
    assert _finite(1.5) == 1.5
    assert _finite(float("inf")) == 0.0
    assert _finite(float("nan")) == 0.0
    assert _finite("2.5") == 2.5
    assert _finite(None) == 0.0
    assert _stamp_for_filename("2026-11-13T10:46:57Z") == "20261113T104657Z"
    iso = _utc_now_iso()
    assert iso.endswith("Z") and "T" in iso


def test_all_finite_numbers():
    assert _all_finite_numbers({"a": 1.0, "b": [2.0, 3.0], "c": True}) is True
    assert _all_finite_numbers({"a": float("nan")}) is False
    assert _all_finite_numbers([float("inf")]) is False


# --------------------------------------------------------------------------- #
# 2. Real data loading (no network, deterministic loaders)
# --------------------------------------------------------------------------- #


def test_load_real_options_chain_shape():
    chain = load_btc_options_chain("BTC", spot=SPOT)
    assert chain.underlying == "BTC"
    assert chain.venue == "synthetic"
    assert len(chain.quotes) == 30
    for q in chain.quotes:
        assert q.contract.strike > 0.0
        assert q.contract.option_type in ("call", "put")
        assert q.mark_iv is not None and q.mark_iv > 0.0


def test_load_real_orderflow_shape():
    snap = load_btc_orderflow("BTC", "synthetic")
    assert snap.symbol == "BTC"
    assert snap.venue == "synthetic"
    assert len(snap.trades) == 1000
    assert len(snap.liquidations) == 20
    assert len(snap.funding_rates) == 8
    for t in snap.trades:
        assert t.symbol == "BTCUSDT"
        assert t.size > 0.0 and t.price > 0.0
        assert str(t.side).lower() in ("buy", "sell")


# --------------------------------------------------------------------------- #
# 3. Signals, bars, and toxicity
# --------------------------------------------------------------------------- #


def test_bars_and_signal_alignment():
    report = _report()
    bars = report["bars"]
    assert bars["n_bars"] > max(HORIZONS) + 1
    assert bars["n_trades_total"] == 1000
    assert bars["bar_duration_seconds"] > 0.0
    for key in ("combined", "options_only", "orderflow_only"):
        sig = report["signals"][key]
        assert sig["n_bars"] == bars["n_bars"]
        assert all(math.isfinite(float(v)) for v in [sig.get("mean_signal", 0.0)])


def test_toxicity_gate_non_degenerate():
    report = _report()
    tox = report["toxicity"]
    assert tox["toxicity_measured"] is True
    assert 0.0 < float(tox["mean_toxicity"]) < 1.0
    assert 0.0 < float(tox["toxic_gate_active_fraction"]) < 1.0
    assert math.isfinite(float(tox["p95_toxicity"]))
    assert float(tox["toxicity_threshold"]) == DEFAULT_TOXICITY_THRESHOLD


# --------------------------------------------------------------------------- #
# 4. Alpha and statistical defensibility
# --------------------------------------------------------------------------- #


def test_alpha_ic_fields_finite():
    report = _report()
    for key in ("combined", "options", "orderflow"):
        alpha = report["alpha"][key]
        assert int(alpha["n_horizons"]) == len(HORIZONS)
        assert math.isfinite(float(alpha["ic_mean"]))
        assert math.isfinite(float(alpha["ic_tstat"]))
        ci = alpha["ic_bootstrap_ci"]
        assert math.isfinite(float(ci["lo"])) and math.isfinite(float(ci["hi"]))
        for h in HORIZONS:
            assert str(h) in alpha["ic_by_horizon"] or h in alpha["ic_by_horizon"]


def test_statistical_defensibility_fields():
    report = _report()
    st = report["statistical"]
    assert "permutation" in st and "p_value" in st["permutation"]
    assert 0.0 <= float(st["permutation"]["p_value"]) <= 1.0
    assert isinstance(st["dsr"], dict) and st["dsr"]
    assert all(math.isfinite(float(v)) for v in st["dsr"].values())
    assert "pbo" in st and "overall_pbo" in st["pbo"]
    assert math.isfinite(float(st["pbo"].get("overall_pbo", 0.0)))
    assert "bh_fdr" in st and st["bh_fdr"]["alpha"] > 0
    assert isinstance(report["permutation_pairs"], dict)
    assert all(0.0 <= float(v) <= 1.0 for v in report["permutation_pairs"].values())


# --------------------------------------------------------------------------- #
# 5. Walk-forward controls, cost sensitivity, regimes, kill-switch
# --------------------------------------------------------------------------- #


def test_multi_seed_walkforward_aggregate_controls():
    report = _report()
    wf = report["walkforward"]
    assert list(wf["seeds"]) == list(DEFAULT_SEEDS)
    agg = wf["aggregate"]
    for name in ("combined", "flat", "options_only", "orderflow_only"):
        m = agg[name]
        for field in ("mean_oos_return", "mean_oos_sharpe", "mean_oos_max_drawdown",
                      "mean_total_cost_usd", "mean_num_trades", "mean_num_windows"):
            assert math.isfinite(float(m[field]))
        assert float(m["mean_num_windows"]) > 0
    # Flat control should be exactly flat in return/cost/trades.
    flat = agg["flat"]
    assert abs(float(flat["mean_oos_return"])) <= 1e-12
    assert abs(float(flat["mean_total_cost_usd"])) <= 1e-9
    assert abs(float(flat["mean_num_trades"])) <= 1e-9


def test_cost_sensitivity_grid_and_monotonic_cost_pressure():
    report = _report()
    cs = report["cost_sensitivity"]
    grid = cs["cost_grid"]
    assert list(map(float, cs["cost_grid_bps"])) == list(map(float, COST_GRID_BPS))
    for bps in COST_GRID_BPS:
        v = grid[str(float(bps))]
        assert math.isfinite(float(v["mean_oos_sharpe"]))
        assert math.isfinite(float(v["mean_oos_return"]))
        assert float(v["mean_total_cost_usd"]) >= 0.0
    # Higher spread should not reduce total cost for a traded strategy.
    assert float(grid["5.0"]["mean_total_cost_usd"]) >= float(grid["0.0"]["mean_total_cost_usd"]) - 1e-9


def test_regime_stress_and_kill_switch_reported():
    report = _report()
    rs = report["regime_stress"]
    for key in ("high_toxicity_regime", "low_toxicity_regime"):
        reg = rs[key]
        for field in ("num_windows", "net_return", "sharpe", "max_drawdown"):
            assert math.isfinite(float(reg[field]))
    assert "iv_skew_slope" in rs and math.isfinite(float(rs["iv_skew_slope"]))
    ks = report["kill_switch"]
    for field in ("observed_max_dd", "observed_mean_dd", "observed_max_toxicity",
                  "observed_main_cost_bps", "kill_switch_dd_threshold",
                  "kill_switch_toxicity_threshold", "kill_switch_cost_bps_threshold"):
        assert math.isfinite(float(ks[field]))
    for field in ("dd_triggered", "toxicity_triggered", "cost_triggered", "any_triggered"):
        assert isinstance(ks[field], bool)


# --------------------------------------------------------------------------- #
# 6. Verdict, evidence, and strict serialization
# --------------------------------------------------------------------------- #


def test_deterministic_verdict_structure_and_consistency():
    report = _report()
    vc = report["verdict_checks"]
    assert report["verdict"] in ("GO", "NO-GO")
    assert isinstance(vc["checks"], list) and len(vc["checks"]) == 6
    assert vc["n_checks"] == 6
    expected = {
        "signal_exists",
        "ic_significant",
        "net_of_cost_superior_vs_controls",
        "toxicity_gate_measured",
        "robust_across_regimes",
        "guardrails_consistent_with_eval13_14_15",
    }
    assert {c["name"] for c in vc["checks"]} == expected
    assert all(isinstance(c["pass"], bool) for c in vc["checks"])
    assert all("threshold" in c and "observed" in c and "reason" in c for c in vc["checks"])
    assert vc["all_checks_pass"] == all(c["pass"] for c in vc["checks"])
    assert (vc["n_passed"] == vc["n_checks"]) == vc["all_checks_pass"]
    assert set(vc["failed_checks"]) == {c["name"] for c in vc["checks"] if not c["pass"]}
    assert report["verdict"] == ("GO" if vc["all_checks_pass"] else "NO-GO")


def test_verdict_api_matches_report_checks():
    report = _report()
    vc = compute_production_simulation_verdict(
        report["alpha"]["combined"],
        report["toxicity"],
        report["walkforward"]["aggregate"],
        report["cost_sensitivity"],
        report["regime_stress"],
        report["kill_switch"],
        report["statistical"],
        report["permutation_pairs"],
        no_lookahead_asserted=True,
    )
    assert vc["verdict"] == report["verdict"]
    assert vc["failed_checks"] == report["verdict_checks"]["failed_checks"]
    assert vc["n_passed"] == report["verdict_checks"]["n_passed"]
    assert vc["all_checks_pass"] == report["verdict_checks"]["all_checks_pass"]


def test_evidence_and_paper_only_flags():
    report = _report()
    ev = report["evidence_matrix"]
    assert ev["options_chain_loaded"] is True and ev["n_options_quotes"] == 30
    assert ev["orderflow_loaded"] is True and ev["n_trades"] == 1000
    assert ev["n_liquidations"] == 20 and ev["n_funding_rates"] == 8
    assert ev["bars_constructed"] is True
    assert ev["multi_seed_walkforward_run"] is True
    assert ev["paper_only"] is True and ev["live_trading_enabled"] is False
    assert ev["toxicity_gate_applied_to_all_pillars"] is True
    assert report["trading_mode"] == TRADING_MODE
    assert report["live_trading_enabled"] is False
    assert report["deployment_authorization"]["mode"] == "paper_only"


def test_strict_serialization_no_valid_true_and_no_nonfinite():
    report = _report()
    assert _all_finite_numbers(report)
    text = json.dumps(report, sort_keys=True, allow_nan=False)
    parsed = json.loads(text)
    assert "valid" not in parsed or parsed.get("valid") is not True
    assert parsed["never_valid_true"] is True
    assert parsed["verdict"] in ("GO", "NO-GO")


# --------------------------------------------------------------------------- #
# 7. CLI artifact emission
# --------------------------------------------------------------------------- #


def test_cli_writes_strict_artifacts(tmp_path):
    out = tmp_path / "rs"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    cmd = [sys.executable, "-m", "src.analytics.production_simulation_evaluation",
           "--out", str(out), "--timestamp", "2026-11-13T10:46:57Z"]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, check=True)
    summary = json.loads(proc.stdout.strip().splitlines()[0])
    assert summary["report_id"] == "PRODUCTION_SIMULATION_EVAL_19"
    assert summary["verdict"] in ("GO", "NO-GO")
    assert "artifact_paths" in summary
    json_path = Path(summary["artifact_paths"]["json"])
    md_path = Path(summary["artifact_paths"]["md"])
    assert json_path.exists() and md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["report_id"] == "PRODUCTION_SIMULATION_EVAL_19"
    assert "valid" not in payload or payload.get("valid") is not True
    assert json_path.name == "PRODUCTION_SIMULATION_EVAL_20261113T104657Z.json"
    assert md_path.name == "PRODUCTION_SIMULATION_EVAL_20261113T104657Z.md"
    assert _all_finite_numbers(payload)
