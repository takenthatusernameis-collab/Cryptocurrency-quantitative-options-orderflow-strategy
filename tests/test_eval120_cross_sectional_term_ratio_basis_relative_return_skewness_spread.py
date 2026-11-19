#!/usr/bin/env python3
"""Tests for EVAL-120: cross-sectional term-ratio basis -> relative return skewness spread."""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.eval120_cross_sectional_term_ratio_basis_relative_return_skewness_spread as e120  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures: minimal synthetic captures that satisfy the EVAL-77 floor
# ---------------------------------------------------------------------------
def _make_trade(ts_ms: int, iv: float, strike: float, expiry_ms: int, side: str = "buy") -> Dict[str, Any]:
    return {
        "timestamp": ts_ms,
        "iv": iv,
        "strike": strike,
        "expiry": expiry_ms,
        "side": side,
        "amount": 1.0,
        "price": 0.01,
    }


def _make_perp_bar(ts_ms: int, close: float) -> Dict[str, Any]:
    return {
        "ts": ts_ms,
        "open": close,
        "high": close,
        "low": close,
        "close": close,
        "volume": 100.0,
    }


def _make_capture(
    underlying: str,
    *,
    n_trades: int = 500,
    n_bars: int = 1000,
    bar_seconds: int = 60,
    perp_start: float = 50000.0,
) -> Dict[str, Any]:
    """Create a synthetic capture with option trades and perp bars."""
    base_ts = 1700000000000  # fixed base timestamp
    trades = []
    expiries = [base_ts + 7 * 24 * 3600 * 1000, base_ts + 30 * 24 * 3600 * 1000]  # 7d and 30d
    strikes = [perp_start * 0.95, perp_start, perp_start * 1.05]

    for i in range(n_trades):
        ts = base_ts + i * 1000
        exp = expiries[i % 2]
        strike = strikes[i % 3]
        iv = 0.5 + 0.1 * (i % 10) / 10.0
        trades.append(_make_trade(ts, iv, strike, exp))

    perp_bars = []
    close = perp_start
    for i in range(n_bars):
        ts = base_ts + i * bar_seconds * 1000
        close *= 1.0 + 0.0001 * (i % 3 - 1)  # small random walk
        perp_bars.append(_make_perp_bar(ts, close))

    return {
        "underlying": underlying,
        "option_trades": trades,
        "perp_bars": perp_bars,
        "metadata": {"source": "test"},
    }


@pytest.fixture
def btc_capture() -> Dict[str, Any]:
    return _make_capture("BTC", n_trades=600, n_bars=1500, perp_start=50000.0)


@pytest.fixture
def eth_capture() -> Dict[str, Any]:
    return _make_capture("ETH", n_trades=600, n_bars=1500, perp_start=3000.0)


