from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import generate_phase42_greeks_risk_paper_evidence as g  # noqa: E402


def test_generate_produces_valid_paper_only_artifact():
    d = g.generate(cycles=8, seed=42042)
    ok, issues = g.validate_artifact(d)
    assert ok, issues
    assert d["artifact_type"] == g.ARTIFACT_TYPE
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["advisory"] is True
    assert d["no_external_venue_mutation"] is True
    assert d["venues"] == ["deribit", "okx", "binance"]
    assert d["symbols"] == ["BTC", "ETH"]
    assert d["risk_summary"]["total_cycles"] == 8
    assert d["campaign"]["paper_only"] is True
    assert set(u["underlying"] for u in d["campaign"]["snapshots"][0]["by_underlying"]) == {"BTC", "ETH"}


def test_main_writes_additive_artifact(tmp_path, monkeypatch):
    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    monkeypatch.setattr(g, "RS", rs)
    monkeypatch.setattr(g, "REPO", tmp_path)
    rc = g.main(["--cycles", "6", "--seed", "7"])
    assert rc == 0
    out = list(rs.glob("PHASE42_GREEKS_RISK_PAPER_EVIDENCE_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = g.validate_artifact(d)
    assert ok, issues
    assert d["next9_unblocked"] is False
    assert d["live_trading_enabled"] is False


def test_validate_rejects_live_or_next9_unblock():
    d = g.generate(cycles=4, seed=1)
    d["next9_unblocked"] = True
    ok, issues = g.validate_artifact(d)
    assert not ok
    assert "must_not_unblock_next9" in issues
    d2 = g.generate(cycles=4, seed=1)
    d2["live_trading_enabled"] = True
    ok2, issues2 = g.validate_artifact(d2)
    assert not ok2
    assert "must_not_enable_live_trading" in issues2
    d3 = g.generate(cycles=4, seed=1)
    d3["paper_only"] = False
    ok3, issues3 = g.validate_artifact(d3)
    assert not ok3
    assert "paper_only_required" in issues3
