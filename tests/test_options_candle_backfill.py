"""Tests for the dense option-candle backfill (EVAL-41 Track B).

Covers candle grouping by bar start, bar-end snapshot timestamps, coverage
floors, loader-compatible export emission, distinct per-snapshot signals, the
synthetic-path refusal, and the no-data failure. All HTTP is faked; no network.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from src.campaign.integrated import RealDataUnavailable
from src.data import options_candle_backfill as backfill
from src.data.loader import DataLoader
from src.features.options_pricing import black_scholes_price
from src.data.schemas import PricingInputs

SPOT = 66825.3
EXPIRIES = ("261127", "261204")


class FakeResponse:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Dict[str, Any]:
        return self._payload


class FakeSession:
    """Deterministic offline OKX option-candle double."""

    def __init__(self, candles: Dict[str, List[List[Any]]], tickers: Optional[List[Dict[str, Any]]] = None) -> None:
        self.candles = candles
        self.tickers = tickers or []
        self.calls: List[tuple] = []

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 0.0) -> FakeResponse:
        params = params or {}
        self.calls.append((url, dict(params), timeout))
        if url.endswith(backfill.INSTRUMENTS_ENDPOINT):
            return FakeResponse({"code": "0", "data": _instruments()})
        if url.endswith(backfill.HISTORY_CANDLES_ENDPOINT):
            rows = self.candles.get(str(params.get("instId")), [])
            return FakeResponse({"code": "0", "data": rows})
        if url.endswith(backfill.TICKERS_ENDPOINT):
            return FakeResponse({"code": "0", "data": self.tickers})
        raise AssertionError(f"unexpected URL: {url}")


def _expiry_dt(token: str) -> datetime:
    return datetime.strptime("20" + token, "%Y%m%d").replace(tzinfo=timezone.utc)


def _instruments() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for token in EXPIRIES:
        for strike in (60000.0, 65000.0, 70000.0):
            for right in ("C", "P"):
                rows.append(
                    {
                        "instId": f"BTC-USD-{token}-{int(strike)}-{right}",
                        "state": "live",
                        "ctVal": "1",
                    }
                )
    return rows


def _candle_rows(inst_id: str, *, base_ms: int, n_bars: int, drift: float) -> List[List[Any]]:
    """Build OKX-shaped candles: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]."""
    parts = inst_id.split("-")
    token = parts[2]
    strike = float(parts[3])
    right = parts[4]
    rows: List[List[Any]] = []
    for i in range(n_bars):
        bar_start = base_ms + i * 300_000
        spot = SPOT * (1.0 + drift * i)
        texp = (_expiry_dt(token) - datetime.fromtimestamp(bar_start / 1000.0, tz=timezone.utc)).total_seconds() / (
            365.25 * 24 * 3600
        )
        price = black_scholes_price(
            PricingInputs(
                spot=spot, strike=strike, rate=0.0, volatility=0.6,
                time_to_expiry=max(texp, 1e-6), option_type="call" if right == "C" else "put", seed=42,
            )
        )
        close = price / spot  # BTC per 1 BTC, the OKX inverse convention
        rows.append([str(bar_start), str(close), str(close), str(close), str(close), "0", "0", "0", "1"])
    return rows


def _all_candles(*, n_bars: int = 12, drift: float = 0.0005) -> Dict[str, List[List[Any]]]:
    base_ms = int(datetime(2026, 11, 14, 11, 30, tzinfo=timezone.utc).timestamp() * 1000)
    return {inst_id: _candle_rows(inst_id, base_ms=base_ms, n_bars=n_bars, drift=drift) for inst_id in _instrument_ids()}


def _instrument_ids() -> List[str]:
    return [row["instId"] for row in _instruments()]


def _tickers() -> List[Dict[str, Any]]:
    return [
        {"instId": inst_id, "bidPx": "0.0200", "askPx": "0.0204", "ts": "1794655800000"}
        for inst_id in _instrument_ids()
    ]


def test_candles_group_by_bar_and_snapshot_uses_bar_end() -> None:
    session = FakeSession(_all_candles(n_bars=12), _tickers())
    candles = backfill.fetch_option_candles(
        [{"inst_id": i} for i in _instrument_ids()], session=session, bar="5m", limit=100,
        request_delay_seconds=0.0,
    )
    assert len(candles) == 12
    snapshots = backfill.build_snapshots(
        candles,
        backfill.fetch_live_option_instruments("BTC", session=session, spot=SPOT),
        bar="5m",
        spreads={i: 0.0002 for i in _instrument_ids()},
    )
    assert len(snapshots) == 12
    first_bar_start = min(candles)
    expected_end = datetime.fromtimestamp(first_bar_start / 1000.0, tz=timezone.utc) + timedelta(minutes=5)
    assert snapshots[0].bar_end == expected_end.isoformat().replace("+00:00", "Z")
    assert snapshots[0].n_quotes == 12
    assert snapshots[0].n_expiries == len(EXPIRIES)
    for quote in snapshots[0].quotes:
        assert quote["bid"] < quote["mark"] < quote["ask"]
        assert quote["price_mode"] == "candle_close_with_reconstructed_spread"
        assert quote["spread_source"] == "okx_ticker_measured"


def test_coverage_floors_drop_sparse_bars() -> None:
    raw = _all_candles(n_bars=12)
    # one bar with only two instruments fails the >= 8 quote floor
    candles = backfill.group_candles_by_bar({k: v[:1] for k, v in list(raw.items())[:2]}, bar="5m")
    assert backfill.build_snapshots(candles, backfill.fetch_live_option_instruments("BTC", session=FakeSession(candles)), bar="5m") == []
    # one expiry only fails the >= 2 expiry floor
    one_expiry = backfill.group_candles_by_bar({k: v for k, v in raw.items() if "-261127-" in k}, bar="5m")
    assert backfill.build_snapshots(one_expiry, backfill.fetch_live_option_instruments("BTC", session=FakeSession(candles)), bar="5m") == []


def test_constant_spread_fallback_when_tickers_missing() -> None:
    session = FakeSession(_all_candles(n_bars=6))
    candles = backfill.fetch_option_candles(
        [{"inst_id": i} for i in _instrument_ids()], session=session, bar="5m", limit=100,
        request_delay_seconds=0.0,
    )
    snapshots = backfill.build_snapshots(
        candles, backfill.fetch_live_option_instruments("BTC", session=session, spot=SPOT), bar="5m"
    )
    assert snapshots
    assert all(q["spread_source"] == "constant_fallback" for q in snapshots[0].quotes)


def test_backfill_writes_loader_compatible_exports(tmp_path: Path) -> None:
    session = FakeSession(_all_candles(n_bars=12), _tickers())
    result = backfill.backfill_dense_option_snapshots(
        underlying="BTC", spot=SPOT, bar="5m", limit=100, out_dir=tmp_path,
        request_delay_seconds=0.0, session=session,
        timestamp="2026-11-14T20:00:00Z",
    )
    assert result.n_snapshots == 12
    assert len(result.paths) == 12
    assert result.span_seconds == 11 * 300.0
    assert result.authenticity_verified is False

    chain = DataLoader(cache=False).load_options_chain(result.paths[0], venue="okx", underlying="BTC")
    assert chain.quotes
    assert all(q.bid > 0.0 and q.ask > 0.0 for q in chain.quotes)

    raw = json.loads(Path(result.paths[0]).read_text(encoding="utf-8"))
    assert raw["schema"] == "okx_public_options_candle_backfill_v1"
    assert raw["source"]["derived_from"] == "okx_market_history_candles"
    assert raw["source"]["candle_bar"] == "5m"
    assert raw["acquired_at"] == result.snapshots[0].bar_end


def test_written_series_yields_distinct_time_varying_signals(tmp_path: Path) -> None:
    from src.analytics.options_time_varying_signal import load_snapshot_signals

    session = FakeSession(_all_candles(n_bars=12, drift=0.0005), _tickers())
    result = backfill.backfill_dense_option_snapshots(
        underlying="BTC", spot=SPOT, bar="5m", limit=100, out_dir=tmp_path,
        request_delay_seconds=0.0, session=session,
        timestamp="2026-11-14T20:00:00Z",
    )
    signals = load_snapshot_signals("BTC", tmp_path)
    assert len(signals) == result.n_snapshots
    levels = [s.options_signal_raw for s in signals]
    assert len({round(v, 12) for v in levels}) > 1
    stamps = [s.snapshot_timestamp for s in signals]
    assert stamps == sorted(stamps)
    assert stamps[0] == result.snapshots[0].bar_end


def test_missing_candles_raise_real_data_unavailable(tmp_path: Path) -> None:
    with pytest.raises(RealDataUnavailable):
        backfill.backfill_dense_option_snapshots(
            underlying="BTC", spot=SPOT, bar="5m", out_dir=tmp_path,
            request_delay_seconds=0.0, session=FakeSession({}),
            timestamp="2026-11-14T20:00:00Z",
        )


def test_synthetic_output_path_is_refused(tmp_path: Path) -> None:
    snapshots = backfill.build_snapshots(
        backfill.group_candles_by_bar(_all_candles(n_bars=6), bar="5m"),
        backfill.fetch_live_option_instruments("BTC", session=FakeSession(_all_candles()), spot=SPOT),
        bar="5m",
    )
    with pytest.raises(backfill.AcquisitionError):
        backfill.write_snapshot_exports(
            snapshots[:1], out_dir=tmp_path, underlying="BTC-SYNTHETIC"
        )


def test_unsupported_bar_is_rejected() -> None:
    with pytest.raises(backfill.AcquisitionError):
        backfill._bar_seconds("7m")


# ---------------------------------------------------------------------------
# Historical-window paging (EVAL-46): max_pages / after / before
# ---------------------------------------------------------------------------


class PagingSession:
    """Fake OKX that serves *pages* of candles per instrument via after/before."""

    def __init__(self, pages_by_inst: Dict[str, List[List[List[Any]]]]) -> None:
        # pages_by_inst[inst_id] = [page0_rows, page1_rows, ...] newest-first pages
        self.pages_by_inst = pages_by_inst
        self.calls: List[Dict[str, Any]] = []

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 0.0) -> FakeResponse:
        params = params or {}
        self.calls.append({"url": url, **params})
        if url.endswith(backfill.INSTRUMENTS_ENDPOINT):
            return FakeResponse({"code": "0", "data": _instruments()})
        if url.endswith(backfill.HISTORY_CANDLES_ENDPOINT):
            inst = str(params.get("instId"))
            pages = self.pages_by_inst.get(inst, [])
            after = params.get("after")
            if after is None:
                page = pages[0] if pages else []
                return FakeResponse({"code": "0", "data": page})
            # emulate: after = oldest ts of previous page -> return next older page
            after_ms = int(after)
            older = [p for p in pages if p and min(int(r[0]) for r in p) < after_ms]
            if older:
                return FakeResponse({"code": "0", "data": older[0]})
            return FakeResponse({"code": "0", "data": []})
        if url.endswith(backfill.TICKERS_ENDPOINT):
            return FakeResponse({"code": "0", "data": []})
        raise AssertionError(f"unexpected URL: {url}")


def _ms_pages(inst_ids: List[str], *, base_ms: int, n_pages: int, per_page: int) -> Dict[str, List[List[List[Any]]]]:
    """Build newest-first pages: page k covers the k-th most recent block."""
    out: Dict[str, List[List[List[Any]]]] = {}
    for inst_id in inst_ids:
        pages: List[List[List[Any]]] = []
        # newest page first; each subsequent page is older
        for k in range(n_pages):
            # block k: starts at base_ms + (n_pages-1-k)*per_page*300_000 (older for larger k)
            start = base_ms + (n_pages - 1 - k) * per_page * 300_000
            rows = _candle_rows(inst_id, base_ms=start, n_bars=per_page, drift=0.0)
            rows = list(reversed(rows))  # newest-first within a page, like OKX
            pages.append(rows)
        out[inst_id] = pages
    return out


def test_max_pages_accumulates_backward_history() -> None:
    ids = _instrument_ids()
    base_ms = int(datetime(2026, 11, 14, 11, 30, tzinfo=timezone.utc).timestamp() * 1000)
    pages = _ms_pages(ids, base_ms=base_ms, n_pages=3, per_page=100)
    session = PagingSession(pages)
    candles = backfill.fetch_option_candles(
        [{"inst_id": i} for i in ids], session=session, bar="5m", limit=100,
        request_delay_seconds=0.0, max_pages=3,
    )
    # 3 pages x 100 bars = 300 distinct bars (assuming no overlap)
    assert len(candles) == 300
    # paging must have issued >1 history-candles call per instrument
    hist_calls = [c for c in session.calls if backfill.HISTORY_CANDLES_ENDPOINT in c.get("url", "")]
    # second page must carry an after cursor
    after_calls = [c for c in session.calls if "after" in c]
    assert after_calls, "expected backward paging via after cursor"
    assert all(str(c["after"]).isdigit() for c in after_calls)


def test_max_pages_one_keeps_single_page_semantics() -> None:
    ids = _instrument_ids()
    base_ms = int(datetime(2026, 11, 14, 11, 30, tzinfo=timezone.utc).timestamp() * 1000)
    pages = _ms_pages(ids, base_ms=base_ms, n_pages=3, per_page=100)
    session = PagingSession(pages)
    candles = backfill.fetch_option_candles(
        [{"inst_id": i} for i in ids], session=session, bar="5m", limit=100,
        request_delay_seconds=0.0, max_pages=1,
    )
    assert len(candles) == 100
    assert not [c for c in session.calls if "after" in c]


def test_max_pages_rejects_non_positive() -> None:
    session = PagingSession({})
    with pytest.raises(backfill.AcquisitionError):
        backfill.fetch_option_candles(
            [{"inst_id": "BTC-USD-261127-60000-C"}], session=session, max_pages=0,
            request_delay_seconds=0.0,
        )


def test_coerce_cursor_accepts_iso_and_ms() -> None:
    assert backfill._coerce_cursor(None) is None
    assert backfill._coerce_cursor("") is None
    assert backfill._coerce_cursor(1794655800000) == "1794655800000"
    assert backfill._coerce_cursor("1794655800000") == "1794655800000"
    iso_ms = backfill._coerce_cursor("2026-11-14T15:01:50Z")
    assert iso_ms is not None and iso_ms.isdigit()


def test_backfill_records_paging_metadata(tmp_path: Path) -> None:
    ids = _instrument_ids()
    base_ms = int(datetime(2026, 11, 14, 11, 30, tzinfo=timezone.utc).timestamp() * 1000)
    pages = _ms_pages(ids, base_ms=base_ms, n_pages=2, per_page=12)
    session = PagingSession(pages)
    result = backfill.backfill_dense_option_snapshots(
        underlying="BTC", spot=SPOT, bar="5m", limit=12, out_dir=tmp_path,
        request_delay_seconds=0.0, session=session, max_pages=2,
        timestamp="2026-11-14T20:00:00Z",
    )
    assert result.max_pages == 2
    assert result.after is None and result.before is None
    assert result.n_snapshots == 24