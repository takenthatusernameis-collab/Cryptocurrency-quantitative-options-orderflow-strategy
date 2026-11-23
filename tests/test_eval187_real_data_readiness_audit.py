"""Unit tests for the EVAL-187 real-data readiness audit."""

from __future__ import annotations

import json
from pathlib import Path

import scripts.eval187_real_data_readiness_audit as audit


def _capture(
    *,
    underlying: str = "BTC",
    snapshots: int = 1,
    quotes: int = 1,
    option_trades: int = 1,
    perp_candles: int = 1,
    okx_perp_trades: int = 1,
    public_read_only: bool = True,
    authenticated: bool = False,
    spot: object = 60000.0,
) -> dict:
    surface_snapshots = []
    for i in range(snapshots):
        surface_quotes = []
        for j in range(quotes):
            surface_quotes.append(
                {
                    "symbol": f"{underlying}-TEST-{i}-{j}",
                    "bid": 0.01,
                    "ask": 0.02,
                    "mark": 0.015,
                    "bid_iv": 0.5,
                    "ask_iv": 0.6,
                    "mark_iv": 0.55,
                }
            )
        surface_snapshots.append({"bar_ms": 1700000000000 + i * 300000, "spot": spot, "quotes": surface_quotes})
    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": underlying,
        "venue": "deribit+okx",
        "window_start": "2026-11-22T07:12:00Z",
        "window_end": "2026-11-26T00:00:00Z",
        "perp_resolution": "1",
        "surface": {"bar_seconds": 300, "resolution": "5", "snapshots": surface_snapshots},
        "option_trades": [
            {
                "ts": 1700000000000 + i * 1000,
                "instrument": f"{underlying}-TEST-{i}",
                "price": 0.01,
                "amount": 1.0,
            }
            for i in range(option_trades)
        ],
        "perp_candles": [
            {
                "ts": 1700000000000 + i * 60000,
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 1.5,
            }
            for i in range(perp_candles)
        ],
        "okx_inst_id": f"{underlying}-USD-SWAP",
        "okx_perp_trades": [
            {
                "ts": 1700000000000 + i * 1000,
                "instrument": f"{underlying}-USD-SWAP",
                "px": 1.0,
                "sz": 1.0,
            }
            for i in range(okx_perp_trades)
        ],
        "source": {"public_read_only": public_read_only, "authenticated": authenticated},
    }


def _write_capture(capture_root: Path, name: str, payload: dict) -> Path:
    capture_root.mkdir(parents=True, exist_ok=True)
    path = capture_root / name
    path.write_text(json.dumps(payload))
    return path


def test_audit_ok_capture(tmp_path):
    path = _write_capture(tmp_path, "three_way_BTC_test.json", _capture())
    row = audit._audit_capture(path)
    assert row["status"] == audit.STATUS_OK
    assert row["underlying"] == "BTC"
    assert row["n_surface_snapshots"] == 1
    assert row["n_option_trades"] == 1
    assert row["n_perp_candles"] == 1
    assert row["n_okx_perp_trades"] == 1
    assert row["issues"] == []


def test_audit_sparse_capture(tmp_path):
    path = _write_capture(
        tmp_path,
        "three_way_BTC_test.json",
        _capture(okx_perp_trades=0),
    )
    row = audit._audit_capture(path)
    assert row["status"] == audit.STATUS_SPARSE
    assert "okx_perp_trades_empty" in row["issues"]


def test_audit_degenerate_capture(tmp_path):
    payload = _capture(snapshots=0, quotes=0, option_trades=0, perp_candles=0, okx_perp_trades=0)
    path = _write_capture(tmp_path, "three_way_BTC_test.json", payload)
    row = audit._audit_capture(path)
    assert row["status"] == audit.STATUS_DEGENERATE
    assert "surface_snapshots_empty" in row["issues"]
    assert "option_trades_empty" in row["issues"]
    assert "perp_candles_empty" in row["issues"]
    assert "okx_perp_trades_empty" in row["issues"]


def test_audit_error_capture(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "three_way_BTC_test.json"
    path.write_text("{not-json")
    row = audit._audit_capture(path)
    assert row["status"] == audit.STATUS_ERROR
    assert any(issue.startswith("json_parse_error") for issue in row["issues"])


def test_report_is_non_verdict_and_writes_rolling(tmp_path):
    capture_root = tmp_path / "raw"
    forward_dir = tmp_path / "forward"
    _write_capture(capture_root, "three_way_BTC_test.json", _capture())
    _write_capture(forward_dir, "three_way_BTC_test.json", _capture())
    report = audit.build_report(capture_root=capture_root, forward_dir=forward_dir)
    assert report["is_verdict_rung"] is False
    assert report["audit_status"] == "PASS"
    assert report["summary"]["capture_count"] == 1
    assert report["forward_capture"]["all_ok"] is True
    assert "verdict" not in report
    assert report["is_verdict_rung"] is False