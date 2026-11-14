"""Focused unit tests for the EVAL-45 ETH multi-window acquisition helpers.

These cover only the pure, deterministic helpers: window naming, page/target
arithmetic, floor validation and disjointness checks. They do not touch the
network; the live acquisition is exercised by the script itself.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "eval45_acquire_eth_windows.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("eval45_acquire_eth_windows", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def _trades(n: int, *, start_id: int = 1000, start_ms: int = 1_700_000_000_000,
            step_ms: int = 1000):
    return [
        {
            "trade_id": str(start_id + i),
            "instrument": "ETH-USD-SWAP",
            "price": 3000.0 + i,
            "size": 1.0,
            "side": "buy",
            "timestamp_ms": start_ms + i * step_ms,
            "timestamp": "2026-11-14T00:00:00.000000Z",
        }
        for i in range(n)
    ]


def test_window_filename_is_loader_discoverable_and_refuses_synthetic() -> None:
    name = mod.window_filename("orderflow_okx", "ETH", 3, "507944976")
    assert name == "orderflow_okx_ETH_w03_507944976.json"
    assert name.lower().startswith("orderflow_")
    assert "synthetic" not in name.lower()

    with pytest.raises(mod.AcquisitionError):
        mod.window_filename("orderflow_synthetic", "ETH", 1, "1")


def test_required_pages_rounds_up() -> None:
    assert mod.required_pages(35000, 100) == 350
    assert mod.required_pages(1, 100) == 1
    assert mod.required_pages(101, 100) == 2
    assert mod.required_pages(10, 0) == 10  # page limit floored at 1


def test_estimate_min_bars_uses_measured_rate() -> None:
    # 100 trades in 1000 s -> 0.1 trades/s; 35,000 trades needs 350,000 s.
    bars = mod.estimate_min_bars(1000.0, 100, bar_duration_seconds=15.0, target_trades=35000)
    assert bars == 23334

    assert mod.estimate_min_bars(0.0, 0, bar_duration_seconds=15.0, target_trades=10) == 1


def test_validate_window_accepts_and_measures() -> None:
    trades = _trades(35000, start_ms=1_700_000_000_000, step_ms=15_000)
    facts = mod.validate_window(
        trades=trades, min_trades=35000, min_bars=420, bar_duration_seconds=15.0
    )
    assert facts["n_trades"] == 35000
    assert facts["n_bars"] == 34999  # one trade per 15 s bar
    assert facts["first_trade_id"] == "1000"
    assert facts["last_trade_id"] == str(1000 + 34999)
    assert facts["span_seconds"] == 34999 * 15.0


def test_validate_window_rejects_short_window() -> None:
    with pytest.raises(mod.AcquisitionError, match="trades < required"):
        mod.validate_window(
            trades=_trades(10), min_trades=35000, min_bars=1, bar_duration_seconds=15.0
        )


def test_validate_window_rejects_short_span() -> None:
    trades = _trades(35000, step_ms=100)
    with pytest.raises(mod.AcquisitionError, match="bars < required"):
        mod.validate_window(
            trades=trades, min_trades=35000, min_bars=420, bar_duration_seconds=15.0
        )


def test_validate_window_rejects_duplicate_ids() -> None:
    trades = _trades(100)
    trades[5] = dict(trades[4])
    with pytest.raises(mod.AcquisitionError, match="duplicate trade ids"):
        mod.validate_window(
            trades=trades, min_trades=1, min_bars=1, bar_duration_seconds=15.0
        )


def test_assert_disjoint_accepts_chained_cursor_and_strictly_older() -> None:
    previous = {"first_trade_id": "500", "newest_timestamp_ms": 2000,
                "trade_ids": ["500", "501"]}
    current = {"after_cursor": "500", "newest_timestamp_ms": 1500,
               "trade_ids": ["1", "2"]}
    out = mod.assert_disjoint(previous, current)
    assert out["disjoint"] is True
    assert out["overlap_trade_ids"] == 0


def test_assert_disjoint_rejects_overlap() -> None:
    previous = {"first_trade_id": "500", "newest_timestamp_ms": 2000,
                "trade_ids": ["1", "2"]}
    current = {"after_cursor": "500", "newest_timestamp_ms": 1500,
               "trade_ids": ["2", "3"]}
    with pytest.raises(mod.AcquisitionError, match="overlap"):
        mod.assert_disjoint(previous, current)


def test_assert_disjoint_rejects_wrong_cursor_and_newer_window() -> None:
    previous = {"first_trade_id": "500", "newest_timestamp_ms": 2000,
                "trade_ids": ["1"]}
    with pytest.raises(mod.AcquisitionError, match="cursor"):
        mod.assert_disjoint(previous, {"after_cursor": "999", "newest_timestamp_ms": 1,
                                       "trade_ids": ["2"]})
    with pytest.raises(mod.AcquisitionError, match="strictly older"):
        mod.assert_disjoint(previous, {"after_cursor": "500", "newest_timestamp_ms": 2001,
                                       "trade_ids": ["2"]})


def test_build_report_is_acquisition_only_and_finite() -> None:
    window = {
        "window": 1, "path": "data/raw/x.json", "sha256": "a" * 64,
        "inst_id": "ETH-USD-SWAP", "symbol": "ETH", "after_cursor": None,
        "target_bars": 420, "attempts": [], "pages": 350, "loader_trades": 35000,
        "loader_ok": True, "oldest_timestamp_ms": 1, "newest_timestamp_ms": 2,
        "n_trades": 35000, "n_bars": 420, "span_seconds": 6300.0,
        "first_trade_id": "1", "last_trade_id": "35000",
        "first_trade_utc": "2026-11-14T00:00:00.000000Z",
        "last_trade_utc": "2026-11-14T01:45:00.000000Z",
        "disjointness": {"disjoint": True, "overlap_trade_ids": 0,
                         "after_cursor": None, "strictly_older": True},
    }
    report = mod.build_report(
        generated_at="2026-11-14T23:50:00.000000Z",
        inst_id="ETH-USD-SWAP", symbol="ETH", windows=[window],
        total_trades=35000, bar_duration_seconds=15.0, min_bars=420, min_trades=35000,
    )
    assert report["artifact_kind"] == "data_acquisition"
    assert report["verdict"] == "DATA_ACQUIRED_NO_MEASUREMENT"
    assert report["all_floors_met"] is True
    assert report["all_windows_disjoint"] is True
    assert "trade_ids" not in report["windows"][0]
    assert mod._all_finite(report)