"""Tests for the public real-data acquisition adapter (EVAL-26).

Covers OKX history-trades pagination/deduplication, option-instrument parsing,
bid/ask/expiry filtering, loader-compatible file emission, provenance, sealed
adequacy preview, and the CLI. All HTTP is faked; no network.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from src.data import public_export_acquisition as acq
from src.data.loader import DataLoader

NOW = datetime(2026, 11, 14, 0, 0, 0, tzinfo=timezone.utc)
EXP1 = datetime(2026, 11, 20, 0, 0, 0, tzinfo=timezone.utc)
EXP2 = datetime(2026, 11, 27, 0, 0, 0, tzinfo=timezone.utc)


class FakeResponse:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Dict[str, Any]:
        return self._payload


class FakeSession:
    """Deterministic offline OKX public-API double."""

    def __init__(
        self,
        history_pages: Optional[List[List[Dict[str, Any]]]] = None,
        instruments: Optional[List[Dict[str, Any]]] = None,
        tickers: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.history_pages = history_pages or []
        self.instruments = instruments or []
        self.tickers = tickers or []
        self.history_index: Dict[str, int] = {}
        self.calls: List[tuple] = []

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 0.0) -> FakeResponse:
        params = params or {}
        self.calls.append((url, dict(params), timeout))
        if url.endswith(acq.HISTORY_TRADES_ENDPOINT):
            after = params.get("after")
            index = self.history_index.get(str(after), 0) if after is not None else 0
            rows = self.history_pages[index] if index < len(self.history_pages) else []
            if rows:
                self.history_index[str(rows[-1]["tradeId"])] = index + 1
            return FakeResponse({"code": "0", "data": rows})
        if url.endswith(acq.INSTRUMENTS_ENDPOINT):
            return FakeResponse({"code": "0", "data": self.instruments})
        if url.endswith(acq.TICKERS_ENDPOINT):
            return FakeResponse({"code": "0", "data": self.tickers})
        raise AssertionError(f"unexpected URL: {url}")


def _trade(trade_id: int, ts: datetime, price: float = 60000.0) -> Dict[str, Any]:
    return {
        "instId": "BTC-USD-SWAP",
        "tradeId": str(trade_id),
        "px": str(price),
        "sz": "0.1",
        "side": "buy" if trade_id % 2 == 0 else "sell",
        "ts": str(int(ts.timestamp() * 1000)),
    }


def _instrument(inst_id: str, strike: float, expiry: datetime, right: str) -> Dict[str, Any]:
    return {
        "instId": inst_id,
        "instType": "OPTION",
        "uly": "BTC-USD",
        "ctVal": "0.01",
        "strike": str(strike),
        "expTime": str(int(expiry.timestamp() * 1000)),
        "optType": right,
    }


def _ticker(inst_id: str, bid: float, ask: float, ts: datetime = NOW) -> Dict[str, Any]:
    return {
        "instId": inst_id,
        "bidPx": str(bid),
        "askPx": str(ask),
        "last": str((bid + ask) / 2.0),
        "markPx": str((bid + ask) / 2.0),
        "ts": str(int(ts.timestamp() * 1000)),
    }


def test_parse_option_id_accepts_okx_format_and_rejects_malformed():
    parsed = acq._parse_option_id("BTC-USD-261127-102000-C")
    assert parsed is not None
    assert parsed["underlying"] == "BTC"
    assert parsed["strike"] == 102000.0
    assert parsed["expiry"] == datetime(2026, 11, 27, tzinfo=timezone.utc)
    assert parsed["option_type"] == "call"
    assert acq._parse_option_id("BTC-USD_UM-261127-102000-P") is None
    assert acq._parse_option_id("not-an-option") is None


def test_history_trades_paginate_deduplicate_and_sort():
    pages = [
        [
            _trade(100, NOW, 60000.0),
            _trade(99, NOW - timedelta(seconds=20), 60001.0),
            _trade(98, NOW - timedelta(seconds=40), 60002.0),
        ],
        [
            _trade(98, NOW - timedelta(seconds=40), 60002.0),
            _trade(97, NOW - timedelta(seconds=60), 60003.0),
            _trade(96, NOW - timedelta(seconds=80), 60004.0),
        ],
        [],
    ]
    session = FakeSession(history_pages=pages)
    result = acq.fetch_okx_history_trades(
        "BTC-USD-SWAP",
        session=session,
        min_bars=3,
        bar_duration_seconds=15.0,
        page_limit=3,
        request_delay_seconds=0.0,
    )
    assert result["n_trades"] == 5
    assert [t["trade_id"] for t in result["trades"]] == ["96", "97", "98", "99", "100"]
    assert result["pages"] == 2
    assert result["n_bars"] == 6  # 80s span -> ceil(80/15)
    assert result["span_seconds"] == 80.0
    assert all(t["side"] in ("buy", "sell") for t in result["trades"])


def test_option_chain_filters_invalid_quotes_and_counts_expiries():
    instruments = [
        _instrument("BTC-USD-261120-60000-C", 60000, EXP1, "C"),
        _instrument("BTC-USD-261120-65000-P", 65000, EXP1, "P"),
        _instrument("BTC-USD-261127-70000-C", 70000, EXP2, "C"),
        _instrument("BTC-USD-261127-75000-P", 75000, EXP2, "P"),
        _instrument("BTC-USD-261120-80000-C", 80000, EXP1, "C"),  # zero bid
        _instrument("BTC-USD-261120-85000-C", 85000, EXP1, "C"),  # crossed
        _instrument("BTC-USD-261113-90000-C", 90000, datetime(2026, 11, 13, tzinfo=timezone.utc), "C"),
        {"instId": "MALFORMED"},
    ]
    # OKX quotes options in USD per 1 BTC, which is the canonical OptionQuote
    # convention (spot/strikes are USD). No unit conversion is applied.
    tickers = [
        _ticker("BTC-USD-261120-60000-C", 1000.0, 2000.0),
        _ticker("BTC-USD-261120-65000-P", 2000.0, 3000.0),
        _ticker("BTC-USD-261127-70000-C", 3000.0, 4000.0),
        _ticker("BTC-USD-261127-75000-P", 4000.0, 5000.0),
        _ticker("BTC-USD-261120-80000-C", 0.0, 2000.0),
        _ticker("BTC-USD-261120-85000-C", 5000.0, 4000.0),
        _ticker("BTC-USD-261113-90000-C", 1000.0, 2000.0),
    ]
    session = FakeSession(instruments=instruments, tickers=tickers)
    result = acq.fetch_okx_option_chain("BTC", session=session, now=NOW)
    assert result["n_quotes"] == 4
    assert result["n_contracts"] == 4
    assert result["n_expiries"] == 2
    assert result["expiries"] == [
        "2026-11-20T00:00:00Z",
        "2026-11-27T00:00:00Z",
    ]
    assert all(q["ask"] >= q["bid"] > 0 for q in result["quotes"])
    assert all(q["expiry"] > NOW.isoformat() for q in result["quotes"])
    # Premiums are kept in the venue's BTC-per-1-BTC quote unit, which is the
    # canonical OptionQuote convention. No unit conversion is applied.
    first = next(q for q in result["quotes"] if q["symbol"].endswith("60000-C"))
    assert first["bid"] == pytest.approx(1000.0)
    assert first["ask"] == pytest.approx(2000.0)
    assert first["contract_size"] == pytest.approx(0.01)
    assert first["price_unit"] == "btc_per_1btc"


def _adequate_history_pages(n_trades: int = 1610, page_size: int = 100) -> List[List[Dict[str, Any]]]:
    pages: List[List[Dict[str, Any]]] = []
    for start in range(0, n_trades, page_size):
        rows = []
        for i in range(start, min(start + page_size, n_trades)):
            rows.append(_trade(100000 - i, NOW - timedelta(seconds=i * 15), 60000.0 + i))
        pages.append(rows)
    return pages


def _adequate_option_inputs() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    instruments: List[Dict[str, Any]] = []
    tickers: List[Dict[str, Any]] = []
    for expiry_i, expiry in enumerate((EXP1, EXP2)):
        for strike_i in range(4):
            right = "C" if strike_i % 2 == 0 else "P"
            strike = 60000 + strike_i * 5000
            inst_id = f"BTC-USD-{expiry.strftime('%y%m%d')}-{strike}-{right}"
            instruments.append(_instrument(inst_id, strike, expiry, right))
            tickers.append(_ticker(inst_id, 0.01 + strike_i * 0.001, 0.02 + strike_i * 0.001))
    return instruments, tickers


def test_write_orderflow_tape_is_loader_compatible(tmp_path):
    pages = [[_trade(1, NOW), _trade(2, NOW + timedelta(seconds=15))]]
    session = FakeSession(history_pages=pages)
    result = acq.fetch_okx_history_trades(
        "BTC-USD-SWAP",
        session=session,
        min_bars=2,
        bar_duration_seconds=15.0,
        request_delay_seconds=0.0,
    )
    path = tmp_path / "orderflow_okx_BTC-USD-SWAP.json"
    acq.write_orderflow_tape(result, path)
    snapshot = DataLoader(cache=False).load_orderflow(
        path, venue="okx", symbol="BTC-USD-SWAP"
    )
    assert snapshot.venue == "okx"
    assert len(snapshot.trades) == 2
    assert [t.side for t in snapshot.trades] == ["sell", "buy"]  # id 1 odd -> sell, id 2 even -> buy
    assert path.read_text(encoding="utf-8").find("synthetic") == -1


def test_write_options_chain_is_loader_compatible(tmp_path):
    instruments, tickers = _adequate_option_inputs()
    session = FakeSession(instruments=instruments, tickers=tickers)
    result = acq.fetch_okx_option_chain("BTC", session=session, now=NOW)
    path = tmp_path / "options_okx_BTC_20261114T000000Z.json"
    acq.write_options_chain(result, path)
    chain = DataLoader(cache=False).load_options_chain(path, venue="okx", underlying="BTC")
    assert chain.underlying == "BTC"
    assert chain.venue == "okx"
    assert len(chain.quotes) == 8
    assert len({q.contract.expiry for q in chain.quotes}) == 2


def test_acquire_public_exports_writes_files_report_and_adequacy(tmp_path):
    instruments, tickers = _adequate_option_inputs()
    session = FakeSession(
        history_pages=_adequate_history_pages(),
        instruments=instruments,
        tickers=tickers,
    )
    data_dir = tmp_path / "raw"
    out_dir = tmp_path / "research_state"
    report = acq.acquire_public_exports(
        underlying="BTC",
        orderflow_instrument="BTC-USD-SWAP",
        data_dir=data_dir,
        out_dir=out_dir,
        timestamp="2026-11-14T03:00:00Z",
        min_bars=1600,
        bar_duration_seconds=15.0,
        request_delay_seconds=0.0,
        session=session,
    )
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["authenticity_verified"] is False
    assert report["never_valid_true"] is True
    assert report["adequacy"]["orderflow_adequate"] is True
    assert report["adequacy"]["options_adequate"] is True
    of_path = data_dir / "orderflow_okx_BTC-USD-SWAP.json"
    op_path = data_dir / "options_okx_BTC_20261114T030000Z.json"
    assert of_path.exists()
    assert op_path.exists()
    assert "synthetic" not in of_path.name.lower()
    assert "synthetic" not in op_path.name.lower()
    assert report["orderflow"]["n_trades"] == 1610
    assert report["orderflow"]["n_returns"] >= 1000
    assert report["orderflow"]["n_windows"] >= 20
    assert report["options"]["n_contracts"] == 8
    assert report["options"]["n_expiries"] == 2
    assert report["artifact_paths"]["json"].endswith(
        "PUBLIC_EXPORT_ACQUISITION_20261114T030000Z.json"
    )
    assert Path(report["artifact_paths"]["json"]).exists()
    assert Path(report["artifact_paths"]["md"]).exists()
    artifact = json.loads(Path(report["artifact_paths"]["json"]).read_text(encoding="utf-8"))
    assert artifact["never_valid_true"] is True


def test_acquire_refuses_synthetic_output_name(tmp_path):
    with pytest.raises(acq.AcquisitionError):
        acq.write_orderflow_tape(
            {"instrument": "BTC-USD-SWAP", "trades": []},
            tmp_path / "orderflow_okx_BTCUSDT_synthetic.json",
        )


def test_cli_main_uses_public_session_and_writes_artifact(tmp_path, monkeypatch):
    instruments, tickers = _adequate_option_inputs()
    fake = FakeSession(
        history_pages=_adequate_history_pages(),
        instruments=instruments,
        tickers=tickers,
    )
    monkeypatch.setattr(acq.requests, "Session", lambda: fake)
    data_dir = tmp_path / "raw"
    out_dir = tmp_path / "research_state"
    exit_code = acq.main(
        [
            "--underlying",
            "BTC",
            "--orderflow-instrument",
            "BTC-USD-SWAP",
            "--data-dir",
            str(data_dir),
            "--out",
            str(out_dir),
            "--timestamp",
            "2026-11-14T03:10:00Z",
            "--min-bars",
            "1600",
            "--request-delay-seconds",
            "0",
        ]
    )
    assert exit_code == 0
    assert (data_dir / "orderflow_okx_BTC-USD-SWAP.json").exists()
    assert (out_dir / "PUBLIC_EXPORT_ACQUISITION_20261114T031000Z.json").exists()