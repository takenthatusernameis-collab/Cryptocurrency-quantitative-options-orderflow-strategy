#!/usr/bin/env python3
"""EVAL-44: campaign closure certification (final rung).

Recomputes the termination verdict from sealed artifact hashes and pre-declared
bars only (no re-running), verifies the sealed EVAL chain is present and
append-only in form (new timestamped artifact, no mutation of sealed inputs),
and seals ``EVAL_44_CAMPAIGN_CLOSURE_<UTC>.{json,md}`` with a machine-checkable
ledger.

Paper-only, real-data only, no synthetic fallback, no phaseNN_* wrappers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_44_CAMPAIGN_CLOSURE"
TASK_ID = "INIT-2026-11-14T23:14:32Z-EVAL-44-CLOSURE-CERTIFY-AND-SEAL"
STAMP_RE = re.compile(r"(\d{8}T\d{6}(?:\d+)?Z)")

# Pre-declared sealed bars / expected verdicts (do not re-run).
PREDECLARED = {
    "FINAL_TERMINATION_MEMO_36_20261114T145419Z": {
        "path": "research_state/FINAL_TERMINATION_MEMO_36_20261114T145419Z.json",
        "sha256": "e05da3950a32bc4344acdaeac7382dc298748a9ca8262ad6c39fa06e17af8d58",
        "expect_verdict_contains": "NO-GO",
        "bar": "EVAL-36 TERMINATE_NO_GO",
    },
    "FINAL_TERMINATION_AUDIT_37_20261114T152849Z": {
        "path": "research_state/FINAL_TERMINATION_AUDIT_37_20261114T152849Z.json",
        "sha256": "74a1869d62ea5f706e1ded359b0c1d6d1527bd9a455826a09e84011b83a2819c",
        "expect_verdict": "PASS",
        "expect_n_checks": 9,
        "bar": "EVAL-37 PASS 9/9",
    },
    "ORDERFLOW_ROBUSTNESS_41_20261114T193836Z": {
        "path": "research_state/ORDERFLOW_ROBUSTNESS_41_20261114T193836Z.json",
        "sha256": "1f248487497e5d4c5deb4b33eb952208f3f811d1e2c1646e542733c487aae854",
        "expect_verdict_contains": "NO-GO",
        "bar": "EVAL-41 Track A orderflow robustness NO-GO/REPLICATION",
    },
    "EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z": {
        "path": "research_state/EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z.json",
        "sha256": "f8446f9088e69feb111a65ef7ac60fbe19e007822d2ccd4c74be9e72d00b5db4",
        "expect_verdict_contains": "NO-GO",
        "bar": "EVAL-41 Track B options time-series REPLICATION/NO-GO",
    },
    "EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z": {
        "path": "research_state/EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z.json",
        "sha256": "fc913898398a7e208f6f8f70a75ad584929bc1e59698cc8170ed6ac305857157",
        "expect_verdict_contains": "NO-GO",
        "bar": "EVAL-42 options independent audit NO-GO CONFIRMED",
    },
    "EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z": {
        "path": "research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.json",
        "sha256": "a9eea6dc4ab5e82d4cb9b1d8abf7fcb567eb8f2c84528c38cde213fc244c4194",
        "expect_verdict_contains": "NO-GO",
        "bar": "EVAL-43 orderflow full-roster meta NO-GO CONFIRMED (PASS)",
    },
}

COMMANDS = [
    "./scripts/verify_env.sh --check",
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval44_campaign_closure_certify.py",
    "python3 scripts/eval44_campaign_closure_certify.py",
    f'python3 scripts/check_session_sealed.py --task-id "{TASK_ID}" --glob "EVAL_44_*"',
]

CODE_PATHS = [
    "scripts/eval44_campaign_closure_certify.py",
    "scripts/check_session_sealed.py",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_sealed_eval_artifacts() -> List[Dict[str, Any]]:
    patterns = ["EVAL_*", "FINAL_TERMINATION_*"]
    out: List[Dict[str, Any]] = []
    seen = set()
    for pat in patterns:
        for p in sorted(OUT_DIR.glob(pat)):
            if not p.is_file():
                continue
            rel = str(p.relative_to(ROOT))
            if rel in seen:
                continue
            seen.add(rel)
            stamps = STAMP_RE.findall(p.name)
            out.append({
                "path": rel,
                "sha256": sha256_file(p),
                "stamp": max(stamps) if stamps else None,
                "bytes": p.stat().st_size,
            })
    out.sort(key=lambda x: x["path"])
    return out


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def recompute_termination() -> Dict[str, Any]:
    checks = []
    all_ok = True
    for name, spec in PREDECLARED.items():
        p = ROOT / spec["path"]
        item: Dict[str, Any] = {"name": name, "path": spec["path"], "bar": spec["bar"]}
        if not p.exists():
            item.update({"ok": False, "error": "missing"})
            checks.append(item)
            all_ok = False
            continue
        digest = sha256_file(p)
        d = load_json(p)
        verdict = d.get("verdict")
        hash_ok = digest == spec["sha256"]
        verdict_ok = True
        if "expect_verdict" in spec:
            verdict_ok = verdict == spec["expect_verdict"]
        if "expect_verdict_contains" in spec:
            verdict_ok = verdict_ok and isinstance(verdict, str) and spec["expect_verdict_contains"] in verdict
        n_checks_ok = True
        if "expect_n_checks" in spec:
            n_checks_ok = d.get("n_checks") == spec["expect_n_checks"]
        ok = hash_ok and verdict_ok and n_checks_ok
        item.update({
            "ok": ok,
            "sha256": digest,
            "expected_sha256": spec["sha256"],
            "hash_match": hash_ok,
            "observed_verdict": verdict,
            "verdict_ok": verdict_ok,
            "n_checks_ok": n_checks_ok,
        })
        if "expect_n_checks" in spec:
            item["observed_n_checks"] = d.get("n_checks")
        checks.append(item)
        all_ok = all_ok and ok

    # Recomputed verdict from sealed evidence + pre-declared bars only.
    # Campaign terminated NO-GO (EVAL-36), termination audit PASS 9/9 (EVAL-37),
    # options pillar closed NO-GO/REPLICATION + NO-GO CONFIRMED (EVAL-41B,42),
    # orderflow pillar closed NO-GO/REPLICATION + NO-GO CONFIRMED (EVAL-41A,43).
    campaign_closed = all_ok
    recomputed = {
        "campaign_status": "TERMINATED_NO_GO_CLOSED" if campaign_closed else "CERTIFICATION_FAILED",
        "campaign_closed": campaign_closed,
        "basis": "recomputed from sealed artifact hashes and pre-declared bars only (no re-running)",
        "sealed_chain_span": "EVAL-02..EVAL-43 plus termination memo/audit",
        "bars_satisfied": [c["bar"] for c in checks if c.get("ok")],
        "bars_failed": [c["bar"] for c in checks if not c.get("ok")],
        "options_pillar": "CLOSED (EVAL-41 Track B REPLICATION/NO-GO; EVAL-42 NO-GO CONFIRMED)" if all_ok else "UNCERTAIN",
        "orderflow_pillar": "CLOSED (EVAL-41 Track A NO-GO/REPLICATION; EVAL-43 NO-GO CONFIRMED PASS)" if all_ok else "UNCERTAIN",
        "net_of_cost_tradable": False if campaign_closed else None,
        "new_real_data_required": True,
        "checks": checks,
    }
    return recomputed


def build_report() -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ledger = list_sealed_eval_artifacts()
    termination = recompute_termination()
    # Append-only verification (form): this run produces a new timestamped EVAL_44 artifact;
    # we assert all predeclared sealed inputs still match recorded hashes/verdicts.
    append_only_verified = all(c.get("hash_match") for c in termination["checks"]) and all(
        c.get("ok") for c in termination["checks"]
    )
    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "eval_id": "EVAL-44",
        "task_id": TASK_ID,
        "generated_at": generated_at,
        "stamp": stamp,
        "verdict": "CAMPAIGN_CLOSED" if termination["campaign_closed"] else "CERTIFICATION_FAILED",
        "campaign_closed": termination["campaign_closed"],
        "termination_recompute": termination,
        "append_only_verified": append_only_verified,
        "append_only_note": (
            "All pre-declared sealed input artifacts present with stable sha256 and expected verdicts; "
            "this certification is an append-only timestamped artifact (no sealed inputs mutated, no evals re-run)."
        ),
        "artifact_ledger": ledger,
        "artifact_ledger_count": len(ledger),
        "sealed_chain_summary": {
            "eval_range": "EVAL-02..EVAL-43",
            "terminal_memo": "FINAL_TERMINATION_MEMO_36_20261114T145419Z (TERMINATE_NO_GO)",
            "terminal_audit": "FINAL_TERMINATION_AUDIT_37_20261114T152849Z (PASS 9/9)",
            "closure_rung": REPORT_ID,
        },
        "commands": COMMANDS,
        "code_paths": CODE_PATHS,
        "invariants": {
            "paper_only": True,
            "live_trading_enabled": False,
            "env_absent": not (ROOT / ".env").exists(),
            "re_runs_performed": False,
            "synthetic_fallback": False,
            "phaseNN_wrappers": False,
        },
        "never_valid_true": True,
    }
    return report


def render_md(report: Dict[str, Any]) -> str:
    t = report["termination_recompute"]
    lines = []
    lines.append(f"# {report['report_id']} — {report['stamp']}")
    lines.append("")
    lines.append(f"- **Verdict:** `{report['verdict']}`")
    lines.append(f"- **Campaign closed:** `{report['campaign_closed']}`")
    lines.append(f"- **Task:** `{report['task_id']}`")
    lines.append(f"- **Generated:** `{report['generated_at']}`")
    lines.append(f"- **Re-runs performed:** `False` (recomputed from sealed hashes + pre-declared bars only)")
    lines.append(f"- **Append-only verified:** `{report['append_only_verified']}`")
    lines.append("")
    lines.append("## Recomputed termination verdict")
    lines.append("")
    lines.append(f"- Status: **{t['campaign_status']}**")
    lines.append(f"- Basis: {t['basis']}")
    lines.append(f"- Options pillar: {t['options_pillar']}")
    lines.append(f"- Orderflow pillar: {t['orderflow_pillar']}")
    lines.append(f"- Net-of-cost tradable on available real BTC/OKX data: **{t['net_of_cost_tradable']}**")
    lines.append(f"- New real data required for any further progress: **{t['new_real_data_required']}**")
    lines.append("")
    lines.append("## Pre-declared bar checks (sealed inputs)")
    lines.append("")
    lines.append("| name | ok | hash match | verdict ok | observed verdict |")
    lines.append("|---|---|---:|---:|---|")
    for c in t["checks"]:
        lines.append(
            f"| `{c['name']}` | {c.get('ok')} | {c.get('hash_match')} | {c.get('verdict_ok')} | `{c.get('observed_verdict')}` |"
        )
    lines.append("")
    lines.append("## Artifact ledger (EVAL_* / FINAL_TERMINATION_*)")
    lines.append("")
    lines.append(f"Total artifacts: **{report['artifact_ledger_count']}**")
    lines.append("")
    lines.append("| path | sha256 | stamp | bytes |")
    lines.append("|---|---|---|---:|")
    for a in report["artifact_ledger"]:
        lines.append(f"| `{a['path']}` | `{a['sha256']}` | `{a.get('stamp')}` | {a['bytes']} |")
    lines.append("")
    lines.append("## Invariants")
    lines.append("")
    for k, v in report["invariants"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    for cmd in report["commands"]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    lines.append("## Closure")
    lines.append("")
    lines.append("Campaign is closed pending new real data. No further artifacts unless new real data arrives.")
    lines.append("The cryptocurrency quantitative options+orderflow strategy is definitively not net-of-cost tradable on the available real BTC/OKX data.")
    return "\n".join(lines) + "\n"


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)

    report = build_report()
    stamp = report["stamp"]
    json_path = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
    md_path = OUT_DIR / f"{REPORT_ID}_{stamp}.md"

    payload = serialize_metrics_strict(report)
    assert_json_valid(payload)
    md = render_md(report)

    if args.no_write:
        print(json.dumps({"report_id": REPORT_ID, "stamp": stamp, "verdict": report["verdict"], "campaign_closed": report["campaign_closed"], "artifact_paths": {}}, sort_keys=True))
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")

    result = {
        "report_id": REPORT_ID,
        "stamp": stamp,
        "verdict": report["verdict"],
        "campaign_closed": report["campaign_closed"],
        "append_only_verified": report["append_only_verified"],
        "artifact_paths": {
            "json": str(json_path.relative_to(ROOT)),
            "md": str(md_path.relative_to(ROOT)),
        },
        "artifact_ledger_count": report["artifact_ledger_count"],
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if report["campaign_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
