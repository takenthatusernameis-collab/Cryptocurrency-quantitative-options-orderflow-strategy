"""Retrospective dense real options snapshot series from OKX option candles (EVAL-41 Track B).

This module removes the EVAL-41 Track B bottleneck. OKX option *tickers* are
current-only, so the previous handoff required >= 2 h of wall-clock polling to
collect >= 12 real snapshots. The public, read-only
``/api/v5/market/history-candles`` endpoint serves **historical** per-instrument
option prices (5m/15m/1H bars), so a dense, real, loader-compatible snapshot
series can be reconstructed *retroactively* in a single pass: no waiting, no
credentials, no synthetic fallback.

Provenance rules (non-negotiable):

  * every price is an OKX option candle **close** for a real instrument at a real
    timestamp — never a model output, never relabelled synthetic;
  * a snapshot is timestamped at the candle's **bar end** (``bar_start + bar``),
    not its bar start, so no future information leaks into the bar it is aligned to;
  * bid/ask are reconstructed around the measured close using the instrument's
    *measured* live relative spread when available (fallback: an explicit constant
    recorded in the artifact). ``price_mode`` records this per quote, so no consumer
    can mistake a reconstructed quote for a venue quote;
  * ``authenticity_verified`` stays ``false`` and no ``{"valid": true}`` is emitted.

CLI::

    python -m src.data.options_candle_backfill \
        --underlying BTC --expiries 261120,261127,261204 --bar 5m --limit 100 \
        --out data/raw/options_candles --data-dir data/raw/options_candles \
        --report-out research_state
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import requests

from src.data.public_export_acquisition import (
    INSTRUMENTS_ENDPOINT,
    TICKERS_ENDPOINT,
    AcquisitionError,
    _as_float,
    _get_json,
    _iso,
    _parse_option_id,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "OPTIONS_CANDLE_BACKFILL_41"
OUT_DIR = Path("research_state")
DATA_RAW_DIR = Path("data/raw")

# Public, read-only OKX candle endpoint. Kept local so the sealed EVAL-26 module
# is not modified by this additive acquisition path.
HISTORY_CANDLES_ENDPOINT = "/api/v5/market/history-candles"

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

DEFAULT_BAR = "5m"
DEFAULT_LIMIT = 100
DEFAULT_REQUEST_DELAY_SECONDS = 0.10
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_RETRIES = 4
DEFAULT_MIN_MONEYNESS = 0.7
DEFAULT_MAX_MONEYNESS = 1.3
DEFAULT_SPREAD_FRACTION = 0.02
MIN_SNAPSHOTS_FOR_SERIES = 12
MIN_SERIES_SPAN_SECONDS = 2 * 60 * 60

_BAR_SECONDS = {"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1H": 3600, "2H": 7200, "4H": 14400}

_SYNTHETIC_MARKERS: Tuple[str, ...] = ("synthetic",)


def _bar_seconds(bar: str) -> int:
    key = str(bar).strip()
    if key not in _BAR_SECONDS:
        raise AcquisitionError(f"unsupported candle bar {bar!r}; expected one of {sorted(_BAR_SECONDS)}")
    return _BAR_SECONDS[key]


def _bar_end(bar_start_ms: int, bar: str) -> datetime:
    """Candle close time. OKX stamps a bar with its *open* time."""
    return datetime.fromtimestamp(int(bar_start_ms) / 1000.0, tz=timezone.utc) + timedelta(
        seconds=_bar_seconds(bar)
    )


def _iso_ms(value: Any) -> Optional[int]:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ensure_not_synthetic(path: Path) -> None:
    if any(marker in path.name.lower() for marker in _SYNTHETIC_MARKERS):
        raise AcquisitionError(f"refusing synthetic-marked output path: {path.name}")


@dataclass
class CandleSnapshot:
    """One reconstructed real cross-section at a single bar end."""

    bar_start_ms: int
    bar_end: str
    quotes: List[Dict[str, Any]]
    n_expiries: int
    n_strikes: int
    n_calls: int
    n_puts: int

    @property
    def n_quotes(self) -> int:
        return len(self.quotes)


@dataclass
class BackfillResult:
    """Measured result of a dense option-candle backfill."""

    report_id: str
    generated_at: str
    trading_mode: str
    live_trading_enabled: bool
    data_provenance: str
    authenticity_verified: bool
    symbol: str
    venue: str
    bar: str
    bar_limit: int
    n_instruments_requested: int
    n_instruments_with_candles: int
    n_snapshots: int
    snapshots: List[CandleSnapshot]
    span_seconds: float
    start_timestamp: str
    end_timestamp: str
    paths: List[str] = field(default_factory=list)
    content_sha256: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


def fetch_live_option_instruments(
    underlying: str,
    *,
    session: Any,
    expiries: Optional[Sequence[str]] = None,
    spot: Optional[float] = None,
    min_moneyness: float = DEFAULT_MIN_MONEYNESS,
    max_moneyness: float = DEFAULT_MAX_MONEYNESS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> List[Dict[str, Any]]:
    """Return live ``underlying`` option instruments inside a moneyness band.

    ``expiries`` filters on the OKX ``YYMMDD`` expiry token (e.g. ``"261127"``).
    ``spot`` is the moneyness centre; when omitted the band is not applied.
    """
    underlying = str(underlying).strip().upper()
    rows = _get_json(
        session,
        INSTRUMENTS_ENDPOINT,
        {"instType": "OPTION", "uly": f"{underlying}-USD"},
        timeout=timeout,
        max_retries=max_retries,
    ).get("data") or []
    if not isinstance(rows, list):
        raise AcquisitionError(f"{underlying}: instruments payload is not a list")

    wanted = {str(e).strip() for e in expiries} if expiries else None
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        inst_id = str(row.get("instId") or "").strip()
        if not inst_id or str(row.get("state") or "").strip().lower() != "live":
            continue
        parsed = _parse_option_id(inst_id)
        if not parsed or parsed["underlying"] != underlying:
            continue
        if wanted is not None and inst_id.split("-")[2] not in wanted:
            continue
        strike = float(parsed["strike"])
        if spot is not None and float(spot) > 0.0:
            moneyness = strike / float(spot)
            if moneyness < float(min_moneyness) or moneyness > float(max_moneyness):
                continue
        out.append(
            {
                "inst_id": inst_id,
                "underlying": underlying,
                "expiry": parsed["expiry"],
                "expiry_token": inst_id.split("-")[2],
                "strike": strike,
                "option_type": parsed["option_type"],
                "contract_size": _as_float(row.get("ctVal")) or 1.0,
            }
        )
    out.sort(key=lambda r: (r["expiry"], r["strike"], r["option_type"]))
    return out


def group_candles_by_bar(
    rows_by_instrument: Mapping[str, Sequence[Sequence[Any]]],
    *,
    bar: str = DEFAULT_BAR,
) -> Dict[int, Dict[str, float]]:
    """Group raw OKX candles into ``{bar_start_ms: {inst_id: close}}``.

    Rows are ``[ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]``. Rows with an
    unparseable timestamp or a non-positive close are dropped; nothing is
    interpolated or forward-filled.
    """
    _bar_seconds(bar)
    out: Dict[int, Dict[str, float]] = {}
    for inst_id, rows in rows_by_instrument.items():
        if not isinstance(rows, (list, tuple)):
            continue
        for candle in rows:
            if isinstance(candle, Mapping):
                values = [candle.get(k) for k in ("ts", "o", "h", "l", "c")]
            elif isinstance(candle, (list, tuple)):
                values = list(candle)
            else:
                continue
            if len(values) < 5:
                continue
            bar_start = _iso_ms(values[0])
            close = _as_float(values[4])
            if bar_start is None or close is None or close <= 0.0:
                continue
            out.setdefault(int(bar_start), {})[str(inst_id)] = float(close)
    return out


def fetch_option_candles(
    instruments: Sequence[Mapping[str, Any]],
    *,
    session: Any,
    bar: str = DEFAULT_BAR,
    limit: int = DEFAULT_LIMIT,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Dict[int, Dict[str, float]]:
    """Fetch candle closes per instrument and group them by bar-start timestamp.

    Returns ``{bar_start_ms: {inst_id: close}}``. Instruments whose candles are
    empty, zero-priced or unparseable are skipped; nothing is interpolated and no
    price is ever fabricated.
    """
    _bar_seconds(bar)
    raw: Dict[str, List[Sequence[Any]]] = {}
    for row in instruments:
        inst_id = str(row.get("inst_id") or "").strip()
        if not inst_id:
            continue
        payload = _get_json(
            session,
            HISTORY_CANDLES_ENDPOINT,
            {"instId": inst_id, "bar": str(bar), "limit": str(max(int(limit), 1))},
            timeout=timeout,
            max_retries=max_retries,
        )
        rows = payload.get("data") or []
        if not isinstance(rows, (list, tuple)):
            continue
        raw[inst_id] = rows
        if request_delay_seconds > 0:
            time.sleep(float(request_delay_seconds))
    return group_candles_by_bar(raw, bar=bar)


def fetch_reference_spreads(
    underlying: str,
    *,
    session: Any,
    default_spread_fraction: float = DEFAULT_SPREAD_FRACTION,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> Tuple[Dict[str, float], str]:
    """Measure each live option's relative bid-ask spread for quote reconstruction.

    Returns ``({inst_id: relative_spread}, source)`` where ``source`` is either
    ``"okx_ticker_measured"`` or ``"constant_fallback"`` when no usable tickers
    were returned. The source is recorded in every artifact so a reconstructed
    quote can never be mistaken for a venue quote.
    """
    rows = _get_json(
        session,
        TICKERS_ENDPOINT,
        {"instType": "OPTION", "uly": f"{str(underlying).strip().upper()}-USD"},
        timeout=timeout,
        max_retries=max_retries,
    ).get("data") or []
    spreads: Dict[str, float] = {}
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, Mapping):
            continue
        inst_id = str(row.get("instId") or "").strip()
        if not inst_id:
            continue
        bid = _as_float(row.get("bidPx"))
        ask = _as_float(row.get("askPx"))
        if bid is None or ask is None or bid <= 0.0 or ask < bid:
            continue
        mid = 0.5 * (bid + ask)
        if mid <= 0.0:
            continue
        fraction = (ask - bid) / mid
        if math.isfinite(fraction) and fraction > 0.0:
            spreads[inst_id] = float(fraction)
    if not spreads:
        return {}, "constant_fallback"
    return spreads, "okx_ticker_measured"


def build_snapshots(
    candles_by_bar: Mapping[int, Mapping[str, float]],
    instruments: Sequence[Mapping[str, Any]],
    *,
    bar: str = DEFAULT_BAR,
    spreads: Optional[Mapping[str, float]] = None,
    default_spread_fraction: float = DEFAULT_SPREAD_FRACTION,
    min_quotes: int = 8,
    min_expiries: int = 2,
    min_strikes_per_expiry: int = 2,
) -> List[CandleSnapshot]:
    """Assemble loader-compatible cross-sections from grouped candle closes.

    A bar is emitted only when it carries at least ``min_quotes`` quotes spanning
    ``min_expiries`` expiries, each with at least ``min_strikes_per_expiry``
    distinct strikes. Sparse bars are skipped and counted by the caller, never
    padded.
    """
    by_id = {str(r.get("inst_id")): r for r in instruments}
    spreads = dict(spreads or {})
    snapshots: List[CandleSnapshot] = []
    for bar_start in sorted(candles_by_bar):
        closes = candles_by_bar[bar_start]
        quotes: List[Dict[str, Any]] = []
        expiries: Dict[datetime, set] = {}
        strikes = 0
        calls = 0
        puts = 0
        for inst_id, close in closes.items():
            row = by_id.get(inst_id)
            if row is None:
                continue
            spread = float(spreads.get(inst_id, default_spread_fraction))
            if not (math.isfinite(spread) and spread > 0.0):
                spread = float(default_spread_fraction)
            half = 0.5 * spread
            bid = float(close) * (1.0 - half)
            ask = float(close) * (1.0 + half)
            if bid <= 0.0:
                continue
            bar_end = _bar_end(bar_start, bar)
            quotes.append(
                {
                    "symbol": inst_id,
                    "underlying": row["underlying"],
                    "strike": float(row["strike"]),
                    "expiry": _iso(row["expiry"]),
                    "option_type": row["option_type"],
                    "venue": "okx",
                    "contract_size": float(row["contract_size"]),
                    "bid": bid,
                    "ask": ask,
                    "last": float(close),
                    "mark": float(close),
                    "bid_iv": None,
                    "ask_iv": None,
                    "mark_iv": None,
                    "delta": None,
                    "gamma": None,
                    "theta": None,
                    "vega": None,
                    "open_interest": 0.0,
                    "volume": 0.0,
                    "timestamp": _iso(bar_end),
                    "price_unit": "btc_per_1btc",
                    "venue_quote_unit": "btc_per_1btc",
                    "price_mode": "candle_close_with_reconstructed_spread",
                    "spread_source": "okx_ticker_measured" if inst_id in spreads else "constant_fallback",
                    "candle_bar_start_ms": int(bar_start),
                    "candle_bar": str(bar),
                }
            )
            expiries.setdefault(row["expiry"], set()).add(float(row["strike"]))
            strikes += 1
            if row["option_type"] == "call":
                calls += 1
            else:
                puts += 1
        per_expiry = {exp: len(v) for exp, v in expiries.items()}
        if len(quotes) < int(min_quotes):
            continue
        if len(per_expiry) < int(min_expiries):
            continue
        if any(count < int(min_strikes_per_expiry) for count in per_expiry.values()):
            continue
        snapshots.append(
            CandleSnapshot(
                bar_start_ms=int(bar_start),
                bar_end=_iso(_bar_end(bar_start, bar)),
                quotes=quotes,
                n_expiries=len(per_expiry),
                n_strikes=len({q["strike"] for q in quotes}),
                n_calls=calls,
                n_puts=puts,
            )
        )
    return snapshots


def write_snapshot_exports(
    snapshots: Sequence[CandleSnapshot],
    *,
    out_dir: Path | str,
    underlying: str = "BTC",
    venue: str = "okx",
    bar: str = DEFAULT_BAR,
) -> List[Path]:
    """Write one loader-compatible ``options_<venue>_<UNDERLYING>_<UTC>.json`` per snapshot."""
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    for snap in snapshots:
        stamp = snap.bar_end.replace("-", "").replace(":", "").split(".")[0]
        stamp = f"{stamp[:8]}T{stamp[9:15]}Z"
        path = root / f"options_{venue}_{underlying.upper()}_{stamp}.json"
        _ensure_not_synthetic(path)
        payload = {
            "schema": "okx_public_options_candle_backfill_v1",
            "underlying": underlying.upper(),
            "venue": venue,
            "quotes": snap.quotes,
            "acquired_at": snap.bar_end,
            "source": {
                "venue": venue,
                "endpoints": [HISTORY_CANDLES_ENDPOINT, TICKERS_ENDPOINT],
                "authenticated": False,
                "public_read_only": True,
                "price_mode": "okx_option_candle_close",
                "candle_bar": str(bar),
                "candle_bar_start_ms": int(snap.bar_start_ms),
                "derived_from": "okx_market_history_candles",
                "note": "bid/ask reconstructed around the measured close; not venue quotes",
            },
        }
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def backfill_dense_option_snapshots(
    *,
    underlying: str = "BTC",
    expiries: Optional[Sequence[str]] = None,
    bar: str = DEFAULT_BAR,
    limit: int = DEFAULT_LIMIT,
    spot: Optional[float] = None,
    min_moneyness: float = DEFAULT_MIN_MONEYNESS,
    max_moneyness: float = DEFAULT_MAX_MONEYNESS,
    out_dir: Path | str = DATA_RAW_DIR,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_retries: int = DEFAULT_MAX_RETRIES,
    session: Any = None,
    timestamp: Optional[str] = None,
) -> BackfillResult:
    """Fetch, reconstruct, write and measure a dense real option snapshot series.

    ``session`` is injectable for offline tests; production uses a fresh
    ``requests.Session``. Raises ``RealDataUnavailable`` semantics via
    ``AcquisitionError`` when no snapshot survives the coverage floors, so an
    empty or degenerate series can never be reported as a measurement.
    """
    from src.campaign.integrated import RealDataUnavailable

    stamp = timestamp or _iso(datetime.now(timezone.utc))
    session = session or requests.Session()
    underlying = str(underlying).strip().upper()
    out = Path(out_dir)

    instruments = fetch_live_option_instruments(
        underlying,
        session=session,
        expiries=expiries,
        spot=spot,
        min_moneyness=min_moneyness,
        max_moneyness=max_moneyness,
        timeout=timeout,
        max_retries=max_retries,
    )
    if not instruments:
        raise RealDataUnavailable(f"no live option instruments for {underlying!r}")

    candles = fetch_option_candles(
        instruments,
        session=session,
        bar=bar,
        limit=limit,
        request_delay_seconds=request_delay_seconds,
        timeout=timeout,
        max_retries=max_retries,
    )
    if not candles:
        raise RealDataUnavailable(f"no option candles for {underlying!r} bar={bar!r}")

    spreads, spread_source = fetch_reference_spreads(
        underlying, session=session, timeout=timeout, max_retries=max_retries
    )
    snapshots = build_snapshots(
        candles,
        instruments,
        bar=bar,
        spreads=spreads,
        default_spread_fraction=DEFAULT_SPREAD_FRACTION,
    )
    if not snapshots:
        raise RealDataUnavailable(
            f"no snapshot met the coverage floors for {underlying!r} bar={bar!r}"
        )

    paths = write_snapshot_exports(
        snapshots, out_dir=out, underlying=underlying, bar=bar
    )

    start_ms = min(s.bar_start_ms for s in snapshots)
    end_ms = max(s.bar_start_ms for s in snapshots)
    span_seconds = float((_bar_end(end_ms, bar) - _bar_end(start_ms, bar)).total_seconds())
    warnings: List[str] = []
    if len(snapshots) < MIN_SNAPSHOTS_FOR_SERIES:
        warnings.append(
            f"only {len(snapshots)} snapshot(s) reconstructed (< {MIN_SNAPSHOTS_FOR_SERIES})"
        )
    if span_seconds < MIN_SERIES_SPAN_SECONDS:
        warnings.append(
            f"span {span_seconds:.0f}s < {MIN_SERIES_SPAN_SECONDS}s"
        )
    if spread_source != "okx_ticker_measured":
        warnings.append(
            "live tickers unavailable; reconstructed spreads use the constant fallback "
            f"({DEFAULT_SPREAD_FRACTION})"
        )

    return BackfillResult(
        report_id=REPORT_ID,
        generated_at=stamp,
        trading_mode=TRADING_MODE,
        live_trading_enabled=LIVE_TRADING_ENABLED,
        data_provenance="real_public_exchange_export_derived_from_candles",
        authenticity_verified=False,
        symbol=underlying,
        venue="okx",
        bar=str(bar),
        bar_limit=int(limit),
        n_instruments_requested=int(len(instruments)),
        n_instruments_with_candles=int(len({i for c in candles.values() for i in c})),
        n_snapshots=int(len(snapshots)),
        snapshots=snapshots,
        span_seconds=span_seconds,
        start_timestamp=_iso(_bar_end(start_ms, bar)),
        end_timestamp=_iso(_bar_end(end_ms, bar)),
        paths=[str(p) for p in paths],
        content_sha256={str(p): _sha256(p) for p in paths},
        warnings=warnings,
    )


def _result_to_dict(result: BackfillResult) -> Dict[str, Any]:
    return {
        "report_id": result.report_id,
        "generated_at": result.generated_at,
        "trading_mode": result.trading_mode,
        "live_trading_enabled": result.live_trading_enabled,
        "never_valid_true": True,
        "data_provenance": result.data_provenance,
        "authenticity_verified": result.authenticity_verified,
        "symbol": result.symbol,
        "venue": result.venue,
        "bar": result.bar,
        "bar_limit": result.bar_limit,
        "n_instruments_requested": result.n_instruments_requested,
        "n_instruments_with_candles": result.n_instruments_with_candles,
        "n_snapshots": result.n_snapshots,
        "span_seconds": result.span_seconds,
        "start_timestamp": result.start_timestamp,
        "end_timestamp": result.end_timestamp,
        "snapshots": [
            {
                "bar_start_ms": s.bar_start_ms,
                "bar_end": s.bar_end,
                "n_quotes": s.n_quotes,
                "n_expiries": s.n_expiries,
                "n_strikes": s.n_strikes,
                "n_calls": s.n_calls,
                "n_puts": s.n_puts,
            }
            for s in result.snapshots
        ],
        "paths": list(result.paths),
        "content_sha256": dict(result.content_sha256),
        "warnings": list(result.warnings),
    }


def write_backfill_report(result: BackfillResult, out_dir: Path | str = OUT_DIR) -> Dict[str, str]:
    """Write the strict JSON + MD artifact for a dense candle backfill."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = result.generated_at.replace("-", "").replace(":", "").split(".")[0]
    stamp = f"{stamp[:8]}T{stamp[9:15]}Z"
    json_path = out / f"{REPORT_ID}_{stamp}.json"
    md_path = out / f"{REPORT_ID}_{stamp}.md"

    payload = _result_to_dict(result)
    payload["artifact_paths"] = {"json": str(json_path), "md": str(md_path)}
    serialized = serialize_metrics_strict(payload)
    assert_json_valid(serialized)
    json_path.write_text(
        json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# {REPORT_ID} — dense real options snapshot series from OKX option candles",
        "",
        f"- generated_at: {result.generated_at}",
        f"- trading_mode: {result.trading_mode} (live_trading_enabled={str(result.live_trading_enabled).lower()})",
        f"- data_provenance: {result.data_provenance} (authenticity_verified={str(result.authenticity_verified).lower()})",
        f"- never_valid_true: True",
        f"- symbol: {result.symbol}  venue: {result.venue}  bar: {result.bar}",
        f"- instruments requested: {result.n_instruments_requested}; with candles: {result.n_instruments_with_candles}",
        f"- snapshots: {result.n_snapshots}",
        f"- span: {result.span_seconds:.0f}s ({result.start_timestamp} → {result.end_timestamp})",
        f"- min_snapshots_for_series: {MIN_SNAPSHOTS_FOR_SERIES}; min_span_seconds: {MIN_SERIES_SPAN_SECONDS}",
        "",
        "## Snapshots",
        "",
    ]
    for snap in result.snapshots:
        lines.append(
            f"- {snap.bar_end}: {snap.n_quotes} quotes, {snap.n_expiries} expiries, "
            f"{snap.n_strikes} strikes ({snap.n_calls} calls / {snap.n_puts} puts)"
        )
    lines.extend(["", "## Provenance", ""])
    lines.append(
        "Prices are OKX option **candle closes** (public read-only "
        "`/api/v5/market/history-candles`). Each snapshot is stamped at the candle's "
        "bar **end**, so it carries no information from the bar it is aligned to. "
        "bid/ask are reconstructed around the measured close with the instrument's "
        "measured live relative spread (fallback: constant, recorded). These are "
        "reconstructed quotes, not venue quotes; `authenticity_verified` stays false."
    )
    if result.warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in result.warnings:
            lines.append(f"- {warning}")
    lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct a dense real option snapshot series from OKX option candles."
    )
    parser.add_argument("--underlying", default="BTC")
    parser.add_argument(
        "--expiries",
        default=None,
        help="comma-separated OKX expiry tokens, e.g. 261120,261127,261204",
    )
    parser.add_argument("--bar", default=DEFAULT_BAR, help="candle bar size, e.g. 5m")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="candles per instrument")
    parser.add_argument("--spot", type=float, default=None, help="moneyness centre (default: no band)")
    parser.add_argument("--min-moneyness", type=float, default=DEFAULT_MIN_MONEYNESS)
    parser.add_argument("--max-moneyness", type=float, default=DEFAULT_MAX_MONEYNESS)
    parser.add_argument("--out", default=str(DATA_RAW_DIR), help="snapshot export dir")
    parser.add_argument("--report-out", default=str(OUT_DIR), help="artifact dir")
    parser.add_argument("--request-delay-seconds", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--timestamp", default=None)
    args = parser.parse_args(argv)

    expiries = [e.strip() for e in args.expiries.split(",") if e.strip()] if args.expiries else None
    result = backfill_dense_option_snapshots(
        underlying=args.underlying,
        expiries=expiries,
        bar=args.bar,
        limit=args.limit,
        spot=args.spot,
        min_moneyness=args.min_moneyness,
        max_moneyness=args.max_moneyness,
        out_dir=Path(args.out),
        request_delay_seconds=args.request_delay_seconds,
        timeout=args.timeout,
        max_retries=args.max_retries,
        timestamp=args.timestamp,
    )
    artifact_paths = write_backfill_report(result, Path(args.report_out))
    print(
        json.dumps(
            {
                "report_id": result.report_id,
                "n_snapshots": result.n_snapshots,
                "span_seconds": result.span_seconds,
                "start_timestamp": result.start_timestamp,
                "end_timestamp": result.end_timestamp,
                "warnings": result.warnings,
                "artifact_paths": artifact_paths,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())