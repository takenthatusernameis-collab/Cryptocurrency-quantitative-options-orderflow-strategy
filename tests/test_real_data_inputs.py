"""Tests for real-data-first campaign loaders (EVAL-23/24 entry points).

These loaders never fall back to synthetic data: they discover non-synthetic
``orderflow_*`` / ``options_*`` exports under ``data/raw/`` and raise when none
exist. All fixtures are temp-dir files; no network.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.campaign.integrated import (
    RealDataUnavailable,
    load_real_options_chain,
    load_real_orderflow,
)

NOW = datetime(2026, 11, 14, 0, 0, 0, tzinfo=timezone.utc)
EXP1 = datetime(2026, 11, 20, tzinfo=timezone.utc)
EXP2 = datetime(2026, 11, 27, tzinfo=timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _write_orderflow(path: Path, symbol: str, venue: str, n: int = 3) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    trades = []
    for i in range(n):
        trades.append(
            {
                "trade_id": f"t{i:04d}",
                "symbol": symbol,
                "venue": venue,
                "price": 60000.0 + i,
                "size": 0.1,
                "side": "buy" if i % 2 == 0 else "sell",
                "timestamp": _iso(NOW + timedelta(seconds=i * 15)),
            }
        )
    path.write_text(
        json.dumps(
            {
                "trades": trades,
                "liquidations": [],
                "funding_rates": [],
                "symbol": symbol,
                "venue": venue,
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_options(path: Path, underlying: str, venue: str, n: int = 2) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    quotes = []
    for i in range(n):
        quotes.append(
            {
                "symbol": f"{underlying}-USD-{(EXP1 if i == 0 else EXP2).strftime('%y%m%d')}-{60000 + i * 1000}-C",
                "underlying": underlying,
                "strike": 60000.0 + i * 1000,
                "expiry": _iso(EXP1 if i == 0 else EXP2),
                "option_type": "call",
                "venue": venue,
                "contract_size": 1.0,
                "bid": 100.0 + i,
                "ask": 110.0 + i,
                "last": 105.0 + i,
                "mark": 105.0 + i,
                "timestamp": _iso(NOW),
            }
        )
    path.write_text(
        json.dumps({"quotes": quotes, "underlying": underlying, "venue": venue}),
        encoding="utf-8",
    )
    return path


def test_real_orderflow_loader_prefers_non_synthetic_and_matches_symbol(tmp_path):
    raw = tmp_path / "raw"
    _write_orderflow(raw / "orderflow_okx_BTCUSDT_synthetic.json", "BTCUSDT", "synthetic")
    _write_orderflow(raw / "orderflow_okx_ETH-USD-SWAP.json", "ETH-USD-SWAP", "okx")
    _write_orderflow(raw / "orderflow_okx_BTC-USD-SWAP.json", "BTC-USD-SWAP", "okx")
    snap = load_real_orderflow("BTC", data_raw=raw)
    assert snap.venue == "okx"
    assert snap.symbol == "BTC"
    assert len(snap.trades) == 3
    assert snap.trades[0].venue == "okx"


def test_real_orderflow_loader_raises_without_real_export(tmp_path):
    raw = tmp_path / "raw"
    _write_orderflow(raw / "orderflow_okx_ETH-USD-SWAP.json", "ETH-USD-SWAP", "okx")
    with pytest.raises(RealDataUnavailable):
        load_real_orderflow("BTC", data_raw=raw)


def test_real_options_loader_prefers_non_synthetic_and_matches_underlying(tmp_path):
    raw = tmp_path / "raw"
    _write_options(raw / "options_okx_BTC_synthetic.json", "BTC", "synthetic")
    _write_options(raw / "options_okx_ETH_20261114T000000Z.json", "ETH", "okx")
    _write_options(raw / "options_okx_BTC_20261114T010000Z.json", "BTC", "okx")
    chain = load_real_options_chain("BTC", data_raw=raw)
    assert chain.underlying == "BTC"
    assert chain.venue == "okx"
    assert len(chain.quotes) == 2
    assert len({q.contract.expiry for q in chain.quotes}) == 2


def test_real_options_loader_raises_without_real_export(tmp_path):
    raw = tmp_path / "raw"
    _write_options(raw / "options_okx_ETH_20261114T000000Z.json", "ETH", "okx")
    with pytest.raises(RealDataUnavailable):
        load_real_options_chain("BTC", data_raw=raw)


def test_real_options_loader_rejects_empty_chain(tmp_path):
    raw = tmp_path / "raw"
    (raw).mkdir(parents=True, exist_ok=True)
    (raw / "options_okx_BTC_20261114T000000Z.json").write_text(
        json.dumps({"quotes": [], "underlying": "BTC", "venue": "okx"}),
        encoding="utf-8",
    )
    with pytest.raises(RealDataUnavailable):
        load_real_options_chain("BTC", data_raw=raw)