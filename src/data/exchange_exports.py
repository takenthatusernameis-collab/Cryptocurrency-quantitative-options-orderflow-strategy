"""Deterministic offline adapters for exchange trade-export formats (EVAL-23B).

The only blocker on a trustworthy net-of-cost verdict is an adequate real tape.
EVAL-23B removes the acquisition-format blocker without touching the network:
it parses common OKX, Binance and Deribit trade-export CSV/JSON documents into
the sealed :class:`~src.data.schemas.OrderflowSnapshot` representation, writes a
loader-compatible normalized tape, and seals an explicit readiness artifact.

The adapter is paper-only, deterministic and offline. It never substitutes
synthetic data, never claims provenance it cannot verify, and never emits
``{"valid": true}``. A parsed export is recorded as ``exchange_export`` with
``authenticity_verified=false``; only the sealed EVAL-22 gate may decide whether
a tape is a real tape.

CLI::

    python -m src.data.exchange_exports --in <file> --venue okx --symbol BTC-USDT \
        --out research_state/ [--data-dir data/raw]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from src.data.normalization import normalize_symbol
from src.data.schemas import OrderflowSnapshot, Trade
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "EXCHANGE_EXPORT_ADAPTERS_23B"
OUT_DIR = Path("research_state")
DATA_RAW_DIR = Path("data/raw")

SUPPORTED_VENUES: Tuple[str, ...] = ("okx", "binance", "deribit")
SUPPORTED_FORMATS: Tuple[str, ...] = ("csv", "json")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

DEFAULT_BAR_DURATION_SECONDS = 15.0
DEFAULT_TRAIN_WINDOW = 500
DEFAULT_TEST_WINDOW = 100
DEFAULT_STEP_SIZE = 50
DEFAULT_MIN_RETURNS = 1000
DEFAULT_MIN_WINDOWS = 20

_SYNTHETIC_MARKERS: Tuple[str, ...] = ("synthetic",)

_FIELD_ALIASES: Dict[str, Tuple[str, ...]] = {
    "trade_id": ("tradeid", "id", "tid", "tradenum", "tradeidentifier"),
    "timestamp": (
        "timestamp",
        "time",
        "ts",
        "date",
        "datetime",
        "tradetime",
        "transacttime",
        "eventtime",
    ),
    "price": ("price", "px", "tradeprice", "fillprice", "executionprice"),
    "size": (
        "size",
        "sz",
        "qty",
        "quantity",
        "amount",
        "volume",
        "filledqty",
        "contracts",
        "sizeusdt",
    ),
    "side": (
        "side",
        "takertype",
        "takerside",
        "direction",
        "aggressor",
        "takerbuyer",
        "takerbuyside",
    ),
    "symbol": (
        "symbol",
        "instid",
        "instrument",
        "instrumentname",
        "pair",
        "market",
        "contract",
    ),
    "is_buyer_maker": ("isbuyermaker", "buyermaker", "ismakerbuy", "buyorempty"),
}

_VENUE_COLUMN_ORDER: Dict[str, Tuple[str, ...]] = {
    "okx": ("tradeid", "instid", "price", "size", "side", "timestamp"),
    "binance": (
        "id",
        "price",
        "qty",
        "quoteqty",
        "time",
        "isbuyermaker",
        "isbestmatch",
    ),
    "deribit": (
        "tradeid",
        "timestamp",
        "instrumentname",
        "price",
        "amount",
        "direction",
    ),
}

_VENUE_FORMATS: Dict[str, Dict[str, Any]] = {
    "okx": {
        "csv_headers": ["tradeId", "instId", "px", "sz", "side", "ts"],
        "json_shape": "list | {data: [...]} | {trades: [...]}",
        "timestamp_forms": ["ISO-8601", "epoch-ms"],
        "side_forms": ["buy", "sell"],
    },
    "binance": {
        "csv_headers": ["Id", "Price", "Qty", "QuoteQty", "Time", "IsBuyerMaker"],
        "json_shape": "list | {trades: [...]} | {data: [...]}",
        "timestamp_forms": ["ISO-8601", "epoch-ms"],
        "side_forms": ["isBuyerMaker=true -> sell", "isBuyerMaker=false -> buy"],
    },
    "deribit": {
        "csv_headers": [
            "trade_id",
            "timestamp",
            "instrument_name",
            "price",
            "amount",
            "direction",
        ],
        "json_shape": "list | {result: [...]} | {trades: [...]}",
        "timestamp_forms": ["epoch-ms", "ISO-8601"],
        "side_forms": ["buy", "sell"],
    },
}


class ExchangeExportRejected(ValueError):
    """An export document failed format, schema or microstructure validation."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    ts = (
        iso_ts.replace(":", "")
        .replace("-", "")
        .replace("T", "")
        .replace("Z", "")
        .split(".")[0]
    )
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ""