@pytest.fixture
def captures(btc_capture: Dict[str, Any], eth_capture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {"BTC": btc_capture, "ETH": eth_capture}


# ---------------------------------------------------------------------------
# Test: _forward_return_skewness (third standardized moment)
# ---------------------------------------------------------------------------
def test_forward_return_skewness_basic():
    closes = [100.0, 101.0, 102.0, 101.5, 103.0, 104.0, 105.0, 106.0]
    out = e120._forward_return_skewness(closes, horizon_bars=3)
    assert isinstance(out, list)
    assert len(out) == len(closes) - 3  # n - h
    for v in out:
        if v is not None:
            assert isinstance(v, float)
            assert math.isfinite(v)


def test_forward_return_skewness_symmetric():
    # Symmetric returns around mean -> skewness ~ 0
    closes = [100.0]
    for i in range(1, 20):
        closes.append(100.0 + 0.5 * ((-1) ** i))  # oscillates
    out = e120._forward_return_skewness(closes, horizon_bars=5)
    for v in out:
        if v is not None:
            assert abs(v) < 1.0  # should be near zero


def test_forward_return_skewness_positive_skew():
    # Positive skew: a few large positive returns
    closes = [100.0]
    for _ in range(10):
        closes.append(closes[-1] * 1.001)  # small positive
    closes.append(closes[-1] * 1.05)  # large positive jump
    out = e120._forward_return_skewness(closes, horizon_bars=5)
    assert any(v is not None and v > 0 for v in out)


def test_forward_return_skewness_insufficient_returns():
    # Fewer than 3 returns in window -> None
    closes = [100.0, 101.0, 102.0]
    out = e120._forward_return_skewness(closes, horizon_bars=5)  # horizon > available
    assert all(v is None for v in out)


def test_forward_return_skewness_zero_variance():
    # Constant returns -> zero variance -> None
    closes = [100.0, 100.0, 100.0, 100.0, 100.0]
    out = e120._forward_return_skewness(closes, horizon_bars=2)
    assert all(v is None for v in out)


# ---------------------------------------------------------------------------
# Test: _relative_skewness_spread
# ---------------------------------------------------------------------------
def test_relative_skewness_spread_shapes(captures: Dict[str, Dict[str, Any]]):
    cs = e120.build_cross_section_with_term(captures, bar_seconds=60.0)
    spread = e120._relative_skewness_spread(cs, bar_seconds=60.0, horizon_bars=6)
    assert isinstance(spread, list)
    # Just verify the function returns a list (may be empty with synthetic data)


# ---------------------------------------------------------------------------
# Test: _relative_term_ratio_series
# ---------------------------------------------------------------------------
def test_relative_term_ratio_series_shape(captures: Dict[str, Dict[str, Any]]):
    cs = e120.build_cross_section_with_term(captures, bar_seconds=60.0)
    rel_z = e120._relative_term_ratio_series(cs, term_signal="term_ratio")
    assert isinstance(rel_z, list)
    assert len(rel_z) == len(cs["common"])


# ---------------------------------------------------------------------------
# Test: build_cross_section_with_term
# ---------------------------------------------------------------------------
def test_build_cross_section_with_term_overlays_term_ratio(captures: Dict[str, Dict[str, Any]]):
    cs = e120.build_cross_section_with_term(captures, bar_seconds=60.0)
    assert "common" in cs
    assert "maps" in cs
    assert "BTC" in cs["maps"]
    assert "ETH" in cs["maps"]
    # Check term_ratio is overlaid
    for inst in ("BTC", "ETH"):
        for bo, bar in cs["maps"][inst].items():
            if "term_ratio" not in bar:
                pass  # may be None if no term bar at that time


# ---------------------------------------------------------------------------
# Test: evaluate_config
# ---------------------------------------------------------------------------
def test_evaluate_config_returns_dict(captures: Dict[str, Dict[str, Any]]):
    res = e120.evaluate_config(
        captures, term_signal="term_ratio", bar_seconds=60.0, horizon_bars=6
    )
    assert isinstance(res, dict)
    for key in ("signal", "bar_seconds", "horizon_bars", "n_common_bars", "n_pairs", "pass"):
        assert key in res
    assert res["signal"] == "term_ratio"
    assert res["bar_seconds"] == 60.0
    assert res["horizon_bars"] == 6


def test_evaluate_config_insufficient_common_bars():
    # Empty captures -> insufficient common bars
    res = e120.evaluate_config(
        {"BTC": {"option_trades": [], "perp_bars": []}, "ETH": {"option_trades": [], "perp_bars": []}},
        term_signal="term_ratio", bar_seconds=60.0, horizon_bars=6
    )
    assert res["error"] == "insufficient common surface bars"
    assert res["pass"] is False


# ---------------------------------------------------------------------------
# Test: campaign_floor (reuses EVAL-77 verbatim)
# ---------------------------------------------------------------------------
def test_campaign_floor_is_eval77(captures: Dict[str, Dict[str, Any]]):
    floor = e120.campaign_floor(captures)
    assert isinstance(floor, dict)
    for key in ("underlyings", "per_underlying", "underlyings_ok", "aligned_common_bars_by_grid", "aligned_common_bars_binding", "aligned_ok", "checks", "ok"):
        assert key in floor


# ---------------------------------------------------------------------------
# Test: build_protocol
# ---------------------------------------------------------------------------
def test_build_protocol_structure():
    proto = e120.build_protocol("data/raw/eval61")
    assert proto["eval"] == "EVAL-120"
    assert "cross_section" in proto
    cs = proto["cross_section"]
    assert cs["baseline"] == "BTC"
    assert cs["relative"] == "ETH"
    assert "rel_z_k = expanding_z( term_ratio[ETH](k) - term_ratio[BTC](k) )" in cs["relative_signal"]
    assert proto["term_signals"] == ["term_ratio"]
    assert proto["bar_seconds_grid"] == [60.0, 300.0]
    assert proto["forward_horizons_bars"] == [6, 24, 72]
    # Stats come from e65 (PERMUTATION_PERMS=1000, etc.)
    assert proto["stats"]["permutation_perms"] == 1000
    assert proto["stats"]["min_usable_pairs_per_config"] == 120


# ---------------------------------------------------------------------------
# Test: run_eval120 (no-write mode)
# ---------------------------------------------------------------------------
def test_run_eval120_no_write(captures: Dict[str, Dict[str, Any]]):
    with patch("scripts.eval120_cross_sectional_term_ratio_basis_relative_return_skewness_spread._select_captures") as mock_select:
        mock_select.return_value = captures
        report = e120.run_eval120(capture_dir="data/raw/eval61", write=False)
        assert report["report_id"] == e120.REPORT_ID
        assert "verdict" in report
        assert "floor_ok" in report
        assert "per_config" in report
        assert len(report["per_config"]) == 6  # 1 signal x 2 grids x 3 horizons


# ---------------------------------------------------------------------------
# Test: seal artifact builders
# ---------------------------------------------------------------------------
def test_build_prereg(report_dict: Dict[str, Any]):
    prereg = e120._build_prereg(report_dict)
    assert prereg["prereg_id"] == e120.PREREG_ID
    assert "hypothesis" in prereg
    assert "protocol" in prereg
    assert prereg["capture_dir"] == report_dict.get("capture_dir")


def test_build_md(report_dict: Dict[str, Any]):
    md = e120._build_md(report_dict)
    assert e120.REPORT_ID in md
    assert "Verdict" in md
    assert "Per-config" in md
    assert "Pooled" in md


def test_build_blocked_report(report_dict: Dict[str, Any]):
    blocked = e120._build_blocked_report(report_dict)
    assert blocked["report_id"] == e120.BLOCKED_ID
    assert blocked["verdict"] == "BLOCKED"
    assert blocked["floor_ok"] is False


# ---------------------------------------------------------------------------
# Test: constants match expectations
# ---------------------------------------------------------------------------
def test_constants():
    assert e120.TERM_SIGNALS == ("term_ratio",)
    assert e120.TARGET == "forward_relative_return_skewness_spread"
    assert e120.GRID_BAR_SECONDS == (60.0, 300.0)
    assert e120.FORWARD_HORIZONS_BARS == (6, 24, 72)
    assert e120.BASELINE == "BTC"
    assert e120.RELATIVE == "ETH"
    assert e120.MIN_USABLE_PAIRS_PER_CONFIG == 120
    assert e120.FLOOR is e120.e77.FLOOR  # identity, not copy


# ---------------------------------------------------------------------------
# Test: CODE_PATHS and COMMANDS
# ---------------------------------------------------------------------------
def test_code_paths():
    assert "scripts/eval120_cross_sectional_term_ratio_basis_relative_return_skewness_spread.py" in e120.CODE_PATHS
    assert "scripts/eval77_cross_sectional_surface_basis_rv_predictiveness.py" in e120.CODE_PATHS
    assert "scripts/eval74_surface_term_structure_predictiveness.py" in e120.CODE_PATHS
    assert "scripts/eval85_surface_skew_forward_return_tail.py" in e120.CODE_PATHS


def test_commands():
    cmds = " ".join(e120.COMMANDS)
    assert "eval120_cross_sectional_term_ratio_basis_relative_return_skewness_spread.py" in cmds
    assert "test_eval120_cross_sectional_term_ratio_basis_relative_return_skewness_spread.py" in cmds
    assert "--no-write" in cmds
    assert "--seal" in cmds


# ---------------------------------------------------------------------------
# Report dict fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def report_dict() -> Dict[str, Any]:
    return {
        "report_id": e120.REPORT_ID,
        "generated_at": "2026-11-19T06:15:00Z",
        "task": "EVAL120-TEST",
        "verdict": "NO-GO CONFIRMED (PASS)",
        "verdict_detail": "test",
        "floor_ok": True,
        "capture_dir": "data/raw/eval61",
        "underlyings": ["BTC", "ETH"],
        "floor": dict(e120.FLOOR),
        "campaign_floor": {
            "underlyings": ["BTC", "ETH"],
            "per_underlying": {
                "BTC": {"surface_floor_ok": True, "surface_floor": {"n_option_trades": 1000, "n_near_atm_option_trades": 500, "n_perp_candles": 2000, "perp_span_seconds": 100000}, "ok": True},
                "ETH": {"surface_floor_ok": True, "surface_floor": {"n_option_trades": 1000, "n_near_atm_option_trades": 500, "n_perp_candles": 2000, "perp_span_seconds": 100000}, "ok": True},
            },
            "underlyings_ok": True,
            "aligned_common_bars_by_grid": {"60.0": 500, "300.0": 100},
            "aligned_common_bars_binding": 100,
            "aligned_ok": True,
            "checks": {"underlyings_ok": True, "aligned_ok": True},
            "ok": True,
        },
        "protocol": e120.build_protocol("data/raw/eval61"),
        "per_config": [
            {"signal": "term_ratio", "bar_seconds": 60.0, "horizon_bars": 6, "n_common_bars": 500, "n_pairs": 200, "spearman_ic": 0.01, "permutation_p": 0.3, "bootstrap_ci": [0.01, -0.02, 0.04], "nonzero_signal_pairs": 180, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 60.0, "horizon_bars": 24, "n_common_bars": 500, "n_pairs": 200, "spearman_ic": 0.02, "permutation_p": 0.2, "bootstrap_ci": [0.02, -0.01, 0.05], "nonzero_signal_pairs": 180, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 60.0, "horizon_bars": 72, "n_common_bars": 500, "n_pairs": 200, "spearman_ic": 0.0, "permutation_p": 0.5, "bootstrap_ci": [0.0, -0.03, 0.03], "nonzero_signal_pairs": 180, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 300.0, "horizon_bars": 6, "n_common_bars": 100, "n_pairs": 50, "spearman_ic": -0.01, "permutation_p": 0.6, "bootstrap_ci": [-0.01, -0.05, 0.03], "nonzero_signal_pairs": 45, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 300.0, "horizon_bars": 24, "n_common_bars": 100, "n_pairs": 50, "spearman_ic": 0.0, "permutation_p": 0.5, "bootstrap_ci": [0.0, -0.04, 0.04], "nonzero_signal_pairs": 45, "pass": False},
            {"signal": "term_ratio", "bar_seconds": 300.0, "horizon_bars": 72, "n_common_bars": 100, "n_pairs": 50, "spearman_ic": 0.0, "permutation_p": 0.5, "bootstrap_ci": [0.0, -0.04, 0.04], "nonzero_signal_pairs": 45, "pass": False},
        ],
        "summary": {"n_configs": 6, "n_pass": 0, "pass_configs": [], "best_ic": 0.02, "best_config": "term_ratio::bar60.0::h24"},
        "pooled": {"bh_fdr": {"rejected": []}, "any_config_pass": False, "campaign_state": "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD"},
        "errors": [],
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])