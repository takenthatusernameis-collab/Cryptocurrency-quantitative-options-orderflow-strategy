from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import generate_r3_venue_ops_rehearsal as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def test_gen_r3_strict_produces_valid_artifact():
    d = g.gen_r3_strict(g._utc())
    ok, issues = v.validate_artifact(d, "R3")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R3"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["no_external_venue_mutation"] is True
    assert d["advisory"] is True
    assert isinstance(d["checklist"], list) and len(d["checklist"]) >= 7
    assert isinstance(d["evidence_refs"], list) and d["evidence_refs"]
    assert d["strictness"] == "enhanced_extraction_v2"


def test_r3_covers_partial_fill_reject_rate_limit_maintenance():
    d = g.gen_r3_strict(g._utc())
    text = json.dumps(d).lower()
    for needle in ("partial-fill", "reject", "rate-limit", "maintenance"):
        assert needle in text


def test_r3_cites_required_sources_when_present():
    d = g.gen_r3_strict(g._utc())
    refs = " ".join(d["evidence_refs"])
    assert "CROSSVENUE_ORCHESTRATION_REPORT.json" in refs
    assert "PHASE37_CROSS_VENUE_ROUTING_REPORT.json" in refs
    assert "INCIDENT_DRILL" in refs
    assert "PAPER_RUNBOOK.md" in refs


def test_r3_flags_never_unblock_next9():
    d = g.gen_r3_strict(g._utc())
    assert d["next9_unblocked"] is False
    assert d["flags"]["advisory_only"] is True
    assert d["flags"]["no_external_venue_mutation"] is True


def test_main_writes_valid_r3_artifact(tmp_path, monkeypatch):
    rs = tmp_path / "research_state"
    docs = tmp_path / "docs"
    rs.mkdir(parents=True)
    docs.mkdir(parents=True)
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({
        "report": "CROSSVENUE_ORCHESTRATION_REPORT", "paper_only": True, "venues": ["deribit"], "symbols": ["BTC"],
        "counts": {"cycles_completed": 1}, "halted": False, "kill_switch": {"triggered": False}, "pnl": {"net_pnl_usd": 0.0},
    }))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok": True, "cycles": 1}))
    (rs / "INCIDENT_DRILL_20261107T000000Z.json").write_text(json.dumps({
        "drill_id": "INCIDENT_DRILL_20261107T000000Z", "paper_only": True, "all_passed": True,
        "guardrail": "No live capital", "scenarios": [{"name": "x", "category": "reconciliation", "passed": True}],
    }))
    (docs / "PAPER_RUNBOOK.md").write_text("rate limit partial fill reject maintenance kill-switch reconciliation")
    monkeypatch.setattr(g, "RS", rs)
    monkeypatch.setattr(g, "REPO", tmp_path)
    monkeypatch.setattr(g, "DOCS", docs)
    rc = g.main([])
    assert rc == 0
    out = list(rs.glob("R3_VENUE_OPS_REHEARSAL_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R3")
    assert ok, issues
    assert d["flags"]["deterministic_pass"] is True
    assert d["next9_unblocked"] is False

def test_r3_runbook_keyword_variants_reduce_false_warns(tmp_path, monkeypatch):
    rs = tmp_path / "research_state"; docs = tmp_path / "docs"
    rs.mkdir(parents=True); docs.mkdir(parents=True)
    (rs / "CROSSVENUE_ORCHESTRATION_REPORT.json").write_text(json.dumps({
        "report":"CROSSVENUE_ORCHESTRATION_REPORT","paper_only":True,"venues":["deribit","okx"],
        "symbols":["BTC"],"counts":{"cycles_completed":1},"halted":False,"kill_switch":{"triggered":False},"pnl":{"net_pnl_usd":0.0}}))
    (rs / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json").write_text(json.dumps({"ok":True,"cycles":1,"venues":["deribit","okx"]}))
    (rs / "INCIDENT_DRILL_20261107T000000Z.json").write_text(json.dumps({
        "drill_id":"INCIDENT_DRILL_20261107T000000Z","paper_only":True,"all_passed":True,
        "guardrail":"No live capital","scenarios":[{"name":"x","category":"reconciliation","passed":True}]}))
    # synonyms/case variants
    (docs / "PAPER_RUNBOOK.md").write_text("Rate-Limit handling; partially filled orders; order rejected; scheduled outage/maintenance; circuit breaker; position mismatch reconciliation")
    monkeypatch.setattr(g, "RS", rs); monkeypatch.setattr(g, "REPO", tmp_path); monkeypatch.setattr(g, "DOCS", docs)
    d = g.gen_r3_strict(g._utc())
    ok, issues = v.validate_artifact(d, "R3")
    assert ok, issues
    assert not any('paper_runbook_missing_keywords' in w for w in d['warn_flags']), d['warn_flags']
    assert d['strictness'] == 'enhanced_extraction_v2'


def test_r3_per_venue_coverage_rows_present():
    d = g.gen_r3_strict(g._utc())
    assert isinstance(d.get('per_venue_coverage'), list) and d['per_venue_coverage']
    venues = {r.get('venue') for r in d['per_venue_coverage']}
    assert 'deribit' in venues or 'okx' in venues or 'binance' in venues
    r31 = next(i for i in d['checklist'] if i['id']=='R3.1')
    assert isinstance(r31.get('per_venue'), list)
