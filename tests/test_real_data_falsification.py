"""Numeric-invariant tests for EVAL-25 real-data falsification-readiness gate.

Covers discovery (synthetic exclusion, ordering), orderflow and option-candidate
loading, EVAL-22 / EVAL-24 adequacy counts and shortfalls, rejection isolation,
strict serialization (no ``{"valid": true}``), determinism, CLI artifact
emission, the offline guarantee, and the measured repo state (data/raw yields
0 real candidates). All fixtures are temp-dir files; paper-only, offline, no
network.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.analytics.real_data_falsification import (
    REPORT_ID,
    _discover_candidates,
    _parse_options_name,
    _parse_orderflow_name,
    evaluate_real_data_falsification,
    main as cli_main,
)

START = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
EXP1 = datetime(2026, 1, 30, 8, 0, 0, tzinfo=timezone.utc)
EXP2 = datetime(2026, 2, 27, 8, 0, 0, tzinfo=timezone.utc)
FIXED_TS = "2026-11-14T00:45:00Z"


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _orderflow_trades(n: int = 5, seconds_span: int = 4) -> list:
    trades = []
    price = 50000.0
    for i in range(n):
        side = "buy" if i % 2 == 0 else "sell"
        price += 0.5 if side == "buy" else -0.25
        trades.append(
            {
                "trade_id": f"r{i:05d}",
                "timestamp": _iso(START),
                "price": round(price, 2),
                "size": 0.1 + (i % 3) * 0.01,
                "side": side,
            }
        )
    return trades


def _write_orderflow(path: Path, trades, venue: str = "binance", symbol: str = "BTCUSDT") -> Path:
    _write(path, json.dumps({"trades": trades, "venue": venue, "symbol": symbol}))
    return path


def _option_quotes(n: int = 8, expiries: tuple = (EXP1, EXP2)) -> list:
    quotes = []
    strikes = [60000 + i * 1000 for i in range(n)]
    for i, strike in enumerate(strikes):
        expiry = expiries[i % len(expiries)]
        quotes.append(
            {
                "symbol": f"BTC-{int(expiry.strftime('%y%m%d'))}-{strike}-C",
                "underlying": "BTC",
                "strike": float(strike),
                "expiry": _iso(expiry),
                "option_type": "call",
                "bid": 100.0,
                "ask": 110.0,
                "mark": 105.0,
                "timestamp": _iso(START),
                "contract_size": 1.0,
            }
        )
    return quotes


def _write_options(path: Path, quotes) -> Path:
    _write(path, json.dumps({"quotes": quotes}))
    return path


def _run_gate(data_dir: Path, out_dir: Path, write: bool = True) -> dict:
    return evaluate_real_data_falsification(
        repo_root=".",
        write=write,
        out_dir=out_dir,
        data_dir=data_dir,
        timestamp=FIXED_TS,
    )


# --- discovery ---


def test_discovery_finds_orderflow_and_options_excludes_synthetic_sorted(tmp_path):
    _write_orderflow(tmp_path / "orderflow_binance_BTCUSDT.json", _orderflow_trades())
    _write_orderflow(tmp_path / "orderflow_okx_ETHUSDT.json", _orderflow_trades())
    _write_options(tmp_path / "options_deribit_BTC_20260115T000000Z.json", _option_quotes())
    _write_orderflow(tmp_path / "orderflow_btcusdt_synthetic.json", _orderflow_trades(), venue="synthetic")
    _write_options(tmp_path / "options_binance_BTC_synthetic.json", _option_quotes())
    (tmp_path / "notes.txt").write_text("not a candidate\n", encoding="utf-8")
    found = [p.name for p in _discover_candidates(tmp_path)]
    assert found == sorted(found)
    assert found == [
        "options_deribit_BTC_20260115T000000Z.json",
        "orderflow_binance_BTCUSDT.json",
        "orderflow_okx_ETHUSDT.json",
    ]


def test_discovery_empty_or_missing_dir_returns_empty(tmp_path):
    assert _discover_candidates(tmp_path / "nonexistent") == []
    assert _discover_candidates(tmp_path / "empty") == []
    (tmp_path / "empty").mkdir()
    assert _discover_candidates(tmp_path / "empty") == []


def test_filename_parsers():
    venue, symbol = _parse_orderflow_name(Path("orderflow_okx_ETHUSDT.json"))
    assert venue == "okx" and symbol == "ETHUSDT"
    venue, symbol = _parse_orderflow_name(Path("orderflow_binance_BTC_USDT.json"))
    assert venue == "binance" and symbol == "BTC_USDT"
    venue, underlying = _parse_options_name(Path("options_deribit_BTC_20260115T000000Z.json"))
    assert venue == "deribit" and underlying == "BTC"


# --- orderflow candidate: below adequacy floor ---


def test_orderflow_candidate_below_floor_counts_and_verdict(tmp_path):
    path = _write_orderflow(tmp_path / "orderflow_binance_BTCUSDT.json", _orderflow_trades(n=5))
    report = _run_gate(tmp_path, tmp_path / "out")
    assert report["n_candidates"] == 1
    assert report["n_orderflow_candidates"] == 1
    assert report["n_options_candidates"] == 0
    assert report["n_adequate_orderflow"] == 0
    assert report["n_adequate_options"] == 0
    assert report["overall_verdict"] == "NO-GO"
    c = report["candidates"][0]
    assert c["kind"] == "orderflow"
    assert c["loaded"] is True
    assert c["venue"] == "binance"
    assert c["symbol"] == "BTCUSDT"
    assert len(c["content_sha256"]) == 64
    assert c["provenance"]["n_trades"] == 5
    ta = c["trade_adequacy"]
    assert ta["n_returns"] == 0
    assert ta["n_windows"] == 0
    assert ta["sample_adequate"] is False
    assert ta["shortfall_returns"] == 1000
    assert ta["shortfall_windows"] == 20
    assert c["verdict"] == "NO-GO"
    assert c["verdict_reason"].startswith("orderflow tape below EVAL-22")


def test_orderflow_candidate_unreadable_json_is_isolated(tmp_path):
    path = tmp_path / "orderflow_binance_BTCUSDT.json"
    path.write_text("{ not valid json", encoding="utf-8")
    report = _run_gate(tmp_path, tmp_path / "out")
    c = report["candidates"][0]
    assert c["loaded"] is False
    assert c["rejection_reason"] is not None
    assert c["verdict"] == "NO-GO"
    assert report["overall_verdict"] == "NO-GO"


def test_synthetic_orderflow_filename_excluded(tmp_path):
    _write_orderflow(tmp_path / "orderflow_btcusdt_synthetic.json", _orderflow_trades(), venue="synthetic")
    report = _run_gate(tmp_path, tmp_path / "out")
    assert report["n_candidates"] == 0
    assert report["overall_verdict"] == "NO-GO"
    assert "no real-data candidates" in report["overall_reason"]


# --- options candidate: adequacy counts and shortfalls ---


def test_options_candidate_adequate_go(tmp_path):
    path = _write_options(tmp_path / "options_deribit_BTC_20260115T000000Z.json", _option_quotes())
    report = _run_gate(tmp_path, tmp_path / "out")
    assert report["n_candidates"] == 1
    assert report["n_options_candidates"] == 1
    assert report["n_adequate_options"] == 1
    c = report["candidates"][0]
    assert c["kind"] == "options"
    assert c["loaded"] is True
    assert c["venue"] == "deribit"
    assert c["underlying"] == "BTC"
    oa = c["option_adequacy"]
    assert oa["n_quotes"] == 8
    assert oa["n_contracts"] == 8
    assert oa["n_expiries"] == 2
    assert oa["sample_adequate"] is True
    assert oa["shortfall_contracts"] == 0
    assert oa["shortfall_quotes"] == 0
    assert oa["shortfall_expiries"] == 0
    assert c["verdict"] == "GO"
    assert c["verdict_reason"].startswith("option chain clears EVAL-24")


def test_options_candidate_inadequate_shortfall(tmp_path):
    quotes = _option_quotes(n=3, expiries=(EXP1,))  # 3 quotes, 3 contracts, 1 expiry
    path = _write_options(tmp_path / "options_okx_BTC_20260115T000000Z.json", quotes)
    report = _run_gate(tmp_path, tmp_path / "out")
    c = report["candidates"][0]
    oa = c["option_adequacy"]
    assert oa["n_quotes"] == 3
    assert oa["n_contracts"] == 3
    assert oa["n_expiries"] == 1
    assert oa["sample_adequate"] is False
    assert oa["shortfall_contracts"] == 5
    assert oa["shortfall_quotes"] == 5
    assert oa["shortfall_expiries"] == 1
    assert c["verdict"] == "NO-GO"
    assert report["overall_verdict"] == "NO-GO"


def test_options_candidate_bad_shape_is_isolated(tmp_path):
    path = tmp_path / "options_okx_BTC_20260115T000000Z.json"
    path.write_text(json.dumps({"quotes": "not-a-list"}), encoding="utf-8")
    report = _run_gate(tmp_path, tmp_path / "out")
    c = report["candidates"][0]
    assert c["loaded"] is False
    assert c["rejection_reason"] is not None
    assert c["verdict"] == "NO-GO"


# --- serialization / artifact / determinism / offline ---


def test_report_strict_no_valid_true(tmp_path):
    _write_orderflow(tmp_path / "orderflow_binance_BTCUSDT.json", _orderflow_trades())
    report = _run_gate(tmp_path, tmp_path / "out", write=True)
    json_path = Path(report["artifact_paths"]["json"])
    md_path = Path(report["artifact_paths"]["md"])
    assert json_path.exists() and md_path.exists()
    text = json_path.read_text(encoding="utf-8")
    assert '"valid": true' not in text
    assert "NaN" not in text and "Infinity" not in text
    parsed = json.loads(text)
    assert parsed["never_valid_true"] is True
    assert parsed["authenticity_verified"] is False
    assert parsed["data_provenance"] == "real"
    assert len(parsed["canonical_fingerprint"]) == 64
    assert parsed["report_id"] == REPORT_ID


def test_determinism_repeat_run(tmp_path):
    _write_orderflow(tmp_path / "orderflow_binance_BTCUSDT.json", _orderflow_trades())
    _write_options(tmp_path / "options_deribit_BTC_20260115T000000Z.json", _option_quotes())
    first = _run_gate(tmp_path, tmp_path / "out1", write=False)
    second = _run_gate(tmp_path, tmp_path / "out2", write=False)
    assert first["overall_verdict"] == second["overall_verdict"]
    assert first["n_candidates"] == second["n_candidates"]
    assert first["canonical_fingerprint"] == second["canonical_fingerprint"]
    assert [c["verdict"] for c in first["candidates"]] == [c["verdict"] for c in second["candidates"]]


def test_cli_emits_artifacts_and_nogo(tmp_path):
    _write_orderflow(tmp_path / "orderflow_binance_BTCUSDT.json", _orderflow_trades())
    art = tmp_path / "art"
    rc = cli_main(
        ["--repo", str(tmp_path), "--out", str(art), "--data-dir", str(tmp_path), "--timestamp", FIXED_TS]
    )
    assert rc == 0
    json_path = art / "REAL_DATA_FALSIFICATION_20261114T004500Z.json"
    md_path = art / "REAL_DATA_FALSIFICATION_20261114T004500Z.md"
    assert json_path.exists() and md_path.exists()
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    assert parsed["overall_verdict"] == "NO-GO"
    assert parsed["n_candidates"] == 1
    assert parsed["artifact_paths"]["json"].endswith(json_path.name)


def test_offline_guarantee(monkeypatch, tmp_path):
    _write_orderflow(tmp_path / "orderflow_binance_BTCUSDT.json", _orderflow_trades())

    def _guard(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("EVAL-25 attempted a network call; offline only")

    import socket

    monkeypatch.setattr(socket, "create_connection", _guard)
    report = evaluate_real_data_falsification(
        repo_root=".", write=False, out_dir=tmp_path / "out", data_dir=tmp_path, timestamp=FIXED_TS
    )
    assert report["overall_verdict"] in ("GO", "NO-GO")
    assert report["never_valid_true"] is True


# --- measured repo state ---


def test_repo_data_raw_yields_zero_real_candidates():
    data_raw = Path("data/raw")
    if not data_raw.exists():
        pytest.skip("data/raw not present")
    report = evaluate_real_data_falsification(
        repo_root=".", write=False, out_dir=Path("tests/__tmp_nogo__"), data_dir=data_raw, timestamp=FIXED_TS
    )
    # Both files in data/raw are *_synthetic* and excluded from discovery.
    assert report["n_candidates"] == 0
    assert report["n_orderflow_candidates"] == 0
    assert report["n_options_candidates"] == 0
    assert report["n_adequate_orderflow"] == 0
    assert report["n_adequate_options"] == 0
    assert report["overall_verdict"] == "NO-GO"
    assert "no real-data candidates" in report["overall_reason"]
    assert report["authenticity_verified"] is False
