#!/usr/bin/env python3
"""EVAL-186 TRACK A fresh-window replication of the dual traded-form NO-GO.

The repository charter is crypto options surface + options order-flow -> tradeable,
net-of-cost alpha on real public data. EVAL-69 (order flow) and EVAL-184 (surface)
are sealed NO-GO CONFIRMED (PASS) results on the EVAL-84/185 capture. This campaign
tests temporal robustness by running the same two pre-registered traded-form
families, with ``write=False``, on a new strictly forward BTC+ETH capture.

The replication is BLOCKED unless both underlyings meet the EVAL-64 floor and both
capture windows are disjoint from the sealed EVAL-64/65 window and the previous
EVAL-84/185 window. Under-floor or overlapping data is never reported as NO-GO.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64  # noqa: E402
import scripts.eval67_btc_oflow_tox_rv_oos as e67  # noqa: E402
import scripts.eval69_pooled_btc_eth_oflow_tox_rv_traded_oos as e69  # noqa: E402
import scripts.eval184_surface_traded_netofcost_oos as e184  # noqa: E402

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_COMBINED"
PREREG_ID = "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_PREREGISTRATION"
BLOCKED_ID = "EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED"
PREREG_GLOB = PREREG_ID + "_*"
COMBINED_GLOB = REPORT_ID + "_*"
BLOCKED_GLOB = BLOCKED_ID + "_*"

DEFAULT_CAPTURE_DIR = "data/raw/eval185cap"
DEFAULT_TASK_LABEL = "EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION"
UNDERLYINGS: Tuple[str, ...] = ("BTC", "ETH")
MIN_UNDERLYINGS = len(UNDERLYINGS)
MIN_POOLED_RETURNS = 790

SEALED_WINDOW_START = e67.SEALED_BTC_WINDOW_START
SEALED_WINDOW_END = e67.SEALED_BTC_WINDOW_END
PREVIOUS_CAPTURE_DIR = "data/raw/eval84cap"
PREVIOUS_WINDOW_START = "2026-11-18T13:58:43Z"
PREVIOUS_WINDOW_END = "2026-11-22T06:46:43Z"
ACQUIRE_DAYS = 3.7
MIN_CAPTURE_SPAN_SECONDS = 300000.0
RECOMMENDED_CAPTURE_END = "2026-11-26T00:00:00Z"

_underlying_floor_strict = e64._underlying_floor_strict

CODE_PATHS: Tuple[str, ...] = (
    "scripts/eval60_acquire_three_way.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval64_orderflow_realized_vol_markpath_feasible.py",
    "scripts/eval67_btc_oflow_tox_rv_oos.py",
    "scripts/eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
    "scripts/eval184_surface_traded_netofcost_oos.py",
    "scripts/eval186_track_a_fresh_window_replication.py",
    "scripts/eval186_phaseb_gate.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval186_track_a_fresh_window_replication.py "
    "scripts/eval186_phaseb_gate.py "
    "tests/test_eval186_track_a_fresh_window_replication.py",
    "python3 -m pytest -q tests/test_eval186_track_a_fresh_window_replication.py",
    "python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
    "--days 3.7 --end 2026-11-26T00:00:00Z --max-per-expiry 30 "
    "--out-dir data/raw/eval185cap --seal",
    "python3 scripts/eval186_track_a_fresh_window_replication.py "
    "--capture-dir data/raw/eval185cap --no-write",
    "python3 scripts/eval186_track_a_fresh_window_replication.py "
    "--capture-dir data/raw/eval185cap --seal --task-label "
    "EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION",
    "python3 scripts/eval186_phaseb_gate.py --execute",
)


class NoRealCaptureError(RuntimeError):
    """Raised when sealing is attempted before a real BTC+ETH capture exists."""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def earliest_forward_capture_end() -> str:
    end = _parse_iso(PREVIOUS_WINDOW_END) + timedelta(days=ACQUIRE_DAYS)
    return _iso(end)


EARLIEST_FORWARD_CAPTURE_END = earliest_forward_capture_end()


def _capture_window(capture: Dict[str, Any]) -> Tuple[Optional[datetime], Optional[datetime]]:
    try:
        start = _parse_iso(str(capture.get("window_start")))
        end = _parse_iso(str(capture.get("window_end")))
    except (TypeError, ValueError):
        return None, None
    return start, end


def _overlap_seconds(
    start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime
) -> float:
    return max(0.0, (min(end_a, end_b) - max(start_a, start_b)).total_seconds())


def check_forward_disjointness(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = str(capture.get("underlying", "?"))
    start, end = _capture_window(capture)
    sealed_start = _parse_iso(SEALED_WINDOW_START)
    sealed_end = _parse_iso(SEALED_WINDOW_END)
    previous_start = _parse_iso(PREVIOUS_WINDOW_START)
    previous_end = _parse_iso(PREVIOUS_WINDOW_END)
    if start is None or end is None:
        return {
            "underlying": inst,
            "ok": False,
            "reason": "missing_capture_window",
            "capture_window": [None, None],
            "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
            "previous_window": [PREVIOUS_WINDOW_START, PREVIOUS_WINDOW_END],
            "sealed_overlap_seconds": None,
            "previous_overlap_seconds": None,
            "starts_after_previous": False,
            "capture_span_seconds": None,
            "meets_min_span": False,
        }
    sealed_overlap = _overlap_seconds(start, end, sealed_start, sealed_end)
    previous_overlap = _overlap_seconds(start, end, previous_start, previous_end)
    starts_after_previous = start >= previous_end and end > previous_end
    span = (end - start).total_seconds()
    meets_min_span = span >= MIN_CAPTURE_SPAN_SECONDS
    ok = bool(
        sealed_overlap <= 0.0
        and previous_overlap <= 0.0
        and starts_after_previous
        and meets_min_span
    )
    if ok:
        reason = "strictly_forward_disjoint"
    elif sealed_overlap > 0.0:
        reason = "overlaps_sealed_eval64_window"
    elif previous_overlap > 0.0:
        reason = "overlaps_eval84_eval185_window"
    elif not starts_after_previous:
        reason = "not_after_eval84_eval185_window"
    else:
        reason = "below_minimum_capture_span"
    return {
        "underlying": inst,
        "ok": ok,
        "reason": reason,
        "capture_window": [_iso(start), _iso(end)],
        "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
        "previous_window": [PREVIOUS_WINDOW_START, PREVIOUS_WINDOW_END],
        "sealed_overlap_seconds": round(sealed_overlap, 3),
        "previous_overlap_seconds": round(previous_overlap, 3),
        "starts_after_previous": bool(starts_after_previous),
        "capture_span_seconds": round(span, 3),
        "meets_min_span": bool(meets_min_span),
    }


def _select_captures(capture_dir: str) -> List[Dict[str, Any]]:
    captures = e184._select_one_capture_per_underlying(
        e61._capture_inventory(capture_dir)
    )
    return [c for c in captures if str(c.get("underlying", "")).upper() in UNDERLYINGS]


def _has_real_capture(capture_dir: Path) -> bool:
    return any(capture_dir.glob("three_way_BTC_*.json")) and any(
        capture_dir.glob("three_way_ETH_*.json")
    )


def _floor_summary(capture: Dict[str, Any]) -> Dict[str, Any]:
    floor = _underlying_floor_strict(capture)
    return {
        "underlying": floor.get("underlying", "?"),
        "n_surface_snapshots": floor.get("n_surface_snapshots", 0),
        "n_surface_instruments": floor.get("n_surface_instruments", 0),
        "n_surface_bars_5m": floor.get("n_surface_bars_5m", 0),
        "n_option_trades": floor.get("n_option_trades", 0),
        "n_of_instruments": floor.get("n_of_instruments", 0),
        "of_span_seconds": float(floor.get("of_span_seconds", 0.0) or 0.0),
        "n_of_bars_5m": floor.get("n_of_bars_5m", 0),
        "n_perp_candles": floor.get("n_perp_candles", 0),
        "perp_span_seconds": float(floor.get("perp_span_seconds", 0.0) or 0.0),
        "n_perp_bars_5m": floor.get("n_perp_bars_5m", 0),
        "n_common_bars_5m": floor.get("n_common_bars_5m", 0),
        "checks": dict(floor.get("checks") or {}),
        "ok": bool(floor.get("ok", False)),
    }


def _family_summary(report: Dict[str, Any], family: str) -> Dict[str, Any]:
    pooled = dict(report.get("pooled") or {})
    return {
        "family": family,
        "source_report_id": report.get("report_id"),
        "verdict": report.get("verdict"),
        "floor_ok": bool(report.get("floor_ok", False)),
        "disjointness_ok": bool(report.get("disjointness_ok", False)),
        "floor_and_disjoint_ok": bool(report.get("floor_and_disjoint_ok", False)),
        "missing_underlyings": list(report.get("missing_underlyings") or []),
        "max_pooled_returns": pooled.get("max_pooled_returns", 0),
        "power_adequate": bool(pooled.get("power_adequate", False)),
        "min_pooled_returns": pooled.get("min_pooled_returns", MIN_POOLED_RETURNS),
        "pass_configs": list(pooled.get("pass_configs") or []),
        "bh_fdr_rejected": list((pooled.get("bh_fdr") or {}).get("rejected") or []),
        "per_config": list(report.get("per_config") or []),
        "errors": list(report.get("errors") or []),
    }


def _empty_family(family: str) -> Dict[str, Any]:
    return {
        "family": family,
        "source_report_id": None,
        "verdict": "BLOCKED",
        "floor_ok": False,
        "disjointness_ok": False,
        "floor_and_disjoint_ok": False,
        "missing_underlyings": list(UNDERLYINGS),
        "max_pooled_returns": 0,
        "power_adequate": False,
        "min_pooled_returns": MIN_POOLED_RETURNS,
        "pass_configs": [],
        "bh_fdr_rejected": [],
        "per_config": [],
        "errors": [],
    }


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-186",
        "title": "TRACK A fresh-window replication of the EVAL-69 order-flow and "
                 "EVAL-184 surface traded-form NO-GO results on a strictly forward "
                 "real BTC+ETH capture",
        "extends": "EVAL-69 and EVAL-184 (both family runners execute with write=False "
                   "on a new capture; neither sealed artifact is modified)",
        "supersedes": "nothing - this is a temporal robustness check of the dual "
                      "NO-GO, not a re-seal of either family",
        "capture_dir": str(capture_dir),
        "underlyings_required": list(UNDERLYINGS),
        "previous_capture_dir": PREVIOUS_CAPTURE_DIR,
        "previous_window": [PREVIOUS_WINDOW_START, PREVIOUS_WINDOW_END],
        "sealed_window": [SEALED_WINDOW_START, SEALED_WINDOW_END],
        "acquire_days": float(ACQUIRE_DAYS),
        "earliest_forward_capture_end": EARLIEST_FORWARD_CAPTURE_END,
        "recommended_capture_end": RECOMMENDED_CAPTURE_END,
        "min_capture_span_seconds": float(MIN_CAPTURE_SPAN_SECONDS),
        "families": {
            "order_flow": {
                "runner": "scripts.eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py",
                "write": False,
            },
            "surface": {
                "runner": "scripts.eval184_surface_traded_netofcost_oos.py",
                "write": False,
            },
        },
        "go_bar": (
            "GO CONFIRMED if either family independently returns GO CONFIRMED on the "
            "fresh forward capture. NO-GO CONFIRMED (PASS) only if both families "
            "return NO-GO CONFIRMED (PASS) and both are power adequate. "
            "INCONCLUSIVE (UNDERPOWERED) if neither is GO and either is underpowered. "
            "BLOCKED if an underlying is missing, the EVAL-64 floor fails, or the "
            "capture overlaps the sealed EVAL-64/65 window or the EVAL-84/185 window. "
            "Under-floor or non-disjoint data is never NO-GO."
        ),
        "floor": {
            "source": "EVAL-64 feasible floor reused verbatim (never weakened)",
            "min_underlyings": int(MIN_UNDERLYINGS),
            "checks": [
                "snapshots_ok",
                "surface_instruments_ok",
                "surface_bars_ok",
                "trades_ok",
                "of_instruments_ok",
                "of_span_ok",
                "of_bars_ok",
                "perp_bars_ok",
                "perp_span_ok",
                "common_overlap_ok",
            ],
        },
        "min_pooled_returns": int(MIN_POOLED_RETURNS),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _blocked_family_placeholders() -> Dict[str, Dict[str, Any]]:
    return {
        "order_flow": _empty_family("order_flow"),
        "surface": _empty_family("surface"),
    }


def run_eval186(
    *,
    capture_dir: str = DEFAULT_CAPTURE_DIR,
    write: bool = True,
    task_label: str = DEFAULT_TASK_LABEL,
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    if write and not _has_real_capture(capture_dir_abs):
        raise NoRealCaptureError(
            f"no real BTC+ETH capture found in {capture_dir_abs}; acquire a strictly "
            "forward capture before sealing EVAL-186"
        )

    captures = _select_captures(str(capture_dir_abs))
    present = {str(c.get("underlying", "")).upper() for c in captures}
    missing = [u for u in UNDERLYINGS if u not in present]
    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    forward_disjointness: Dict[str, Dict[str, Any]] = {}
    for cap in captures:
        inst = str(cap.get("underlying", "?"))
        per_underlying_floor[inst] = _floor_summary(cap)
        forward_disjointness[inst] = check_forward_disjointness(cap)

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and not missing
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )
    forward_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and not missing
        and forward_disjointness
        and all(v["ok"] for v in forward_disjointness.values())
    )

    errors: List[str] = []
    families: Dict[str, Dict[str, Any]] = _blocked_family_placeholders()
    if captures and not missing and floor_ok and forward_ok:
        try:
            order_report = e69.run_eval69(
                capture_dir=str(capture_dir_abs), write=False, task_label=task_label
            )
            families["order_flow"] = _family_summary(order_report, "order_flow")
            errors.extend(str(e) for e in (order_report.get("errors") or []))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"order_flow: {exc!r}")
        try:
            surface_report = e184.run_eval184(
                capture_dir=str(capture_dir_abs), write=False, task_label=task_label
            )
            families["surface"] = _family_summary(surface_report, "surface")
            errors.extend(str(e) for e in (surface_report.get("errors") or []))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"surface: {exc!r}")

    family_infra_ok = all(
        bool(families[name].get("floor_and_disjoint_ok", False))
        for name in ("order_flow", "surface")
    )
    infrastructure_ok = bool(floor_ok and forward_ok and family_infra_ok)
    go_families = [
        name
        for name in ("order_flow", "surface")
        if families[name].get("verdict") == "GO CONFIRMED"
    ]
    power_adequate = all(
        bool(families[name].get("power_adequate", False))
        for name in ("order_flow", "surface")
    )

    if not infrastructure_ok:
        verdict = "BLOCKED"
    elif go_families:
        verdict = "GO CONFIRMED"
    elif not power_adequate:
        verdict = "INCONCLUSIVE (UNDERPOWERED)"
    else:
        verdict = "NO-GO CONFIRMED (PASS)"

    protocol = build_protocol(capture_dir)
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict,
        "verdict_detail": (
            "fresh strictly-forward BTC+ETH replication of the EVAL-69 order-flow and "
            "EVAL-184 surface traded-form families; family runners executed with "
            "write=False and neither sealed family artifact was modified"
            if infrastructure_ok
            else "capture is missing an underlying, below the EVAL-64 floor, overlaps "
                 "the sealed EVAL-64/65 or EVAL-84/185 window, or a family could not "
                 "be evaluated; no GO/NO-GO verdict"
        ),
        "floor_ok": bool(floor_ok),
        "forward_disjointness_ok": bool(forward_ok),
        "floor_and_disjoint_ok": infrastructure_ok,
        "missing_underlyings": missing,
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(present),
        "protocol": protocol,
        "per_underlying_floor": per_underlying_floor,
        "forward_disjointness": forward_disjointness,
        "families": families,
        "pooled": {
            "go_families": go_families,
            "power_adequate": bool(power_adequate),
            "min_pooled_returns": int(MIN_POOLED_RETURNS),
            "family_verdicts": {
                name: families[name].get("verdict") for name in ("order_flow", "surface")
            },
        },
        "errors": errors,
    }

    if not write:
        return report

    if not list(OUT_DIR.glob(PREREG_GLOB)):
        e62._seal(PREREG_ID, _build_prereg(report), _build_prereg_md)

    if not infrastructure_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        return report

    e62._seal(REPORT_ID, report, _build_md)
    return report


def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The EVAL-69 order-flow and EVAL-184 surface traded-form NO-GO results "
            "are temporally robust on a strictly forward, floor-compliant BTC+ETH "
            "capture that does not overlap the sealed EVAL-64/65 or EVAL-84/185 "
            "windows. A GO in either family refutes the dual NO-GO; under-floor or "
            "overlapping data is BLOCKED and never NO-GO."
        ),
        "extends": p["extends"],
        "capture_dir": report["capture_dir"],
        "previous_window": p["previous_window"],
        "sealed_window": p["sealed_window"],
        "earliest_forward_capture_end": p["earliest_forward_capture_end"],
        "recommended_capture_end": p["recommended_capture_end"],
        "protocol": p,
    }


def _build_prereg_md(report: Dict[str, Any]) -> str:
    p = report["protocol"]
    lines = [
        f"# {PREREG_ID} - TRACK A fresh-window replication of the dual traded-form NO-GO",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Task: `{report['task']}`",
        f"- Hypothesis: {report['hypothesis']}",
        f"- Capture dir: `{report['capture_dir']}`",
        f"- Previous EVAL-84/185 window: `{PREVIOUS_WINDOW_START}` .. `{PREVIOUS_WINDOW_END}`",
        f"- Earliest strictly forward 3.7-day capture end: `{EARLIEST_FORWARD_CAPTURE_END}`",
        f"- Recommended acquisition end: `{RECOMMENDED_CAPTURE_END}`",
        "",
        "## Pre-declared replication families",
        "",
        "- Order flow: EVAL-69 runner, `write=False`, unchanged GO bar and power floor.",
        "- Surface: EVAL-184 runner, `write=False`, unchanged GO bar and power floor.",
        "- Neither sealed EVAL-69 nor EVAL-184 artifact is re-sealed or modified.",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor",
        "",
        "- EVAL-64 floor reused verbatim; both BTC and ETH required.",
        f"- Minimum pooled returns per family: {p['min_pooled_returns']}.",
        "",
        "## Acquisition",
        "",
        "```bash",
        "python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
        "--days 3.7 --end 2026-11-26T00:00:00Z --max-per-expiry 30 "
        "--out-dir data/raw/eval185cap --seal",
        "```",
        "",
    ]
    return "\n".join(lines) + "\n"


def _family_table(families: Dict[str, Dict[str, Any]]) -> List[str]:
    lines = [
        "| family | verdict | floor | power | max pooled | pass configs |",
        "|---|---|---|---|---|---|",
    ]
    for name in ("order_flow", "surface"):
        fam = families.get(name) or _empty_family(name)
        lines.append(
            f"| {name} | {fam.get('verdict')} | {fam.get('floor_and_disjoint_ok')} | "
            f"{fam.get('power_adequate')} | {fam.get('max_pooled_returns')} | "
            f"{fam.get('pass_configs')} |"
        )
    return lines


def _build_md(report: Dict[str, Any]) -> str:
    lines = [
        f"# {report['report_id']} - TRACK A fresh-window replication of the dual traded-form NO-GO",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Task: `{report['task']}`",
        f"- Verdict: **{report['verdict']}**",
        f"- Floor OK: {report['floor_ok']}",
        f"- Strictly-forward disjointness OK: {report['forward_disjointness_ok']}",
        f"- Missing underlyings: {report['missing_underlyings']}",
        f"- GO families: {report['pooled']['go_families']}",
        f"- Both families power adequate: {report['pooled']['power_adequate']}",
        "",
        "## Family replication",
        "",
    ]
    lines.extend(_family_table(report.get("families") or {}))
    lines.extend(["", "## Forward disjointness", "", "| underlying | ok | reason | capture window | previous overlap s | sealed overlap s |", "|---|---|---|---|---|---|"])
    for inst, row in (report.get("forward_disjointness") or {}).items():
        lines.append(
            f"| {inst} | {row.get('ok')} | {row.get('reason')} | "
            f"{row.get('capture_window')} | {row.get('previous_overlap_seconds')} | "
            f"{row.get('sealed_overlap_seconds')} |"
        )
    lines.extend(["", "## Per-underlying EVAL-64 floor", "", "| underlying | snaps | surf inst | 5m bars | trades | of inst | perp bars | perp span s | common 5m | ok |", "|---|---|---|---|---|---|---|---|---|---|"])
    for inst, row in (report.get("per_underlying_floor") or {}).items():
        lines.append(
            f"| {inst} | {row.get('n_surface_snapshots')} | {row.get('n_surface_instruments')} | "
            f"{row.get('n_surface_bars_5m')} | {row.get('n_option_trades')} | "
            f"{row.get('n_of_instruments')} | {row.get('n_perp_bars_5m')} | "
            f"{float(row.get('perp_span_seconds', 0.0) or 0.0):.0f} | "
            f"{row.get('n_common_bars_5m')} | {row.get('ok')} |"
        )
    if report.get("errors"):
        lines.extend(["", "## Errors", ""] + [f"- {e}" for e in report["errors"]])
    return "\n".join(lines) + "\n"


def _build_blocked_report(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "verdict": "BLOCKED",
        "capture_dir": report["capture_dir"],
        "underlyings": report.get("underlyings", []),
        "missing_underlyings": report.get("missing_underlyings", []),
        "floor_ok": report.get("floor_ok", False),
        "forward_disjointness_ok": report.get("forward_disjointness_ok", False),
        "per_underlying_floor": report.get("per_underlying_floor", {}),
        "forward_disjointness": report.get("forward_disjointness", {}),
        "families": report.get("families", {}),
        "errors": report.get("errors", []),
        "note": "measured BLOCKED; not NO-GO",
    }


def _build_blocked_md(report: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} - TRACK A fresh-window replication BLOCKED",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Task: `{report['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{report['capture_dir']}`",
        f"- Floor OK: {report.get('floor_ok', False)}",
        f"- Strictly-forward disjointness OK: {report.get('forward_disjointness_ok', False)}",
        "",
        "The capture is missing a required underlying, is below the pre-registered "
        "EVAL-64 feasible floor, or overlaps the sealed EVAL-64/65 or EVAL-84/185 "
        "window. No GO/NO-GO verdict is emitted.",
        "",
        "## Forward disjointness",
        "",
    ]
    for inst, row in (report.get("forward_disjointness") or {}).items():
        lines.append(f"- {inst}: {json.dumps(row, sort_keys=True)}")
    lines.extend(["", "## Per-underlying floor", ""])
    for inst, row in (report.get("per_underlying_floor") or {}).items():
        lines.append(f"- {inst}: {json.dumps(row.get('checks') or {}, sort_keys=True)}")
    lines.append("")
    return "\n".join(lines) + "\n"


def build_prereg_document(
    *, task_label: str = DEFAULT_TASK_LABEL, capture_dir: str = DEFAULT_CAPTURE_DIR
) -> Dict[str, Any]:
    report = {
        "generated_at": _utc_now_iso(),
        "task": task_label,
        "capture_dir": str(capture_dir),
        "protocol": build_protocol(capture_dir),
    }
    return _build_prereg(report)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="EVAL-186 TRACK A fresh-window replication of the dual traded-form NO-GO"
    )
    parser.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    parser.add_argument("--no-write", action="store_true", help="compute and print; seal nothing")
    parser.add_argument("--seal", action="store_true", help="seal prereg and combined/blocked")
    parser.add_argument("--task-label", default=DEFAULT_TASK_LABEL)
    parser.add_argument("--emit-prereg", action="store_true")
    args = parser.parse_args(argv)

    if args.emit_prereg:
        prereg = build_prereg_document(
            task_label=args.task_label, capture_dir=args.capture_dir
        )
        written = e62._seal(PREREG_ID, prereg, _build_prereg_md)
        print(json.dumps({"prereg_id": PREREG_ID, "written": written}, indent=2))
        return 0

    write = not args.no_write
    try:
        report = run_eval186(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except NoRealCaptureError as exc:
        print(json.dumps({"verdict": "NOT_SEALED", "reason": str(exc)}, indent=2))
        return 2
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report(
                {
                    "generated_at": _utc_now_iso(),
                    "task": args.task_label,
                    "capture_dir": args.capture_dir,
                    "underlyings": [],
                    "missing_underlyings": list(UNDERLYINGS),
                    "floor_ok": False,
                    "forward_disjointness_ok": False,
                    "per_underlying_floor": {},
                    "forward_disjointness": {},
                    "families": _blocked_family_placeholders(),
                    "errors": [repr(exc)],
                }
            )
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(
        json.dumps(
            {
                "verdict": report.get("verdict"),
                "floor_ok": report.get("floor_ok"),
                "forward_disjointness_ok": report.get("forward_disjointness_ok"),
                "missing_underlyings": report.get("missing_underlyings"),
                "underlyings": report.get("underlyings"),
                "family_verdicts": report.get("pooled", {}).get("family_verdicts"),
                "go_families": report.get("pooled", {}).get("go_families"),
                "power_adequate": report.get("pooled", {}).get("power_adequate"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())