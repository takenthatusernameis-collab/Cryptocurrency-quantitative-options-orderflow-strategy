from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import validate_next9_approval_artifact as v  # noqa: E402


def test_current_repo_blocks_next9():
    r = v.check_current(REPO)
    assert r["next9_unblocked"] is False
    assert r["paper_only"] is True
    assert r["live_trading_enabled"] is False
    assert any("A1" in i or "missing" in i or "not_explicitly_approved" in i for i in r["issues"])


def test_rejects_live_enabling_artifact():
    ok, issues = v.validate_approval_artifact({"live_trading_enabled": True, "human_approval_checklist": []})
    assert ok is False
    assert "artifact_must_not_enable_live_trading" in issues


def test_full_approvals_require_fields():
    checklist = []
    for i in range(1, 8):
        aid = f"A{i}"
        item = {"id": aid, "approved": True, "approver_identity": "x", "timestamp_utc": "2026-01-01T00:00:00Z"}
        for canonical, _mandatory in v.REQUIRED_FIELDS[aid]:
            if canonical == "approved":
                continue
            if canonical not in item:
                item[canonical] = "ok" if canonical != "limits" else {"max_notional": 1}
        checklist.append(item)
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is True
    assert issues == []


def test_partial_approval_blocked():
    checklist = [{"id": "A1", "approved": True, "approver_identity": "x", "timestamp_utc": "t", "scope": "s"}]
    ok, issues = v.validate_approval_artifact({"human_approval_checklist": checklist})
    assert ok is False
    assert "missing_A2" in issues


def test_bare_approved_true_is_false_green():
    # Regression: `approved: true` alone must NOT unblock NEXT9.
    checklist = [
        {"id": f"A{i}", "approved": True}
        for i in range(1, 8)
    ]
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is False
    assert any("A1_missing_approver_identity" in i for i in issues)
    assert any("A1_missing_scope" in i for i in issues)


def test_next8_proposal_schema_aliases_validate():
    # The review-only proposal uses `approver` + descriptive `item` fields.
    # These must map onto the canonical invariant set, not be structurally vetoed.
    prop = json.loads((REPO / "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json").read_text(encoding="utf-8"))
    ok, issues = v.validate_approval_artifact(prop)
    assert ok is False
    # Blocked because approvals are false, not because of schema mismatch.
    assert "artifact_must_not_enable_live_trading" not in issues
    assert "missing_human_approval_checklist" not in issues
    assert any("A1_not_explicitly_approved" in i for i in issues)


def test_next8_proposal_with_real_approvals_unblocks():
    prop = json.loads((REPO / "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json").read_text(encoding="utf-8"))
    for item in prop["human_approval_checklist"]:
        item["approved"] = True
        item["approver"] = "human-approver"
        item["timestamp_utc"] = "2026-01-01T00:00:00Z"
    ok, issues = v.validate_approval_artifact(prop)
    assert ok is True, issues


def test_check_current_uses_proposal_schema():
    r = v.check_current(REPO)
    assert r["next9_unblocked"] is False
    assert r["paper_only"] is True
    assert r["live_trading_enabled"] is False
    # The review-only proposal must be recognized as a valid checklist container.
    assert "missing_human_approval_checklist" not in r["issues"]
    assert "missing_proposal_json" not in r["issues"]


def test_conflicting_unblock_claim_rejected():
    # A checkpoint that claims unblock while approvals are absent must not pass.
    cp = {
        "live_enablement_decision": "APPROVED",
        "paper_only": True,
        "live_trading_enabled": False,
        "artifacts": {"proposal_json": "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json"},
    }
    ok, issues = v.validate_approval_artifact(cp)
    assert ok is False

def test_conflicting_live_enabling_flag_in_artifact():
    ok, issues = v.validate_approval_artifact({
        "live_trading_enabled": True,
        "paper_only": False,
        "human_approval_checklist": [{"id": f"A{i}", "approved": True} for i in range(1, 8)],
    })
    assert ok is False
    assert "artifact_must_not_enable_live_trading" in issues
    assert "artifact_must_not_claim_not_paper_only" in issues


def test_missing_scope_and_limits_specific_fields():
    checklist = []
    for i in range(1, 8):
        aid = f"A{i}"
        item = {"id": aid, "approved": True, "approver_identity": "x", "timestamp_utc": "2026-01-01T00:00:00Z"}
        for canonical, _mandatory in v.REQUIRED_FIELDS[aid]:
            if canonical in ("approved", "scope", "limits"):
                continue
            item[canonical] = "ok"
        checklist.append(item)
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is False
    assert "A1_missing_scope" in issues
    assert "A2_missing_limits" in issues


def test_stale_or_malformed_timestamp_still_structurally_checked():
    # Validator currently checks presence/non-empty; timestamp freshness is a human/process control.
    # This test locks the contract: a present timestamp satisfies structural validation (no false-green on missing timestamp).
    checklist = []
    for i in range(1, 8):
        aid = f"A{i}"
        item = {"id": aid, "approved": True, "approver_identity": "x", "timestamp_utc": "1999-01-01T00:00:00Z"}
        for canonical, _mandatory in v.REQUIRED_FIELDS[aid]:
            if canonical == "approved":
                continue
            if canonical not in item:
                item[canonical] = "ok" if canonical != "limits" else {"max_notional": 1}
        checklist.append(item)
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is True, issues  # structural pass; freshness enforcement is policy/ops, not this validator


