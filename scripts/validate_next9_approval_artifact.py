#!/usr/bin/env python3
"""Validate NEXT9/A1–A7 approval artifacts (paper-only, additive).

Refuses to treat NEXT9 as unblocked unless an explicitly provided artifact
contains all required approval fields. Never enables live trading.

Usage:
  PYTHONPATH=. python scripts/validate_next9_approval_artifact.py --check-current
  PYTHONPATH=. python scripts/validate_next9_approval_artifact.py --artifact path.json [--strict]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
CP = RS / "campaign_checkpoints"

REQUIRED_APPROVAL_IDS = [f"A{i}" for i in range(1, 8)]
# Canonical required fields per approval id. Each entry is (field, mandatory).
# `approved` is the explicit human decision; every other field must carry a
# non-empty, non-false value so a bare `approved: true` cannot unblock NEXT9.
REQUIRED_FIELDS = {
    "A1": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("scope", True)],
    "A2": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("limits", True)],
    "A3": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("canary_scope", True)],
    "A4": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("rehearsal_evidence", True)],
    "A5": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("credential_controls_confirmed", True)],
    "A6": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("rollback_owner", True)],
    "A7": [("approver_identity", True), ("timestamp_utc", True), ("approved", True), ("live_disabled_until_approved_decision", True)],
}
# Aliases accepted for the canonical names, so both the canonical schema and the
# NEXT8 review-only proposal schema (which uses `approver` + a descriptive
# `item`) validate against the same invariant set.
FIELD_ALIASES = {
    "approver_identity": ("approver_identity", "approver"),
    "timestamp_utc": ("timestamp_utc", "timestamp"),
    "scope": ("scope", "item"),
    "limits": ("limits", "item"),
    "canary_scope": ("canary_scope", "item"),
    "rehearsal_evidence": ("rehearsal_evidence", "item"),
    "credential_controls_confirmed": ("credential_controls_confirmed", "item"),
    "rollback_owner": ("rollback_owner", "item"),
    "live_disabled_until_approved_decision": ("live_disabled_until_approved_decision", "item"),
}
# Canonical field names only (for legacy callers / tests).
REQUIRED_FIELD_NAMES = {aid: [f for f, _ in fields] for aid, fields in REQUIRED_FIELDS.items()}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_field(item: Dict[str, Any], canonical: str) -> Any:
    """Return the first non-None value among the canonical field and its aliases."""
    for name in FIELD_ALIASES.get(canonical, (canonical,)):
        v = item.get(name)
        if v is not None and v != "":
            return v
    return None


def _parse_ts(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 UTC timestamp into an aware datetime. Returns None if unparseable."""
    if not isinstance(value, str) or not value:
        return None
    s = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _approval_freshness_issues(
    data: Dict[str, Any],
    *,
    max_age_hours: Optional[float],
    effective_until_utc: Optional[str],
    now: Optional[datetime] = None,
) -> List[str]:
    """Advisory/default-off structural freshness check.

    Defaults off: when both `max_age_hours` and `effective_until_utc` are None this
    function returns an empty list and the validator behaves exactly as before. When
    enabled it can only *tighten* the block (never loosen it): it reports issues for
    stale approvals or expired effective_until_utc windows. It never grants approval
    and never enables live trading.
    """
    if max_age_hours is None and not effective_until_utc:
        return []
    issues: List[str] = []
    checklist = data.get("human_approval_checklist") or data.get("approvals") or []
    if not isinstance(checklist, list) or not checklist:
        return issues
    by_id = {str(item.get("id") or item.get("approval_id") or ""): item for item in checklist if isinstance(item, dict)}
    now = now or datetime.now(timezone.utc)
    for aid in REQUIRED_APPROVAL_IDS:
        item = by_id.get(aid)
        if not item:
            continue
        ts_raw = _resolve_field(item, "timestamp_utc")
        ts = _parse_ts(ts_raw)
        if max_age_hours is not None:
            if ts is None:
                issues.append(f"{aid}_approval_timestamp_unparseable")
            else:
                age_hours = (now - ts).total_seconds() / 3600.0
                if age_hours > float(max_age_hours) + 1e-9:
                    issues.append(f"{aid}_approval_stale_hours:{age_hours:.2f}:{float(max_age_hours)}")
        if effective_until_utc:
            eff = _parse_ts(effective_until_utc)
            if eff is None:
                issues.append("effective_until_utc_unparseable")
            elif ts is not None and ts > eff:
                issues.append(f"{aid}_approval_timestamp_after_effective_until_utc")
    return issues


