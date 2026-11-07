from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import generate_r7_human_process_checklist as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402
import validate_next9_approval_artifact as n9  # noqa: E402


def test_gen_r7_strict_produces_valid_artifact():
    d = g.gen_r7_strict(g._utc())
    ok, issues = v.validate_artifact(d, "R7")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R7"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["cannot_grant_approval"] is True
    assert d["advisory"] is True
    assert d["strictness"] == "enhanced_extraction_v1"


def test_r7_contains_all_a1_a7_process_items_and_cannot_grant_approval():
    d = g.gen_r7_strict(g._utc())
    ids = [it["id"] for it in d["process_checklist"]]
    assert ids == [f"A{i}" for i in range(1, 8)]
    for it in d["process_checklist"]:
        assert it["recorded_approval"] is False
        assert "cannot" in it["note"].lower()
    assert d["next9_validation_contract"]["this_artifact_grants_approvals"] is False
    assert d["next9_validation_contract"]["this_artifact_unblocks_next9"] is False
    assert d["next9_validator_ref"] == "scripts/validate_next9_approval_artifact.py"


def test_r7_crossrefs_next8_and_next9_validator():
    d = g.gen_r7_strict(g._utc())
    refs = " ".join(d["evidence_refs"])
    assert "LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json" in refs
    assert "validate_next9_approval_artifact.py" in refs
    assert d["proposal_crossref"]["next8_checkpoint"] == "research_state/campaign_checkpoints/LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json"


def test_r7_does_not_unblock_next9_validator():
    d = g.gen_r7_strict(g._utc())
    ok, issues = n9.validate_approval_artifact(d)
    assert ok is False
    assert any("missing_human_approval_checklist" in i or "missing_A" in i or "not_explicitly_approved" in i for i in issues)
    cur = n9.check_current(REPO)
    assert cur["next9_unblocked"] is False


def test_main_writes_valid_r7_artifact_and_enforces_invariant(tmp_path, monkeypatch):
    rs = tmp_path / "research_state"
    cp = rs / "campaign_checkpoints"
    scripts = tmp_path / "scripts"
    cp.mkdir(parents=True)
    scripts.mkdir(parents=True)
    (cp / "LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json").write_text(json.dumps({
        "live_enablement_decision": "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL",
        "artifacts": {"proposal_json": "research_state/LIVE_ENABLEMENT_PROPOSAL_X.json"},
    }))
    (rs / "LIVE_ENABLEMENT_PROPOSAL_X.json").write_text(json.dumps({
        "proposal_id": "X",
        "human_approval_checklist": [{"id": f"A{i}", "approved": False, "required": True, "item": "x"} for i in range(1, 8)],
    }))
    (scripts / "validate_next9_approval_artifact.py").write_text("# stub")
    monkeypatch.setattr(g, "RS", rs)
    monkeypatch.setattr(g, "CP", cp)
    monkeypatch.setattr(g, "REPO", tmp_path)
    rc = g.main([])
    assert rc == 0
    out = list(rs.glob("R7_HUMAN_PROCESS_CHECKLIST_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R7")
    assert ok, issues
    assert d["cannot_grant_approval"] is True
    assert d["next9_unblocked"] is False
