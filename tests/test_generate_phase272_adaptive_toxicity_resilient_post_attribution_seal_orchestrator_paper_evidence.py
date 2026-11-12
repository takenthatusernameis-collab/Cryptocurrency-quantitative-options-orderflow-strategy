import json
import os
import sys
from pathlib import Path

os.environ["PHASE_QUICK_VERIFY"] = "1"
sys.setrecursionlimit(200000)

from scripts import generate_phase272_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence as gen


def test_phase272_generate_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rs = Path(tmp_path) / "research_state"
    rs.mkdir(parents=True, exist_ok=True)
    art = gen.generate(cycles=40, seed=272272, write=True)
    assert art["paper_only"] is True
    assert art["live_trading_enabled"] is False
    assert art["next9_unblocked"] is False
    assert art["campaign"]["composes"] == ["PHASE271", "PHASE32"]
    assert art["campaign"]["gates_ok"] is True
    assert art["seal_surface"]["deterministic_replay_equal"] is True
    assert art["seal_surface"]["bounds_ok"] is True
    assert len(art["venue_symbol_coverage"]) == 12
    p = Path(art["artifact_path"])
    d = json.loads(p.read_text())
    ok, issues = gen.validate_artifact(d)
    assert ok, issues