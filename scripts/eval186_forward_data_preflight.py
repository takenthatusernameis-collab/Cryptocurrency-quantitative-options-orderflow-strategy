#!/usr/bin/env python3
"""EVAL-186 FORWARD-DATA PREFLIGHT (anti-avoidance gate).

This is the MANDATORY first heavy-work check for every session while EVAL-186
(TRACK A fresh-window replication) is sealed ``BLOCKED`` for lack of forward real
data. It deterministically answers one question:

    "Is a floor-compliant, strictly-forward, disjoint capture now ACQUIRABLE?
     If so, what exact acquisition command produces it?"

A future agent may NOT claim "there is no on-charter heavy work to do" without
running this script and showing its output. The script reuses the sealed runner's
own constants and helpers (``scripts.eval186_track_a_fresh_window_replication``),
so it can never disagree with the runner about the floor, the disjointness rule,
the previous/sealed windows, or the earliest viable forward window end.

Verdicts (printed as JSON, exit code in parentheses):

* ``READY_TO_ACQUIRE`` (0)  — real forward data now covers a floor-compliant
  strictly-forward window; ``acquire_command`` is the exact
  ``scripts/eval60_acquire_three_way.py`` invocation to run, followed by the
  runner ``--no-write`` check and the ``eval186_phaseb_gate.py --execute`` seal.
  Use ``--end`` = the suggested end (or any later strictly-forward end that is
  disjoint from both sealed windows).

* ``WAIT_FORWARD_DATA`` (10) — forward real data is still insufficient. The
  script prints the runner's ``earliest_forward_capture_end`` (the first end
  that guarantees >= MIN_CAPTURE_SPAN_SECONDS of perp span after the previous
  window), the wall-clock seconds remaining, and the exact acquire command to
  run once that time is reached. Waiting is a measured fact, not an excuse.

* ``BLOCKED_NON_DISJOINT`` (1) / ``BLOCKED_NO_CAPTURE`` (1) — the capture on
  disk is non-empty but non-disjoint or missing an underlying; this is a real
  blocker (never ``NO-GO``) and must be resolved before acquisition.

This script never writes captures, never seals, and never weakens the EVAL-64
floor. It only reports. The heavy compute + seal remains
``eval186_track_a_fresh_window_replication.py`` + ``eval186_phaseb_gate.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Reuse the sealed runner's own constants and helpers so this preflight can never
# drift from the runner about the floor / disjointness / windows.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
sys.path.insert(0, str(_REPO_ROOT))

# Self-bootstrap runtime deps so `python3 scripts/eval186_forward_data_preflight.py`
# works without a PYTHONPATH=.venv-deps prefix (the runner imports numpy/pandas/scipy).
# Mirrors the driver's _child_env() trap fix; deps are git-ignored, not in checkout.
try:  # pragma: no cover - import-side bootstrap
    import numpy  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    _deps = _REPO_ROOT / ".venv-deps"
    if _deps.is_dir():
        sys.path.insert(0, str(_deps))

import scripts.eval186_track_a_fresh_window_replication as e186  # noqa: E402


EXIT_READY = 0
EXIT_BLOCKED = 1
EXIT_WAIT = 10


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime:
    return e186._parse_iso(value)


def _iso(dt: datetime) -> str:
    return e186._iso(dt)


def _load_captures(capture_dir: str) -> List[Dict[str, Any]]:
    """Return one capture per underlying (BTC, ETH) using the runner's loader."""
    return e186._select_captures(capture_dir)


def _build_acquire_command(end_iso: str, capture_dir: str, out_dir: str) -> List[str]:
    """Exact acquisition command for a floor-compliant forward window."""
    return [
        "python3",
        "scripts/eval60_acquire_three_way.py",
        "--underlying",
        "BTC",
        "--underlying",
        "ETH",
        "--days",
        str(float(e186.ACQUIRE_DAYS)),
        "--end",
        end_iso,
        "--max-per-expiry",
        "30",
        "--out-dir",
        out_dir,
        "--seal",
    ]


def _followup_commands(out_dir: str) -> List[str]:
    return [
        "PYTHONPATH=.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py "
        f"--capture-dir {out_dir} --no-write",
        "python3 scripts/eval186_phaseb_gate.py --execute",
    ]


def _seconds_until(target: datetime, now: datetime) -> float:
    return max(0.0, (target - now).total_seconds())


