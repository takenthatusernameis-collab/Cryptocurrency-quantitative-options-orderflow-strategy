"""Numeric-invariant tests for EVAL-23B exchange trade-export adapters.

Covers OKX/Binance/Deribit CSV+JSON parsing, side semantics, strict timestamp
and microstructure rejection, canonical order/fingerprint invariance, loader
compatibility of the normalized tape, strict serialization, adequacy reporting,
and CLI artifact emission. All fixtures are temp-dir files; no network.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.data.exchange_exports import (
    REPORT_ID,
    ExchangeExportRejected,
    _canonical_fingerprint,
    evaluate_exchange_export,
    main as cli_main,
    parse_exchange_export,
    write_normalized_orderflow_tape,
)
from src.data.loader import DataLoader

START = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _okx_csv(path: Path, rows: int = 3) -> Path:
    lines = ["tradeId,instId,px,sz,side,ts"]
    for i in range(rows):
        lines.append(
            f"{1000 + i},BTC-USDT,{60000 + i},0.{10 + i},"
            f"{'buy' if i % 2 == 0 else 'sell'},{_iso(START + timedelta(seconds=i * 5))}"
        )
    return _write(path, "\n".join(lines) + "\n")


def _binance_csv(path: Path) -> Path:
    return _write(
        path,
        "Id,Price,Qty,QuoteQty,Time,IsBuyerMaker,IsBestMatch\n"
        "2001,60000.0,0.5,30000.0,2026-01-01 00:00:00.000,false,true\n"
        "2002,60010.0,0.4,24004.0,2026-01-01 00:00:05.000,true,true\n",
    )


def _deribit_json(path: Path) -> Path:
    payload = {
        "result": [
            {
                "trade_id": "3001",
                "timestamp": 1767225600000,
                "instrument_name": "BTC-PERPETUAL",
                "price": 60020.0,
                "amount": 0.3,
                "direction": "buy",
            },
            {
                "trade_id": "3002",
                "timestamp": 1767225605000,
                "instrument_name": "BTC-PERPETUAL",
                "price": 60030.0,
                "amount": 0.2,
                "direction": "sell",
            },
        ]
    }
    return _write(path, json.dumps(payload))


def _binance_json(path: Path) -> Path:
    payload = [
        {
            "id": 2101,
            "price": "60000.0",
            "qty": "0.5",
            "time": 1767225600000,
            "isBuyerMaker": False,
        },
        {
            "id": 2102,
            "price": "60010.0",
            "qty": "0.4",
            "time": 1767225605000,
            "isBuyerMaker": True,
        },
    ]
    return _write(path, json.dumps(payload))


# --- venue parsers ---


def test_okx_csv_parses_and_normalizes(tmp_path):
    snapshot = parse_exchange_export(_okx_csv(tmp_path / "okx.csv"), "okx", "BTC-USDT")
    assert snapshot.venue == "okx"
    assert snapshot.symbol == "BTCUSDT"
    assert len(snapshot.trades) == 3
    assert [t.trade_id for t in snapshot.trades] == ["1000", "1001", "1002"]
    assert [t.side for t in snapshot.trades] == ["buy", "sell", "buy"]
    assert [t.price for t in snapshot.trades] == [60000.0, 60001.0, 60002.0]
    assert [t.size for t in snapshot.trades] == [0.10, 0.11, 0.12]
    assert snapshot.timestamp == START + timedelta(seconds=10)
    assert snapshot.trades[0].timestamp == START


def test_binance_csv_is_buyer_maker_side(tmp_path):
    snapshot = parse_exchange_export(_binance_csv(tmp_path / "binance.csv"), "binance", "BTCUSDT")
    assert snapshot.venue == "binance"
    assert [t.side for t in snapshot.trades] == ["buy", "sell"]
    assert [t.trade_id for t in snapshot.trades] == ["2001", "2002"]
    assert snapshot.trades[0].timestamp == START
    assert snapshot.trades[1].timestamp == START + timedelta(seconds=5)


def test_binance_json_is_buyer_maker_side(tmp_path):
    snapshot = parse_exchange_export(_binance_json(tmp_path / "binance.json"), "binance", "BTCUSDT")
    assert [t.side for t in snapshot.trades] == ["buy", "sell"]
    assert [t.trade_id for t in snapshot.trades] == ["2101", "2102"]


def test_deribit_json_parses_epoch_ms(tmp_path):
    snapshot = parse_exchange_export(
        _deribit_json(tmp_path / "deribit.json"), "deribit", "BTC-PERPETUAL"
    )
    assert snapshot.venue == "deribit"
    assert snapshot.symbol == "BTCPERPETUAL"
    assert [t.trade_id for t in snapshot.trades] == ["3001", "3002"]
    assert snapshot.trades[0].timestamp == START
    assert snapshot.trades[1].timestamp == START + timedelta(seconds=5)


# --- validation ---


def test_missing_trade_ids_are_deterministic(tmp_path):
    path = _write(
        tmp_path / "okx-no-id.csv",
        "instId,px,sz,side,ts\n"
        "BTC-USDT,60000,0.1,buy,2026-01-01T00:00:00Z\n"
        "BTC-USDT,60001,0.2,sell,2026-01-01T00:00:05Z\n",
    )
    first = parse_exchange_export(path, "okx", "BTCUSDT")
    second = parse_exchange_export(path, "okx", "BTCUSDT")
    ids = [t.trade_id for t in first.trades]
    assert ids == [t.trade_id for t in second.trades]
    assert all(tid.startswith("auto-") for tid in ids)
    assert len(set(ids)) == 2


@pytest.mark.parametrize(
    "row",
    [
        "1001,BTC-USDT,60000,0.1,buy,not-a-time",
        "1002,BTC-USDT,0,0.1,buy,2026-01-01T00:00:00Z",
        "1003,BTC-USDT,60000,-0.1,buy,2026-01-01T00:00:00Z",
        "1004,BTC-USDT,60000,0.1,hold,2026-01-01T00:00:00Z",
    ],
)
def test_invalid_rows_are_rejected(tmp_path, row):
    path = _write(
        tmp_path / "bad.csv",
        "tradeId,instId,px,sz,side,ts\n" + row + "\n",
    )
    with pytest.raises(ExchangeExportRejected):
        parse_exchange_export(path, "okx", "BTCUSDT")


def test_empty_export_rejected(tmp_path):
    csv_path = _write(tmp_path / "empty.csv", "tradeId,instId,px,sz,side,ts\n")
    json_path = _write(tmp_path / "empty.json", "[]")
    with pytest.raises(ExchangeExportRejected):
        parse_exchange_export(csv_path, "okx", "BTCUSDT")
    with pytest.raises(ExchangeExportRejected):
        parse_exchange_export(json_path, "okx", "BTCUSDT")


def test_unsupported_venue_rejected(tmp_path):
    path = _okx_csv(tmp_path / "okx.csv")
    with pytest.raises(ExchangeExportRejected):
        parse_exchange_export(path, "coinbase", "BTCUSDT")


def test_synthetic_filename_rejected(tmp_path):
    path = _okx_csv(tmp_path / "orderflow_binance_BTCUSDT_synthetic.csv")
    with pytest.raises(ExchangeExportRejected):
        parse_exchange_export(path, "binance", "BTCUSDT")


def test_duplicate_trade_id_rejected(tmp_path):
    path = _write(
        tmp_path / "dup.csv",
        "tradeId,instId,px,sz,side,ts\n"
        "1,BTC-USDT,60000,0.1,buy,2026-01-01T00:00:00Z\n"
        "1,BTC-USDT,60001,0.2,sell,2026-01-01T00:00:05Z\n",
    )
    with pytest.raises(ExchangeExportRejected):
        parse_exchange_export(path, "okx", "BTCUSDT")


# --- ordering / determinism ---


def test_canonical_order_and_fingerprint_are_row_order_invariant(tmp_path):
    rows = [
        "3001,BTC-USDT,60002,0.3,sell,2026-01-01T00:00:05Z",
        "3000,BTC-USDT,60000,0.1,buy,2026-01-01T00:00:00Z",
        "3002,BTC-USDT,60001,0.2,buy,2026-01-01T00:00:05Z",
    ]
    header = "tradeId,instId,px,sz,side,ts"
    first = _write(tmp_path / "a.csv", header + "\n" + "\n".join(rows) + "\n")
    second = _write(
        tmp_path / "b.csv", header + "\n" + "\n".join(reversed(rows)) + "\n"
    )
    snap_a = parse_exchange_export(first, "okx", "BTCUSDT")
    snap_b = parse_exchange_export(second, "okx", "BTCUSDT")
    order_a = [(t.trade_id, t.price, t.size, t.side) for t in snap_a.trades]
    order_b = [(t.trade_id, t.price, t.size, t.side) for t in snap_b.trades]
    assert order_a == order_b
    assert _canonical_fingerprint(snap_a) == _canonical_fingerprint(snap_b)
    assert [t.trade_id for t in snap_a.trades] == ["3000", "3001", "3002"]


def test_deterministic_parse_same_file(tmp_path):
    path = _binance_csv(tmp_path / "binance.csv")
    first = parse_exchange_export(path, "binance", "BTCUSDT")
    second = parse_exchange_export(path, "binance", "BTCUSDT")
    assert [(t.trade_id, t.price, t.size, t.side, t.timestamp) for t in first.trades] == [
        (t.trade_id, t.price, t.size, t.side, t.timestamp) for t in second.trades
    ]


# --- normalized tape ---


def test_normalized_tape_is_loader_compatible(tmp_path):
    snapshot = parse_exchange_export(_binance_csv(tmp_path / "binance.csv"), "binance", "BTCUSDT")
    target = write_normalized_orderflow_tape(snapshot, tmp_path / "normalized.json")
    assert target.exists()
    loaded = DataLoader(cache=False).load_orderflow(
        target, venue="binance", symbol="BTCUSDT"
    )
    assert len(loaded.trades) == 2
    assert [t.side for t in loaded.trades] == ["buy", "sell"]
    assert loaded.venue == "binance"
    assert loaded.symbol == "BTCUSDT"


def test_write_normalized_tape_to_directory_uses_venue_symbol(tmp_path):
    snapshot = parse_exchange_export(_okx_csv(tmp_path / "okx.csv"), "okx", "BTC-USDT")
    target = write_normalized_orderflow_tape(snapshot, tmp_path / "normalized")
    assert target.parent == tmp_path / "normalized"
    assert target.name.startswith("orderflow_okx_BTCUSDT_")
    assert target.suffix == ".json"


# --- artifact / adequacy / CLI ---


def test_artifact_is_strict_and_has_no_valid_true(tmp_path):
    source = _okx_csv(tmp_path / "okx.csv")
    report = evaluate_exchange_export(
        source,
        "okx",
        "BTC-USDT",
        write=True,
        out_dir=tmp_path / "art",
        normalized_out=tmp_path / "raw",
        timestamp="2026-11-13T23:55:00Z",
    )
    assert report["report_id"] == REPORT_ID
    assert report["adapter_verdict"] == "PASS"
    assert report["overall_verdict"] == "NO-GO"
    assert report["never_valid_true"] is True
    assert report["data_provenance"] == "exchange_export"
    assert report["authenticity_verified"] is False
    assert len(report["supported_formats"]) == 3
    json_path = Path(report["artifact_paths"]["json"])
    md_path = Path(report["artifact_paths"]["md"])
    assert json_path.exists() and md_path.exists()
    text = json_path.read_text(encoding="utf-8")
    assert '"valid": true' not in text
    assert json.loads(text)["adapter_verdict"] == "PASS"


def _adequate_export(path: Path) -> Path:
    rows = []
    for i in range(1600):
        rows.append(
            {
                "trade_id": f"a{i:06d}",
                "timestamp": int(
                    (START + timedelta(seconds=i * 15)).timestamp() * 1000
                ),
                "price": 60000.0 + i,
                "size": 0.1,
                "side": "buy" if i % 2 == 0 else "sell",
            }
        )
    return _write(path, json.dumps(rows))


def test_adequate_export_reports_go_and_normalizes(tmp_path):
    source = _adequate_export(tmp_path / "adequate.json")
    report = evaluate_exchange_export(
        source,
        "binance",
        "BTCUSDT",
        write=False,
        normalized_out=tmp_path / "raw",
        timestamp="2026-11-13T23:56:00Z",
    )
    assert report["adapter_verdict"] == "PASS"
    assert report["overall_verdict"] == "GO"
    assert report["adequacy"]["n_returns"] >= 1000
    assert report["adequacy"]["n_windows"] >= 20
    assert report["adequacy"]["sample_adequate"] is True
    normalized = Path(report["normalized_tape_path"])
    assert normalized.exists()
    assert len(report["normalized_tape_sha256"]) == 64


def test_cli_writes_artifacts_and_normalized_tape(tmp_path):
    source = _okx_csv(tmp_path / "okx.csv")
    art = tmp_path / "art"
    raw = tmp_path / "raw"
    rc = cli_main(
        [
            "--in",
            str(source),
            "--venue",
            "okx",
            "--symbol",
            "BTC-USDT",
            "--out",
            str(art),
            "--data-dir",
            str(raw),
            "--timestamp",
            "2026-11-13T23:57:00Z",
        ]
    )
    assert rc == 0
    json_path = art / "EXCHANGE_EXPORT_ADAPTERS_20261113T235700Z.json"
    md_path = art / "EXCHANGE_EXPORT_ADAPTERS_20261113T235700Z.md"
    assert json_path.exists() and md_path.exists()
    tapes = list(raw.glob("orderflow_okx_BTCUSDT_*.json"))
    assert len(tapes) == 1
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["adapter_verdict"] == "PASS"
    assert report["normalized_tape_path"].endswith(tapes[0].name)