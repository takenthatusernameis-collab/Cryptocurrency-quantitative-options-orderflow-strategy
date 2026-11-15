#!/usr/bin/env python3
"""EVAL-45 Leg B: real ETH options net-of-cost readiness + BLOCKED seal.

Leg B (ETH options net-of-cost) needs a dense real ETH option snapshot
time-series, like the 101 BTC snapshots the sealed EVAL-42 pipeline consumes.
A single option cross-section cannot support a net-of-cost walk-forward (IC,
quintile long-short, sign-flip, continuous z-score, each with 1000-permutation
paired permutation, 1000-resample block bootstrap, CSCV PBO, BH-FDR). Collecting
a real series requires hours of repeated public polling, which is infeasible
inside a single session.

This script measures the on-disk ETH option snapshot count (it never fabricates
or relabels BTC as ETH), records the ETH option venue's reachability as measured
evidence, and seals ``EVAL_45_OPTIONS_ETH_BLOCKED_<UTC>.{json,md}`` with the
measured reason and the EVAL-46 remediation. It never emits a GO/NO-GO verdict.

CLI::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 scripts/eval45_options_eth_blocked.py            # probe + seal
    python3 scripts/eval45_options_eth_blocked.py --no-probe # offline seal
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "EVAL_45_OPTIONS_ETH_BLOCKED"
OUT_DIR = Path("research_state")
DEFAULT_OPTIONS_DIR = Path("data/raw/options_candles")
BTC_SNAPSHOT_REFERENCE = 101
REQUIRED_ETH_OPTION_SNAPSHOTS = 30

CODE_PATHS: Tuple[str, ...] = (
    "scripts/eval45_options_eth_blocked.py",
    "scripts/eval42_options_timeseries_independent_audit.py",
    "src/data/public_export_acquisition.py",
    "tests/test_eval45_options_eth_blocked.py",
)


def _load_eval43():
    path = ROOT / "scripts" / "eval43_orderflow_full_roster_meta.py"
    spec = importlib.util.spec_from_file_location("eval43_orderflow_full_roster_meta", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


eval43 = _load_eval43()


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------


def assess_readiness(*, snapshot_count: int, required_min: int = REQUIRED_ETH_OPTION_SNAPSHOTS) -> Dict[str, Any]:
    """Decide whether an ETH options net-of-cost walk-forward is feasible.

    A dense real snapshot series is required; a single cross-section (or none)
    cannot support the pre-declared falsification statistics, so the leg is
    BLOCKED rather than measured on insufficient data.
    """
    n = int(snapshot_count)
    req = int(required_min)
    return {
        "snapshot_count": n,
        "required_min": req,
        "btc_snapshot_reference": BTC_SNAPSHOT_REFERENCE,
        "dense_series_available": bool(n >= req),
        "blocked": bool(n < req),
        "reason": (
            f"{n} real ETH option snapshots on disk < required {req} dense "
            f"snapshots (BTC reference: {BTC_SNAPSHOT_REFERENCE}); a single "
            "cross-section cannot support a net-of-cost walk-forward"
        ),
    }


def count_eth_option_snapshots(options_dir: Path | str = DEFAULT_OPTIONS_DIR) -> Dict[str, Any]:
    """Count real ETH option snapshots on disk without fabricating any.

    Scans the flat option-candle directory and counts files whose JSON payload
    references an ``ETH-USD`` option instrument. Never substitutes BTC data.
    """
    root = Path(options_dir)
    if not root.is_dir():
        return {"snapshot_count": 0, "sample_paths": [], "scan_error": f"missing dir: {root}"}
    count = 0
    sample: List[str] = []
    scan_error: Optional[str] = None
    for path in sorted(root.glob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:  # noqa: BLE001 - record, keep scanning
            scan_error = f"{path.name}: {exc}"
            continue
        if "ETH-USD" not in text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            # Fall back to substring match already satisfied above.
            payload = None
        if payload is not None and not _payload_references_eth(payload):
            continue
        count += 1
        if len(sample) < 5:
            sample.append(str(path))
    return {"snapshot_count": int(count), "sample_paths": sample, "scan_error": scan_error}


def _payload_references_eth(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if isinstance(value, str) and "ETH-USD" in value:
                return True
            if _payload_references_eth(value):
                return True
        return False
    if isinstance(payload, (list, tuple)):
        return any(_payload_references_eth(v) for v in payload)
    return False


def probe_eth_option_venue(session: Any = None) -> Dict[str, Any]:
    """Best-effort measured venue reachability for ETH options (never required)."""
    try:
        import requests

        from src.data.public_export_acquisition import fetch_okx_option_chain

        sess = session or requests.Session()
        result = fetch_okx_option_chain("ETH", session=sess)
        quotes = list(result.get("quotes") or [])
        expiries = sorted({str(q.get("expiry")) for q in quotes if q.get("expiry")})
        return {
            "reachable": True,
            "n_quotes": len(quotes),
            "n_distinct_expiries": len(expiries),
            "expiries": expiries,
            "sample_timestamp": quotes[0].get("timestamp") if quotes else None,
        }
    except Exception as exc:  # noqa: BLE001 - record the measured failure
        return {"reachable": False, "error_type": type(exc).__name__, "error": str(exc)}


# ---------------------------------------------------------------------------
# Report assembly / sealing
# ---------------------------------------------------------------------------


def build_blocked_report(
    *,
    generated_at: str,
    readiness: Mapping[str, Any],
    disk: Mapping[str, Any],
    venue: Mapping[str, Any],
    command: str,
    probe: bool,
) -> Dict[str, Any]:
    return {
        "report_id": REPORT_ID,
        "artifact_kind": "measurement_blocked",
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-45-OPTIONS-ETH-BLOCKED",
        "leg": "B_ETH_OPTIONS_NET_OF_COST",
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "authenticity_verified": False,
        "status": "BLOCKED",
        "verdict": "BLOCKED",
        "reason": str(readiness["reason"]),
        "readiness": dict(readiness),
        "disk_scan": dict(disk),
        "venue_probe": dict(venue),
        "venue_probed": bool(probe),
        "command": command,
        "attempts": [
            "Counted real ETH option snapshots on disk via "
            "scripts/eval45_options_eth_blocked.py (no BTC relabel, no synthesis).",
            "Probed the public OKX ETH-USD option venue to confirm reachability "
            "is not the blocker (single cross-section is not a time-series).",
            "No substitution attempted: BTC snapshots are never relabelled as ETH; "
            "a single cross-section is never reported as a net-of-cost result.",
        ],
        "remediation": [
            "EVAL-46: collect a dense real ETH-USD option snapshot time-series "
            "(public read-only polling over the required horizon, >= "
            f"{REQUIRED_ETH_OPTION_SNAPSHOTS} snapshots) into data/raw/options_candles/.",
            "Then run the sealed EVAL-42 independent options audit on the ETH series "
            "(IC, quintile long-short, sign-flip, continuous z-score; 1000-perm, "
            "1000-bootstrap, CSCV PBO k=4, BH-FDR alpha 0.1, seed 42) and seal EVAL_46.",
        ],
        "code_paths": list(CODE_PATHS),
    }


def build_blocked_md(r: Mapping[str, Any]) -> str:
    readiness = r["readiness"]
    disk = r["disk_scan"]
    venue = r["venue_probe"]
    lines = [
        f"# {r['report_id']} — ETH options net-of-cost BLOCKED (EVAL-45 Leg B)",
        "",
        f"- **Generated:** {r['generated_at']}",
        f"- **Task ID:** `{r['task_id']}`",
        f"- **Status:** `{r['status']}` — {r['reason']}",
        f"- **Trading mode:** {r['trading_mode']} (live_trading_enabled={r['live_trading_enabled']})",
        "",
        "## Readiness (measured)",
        "",
        f"- Real ETH option snapshots on disk: {readiness['snapshot_count']} "
        f"(required min {readiness['required_min']}; BTC reference {readiness['btc_snapshot_reference']})",
        f"- Dense series available: {readiness['dense_series_available']}",
        f"- Disk scan error: {disk.get('scan_error')}",
        "",
        "## Venue reachability (measured, not the blocker)",
        "",
    ]
    if r["venue_probed"]:
        if venue.get("reachable"):
            lines.append(
                f"- OKX ETH-USD option venue reachable: {venue.get('n_quotes')} quotes, "
                f"{venue.get('n_distinct_expiries')} distinct expiries "
                f"(sample ts {venue.get('sample_timestamp')})"
            )
        else:
            lines.append(f"- Venue probe failed: {venue.get('error_type')}: {venue.get('error')}")
    else:
        lines.append("- Venue probe skipped (--no-probe).")
    lines += [
        "",
        "## Why BLOCKED (not NO-GO)",
        "",
        "A net-of-cost walk-forward requires a dense real snapshot time-series; a "
        "single cross-section cannot support the pre-declared IC/quintile/sign-flip/"
        "z-score falsification statistics. This is an acquisition-horizon blocker, "
        "not a measured NO-GO — the ETH options pillar remains OPEN.",
        "",
        "## Attempts",
    ]
    lines += [f"- {a}" for a in r["attempts"]]
    lines += ["", "## Remediation (EVAL-46)"]
    lines += [f"- {a}" for a in r["remediation"]]
    lines += ["", "## Command", f"```bash\n{r['command']}\n```", ""]
    lines += ["## Code paths"]
    lines += [f"- `{p}`" for p in r["code_paths"]]
    lines.append("")
    return "\n".join(lines)


def seal(report: Mapping[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = eval43._stamp_for_filename(str(report["generated_at"]))
    jpath = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
    mpath = OUT_DIR / f"{REPORT_ID}_{stamp}.md"
    eval43._write_json(jpath, dict(report))
    mpath.write_text(build_blocked_md(report) + "\n", encoding="utf-8")
    return {"json": str(jpath), "md": str(mpath)}


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--options-dir", default=str(DEFAULT_OPTIONS_DIR))
    ap.add_argument("--required-min", type=int, default=REQUIRED_ETH_OPTION_SNAPSHOTS)
    ap.add_argument("--probe", dest="probe", action="store_true", default=True)
    ap.add_argument("--no-probe", dest="probe", action="store_false")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)

    disk = count_eth_option_snapshots(Path(args.options_dir))
    readiness = assess_readiness(
        snapshot_count=disk["snapshot_count"], required_min=args.required_min
    )
    venue = probe_eth_option_venue() if args.probe else {
        "reachable": None, "skipped": True,
    }
    generated_at = eval43._utc_now_iso()
    report = build_blocked_report(
        generated_at=generated_at,
        readiness=readiness,
        disk=disk,
        venue=venue,
        command=" ".join(["python3", "scripts/eval45_options_eth_blocked.py", *(argv or [])]),
        probe=args.probe,
    )
    if not eval43._all_finite(report):
        print(json.dumps({"report_id": REPORT_ID, "status": "FAILED",
                          "error": "non-finite values in report"}, sort_keys=True))
        return 1
    paths = {} if args.no_write else seal(report)
    print(json.dumps({
        "report_id": REPORT_ID,
        "verdict": report["verdict"],
        "snapshot_count": readiness["snapshot_count"],
        "required_min": readiness["required_min"],
        "dense_series_available": readiness["dense_series_available"],
        "venue_reachable": venue.get("reachable"),
        "artifact_paths": paths,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())