def build_report(capture_dir: str, out_dir: str, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or _utc_now()
    earliest_end = _parse_iso(e186.EARLIEST_FORWARD_CAPTURE_END)
    prev_end = _parse_iso(e186.PREVIOUS_WINDOW_END)
    span_floor = float(e186.MIN_CAPTURE_SPAN_SECONDS)

    has_capture = e186._has_real_capture(Path(capture_dir))
    captures = _load_captures(capture_dir) if has_capture else []

    per_underlying: List[Dict[str, Any]] = []
    floor_ok = bool(captures) and has_capture
    disjoint_ok = True
    missing: List[str] = []
    present_underlyings = {str(c.get("underlying", "")).upper() for c in captures}

    for u in e186.UNDERLYINGS:
        if u not in present_underlyings:
            missing.append(u)
            disjoint_ok = False
            floor_ok = False
            per_underlying.append(
                {
                    "underlying": u,
                    "present": False,
                    "floor_ok": False,
                    "disjointness_ok": False,
                    "reason": "missing_underlying",
                }
            )
            continue
        cap = next(c for c in captures if str(c.get("underlying", "")).upper() == u)
        floor = e186._floor_summary(cap)
        disj = e186.check_forward_disjointness(cap)
        floor_ok = floor_ok and bool(floor.get("ok", False))
        disjoint_ok = disjoint_ok and bool(disj.get("ok", False))
        per_underlying.append(
            {
                "underlying": u,
                "present": True,
                "window": disj.get("capture_window"),
                "capture_span_seconds": disj.get("capture_span_seconds"),
                "starts_after_previous": disj.get("starts_after_previous"),
                "disjointness_ok": bool(disj.get("ok", False)),
                "disjointness_reason": disj.get("reason"),
                "floor_ok": bool(floor.get("ok", False)),
                "n_surface_snapshots": floor.get("n_surface_snapshots"),
                "n_surface_bars_5m": floor.get("n_surface_bars_5m"),
                "n_option_trades": floor.get("n_option_trades"),
                "n_of_bars_5m": floor.get("n_of_bars_5m"),
                "n_perp_candles": floor.get("n_perp_candles"),
                "perp_span_seconds": floor.get("perp_span_seconds"),
                "n_perp_bars_5m": floor.get("n_perp_bars_5m"),
                "n_common_bars_5m": floor.get("n_common_bars_5m"),
                "checks": floor.get("checks"),
            }
        )

    secs_remaining = _seconds_until(earliest_end, now)
    now_past_earliest = now >= earliest_end

    # The acquire end is the earliest viable forward end (or "now-ish" once we are
    # past it; a later strictly-forward end is also fine, but earliest is safest).
    suggested_end = _iso(earliest_end) if not now_past_earliest else _iso(
        prev_end.replace(microsecond=0)
        if False
        else now
    )
    acquire_command = _build_acquire_command(suggested_end, capture_dir, out_dir)
    followup = _followup_commands(out_dir)

    if not has_capture or missing:
        verdict = "BLOCKED_NO_CAPTURE"
        exit_code = EXIT_BLOCKED
        action = (
            "Acquire a fresh strictly-forward capture (see acquire_command). "
            "Under-floor/non-disjoint/missing data is BLOCKED, never NO-GO."
        )
    elif not disjoint_ok:
        verdict = "BLOCKED_NON_DISJOINT"
        exit_code = EXIT_BLOCKED
        action = (
            "On-disk capture overlaps a sealed/previous window or is missing an "
            "underlying. Acquire a strictly-forward capture (see acquire_command)."
        )
    elif floor_ok and disjoint_ok:
        verdict = "READY_TO_ACQUIRE"
        exit_code = EXIT_READY
        action = (
            "Floor + disjointness now satisfied on disk. Run acquire_command, then "
            "followup commands (runner --no-write, then eval186_phaseb_gate.py --execute)."
        )
    else:
        # Under-floor but disjoint and present: the expected WAIT state.
        verdict = "WAIT_FORWARD_DATA"
        exit_code = EXIT_WAIT
        action = (
            "Forward real data still under the EVAL-64 floor. This is a measured "
            "wall-clock wait, not a missing-data excuse. Re-run this preflight once "
            "now >= earliest_forward_capture_end, then run acquire_command + followup."
        )

    return {
        "script": "eval186_forward_data_preflight",
        "generated_at": _iso(now),
        "capture_dir": capture_dir,
        "out_dir": out_dir,
        "verdict": verdict,
        "exit_code": exit_code,
        "action": action,
        "has_capture": bool(has_capture),
        "missing_underlyings": missing,
        "floor_ok": bool(floor_ok),
        "disjointness_ok": bool(disjoint_ok),
        "floor_and_disjoint_ok": bool(floor_ok and disjoint_ok),
        "previous_window_end": e186.PREVIOUS_WINDOW_END,
        "earliest_forward_capture_end": e186.EARLIEST_FORWARD_CAPTURE_END,
        "min_capture_span_seconds": span_floor,
        "acquire_days": float(e186.ACQUIRE_DAYS),
        "now": _iso(now),
        "now_past_earliest_forward_end": bool(now_past_earliest),
        "seconds_until_earliest_forward_end": round(secs_remaining, 3),
        "suggested_acquire_end": suggested_end,
        "acquire_command": acquire_command,
        "followup_commands": followup,
        "per_underlying": per_underlying,
        "note": (
            "EVAL-186 is sealed BLOCKED (append-only). This preflight only reports "
            "forward-data sufficiency; it never seals, writes captures, or weakens the floor."
        ),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="EVAL-186 forward-data preflight (anti-avoidance gate).")
    parser.add_argument(
        "--capture-dir",
        default=e186.DEFAULT_CAPTURE_DIR,
        help="Directory holding three_way_{BTC,ETH}_*.json (default: %(default)s).",
    )
    parser.add_argument(
        "--out-dir",
        default=e186.DEFAULT_CAPTURE_DIR,
        help="Target --out-dir for the suggested acquisition command (default: %(default)s).",
    )
    args = parser.parse_args(argv)

    report = build_report(args.capture_dir, args.out_dir)
    print(json.dumps(report, indent=2))
    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())