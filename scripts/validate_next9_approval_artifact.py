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
REQUIRED_FIELDS = {
    "A1": ["approver_identity", "timestamp_utc", "approved", "scope"],
    "A2": ["approver_identity", "timestamp_utc", "approved", "limits"],
    "A3": ["approver_identity", "timestamp_utc", "approved", "canary_scope"],
    "A4": ["approver_identity", "timestamp_utc", "approved", "rehearsal_evidence"],
    "A5": ["approver_identity", "timestamp_utc", "approved", "credential_controls_confirmed"],
    "A6": ["approver_identity", "timestamp_utc", "approved", "rollback_owner"],
    "A7": ["approver_identity", "timestamp_utc", "approved", "live_disabled_until_approved_decision"],
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


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
        if item.get("approved") is not True:
            issues.append(f"{aid}_not_explicitly_approved")
        for f in REQUIRED_FIELDS[aid]:
            v = item.get(f)
            if v is None or v == "" or v is False and f not in {"approved"}:
                if f == "approved":
                    continue
                issues.append(f"{aid}_missing_{f}")
    unblocked = len([i for i in issues if i]) == 0
    return unblocked, issues


def check_current(repo: Path = REPO) -> Dict[str, Any]:
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
    return {
        "next9_unblocked": bool(ok),
        "issues": issues,
        "checkpoint_decision": cp.get("live_enablement_decision"),
        "paper_only": True,
        "live_trading_enabled": False,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", help="Path to approval artifact JSON")
    ap.add_argument("--check-current", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--write", action="store_true", help="Write additive timestamped report to research_state/")
    args = ap.parse_args(argv)
    if args.check_current or not args.artifact:
        result = check_current(REPO)
    else:
        data = _load(REPO / args.artifact) if not Path(args.artifact).is_absolute() else _load(Path(args.artifact))
        if data is None:
            result = {"next9_unblocked": False, "issues": ["artifact_not_found_or_invalid_json"]}
        else:
            ok, issues = validate_approval_artifact(data)
            result = {"next9_unblocked": bool(ok), "issues": issues, "artifact": str(args.artifact)}
    result["timestamp_utc"] = _utc()
    result["paper_only"] = True
    result["live_trading_enabled"] = False
    print(json.dumps(result, indent=2))
    if args.write:
        RS.mkdir(parents=True, exist_ok=True)
        out = RS / f"NEXT9_APPROVAL_VALIDATION_{result['timestamp_utc']}.json"
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out.relative_to(REPO)}")
    if args.strict and not result["next9_unblocked"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
