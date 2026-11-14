"""Public real-data acquisition (EVAL-26, paper-only).

The EVAL-25 gate is code-complete but data-blocked: ``data/raw/`` contains only
synthetic tapes and no real option chain. This module removes that last
bottleneck without credentials or order placement.

It fetches **read-only public** OKX market data (the same public endpoints the
repository's ``src.ingestion.okx`` client already uses) and writes
loader-compatible, provenance-stamped exports under ``data/raw/``:

  * ``orderflow_okx_<instrument>.json`` — paginated public trade tape from
    ``/api/v5/market/history-trades`` (no authentication, no ``.env``);
  * ``options_okx_<UNDERLYING>_<UTC>.json`` — option instruments and tickers
    from ``/api/v5/public/instruments`` and ``/api/v5/market/tickers``.

The adapter never substitutes synthetic data, never claims provenance it cannot
verify (``authenticity_verified=false``), and never emits ``{"valid": true}``.
A GO/NO-GO decision remains with the sealed EVAL-22/EVAL-24/EVAL-25 gates.

CLI::

    python -m src.data.public_export_acquisition \
        --underlying BTC --orderflow-instrument BTC-USD-SWAP \
        --min-bars 1550 --bar-duration-seconds 15
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import requests

from src.analytics.measurement_validity_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_MIN_RETURNS,
    DEFAULT_MIN_WINDOWS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TRAIN_WINDOW,
    _stamp_for_filename,
    _utc_now_iso,
)
from src.analytics.sample_adequacy_acquisition import _count_windows_for_bars
from src.data.options_exports import (
    DEFAULT_MIN_CONTRACTS,
    DEFAULT_MIN_EXPIRIES,
    DEFAULT_MIN_QUOTES,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "PUBLIC_EXPORT_ACQUISITION_26"
OUT_DIR = Path("research_state")
DATA_RAW_DIR = Path("data/raw")

OKX_BASE_URL = "https://www.okx.com"
HISTORY_TRADES_ENDPOINT = "/api/v5/market/history-trades"
INSTRUMENTS_ENDPOINT = "/api/v5/public/instruments"
TICKERS_ENDPOINT = "/api/v5/market/tickers"

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# EVAL-22 adequacy floors. The acquisition target is deliberately a little
# above the floor so a few empty bars cannot push the tape below it.
DEFAULT_MIN_BARS = 1550
DEFAULT_PAGE_LIMIT = 100
DEFAULT_MAX_PAGES = 4000
DEFAULT_REQUEST_DELAY_SECONDS = 0.10
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_RETRIES = 4

_OPTION_ID_RE = re.compile(
    r"^([A-Z0-9]+)-([A-Z0-9]+)-(\d{6}|\d{8})-(\d+(?:\.\d+)?)-([CP])$"
)
_SYNTHETIC_MARKERS: Tuple[str, ...] = ("synthetic",)


class AcquisitionError(RuntimeError):
    """A public export could not be fetched or written."""


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_ts_ms(value: Any) -> datetime:
    """Strictly parse an epoch-millisecond timestamp; never substitute ``now``."""
    try:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc)
        elif isinstance(value, str) and value.strip():
            dt = datetime.fromtimestamp(float(value.strip()) / 1000.0, tz=timezone.utc)
        else:
            raise AcquisitionError(f"unparseable timestamp: {value!r}")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if not math.isfinite(dt.timestamp()):
            raise AcquisitionError(f"non-finite timestamp: {value!r}")
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError, OSError) as exc:
        raise AcquisitionError(f"unparseable timestamp: {value!r}") from exc


def _parse_option_id(inst_id: str) -> Optional[Dict[str, Any]]:
    """Parse ``BTC-USD-261127-102000-C`` into static option terms."""
    match = _OPTION_ID_RE.match(str(inst_id or "").strip())
    if not match:
        return None
    underlying, _quote_ccy, expiry_raw, strike_raw, right = match.groups()
    try:
        if len(expiry_raw) == 8:
            expiry = datetime.strptime(expiry_raw, "%Y%m%d").replace(tzinfo=timezone.utc)
        else:
            expiry = datetime.strptime(expiry_raw, "%y%m%d").replace(tzinfo=timezone.utc)
        strike = float(strike_raw)
    except (ValueError, TypeError):
        return None
    if strike <= 0:
        return None
    return {
        "underlying": underlying.upper(),
        "expiry": expiry,
        "strike": strike,
        "option_type": "call" if right == "C" else "put",
    }


def _get_json(
    session: Any,
    endpoint: str,
    params: Mapping[str, Any],
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Dict[str, Any]:
    """GET a public OKX endpoint with bounded retry/backoff and code checks."""
    url = f"{OKX_BASE_URL}{endpoint}"
    last_exc: Optional[Exception] = None
    for attempt in range(max(int(max_retries), 1)):
        try:
            response = session.get(url, params=dict(params), timeout=timeout)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise AcquisitionError(f"{endpoint}: non-object response")
            if str(payload.get("code")) not in ("0", "00000"):
                raise AcquisitionError(
                    f"{endpoint}: API code={payload.get('code')!r} "
                    f"msg={payload.get('msg')!r}"
                )
            return payload
        except AcquisitionError:
            raise
        except Exception as exc:  # noqa: BLE001  (retry transient transport errors)
            last_exc = exc
            if attempt + 1 < max(int(max_retries), 1):
                time.sleep(min(2.0, 0.2 * (attempt + 1)))
    raise AcquisitionError(f"{endpoint}: request failed after retries: {last_exc}")


def _as_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _bar_count(trades: Sequence[Mapping[str, Any]], bar_duration_seconds: float) -> int:
    if not trades:
        return 0
    start = min(_parse_ts_ms(t["timestamp_ms"]) for t in trades)
    end = max(_parse_ts_ms(t["timestamp_ms"]) for t in trades)
    span = (end - start).total_seconds()
    return max(1, int(math.ceil(span / max(float(bar_duration_seconds), 1.0))))


def fetch_okx_history_trades(
    inst_id: str,
    *,
    session: Any,
    min_bars: int = DEFAULT_MIN_BARS,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    page_limit: int = DEFAULT_PAGE_LIMIT,
    max_pages: int = DEFAULT_MAX_PAGES,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Dict[str, Any]:
    """Fetch a real, paginated public trade tape for ``inst_id``.

    OKX ``history-trades`` returns newest-first pages; ``after`` pages backwards
    from the oldest trade id of the previous page. Duplicate trade ids are
    dropped, so the result is independent of page overlap. The loop stops when
    the tape spans at least ``min_bars`` bars, the venue stops returning rows,
    or ``max_pages`` is reached.
    """
    trades: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    after: Optional[str] = None
    pages = 0
    target_span_seconds = max(int(min_bars), 1) * max(float(bar_duration_seconds), 1.0)

    while pages < max(int(max_pages), 1):
        params: Dict[str, Any] = {
            "instId": str(inst_id),
            "limit": str(max(int(page_limit), 1)),
        }
        if after is not None:
            params["after"] = str(after)
        payload = _get_json(
            session,
            HISTORY_TRADES_ENDPOINT,
            params,
            timeout=timeout,
            max_retries=max_retries,
        )
        rows = payload.get("data") or []
        if not isinstance(rows, list) or not rows:
            break

        new_rows = 0
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            trade_id = str(row.get("tradeId") or "").strip()
            if not trade_id or trade_id in seen_ids:
                continue
            price = _as_float(row.get("px"))
            size = _as_float(row.get("sz"))
            if price is None or price <= 0 or size is None or size < 0:
                continue
            try:
                ts = _parse_ts_ms(row.get("ts"))
            except AcquisitionError:
                continue
            side = str(row.get("side") or "").strip().lower()
            if side not in ("buy", "sell"):
                side = "buy" if str(row.get("side") or "").strip().lower() in ("bid", "b") else "sell"
            seen_ids.add(trade_id)
            trades.append(
                {
                    "trade_id": trade_id,
                    "instrument": str(row.get("instId") or inst_id),
                    "price": float(price),
                    "size": float(size),
                    "side": side,
                    "timestamp_ms": int(ts.timestamp() * 1000),
                    "timestamp": _iso(ts),
                }
            )
            new_rows += 1

        pages += 1
        last_id = str(rows[-1].get("tradeId") or "").strip() if isinstance(rows[-1], Mapping) else ""
        if new_rows == 0 or not last_id:
            break
        after = last_id

        if trades:
            start = min(_parse_ts_ms(t["timestamp_ms"]) for t in trades)
            end = max(_parse_ts_ms(t["timestamp_ms"]) for t in trades)
            if (end - start).total_seconds() >= target_span_seconds:
                break
        if len(rows) < max(int(page_limit), 1):
            break
        if request_delay_seconds > 0:
            time.sleep(float(request_delay_seconds))

    trades.sort(key=lambda t: (int(t["timestamp_ms"]), str(t["trade_id"])))
    n_bars = _bar_count(trades, bar_duration_seconds)
    span_seconds = 0.0
    if trades:
        span_seconds = (
            _parse_ts_ms(trades[-1]["timestamp_ms"]) - _parse_ts_ms(trades[0]["timestamp_ms"])
        ).total_seconds()
    return {
        "instrument": str(inst_id),
        "trades": trades,
        "n_trades": len(trades),
        "n_bars": int(n_bars),
        "span_seconds": float(span_seconds),
        "pages": int(pages),
        "target_span_seconds": float(target_span_seconds),
    }


def fetch_okx_option_chain(
    underlying: str,
    *,
    session: Any,
    now: Optional[datetime] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Dict[str, Any]:
    """Fetch a real public option cross-section for ``underlying``.

    Only contracts with a positive, non-crossed bid/ask and a future expiry are
    emitted. Every quote carries the ticker timestamp, never ``now`` as a
    substitute for a missing timestamp.
    """
    underlying = str(underlying).strip().upper()
    uly = f"{underlying}-USD"
    now = now or datetime.now(timezone.utc)
    instruments = _get_json(
        session,
        INSTRUMENTS_ENDPOINT,
        {"instType": "OPTION", "uly": uly},
        timeout=timeout,
        max_retries=max_retries,
    ).get("data") or []
    tickers = _get_json(
        session,
        TICKERS_ENDPOINT,
        {"instType": "OPTION", "uly": uly},
        timeout=timeout,
        max_retries=max_retries,
    ).get("data") or []
    if not isinstance(instruments, list) or not isinstance(tickers, list):
        raise AcquisitionError(f"{underlying}: instruments/tickers payload is not a list")

    ticker_map: Dict[str, Mapping[str, Any]] = {}
    for ticker in tickers:
        if isinstance(ticker, Mapping) and ticker.get("instId"):
            ticker_map[str(ticker["instId"])] = ticker

    quotes: List[Dict[str, Any]] = []
    expiries: set[str] = set()
    for instrument in instruments:
        if not isinstance(instrument, Mapping):
            continue
        inst_id = str(instrument.get("instId") or "").strip()
        parsed = _parse_option_id(inst_id)
        if not parsed or parsed["underlying"] != underlying:
            continue
        expiry = parsed["expiry"]
        if expiry <= now:
            continue
        ticker = ticker_map.get(inst_id)
        if not ticker:
            continue
        bid = _as_float(ticker.get("bidPx"))
        ask = _as_float(ticker.get("askPx"))
        if bid is None or ask is None or bid <= 0 or ask <= 0 or ask < bid:
            continue
        try:
            quote_ts = _parse_ts_ms(ticker.get("ts"))
        except AcquisitionError:
            continue
        if quote_ts <= now - timedelta(days=2):
            continue
        contract_size = _as_float(instrument.get("ctVal")) or 1.0
        quotes.append(
            {
                "symbol": inst_id,
                "underlying": underlying,
                "strike": float(parsed["strike"]),
                "expiry": _iso(expiry),
                "option_type": parsed["option_type"],
                "venue": "okx",
                "contract_size": float(contract_size),
                "bid": float(bid),
                "ask": float(ask),
                "last": _as_float(ticker.get("last")),
                "mark": _as_float(ticker.get("markPx")),
                "bid_iv": _as_float(ticker.get("bidVol")),
                "ask_iv": _as_float(ticker.get("askVol")),
                "mark_iv": _as_float(ticker.get("markVol")),
                "delta": _as_float(ticker.get("delta")),
                "gamma": _as_float(ticker.get("gamma")),
                "theta": _as_float(ticker.get("theta")),
                "vega": _as_float(ticker.get("vega")),
                "open_interest": _as_float(ticker.get("oi")) or 0.0,
                "volume": _as_float(ticker.get("vol24h")) or 0.0,
                "timestamp": _iso(quote_ts),
            }
        )
        expiries.add(_iso(expiry))

    quotes.sort(key=lambda q: (q["expiry"], q["strike"], q["option_type"], q["symbol"]))
    return {
        "underlying": underlying,
        "venue": "okx",
        "quotes": quotes,
        "n_quotes": len(quotes),
        "n_contracts": len({q["symbol"] for q in quotes}),
        "n_expiries": len(expiries),
        "expiries": sorted(expiries),
        "uly": uly,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ensure_not_synthetic(path: Path) -> None:
    if any(marker in path.name.lower() for marker in _SYNTHETIC_MARKERS):
        raise AcquisitionError(f"refusing synthetic-marked output path: {path.name}")


def write_orderflow_tape(result: Mapping[str, Any], path: Path) -> Path:
    """Write a loader-compatible orderflow tape with explicit provenance."""
    path = Path(path)
    _ensure_not_synthetic(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    trades = []
    for trade in result["trades"]:
        trades.append(
            {
                "trade_id": trade["trade_id"],
                "symbol": result["instrument"],
                "venue": "okx",
                "price": trade["price"],
                "size": trade["size"],
                "side": trade["side"],
                "timestamp": trade["timestamp"],
            }
        )
    payload = {
        "schema": "okx_public_trades_v1",
        "symbol": result["instrument"],
        "venue": "okx",
        "trades": trades,
        "liquidations": [],
        "funding_rates": [],
        "acquired_at": _iso(datetime.now(timezone.utc)),
        "source": {
            "venue": "okx",
            "endpoint": HISTORY_TRADES_ENDPOINT,
            "instrument": result["instrument"],
            "authenticated": False,
            "public_read_only": True,
        },
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return path


def write_options_chain(result: Mapping[str, Any], path: Path) -> Path:
    """Write a loader-compatible option-chain export with explicit provenance."""
    path = Path(path)
    _ensure_not_synthetic(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "okx_public_options_v1",
        "underlying": result["underlying"],
        "venue": "okx",
        "quotes": list(result["quotes"]),
        "acquired_at": _iso(datetime.now(timezone.utc)),
        "source": {
            "venue": "okx",
            "endpoints": [INSTRUMENTS_ENDPOINT, TICKERS_ENDPOINT],
            "uly": result["uly"],
            "authenticated": False,
            "public_read_only": True,
        },
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return path


def _write_markdown(report: Mapping[str, Any]) -> str:
    of = report.get("orderflow") or {}
    op = report.get("options") or {}
    lines = [
        f"# {report['report_id']} — PUBLIC REAL-DATA ACQUISITION (EVAL-26)",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- trading_mode: {report['trading_mode']} "
        f"(live_trading_enabled={str(report['live_trading_enabled']).lower()})",
        f"- data_provenance: {report['data_provenance']} "
        f"(authenticity_verified={str(report['authenticity_verified']).lower()})",
        f"- source: {report['source']}",
        "",
        "## Orderflow tape",
        "",
        f"- instrument: `{of.get('instrument')}`",
        f"- path: `{of.get('path')}`",
        f"- n_trades: {of.get('n_trades')}, n_bars: {of.get('n_bars')}, "
        f"span_seconds: {of.get('span_seconds')}, pages: {of.get('pages')}",
        f"- content_sha256: `{of.get('content_sha256')}`",
        "",
        "## Option chain",
        "",
        f"- underlying: `{op.get('underlying')}`",
        f"- path: `{op.get('path')}`",
        f"- n_quotes: {op.get('n_quotes')}, n_contracts: {op.get('n_contracts')}, "
        f"n_expiries: {op.get('n_expiries')}",
        f"- expiries: {op.get('expiries')}",
        f"- content_sha256: `{op.get('content_sha256')}`",
        "",
        "## Adequacy preview (sealed floors)",
        "",
        f"- {report.get('adequacy')}",
        "",
        "This is an acquisition/readiness artifact only. The sealed EVAL-22, "
        "EVAL-24 and EVAL-25 gates remain the only source of a GO/NO-GO verdict; "
        "synthetic data is never relabeled and no ``{\"valid\": true}`` is emitted.",
        "",
    ]
    return "\n".join(lines)


def acquire_public_exports(
    *,
    underlying: str = "BTC",
    orderflow_instrument: str = "BTC-USD-SWAP",
    orderflow_symbol: Optional[str] = None,
    data_dir: Path | str = DATA_RAW_DIR,
    out_dir: Path | str = OUT_DIR,
    timestamp: Optional[str] = None,
    min_bars: int = DEFAULT_MIN_BARS,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    page_limit: int = DEFAULT_PAGE_LIMIT,
    max_pages: int = DEFAULT_MAX_PAGES,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    skip_orderflow: bool = False,
    skip_options: bool = False,
    session: Any = None,
) -> Dict[str, Any]:
    """Fetch public OKX exports, write loader-compatible files and seal a report.

    ``session`` is injectable for offline tests; production uses a fresh
    ``requests.Session``. No credentials, no order placement, no ``.env``.
    """
    stamp = timestamp or _utc_now_iso()
    data_dir = Path(data_dir)
    out_dir = Path(out_dir)
    session = session or requests.Session()

    orderflow_path = data_dir / f"orderflow_okx_{orderflow_symbol or orderflow_instrument}.json"
    options_path = (
        data_dir
        / f"options_okx_{underlying.upper()}_{_stamp_for_filename(stamp)}.json"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "data_provenance": "real_public_exchange_export",
        "authenticity_verified": False,
        "source": {
            "venue": "okx",
            "endpoints": [
                HISTORY_TRADES_ENDPOINT,
                INSTRUMENTS_ENDPOINT,
                TICKERS_ENDPOINT,
            ],
            "authenticated": False,
            "public_read_only": True,
            "network": "public_market_data_only",
        },
        "orderflow": None,
        "options": None,
        "adequacy": None,
    }

    if not skip_orderflow:
        of_result = fetch_okx_history_trades(
            orderflow_instrument,
            session=session,
            min_bars=min_bars,
            bar_duration_seconds=bar_duration_seconds,
            page_limit=page_limit,
            max_pages=max_pages,
            request_delay_seconds=request_delay_seconds,
            timeout=timeout,
            max_retries=max_retries,
        )
        write_orderflow_tape(of_result, orderflow_path)
        n_bars = int(of_result["n_bars"])
        n_windows = _count_windows_for_bars(
            n_bars,
            DEFAULT_TRAIN_WINDOW,
            DEFAULT_TEST_WINDOW,
            DEFAULT_STEP_SIZE,
        )
        n_returns = max(0, n_bars - 1)
        report["orderflow"] = {
            "instrument": of_result["instrument"],
            "path": str(orderflow_path),
            "content_sha256": _sha256(orderflow_path),
            "n_trades": int(of_result["n_trades"]),
            "n_bars": n_bars,
            "n_returns": int(n_returns),
            "n_windows": int(n_windows),
            "span_seconds": float(of_result["span_seconds"]),
            "pages": int(of_result["pages"]),
            "start_timestamp": of_result["trades"][0]["timestamp"] if of_result["trades"] else None,
            "end_timestamp": of_result["trades"][-1]["timestamp"] if of_result["trades"] else None,
        }

    if not skip_options:
        op_result = fetch_okx_option_chain(
            underlying,
            session=session,
            now=datetime.now(timezone.utc),
            timeout=timeout,
            max_retries=max_retries,
        )
        write_options_chain(op_result, options_path)
        report["options"] = {
            "underlying": op_result["underlying"],
            "path": str(options_path),
            "content_sha256": _sha256(options_path),
            "n_quotes": int(op_result["n_quotes"]),
            "n_contracts": int(op_result["n_contracts"]),
            "n_expiries": int(op_result["n_expiries"]),
            "expiries": list(op_result["expiries"]),
            "uly": op_result["uly"],
        }

    of = report.get("orderflow") or {}
    op = report.get("options") or {}
    report["adequacy"] = {
        "orderflow_min_returns": int(DEFAULT_MIN_RETURNS),
        "orderflow_min_windows": int(DEFAULT_MIN_WINDOWS),
        "orderflow_bar_duration_seconds": float(bar_duration_seconds),
        "orderflow_adequate": bool(
            of
            and int(of.get("n_returns", 0)) >= int(DEFAULT_MIN_RETURNS)
            and int(of.get("n_windows", 0)) >= int(DEFAULT_MIN_WINDOWS)
        ),
        "options_min_contracts": int(DEFAULT_MIN_CONTRACTS),
        "options_min_quotes": int(DEFAULT_MIN_QUOTES),
        "options_min_expiries": int(DEFAULT_MIN_EXPIRIES),
        "options_adequate": bool(
            op
            and int(op.get("n_contracts", 0)) >= int(DEFAULT_MIN_CONTRACTS)
            and int(op.get("n_quotes", 0)) >= int(DEFAULT_MIN_QUOTES)
            and int(op.get("n_expiries", 0)) >= int(DEFAULT_MIN_EXPIRIES)
        ),
    }

    serialized = serialize_metrics_strict(report)
    assert_json_valid(serialized)

    out_dir.mkdir(parents=True, exist_ok=True)
    filename_stamp = _stamp_for_filename(stamp)
    json_path = out_dir / f"PUBLIC_EXPORT_ACQUISITION_{filename_stamp}.json"
    md_path = out_dir / f"PUBLIC_EXPORT_ACQUISITION_{filename_stamp}.md"
    serialized["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
    json_path.write_text(
        json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")
    result = dict(serialized)
    result["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Acquire public OKX real-data exports (EVAL-26, paper-only)."
    )
    parser.add_argument("--underlying", default="BTC", help="option underlying, e.g. BTC")
    parser.add_argument(
        "--orderflow-instrument",
        default="BTC-USD-SWAP",
        help="public OKX instrument id for the trade tape",
    )
    parser.add_argument(
        "--orderflow-symbol",
        default=None,
        help="filename symbol token (default: --orderflow-instrument)",
    )
    parser.add_argument("--data-dir", default=str(DATA_RAW_DIR), help="raw data output dir")
    parser.add_argument("--out", default=str(OUT_DIR), help="artifact output dir")
    parser.add_argument("--timestamp", default=None, help="UTC timestamp for artifact names")
    parser.add_argument("--min-bars", type=int, default=DEFAULT_MIN_BARS)
    parser.add_argument(
        "--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS
    )
    parser.add_argument("--page-limit", type=int, default=DEFAULT_PAGE_LIMIT)
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument(
        "--request-delay-seconds", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--skip-orderflow", action="store_true")
    parser.add_argument("--skip-options", action="store_true")
    args = parser.parse_args(argv)

    report = acquire_public_exports(
        underlying=args.underlying,
        orderflow_instrument=args.orderflow_instrument,
        orderflow_symbol=args.orderflow_symbol,
        data_dir=Path(args.data_dir),
        out_dir=Path(args.out),
        timestamp=args.timestamp,
        min_bars=args.min_bars,
        bar_duration_seconds=args.bar_duration_seconds,
        page_limit=args.page_limit,
        max_pages=args.max_pages,
        request_delay_seconds=args.request_delay_seconds,
        timeout=args.timeout,
        max_retries=args.max_retries,
        skip_orderflow=args.skip_orderflow,
        skip_options=args.skip_options,
    )
    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "generated_at": report["generated_at"],
                "orderflow": report.get("orderflow"),
                "options": report.get("options"),
                "adequacy": report.get("adequacy"),
                "artifact_paths": report.get("artifact_paths"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())