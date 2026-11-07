#!/usr/bin/env python3
"""Validate R3-R7 risk-reduction evidence artifacts (paper-only, additive, advisory).

Covers repo-name-prioritized paper-ops risk lanes for crypto options orderflow:
  R3 venue/ops rehearsal evidence
  R4 credential-controls checklist confirmation (NO secrets committed)
  R5 execution/slippage simulation evidence (paper/backtest-derived)
  R6 drift-detection report
  R7 human-process/A1-A7 process checklist artifacts (cannot grant approval)

Advisory by default: does not enable live trading, does not unblock NEXT9, and
must not be wired to block current paper-ops unless a caller explicitly opts in
to a strict flag that defaults off.

Usage:
  PYTHONPATH=. python3 scripts/validate_r3_r7_reduction_evidence.py --artifact path.json --kind R3 --strict
  PYTHONPATH=. python3 scripts/validate_r3_r7_reduction_evidence.py --check-repo [--write]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"

KINDS = ("R3", "R4", "R5", "R6", "R7")
ARTIFACT_TYPES = {
    "R3": "VENUE_OPS_REHEARSAL_EVIDENCE",
    "R4": "CREDENTIAL_CONTROLS_CHECKLIST",
    "R5": "EXECUTION_SLIPPAGE_SIM_EVIDENCE",
    "R6": "DRIFT_DETECTION_REPORT",
    "R7": "HUMAN_PROCESS_A1_A7_CHECKLIST",
}
PATTERNS = {
    "R3": "R3_VENUE_OPS_REHEARSAL_*.json",
    "R4": "R4_CREDENTIAL_CONTROLS_CHECKLIST_*.json",
    "R5": "R5_EXECUTION_SLIPPAGE_SIM_EVIDENCE_*.json",
    "R6": "R6_DRIFT_DETECTION_REPORT_*.json",
    "R7": "R7_HUMAN_PROCESS_CHECKLIST_*.json",
}
SECRET_KEY_RE = re.compile(r"(secret|api_?key|private_?key|passphrase|token|credential_value|password)", re.I)
SECRET_VALUE_RE = re.compile(r"(sk[-_]|pk[-_]|-----BEGIN|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-)")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _require(d: Dict[str, Any], key: str, issues: List[str], kind: str) -> Any:
    v = d.get(key)
    if v is None or v == "" or v == [] or v == {}:
        issues.append(f"{kind}_missing_{key}")
    return v


def _common_guards(d: Dict[str, Any], kind: str) -> List[str]:
    issues: List[str] = []
    if d.get("live_trading_enabled") is True:
        issues.append(f"{kind}_must_not_enable_live_trading")
    if d.get("paper_only") is not True:
        issues.append(f"{kind}_paper_only_required")
    if d.get("next9_unblocked") is True:
        issues.append(f"{kind}_must_not_unblock_next9")
    return issues


def _scan_for_secret_values(obj: Any, path: str = "") -> List[str]:
    hits: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}" if path else str(k)
            if SECRET_KEY_RE.search(str(k)) and isinstance(v, str) and v.strip() and v.strip().lower() not in {"redacted", "absent", "not_stored", "env_only", "secret_manager", "false", "true", "n/a", "na", "none", "null"}:
                # suspicious: a secret-like key carrying a non-placeholder value
                if len(v.strip()) > 12 and not v.strip().startswith("<") and " " not in v.strip()[:40]:
                    hits.append(f"possible_secret_value:{kp}")
            if isinstance(v, str) and SECRET_VALUE_RE.search(v):
                hits.append(f"secret_pattern:{kp}")
            hits.extend(_scan_for_secret_values(v, kp))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(_scan_for_secret_values(v, f"{path}[{i}]"))
    return hits


def validate_r3(d: Dict[str, Any]) -> Tuple[bool, List[str]]:
    kind = "R3"
    issues = _common_guards(d, kind)
    if d.get("artifact_type") != ARTIFACT_TYPES[kind]:
        issues.append(f"{kind}_artifact_type_mismatch")
    _require(d, "timestamp_utc", issues, kind)
    _require(d, "venues", issues, kind)
    _require(d, "symbols", issues, kind)
    _require(d, "rehearsal_scope", issues, kind)
    checklist = _require(d, "checklist", issues, kind)
    if isinstance(checklist, list):
        for item in checklist:
            if not isinstance(item, dict) or not item.get("id") or "status" not in item:
                issues.append(f"{kind}_invalid_checklist_item")
                break
    _require(d, "evidence_refs", issues, kind)
    _require(d, "no_external_venue_mutation", issues, kind)
    if d.get("no_external_venue_mutation") is not True:
        issues.append(f"{kind}_external_venue_mutation_not_allowed")
    return len(issues) == 0, issues


def validate_r4(d: Dict[str, Any]) -> Tuple[bool, List[str]]:
    kind = "R4"
    issues = _common_guards(d, kind)
    if d.get("artifact_type") != ARTIFACT_TYPES[kind]:
        issues.append(f"{kind}_artifact_type_mismatch")
    _require(d, "timestamp_utc", issues, kind)
    _require(d, "checklist", issues, kind)
    checklist = d.get("checklist") or []
    if isinstance(checklist, list):
        for item in checklist:
            if not isinstance(item, dict) or not item.get("control") or "confirmed" not in item:
                issues.append(f"{kind}_invalid_checklist_item")
                break
    if d.get("secrets_committed") is not False:
        issues.append(f"{kind}_secrets_committed_must_be_false")
    if d.get("attestation_only") is not True:
        issues.append(f"{kind}_attestation_only_required")
    issues.extend(_scan_for_secret_values(d))
    return len(issues) == 0, issues


def validate_r5(d: Dict[str, Any]) -> Tuple[bool, List[str]]:
    kind = "R5"
    issues = _common_guards(d, kind)
    if d.get("artifact_type") != ARTIFACT_TYPES[kind]:
        issues.append(f"{kind}_artifact_type_mismatch")
    _require(d, "timestamp_utc", issues, kind)
    _require(d, "simulation_scope", issues, kind)
    _require(d, "evidence_refs", issues, kind)
    metrics = _require(d, "metrics", issues, kind)
    if isinstance(metrics, dict):
        for k in ("slippage_assumption_documented", "fill_quality_documented"):
            if metrics.get(k) is not True:
                issues.append(f"{kind}_metrics_{k}_required")
    _require(d, "paper_or_backtest_derived", issues, kind)
    if d.get("paper_or_backtest_derived") is not True:
        issues.append(f"{kind}_must_be_paper_or_backtest_derived")
    return len(issues) == 0, issues


def validate_r6(d: Dict[str, Any]) -> Tuple[bool, List[str]]:
    kind = "R6"
    issues = _common_guards(d, kind)
    if d.get("artifact_type") != ARTIFACT_TYPES[kind]:
        issues.append(f"{kind}_artifact_type_mismatch")
    _require(d, "timestamp_utc", issues, kind)
    _require(d, "thresholds", issues, kind)
    _require(d, "flags", issues, kind)
    _require(d, "evidence_refs", issues, kind)
    _require(d, "deterministic", issues, kind)
    if d.get("deterministic") is not True:
        issues.append(f"{kind}_deterministic_required")
    return len(issues) == 0, issues


def validate_r7(d: Dict[str, Any]) -> Tuple[bool, List[str]]:
    kind = "R7"
    issues = _common_guards(d, kind)
    if d.get("artifact_type") != ARTIFACT_TYPES[kind]:
        issues.append(f"{kind}_artifact_type_mismatch")
    _require(d, "timestamp_utc", issues, kind)
    items = _require(d, "process_checklist", issues, kind)
    if isinstance(items, list):
        ids = {str(it.get("id")) for it in items if isinstance(it, dict)}
        for aid in [f"A{i}" for i in range(1, 8)]:
            if aid not in ids:
                issues.append(f"{kind}_missing_{aid}_process_item")
    _require(d, "cannot_grant_approval", issues, kind)
    if d.get("cannot_grant_approval") is not True:
        issues.append(f"{kind}_cannot_grant_approval_must_be_true")
    _require(d, "next9_validator_ref", issues, kind)
    return len(issues) == 0, issues


VALIDATORS = {"R3": validate_r3, "R4": validate_r4, "R5": validate_r5, "R6": validate_r6, "R7": validate_r7}


def validate_artifact(d: Dict[str, Any], kind: str) -> Tuple[bool, List[str]]:
    if kind not in VALIDATORS:
        return False, [f"unknown_kind:{kind}"]
    return VALIDATORS[kind](d)


def find_latest(repo: Path, kind: str) -> Optional[Path]:
    cands = sorted((repo / "research_state").glob(PATTERNS[kind]))
    return cands[-1] if cands else None


def check_repo(repo: Path = REPO) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "artifact_type": "R3_R7_REDUCTION_EVIDENCE_VALIDATION",
        "timestamp_utc": _utc_iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "advisory": True,
        "kinds": {},
    }
    all_ok = True
    for kind in KINDS:
        p = find_latest(repo, kind)
        if not p:
            report["kinds"][kind] = {"present": False, "valid": False, "issues": [f"{kind}_no_artifact_found"], "path": None}
            all_ok = False
            continue
        d = _load(p)
        if d is None:
            report["kinds"][kind] = {"present": True, "valid": False, "issues": [f"{kind}_invalid_json"], "path": str(p.relative_to(repo))}
            all_ok = False
            continue
        ok, issues = validate_artifact(d, kind)
        report["kinds"][kind] = {"present": True, "valid": ok, "issues": issues, "path": str(p.relative_to(repo))}
        all_ok = all_ok and ok
    report["all_present_and_valid"] = all_ok
    report["action_required"] = [] if all_ok else ["provide_valid_r3_r7_reduction_evidence_artifacts"]
    return report


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Validate R3-R7 reduction evidence (paper-only, advisory)")
    ap.add_argument("--artifact", help="Path to artifact JSON")
    ap.add_argument("--kind", choices=list(KINDS))
    ap.add_argument("--check-repo", action="store_true")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero if invalid/missing (opt-in)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    if args.check_repo or (not args.artifact and not args.kind):
        result = check_repo(REPO)
        print(json.dumps(result, indent=2, allow_nan=False))
        if args.write:
            RS.mkdir(parents=True, exist_ok=True)
            out = RS / f"R3_R7_REDUCTION_EVIDENCE_VALIDATION_{_utc()}.json"
            out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            print(f"wrote {out.relative_to(REPO)}")
        if args.strict and not result.get("all_present_and_valid"):
            return 1
        return 0

    if not args.artifact or not args.kind:
        ap.error("--artifact and --kind required unless --check-repo")
    path = Path(args.artifact)
    if not path.is_absolute():
        path = REPO / path
    d = _load(path)
    if d is None:
        result = {"kind": args.kind, "valid": False, "issues": ["artifact_not_found_or_invalid_json"], "paper_only": True, "live_trading_enabled": False}
    else:
        ok, issues = validate_artifact(d, args.kind)
        result = {"kind": args.kind, "valid": ok, "issues": issues, "artifact": str(args.artifact), "paper_only": True, "live_trading_enabled": False, "next9_unblocked": False}
    print(json.dumps(result, indent=2, allow_nan=False))
    if args.strict and not result.get("valid"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
