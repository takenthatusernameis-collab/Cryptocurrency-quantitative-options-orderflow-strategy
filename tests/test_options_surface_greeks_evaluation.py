"""Numeric-invariant tests for src/analytics/options_surface_greeks_evaluation.py (EVAL-16).

Covers: real-chain loading, measured data-quality invariants (BS-vs-mark and
parity residuals are finite and reproduce the known inconsistency), surface
reconstruction point counts and calibration residual, arbitrage checks on the
reconstructed grid, greeks recompute vs finite-difference agreement (delta/vega
match fraction == 1.0 on this deterministic chain), stored-vs-recomputed delta
error bounds, book-greek finiteness, net-of-cost delta-hedge determinism with a
finite Sharpe, deterministic verdict structure, strict serialization (no
NaN/Infinity), and an explicit assertion the report is never ``{"valid": True}``.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.analytics.options_surface_greeks_evaluation import (
    ARBITRAGE_MAX_VIOLATIONS,
    BS_VS_MARK_MAX_ABS_TOL,
    GREEK_FD_MATCH_FRACTION_TOL,
    GREEK_FD_TOL,
    PARITY_MAX_ABS_TOL,
    REPORT_ID,
    SURFACE_RESIDUAL_MAX_ABS_TOL,
    _all_finite_numbers,
    _atm_strike,
    _finite,
    _stamp_for_filename,
    _utc_now_iso,
    check_arbitrage_on_grid,
    compute_book_greeks,
    compute_data_quality_metrics,
    compute_greeks_metrics,
    compute_options_surface_verdict,
    evaluate_options_surface_greeks,
    load_btc_chain,
    reconstruct_surface,
    run_delta_hedge_oos,
)
from src.campaign.integrated import DEFAULT_SPOT, DETERMINISTIC_NOW

REPO_ROOT = Path(__file__).resolve().parents[1]
SPOT = float(DEFAULT_SPOT["BTC"])


def _report():
    return evaluate_options_surface_greeks(write=False, timestamp="2026-11-13T07:00:00Z")


# --------------------------------------------------------------------------- #
# 1. Helpers
# --------------------------------------------------------------------------- #

def test_finite_helper():
    assert _finite(1.5) == 1.5
    assert _finite(float("inf")) == 0.0
    assert _finite(float("nan")) == 0.0
    assert _finite("2.5") == 2.5
    assert _finite(None) == 0.0


def test_stamp_and_utc_helpers():
    assert _stamp_for_filename("2026-11-13T07:00:00Z") == "20261113T070000Z"
    assert _stamp_for_filename("2026-11-13T07:00:00.123456Z") == "20261113T070000Z"
    iso = _utc_now_iso()
    assert iso.endswith("Z") and "T" in iso and "+" not in iso


def test_all_finite_numbers():
    assert _all_finite_numbers({"a": 1.0, "b": [2.0, 3.0]}) is True
    assert _all_finite_numbers({"a": float("nan")}) is False
    assert _all_finite_numbers([float("inf")]) is False


# --------------------------------------------------------------------------- #
# 2. Real chain loading + ATM strike
# --------------------------------------------------------------------------- #

def test_load_real_chain_shape():
    chain = load_btc_chain()
    assert len(chain.quotes) == 30
    assert chain.underlying == "BTC"
    expiries = {str(q.contract.expiry) for q in chain.quotes}
    assert len(expiries) == 3
    for q in chain.quotes:
        assert q.open_interest > 0.0


def test_atm_strike_is_closest():
    chain = load_btc_chain()
    k = _atm_strike(chain, SPOT)
    # 65000 is an exact strike on the grid.
    assert k == 65000.0


# --------------------------------------------------------------------------- #
# 3. Data quality (measured, not fudged)
# --------------------------------------------------------------------------- #

def test_data_quality_reproduces_known_inconsistency():
    dq = compute_data_quality_metrics(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    assert dq["n_quotes"] == 30
    # The file is known-inconsistent: BS(mark_iv) vs mark and parity residuals
    # are large, and the module must report them rather than assume coherence.
    assert dq["bs_vs_mark_max_abs"] > 1000.0
    assert dq["parity_residual_max_abs"] > 1000.0
    assert dq["bs_vs_mark_max_abs"] > BS_VS_MARK_MAX_ABS_TOL
    assert dq["parity_residual_max_abs"] > PARITY_MAX_ABS_TOL


def test_data_quality_mark_iv_range():
    dq = compute_data_quality_metrics(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    assert 0.0 < dq["mark_iv_min"] <= dq["mark_iv_max"]
    assert dq["n_distinct_iv"] > 1
    assert dq["n_parity_pairs"] == 15
    assert _all_finite_numbers(dq)


# --------------------------------------------------------------------------- #
# 4. Surface reconstruction
# --------------------------------------------------------------------------- #

def test_surface_reconstruction_points_and_residual():
    s = reconstruct_surface(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    assert s["n_points"] == 30
    assert s["n_expiries"] == 3
    assert s["residual_report"]["residual_max_abs"] <= SURFACE_RESIDUAL_MAX_ABS_TOL
    assert s["residual_report"]["num_points"] == 30


def test_surface_get_iv_finite():
    s = reconstruct_surface(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    iv = s["surface"].get_iv(65000.0, 0.02, "call")
    assert math.isfinite(iv) and 0.0 < iv < 5.0


# --------------------------------------------------------------------------- #
# 5. Arbitrage checks
# --------------------------------------------------------------------------- #

def test_arbitrage_checks_are_finite_and_bounded():
    s = reconstruct_surface(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    a = check_arbitrage_on_grid(s["surface"], SPOT, now=DETERMINISTIC_NOW)
    assert a["butterfly_checks"] == 9
    assert a["calendar_checks"] == 10
    assert a["total_violations"] == a["butterfly_violations"] + a["calendar_violations"]
    assert a["total_violations"] <= 5  # measured small violation set on this grid
    assert a["butterfly_max_violation"] >= 0.0
    assert a["calendar_max_violation"] >= 0.0
    assert _all_finite_numbers(a)


def test_arbitrage_free_flag_matches_violations():
    s = reconstruct_surface(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    a = check_arbitrage_on_grid(s["surface"], SPOT, now=DETERMINISTIC_NOW)
    assert a["arbitrage_free"] == (a["total_violations"] == ARBITRAGE_MAX_VIOLATIONS)


# --------------------------------------------------------------------------- #
# 6. Greeks recompute
# --------------------------------------------------------------------------- #

def test_greeks_analytic_matches_finite_difference():
    s = reconstruct_surface(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    g = compute_greeks_metrics(load_btc_chain(), s["surface"], SPOT, now=DETERMINISTIC_NOW)
    assert g["n_evaluated"] == 30
    assert g["delta_match_fraction"] == 1.0
    assert g["vega_match_fraction"] == 1.0
    assert g["delta_match_fraction"] >= GREEK_FD_MATCH_FRACTION_TOL
    assert g["vega_match_fraction"] >= GREEK_FD_MATCH_FRACTION_TOL
    assert g["fd_tol"] == GREEK_FD_TOL


def test_greeks_stored_vs_recomputed_delta_error_positive():
    s = reconstruct_surface(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    g = compute_greeks_metrics(load_btc_chain(), s["surface"], SPOT, now=DETERMINISTIC_NOW)
    # Stored greeks disagree with surface-recomputed greeks (data is inconsistent).
    assert g["delta_err_max"] > 0.1
    assert g["delta_err_mean"] > 0.05
    for row in g["recomputed"]:
        assert 0.0 <= row["recomputed_delta"] <= 1.0 or -1.0 <= row["recomputed_delta"] <= 0.0
        assert row["delta_match"] is True
        assert row["vega_match"] is True


# --------------------------------------------------------------------------- #
# 7. Book greeks
# --------------------------------------------------------------------------- #

def test_book_greeks_finite():
    b = compute_book_greeks(load_btc_chain(), SPOT, now=DETERMINISTIC_NOW)
    assert b["total_gex"] > 0.0
    assert b["gamma_flip_level"] > 0.0
    assert b["put_call_ratio"] > 0.0
    assert b["max_pain"] > 0.0
    assert b["n_expiries_in_atm_ts"] == 3
    assert b["liquidity"]["total_oi"] > 0.0
    assert _all_finite_numbers(b)


# --------------------------------------------------------------------------- #
# 8. Net-of-cost delta hedge
# --------------------------------------------------------------------------- #

def test_delta_hedge_deterministic_and_finite():
    chain = load_btc_chain()
    h1 = run_delta_hedge_oos(chain, SPOT, seeds=(1, 2), n_points=160,
                             train_window=60, test_window=20, step_size=20)
    h2 = run_delta_hedge_oos(chain, SPOT, seeds=(1, 2), n_points=160,
                             train_window=60, test_window=20, step_size=20)
    assert h1 == h2
    assert h1["n_windows"] > 0
    assert math.isfinite(h1["mean_with_options_sharpe"])
    assert math.isfinite(h1["mean_with_options_return"])
    assert math.isfinite(h1["mean_without_options_sharpe"])
    assert _all_finite_numbers(h1)


def test_delta_hedge_spread_cost_monotone_effect():
    chain = load_btc_chain()
    lo = run_delta_hedge_oos(chain, SPOT, seeds=(1,), n_points=120,
                             train_window=40, test_window=20, step_size=20,
                             spread_bps=0.0)
    hi = run_delta_hedge_oos(chain, SPOT, seeds=(1,), n_points=120,
                             train_window=40, test_window=20, step_size=20,
                             spread_bps=50.0)
    # Higher spread cost can only reduce (or leave unchanged) the mean return.
    assert hi["mean_with_options_return"] <= lo["mean_with_options_return"] + 1e-9


# --------------------------------------------------------------------------- #
# 9. Verdict
# --------------------------------------------------------------------------- #

def test_verdict_structure_and_no_go_on_inconsistent_data():
    r = _report()
    v = r["verdict_checks"]
    assert r["verdict"] in ("GO", "NO-GO")
    assert v["verdict"] == r["verdict"]
    assert v["n_checks"] == 9
    assert v["n_passed"] + len(v["failed_checks"]) == v["n_checks"]
    assert v["all_checks_pass"] == (r["verdict"] == "GO")
    # Known-inconsistent chain -> data-quality checks must fail.
    assert "data_quality_bs_vs_mark" in v["failed_checks"]
    assert "data_quality_put_call_parity" in v["failed_checks"]
    assert "greeks_stored_vs_recomputed_delta" in v["failed_checks"]
    for c in v["checks"]:
        assert c["threshold"] == c["threshold"]  # finite
        assert c["observed"] == c["observed"]
        assert isinstance(c["reason"], str) and c["reason"]


def test_verdict_matches_function():
    chain = load_btc_chain()
    dq = compute_data_quality_metrics(chain, SPOT, now=DETERMINISTIC_NOW)
    s = reconstruct_surface(chain, SPOT, now=DETERMINISTIC_NOW)
    a = check_arbitrage_on_grid(s["surface"], SPOT, now=DETERMINISTIC_NOW)
    g = compute_greeks_metrics(chain, s["surface"], SPOT, now=DETERMINISTIC_NOW)
    b = compute_book_greeks(chain, SPOT, now=DETERMINISTIC_NOW)
    h = run_delta_hedge_oos(chain, SPOT, seeds=(1,), n_points=120,
                            train_window=40, test_window=20, step_size=20)
    v = compute_options_surface_verdict(dq, s, a, g, b, h)
    assert v["verdict"] == ("GO" if v["all_checks_pass"] else "NO-GO")
    assert v["n_passed"] == sum(1 for c in v["checks"] if c["pass"])


# --------------------------------------------------------------------------- #
# 10. Report-level invariants
# --------------------------------------------------------------------------- #

def test_report_never_valid_true_and_strict_serializable():
    r = _report()
    assert r["never_valid_true"] is True
    assert "valid" not in r or r.get("valid") is not True
    assert r["report_id"] == REPORT_ID
    assert r["trading_mode"] == "paper"
    assert r["live_trading_enabled"] is False
    # Strict JSON with allow_nan=False must succeed.
    text = json.dumps(r, allow_nan=False, sort_keys=True)
    assert "NaN" not in text and "Infinity" not in text
    assert _all_finite_numbers(r)


def test_report_evidence_matrix_complete():
    r = _report()
    em = r["evidence_matrix"]
    assert em["options_chain_loaded"] is True
    assert em["surface_reconstructed"] is True
    assert em["greeks_recomputed_from_surface"] is True
    assert em["paper_only"] is True
    assert em["live_trading_enabled"] is False


# --------------------------------------------------------------------------- #
# 11. CLI writes both artifacts
# --------------------------------------------------------------------------- #

def test_cli_writes_artifacts(tmp_path):
    code = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "src" / "analytics" / "options_surface_greeks_evaluation.py"),
            "--seeds", "1",
            "--n-points", "120",
            "--train-window", "40",
            "--test-window", "20",
            "--step-size", "20",
            "--out", str(tmp_path),
            "--timestamp", "2026-11-13T07:00:00Z",
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert code.returncode == 0, code.stderr
    written = [line.split("Wrote ", 1)[1] for line in code.stdout.splitlines() if line.startswith("Wrote ")]
    assert len(written) == 2
    for rel in written:
        p = Path(rel)
        if not p.is_absolute():
            p = tmp_path / p
        assert p.exists(), f"missing artifact {p}"
        text = p.read_text()
        assert "NaN" not in text and "Infinity" not in text