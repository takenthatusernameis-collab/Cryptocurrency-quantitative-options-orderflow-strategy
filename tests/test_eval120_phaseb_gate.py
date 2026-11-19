#!/usr/bin/env python3
"""Tests for EVAL-120 phase-B gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.eval120_phaseb_gate as e120gate  # noqa: E402


# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------
def test_gate_constants():
    assert e120gate.REPORT_ID == "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED"
    assert e120gate.PREREG_ID == "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION"
    assert e120gate.BLOCKED_ID == "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED"
    assert "min_underlyings" in e120gate.REQUIRED_FLOOR_KEYS
    assert e120gate.EXPECTED_BASELINE == "BTC"
    assert e120gate.EXPECTED_RELATIVE == "ETH"


# ---------------------------------------------------------------------------
# Test verification functions with mock data
# ---------------------------------------------------------------------------
def _make_valid_prereg() -> Dict[str, Any]:
    return {
        "prereg_id": e120gate.PREREG_ID,
        "generated_at": "2026-11-19T06:15:00Z",
        "task": "EVAL120-TEST",
        "hypothesis": "The causal cross-sectional options implied-vol term-ratio basis (term_ratio_ETH - term_ratio_BTC, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward relative realized return skewness spread (skewness[ETH] - skewness[BTC] over the next H perp log returns), independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-77 surface basis floor.",
        "extends": "EVAL-77 (cross-sectional surface basis atm_iv+skew -> forward realized-vol spread) and EVAL-105 (cross-sectional term-ratio basis -> relative tail-asymmetry spread) and EVAL-116 (cross-sectional skew basis -> relative return skewness spread): same Spearman rank-IC statistic and sealed signal/target reconstructions reused verbatim, but a distinct on-charter signal x target cell — the *cross-sectional term-ratio basis* (term_ratio_ETH - term_ratio_BTC) -> forward *relative realized return skewness spread*; no new acquisition",
        "protocol": {
            "cross_section": {"baseline": "BTC", "relative": "ETH"},
            "term_signals": ["term_ratio"],
            "bar_seconds_grid": [60.0, 300.0],
            "forward_horizons_bars": [6, 24, 72],
            "stats": {
                "permutation_perms": 1000,
                "bootstrap_resamples": 20000,
                "bootstrap_block": 8,
                "fdr_alpha": 0.05,
                "seed": 1337,
                "zwindow": 48,
                "min_usable_pairs_per_config": 120,
            },
        },
        "capture_dir": "data/raw/eval61",
        "floor": {
            "min_underlyings": 2,
            "min_aligned_common_bars": 200,
            "min_usable_pairs_per_config": 120,
            "note": "EVAL-120 consumes both underlyings' trade-tape IV surfaces and both perp series, so it reuses the sealed EVAL-77 composed surface basis floor verbatim (the EVAL-71 surface floor applied to BOTH BTC and ETH, plus a cross-sectional alignment floor of >= min_aligned_common_bars common bar-ends on the coarsest grid), applied to BOTH BTC and ETH. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched.",
        },
    }


def _make_valid_combined() -> Dict[str, Any]:
    return {
        "report_id": e120gate.REPORT_ID,
        "generated_at": "2026-11-19T06:15:00Z",
        "task": "EVAL120-TEST",
        "verdict": "NO-GO CONFIRMED (PASS)",
        "verdict_detail": "test",
        "floor_ok": True,
        "capture_dir": "data/raw/eval61",
        "underlyings": ["BTC", "ETH"],
        "floor": dict(e120gate.FLOOR),
        "campaign_floor": {
            "underlyings": ["BTC", "ETH"],
            "underlyings_ok": True,
            "aligned_common_bars_by_grid": {"60.0": 500, "300.0": 100},
            "aligned_common_bars_binding": 100,
            "aligned_ok": True,
            "checks": {"underlyings_ok": True, "aligned_ok": True},
            "ok": True,
        },
        "protocol": {},
        "per_config": [
            {"signal": "term_ratio", "bar_seconds": 60.0, "horizon_bars": 6, "n_pairs": 200, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 60.0, "horizon_bars": 24, "n_pairs": 200, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 60.0, "horizon_bars": 72, "n_pairs": 200, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 300.0, "horizon_bars": 6, "n_pairs": 50, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 300.0, "horizon_bars": 24, "n_pairs": 50, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 300.0, "horizon_bars": 72, "n_pairs": 50, "pass": False},
        ],
        "summary": {"n_configs": 6, "n_pass": 0, "pass_configs": [], "best_ic": 0.0, "best_config": "n/a"},
        "pooled": {
            "bh_fdr": {"rejected": []},
            "any_config_pass": False,
            "campaign_state": "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD",
        },
        "errors": [],
    }


def _make_valid_blocked() -> Dict[str, Any]:
    return {
        "report_id": e120gate.BLOCKED_ID,
        "generated_at": "2026-11-19T06:15:00Z",
        "task": "EVAL120-TEST",
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-77 surface basis floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": "data/raw/eval61",
        "underlyings": ["BTC", "ETH"],
        "floor": dict(e120gate.FLOOR),
        "campaign_floor": {},
        "errors": [],
    }


def test_verify_prereg_valid(tmp_path: Path):
    prereg = _make_valid_prereg()
    p = tmp_path / "prereg.json"
    p.write_text(json.dumps(prereg))
    ok, errors = e120gate._verify_prereg(p)
    assert ok, f"Expected valid prereg, got errors: {errors}"


def test_verify_prereg_missing_field(tmp_path: Path):
    prereg = _make_valid_prereg()
    del prereg["hypothesis"]
    p = tmp_path / "prereg.json"
    p.write_text(json.dumps(prereg))
    ok, errors = e120gate._verify_prereg(p)
    assert not ok
    assert any("hypothesis" in e for e in errors)


def test_verify_prereg_wrong_id(tmp_path: Path):
    prereg = _make_valid_prereg()
    prereg["prereg_id"] = "WRONG_ID"
    p = tmp_path / "prereg.json"
    p.write_text(json.dumps(prereg))
    ok, errors = e120gate._verify_prereg(p)
    assert not ok
    assert any("prereg_id mismatch" in e for e in errors)


def test_verify_combined_valid(tmp_path: Path):
    combined = _make_valid_combined()
    p = tmp_path / "combined.json"
    p.write_text(json.dumps(combined))
    ok, errors = e120gate._verify_combined(p)
    assert ok, f"Expected valid combined, got errors: {errors}"


def test_verify_combined_wrong_verdict(tmp_path: Path):
    combined = _make_valid_combined()
    combined["verdict"] = "INVALID"
    p = tmp_path / "combined.json"
    p.write_text(json.dumps(combined))
    ok, errors = e120gate._verify_combined(p)
    assert not ok
    assert any("invalid verdict" in e for e in errors)


def test_verify_combined_missing_underlyings(tmp_path: Path):
    combined = _make_valid_combined()
    combined["underlyings"] = ["BTC"]
    p = tmp_path / "combined.json"
    p.write_text(json.dumps(combined))
    ok, errors = e120gate._verify_combined(p)
    assert not ok
    assert any("underlyings must be a list of 2" in e for e in errors)


def test_verify_combined_floor_ok_false_with_go_verdict(tmp_path: Path):
    combined = _make_valid_combined()
    combined["floor_ok"] = False
    combined["verdict"] = "GO CONFIRMED"
    p = tmp_path / "combined.json"
    p.write_text(json.dumps(combined))
    ok, errors = e120gate._verify_combined(p)
    assert not ok
    assert any("floor_ok is False but verdict is" in e for e in errors)


def test_verify_blocked_valid(tmp_path: Path):
    blocked = _make_valid_blocked()
    p = tmp_path / "blocked.json"
    p.write_text(json.dumps(blocked))
    ok, errors = e120gate._verify_blocked(p)
    assert ok, f"Expected valid blocked, got errors: {errors}"


def test_verify_blocked_wrong_verdict(tmp_path: Path):
    blocked = _make_valid_blocked()
    blocked["verdict"] = "NO-GO CONFIRMED (PASS)"
    p = tmp_path / "blocked.json"
    p.write_text(json.dumps(blocked))
    ok, errors = e120gate._verify_blocked(p)
    assert not ok
    assert any("verdict must be 'BLOCKED'" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])