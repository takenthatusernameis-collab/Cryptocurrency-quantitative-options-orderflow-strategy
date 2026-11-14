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
    args = ap.parse_args(argv)

    iso = _ISO_RE.search(args.task_id)
    if not iso:
        print("FAIL: task id has no ISO-8601 UTC timestamp", file=sys.stderr)
        return 2
    floor = _to_stamp(iso.group(1))

    if not OUT_DIR.is_dir():
        print(f"FAIL: {OUT_DIR} does not exist", file=sys.stderr)
        return 2

    matched: list[tuple[str, str]] = []
    for path in sorted(OUT_DIR.glob(args.glob)):
        if not path.is_file():
            continue
        stamps = _STAMP_RE.findall(path.name)
        if not stamps:
            continue
        if max(stamps) >= floor:
            matched.append((path.name, max(stamps)))

    if not matched:
        print(
            f"FAIL: no artifact matching {args.glob!r} with stamp >= {floor} in {OUT_DIR}",
            file=sys.stderr,
        )
        return 1

    for name, stamp in matched:
        print(f"OK: {name} (stamp {stamp} >= {floor})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())