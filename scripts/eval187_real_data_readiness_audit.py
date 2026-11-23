#!/usr/bin/env python3
"""EVAL-187 real-data readiness audit (non-verdict; EVAL-186 prerequisite)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
RS_DIR = ROOT / "research_state"
DATA_DIR = ROOT / "data" / "raw"
FORWARD_CAPTURE_DIR = DATA_DIR / "eval185cap"

REPORT_ID = "EVAL_187_REAL_DATA_READINESS_AUDIT"
ROLLING_JSON = RS_DIR / "EVAL_187_REAL_DATA_READINESS.json"
ROLLING_MD = RS_DIR / "EVAL_187_REAL_DATA_READINESS.md"
TASK_ID = "INIT-2026-11-23T10:50:09Z-EVAL187-REAL-DATA-READINESS-AUDIT"
TASK_LABEL = "EVAL187-REAL-DATA-READINESS-AUDIT"
CAPTURE_GLOB = "**/three_way_*.json"

STATUS_OK = "OK"
STATUS_SPARSE = "SPARSE"
STATUS_DEGENERATE = "DEGENERATE"
STATUS_ERROR = "ERROR"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: Any) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _span_seconds(start: Any, end: Any) -> float:
    start_dt = _parse_iso(start)
    end_dt = _parse_iso(end)
    if start_dt is None or end_dt is None:
        return 0.0
    return max(0.0, (end_dt - start_dt).total_seconds())


def _rows(value: Any) -> List[Dict[str, Any]]:
    return [row for row in (value or []) if isinstance(row, dict)] if isinstance(value, list) else []


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _positive_number(value: Any) -> bool:
    return _is_number(value) and float(value) > 0.0


def _row_span_seconds(rows: Sequence[Dict[str, Any]], key: str = "ts") -> float:
    stamps = [int(row.get(key) or 0) for row in rows if int(row.get(key) or 0) > 0]
    if len(stamps) < 2:
        return 0.0
    return max(0.0, (max(stamps) - min(stamps)) / 1000.0)


def _bar_count(span_seconds: float, bar_seconds: float = 300.0) -> int:
    return int(span_seconds // bar_seconds) if span_seconds > 0 else 0


def _capture_files(capture_root: Path) -> List[Path]:
    if not capture_root.is_dir():
        return []
    return sorted(path for path in capture_root.glob(CAPTURE_GLOB) if path.is_file())


def _audit_capture(path: Path) -> Dict[str, Any]:
    size_bytes = path.stat().st_size if path.exists() else 0
    row: Dict[str, Any] = {
        "path": str(path),
        "relative_path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "size_bytes": int(size_bytes),
    }
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        row.update({"status": STATUS_ERROR, "issues": [f"json_parse_error:{exc!r}"]})
        return row

    if not isinstance(payload, dict):
        row.update({"status": STATUS_ERROR, "issues": ["json_root_not_object"]})
        return row

    schema = str(payload.get("schema") or "")
    underlying = str(payload.get("underlying") or "")
    venue = str(payload.get("venue") or "")
    window_start = payload.get("window_start")
    window_end = payload.get("window_end")
    capture_span = _span_seconds(window_start, window_end)

    surface = _dict(payload.get("surface"))
    snapshots = _rows(surface.get("snapshots"))
    quotes: List[Dict[str, Any]] = []
    spot_non_null = 0
    for snapshot in snapshots:
        if snapshot.get("spot") is not None:
            spot_non_null += 1
        quotes.extend(_rows(snapshot.get("quotes")))

    quotes_with_bid_ask = sum(
        1 for quote in quotes if _positive_number(quote.get("bid")) and _positive_number(quote.get("ask"))
    )
    quotes_with_mark = sum(1 for quote in quotes if _positive_number(quote.get("mark")))
    quotes_with_iv = sum(
        1
        for quote in quotes
        if any(_is_number(quote.get(key)) for key in ("bid_iv", "ask_iv", "mark_iv"))
    )
    surface_instruments = len({str(quote.get("symbol")) for quote in quotes if quote.get("symbol")})

    option_trades = _rows(payload.get("option_trades"))
    option_trades_with_price_size = sum(
        1
        for trade in option_trades
        if _positive_number(trade.get("price")) and _positive_number(trade.get("amount"))
    )
    option_trades_with_instrument = sum(1 for trade in option_trades if trade.get("instrument"))
    option_trades_with_ts = sum(1 for trade in option_trades if int(trade.get("ts") or 0) > 0)
    option_span = _row_span_seconds(option_trades)

    perp_candles = _rows(payload.get("perp_candles"))
    perp_candles_with_ohlc = sum(
        1
        for candle in perp_candles
        if all(_is_number(candle.get(key)) for key in ("open", "high", "low", "close"))
    )
    perp_candles_with_ts = sum(1 for candle in perp_candles if int(candle.get("ts") or 0) > 0)
    perp_span = _row_span_seconds(perp_candles)

    okx_perp_trades = _rows(payload.get("okx_perp_trades"))
    okx_perp_trades_with_price_size = sum(
        1
        for trade in okx_perp_trades
        if _positive_number(trade.get("px")) and _positive_number(trade.get("sz"))
    )
    okx_perp_trades_with_ts = sum(1 for trade in okx_perp_trades if int(trade.get("ts") or 0) > 0)
    okx_span = _row_span_seconds(okx_perp_trades)

    source = _dict(payload.get("source"))
    source_public_read_only = bool(source.get("public_read_only"))
    source_authenticated = bool(source.get("authenticated"))
    is_synthetic = "synthetic" in path.name.lower() or "synthetic" in schema.lower()

    issues: List[str] = []
    if capture_span <= 0:
        issues.append("invalid_capture_window")
    if not snapshots:
        issues.append("surface_snapshots_empty")
    if snapshots and spot_non_null == 0:
        issues.append("surface_spot_all_null")
    if quotes and quotes_with_bid_ask == 0:
        issues.append("surface_quotes_missing_bid_ask")
    if quotes and quotes_with_mark == 0:
        issues.append("surface_quotes_missing_mark")
    if not option_trades:
        issues.append("option_trades_empty")
    if option_trades and option_trades_with_price_size == 0:
        issues.append("option_trades_missing_price_size")
    if not perp_candles:
        issues.append("perp_candles_empty")
    if perp_candles and perp_candles_with_ohlc == 0:
        issues.append("perp_candles_missing_ohlc")
    if not okx_perp_trades:
        issues.append("okx_perp_trades_empty")
    if okx_perp_trades and okx_perp_trades_with_price_size == 0:
        issues.append("okx_perp_trades_missing_price_size")
    if not source_public_read_only:
        issues.append("source_not_public_read_only")
    if source_authenticated:
        issues.append("source_authenticated")
    if is_synthetic:
        issues.append("synthetic_marker")

    core_counts = (len(snapshots), len(option_trades), len(perp_candles), len(okx_perp_trades))
    if all(count == 0 for count in core_counts):
        status = STATUS_DEGENERATE
    elif all(count > 0 for count in core_counts) and not any(
        issue
        for issue in issues
        if issue
        in {
            "invalid_capture_window",
            "surface_snapshots_empty",
            "surface_spot_all_null",
            "surface_quotes_missing_bid_ask",
            "surface_quotes_missing_mark",
            "option_trades_empty",
            "option_trades_missing_price_size",
            "perp_candles_empty",
            "perp_candles_missing_ohlc",
            "okx_perp_trades_empty",
            "okx_perp_trades_missing_price_size",
            "synthetic_marker",
        }
    ):
        status = STATUS_OK
    else:
        status = STATUS_SPARSE

    row.update(
        {
            "schema": schema,
            "underlying": underlying,
            "venue": venue,
            "window_start": window_start,
            "window_end": window_end,
            "capture_span_seconds": round(capture_span, 3),
            "n_surface_snapshots": len(snapshots),
            "n_surface_bars_5m": _bar_count(capture_span),
            "n_surface_instruments": surface_instruments,
            "n_surface_quotes": len(quotes),
            "n_surface_snapshots_with_spot": spot_non_null,
            "n_surface_quotes_with_bid_ask": quotes_with_bid_ask,
            "n_surface_quotes_with_mark": quotes_with_mark,
            "n_surface_quotes_with_iv": quotes_with_iv,
            "n_option_trades": len(option_trades),
            "n_option_trades_with_price_size": option_trades_with_price_size,
            "n_option_trades_with_instrument": option_trades_with_instrument,
            "n_option_trades_with_ts": option_trades_with_ts,
            "option_trade_span_seconds": round(option_span, 3),
            "n_option_bars_5m": _bar_count(option_span),
            "n_perp_candles": len(perp_candles),
            "n_perp_candles_with_ohlc": perp_candles_with_ohlc,
            "n_perp_candles_with_ts": perp_candles_with_ts,
            "perp_span_seconds": round(perp_span, 3),
            "n_perp_bars_5m": _bar_count(perp_span),
            "n_okx_perp_trades": len(okx_perp_trades),
            "n_okx_perp_trades_with_price_size": okx_perp_trades_with_price_size,
            "n_okx_perp_trades_with_ts": okx_perp_trades_with_ts,
            "okx_perp_trade_span_seconds": round(okx_span, 3),
            "source_public_read_only": source_public_read_only,
            "source_authenticated": source_authenticated,
            "is_synthetic": is_synthetic,
            "status": status,
            "issues": issues,
        }
    )
    return row


def _status_counts(captures: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    counts = {STATUS_OK: 0, STATUS_SPARSE: 0, STATUS_DEGENERATE: 0, STATUS_ERROR: 0}
    for capture in captures:
        status = str(capture.get("status") or STATUS_ERROR)
        counts[status] = counts.get(status, 0) + 1
    return counts


def _issue_counts(captures: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for capture in captures:
        for issue in capture.get("issues") or []:
            counts[str(issue)] = counts.get(str(issue), 0) + 1
    return dict(sorted(counts.items()))


def _forward_capture(capture_root: Path, forward_dir: Path) -> Dict[str, Any]:
    files = _capture_files(forward_dir)
    return {
        "capture_dir": str(forward_dir),
        "file_count": len(files),
        "files": [str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path) for path in files],
        "audits": [_audit_capture(path) for path in files],
    }


def build_report(
    *,
    capture_root: Path = DATA_DIR,
    forward_dir: Path = FORWARD_CAPTURE_DIR,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    started = time.monotonic()
    now = now or _utc_now()
    paths = _capture_files(capture_root)
    captures = [_audit_capture(path) for path in paths]
    counts = _status_counts(captures)
    issues = _issue_counts(captures)
    total_bytes = sum(int(capture.get("size_bytes") or 0) for capture in captures)
    total_surface_snapshots = sum(int(capture.get("n_surface_snapshots") or 0) for capture in captures)
    total_option_trades = sum(int(capture.get("n_option_trades") or 0) for capture in captures)
    total_perp_candles = sum(int(capture.get("n_perp_candles") or 0) for capture in captures)
    total_okx_perp_trades = sum(int(capture.get("n_okx_perp_trades") or 0) for capture in captures)
    total_records = total_surface_snapshots + total_option_trades + total_perp_candles + total_okx_perp_trades

    if counts[STATUS_ERROR] > 0:
        audit_status = STATUS_ERROR
    elif counts[STATUS_SPARSE] > 0 or counts[STATUS_DEGENERATE] > 0:
        audit_status = "ATTENTION"
    else:
        audit_status = "PASS"

    forward = _forward_capture(capture_root, forward_dir)
    forward_statuses = [str(item.get("status") or STATUS_ERROR) for item in forward["audits"]]
    forward_ok = bool(forward["audits"]) and all(status == STATUS_OK for status in forward_statuses)

    report = {
        "report_id": REPORT_ID,
        "generated_at": _iso(now),
        "task_id": TASK_ID,
        "task": TASK_LABEL,
        "is_verdict_rung": False,
        "ok": counts[STATUS_ERROR] == 0,
        "audit_status": audit_status,
        "capture_root": str(capture_root),
        "captures": captures,
        "summary": {
            "capture_count": len(captures),
            "status_counts": counts,
            "issue_counts": issues,
            "underlyings": sorted({str(capture.get("underlying") or "") for capture in captures if capture.get("underlying")}),
            "venues": sorted({str(capture.get("venue") or "") for capture in captures if capture.get("venue")}),
            "total_bytes": total_bytes,
            "total_surface_snapshots": total_surface_snapshots,
            "total_option_trades": total_option_trades,
            "total_perp_candles": total_perp_candles,
            "total_okx_perp_trades": total_okx_perp_trades,
            "total_records": total_records,
        },
        "forward_capture": {
            "capture_dir": forward["capture_dir"],
            "file_count": forward["file_count"],
            "files": forward["files"],
            "statuses": forward_statuses,
            "all_ok": forward_ok,
            "audits": forward["audits"],
        },
        "heavy_work": {
            "files_scanned": len(captures),
            "bytes_scanned": total_bytes,
            "records_scanned": total_records,
            "duration_seconds": round(time.monotonic() - started, 3),
        },
        "note": (
            "EVAL-187 is a non-verdict real-data readiness audit. It never emits GO/NO-GO, "
            "never modifies sealed artifacts or src/, and never replaces EVAL-186."
        ),
    }
    return report


def _md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|")


def build_markdown(report: Dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    counts = summary.get("status_counts") or {}
    issues = summary.get("issue_counts") or {}
    lines = [
        f"# {REPORT_ID} — real-data readiness audit (non-verdict)",
        "",
        f"- Generated: `{report.get('generated_at')}`",
        f"- Task: `{report.get('task')}`",
        f"- Verdict rung: `{report.get('is_verdict_rung')}`",
        f"- Audit status: **{report.get('audit_status')}**",
        f"- Captures scanned: `{summary.get('capture_count')}`",
        f"- Bytes scanned: `{summary.get('total_bytes')}`",
        f"- Records scanned: `{summary.get('total_records')}`",
        f"- Surface snapshots: `{summary.get('total_surface_snapshots')}`",
        f"- Option trades: `{summary.get('total_option_trades')}`",
        f"- Perp candles: `{summary.get('total_perp_candles')}`",
        f"- OKX perp trades: `{summary.get('total_okx_perp_trades')}`",
        "",
        "## Status counts",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status in (STATUS_OK, STATUS_SPARSE, STATUS_DEGENERATE, STATUS_ERROR):
        lines.append(f"| {status} | {counts.get(status, 0)} |")
    lines.extend(["", "## Issue counts", "", "| issue | count |", "|---|---:|"])
    if issues:
        for issue, count in issues.items():
            lines.append(f"| {_md_escape(issue)} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Captures",
            "",
            "| relative path | underlying | status | span s | snaps | quotes | opt trades | perp candles | okx trades | issues |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for capture in report.get("captures") or []:
        lines.append(
            "| {path} | {underlying} | {status} | {span} | {snaps} | {quotes} | {trades} | {perp} | {okx} | {issues} |".format(
                path=_md_escape(capture.get("relative_path")),
                underlying=_md_escape(capture.get("underlying")),
                status=_md_escape(capture.get("status")),
                span=capture.get("capture_span_seconds"),
                snaps=capture.get("n_surface_snapshots"),
                quotes=capture.get("n_surface_quotes"),
                trades=capture.get("n_option_trades"),
                perp=capture.get("n_perp_candles"),
                okx=capture.get("n_okx_perp_trades"),
                issues=_md_escape(", ".join(capture.get("issues") or [])),
            )
        )
    forward = report.get("forward_capture") or {}
    lines.extend(
        [
            "",
            "## Forward capture",
            "",
            f"- Directory: `{(forward.get('capture_dir') or '')}`",
            f"- File count: `{forward.get('file_count')}`",
            f"- All OK: `{forward.get('all_ok')}`",
            f"- Statuses: `{', '.join(forward.get('statuses') or [])}`",
            "",
            "Run `python3 scripts/eval186_forward_data_preflight.py` for the authoritative EVAL-186 forward-data verdict.",
            "",
        ]
    )
    return "\n".join(lines)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def write_rolling(report: Dict[str, Any]) -> Tuple[Path, Path]:
    _atomic_write(ROLLING_JSON, json.dumps(report, indent=2, default=str) + "\n")
    _atomic_write(ROLLING_MD, build_markdown(report))
    return ROLLING_JSON, ROLLING_MD


def write_sealed(report: Dict[str, Any]) -> Tuple[Path, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = RS_DIR / f"{REPORT_ID}_{stamp}.json"
    md_path = RS_DIR / f"{REPORT_ID}_{stamp}.md"
    _atomic_write(json_path, json.dumps(report, indent=2, default=str) + "\n")
    _atomic_write(md_path, build_markdown(report))
    return json_path, md_path


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="EVAL-187 real-data readiness audit (non-verdict).")
    parser.add_argument("--capture-root", default=str(DATA_DIR))
    parser.add_argument("--forward-capture-dir", default=str(FORWARD_CAPTURE_DIR))
    parser.add_argument("--execute", action="store_true", help="write the rolling readiness JSON/MD")
    parser.add_argument("--no-write", action="store_true", help="compute and print; write nothing")
    parser.add_argument("--seal", action="store_true", help="also write a timestamped audit artifact")
    args = parser.parse_args(argv)

    report = build_report(
        capture_root=Path(args.capture_root),
        forward_dir=Path(args.forward_capture_dir),
    )
    if args.execute and not args.no_write:
        json_path, md_path = write_rolling(report)
        report["rolling_json"] = str(json_path)
        report["rolling_md"] = str(md_path)
    if args.seal:
        json_path, md_path = write_sealed(report)
        report["sealed_json"] = str(json_path)
        report["sealed_md"] = str(md_path)
    print(json.dumps(report, indent=2, default=str))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())