"""Numeric-invariant tests for EVAL-22 real-tape ingestion gate.

Covers discovery filtering, provenance/adequacy verdicts, microstructure and
timestamp validation, causal time-truncation invariance, row-order determinism,
strict serialization, and CLI/artifact emission. All tests use synthetic fixtures
written to temp dirs (paper-only, offline, no network).
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.analytics.measurement_validity_evaluation import (
    DEFAULT_MIN_RETURNS,
    DEFAULT_MIN_WINDOWS,
)
from src.analytics.real_tape_ingestion import (
    CANONICAL_SYNTHETIC_SHA256,
    RealTapeRejected,
    assert_causal_time_truncation,
    discover_real_orderflow_tapes,
    evaluate_candidate,
    evaluate_real_tape_ingestion,
    load_real_tape,
    main as cli_main,
)
from src.analytics.sample_adequacy_acquisition import build_synthetic_orderflow_tape
from src.telemetry.serialization import assert_json_valid


def _write_tape(path: Path, trades, venue="binance", symbol="BTCUSDT") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"trades": trades, "venue": venue, "symbol": symbol, "liquidations": [], "funding_rates": []}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _real_trades(n: int = 40, start=None, step_seconds: int = 5):
    start = start or datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    trades = []
    price = 50000.0
    for i in range(n):
        side = "buy" if i % 2 == 0 else "sell"
        price += 0.5 if side == "buy" else -0.25
        trades.append(
            {
                "trade_id": f"r{i:05d}",
                "timestamp": (start + timedelta(seconds=i * step_seconds)).isoformat().replace("+00:00", "Z"),
                "price": round(price, 2),
                "size": 0.1 + (i % 3) * 0.01,
                "side": side,
            }
        )
    return trades


def _real_path(data_dir: Path, name: str = "orderflow_binance_BTCUSDT.json", n: int = 40, step_seconds: int = 5):
    return _write_tape(data_dir / name, _real_trades(n=n, step_seconds=step_seconds))


# --- discovery ---


def test_discovery_excludes_synthetic_and_includes_real(tmp_path):
    _write_tape(tmp_path / "orderflow_btcusdt_synthetic.json", _real_trades(20), venue="synthetic")
    _write_tape(tmp_path / "orderflow_binance_BTCUSDT_synthetic.json", _real_trades(20), venue="binance")
    real = _real_path(tmp_path, "orderflow_binance_BTCUSDT.json")
    _write_tape(tmp_path / "options_binance_BTCUSDT.json", _real_trades(20))
    found = discover_real_orderflow_tapes(tmp_path)
    assert found == [real]


def test_discovery_sorted(tmp_path):
    _real_path(tmp_path, "orderflow_okx_BTCUSDT.json")
    _real_path(tmp_path, "orderflow_binance_BTCUSDT.json")
    names = [p.name for p in discover_real_orderflow_tapes(tmp_path)]
    assert names == sorted(names)


# --- loading / provenance ---


def test_load_real_tape_provenance(tmp_path):
    path = _real_path(tmp_path)
    snap, prov = load_real_tape(path)
    assert prov["kind"] == "real"
    assert prov["venue"] == "binance"
    assert prov["symbol"] == "BTCUSDT"
    assert prov["path"] == str(path)
    assert prov["n_trades"] == len(snap.trades)
    assert len(prov["content_sha256"]) == 64
    assert prov["content_sha256"] != CANONICAL_SYNTHETIC_SHA256
    assert len(prov["tape_fingerprint_canonical"]) == 64
    assert prov["span_seconds"] > 0


def test_load_rejects_synthetic_venue(tmp_path):
    # filename venue parsed as 'synthetic' -> rejected even if called directly
    path = _write_tape(tmp_path / "orderflow_synthetic_BTCUSDT.json", _real_trades(20, step_seconds=5), venue="binance")
    with pytest.raises(RealTapeRejected):
        load_real_tape(path)


def test_load_rejects_empty(tmp_path):
    path = _write_tape(tmp_path / "orderflow_binance_BTCUSDT.json", [])
    with pytest.raises(RealTapeRejected):
        load_real_tape(path)


def test_load_rejects_bad_filename(tmp_path):
    path = tmp_path / "orderflow__BTCUSDT.json"
    path.write_text(json.dumps({"trades": _real_trades(20), "venue": "binance", "symbol": "BTCUSDT"}), encoding="utf-8")
    with pytest.raises(RealTapeRejected):
        load_real_tape(path)


def test_load_rejects_unparseable_timestamp(tmp_path):
    trades = _real_trades(20)
    trades[3]["timestamp"] = "not-a-date"
    path = _write_tape(tmp_path / "orderflow_binance_BTCUSDT.json", trades)
    with pytest.raises(RealTapeRejected):
        load_real_tape(path)


def test_microstructure_rejects_bad_price_size_side(tmp_path):
    base = _real_trades(20)
    bad_price = list(base); bad_price[1] = {**base[1], "price": -1}
    with pytest.raises(RealTapeRejected):
        load_real_tape(_write_tape(tmp_path / "orderflow_binance_BTCUSDT.json", bad_price))
    bad_size = list(base); bad_size[1] = {**base[1], "size": 0}
    with pytest.raises(RealTapeRejected):
        load_real_tape(_write_tape(tmp_path / "orderflow_binance_BTCUSDT.json", bad_size))
    bad_side = list(base); bad_side[1] = {**base[1], "side": "unknown"}
    with pytest.raises(RealTapeRejected):
        load_real_tape(_write_tape(tmp_path / "orderflow_binance_BTCUSDT.json", bad_side))


# --- causal no-lookahead: time-truncation invariance ---


def test_causal_time_truncation_invariance():
    snap = build_synthetic_orderflow_tape(
        n_bars=120, trades_per_bar=10, bar_duration_seconds=15.0,
        start=datetime(2026, 1, 1, tzinfo=timezone.utc), seed=7,
    )
    assert assert_causal_time_truncation(snap.trades, 15.0) is True


# --- row-order invariance / determinism ---


def test_row_order_invariance_same_artifact(tmp_path):
    trades = _real_trades(60)
    p1 = _write_tape(tmp_path / "a" / "orderflow_binance_BTCUSDT.json", list(trades))
    p2 = _write_tape(tmp_path / "b" / "orderflow_binance_BTCUSDT.json", list(reversed(trades)))
    r1 = evaluate_candidate(p1, timestamp="2026-11-13T00:00:00Z")
    r2 = evaluate_candidate(p2, timestamp="2026-11-13T00:00:00Z")
    assert r1["provenance"]["tape_fingerprint_canonical"] == r2["provenance"]["tape_fingerprint_canonical"]
    assert r1["bars"] == r2["bars"]
    assert r1["verdict"] == r2["verdict"]
    if "determinism" in r1:
        assert r1["determinism"] == r2["determinism"]


# --- adequacy / verdict ---


def test_inadequate_real_tape_nogo_with_shortfall(tmp_path):
    path = _real_path(tmp_path, n=40)
    res = evaluate_candidate(path, timestamp="2026-11-13T00:00:00Z")
    assert res["real_tape_loaded"] is True
    assert res["provenance"]["kind"] == "real"
    assert res["verdict"] == "NO-GO"
    assert res["adequacy"]["n_returns"] < DEFAULT_MIN_RETURNS or res["adequacy"]["n_windows"] < DEFAULT_MIN_WINDOWS
    assert res["bars"]["shortfall_returns"] == max(0, DEFAULT_MIN_RETURNS - res["adequacy"]["n_returns"])
    assert res["bars"]["shortfall_windows"] == max(0, DEFAULT_MIN_WINDOWS - res["adequacy"]["n_windows"])
    assert res["causal_no_lookahead"] is True
    assert res["microstructure_sane"] is True


def test_overall_no_real_tapes_nogo(tmp_path):
    snap = build_synthetic_orderflow_tape(n_bars=5, trades_per_bar=10, start=datetime(2026, 1, 1, tzinfo=timezone.utc), seed=1)
    trades = [
        {"trade_id": t.trade_id, "timestamp": t.timestamp.isoformat().replace("+00:00", "Z"), "price": t.price, "size": t.size, "side": t.side}
        for t in snap.trades
    ]
    _write_tape(tmp_path / "orderflow_btcusdt_synthetic.json", trades, venue="synthetic")
    report = evaluate_real_tape_ingestion(write=False, data_dir=tmp_path, timestamp="2026-11-13T00:00:00Z")
    assert report["overall_verdict"] == "NO-GO"
    assert report["n_candidates"] == 0
    assert report["n_adequate"] == 0
    assert report["data_provenance"] == "real"
    assert report["overall_reason"] == "no adequate real tape; synthetic never substituted"


# --- strict serialization and no {"valid": true} ---


def test_strict_serialization_no_valid_true(tmp_path):
    _real_path(tmp_path, n=40)
    report = evaluate_real_tape_ingestion(write=False, data_dir=tmp_path, timestamp="2026-11-13T00:00:00Z")
    text = json.dumps(report, sort_keys=True, allow_nan=False)
    assert '"valid"' not in text
    assert_json_valid(report)


def test_determinism_two_runs_byte_identical(tmp_path):
    _real_path(tmp_path, n=40)
    r1 = evaluate_real_tape_ingestion(write=False, data_dir=tmp_path, timestamp="2026-11-13T00:00:00Z")
    r2 = evaluate_real_tape_ingestion(write=False, data_dir=tmp_path, timestamp="2026-11-13T00:00:00Z")
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)


# --- CLI writes artifacts ---


def test_cli_writes_json_and_md(tmp_path):
    data_dir = tmp_path / "raw"
    out_dir = tmp_path / "out"
    data_dir.mkdir()
    _real_path(data_dir, n=40)
    rc = cli_main(["--out", str(out_dir), "--data-dir", str(data_dir), "--timestamp", "2026-11-13T00:00:00Z"])
    assert rc == 0
    jsons = list(out_dir.glob("REAL_TAPE_INGESTION_*.json"))
    mds = list(out_dir.glob("REAL_TAPE_INGESTION_*.md"))
    assert len(jsons) == 1 and len(mds) == 1
    payload = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert payload["overall_verdict"] == "NO-GO"
    assert payload["report_id"] == "REAL_TAPE_INGESTION_22"
    assert "NO-GO" in mds[0].read_text(encoding="utf-8")