def validate_approval_artifact(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    if data.get("live_trading_enabled") is True:
        issues.append("artifact_must_not_enable_live_trading")
    if data.get("paper_only") is False:
        issues.append("artifact_must_not_claim_not_paper_only")
    checklist = data.get("human_approval_checklist") or data.get("approvals") or []
    if not isinstance(checklist, list) or not checklist:
        issues.append("missing_human_approval_checklist")
        return False, issues
    by_id = {str(item.get("id") or item.get("approval_id") or ""): item for item in checklist if isinstance(item, dict)}
    for aid in REQUIRED_APPROVAL_IDS:
        item = by_id.get(aid)
        if not item:
            issues.append(f"missing_{aid}")
            continue
        for canonical, mandatory in REQUIRED_FIELDS[aid]:
            if canonical == "approved":
                if item.get("approved") is not True:
                    issues.append(f"{aid}_not_explicitly_approved")
                continue
            if not mandatory:
                continue
            v = _resolve_field(item, canonical)
            if v is None or v == "" or v is False:
                issues.append(f"{aid}_missing_{canonical}")
    unblocked = len(issues) == 0
    return unblocked, issues


def check_current(repo: Path = REPO, *, max_age_hours: Optional[float] = None, effective_until_utc: Optional[str] = None) -> Dict[str, Any]:
    cp = _load(repo / "research_state/campaign_checkpoints/LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json")
    issues: List[str] = []
    if not cp:
        issues.append("missing_next8_checkpoint")
        return {"next9_unblocked": False, "issues": issues, "paper_only": True, "live_trading_enabled": False}
    prop = _load(repo / ((cp.get("artifacts") or {}).get("proposal_json") or ""))
    if not prop:
        issues.append("missing_proposal_json")
        return {"next9_unblocked": False, "issues": issues, "checkpoint_decision": cp.get("live_enablement_decision")}
    ok, iss = validate_approval_artifact(prop)
    issues.extend(iss)
    if cp.get("live_enablement_decision") == "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL" and ok:
        issues.append("checkpoint_decision_conflicts_with_full_approvals")
        ok = False
    fresh = _approval_freshness_issues(
        prop, max_age_hours=max_age_hours, effective_until_utc=effective_until_utc
    )
    if fresh:
        issues.extend(fresh)
        ok = False
    return {
        "next9_unblocked": bool(ok),
        "issues": issues,
        "checkpoint_decision": cp.get("live_enablement_decision"),
        "paper_only": True,
        "live_trading_enabled": False,
        "approval_freshness_check": {
            "enabled": bool(max_age_hours is not None or effective_until_utc),
            "max_age_hours": max_age_hours,
            "effective_until_utc": effective_until_utc,
            "freshness_issues": fresh,
        },
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", help="Path to approval artifact JSON")
    ap.add_argument("--check-current", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--write", action="store_true", help="Write additive timestamped report to research_state/")
    ap.add_argument("--max-approval-age-hours", type=float, default=None, help="Advisory/default-off: reject approvals older than N hours (never grants approval)")
    ap.add_argument("--effective-until-utc", default=None, help="Advisory/default-off: reject approvals whose timestamp is after this UTC ISO-8601 cutoff (never grants approval)")
    args = ap.parse_args(argv)
    if args.check_current or not args.artifact:
        result = check_current(
            REPO,
            max_age_hours=args.max_approval_age_hours,
            effective_until_utc=args.effective_until_utc,
        )
    else:
        data = _load(REPO / args.artifact) if not Path(args.artifact).is_absolute() else _load(Path(args.artifact))
        if data is None:
            result = {"next9_unblocked": False, "issues": ["artifact_not_found_or_invalid_json"]}
        else:
            ok, issues = validate_approval_artifact(data)
            fresh = _approval_freshness_issues(
                data,
                max_age_hours=args.max_approval_age_hours,
                effective_until_utc=args.effective_until_utc,
            )
            if fresh:
                issues.extend(fresh)
                ok = False
            result = {"next9_unblocked": bool(ok), "issues": issues, "artifact": str(args.artifact)}
            result["approval_freshness_check"] = {
                "enabled": bool(args.max_approval_age_hours is not None or args.effective_until_utc),
                "max_age_hours": args.max_approval_age_hours,
                "effective_until_utc": args.effective_until_utc,
                "freshness_issues": fresh,
            }
    result["timestamp_utc"] = _utc()
    result["paper_only"] = True
    result["live_trading_enabled"] = False
    print(json.dumps(result, indent=2))
    if args.write:
        RS.mkdir(parents=True, exist_ok=True)
        out = RS / f"NEXT9_APPROVAL_VALIDATION_{result['timestamp_utc']}.json"
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        try:
            shown = out.relative_to(REPO)
        except Exception:
            shown = out
        print(f"wrote {shown}")
    if args.strict and not result["next9_unblocked"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