def _normalize_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _normalized_record(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {_normalize_key(k): v for k, v in record.items()}


def _first_present(
    record: Mapping[str, Any], aliases: Sequence[str]
) -> Tuple[Optional[str], Any]:
    for alias in aliases:
        key = _normalize_key(alias)
        if key in record:
            value = record[key]
            if value is not None and str(value).strip() != "":
                return key, value
    return None, None


def _parse_epoch(value: float) -> datetime:
    magnitude = abs(float(value))
    if magnitude >= 1e17:
        seconds = float(value) / 1e9
    elif magnitude >= 1e14:
        seconds = float(value) / 1e6
    elif magnitude >= 1e11:
        seconds = float(value) / 1e3
    else:
        seconds = float(value)
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def _parse_ts(value: Any) -> datetime:
    try:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, bool):
            raise ExchangeExportRejected(f"boolean timestamp: {value!r}")
        elif isinstance(value, (int, float)):
            parsed = _parse_epoch(float(value))
        elif isinstance(value, str) and value.strip():
            text = value.strip()
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                try:
                    parsed = _parse_epoch(float(text))
                except (TypeError, ValueError, OverflowError, OSError):
                    raise ExchangeExportRejected(
                        f"unparseable timestamp: {value!r}"
                    ) from None
        else:
            raise ExchangeExportRejected(f"unparseable timestamp: {value!r}")
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(timezone.utc)
        if not math.isfinite(parsed.timestamp()):
            raise ExchangeExportRejected(f"non-finite timestamp: {value!r}")
        return parsed
    except ExchangeExportRejected:
        raise
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        raise ExchangeExportRejected(f"unparseable timestamp: {value!r}") from exc


def _parse_number(value: Any, field: str, *, positive: bool = True) -> float:
    if isinstance(value, bool):
        raise ExchangeExportRejected(f"{field} is boolean: {value!r}")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ExchangeExportRejected(f"non-numeric {field}: {value!r}") from None
    if not math.isfinite(number):
        raise ExchangeExportRejected(f"non-finite {field}: {value!r}")
    if positive and number <= 0.0:
        raise ExchangeExportRejected(f"non-positive {field}: {number!r}")
    return number


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if int(value) == 1:
            return True
        if int(value) == 0:
            return False
    text = str(value).strip().lower()
    if text in ("true", "t", "yes", "y", "1"):
        return True
    if text in ("false", "f", "no", "n", "0"):
        return False
    raise ExchangeExportRejected(f"non-boolean flag: {value!r}")


def _parse_side(record: Mapping[str, Any]) -> str:
    side_key, side_value = _first_present(record, _FIELD_ALIASES["side"])
    if side_key is not None:
        text = str(side_value).strip().lower()
        if text in ("buy", "b", "bid", "long"):
            return "buy"
        if text in ("sell", "s", "ask", "offer", "short"):
            return "sell"
        if side_key in ("takerbuyer", "takerbuyside"):
            return "buy" if _parse_bool(side_value) else "sell"
        raise ExchangeExportRejected(f"invalid side: {side_value!r}")

    maker_key, maker_value = _first_present(record, _FIELD_ALIASES["is_buyer_maker"])
    if maker_key is not None:
        return "sell" if _parse_bool(maker_value) else "buy"

    raise ExchangeExportRejected("missing side")


