from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")
sys.setrecursionlimit(200000)

from scripts import generate_phase288_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence as gen


def test_phase288_generate_validate(tmp_path: Path) -> None:
    art = gen.generate(cycles=40, seed=288288, write=False)
    assert art["validation"]["valid"] is True
    assert art["validation"]["issues"] == []
    assert art["paper_only"] is True
    assert art["live_trading_enabled"] is False
    assert art["next9_unblocked"] is False
    assert art["campaign"]["composes"] == ["PHASE287", "PHASE32"]
    assert art["risk_posture"]["upstream_phase287"] is True
    assert art["risk_posture"]["upstream_phase32"] is True
    assert art["seal_surface"]["deterministic_replay_equal"] is True
    assert art["seal_surface"]["bounds_ok"] is True
    assert len(art["venue_symbol_coverage"]) == 12


def test_phase288_validate_only_roundtrip(tmp_path: Path) -> None:
    art = gen.generate(cycles=40, seed=288288, write=True, outdir=str(tmp_path))
    p = art["artifact_path"]
    assert Path(p).exists()
    d = json.loads(Path(p).read_text())
    ok, issues = gen.validate_artifact(d)
    assert ok is True
    assert issues == []
