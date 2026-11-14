"""Deterministic offline adapters for exchange option-export formats (EVAL-24A).

EVAL-23B removed the trade-tape acquisition blocker; EVAL-24A removes the
option-chain acquisition blocker in the same spirit. It parses common OKX,
Binance and Deribit option trade/quote export CSV/JSON documents into the sealed
:class:`~src.data.schemas.OptionContract` / :class:`~src.data.schemas.OptionQuote`
/ :class:`~src.data.schemas.OptionsChain` representation, writes a
loader-compatible normalized options-chain tape, and seals an explicit readiness
artifact.

The adapter is paper-only, deterministic and offline. It never substitutes
synthetic data, never claims provenance it cannot verify, and never emits
``{"valid": true}``. A parsed export is recorded as ``exchange_export`` with
``authenticity_verified=false``; only a sealed downstream gate may decide whether
a chain is a real, adequate chain.

CLI::

    python -m src.data.options_exports --in <file> --venue deribit \
        --underlying BTC --out research_state/ [--data-dir data/examples/normalized]
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
from src.data.schemas import OptionsChain, OptionContract, OptionQuote
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "OPTIONS_EXPORT_ADAPTERS_24A"
OUT_DIR = Path("research_state")

SUPPORTED_VENUES: Tuple[str, ...] = ("okx", "binance", "deribit")
SUPPORTED_FORMATS: Tuple[str, ...] = ("csv", "json")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# Readiness floors for an *adequate* option chain (contracts/quotes cross-section).
# These are acquisition-readiness floors, not a performance gate; a chain below
# them is still parsed (adapter PASS) but reported NO-GO for downstream use.
DEFAULT_MIN_CONTRACTS = 8
DEFAULT_MIN_QUOTES = 8
DEFAULT_MIN_EXPIRIES = 2
DEFAULT_BID_ASK_TOLERANCE = 1e-9

_SYNTHETIC_MARKERS: Tuple[str, ...] = ("synthetic",)

# Field aliases (normalized to lowercase alnum for matching).
_FIELD_ALIASES: Dict[str, Tuple[str, ...]] = {
    "symbol": (
        "symbol",
        "instid",
        "instrument",
        "instrumentname",
        "instrumentid",
        "contract",
        "contractname",
    ),
    "underlying": ("underlying", "underlyingprice", "underlyingasset", "basecurrency"),
    "strike": ("strike", "strikeprice", "k"),
    "expiry": (
        "expiry",
        "expiration",
        "expirytime",
        "expirationtime",
        "expirationtimestamp",
        "expiry_timestamp".replace("_", ""),
        "expiredate",
        "expirydate",
        "deliverytime",
        "maturity",
        "matures",
    ),
    "option_type": (
        "optiontype",
        "type",
        "opttype",
        "callput",
        "cp",
        "right",
        "class",
    ),
    "timestamp": (
        "timestamp",
        "time",
        "ts",
        "date",
        "datetime",
        "quotetime",
        "tradetime",
        "transacttime",
        "eventtime",
        "updatedat",
    ),
    "bid": ("bid", "bidprice", "bestbid", "bidpx"),
    "ask": ("ask", "askprice", "bestask", "askpx", "offer", "offerprice"),
    "last": ("last", "lastprice", "lastpx", "trade"),
    "mark": ("mark", "markprice", "markpx", "mid", "midprice"),
    "bid_iv": ("bidiv", "bidimpliedvol", "bidivl"),
    "ask_iv": ("askiv", "askimpliedvol", "askivl"),
    "mark_iv": ("markiv", "markimpliedvol", "markivl", "iv", "impliedvol", "impliedvolatility"),
    "delta": ("delta",),
    "gamma": ("gamma",),
    "theta": ("theta",),
    "vega": ("vega",),
    "open_interest": ("openinterest", "oi", "openint"),
    "volume": ("volume", "vol", "vol24h", "volume24h", "turnover"),
    "contract_size": ("contractsize", "contractvalue", "multiplier", "ctval", "csize"),
}

_VENUE_FORMATS: Dict[str, Dict[str, Any]] = {
    "okx": {
        "csv_headers": [
            "instId",
            "strike",
            "expiry",
            "optionType",
            "bid",
            "ask",
            "mark",
            "markIv",
            "delta",
            "gamma",
            "theta",
            "vega",
            "openInterest",
            "volume",
            "ts",
        ],
        "json_shape": "list | {data: [...]} | {quotes: [...]}",
        "timestamp_forms": ["ISO-8601", "epoch-ms"],
        "option_type_forms": ["C", "P", "call", "put"],
    },
    "binance": {
        "csv_headers": [
            "symbol",
            "strike",
            "expiry",
            "optionType",
            "bid",
            "ask",
            "mark",
            "markIv",
            "delta",
            "gamma",
            "theta",
            "vega",
            "openInterest",
            "volume",
            "timestamp",
        ],
        "json_shape": "list | {quotes: [...]} | {data: [...]}",
        "timestamp_forms": ["ISO-8601", "epoch-ms"],
        "option_type_forms": ["CALL", "PUT"],
    },
    "deribit": {
        "csv_headers": [
            "instrument_name",
            "strike",
            "expiration_timestamp",
            "option_type",
            "bid_price",
            "ask_price",
            "mark_price",
            "mark_iv",
            "delta",
            "gamma",
            "theta",
            "vega",
            "open_interest",
            "volume",
            "timestamp",
        ],
        "json_shape": "list | {result: [...]} | {quotes: [...]}",
        "timestamp_forms": ["epoch-ms", "ISO-8601"],
        "option_type_forms": ["call", "put"],
    },
}


class OptionExportRejected(ValueError):
    """An option export failed format, schema or microstructure validation."""


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


def _parse_ts(value: Any, field: str = "timestamp") -> datetime:
    try:
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, bool):
            raise OptionExportRejected(f"boolean {field}: {value!r}")
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
                    raise OptionExportRejected(
                        f"unparseable {field}: {value!r}"
                    ) from None
        else:
            raise OptionExportRejected(f"unparseable {field}: {value!r}")
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(timezone.utc)
        if not math.isfinite(parsed.timestamp()):
            raise OptionExportRejected(f"non-finite {field}: {value!r}")
        return parsed
    except OptionExportRejected:
        raise
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        raise OptionExportRejected(f"unparseable {field}: {value!r}") from exc


def _parse_number(
    value: Any,
    field: str,
    *,
    positive: bool = True,
    non_negative: bool = False,
    allow_none: bool = False,
) -> Optional[float]:
    if value is None or (isinstance(value, str) and not value.strip()):
        if allow_none:
            return None
        raise OptionExportRejected(f"missing {field}")
    if isinstance(value, bool):
        raise OptionExportRejected(f"{field} is boolean: {value!r}")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise OptionExportRejected(f"non-numeric {field}: {value!r}") from None
    if not math.isfinite(number):
        raise OptionExportRejected(f"non-finite {field}: {value!r}")
    if positive and number <= 0.0:
        raise OptionExportRejected(f"non-positive {field}: {number!r}")
    if non_negative and number < 0.0:
        raise OptionExportRejected(f"negative {field}: {number!r}")
    return number


def _parse_option_type(value: Any) -> str:
    if value is None:
        raise OptionExportRejected("missing option_type")
    text = str(value).strip().lower()
    if text in ("c", "call", "calls"):
        return "call"
    if text in ("p", "put", "puts"):
        return "put"
    raise OptionExportRejected(f"invalid option_type: {value!r}")


def _infer_option_type_from_symbol(symbol: str) -> Optional[str]:
    text = symbol.strip().lower()
    if text.endswith("c") or "-c" in text:
        return "call"
    if text.endswith("p") or "-p" in text:
        return "put"
    return None


def _underlying_from_symbol(symbol: str, venue: str) -> str:
    text = symbol.strip()
    if not text:
        return ""
    # OKX / Binance: BTC-YYMMDD-STRIKE-C/P  or  BTC-YYMMDD-STRIKE-C
    parts = text.split("-")
    if len(parts) >= 2 and parts[0]:
        return normalize_symbol(parts[0], venue)
    # Deribit style: BTC-YYMMDD-STRIKE-C/P also handled above; fall back to leading token
    return normalize_symbol(re.split(r"[-_]", text)[0], venue)


def _detect_format(path: Path, format_hint: Optional[str]) -> str:
    if format_hint is not None:
        hint = str(format_hint).strip().lower()
        if hint not in SUPPORTED_FORMATS:
            raise OptionExportRejected(
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
        raise OptionExportRejected(f"unreadable export: {exc}") from None
    if head.startswith("[") or head.startswith("{"):
        return "json"
    return "csv"


def _read_json_records(path: Path) -> List[Mapping[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OptionExportRejected(f"unreadable JSON export: {exc}") from None

    items: Any = raw
    if isinstance(raw, dict):
        for key in ("quotes", "data", "result", "results", "items", "chain"):
            if isinstance(raw.get(key), list):
                items = raw[key]
                break
        else:
            raise OptionExportRejected("JSON export has no quotes/data/result list")
    if not isinstance(items, list):
        raise OptionExportRejected(
            f"JSON export quotes must be a list, got {type(items).__name__}"
        )
    if not items:
        raise OptionExportRejected("empty JSON export")
    if not all(isinstance(item, Mapping) for item in items):
        raise OptionExportRejected("every JSON quote must be an object")
    return list(items)


def _read_csv_records(path: Path, venue: str) -> List[Mapping[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise OptionExportRejected(f"unreadable CSV export: {exc}") from None
    if not text.strip():
        raise OptionExportRejected("empty CSV export")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise OptionExportRejected("CSV export has no data rows")
    if reader.fieldnames is None:
        raise OptionExportRejected("CSV export has no header row")

    header_keys = {_normalize_key(name) for name in reader.fieldnames}
    has_known_header = any(
        _normalize_key(alias) in header_keys
        for aliases in _FIELD_ALIASES.values()
        for alias in aliases
    )
    if has_known_header:
        return [dict(row) for row in rows]

    raise OptionExportRejected(
        f"headerless CSV unsupported for options venue {venue!r}; provide a header row"
    )


def _read_records(path: Path, venue: str, format_hint: Optional[str]) -> List[Mapping[str, Any]]:
    fmt = _detect_format(path, format_hint)
    if fmt == "json":
        return _read_json_records(path)
    return _read_csv_records(path, venue)


def _normalize_records(
    records: Sequence[Mapping[str, Any]], venue: str, underlying: str
) -> Tuple[List[Dict[str, Any]], str]:
    normalized: List[Dict[str, Any]] = []
    for index, raw in enumerate(records):
        record = _normalized_record(raw)

        _, symbol_value = _first_present(record, _FIELD_ALIASES["symbol"])
        symbol = str(symbol_value).strip() if symbol_value is not None else ""

        _, underlying_value = _first_present(record, _FIELD_ALIASES["underlying"])
        record_underlying = (
            normalize_symbol(str(underlying_value), venue)
            if underlying_value is not None
            else ""
        )
        if not record_underlying:
            record_underlying = _underlying_from_symbol(symbol, venue) if symbol else ""

        _, strike_value = _first_present(record, _FIELD_ALIASES["strike"])
        strike = _parse_number(strike_value, "strike", positive=True)

        _, expiry_value = _first_present(record, _FIELD_ALIASES["expiry"])
        expiry = _parse_ts(expiry_value, field="expiry")

        _, type_value = _first_present(record, _FIELD_ALIASES["option_type"])
        if type_value is None:
            inferred = _infer_option_type_from_symbol(symbol)
            if inferred is None:
                raise OptionExportRejected("missing option_type")
            option_type = inferred
        else:
            option_type = _parse_option_type(type_value)

        _, contract_size_value = _first_present(record, _FIELD_ALIASES["contract_size"])
        contract_size = _parse_number(
            contract_size_value, "contract_size", positive=True
        ) if contract_size_value is not None else 1.0

        _, ts_value = _first_present(record, _FIELD_ALIASES["timestamp"])
        timestamp = _parse_ts(ts_value)

        _, bid_value = _first_present(record, _FIELD_ALIASES["bid"])
        bid = _parse_number(bid_value, "bid", positive=False, non_negative=True)

        _, ask_value = _first_present(record, _FIELD_ALIASES["ask"])
        ask = _parse_number(ask_value, "ask", positive=False, non_negative=True)

        if ask < bid - DEFAULT_BID_ASK_TOLERANCE:
            raise OptionExportRejected(
                f"crossed market: ask {ask!r} < bid {bid!r}"
            )

        last = _parse_number(
            _first_present(record, _FIELD_ALIASES["last"])[1],
            "last",
            positive=False,
            non_negative=True,
            allow_none=True,
        )
        mark = _parse_number(
            _first_present(record, _FIELD_ALIASES["mark"])[1],
            "mark",
            positive=False,
            non_negative=True,
            allow_none=True,
        )
        bid_iv = _parse_number(
            _first_present(record, _FIELD_ALIASES["bid_iv"])[1],
            "bid_iv",
            positive=False,
            non_negative=True,
            allow_none=True,
        )
        ask_iv = _parse_number(
            _first_present(record, _FIELD_ALIASES["ask_iv"])[1],
            "ask_iv",
            positive=False,
            non_negative=True,
            allow_none=True,
        )
        mark_iv = _parse_number(
            _first_present(record, _FIELD_ALIASES["mark_iv"])[1],
            "mark_iv",
            positive=False,
            non_negative=True,
            allow_none=True,
        )
        delta = _parse_number(
            _first_present(record, _FIELD_ALIASES["delta"])[1],
            "delta",
            positive=False,
            allow_none=True,
        )
        gamma = _parse_number(
            _first_present(record, _FIELD_ALIASES["gamma"])[1],
            "gamma",
            positive=False,
            allow_none=True,
        )
        theta = _parse_number(
            _first_present(record, _FIELD_ALIASES["theta"])[1],
            "theta",
            positive=False,
            allow_none=True,
        )
        vega = _parse_number(
            _first_present(record, _FIELD_ALIASES["vega"])[1],
            "vega",
            positive=False,
            allow_none=True,
        )

        open_interest = _parse_number(
            _first_present(record, _FIELD_ALIASES["open_interest"])[1],
            "open_interest",
            positive=False,
            non_negative=True,
            allow_none=True,
        )
        volume = _parse_number(
            _first_present(record, _FIELD_ALIASES["volume"])[1],
            "volume",
            positive=False,
            non_negative=True,
            allow_none=True,
        )

        normalized.append(
            {
                "symbol": symbol,
                "underlying": record_underlying,
                "strike": strike,
                "expiry": expiry,
                "option_type": option_type,
                "contract_size": contract_size,
                "timestamp": timestamp,
                "bid": bid,
                "ask": ask,
                "last": last,
                "mark": mark,
                "bid_iv": bid_iv,
                "ask_iv": ask_iv,
                "mark_iv": mark_iv,
                "delta": delta,
                "gamma": gamma,
                "theta": theta,
                "vega": vega,
                "open_interest": open_interest,
                "volume": volume,
                "source_row": index,
            }
        )

    if not normalized:
        raise OptionExportRejected("empty export")

    requested = normalize_symbol(underlying, venue)
    if not requested:
        requested = next(
            (r["underlying"] for r in normalized if r["underlying"]), ""
        )
    if not requested:
        raise OptionExportRejected("empty underlying")

    seen: Dict[Tuple[str, datetime], int] = {}
    for record in normalized:
        if not record["symbol"]:
            raise OptionExportRejected("missing option symbol")
        key = (record["symbol"], record["timestamp"])
        if key in seen:
            raise OptionExportRejected(
                f"duplicate (symbol, timestamp): {record['symbol']!r} @ {record['timestamp']}"
            )
        seen[key] = 1

    normalized.sort(
        key=lambda r: (
            r["timestamp"],
            r["expiry"],
            r["strike"],
            r["option_type"],
            r["symbol"],
        )
    )

    return [
        {
            "symbol": r["symbol"],
            "underlying": r["underlying"] or requested,
            "strike": r["strike"],
            "expiry": r["expiry"],
            "option_type": r["option_type"],
            "contract_size": r["contract_size"],
            "timestamp": r["timestamp"],
            "bid": r["bid"],
            "ask": r["ask"],
            "last": r["last"],
            "mark": r["mark"],
            "bid_iv": r["bid_iv"],
            "ask_iv": r["ask_iv"],
            "mark_iv": r["mark_iv"],
            "delta": r["delta"],
            "gamma": r["gamma"],
            "theta": r["theta"],
            "vega": r["vega"],
            "open_interest": r["open_interest"],
            "volume": r["volume"],
        }
        for r in normalized
    ], requested


def _build_chain(
    normalized: Sequence[Mapping[str, Any]], venue: str, underlying: str
) -> OptionsChain:
    quotes: List[OptionQuote] = []
    previous: Optional[datetime] = None
    for record in normalized:
        timestamp = _parse_ts(record["timestamp"])
        expiry = _parse_ts(record["expiry"], field="expiry")
        if expiry <= timestamp:
            raise OptionExportRejected(
                f"expiry {expiry} must be after timestamp {timestamp}"
            )
        if previous is not None and timestamp < previous:
            raise OptionExportRejected(
                "quote timestamps are not monotone non-decreasing after canonical sort"
            )
        previous = timestamp
        contract = OptionContract(
            symbol=str(record["symbol"]),
            underlying=str(record["underlying"] or underlying),
            strike=float(record["strike"]),
            expiry=expiry,
            option_type=str(record["option_type"]),
            venue=venue,
            contract_size=float(record["contract_size"]),
        )
        quotes.append(
            OptionQuote(
                contract=contract,
                bid=float(record["bid"]),
                ask=float(record["ask"]),
                last=record["last"],
                mark=record["mark"],
                bid_iv=record["bid_iv"],
                ask_iv=record["ask_iv"],
                mark_iv=record["mark_iv"],
                delta=record["delta"],
                gamma=record["gamma"],
                theta=record["theta"],
                vega=record["vega"],
                open_interest=float(record["open_interest"] or 0.0),
                volume=float(record["volume"] or 0.0),
                timestamp=timestamp,
            )
        )
    if not quotes:
        raise OptionExportRejected("empty export")
    return OptionsChain(
        underlying=underlying,
        venue=venue,
        quotes=quotes,
        timestamp=max(q.timestamp for q in quotes),
    )


def _parse_export(
    path: Path,
    venue: str,
    underlying: str,
    format_hint: Optional[str] = None,
) -> Tuple[OptionsChain, Dict[str, Any]]:
    path = Path(path)
    venue_key = str(venue).strip().lower()
    if venue_key not in SUPPORTED_VENUES:
        raise OptionExportRejected(
            f"unsupported venue {venue!r}; expected {SUPPORTED_VENUES}"
        )
    if any(marker in path.name.lower() for marker in _SYNTHETIC_MARKERS):
        raise OptionExportRejected(
            f"synthetic filename is not an exchange option export: {path.name}"
        )
    if not path.is_file():
        raise OptionExportRejected(f"export file not found: {path}")

    fmt = _detect_format(path, format_hint)
    records = _read_records(path, venue_key, format_hint)
    normalized, requested_underlying = _normalize_records(records, venue_key, underlying)
    chain = _build_chain(normalized, venue_key, requested_underlying)

    expiries = sorted({q.contract.expiry for q in chain.quotes})
    strikes = sorted({q.contract.strike for q in chain.quotes})
    contracts = {(q.contract.symbol) for q in chain.quotes}
    metadata = {
        "format": fmt,
        "requested_venue": venue_key,
        "requested_underlying": normalize_symbol(underlying, venue_key),
        "normalized_underlying": chain.underlying,
        "n_records": len(records),
        "n_quotes": len(chain.quotes),
        "n_contracts": len(contracts),
        "n_strikes": len(strikes),
        "n_expires": len(expiries),
        "n_expiries": len(expiries),
        "option_types": sorted({q.contract.option_type for q in chain.quotes}),
        "strikes_min": float(min(strikes)) if strikes else None,
        "strikes_max": float(max(strikes)) if strikes else None,
    }
    return chain, metadata


def parse_options_export(
    path: str | Path,
    venue: str,
    underlying: str,
    format_hint: Optional[str] = None,
) -> OptionsChain:
    """Parse one exchange option export into a canonical options chain."""
    chain, _ = _parse_export(Path(path), venue, underlying, format_hint)
    return chain


def _canonical_fingerprint(chain: OptionsChain) -> str:
    parts = [
        f"{q.timestamp.isoformat()}|{q.contract.underlying}|{q.contract.expiry.isoformat()}|"
        f"{q.contract.strike:.10f}|{q.contract.option_type}|{q.contract.symbol}|"
        f"{q.bid:.10f}|{q.ask:.10f}"
        for q in chain.quotes
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _content_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def write_normalized_options_chain(chain: OptionsChain, out_path: str | Path) -> Path:
    """Write a loader-compatible normalized options chain JSON tape."""
    target = Path(out_path)
    if target.exists() and target.is_dir():
        stamp = _stamp_for_filename(_utc_now_iso())
        target = target / (
            f"options_{chain.venue}_{chain.underlying}_{stamp}.json"
        )
    elif target.suffix.lower() not in (".json",):
        target = target / (
            f"options_{chain.venue}_{chain.underlying}_"
            f"{_stamp_for_filename(_utc_now_iso())}.json"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "underlying": chain.underlying,
        "venue": chain.venue,
        "timestamp": _iso(chain.timestamp),
        "quotes": [
            {
                "symbol": q.contract.symbol,
                "underlying": q.contract.underlying,
                "strike": q.contract.strike,
                "expiry": _iso(q.contract.expiry),
                "option_type": q.contract.option_type,
                "venue": q.contract.venue,
                "contract_size": q.contract.contract_size,
                "bid": q.bid,
                "ask": q.ask,
                "last": q.last,
                "mark": q.mark,
                "bid_iv": q.bid_iv,
                "ask_iv": q.ask_iv,
                "mark_iv": q.mark_iv,
                "delta": q.delta,
                "gamma": q.gamma,
                "theta": q.theta,
                "vega": q.vega,
                "open_interest": q.open_interest,
                "volume": q.volume,
                "timestamp": _iso(q.timestamp),
            }
            for q in chain.quotes
        ],
    }
    assert_json_valid(payload)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return target


def _adequacy_counts(
    chain: OptionsChain,
    min_contracts: int,
    min_quotes: int,
    min_expiries: int,
) -> Dict[str, Any]:
    n_quotes = len(chain.quotes)
    n_contracts = len({q.contract.symbol for q in chain.quotes})
    n_expiries = len({q.contract.expiry for q in chain.quotes})
    n_strikes = len({q.contract.strike for q in chain.quotes})
    sample_adequate = bool(
        n_contracts >= int(min_contracts)
        and n_quotes >= int(min_quotes)
        and n_expiries >= int(min_expiries)
    )
    return {
        "n_quotes": int(n_quotes),
        "n_contracts": int(n_contracts),
        "n_strikes": int(n_strikes),
        "n_expiries": int(n_expiries),
        "min_contracts": int(min_contracts),
        "min_quotes": int(min_quotes),
        "min_expiries": int(min_expiries),
        "sample_adequate": sample_adequate,
        "shortfall_contracts": max(0, int(min_contracts) - n_contracts),
        "shortfall_quotes": max(0, int(min_quotes) - n_quotes),
        "shortfall_expiries": max(0, int(min_expiries) - n_expiries),
    }


def _supported_formats() -> List[Dict[str, Any]]:
    return [
        {"venue": venue, **_VENUE_FORMATS[venue]}
        for venue in SUPPORTED_VENUES
    ]


def evaluate_options_export(
    path: str | Path,
    venue: str,
    underlying: str,
    *,
    format_hint: Optional[str] = None,
    write: bool = True,
    out_dir: Path = OUT_DIR,
    normalized_out: Optional[Path] = None,
    min_contracts: int = DEFAULT_MIN_CONTRACTS,
    min_quotes: int = DEFAULT_MIN_QUOTES,
    min_expiries: int = DEFAULT_MIN_EXPIRIES,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate one option export and return a sealed readiness report."""
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
        "requested_underlying": normalize_symbol(underlying, str(venue).strip().lower()),
        "format": None,
        "adapter_verdict": "FAIL",
        "adequacy": None,
        "n_quotes": 0,
        "n_contracts": 0,
        "n_strikes": 0,
        "n_expiries": 0,
        "span_seconds": None,
        "start_timestamp": None,
        "end_timestamp": None,
        "content_sha256": None,
        "canonical_fingerprint": None,
        "normalized_chain_path": None,
        "normalized_chain_sha256": None,
        "microstructure_sane": False,
        "canonical_order": False,
        "loader_compatible": False,
        "supported_formats": _supported_formats(),
        "overall_verdict": "NO-GO",
        "overall_reason": "adapter failed",
        "floors": {
            "min_contracts": int(min_contracts),
            "min_quotes": int(min_quotes),
            "min_expiries": int(min_expiries),
        },
    }

    try:
        chain, metadata = _parse_export(source, venue, underlying, format_hint)
    except OptionExportRejected as exc:
        base["overall_reason"] = f"adapter rejected export: {exc}"
        return _finalize_report(base, write=write, out_dir=out_dir, stamp=stamp)

    span = (
        max(q.timestamp for q in chain.quotes)
        - min(q.timestamp for q in chain.quotes)
    ).total_seconds()
    adequacy = _adequacy_counts(chain, min_contracts, min_quotes, min_expiries)
    base.update(
        {
            "format": metadata["format"],
            "normalized_underlying": metadata["normalized_underlying"],
            "n_records": metadata["n_records"],
            "n_quotes": metadata["n_quotes"],
            "n_contracts": metadata["n_contracts"],
            "n_strikes": metadata["n_strikes"],
            "n_expiries": metadata["n_expiries"],
            "option_types": metadata["option_types"],
            "strikes_min": metadata["strikes_min"],
            "strikes_max": metadata["strikes_max"],
            "span_seconds": float(span),
            "start_timestamp": _iso(min(q.timestamp for q in chain.quotes)),
            "end_timestamp": _iso(max(q.timestamp for q in chain.quotes)),
            "content_sha256": _content_sha256(source),
            "canonical_fingerprint": _canonical_fingerprint(chain),
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
            normalized_path = write_normalized_options_chain(
                chain, Path(normalized_out)
            )
            base["normalized_chain_path"] = str(normalized_path)
            base["normalized_chain_sha256"] = hashlib.sha256(
                normalized_path.read_bytes()
            ).hexdigest()
        except (OSError, ValueError) as exc:
            base["adapter_verdict"] = "FAIL"
            base["loader_compatible"] = False
            base["overall_reason"] = f"normalized chain write failed: {exc}"
            adapter_failed = True

    if adequacy["sample_adequate"] and not adapter_failed:
        base["overall_verdict"] = "GO"
        base["overall_reason"] = (
            "adapter parsed export and chain clears EVAL-24 adequacy floors"
        )
    elif not adapter_failed:
        base["overall_reason"] = (
            "adapter parsed export but chain is below EVAL-24 adequacy floors "
            f"(contracts {adequacy['n_contracts']}/{adequacy['min_contracts']}, "
            f"quotes {adequacy['n_quotes']}/{adequacy['min_quotes']}, "
            f"expiries {adequacy['n_expiries']}/{adequacy['min_expiries']})"
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
        json_path = out / f"OPTIONS_EXPORT_ADAPTERS_{filename_stamp}.json"
        md_path = out / f"OPTIONS_EXPORT_ADAPTERS_{filename_stamp}.md"
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
        f"# {report['report_id']} — OPTION EXPORT ADAPTERS (EVAL-24A)",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- overall_verdict: **{report['overall_verdict']}**",
        f"- reason: {report['overall_reason']}",
        f"- adapter_verdict: {report['adapter_verdict']}",
        f"- trading_mode: {report['trading_mode']}",
        f"- data_provenance: {report['data_provenance']} "
        f"(authenticity_verified={str(report['authenticity_verified']).lower()})",
        f"- source_path: `{report['source_path']}`",
        f"- venue/underlying: `{report['venue']}` / `{report['requested_underlying']}`",
        f"- format: {report['format']}",
        f"- n_quotes: {report['n_quotes']}",
        f"- n_contracts: {report['n_contracts']}",
        f"- n_strikes: {report['n_strikes']}",
        f"- n_expiries: {report['n_expiries']}",
        f"- span_seconds: {report['span_seconds']}",
        f"- start/end: {report['start_timestamp']} → {report['end_timestamp']}",
        f"- canonical_fingerprint: `{report['canonical_fingerprint']}`",
        f"- normalized_chain: {report['normalized_chain_path']}",
        f"- floors: {report['floors']}",
    ]
    if adequacy:
        lines.append(
            "- adequacy: "
            f"{adequacy['n_contracts']}/{adequacy['min_contracts']} contracts, "
            f"{adequacy['n_quotes']}/{adequacy['min_quotes']} quotes, "
            f"{adequacy['n_expiries']}/{adequacy['min_expiries']} expiries, "
            f"adequate={str(adequacy['sample_adequate']).lower()}"
        )
    lines.extend(
        [
            "",
            "## Supported export formats",
            "",
            "| venue | csv headers | json shape | timestamps | option types |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["supported_formats"]:
        lines.append(
            f"| {item['venue']} | `{', '.join(item['csv_headers'])}` | "
            f"`{item['json_shape']}` | {', '.join(item['timestamp_forms'])} | "
            f"{', '.join(item['option_type_forms'])} |"
        )
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "Offline deterministic adapter; no network, no `.env`, no live "
            "trading. A parsed export is not proof of real provenance; EVAL-24 "
            "must validate the normalized chain before any options-leg decision.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exchange option-export adapters (EVAL-24A, paper-only)"
    )
    parser.add_argument("--in", dest="in_path", required=True, help="export file")
    parser.add_argument(
        "--venue", required=True, choices=SUPPORTED_VENUES, help="export venue"
    )
    parser.add_argument(
        "--underlying", default="", help="normalized underlying, e.g. BTC"
    )
    parser.add_argument(
        "--format", dest="format_hint", choices=SUPPORTED_FORMATS, default=None
    )
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="artifact dir")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="optional directory for the normalized loader-compatible chain",
    )
    parser.add_argument("--no-write", action="store_true", help="do not write artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument("--min-contracts", type=int, default=DEFAULT_MIN_CONTRACTS)
    parser.add_argument("--min-quotes", type=int, default=DEFAULT_MIN_QUOTES)
    parser.add_argument("--min-expiries", type=int, default=DEFAULT_MIN_EXPIRIES)
    args = parser.parse_args(argv)

    normalized_out = Path(args.data_dir) if args.data_dir else None
    report = evaluate_options_export(
        args.in_path,
        args.venue,
        args.underlying,
        format_hint=args.format_hint,
        write=not args.no_write,
        out_dir=Path(args.out),
        normalized_out=normalized_out,
        min_contracts=args.min_contracts,
        min_quotes=args.min_quotes,
        min_expiries=args.min_expiries,
        timestamp=args.timestamp,
    )
    print(
        json.dumps(
            {
                "overall_verdict": report["overall_verdict"],
                "adapter_verdict": report["adapter_verdict"],
                "n_quotes": report["n_quotes"],
                "normalized_chain_path": report["normalized_chain_path"],
                "artifact_paths": report["artifact_paths"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())