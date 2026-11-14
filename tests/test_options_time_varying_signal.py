"""Tests for src/analytics/options_time_varying_signal.py (EVAL-30)."""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.analytics.options_time_varying_signal import (
    SnapshotSignal,
    ExpirySignalPoint,
    snapshot_options_signal,
    load_snapshot_signals,
    align_options_signal_to_bars,
    measure_time_varying_signal,
    build_eval30_report,
    write_eval30_artifact,
    DEFAULT_WEIGHTS,
    MIN_SIGNAL_STDEV,
    MIN_ABS_IC,
)
from src.campaign.integrated import RealDataUnavailable


def test_causality_no_lookahead_alignment():
    """Bar uses newest snapshot with timestamp <= bar_end; no future data."""
    ts_base = datetime(2026, 11, 14, 9, 30, 0, tzinfo=timezone.utc)
    sig1 = SnapshotSignal(
        path="", content_sha256="", snapshot_timestamp=(ts_base).isoformat().replace("+00:00", "Z"),
        n_expiries=1, n_iv_points=1, forward_curve_slope=0.0, atm_iv_term_slope=0.0,
        iv_skew=0.0, put_call_ratio=1.0, components={}, options_signal_raw=0.1,
        points=[], warnings=[]
    )
    sig2 = SnapshotSignal(
        path="", content_sha256="", snapshot_timestamp=(ts_base + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        n_expiries=1, n_iv_points=1, forward_curve_slope=0.0, atm_iv_term_slope=0.0,
        iv_skew=0.0, put_call_ratio=1.0, components={}, options_signal_raw=0.5,
        points=[], warnings=[]
    )

    bar_ends = [
        ts_base - timedelta(minutes=1),  # before first snapshot -> flat
        ts_base + timedelta(minutes=1),  # between snapshots -> sig1
        ts_base + timedelta(minutes=6),  # after second snapshot -> sig2
    ]

    aligned = align_options_signal_to_bars([sig1, sig2], bar_ends)
    assert aligned["signals"][0] == 0.0  # flat before first
    assert aligned["signals"][1] == 0.1  # sig1 value
    assert aligned["signals"][2] == 0.5  # sig2 value


def test_oldest_first_snapshot_ordering():
    """load_snapshot_signals returns snapshots sorted oldest-first."""
    signals = load_snapshot_signals("BTC")
    timestamps = [s.snapshot_timestamp for s in signals]
    assert timestamps == sorted(timestamps), "snapshots not sorted oldest-first"


def test_flat_pre_first_snapshot():
    """Bars before the first snapshot get signal 0.0 (flat)."""
    ts = datetime(2026, 11, 14, 10, 0, 0, tzinfo=timezone.utc)
    sig = SnapshotSignal(
        path="", content_sha256="", snapshot_timestamp=ts.isoformat().replace("+00:00", "Z"),
        n_expiries=1, n_iv_points=1, forward_curve_slope=0.0, atm_iv_term_slope=0.0,
        iv_skew=0.0, put_call_ratio=1.0, components={}, options_signal_raw=0.7,
        points=[], warnings=[]
    )
    bar_ends = [ts - timedelta(minutes=1), ts + timedelta(minutes=1)]
    aligned = align_options_signal_to_bars([sig], bar_ends)
    assert aligned["signals"][0] == 0.0
    assert aligned["signals"][1] == 0.7
    assert aligned["n_flat_bars"] == 1


def test_real_data_unavailable_invariant():
    """load_snapshot_signals raises RealDataUnavailable when no real exports exist."""
    with pytest.raises(RealDataUnavailable):
        load_snapshot_signals("NONEXISTENT_SYMBOL", data_raw=Path("data/raw"))


def test_component_signal_parity_deterministic_fixture():
    """snapshot_options_signal produces deterministic output on a fixed fixture."""
    from src.data.loader import DataLoader
    loader = DataLoader(cache=False)
    chain = loader.load_options_chain(
        "data/raw/options_okx_BTC_20261114T093032Z.json",
        venue="okx",
        underlying="BTC"
    )
    ts = datetime.fromisoformat("2026-11-14T09:30:33.038452+00:00")
    spot = 90000.0

    sig1 = snapshot_options_signal(chain, spot, ts, weights=DEFAULT_WEIGHTS, source_path="data/raw/options_okx_BTC_20261114T093032Z.json")
    sig2 = snapshot_options_signal(chain, spot, ts, weights=DEFAULT_WEIGHTS, source_path="data/raw/options_okx_BTC_20261114T093032Z.json")

    assert sig1.options_signal_raw == sig2.options_signal_raw
    assert sig1.forward_curve_slope == sig2.forward_curve_slope
    assert sig1.atm_iv_term_slope == sig2.atm_iv_term_slope
    assert sig1.iv_skew == sig2.iv_skew
    assert sig1.put_call_ratio == sig2.put_call_ratio
    for k in DEFAULT_WEIGHTS:
        assert sig1.components[k] == sig2.components[k]


def test_measure_time_varying_signal_non_constant_and_ic():
    """measure_time_varying_signal correctly computes non_constant and ic_present."""
    ts_base = datetime(2026, 11, 14, 9, 30, 0, tzinfo=timezone.utc)
    signals = [
        SnapshotSignal(
            path="", content_sha256="", snapshot_timestamp=(ts_base).isoformat().replace("+00:00", "Z"),
            n_expiries=1, n_iv_points=1, forward_curve_slope=0.0, atm_iv_term_slope=0.0,
            iv_skew=0.0, put_call_ratio=1.0, components={}, options_signal_raw=-0.03,
            points=[], warnings=[]
        ),
        SnapshotSignal(
            path="", content_sha256="", snapshot_timestamp=(ts_base + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            n_expiries=1, n_iv_points=1, forward_curve_slope=0.0, atm_iv_term_slope=0.0,
            iv_skew=0.0, put_call_ratio=1.0, components={}, options_signal_raw=0.04,
            points=[], warnings=[]
        ),
    ]
    bar_ends = [ts_base + timedelta(minutes=i) for i in range(10)]
    bar_closes = [100.0 + i * 0.1 for i in range(10)]  # trending up

    m = measure_time_varying_signal(signals, bar_ends, bar_closes, horizons=(1, 5))
    assert m["non_constant"] is True
    assert m["distinct_signal_values"] >= 2
    assert m["step_changes"] >= 1
    assert "ic_by_horizon" in m
    assert "ic_tstat_by_horizon" in m


def test_build_eval30_report_structure():
    """build_eval30_report returns a complete strict-serializable report."""
    from src.campaign.integrated import load_real_orderflow
    from src.analytics.integrated_options_orderflow_evaluation import _build_bars

    snap = load_real_orderflow("BTC")
    bars = _build_bars(snap)
    report = build_eval30_report(symbol="BTC", orderflow_bars=bars)

    assert report["report_id"] == "OPTIONS_LEG_TRADABILITY_30"
    assert report["verdict"] in ("GO", "NO-GO")
    assert "measurement" in report
    assert "checks" in report
    assert "snapshots" in report
    assert len(report["snapshots"]) == 3
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["never_valid_true"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])