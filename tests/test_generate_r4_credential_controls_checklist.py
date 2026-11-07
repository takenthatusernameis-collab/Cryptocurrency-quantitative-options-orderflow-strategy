from __future__ import annotations

import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import generate_r4_credential_controls_checklist as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def test_gen_r4_strict_produces_valid_artifact():
    d = g.gen_r4_strict(g._utc())
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R4"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["attestation_only"] is True
    assert d["advisory"] is True
    assert d["strictness"] == "enhanced_extraction_v2"
    assert isinstance(d["checklist"], list) and len(d["checklist"]) > 0
    controls = {c["control"] for c in d["checklist"]}
    assert "secrets_not_committed" in controls
    assert "live_trading_default_false" in controls
    assert "env_example_live_trading_false" in controls
    assert isinstance(d["flags"]["deterministic_pass"], bool)
    assert isinstance(d["warn_flags"], list)


def test_main_writes_valid_r4_artifact(tmp_path, monkeypatch):
    import generate_r4_credential_controls_checklist as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    (rs / "campaign_checkpoints").mkdir(parents=True)
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    (tmp_path / "src" / "config").mkdir(parents=True)
    (tmp_path / "src" / "config" / "secrets.py").write_text('LIVE_TRADING_ENABLED = false\n')
    (tmp_path / ".env.example").write_text("LIVE_TRADING_ENABLED=false\n")
    rc = gmod.main([])
    assert rc == 0
    out = list(rs.glob("R4_CREDENTIAL_CONTROLS_CHECKLIST_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R4")
    assert ok, issues
    assert d["next9_unblocked"] is False
