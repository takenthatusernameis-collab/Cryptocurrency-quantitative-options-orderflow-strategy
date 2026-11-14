#!/usr/bin/env python3
"""EVAL-45: multi-window real ETH orderflow acquisition (bottleneck removal).

The sealed EVAL-41/42/43/44 campaign is BTC/OKX only. EVAL-45 needs the same
net-of-cost falsification on a **second** crypto asset. The remaining blocker was
never the measurement code: it was that the EVAL-26 acquisition CLI writes one
fixed ``orderflow_okx_<symbol>.json`` path, so N disjoint windows could not be
acquired without hand-rolling cursor chaining.

This script removes that blocker and nothing else:

  * it reuses ``fetch_okx_history_trades`` (public, read-only, no credentials)
    and ``write_orderflow_tape`` from the sealed EVAL-26 module;
  * it chains windows with ``after_cursor = <oldest trade id of previous tape>``
    so windows are strictly disjoint and strictly older (verified, not assumed);
  * every window must meet the declared floors (``--min-trades``, ``--min-bars``)
    or the run raises — a short window is never reported as a success;
  * every written tape is re-loaded through ``load_real_orderflow(symbol=...)``
    and the trade count is compared to the file, so an un-loadable tape fails;
  * provenance is explicit (``authenticated=false``, ``public_read_only=true``)
    and synthetic-marked paths are refused.

It seals a **data-acquisition** manifest
(``EVAL_45_ETH_TAPE_ACQUISITION_<UTC>.{json,md}``) with measured per-window
facts. It does not measure performance and never emits a GO/NO-GO verdict; the
measurement is the next step (EVAL-45 orderflow + options meta-analysis).

CLI::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 scripts/eval45_acquire_eth_windows.py --windows 5 \
        --min-bars 420 --min-trades 35000 --seal
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests

from src.campaign.integrated import load_real_orderflow
from src.data.public_export_acquisition import (
    AcquisitionError,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_REQUEST_DELAY_SECONDS,
    fetch_okx_history_trades,
    write_orderflow_tape,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
DATA_RAW_DIR = Path("data/raw")
REPORT_ID = "EVAL_45_ETH_TAPE_ACQUISITION"

DEFAULT_INST_ID = "ETH-USD-SWAP"
DEFAULT_SYMBOL = "ETH"
DEFAULT_WINDOWS = 5
DEFAULT_MIN_BARS = 420
DEFAULT_MIN_TRADES = 35000
DEFAULT_BAR_DURATION_SECONDS = 15.0
DEFAULT_MAX_PAGES = 6000

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False
DATA_PROVENANCE = "okx_public_read_only_history_trades"
AUTHENTICITY_VERIFIED = False

CODE_PATHS: Tuple[str, ...] = (
    "src/data/public_export_acquisition.py",
    "src/campaign/integrated.py",
    "scripts/eval45_acquire_eth_windows.py",
    "tests/test_eval45_acquire_eth_windows.py",
)


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def stamp_for_filename(iso_ts: str) -> str:
    return _parse_ts(iso_ts).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def window_filename(prefix: str, symbol: str, index: int, first_trade_id: str) -> str:
    """Loader-discoverable, collision-free tape name (never synthetic-marked)."""
    safe_symbol = str(symbol).strip().upper().replace("/", "-")
    safe_prefix = str(prefix).strip().strip("_") or "orderflow_okx"
    if "synthetic" in f"{safe_prefix}_{safe_symbol}".lower():
        raise AcquisitionError("refusing synthetic-marked output name")
    return f"{safe_prefix}_{safe_symbol}_w{index:02d}_{first_trade_id}.json"


def required_pages(min_trades: int, page_limit: int) -> int:
    """Minimum pages that can carry ``min_trades`` rows at ``page_limit``/page."""
    limit = max(int(page_limit), 1)
    return int(math.ceil(max(int(min_trades), 1) / limit))


def estimate_min_bars(
    probe_span_seconds: float,
    probe_trades: int,
    *,
    bar_duration_seconds: float,
    target_trades: int,
) -> int:
    """Bars needed so the span carries ``target_trades`` at the measured rate."""
    bar = max(float(bar_duration_seconds), 1.0)
    span = float(probe_span_seconds)
    n = int(probe_trades)
    if span <= 0.0 or n <= 0:
        return 1
    rate_per_second = n / span
    if rate_per_second <= 0.0:
        return 1
    seconds_needed = max(int(target_trades), 1) / rate_per_second
    return max(1, int(math.ceil(seconds_needed / bar)))


def validate_window(
    *,
    trades: Sequence[Mapping[str, Any]],
    min_trades: int,
    min_bars: int,
    bar_duration_seconds: float,
) -> Dict[str, Any]:
    """Reject a short/degenerate window; return measured window facts."""
    rows = list(trades)
    if len(rows) < int(min_trades):
        raise AcquisitionError(
            f"window has {len(rows)} trades < required {int(min_trades)}"
        )
    ids = [str(r["trade_id"]) for r in rows]
    if len(set(ids)) != len(ids):
        raise AcquisitionError("duplicate trade ids inside a single window")
    stamps = sorted(int(r["timestamp_ms"]) for r in rows)
    span = (stamps[-1] - stamps[0]) / 1000.0
    bars = max(1, int(math.ceil(span / max(float(bar_duration_seconds), 1.0))))
    if bars < int(min_bars):
        raise AcquisitionError(f"window spans {bars} bars < required {int(min_bars)}")
    return {
        "n_trades": len(rows),
        "n_bars": int(bars),
        "span_seconds": float(span),
        "first_trade_id": str(rows[0]["trade_id"]),
        "last_trade_id": str(rows[-1]["trade_id"]),
        "first_trade_utc": str(rows[0]["timestamp"]),
        "last_trade_utc": str(rows[-1]["timestamp"]),
    }


def assert_disjoint(previous: Mapping[str, Any], current: Mapping[str, Any]) -> Dict[str, Any]:
    """Windows are disjoint and strictly older: cursor == previous oldest id."""
    prev_ids = [str(t) for t in previous.get("trade_ids", [])]
    cur_ids = [str(t) for t in current.get("trade_ids", [])]
    overlap = sorted(set(prev_ids) & set(cur_ids))
    if overlap:
        raise AcquisitionError(f"windows overlap on {len(overlap)} trade ids")
    cursor = str(current.get("after_cursor") or "")
    if cursor and cursor != str(previous["first_trade_id"]):
        raise AcquisitionError("cursor is not the previous window's oldest trade id")
    if int(current["newest_timestamp_ms"]) >= int(previous["newest_timestamp_ms"]):
        raise AcquisitionError("current window is not strictly older than the previous")
    return {
        "disjoint": True,
        "overlap_trade_ids": 0,
        "after_cursor": cursor,
        "strictly_older": True,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _all_finite(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, float):
        return math.isfinite(obj)
    if isinstance(obj, int):
        return True
    if isinstance(obj, dict):
        return all(_all_finite(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_finite(v) for v in obj)
    return True


# ---------------------------------------------------------------------------
# Acquisition
# ---------------------------------------------------------------------------


def acquire_windows(
    *,
    inst_id: str = DEFAULT_INST_ID,
    symbol: str = DEFAULT_SYMBOL,
    windows: int = DEFAULT_WINDOWS,
    min_bars: int = DEFAULT_MIN_BARS,
    min_trades: int = DEFAULT_MIN_TRADES,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    page_limit: int = DEFAULT_PAGE_LIMIT,
    max_pages: int = DEFAULT_MAX_PAGES,
    request_delay_seconds: float = DEFAULT_REQUEST_DELAY_SECONDS,
    out_dir: Path | str = DATA_RAW_DIR,
    prefix: str = "orderflow_okx",
    session: Any = None,
    max_attempts: int = 4,
) -> Dict[str, Any]:
    """Acquire ``windows`` disjoint real tapes, each meeting the declared floors."""
    if int(windows) < 1:
        raise AcquisitionError("windows must be >= 1")
    session = session or requests.Session()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    window_records: List[Dict[str, Any]] = []
    cursor: Optional[str] = None
    previous: Optional[Dict[str, Any]] = None

    for index in range(1, int(windows) + 1):
        attempts: List[Dict[str, Any]] = []
        accepted: Optional[Dict[str, Any]] = None
        target_bars = int(min_bars)
        for attempt in range(1, int(max_attempts) + 1):
            result = fetch_okx_history_trades(
                inst_id,
                session=session,
                min_bars=target_bars,
                bar_duration_seconds=bar_duration_seconds,
                page_limit=page_limit,
                max_pages=max_pages,
                request_delay_seconds=request_delay_seconds,
                after_cursor=cursor,
            )
            trades = list(result.get("trades") or [])
            try:
                facts = validate_window(
                    trades=trades,
                    min_trades=min_trades,
                    min_bars=min_bars,
                    bar_duration_seconds=bar_duration_seconds,
                )
            except AcquisitionError as exc:
                attempts.append({"attempt": attempt, "target_bars": target_bars,
                                 "n_trades": len(trades), "error": str(exc)})
                target_bars = int(math.ceil(target_bars * 1.6)) + 1
                continue
            path = out / window_filename(prefix, symbol, index, facts["first_trade_id"])
            write_orderflow_tape(result, path)
            loaded = load_real_orderflow(symbol, orderflow_path=path)
            loaded_trades = int(len(loaded.trades or []))
            if loaded_trades != facts["n_trades"]:
                raise AcquisitionError(
                    f"loader mismatch for {path.name}: file {facts['n_trades']} "
                    f"vs loaded {loaded_trades}"
                )
            newest_ms = max(int(t["timestamp_ms"]) for t in trades)
            record = {
                "window": index,
                "path": str(path),
                "sha256": _sha256(path),
                "inst_id": inst_id,
                "symbol": str(symbol),
                "after_cursor": cursor,
                "target_bars": int(target_bars),
                "attempts": attempts,
                "pages": int(result.get("pages", 0)),
                "loader_trades": loaded_trades,
                "loader_ok": True,
                "trade_ids": [str(t["trade_id"]) for t in trades],
                "oldest_timestamp_ms": min(int(t["timestamp_ms"]) for t in trades),
                "newest_timestamp_ms": newest_ms,
                **facts,
            }
            record["window_facts"] = {
                "n_trades": facts["n_trades"],
                "n_bars": facts["n_bars"],
                "span_seconds": facts["span_seconds"],
                "first_trade_id": facts["first_trade_id"],
                "last_trade_id": facts["last_trade_id"],
                "first_trade_utc": facts["first_trade_utc"],
                "last_trade_utc": facts["last_trade_utc"],
            }
            record["newest_trade_id"] = max(
                (str(t["trade_id"]) for t in trades), key=lambda v: int(v)
            )
            if previous is not None:
                record["disjointness"] = assert_disjoint(previous, record)
            else:
                record["disjointness"] = {"disjoint": True, "overlap_trade_ids": 0,
                                          "after_cursor": None, "strictly_older": True}
            accepted = record
            break

        if accepted is None:
            raise AcquisitionError(
                f"window {index} could not meet the floors after {max_attempts} attempts"
            )
        window_records.append(accepted)
        cursor = accepted["first_trade_id"]
        previous = accepted

    total_trades = sum(int(r["n_trades"]) for r in window_records)
    report = build_report(
        generated_at=utc_now_iso(),
        inst_id=inst_id,
        symbol=symbol,
        windows=window_records,
        total_trades=total_trades,
        bar_duration_seconds=bar_duration_seconds,
        min_bars=min_bars,
        min_trades=min_trades,
    )
    return report


def build_report(
    *,
    generated_at: str,
    inst_id: str,
    symbol: str,
    windows: Sequence[Mapping[str, Any]],
    total_trades: int,
    bar_duration_seconds: float,
    min_bars: int,
    min_trades: int,
) -> Dict[str, Any]:
    """Build the acquisition manifest (no performance verdict, by design)."""
    public = []
    for record in windows:
        public.append({k: v for k, v in record.items() if k != "trade_ids"})
    n_windows = len(public)
    all_disjoint = all(bool(r.get("disjointness", {}).get("disjoint")) for r in public)
    floors_met = n_windows >= 1 and all(
        int(r["n_trades"]) >= int(min_trades) and int(r["n_bars"]) >= int(min_bars)
        for r in public
    )
    return {
        "report_id": REPORT_ID,
        "artifact_kind": "data_acquisition",
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-45-ACQUIRE-ETH-WINDOWS",
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "data_provenance": DATA_PROVENANCE,
        "authenticity_verified": AUTHENTICITY_VERIFIED,
        "venue": "okx",
        "inst_id": str(inst_id),
        "symbol": str(symbol),
        "bar_duration_seconds": float(bar_duration_seconds),
        "declared_floors": {
            "min_windows": int(len(windows)),
            "min_bars": int(min_bars),
            "min_trades": int(min_trades),
        },
        "verdict": "DATA_ACQUIRED_NO_MEASUREMENT",
        "verdict_reason": (
            "real, read-only OKX public ETH trade tapes acquired and loader-verified; "
            "this artifact carries no net-of-cost performance measurement"
        ),
        "n_windows": int(n_windows),
        "total_trades": int(total_trades),
        "all_windows_disjoint": bool(all_disjoint),
        "all_floors_met": bool(floors_met),
        "windows": public,
        "code_paths": list(CODE_PATHS),
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    serialized = serialize_metrics_strict(dict(payload))
    assert_json_valid(serialized)
    path.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_md(report: Mapping[str, Any]) -> str:
    lines = [
        f"# {report['report_id']} — real ETH orderflow tape acquisition",
        "",
        f"- **Generated:** {report['generated_at']}",
        f"- **Task ID:** `{report['task_id']}`",
        f"- **Artifact kind:** `{report['artifact_kind']}` (no performance verdict)",
        f"- **Venue / instrument:** `{report['venue']}` / `{report['inst_id']}` "
        f"(symbol `{report['symbol']}`)",
        f"- **Provenance:** {report['data_provenance']} "
        f"(authenticated=false, authenticity_verified=false)",
        f"- **Floors:** min_trades={report['declared_floors']['min_trades']}, "
        f"min_bars={report['declared_floors']['min_bars']}, "
        f"bar={report['bar_duration_seconds']}s",
        f"- **Windows:** {report['n_windows']} (total {report['total_trades']} trades); "
        f"all disjoint: {report['all_windows_disjoint']}; floors met: {report['all_floors_met']}",
        "",
        "## Windows",
        "",
        "| window | trades | bars | first trade (UTC) | last trade (UTC) | first id | last id | pages | loader | sha256 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for w in report["windows"]:
        lines.append(
            f"| {w['window']} | {w['n_trades']} | {w['n_bars']} | {w['first_trade_utc']} | "
            f"{w['last_trade_utc']} | {w['first_trade_id']} | {w['last_trade_id']} | "
            f"{w['pages']} | {w['loader_ok']} | `{w['sha256'][:16]}…` |"
        )
    lines.append("")
    lines.append("## Paths")
    for w in report["windows"]:
        lines.append(f"- `{w['path']}`")
    lines.append("")
    lines.append("## Code paths")
    for path in report["code_paths"]:
        lines.append(f"- `{path}`")
    return "\n".join(lines)


def seal(report: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = stamp_for_filename(str(report["generated_at"]))
    jpath = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
    mpath = OUT_DIR / f"{REPORT_ID}_{stamp}.md"
    _write_json(jpath, report)
    mpath.write_text(build_md(report) + "\n", encoding="utf-8")
    return {"json": str(jpath), "md": str(mpath)}


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inst-id", default=DEFAULT_INST_ID)
    ap.add_argument("--symbol", default=DEFAULT_SYMBOL)
    ap.add_argument("--windows", type=int, default=DEFAULT_WINDOWS)
    ap.add_argument("--min-bars", type=int, default=DEFAULT_MIN_BARS)
    ap.add_argument("--min-trades", type=int, default=DEFAULT_MIN_TRADES)
    ap.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    ap.add_argument("--page-limit", type=int, default=DEFAULT_PAGE_LIMIT)
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    ap.add_argument("--request-delay-seconds", type=float, default=DEFAULT_REQUEST_DELAY_SECONDS)
    ap.add_argument("--out-dir", default=str(DATA_RAW_DIR))
    ap.add_argument("--prefix", default="orderflow_okx")
    ap.add_argument("--seal", action="store_true", help="write the acquisition manifest")
    ap.add_argument("--no-seal", dest="seal", action="store_false")
    ap.set_defaults(seal=False)
    args = ap.parse_args(argv)

    try:
        report = acquire_windows(
            inst_id=args.inst_id,
            symbol=args.symbol,
            windows=args.windows,
            min_bars=args.min_bars,
            min_trades=args.min_trades,
            bar_duration_seconds=args.bar_duration_seconds,
            page_limit=args.page_limit,
            max_pages=args.max_pages,
            request_delay_seconds=args.request_delay_seconds,
            out_dir=Path(args.out_dir),
            prefix=args.prefix,
        )
    except Exception as exc:  # noqa: BLE001 - fail loudly, never seal a false success
        traceback.print_exc()
        print(json.dumps({"report_id": REPORT_ID, "status": "FAILED",
                          "error_type": type(exc).__name__, "error": str(exc)},
                         sort_keys=True))
        return 1

    if not _all_finite(report):
        print(json.dumps({"report_id": REPORT_ID, "status": "FAILED",
                          "error": "non-finite values in manifest"}, sort_keys=True))
        return 1

    paths = seal(report) if args.seal else {}
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "n_windows": report["n_windows"],
        "total_trades": report["total_trades"],
        "all_windows_disjoint": report["all_windows_disjoint"],
        "all_floors_met": report["all_floors_met"],
        "artifact_paths": paths,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())