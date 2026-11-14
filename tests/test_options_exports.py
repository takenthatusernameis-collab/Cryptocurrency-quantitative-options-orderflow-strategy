"""Numeric-invariant tests for EVAL-24A exchange option-export adapters.

Covers OKX/Binance/Deribit CSV+JSON parsing, contract/quote normalization,
strict timestamp/expiry/strike/bid/ask/IV rejection, duplicate/ambiguous
contract rejection, canonical order/fingerprint invariance, loader compatibility
of the normalized chain, strict serialization, determinism, CLI artifact
emission, and adequacy/readiness reporting. All fixtures are temp-dir files; no
network.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.data.options_exports import (
    REPORT_ID,
    OptionExportRejected,
    _canonical_fingerprint,
    evaluate_options_export,
    main as cli_main,
    parse_options_export,
    write_normalized_options_chain,
)
from src.data.loader import DataLoader

START = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
EXP1 = datetime(2026, 1, 30, 8, 0, 0, tzinfo=timezone.utc)
EXP2 = datetime(2026, 2, 27, 8, 0, 0, tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _okx_csv(path: Path, rows: int = 3) -> Path:
    header = (
        "instId,strike,expiry,optionType,bid,ask,mark,markIv,delta,gamma,"
        "theta,vega,openInterest,volume,ts"
    )
    lines = [header]
    for i in range(rows):
        strike = 60000 + i * 5000
        lines.append(
            f"BTC-260130-{strike}-C,{strike},{_iso(EXP1)},C,"
            f"{1200 - i * 200},{1250 - i * 200},{1225 - i * 200},0.55,"
            f"0.62,0.0021,-18.5,95.0,120.0,8.5,{_iso(START)}"
        )
    return _write(path, "\n".join(lines) + "\n")


def _binance_csv(path: Path) -> Path:
    return _write(
        path,
        "symbol,strike,expiry,optionType,bid,ask,mark,markIv,delta,gamma,theta,vega,openInterest,volume,timestamp\n"
        f"BTC-260130-60000-C,60000,{_iso(EXP1)},CALL,1200,1250,1225,0.55,0.62,0.0021,-18.5,95,120,8.5,{_iso(START)}\n"
        f"BTC-260130-65000-P,65000,{_iso(EXP1)},PUT,410,440,425,0.53,-0.41,0.0023,-13.4,71,66,3.9,{_iso(START)}\n",
    )


def _deribit_json(path: Path) -> Path:
    payload = {
        "result": [
            {
                "instrument_name": "BTC-30JAN26-60000-C",
                "strike": 60000.0,
                "expiration_timestamp": _ms(EXP1),
                "option_type": "call",
                "bid_price": 1200.0,
                "ask_price": 1250.0,
                "mark_price": 1225.0,
                "mark_iv": 0.55,
                "delta": 0.62,
                "gamma": 0.0021,
                "theta": -18.5,
                "vega": 95.0,
                "open_interest": 120.0,
                "volume": 8.5,
                "timestamp": _ms(START),
            },
            {
                "instrument_name": "BTC-30JAN26-65000-C",
                "strike": 65000.0,
                "expiration_timestamp": _ms(EXP1),
                "option_type": "call",
                "bid_price": 820.0,
                "ask_price": 850.0,
                "mark_price": 835.0,
                "mark_iv": 0.52,
                "delta": 0.48,
                "gamma": 0.0024,
                "theta": -14.2,
                "vega": 78.0,
                "open_interest": 95.0,
                "volume": 6.1,
                "timestamp": _ms(START),
            },
        ]
    }
    return _write(path, json.dumps(payload))


# --- venue parsers ---


def test_okx_csv_parses_and_normalizes(tmp_path):
    chain = parse_options_export(_okx_csv(tmp_path / "okx.csv"), "okx", "BTC")
    assert chain.venue == "okx"
    assert chain.underlying == "BTC"
    assert len(chain.quotes) == 3
    assert [q.contract.option_type for q in chain.quotes] == ["call", "call", "call"]
    assert [q.contract.strike for q in chain.quotes] == [60000.0, 65000.0, 70000.0]
    assert [q.bid for q in chain.quotes] == [1200.0, 1000.0, 800.0]
    assert [q.ask for q in chain.quotes] == [1250.0, 1050.0, 850.0]
    assert chain.quotes[0].contract.expiry == EXP1
    assert chain.timestamp == START


def test_binance_csv_call_and_put(tmp_path):
    chain = parse_options_export(_binance_csv(tmp_path / "binance.csv"), "binance", "BTC")
    assert chain.venue == "binance"
    assert [q.contract.option_type for q in chain.quotes] == ["call", "put"]
    assert chain.quotes[1].delta is not None and chain.quotes[1].delta < 0


def test_deribit_json_parses_epoch_ms(tmp_path):
    chain = parse_options_export(
        _deribit_json(tmp_path / "deribit.json"), "deribit", "BTC"
    )
    assert chain.venue == "deribit"
    assert len(chain.quotes) == 2
    assert chain.quotes[0].contract.expiry == EXP1
    assert chain.quotes[0].timestamp == START


def test_option_type_inferred_from_symbol_when_absent(tmp_path):
    path = _write(
        tmp_path / "okx-no-type.csv",
        "instId,strike,expiry,bid,ask,ts\n"
        f"BTC-260130-60000-C,60000,{_iso(EXP1)},1200,1250,{_iso(START)}\n",
    )
    chain = parse_options_export(path, "okx", "BTC")
    assert chain.quotes[0].contract.option_type == "call"


# --- validation / rejection ---


@pytest.mark.parametrize(
    "row",
    [
        # unparseable timestamp
        f"X,60000,{_iso(EXP1)},C,1200,1250,not-a-time",
        # non-positive strike
        f"X,0,{_iso(EXP1)},C,1200,1250,{_iso(START)}",
        # invalid option type
        f"X,60000,{_iso(EXP1)},Z,1200,1250,{_iso(START)}",
        # negative bid
        f"X,60000,{_iso(EXP1)},C,-1200,1250,{_iso(START)}",
        # crossed market
        f"X,60000,{_iso(EXP1)},C,1300,1250,{_iso(START)}",
        # expiry <= timestamp
        f"X,60000,{_iso(START)},C,1200,1250,{_iso(EXP2)}",
        # non-finite IV
        f"X,60000,{_iso(EXP1)},C,1200,1250,0.55,0.62,0.0021,-18.5,95.0,120.0,8.5,inf,{_iso(START)}",
    ],
)
def test_invalid_rows_are_rejected(tmp_path, row):
    path = _write(
        tmp_path / "bad.csv",
        "instId,strike,expiry,optionType,bid,ask,markIv,delta,gamma,theta,vega,openInterest,volume,ts\n"
        + row
        + "\n",
    )
    with pytest.raises(OptionExportRejected):
        parse_options_export(path, "okx", "BTC")


def test_empty_export_rejected(tmp_path):
    csv_path = _write(
        tmp_path / "empty.csv",
        "instId,strike,expiry,optionType,bid,ask,ts\n",
    )
    json_path = _write(tmp_path / "empty.json", "[]")
    with pytest.raises(OptionExportRejected):
        parse_options_export(csv_path, "okx", "BTC")
    with pytest.raises(OptionExportRejected):
        parse_options_export(json_path, "okx", "BTC")


def test_unsupported_venue_rejected(tmp_path):
    path = _okx_csv(tmp_path / "okx.csv")
    with pytest.raises(OptionExportRejected):
        parse_options_export(path, "coinbase", "BTC")


def test_synthetic_filename_rejected(tmp_path):
    path = _okx_csv(tmp_path / "options_btc_synthetic.csv")
    with pytest.raises(OptionExportRejected):
        parse_options_export(path, "okx", "BTC")


def test_duplicate_symbol_timestamp_rejected(tmp_path):
    path = _write(
        tmp_path / "dup.csv",
        "instId,strike,expiry,optionType,bid,ask,ts\n"
        f"BTC-260130-60000-C,60000,{_iso(EXP1)},C,1200,1250,{_iso(START)}\n"
        f"BTC-260130-60000-C,60000,{_iso(EXP1)},C,1210,1260,{_iso(START)}\n",
    )
    with pytest.raises(OptionExportRejected):
        parse_options_export(path, "okx", "BTC")


# --- ordering / determinism ---


def test_canonical_order_and_fingerprint_are_row_order_invariant(tmp_path):
    rows = [
        f"BTC-260130-70000-C,70000,{_iso(EXP1)},C,800,850,{_iso(START)}",
        f"BTC-260130-60000-C,60000,{_iso(EXP1)},C,1200,1250,{_iso(START)}",
        f"BTC-260130-65000-C,65000,{_iso(EXP1)},C,1000,1050,{_iso(START)}",
    ]
    header = "instId,strike,expiry,optionType,bid,ask,ts"
    first = _write(tmp_path / "a.csv", header + "\n" + "\n".join(rows) + "\n")
    second = _write(
        tmp_path / "b.csv", header + "\n" + "\n".join(reversed(rows)) + "\n"
    )
    chain_a = parse_options_export(first, "okx", "BTC")
    chain_b = parse_options_export(second, "okx", "BTC")
    order_a = [(q.contract.strike, q.bid, q.ask) for q in chain_a.quotes]
    order_b = [(q.contract.strike, q.bid, q.ask) for q in chain_b.quotes]
    assert order_a == order_b
    assert _canonical_fingerprint(chain_a) == _canonical_fingerprint(chain_b)
    assert [q.contract.strike for q in chain_a.quotes] == [60000.0, 65000.0, 70000.0]


def test_deterministic_parse_same_file(tmp_path):
    path = _binance_csv(tmp_path / "binance.csv")
    first = parse_options_export(path, "binance", "BTC")
    second = parse_options_export(path, "binance", "BTC")
    assert [
        (q.contract.symbol, q.contract.strike, q.bid, q.ask, q.timestamp)
        for q in first.quotes
    ] == [
        (q.contract.symbol, q.contract.strike, q.bid, q.ask, q.timestamp)
        for q in second.quotes
    ]


# --- normalized chain ---


def test_normalized_chain_is_loader_compatible(tmp_path):
    chain = parse_options_export(_okx_csv(tmp_path / "okx.csv"), "okx", "BTC")
    target = write_normalized_options_chain(chain, tmp_path / "normalized.json")
    assert target.exists()
    loaded = DataLoader(cache=False).load_options_chain(
        target, venue="okx", underlying="BTC"
    )
    assert len(loaded.quotes) == 3
    assert loaded.venue == "okx"
    assert loaded.underlying == "BTC"
    assert [q.contract.strike for q in loaded.quotes] == [60000.0, 65000.0, 70000.0]


def test_write_normalized_chain_to_directory_uses_venue_underlying(tmp_path):
    chain = parse_options_export(_okx_csv(tmp_path / "okx.csv"), "okx", "BTC")
    target = write_normalized_options_chain(chain, tmp_path / "normalized")
    assert target.parent == tmp_path / "normalized"
    assert target.name.startswith("options_okx_BTC_")
    assert target.suffix == ".json"


def test_normalized_chain_is_strict_json(tmp_path):
    chain = parse_options_export(_okx_csv(tmp_path / "okx.csv"), "okx", "BTC")
    target = write_normalized_options_chain(chain, tmp_path / "normalized.json")
    text = target.read_text(encoding="utf-8")
    assert '"valid": true' not in text
    assert "NaN" not in text and "Infinity" not in text
    json.loads(text)  # parses strictly


# --- artifact / adequacy / CLI ---


def test_artifact_is_strict_and_has_no_valid_true(tmp_path):
    source = _okx_csv(tmp_path / "okx.csv")
    report = evaluate_options_export(
        source,
        "okx",
        "BTC",
        write=True,
        out_dir=tmp_path / "art",
        normalized_out=tmp_path / "raw",
        timestamp="2026-11-13T23:59:00Z",
    )
    assert report["report_id"] == REPORT_ID
    assert report["adapter_verdict"] == "PASS"
    assert report["overall_verdict"] == "NO-GO"  # 3 contracts < floor 8
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


def _adequate_chain_path(path: Path) -> Path:
    rows = []
    # 3 expiries x 3 strikes (call/put) => 18 contracts, 18 quotes
    expiries = [
        datetime(2026, 1, 30, 8, tzinfo=timezone.utc),
        datetime(2026, 2, 27, 8, tzinfo=timezone.utc),
        datetime(2026, 3, 27, 8, tzinfo=timezone.utc),
    ]
    strikes = [60000, 65000, 70000]
    for exp in expiries:
        for strike in strikes:
            for ot, bid, ask in (("C", 1200.0, 1250.0), ("P", 400.0, 440.0)):
                symbol = f"BTC-{exp.strftime('%y%m%d')}-{strike}-{ot}"
                rows.append(
                    {
                        "instId": symbol,
                        "strike": strike,
                        "expiry": _iso(exp),
                        "optionType": ot,
                        "bid": bid,
                        "ask": ask,
                        "mark": (bid + ask) / 2,
                        "markIv": 0.55,
                        "timestamp": _iso(START),
                    }
                )
    return _write(path, "instId,strike,expiry,optionType,bid,ask,mark,markIv,timestamp\n" + "\n".join(
        ",".join(str(r[k]) for k in ("instId", "strike", "expiry", "optionType", "bid", "ask", "mark", "markIv", "timestamp"))
        for r in rows
    ) + "\n")


def test_adequate_chain_reports_go_and_normalizes(tmp_path):
    source = _adequate_chain_path(tmp_path / "adequate.csv")
    report = evaluate_options_export(
        source,
        "okx",
        "BTC",
        write=False,
        normalized_out=tmp_path / "raw",
        timestamp="2026-11-14T00:00:00Z",
    )
    assert report["adapter_verdict"] == "PASS"
    assert report["overall_verdict"] == "GO"
    assert report["adequacy"]["n_contracts"] >= 8
    assert report["adequacy"]["n_quotes"] >= 8
    assert report["adequacy"]["n_expiries"] >= 2
    assert report["adequacy"]["sample_adequate"] is True
    normalized = Path(report["normalized_chain_path"])
    assert normalized.exists()
    assert len(report["normalized_chain_sha256"]) == 64
    loaded = DataLoader(cache=False).load_options_chain(normalized, venue="okx", underlying="BTC")
    assert len(loaded.quotes) == 18


def test_cli_writes_artifacts_and_normalized_chain(tmp_path):
    source = _okx_csv(tmp_path / "okx.csv")
    art = tmp_path / "art"
    raw = tmp_path / "raw"
    rc = cli_main(
        [
            "--in",
            str(source),
            "--venue",
            "okx",
            "--underlying",
            "BTC",
            "--out",
            str(art),
            "--data-dir",
            str(raw),
            "--timestamp",
            "2026-11-14T00:01:00Z",
        ]
    )
    assert rc == 0
    json_path = art / "OPTIONS_EXPORT_ADAPTERS_20261114T000100Z.json"
    md_path = art / "OPTIONS_EXPORT_ADAPTERS_20261114T000100Z.md"
    assert json_path.exists() and md_path.exists()
    tapes = list(raw.glob("options_okx_BTC_*.json"))
    assert len(tapes) == 1
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["adapter_verdict"] == "PASS"
    assert report["normalized_chain_path"].endswith(tapes[0].name)