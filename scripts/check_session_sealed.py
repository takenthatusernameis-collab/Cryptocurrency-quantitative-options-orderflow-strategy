#!/usr/bin/env python3
"""Session seal gate: fail unless a NEW artifact exists for this task.

Usage::

    python3 scripts/check_session_sealed.py \
        --task-id "INIT-2026-11-14T22:17:56Z-EVAL-43-ORDERFLOW-FULL-ROSTER-META" \
        --glob "EVAL_43_*"

The task id must contain an ISO-8601 UTC timestamp (e.g. ``...T22:17:56Z...``).
The gate passes only when at least one file in ``research_state/`` matches the
glob and embeds a stamp (``YYYYMMDDTHHMMSSZ``) at or after that timestamp. This
makes a handoff-only or silent session fail loudly instead of stalling.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research_state"

_ISO_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)")
_STAMP_RE = re.compile(r"(\d{8}T\d{6}(?:\d+)?Z)")


def _to_stamp(iso_ts: str) -> str:
    text = iso_ts.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--glob", required=True)
    ap.add_argument("--require-glob", action="append", default=[],
                    help="additional glob (repeatable); at least one file matching EACH must "
                         "exist with a stamp >= the task timestamp (AND semantics). Use this to "
                         "force a verdict artifact so an acquisition-only artifact cannot satisfy "
                         "the gate.")
    ap.add_argument("--require-any-glob", action="append", default=[],
                    help="group of alternative globs (repeatable); at least one file matching "
                         "AT LEAST ONE glob in the group must exist with a stamp >= the task "
                         "timestamp (OR semantics). Use for alternative verdict kinds, e.g. "
                         "EVAL_49_ETH_CROSS_VENUE_COMBINED_* OR EVAL_49_BLOCKED_*.")
    args = ap.parse_args(argv)

    iso = _ISO_RE.search(args.task_id)
    if not iso:
        print("FAIL: task id has no ISO-8601 UTC timestamp", file=sys.stderr)
        return 2
    floor = _to_stamp(iso.group(1))

    if not OUT_DIR.is_dir():
        print(f"FAIL: {OUT_DIR} does not exist", file=sys.stderr)
        return 2

    def _match(pattern: str) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for path in sorted(OUT_DIR.glob(pattern)):
            if not path.is_file():
                continue
            stamps = _STAMP_RE.findall(path.name)
            if not stamps:
                continue
            if max(stamps) >= floor:
                out.append((path.name, max(stamps)))
        return out

    matched = _match(args.glob)

    if not matched:
        print(
            f"FAIL: no artifact matching {args.glob!r} with stamp >= {floor} in {OUT_DIR}",
            file=sys.stderr,
        )
        return 1

    for name, stamp in matched:
        print(f"OK: {name} (stamp {stamp} >= {floor})")

    # Enforce any additional required globs (e.g. a verdict, not just acquisition).
    for req in args.require_glob:
        req_matches = _match(req)
        if not req_matches:
            print(
                f"FAIL: no artifact matching required {req!r} with stamp >= {floor} in {OUT_DIR} "
                f"(an acquisition/handoff-only artifact is not enough)",
                file=sys.stderr,
            )
            return 1
        for name, stamp in req_matches:
            print(f"OK (required): {name} (stamp {stamp} >= {floor})")

    # Enforce an OR group of required globs (e.g. COMBINED verdict OR BLOCKED).
    if args.require_any_glob:
        group_hits: list[tuple[str, str]] = []
        for pat in args.require_any_glob:
            group_hits.extend(_match(pat))
        if not group_hits:
            print(
                "FAIL: no artifact matching any of required "
                f"{args.require_any_glob!r} with stamp >= {floor} in {OUT_DIR} "
                "(an acquisition/handoff-only artifact is not enough)",
                file=sys.stderr,
            )
            return 1
        for name, stamp in group_hits:
            print(f"OK (required-any): {name} (stamp {stamp} >= {floor})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())