def test_artifact_strict_exits_nonzero_on_block(tmp_path, monkeypatch):
    artifact = tmp_path / "next9.json"
    artifact.write_text(json.dumps({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": []}), encoding="utf-8")
    rc = v.main(["--artifact", str(artifact), "--strict"])
    assert rc == 1


def test_artifact_strict_exits_zero_when_fully_approved(tmp_path):
    checklist = []
    for i in range(1, 8):
        aid = f"A{i}"
        item = {"id": aid, "approved": True, "approver_identity": "approver", "timestamp_utc": "2026-11-07T00:00:00Z"}
        for canonical, _mandatory in v.REQUIRED_FIELDS[aid]:
            if canonical == "approved":
                continue
            if canonical not in item:
                item[canonical] = "ok" if canonical != "limits" else {"max_notional_usd": 100}
        checklist.append(item)
    artifact = tmp_path / "next9_ok.json"
    artifact.write_text(json.dumps({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist}), encoding="utf-8")
    rc = v.main(["--artifact", str(artifact), "--strict"])
    assert rc == 0


def test_artifact_not_found_strict():
    rc = v.main(["--artifact", "research_state/DOES_NOT_EXIST_20990101.json", "--strict"])
    assert rc == 1


def test_check_current_write_creates_additive_artifact(tmp_path, monkeypatch):
    monkeypatch.setattr(v, "RS", tmp_path)
    rc = v.main(["--check-current", "--write"])
    assert rc == 0
    outs = list(tmp_path.glob("NEXT9_APPROVAL_VALIDATION_*.json"))
    assert len(outs) == 1
    data = json.loads(outs[0].read_text(encoding="utf-8"))
    assert data["next9_unblocked"] is False
    assert data["paper_only"] is True
    assert data["live_trading_enabled"] is False


def _full_checklist():
    checklist = []
    for i in range(1, 8):
        aid = f"A{i}"
        item = {"id": aid, "approved": True, "approver_identity": "approver", "timestamp_utc": "2026-11-07T00:00:00Z"}
        for canonical, _mandatory in v.REQUIRED_FIELDS[aid]:
            if canonical == "approved":
                continue
            if canonical not in item:
                item[canonical] = "ok" if canonical != "limits" else {"max_notional_usd": 100}
        checklist.append(item)
    return checklist


def test_freshness_disabled_by_default_returns_no_issues():
    data = {"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}
    issues = v._approval_freshness_issues(data, max_age_hours=None, effective_until_utc=None)
    assert issues == []


def test_freshness_max_age_stale_timestamps_produce_issues():
    data = {"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}
    issues = v._approval_freshness_issues(data, max_age_hours=1.0, effective_until_utc=None)
    assert len(issues) == 7
    for i in range(1, 8):
        assert any(f"A{i}_approval_stale_hours:" in it for it in issues)


def test_freshness_effective_until_before_timestamp_produces_issue():
    data = {"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}
    issues = v._approval_freshness_issues(data, max_age_hours=None, effective_until_utc="2020-01-01T00:00:00Z")
    assert any("approval_timestamp_after_effective_until_utc" in it for it in issues)


def test_freshness_never_grants_approval_even_structurally_full():
    data = {"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}
    ok, _ = v.validate_approval_artifact(data)
    assert ok is True
    fresh = v._approval_freshness_issues(data, max_age_hours=1.0, effective_until_utc=None)
    assert fresh
    assert not (ok and not fresh)


def test_cli_freshness_default_off_does_not_tighten():
    with tempfile.TemporaryDirectory() as td:
        artifact = Path(td) / "next9_full.json"
        artifact.write_text(json.dumps({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}), encoding="utf-8")
        rc = v.main(["--artifact", str(artifact), "--strict"])
        assert rc == 0


def test_cli_max_approval_age_hours_tightens_block_still_blocked():
    with tempfile.TemporaryDirectory() as td:
        artifact = Path(td) / "next9_stale.json"
        artifact.write_text(json.dumps({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}), encoding="utf-8")
        rc = v.main(["--artifact", str(artifact), "--max-approval-age-hours", "1", "--strict"])
        assert rc == 1


def test_cli_effective_until_utc_tightens_block_still_blocked():
    with tempfile.TemporaryDirectory() as td:
        artifact = Path(td) / "next9_expired.json"
        artifact.write_text(json.dumps({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}), encoding="utf-8")
        rc = v.main(["--artifact", str(artifact), "--effective-until-utc", "2020-01-01T00:00:00Z", "--strict"])
        assert rc == 1


def test_cli_max_approval_age_hours_writes_additive_blocked_artifact():
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        artifact = td_path / "next9_stale.json"
        artifact.write_text(json.dumps({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": _full_checklist()}), encoding="utf-8")
        old_rs = v.RS
        v.RS = td_path / "research_state"
        try:
            rc = v.main(["--artifact", str(artifact), "--max-approval-age-hours", "1", "--strict", "--write"])
        finally:
            v.RS = old_rs
        assert rc == 1
        outs = list((td_path / "research_state").glob("NEXT9_APPROVAL_VALIDATION_*.json"))
        assert len(outs) == 1
        data = json.loads(outs[0].read_text(encoding="utf-8"))
        assert data["next9_unblocked"] is False
        assert data["paper_only"] is True
        assert data["live_trading_enabled"] is False
        assert data["approval_freshness_check"]["enabled"] is True
        assert len(data["approval_freshness_check"]["freshness_issues"]) == 7
