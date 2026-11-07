#!/usr/bin/env python3
"""Generate stricter R4 credential-controls checklist evidence (paper-only, advisory).

Deterministically consumes repo guardrails (src/config/secrets.py default,
.env.example, tracked git diff for live-enabling files), cross-venue artifacts
(per-venue credential-separation rows), plus a bounded additive secret-pattern
scan over signal artifacts (latest session gate, CV checkpoint, paper campaign,
R3-R7 artifacts) to produce a schema-validated R4 credential-controls checklist.
No secrets are read or committed; the scanner reports pattern matches on
artifact values, never secret material. Never enables live trading. Never
unblocks NEXT9. Advisory/opt-in.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import validate_r3_r7_reduction_evidence as v  # noqa: E402

SECRET_KEY_RE = re.compile(r"(secret|api_?key|private_?key|passphrase|token|credential_value|password)", re.I)
# Stricter local value regex: real provider key prefixes require a word boundary
# and trailing material, so benign words like "risk_manager_init" do not false-positive.
R4_SECRET_VALUE_RE = re.compile(r"\b(sk[-_][A-Za-z0-9]{6,}|pk[-_][A-Za-z0-9]{6,}|-----BEGIN|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9]{6,})")

# Bounded set of signal artifacts to scan for accidental secret material. Never
# scans the full research_state tree (thousands of historical step files).
SIGNAL_PATTERNS = [
    "PAPER_OPS_SESSION_GATE_*.json",
    "PAPER_OPS_READINESS_SNAPSHOT_*.json",
    "PAPER_TRADING_CAMPAIGN_*.json",
    "RECONCILIATION_AUDIT_*.json",
    "PRE_LIVE_GATE_REPORT_*.json",
    "CONTINUOUS_VALIDATION_*.json",
    "CONTINUOUS_VALIDATION_AND_MONITORING_*.json",
    "R3_VENUE_OPS_REHEARSAL_*.json",
    "R4_CREDENTIAL_CONTROLS_CHECKLIST_*.json",
    "R5_EXECUTION_SLIPPAGE_SIM_EVIDENCE_*.json",
    "R6_DRIFT_DETECTION_REPORT_*.json",
    "R7_HUMAN_PROCESS_CHECKLIST_*.json",
    "NEXT9_APPROVAL_VALIDATION_*.json",
    "GO_NO_GO_REPORT_*.json",
    "INCIDENT_DRILL_*.json",
    "CROSSVENUE_ORCHESTRATION_REPORT.json",
    "PHASE37_CROSS_VENUE_ROUTING_REPORT.json",
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _rel(path: Optional[Path]) -> Optional[str]:
    if not path or not path.exists():
        return None
    try:
        return path.relative_to(REPO).as_posix()
    except Exception:
        return str(path)


def _git_tracked_diff_names() -> List[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO), "diff", "--name-only", "HEAD"], stderr=subprocess.DEVNULL, text=True,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []


def _scan_obj_for_secrets(obj: Any, path: str = "", hits: Optional[List[str]] = None) -> List[str]:
    if hits is None:
        hits = []
    if isinstance(obj, dict):
        for k, val in obj.items():
            kp = f"{path}.{k}" if path else str(k)
            if SECRET_KEY_RE.search(str(k)) and isinstance(val, str) and val.strip() and val.strip().lower() not in {"redacted", "absent", "not_stored", "env_only", "secret_manager", "false", "true", "n/a", "na", "none", "null"}:
                if len(val.strip()) > 12 and not val.strip().startswith("<") and " " not in val.strip()[:40]:
                    hits.append(f"possible_secret_value:{kp}")
            if isinstance(val, str) and R4_SECRET_VALUE_RE.search(val):
                hits.append(f"secret_pattern:{kp}")
            _scan_obj_for_secrets(val, kp, hits)
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            _scan_obj_for_secrets(val, f"{path}[{i}]", hits)
    return hits


def _scan_signal_artifacts() -> Tuple[bool, List[str], List[str]]:
    """Scan only the latest signal artifacts for accidental secret material."""
    hits: List[str] = []
    refs: List[str] = []
    if not RS.exists():
        return False, hits, refs
    for pat in SIGNAL_PATTERNS:
        cands = sorted(RS.glob(pat))
        for p in cands[-3:]:  # latest 3 per pattern only
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            rel = p.relative_to(REPO).as_posix()
            refs.append(rel)
            _scan_obj_for_secrets(data, rel, hits)
    return bool(hits), hits, refs


def _venue_context() -> Tuple[List[str], Dict[str, Any], List[str]]:
    refs: List[str] = []
    venues: List[str] = []
    cross_p = RS / "CROSSVENUE_ORCHESTRATION_REPORT.json"
    route_p = RS / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json"
    cross = _load(cross_p) or {}
    route = _load(route_p) or {}
    if cross_p.exists():
        refs.append(_rel(cross_p) or str(cross_p))
    if route_p.exists():
        refs.append(_rel(route_p) or str(route_p))
    for src in (cross, (cross.get("config") or {}) if isinstance(cross, dict) else {}, route):
        if not isinstance(src, dict):
            continue
        v = src.get("venues")
        if isinstance(v, list) and v:
            venues = [str(x) for x in v if str(x).strip()]
            break
    if not venues:
        venues = ["deribit", "okx", "binance"]
    context = {
        "crossvenue_present": bool(cross),
        "routing_present": bool(route),
        "venues": venues,
        "crossvenue_paper_only": cross.get("paper_only") if cross else None,
        "routing_ok": route.get("ok") if route else None,
    }
    return venues, context, refs


def _per_venue_controls(venues: List[str], refs: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for venue in venues:
        rows.append({
            "control": f"paper_live_credential_separation:{venue}",
            "confirmed": False,
            "attestation": f"{venue}: paper credentials must not carry live/trade authority outside approved scope; process confirmation required before any approved live campaign",
            "evidence_refs": refs,
            "venue": venue,
        })
        rows.append({
            "control": f"least_privilege_trade_only_no_withdrawal:{venue}",
            "confirmed": False,
            "attestation": f"{venue}: least-privilege trade-only (no withdrawal) permissions required; verify in approved non-enabling preflight only",
            "evidence_refs": refs,
            "venue": venue,
        })
    return rows


def gen_r4_strict(ts: Optional[str] = None, *, effective_until_hours: Optional[int] = None) -> Dict[str, Any]:
    ts = ts or _utc()
    secrets_p = REPO / "src/config/secrets.py"
    env_example_p = REPO / ".env.example"
    tracked = _git_tracked_diff_names()

    secrets_text = secrets_p.read_text(encoding="utf-8", errors="ignore") if secrets_p.exists() else ""
    env_text = env_example_p.read_text(encoding="utf-8", errors="ignore") if env_example_p.exists() else ""

    default_false = bool(re.search(r"""LIVE_TRADING_ENABLED["']\s*,\s*["']false["']""", secrets_text))
    env_false = "LIVE_TRADING_ENABLED=false" in env_text and "LIVE_TRADING_ENABLED=true" not in env_text
    live_enabling_diff = [f for f in tracked if f in {"src/config/secrets.py", ".env.example"} or "live_trading" in f.lower()]
    secrets_committed, secret_hits, scanned_refs = _scan_signal_artifacts()
    venues, venue_ctx, venue_refs = _venue_context()

    warn_flags: List[str] = []
    if not secrets_p.exists():
        warn_flags.append("secrets_py_missing")
    if not default_false:
        warn_flags.append("live_trading_default_not_false")
    if not env_false:
        warn_flags.append("env_example_live_trading_not_false")
    if live_enabling_diff:
        warn_flags.append("tracked_live_enabling_diff:" + ",".join(sorted(live_enabling_diff)))
    if secrets_committed:
        warn_flags.append("possible_secret_values_in_signal_artifacts")
    if not venue_ctx.get("crossvenue_present"):
        warn_flags.append("crossvenue_orchestration_report_missing")

    controls = [
        {
            "control": "secrets_not_committed",
            "confirmed": not secrets_committed,
            "attestation": "no API keys/secrets committed in signal artifacts; scanner reports pattern hits only, never secret material",
            "evidence_refs": [r for r in [_rel(secrets_p), _rel(env_example_p)] if r],
        },
        {
            "control": "live_trading_default_false",
            "confirmed": default_false,
            "attestation": "src/config/secrets.py default LIVE_TRADING_ENABLED=false; no live capital",
            "evidence_refs": [_rel(secrets_p)] if _rel(secrets_p) else [],
        },
        {
            "control": "env_example_live_trading_false",
            "confirmed": env_false,
            "attestation": ".env.example keeps LIVE_TRADING_ENABLED=false and has no true override",
            "evidence_refs": [_rel(env_example_p)] if _rel(env_example_p) else [],
        },
        {
            "control": "tracked_worktree_clean_of_live_enabling_changes",
            "confirmed": len(live_enabling_diff) == 0,
            "attestation": "git diff --name-only HEAD shows no live-enabling edits to secrets/env/settings",
            "evidence_refs": [],
        },
        {
            "control": "paper_live_credential_separation",
            "confirmed": False,
            "attestation": "process control required before any approved live campaign; paper keys must not carry live authority",
            "evidence_refs": venue_refs,
        },
        {
            "control": "least_privilege_trade_only_no_withdrawal",
            "confirmed": False,
            "attestation": "process control required; verify venue permissions in approved non-enabling preflight only",
            "evidence_refs": venue_refs,
        },
        {
            "control": "rotation_revocation_plan",
            "confirmed": False,
            "attestation": "operator-owned; confirm before any approved live campaign",
            "evidence_refs": [],
        },
        {
            "control": "approved_secret_store_only",
            "confirmed": False,
            "attestation": "no secrets in repo/logs/artifacts/chat transcripts",
            "evidence_refs": [],
        },
    ]
    controls.extend(_per_venue_controls(venues, venue_refs))

    deterministic_pass = bool(
        default_false and env_false and not live_enabling_diff and not secrets_committed and secrets_p.exists() and env_example_p.exists()
    )

    evidence_refs = [r for r in [_rel(secrets_p), _rel(env_example_p), "docs/PAPER_RUNBOOK.md"] + venue_refs if r]

    out = {
        "artifact_type": v.ARTIFACT_TYPES["R4"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "checklist": controls,
        "secrets_committed": secrets_committed,
        "attestation_only": True,
        "advisory": True,
        "strictness": "enhanced_extraction_v2",
        "guardrails": {
            "secrets_py_present": secrets_p.exists(),
            "env_example_present": env_example_p.exists(),
            "live_trading_default_false": default_false,
            "env_example_live_trading_false": env_false,
            "tracked_live_enabling_diff": live_enabling_diff,
            "tracked_worktree_clean": len(live_enabling_diff) == 0,
            "possible_secret_values_in_artifacts": secrets_committed,
        },
        "secret_scan": {
            "scanned_artifact_refs": scanned_refs,
            "hits": secret_hits,
            "hit_count": len(secret_hits),
        },
        "venue_credential_coverage": venue_ctx,
        "flags": {
            "deterministic_pass": deterministic_pass,
            "no_external_venue_mutation": True,
            "advisory_only": True,
            "secrets_not_read_or_logged": True,
        },
        "warn_flags": warn_flags,
        "evidence_refs": evidence_refs,
    }
    if effective_until_hours is not None and effective_until_hours > 0:
        out["effective_until_utc"] = (datetime.now(timezone.utc) + timedelta(hours=effective_until_hours)).isoformat().replace("+00:00", "Z")
        out["flags"]["effective_until_advisory"] = True
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R4 credential-controls checklist evidence (paper-only)")
    ap.add_argument("--effective-until-hours", type=int, default=None, help="Advisory/default-off: add effective_until_utc (informational only; does not grant approvals)")
    args = ap.parse_args(argv)
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r4_strict(_utc(), effective_until_hours=args.effective_until_hours)
    ok, issues = v.validate_artifact(d, "R4")
    if not ok:
        print(json.dumps({"valid": False, "issues": issues}, indent=2))
        return 1
    out = RS / f"R4_CREDENTIAL_CONTROLS_CHECKLIST_{_utc()}.json"
    out.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out.relative_to(REPO)),
        "valid": True,
        "deterministic_pass": d["flags"]["deterministic_pass"],
        "secrets_committed": d["secrets_committed"],
        "venues": d.get("venue_credential_coverage", {}).get("venues"),
        "next9_unblocked": False,
        "warn_flags": d["warn_flags"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())