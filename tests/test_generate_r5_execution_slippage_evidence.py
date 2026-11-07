from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(REPO / "scripts"))
import generate_r5_execution_slippage_evidence as g  # noqa: E402
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def test_gen_r5_strict_produces_valid_artifact():
    ts = g._utc()
    d = g.gen_r5_strict(ts)
    ok, issues = v.validate_artifact(d, "R5")
    assert ok, issues
    assert d["artifact_type"] == v.ARTIFACT_TYPES["R5"]
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["metrics"]["slippage_assumption_documented"] is True
    assert d["metrics"]["fill_quality_documented"] is True
    assert d["paper_or_backtest_derived"] is True
    assert d["advisory"] is True
    assert isinstance(d["evidence_refs"], list) and len(d["evidence_refs"]) > 0


def test_main_writes_valid_r5_artifact(tmp_path, monkeypatch):
    import generate_r5_execution_slippage_evidence as gmod

    rs = tmp_path / "research_state"
    rs.mkdir(parents=True)
    # generator prints relative_to(REPO); make REPO=tmp_path for this test
    monkeypatch.setattr(gmod, "RS", rs)
    monkeypatch.setattr(gmod, "REPO", tmp_path)
    rc = gmod.main([])
    assert rc == 0
    out = list(rs.glob("R5_EXECUTION_SLIPPAGE_SIM_EVIDENCE_*.json"))
    assert len(out) == 1
    d = json.loads(out[0].read_text())
    ok, issues = v.validate_artifact(d, "R5")
    assert ok, issues
    assert d["metrics"]["within_conservative_caps"] is True
