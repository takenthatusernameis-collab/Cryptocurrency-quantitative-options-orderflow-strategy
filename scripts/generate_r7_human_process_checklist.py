#!/usr/bin/env python3
"""Generate stricter R7 human-process/A1-A7 checklist artifact (paper-only, advisory).

Cross-references NEXT8 LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY checkpoint/proposal and the
NEXT9 validator (scripts/validate_next9_approval_artifact.py). Produces schema-validated
R7 process checklist rows for A1-A7 with explicit recorded-approval=false defaults and a
strong cannot-grant-approval invariant. This artifact NEVER grants approval and NEVER
unblocks NEXT9. Deterministic; no external mutation; no live trading.
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
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import validate_r3_r7_reduction_evidence as v  # noqa: E402

NEXT9_VALIDATOR_REF = "scripts/validate_next9_approval_artifact.py"
NEXT8_CP_REL = "research_state/campaign_checkpoints/LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json"

A1_A7_ITEMS = [
    ("A1", "Named human approver reviews proposal and cited prerequisites", "scope"),
    ("A2", "Residual risks R1-R7 accepted/mitigated with documented controls", "limits"),
    ("A3", "Venue/symbol scope and limits/canary size approved", "canary_scope"),
    ("A4", "Kill-switch/circuit-breaker/reconciliation-halt/escalation rehearsed", "rehearsal_evidence"),
    ("A5", "Live credentials least-privilege, paper/live separation, rotation/revocation confirmed", "credential_controls_confirmed"),
    ("A6", "Rollback/disable procedure reviewed; rollback owner assigned", "rollback_owner"),
    ("A7", "Explicit decision recorded: LIVE_TRADING_ENABLED remains false until separately approved campaign passes", "live_disabled_until_approved_decision"),
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


def _proposal_state() -> Tuple[Dict[str, Any], List[str], Optional[str]]:
    cp = _load(REPO / NEXT8_CP_REL)
    refs: List[str] = []
    if (REPO / NEXT8_CP_REL).exists():
        refs.append(NEXT8_CP_REL)
    if not cp:
        return {"present": False, "decision": None, "proposal_items_by_id": {}}, refs, None
    prop_rel = ((cp.get("artifacts") or {}).get("proposal_json") or "")
    prop_path = (REPO / prop_rel) if prop_rel else None
    prop = _load(prop_path) if prop_path else None
    if prop_rel and prop_path and prop_path.exists():
        refs.append(prop_rel)
    items = (prop or {}).get("human_approval_checklist") or []
    by_id = {str(it.get("id")): it for it in items if isinstance(it, dict) and it.get("id")}
    return {
        "present": True,
        "checkpoint_decision": cp.get("live_enablement_decision"),
        "proposal_id": (prop or {}).get("proposal_id"),
        "proposal_items_by_id": {k: {"approved": v.get("approved"), "required": v.get("required"), "item": v.get("item")} for k, v in by_id.items()},
    }, refs, prop_rel or None


def gen_r7_strict(ts: Optional[str] = None) -> Dict[str, Any]:
    proposal_state, refs, prop_rel = _proposal_state()
    validator_ok = (REPO / NEXT9_VALIDATOR_REF).exists()

    warn_flags: List[str] = []
    if not proposal_state.get("present"):
        warn_flags.append("next8_checkpoint_missing")
    if not validator_ok:
        warn_flags.append("next9_validator_missing")
    if proposal_state.get("checkpoint_decision") not in (None, "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL"):
        warn_flags.append("next8_checkpoint_decision_unexpected:" + str(proposal_state.get("checkpoint_decision")))

    by_id = proposal_state.get("proposal_items_by_id") or {}
    checklist = []
    for aid, label, required_field in A1_A7_ITEMS:
        src = by_id.get(aid) or {}
        checklist.append({
            "id": aid,
            "process_item": label,
            "required_validator_field": required_field,
            "recorded_approval": False,
            "proposal_item_present": aid in by_id,
            "proposal_approved_claim": bool(src.get("approved")) if aid in by_id else False,
            "status": "pending_explicit_human_approval_recorded_in_validated_additive_artifact",
            "note": "human/process only; cannot be granted by agent, by this artifact, or by process-checklist generation; NEXT9 validator requires explicit A1-A7 recorded approvals",
            "evidence_refs": [r for r in [NEXT8_CP_REL, prop_rel, NEXT9_VALIDATOR_REF] if r],
        })

    # Hard safety assertions in artifact body for downstream consumers/tests.
    cannot_grant_approval = True
    next9_unblocked = False
    deterministic_pass = bool(proposal_state.get("present") and validator_ok and cannot_grant_approval and not next9_unblocked)

    evidence_refs = list(dict.fromkeys(refs + [NEXT9_VALIDATOR_REF]))
    evidence_refs = [r for r in evidence_refs if (REPO / r).exists()]

    return {
        "artifact_type": v.ARTIFACT_TYPES["R7"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": next9_unblocked,
        "process_checklist": checklist,
        "proposal_crossref": {
            "next8_checkpoint": NEXT8_CP_REL,
            "proposal_json": prop_rel,
            "checkpoint_decision": proposal_state.get("checkpoint_decision"),
            "proposal_id": proposal_state.get("proposal_id"),
            "items_crossreferenced": sorted(by_id.keys()),
        },
        "next9_validation_contract": {
            "validator_ref": NEXT9_VALIDATOR_REF,
            "required_ids": [f"A{i}" for i in range(1, 8)],
            "validator_must_block_without_recorded_approvals": True,
            "this_artifact_grants_approvals": False,
            "this_artifact_unblocks_next9": False,
        },
        "flags": {
            "deterministic_pass": deterministic_pass,
            "cannot_grant_approval": cannot_grant_approval,
            "advisory_only": True,
        },
        "warn_flags": warn_flags,
        "cannot_grant_approval": cannot_grant_approval,
        "next9_validator_ref": NEXT9_VALIDATOR_REF,
        "evidence_refs": evidence_refs,
        "advisory": True,
        "strictness": "enhanced_extraction_v1",
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R7 human-process checklist evidence (paper-only)")
    ap.parse_args(argv)
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r7_strict(_utc())
    ok, issues = v.validate_artifact(d, "R7")
    if not ok:
        print(json.dumps({"valid": False, "issues": issues}, indent=2))
        return 1
    # Extra invariant: R7 must never claim approval/unblock even if schema-valid.
    if d.get("cannot_grant_approval") is not True or d.get("next9_unblocked") is True:
        print(json.dumps({"valid": False, "issues": ["R7_safety_invariant_violation"]}, indent=2))
        return 2
    out = RS / f"R7_HUMAN_PROCESS_CHECKLIST_{_utc()}.json"
    out.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out.relative_to(REPO)),
        "valid": True,
        "deterministic_pass": d["flags"]["deterministic_pass"],
        "cannot_grant_approval": True,
        "next9_unblocked": False,
        "warn_flags": d["warn_flags"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