def _source_symbol(record: Mapping[str, Any]) -> str:
    _, value = _first_present(record, _FIELD_ALIASES["symbol"])
    if value is None:
        return ""
    return normalize_symbol(str(value), "")


def _detect_format(path: Path, format_hint: Optional[str]) -> str:
    if format_hint is not None:
        hint = str(format_hint).strip().lower()
        if hint not in SUPPORTED_FORMATS:
            raise ExchangeExportRejected(
                f"unsupported format hint {format_hint!r}; expected {SUPPORTED_FORMATS}"
            )
        return hint
    suffix = path.suffix.lower()
    if suffix in (".csv", ".tsv", ".txt"):
        return "csv"
    if suffix == ".json":
        return "json"
    try:
        head = path.read_text(encoding="utf-8", errors="strict")[:4096].lstrip()
    except (OSError, UnicodeError) as exc:
        raise ExchangeExportRejected(f"unreadable export: {exc}") from None
    if head.startswith("[") or head.startswith("{"):
        return "json"
    return "csv"


def _read_json_records(path: Path) -> List[Mapping[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExchangeExportRejected(f"unreadable JSON export: {exc}") from None

    items: Any = raw
    if isinstance(raw, dict):
        for key in ("trades", "data", "result", "results", "items"):
            if isinstance(raw.get(key), list):
                items = raw[key]
                break
        else:
            raise ExchangeExportRejected("JSON export has no trades/data/result list")
    if not isinstance(items, list):
        raise ExchangeExportRejected(
            f"JSON export trades must be a list, got {type(items).__name__}"
        )
    if not items:
        raise ExchangeExportRejected("empty JSON export")
    if not all(isinstance(item, Mapping) for item in items):
        raise ExchangeExportRejected("every JSON trade must be an object")
    return list(items)


def _read_csv_records(path: Path, venue: str) -> List[Mapping[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise ExchangeExportRejected(f"unreadable CSV export: {exc}") from None
    if not text.strip():
        raise ExchangeExportRejected("empty CSV export")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise ExchangeExportRejected("CSV export has no data rows")

    if reader.fieldnames is None:
        raise ExchangeExportRejected("CSV export has no header row")

    header_keys = {_normalize_key(name) for name in reader.fieldnames}
    has_known_header = any(
        _normalize_key(alias) in header_keys
        for aliases in _FIELD_ALIASES.values()
        for alias in aliases
    )
    if has_known_header:
        return [dict(row) for row in rows]

    positional = _VENUE_COLUMN_ORDER.get(venue)
    if not positional:
        raise ExchangeExportRejected(f"headerless CSV unsupported for venue {venue!r}")
    positional_rows: List[Mapping[str, Any]] = []
    for raw_row in csv.reader(io.StringIO(text)):
        if not raw_row:
            continue
        positional_rows.append(dict(zip(positional, raw_row)))
    if not positional_rows:
        raise ExchangeExportRejected("headerless CSV export has no data rows")
    return positional_rows


def _read_records(path: Path, venue: str, format_hint: Optional[str]) -> List[Mapping[str, Any]]:
    fmt = _detect_format(path, format_hint)
    if fmt == "json":
        return _read_json_records(path)
    return _read_csv_records(path, venue)


def _normalize_records(
    records: Sequence[Mapping[str, Any]], venue: str, symbol: str
) -> Tuple[List[Dict[str, Any]], str]:
    normalized: List[Dict[str, Any]] = []
    for index, raw in enumerate(records):
        record = _normalized_record(raw)

        _, trade_id_value = _first_present(record, _FIELD_ALIASES["trade_id"])
        trade_id = (
            str(trade_id_value).strip() if trade_id_value is not None else None
        )

        _, timestamp_value = _first_present(record, _FIELD_ALIASES["timestamp"])
        timestamp = _parse_ts(timestamp_value)

        _, price_value = _first_present(record, _FIELD_ALIASES["price"])
        price = _parse_number(price_value, "price", positive=True)

        _, size_value = _first_present(record, _FIELD_ALIASES["size"])
        size = _parse_number(size_value, "size", positive=True)

        side = _parse_side(record)

        normalized.append(
            {
                "trade_id": trade_id,
                "timestamp": timestamp,
                "price": price,
                "size": size,
                "side": side,
                "source_symbol": _source_symbol(record),
                "source_row": index,
            }
        )

    if not normalized:
        raise ExchangeExportRejected("empty export")

    missing = [record for record in normalized if record["trade_id"] is None]
    if missing:
        ordered = sorted(
            missing,
            key=lambda r: (
                r["timestamp"],
                r["price"],
                r["size"],
                r["side"],
                r["source_row"],
            ),
        )
        for sequence, record in enumerate(ordered):
            record["trade_id"] = f"auto-{sequence:08d}"

    seen: Dict[str, int] = {}
    for record in normalized:
        trade_id = record["trade_id"]
        if trade_id in seen:
            raise ExchangeExportRejected(f"duplicate trade_id: {trade_id!r}")
        seen[trade_id] = 1

    normalized.sort(
        key=lambda r: (
            r["timestamp"],
            r["trade_id"],
            r["price"],
            r["size"],
            r["side"],
        )
    )

    requested = normalize_symbol(symbol, venue)
    if not requested:
        requested = next(
            (r["source_symbol"] for r in normalized if r["source_symbol"]), ""
        )
    if not requested:
        raise ExchangeExportRejected("empty symbol")

    return [
        {
            "trade_id": r["trade_id"],
            "timestamp": r["timestamp"],
            "price": r["price"],
            "size": r["size"],
            "side": r["side"],
            "source_symbol": r["source_symbol"],
        }
        for r in normalized
    ], requested


def _build_snapshot(
    normalized: Sequence[Mapping[str, Any]], venue: str, symbol: str
) -> OrderflowSnapshot:
    trades: List[Trade] = []
    previous: Optional[datetime] = None
    for record in normalized:
        timestamp = _parse_ts(record["timestamp"])
        if previous is not None and timestamp < previous:
            raise ExchangeExportRejected(
                "trade timestamps are not monotone non-decreasing after canonical sort"
            )
        previous = timestamp
        trades.append(
            Trade(
                trade_id=str(record["trade_id"]),
                symbol=symbol,
                venue=venue,
                price=float(record["price"]),
                size=float(record["size"]),
                side=str(record["side"]),
                timestamp=timestamp,
            )
        )
    if not trades:
        raise ExchangeExportRejected("empty export")
    return OrderflowSnapshot(
        symbol=symbol,
        venue=venue,
        trades=trades,
        liquidations=[],
        funding_rates=[],
        timestamp=max(trade.timestamp for trade in trades),
    )


def _parse_export(
    path: Path,
    venue: str,
    symbol: str,
    format_hint: Optional[str] = None,
) -> Tuple[OrderflowSnapshot, Dict[str, Any]]:
    path = Path(path)
    venue_key = str(venue).strip().lower()
    if venue_key not in SUPPORTED_VENUES:
        raise ExchangeExportRejected(
            f"unsupported venue {venue!r}; expected {SUPPORTED_VENUES}"
        )
    if any(marker in path.name.lower() for marker in _SYNTHETIC_MARKERS):
        raise ExchangeExportRejected(
            f"synthetic filename is not an exchange export: {path.name}"
        )
    if not path.is_file():
        raise ExchangeExportRejected(f"export file not found: {path}")

    fmt = _detect_format(path, format_hint)
    records = _read_records(path, venue_key, format_hint)
    normalized, requested_symbol = _normalize_records(records, venue_key, symbol)
    snapshot = _build_snapshot(normalized, venue_key, requested_symbol)

    metadata = {
        "format": fmt,
        "requested_venue": venue_key,
        "requested_symbol": normalize_symbol(symbol, venue_key),
        "normalized_symbol": snapshot.symbol,
        "n_records": len(records),
        "n_trades": len(snapshot.trades),
        "source_symbols": sorted(
            {
                str(record["source_symbol"])
                for record in normalized
                if record["source_symbol"]
            }
        ),
        "auto_trade_ids": sum(
            1 for record in normalized if str(record["trade_id"]).startswith("auto-")
        ),
    }
    return snapshot, metadata


def parse_exchange_export(
    path: str | Path,
    venue: str,
    symbol: str,
    format_hint: Optional[str] = None,
) -> OrderflowSnapshot:
    """Parse one exchange trade export into a canonical orderflow snapshot."""
    snapshot, _ = _parse_export(Path(path), venue, symbol, format_hint)
    return snapshot


def _canonical_fingerprint(snapshot: OrderflowSnapshot) -> str:
    parts = [
        f"{t.timestamp.isoformat()}|{t.price:.10f}|{t.size:.10f}|{t.side}"
        for t in snapshot.trades
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _content_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def write_normalized_orderflow_tape(
    snapshot: OrderflowSnapshot, out_path: str | Path
) -> Path:
    """Write a loader-compatible normalized orderflow JSON tape."""
    target = Path(out_path)
    if target.exists() and target.is_dir():
        stamp = _stamp_for_filename(_utc_now_iso())
        target = target / (
            f"orderflow_{snapshot.venue}_{snapshot.symbol}_{stamp}.json"
        )
    elif target.suffix.lower() not in (".json",):
        target = target / (
            f"orderflow_{snapshot.venue}_{snapshot.symbol}_"
            f"{_stamp_for_filename(_utc_now_iso())}.json"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "symbol": snapshot.symbol,
        "venue": snapshot.venue,
        "timestamp": _iso(snapshot.timestamp),
        "trades": [
            {
                "trade_id": trade.trade_id,
                "symbol": trade.symbol,
                "venue": trade.venue,
                "price": trade.price,
                "size": trade.size,
                "side": trade.side,
                "timestamp": _iso(trade.timestamp),
            }
            for trade in snapshot.trades
        ],
        "liquidations": [],
        "funding_rates": [],
    }
    assert_json_valid(payload)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return target


def _window_count(
    n_bars: int, train_window: int, test_window: int, step_size: int
) -> int:
    train = min(int(train_window), max(int(n_bars) - 1, 1))
    test = max(int(test_window), 1)
    step = max(int(step_size), 1)
    if int(n_bars) <= train:
        return 0
    return max(0, (int(n_bars) - train - test) // step + 1)


def _adequacy_counts(
    snapshot: OrderflowSnapshot,
    bar_duration_seconds: float,
    train_window: int,
    test_window: int,
    step_size: int,
    min_returns: int,
    min_windows: int,
) -> Dict[str, Any]:
    from src.analytics.integrated_options_orderflow_evaluation import _build_bars

    bars = _build_bars(snapshot, bar_duration_seconds=bar_duration_seconds)
    n_bars = int(bars["n_bars"])
    n_returns = max(0, n_bars - 1)
    n_windows = _window_count(n_bars, train_window, test_window, step_size)
    return {
        "n_bars": n_bars,
        "n_returns": int(n_returns),
        "n_windows": int(n_windows),
        "min_returns": int(min_returns),
        "min_windows": int(min_windows),
        "bar_duration_seconds": float(bar_duration_seconds),
        "train_window": int(train_window),
        "test_window": int(test_window),
        "step_size": int(step_size),
        "sample_adequate": bool(n_returns >= int(min_returns) and n_windows >= int(min_windows)),
        "shortfall_returns": max(0, int(min_returns) - n_returns),
        "shortfall_windows": max(0, int(min_windows) - n_windows),
    }


def _supported_formats() -> List[Dict[str, Any]]:
    return [
        {"venue": venue, **_VENUE_FORMATS[venue]}
        for venue in SUPPORTED_VENUES
    ]


def evaluate_exchange_export(
    path: str | Path,
    venue: str,
    symbol: str,
    *,
    format_hint: Optional[str] = None,
    write: bool = True,
    out_dir: Path = OUT_DIR,
    normalized_out: Optional[Path] = None,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    min_returns: int = DEFAULT_MIN_RETURNS,
    min_windows: int = DEFAULT_MIN_WINDOWS,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate one exchange export and return a sealed readiness report."""
    stamp = timestamp or _utc_now_iso()
    source = Path(path)
    base: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "data_provenance": "exchange_export",
        "authenticity_verified": False,
        "source_path": str(source),
        "venue": str(venue).strip().lower(),
        "requested_symbol": normalize_symbol(symbol, str(venue).strip().lower()),
        "format": None,
        "adapter_verdict": "FAIL",
        "adequacy": None,
        "n_trades": 0,
        "span_seconds": None,
        "start_timestamp": None,
        "end_timestamp": None,
        "content_sha256": None,
        "canonical_fingerprint": None,
        "normalized_tape_path": None,
        "normalized_tape_sha256": None,
        "microstructure_sane": False,
        "canonical_order": False,
        "loader_compatible": False,
        "supported_formats": _supported_formats(),
        "overall_verdict": "NO-GO",
        "overall_reason": "adapter failed",
        "floors": {
            "min_returns": int(min_returns),
            "min_windows": int(min_windows),
            "bar_duration_seconds": float(bar_duration_seconds),
        },
    }

    try:
        snapshot, metadata = _parse_export(source, venue, symbol, format_hint)
    except ExchangeExportRejected as exc:
        base["overall_reason"] = f"adapter rejected export: {exc}"
        return _finalize_report(base, write=write, out_dir=out_dir, stamp=stamp)

    span = (
        max(trade.timestamp for trade in snapshot.trades)
        - min(trade.timestamp for trade in snapshot.trades)
    ).total_seconds()
    adequacy = _adequacy_counts(
        snapshot,
        bar_duration_seconds,
        train_window,
        test_window,
        step_size,
        min_returns,
        min_windows,
    )
    base.update(
        {
            "format": metadata["format"],
            "normalized_symbol": snapshot.symbol,
            "n_records": metadata["n_records"],
            "n_trades": metadata["n_trades"],
            "auto_trade_ids": metadata["auto_trade_ids"],
            "source_symbols": metadata["source_symbols"],
            "span_seconds": float(span),
            "start_timestamp": _iso(min(trade.timestamp for trade in snapshot.trades)),
            "end_timestamp": _iso(max(trade.timestamp for trade in snapshot.trades)),
            "content_sha256": _content_sha256(source),
            "canonical_fingerprint": _canonical_fingerprint(snapshot),
            "microstructure_sane": True,
            "canonical_order": True,
            "loader_compatible": True,
            "adequacy": adequacy,
            "adapter_verdict": "PASS",
        }
    )

    adapter_failed = base["adapter_verdict"] != "PASS"
    if normalized_out is not None:
        try:
            normalized_path = write_normalized_orderflow_tape(
                snapshot, Path(normalized_out)
            )
            base["normalized_tape_path"] = str(normalized_path)
            base["normalized_tape_sha256"] = hashlib.sha256(
                normalized_path.read_bytes()
            ).hexdigest()
        except (OSError, ValueError) as exc:
            base["adapter_verdict"] = "FAIL"
            base["loader_compatible"] = False
            base["overall_reason"] = f"normalized tape write failed: {exc}"
            adapter_failed = True

    if adequacy["sample_adequate"] and not adapter_failed:
        base["overall_verdict"] = "GO"
        base["overall_reason"] = (
            "adapter parsed export and tape clears EVAL-23 adequacy floors"
        )
    elif not adapter_failed:
        base["overall_reason"] = (
            "adapter parsed export but tape is below EVAL-23 adequacy floors "
            f"(returns {adequacy['n_returns']}/{adequacy['min_returns']}, "
            f"windows {adequacy['n_windows']}/{adequacy['min_windows']})"
        )

    return _finalize_report(base, write=write, out_dir=out_dir, stamp=stamp)


def _finalize_report(
    report: Dict[str, Any], *, write: bool, out_dir: Path, stamp: str
) -> Dict[str, Any]:
    serialized = serialize_metrics_strict(report)
    assert_json_valid(serialized)

    artifact_paths: Dict[str, str] = {}
    if write:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        filename_stamp = _stamp_for_filename(stamp)
        json_path = out / f"EXCHANGE_EXPORT_ADAPTERS_{filename_stamp}.json"
        md_path = out / f"EXCHANGE_EXPORT_ADAPTERS_{filename_stamp}.md"
        artifact_paths = {"json": str(json_path), "md": str(md_path)}
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    result = dict(serialized)
    result["artifact_paths"] = artifact_paths
    return result


def _write_markdown(report: Dict[str, Any]) -> str:
    adequacy = report.get("adequacy") or {}
    lines = [
        f"# {report['report_id']} — EXCHANGE EXPORT ADAPTERS (EVAL-23B)",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- overall_verdict: **{report['overall_verdict']}**",
        f"- reason: {report['overall_reason']}",
        f"- adapter_verdict: {report['adapter_verdict']}",
        f"- trading_mode: {report['trading_mode']}",
        f"- data_provenance: {report['data_provenance']} "
        f"(authenticity_verified={str(report['authenticity_verified']).lower()})",
        f"- source_path: `{report['source_path']}`",
        f"- venue/symbol: `{report['venue']}` / `{report['requested_symbol']}`",
        f"- format: {report['format']}",
        f"- n_trades: {report['n_trades']}",
        f"- span_seconds: {report['span_seconds']}",
        f"- start/end: {report['start_timestamp']} → {report['end_timestamp']}",
        f"- canonical_fingerprint: `{report['canonical_fingerprint']}`",
        f"- normalized_tape: {report['normalized_tape_path']}",
        f"- floors: {report['floors']}",
    ]
    if adequacy:
        lines.append(
            "- adequacy: "
            f"{adequacy['n_returns']}/{adequacy['min_returns']} returns, "
            f"{adequacy['n_windows']}/{adequacy['min_windows']} windows, "
            f"adequate={str(adequacy['sample_adequate']).lower()}"
        )
    lines.extend(
        [
            "",
            "## Supported export formats",
            "",
            "| venue | csv headers | json shape | timestamps | sides |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["supported_formats"]:
        lines.append(
            f"| {item['venue']} | `{', '.join(item['csv_headers'])}` | "
            f"`{item['json_shape']}` | {', '.join(item['timestamp_forms'])} | "
            f"{', '.join(item['side_forms'])} |"
        )
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "Offline deterministic adapter; no network, no `.env`, no live "
            "trading. A parsed export is not proof of real provenance; EVAL-22 "
            "must validate the normalized tape before EVAL-23 uses it.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exchange trade-export adapters (EVAL-23B, paper-only)"
    )
    parser.add_argument("--in", dest="in_path", required=True, help="export file")
    parser.add_argument(
        "--venue", required=True, choices=SUPPORTED_VENUES, help="export venue"
    )
    parser.add_argument("--symbol", default="", help="normalized symbol, e.g. BTC-USDT")
    parser.add_argument(
        "--format", dest="format_hint", choices=SUPPORTED_FORMATS, default=None
    )
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="artifact dir")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="optional directory for the normalized loader-compatible tape",
    )
    parser.add_argument("--no-write", action="store_true", help="do not write artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument(
        "--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS
    )
    parser.add_argument("--min-returns", type=int, default=DEFAULT_MIN_RETURNS)
    parser.add_argument("--min-windows", type=int, default=DEFAULT_MIN_WINDOWS)
    args = parser.parse_args(argv)

    normalized_out = Path(args.data_dir) if args.data_dir else None
    report = evaluate_exchange_export(
        args.in_path,
        args.venue,
        args.symbol,
        format_hint=args.format_hint,
        write=not args.no_write,
        out_dir=Path(args.out),
        normalized_out=normalized_out,
        bar_duration_seconds=args.bar_duration_seconds,
        min_returns=args.min_returns,
        min_windows=args.min_windows,
        timestamp=args.timestamp,
    )
    print(
        json.dumps(
            {
                "overall_verdict": report["overall_verdict"],
                "adapter_verdict": report["adapter_verdict"],
                "n_trades": report["n_trades"],
                "normalized_tape_path": report["normalized_tape_path"],
                "artifact_paths": report["artifact_paths"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())