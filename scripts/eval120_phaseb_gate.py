#!/usr/bin/env python3
"""EVAL-120 phase-B gate: verifies the seal artifacts exist and are well-formed.

This gate is the *only* authority for whether EVAL-120 is SEALED. The runner
script is NOT the seal authority — the runner writes artifacts, this gate
verifies them.

EVAL-120: cross-sectional term-ratio basis (ETH - BTC) -> forward relative
realized return skewness spread predictiveness (Spearman rank IC).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77  # noqa: E402

REPORT_ID = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED"
PREREG_ID = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION"
BLOCKED_ID = "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_BLOCKED"

# The floor for EVAL-120 is the EVAL-77 surface basis floor (identity).
FLOOR: Dict[str, Any] = e77.FLOOR

# Required fields in the COMBINED report (must be present and non-null).
REQUIRED_COMBINED_FIELDS: Tuple[str, ...] = (
    "report_id",
    "generated_at",
    "task",
    "verdict",
    "verdict_detail",
    "floor_ok",
    "capture_dir",
    "underlyings",
    "floor",
    "campaign_floor",
    "protocol",
    "per_config",
    "summary",
    "pooled",
    "errors",
)

# Required fields in the PREREG report.
REQUIRED_PREREG_FIELDS: Tuple[str, ...] = (
    "prereg_id",
    "generated_at",
    "task",
    "hypothesis",
    "extends",
    "protocol",
    "capture_dir",
    "floor",
)

# Required fields in the BLOCKED report.
REQUIRED_BLOCKED_FIELDS: Tuple[str, ...] = (
    "report_id",
    "generated_at",
    "task",
    "verdict",
    "verdict_detail",
    "floor_ok",
    "capture_dir",
    "underlyings",
    "floor",
    "campaign_floor",
    "errors",
)

# Allowed verdict values.
ALLOWED_VERDICTS = ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)", "BLOCKED")

# The floor for EVAL-120 is the EVAL-77 surface basis floor (identity).
REQUIRED_FLOOR_KEYS: Tuple[str, ...] = (
    "min_underlyings",
    "min_aligned_common_bars",
    "min_usable_pairs_per_config",
    "note",
)

# Cross-sectional legs must match EVAL-77 convention.
EXPECTED_BASELINE = "BTC"
EXPECTED_RELATIVE = "ETH"

# Pre-registration timestamp floor (the task was registered at this time).
# The gate will verify prereg is not older than this (prevents back-dating).
PREREG_FLOOR_TS = "2026-11-19T06:10:00Z"  # updated per session


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _find_artifact(pattern: str) -> Optional[Path]:
    """Find the newest artifact matching pattern in research_state/."""
    matches = list(ROOT.glob(f"research_state/{pattern}"))
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _verify_prereg(prereg_path: Path) -> Tuple[bool, List[str]]:
    """Verify the preregistration artifact."""
    errors: List[str] = []
    data = _load_json(prereg_path)
    if data is None:
        errors.append(f"PREREG: invalid JSON or unreadable: {prereg_path}")
        return False, errors

    # Required fields.
    for field in REQUIRED_PREREG_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"PREREG: missing required field '{field}'")

    # ID match.
    if data.get("prereg_id") != PREREG_ID:
        errors.append(f"PREREG: prereg_id mismatch: expected {PREREG_ID}, got {data.get('prereg_id')}")

    # Hypothesis present and non-empty.
    hyp = data.get("hypothesis", "")
    if not hyp or len(hyp) < 50:
        errors.append("PREREG: hypothesis missing or too short")

    # Protocol structure.
    proto = data.get("protocol", {})
    if not proto:
        errors.append("PREREG: protocol missing or empty")
    else:
        # Cross-section legs.
        cs = proto.get("cross_section", {})
        if cs.get("baseline") != EXPECTED_BASELINE:
            errors.append(f"PREREG: cross_section.baseline must be '{EXPECTED_BASELINE}', got {cs.get('baseline')}")
        if cs.get("relative") != EXPECTED_RELATIVE:
            errors.append(f"PREREG: cross_section.relative must be '{EXPECTED_RELATIVE}', got {cs.get('relative')}")

        # Term signals.
        if proto.get("term_signals") != ["term_ratio"]:
            errors.append(f"PREREG: term_signals must be ['term_ratio'], got {proto.get('term_signals')}")

        # Grid and horizons from EVAL-77.
        if proto.get("bar_seconds_grid") != [60.0, 300.0]:
            errors.append(f"PREREG: bar_seconds_grid mismatch: {proto.get('bar_seconds_grid')}")
        if proto.get("forward_horizons_bars") != [6, 24, 72]:
            errors.append(f"PREREG: forward_horizons_bars mismatch: {proto.get('forward_horizons_bars')}")

        # Stats.
        stats = proto.get("stats", {})
        if stats.get("permutation_perms") != 1000:
            errors.append(f"PREREG: permutation_perms mismatch: {stats.get('permutation_perms')}")
        if stats.get("bootstrap_resamples") != 1000:
            errors.append(f"PREREG: bootstrap_resamples mismatch: {stats.get('bootstrap_resamples')}")
        if stats.get("bootstrap_block") != 2:
            errors.append(f"PREREG: bootstrap_block mismatch: {stats.get('bootstrap_block')}")
        if stats.get("fdr_alpha") != 0.1:
            errors.append(f"PREREG: fdr_alpha mismatch: {stats.get('fdr_alpha')}")
        if stats.get("seed") != 42:
            errors.append(f"PREREG: seed mismatch: {stats.get('seed')}")
        if stats.get("zwindow") != 20:
            errors.append(f"PREREG: zwindow mismatch: {stats.get('zwindow')}")
        if stats.get("min_usable_pairs_per_config") != 120:
            errors.append(f"PREREG: min_usable_pairs_per_config mismatch: {stats.get('min_usable_pairs_per_config')}")

    # Floor present.
    floor = data.get("floor", {})
    for key in REQUIRED_FLOOR_KEYS:
        if key not in floor:
            errors.append(f"PREREG: floor missing required key '{key}'")

    # Timestamp floor check (prevent back-dating).
    gen_ts = data.get("generated_at", "")
    if gen_ts and gen_ts < PREREG_FLOOR_TS:
        errors.append(f"PREREG: generated_at {gen_ts} is before pre-registration floor {PREREG_FLOOR_TS}")

    return len(errors) == 0, errors


def _verify_combined(combined_path: Path) -> Tuple[bool, List[str]]:
    """Verify the combined (COMPLETED or BLOCKED) artifact."""
    errors: List[str] = []
    data = _load_json(combined_path)
    if data is None:
        errors.append(f"COMBINED: invalid JSON or unreadable: {combined_path}")
        return False, errors

    # Required fields.
    for field in REQUIRED_COMBINED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"COMBINED: missing required field '{field}'")

    # ID match.
    if data.get("report_id") != REPORT_ID:
        errors.append(f"COMBINED: report_id mismatch: expected {REPORT_ID}, got {data.get('report_id')}")

    # Verdict.
    verdict = data.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"COMBINED: invalid verdict '{verdict}'; allowed: {ALLOWED_VERDICTS}")

    # Floor OK.
    floor_ok = data.get("floor_ok")
    if not isinstance(floor_ok, bool):
        errors.append(f"COMBINED: floor_ok must be bool, got {type(floor_ok)}")

    # Underlyings must include BTC and ETH.
    underlyings = data.get("underlyings", [])
    if not isinstance(underlyings, list) or len(underlyings) != 2:
        errors.append(f"COMBINED: underlyings must be a list of 2, got {underlyings}")
    else:
        if "BTC" not in underlyings:
            errors.append("COMBINED: underlyings must include 'BTC'")
        if "ETH" not in underlyings:
            errors.append("COMBINED: underlyings must include 'ETH'")

    # Campaign floor structure.
    cf = data.get("campaign_floor", {})
    if not cf:
        errors.append("COMBINED: campaign_floor missing or empty")
    else:
        if "underlyings_ok" not in cf:
            errors.append("COMBINED: campaign_floor missing underlyings_ok")
        if "aligned_ok" not in cf:
            errors.append("COMBINED: campaign_floor missing aligned_ok")
        if "ok" not in cf:
            errors.append("COMBINED: campaign_floor missing ok")

    # Per-config: 6 configs expected (1 signal x 2 grids x 3 horizons).
    per_config = data.get("per_config", [])
    if not isinstance(per_config, list) or len(per_config) != 6:
        errors.append(f"COMBINED: expected 6 configs (1 signal x 2 grids x 3 horizons), got {len(per_config)}")
    else:
        for i, c in enumerate(per_config):
            if not isinstance(c, dict):
                errors.append(f"COMBINED: config {i} is not a dict")
                continue
            for key in ("signal", "bar_seconds", "horizon_bars", "n_pairs", "pass"):
                if key not in c:
                    errors.append(f"COMBINED: config {i} missing key '{key}'")
            if c.get("signal") != "term_ratio":
                errors.append(f"COMBINED: config {i} signal must be 'term_ratio', got {c.get('signal')}")

    # Summary structure.
    summary = data.get("summary", {})
    for key in ("n_configs", "n_pass", "pass_configs", "best_ic", "best_config"):
        if key not in summary:
            errors.append(f"COMBINED: summary missing key '{key}'")

    # Pooled structure.
    pooled = data.get("pooled", {})
    for key in ("bh_fdr", "any_config_pass", "campaign_state"):
        if key not in pooled:
            errors.append(f"COMBINED: pooled missing key '{key}'")

    # Campaign state must be one of the two expected.
    cs = pooled.get("campaign_state", "")
    if cs not in (
        "EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD",
        "EVAL_120_BLOCKED_FLOOR",
    ):
        errors.append(f"COMBINED: unexpected campaign_state '{cs}'")

    # If floor_ok is False, verdict must be BLOCKED.
    if not floor_ok and verdict != "BLOCKED":
        errors.append(f"COMBINED: floor_ok is False but verdict is '{verdict}' (must be BLOCKED)")

    # If floor_ok is True, verdict must be GO CONFIRMED or NO-GO CONFIRMED (PASS).
    if floor_ok and verdict == "BLOCKED":
        errors.append(f"COMBINED: floor_ok is True but verdict is BLOCKED")

    return len(errors) == 0, errors


def _verify_blocked(blocked_path: Path) -> Tuple[bool, List[str]]:
    """Verify the BLOCKED artifact (emitted when floor not met)."""
    errors: List[str] = []
    data = _load_json(blocked_path)
    if data is None:
        errors.append(f"BLOCKED: invalid JSON or unreadable: {blocked_path}")
        return False, errors

    for field in REQUIRED_BLOCKED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"BLOCKED: missing required field '{field}'")

    if data.get("report_id") != BLOCKED_ID:
        errors.append(f"BLOCKED: report_id mismatch: expected {BLOCKED_ID}, got {data.get('report_id')}")

    if data.get("verdict") != "BLOCKED":
        errors.append(f"BLOCKED: verdict must be 'BLOCKED', got {data.get('verdict')}")

    if data.get("floor_ok") is not False:
        errors.append(f"BLOCKED: floor_ok must be False, got {data.get('floor_ok')}")

    return len(errors) == 0, errors


def run_gate() -> int:
    """Run the phase-B gate verification."""
    print(f"[{_utc_now_iso()}] EVAL-120 phase-B gate starting...")

    # Find artifacts.
    prereg_path = _find_artifact(f"{PREREG_ID}*.json")
    combined_path = _find_artifact(f"{REPORT_ID}*.json")
    blocked_path = _find_artifact(f"{BLOCKED_ID}*.json")

    if not prereg_path:
        print(f"FAIL: PREREG artifact not found (pattern: {PREREG_ID}*.json)")
        return 1
    if not combined_path and not blocked_path:
        print(f"FAIL: Neither COMBINED ({REPORT_ID}*.json) nor BLOCKED ({BLOCKED_ID}*.json) artifact found")
        return 1

    all_errors: List[str] = []

    # Verify PREREG.
    print(f"  Verifying PREREG: {prereg_path.name}")
    ok, errs = _verify_prereg(prereg_path)
    if not ok:
        all_errors.extend(errs)
        print(f"  PREREG: FAIL ({len(errs)} errors)")
    else:
        print(f"  PREREG: OK")

    # Verify COMBINED or BLOCKED.
    if combined_path:
        print(f"  Verifying COMBINED: {combined_path.name}")
        ok, errs = _verify_combined(combined_path)
        if not ok:
            all_errors.extend(errs)
            print(f"  COMBINED: FAIL ({len(errs)} errors)")
        else:
            print(f"  COMBINED: OK")
    if blocked_path:
        print(f"  Verifying BLOCKED: {blocked_path.name}")
        ok, errs = _verify_blocked(blocked_path)
        if not ok:
            all_errors.extend(errs)
            print(f"  BLOCKED: FAIL ({len(errs)} errors)")
        else:
            print(f"  BLOCKED: OK")

    # Cross-check: if both COMBINED and BLOCKED exist, that's an error.
    if combined_path and blocked_path:
        all_errors.append("Both COMBINED and BLOCKED artifacts exist — only one should be present")
        print("  CROSS-CHECK: FAIL (both COMBINED and BLOCKED present)")

    if all_errors:
        print(f"\n[{_utc_now_iso()}] EVAL-120 phase-B gate FAILED ({len(all_errors)} errors):")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"\n[{_utc_now_iso()}] EVAL-120 phase-B gate PASSED")
    print(f"  PREREG: {prereg_path.name}")
    if combined_path:
        print(f"  COMBINED: {combined_path.name}")
    if blocked_path:
        print(f"  BLOCKED: {blocked_path.name}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-120 phase-B gate: verify seal artifacts")
    ap.add_argument("--execute", action="store_true", help="run the gate (required)")
    args = ap.parse_args(argv)

    if not args.execute:
        print("ERROR: --execute is required", file=sys.stderr)
        return 2

    return run_gate()


if __name__ == "__main__":
    raise SystemExit(main())