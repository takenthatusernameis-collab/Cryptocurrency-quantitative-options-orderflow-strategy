from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

os.environ["PHASE_QUICK_VERIFY"] = "1"

import scripts.generate_phase206_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence as gen  # noqa: E402


def test_generate_phase206_quick_verify_no_write():
    d = gen.generate(cycles=40, seed=206206, write=False)
    assert d["validation"]["valid"] is True
    assert d["validation"]["issues"] == []
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["campaign"]["paper_only"] is True
    assert d["campaign"]["gates_ok"] is True
    assert "PHASE205" in d["campaign"]["composes"]
    assert "PHASE32" in d["campaign"]["composes"]
    assert d["campaign"]["phase"] == "PHASE206_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"
    assert d["seal_surface"]["paper_only"] is True
    assert d["seal_surface"]["deterministic_replay_equal"] is True
    assert d["seal_surface"]["bounds_ok"] is True
    assert len(d["venue_symbol_coverage"]) == 12
    for row in d["venue_symbol_coverage"]:
        assert row["paper_only"] is True
        assert row["probe_gates_ok"] is True
    assert d["risk_posture"]["paper_only"] is True
    assert d["risk_posture"]["next9_unblocked"] is False
    assert d["risk_posture"]["live_trading_enabled"] is False
    assert d["determinism"]["same_seed_cycles_reproduce_surface"] is True
    assert d["determinism"]["bounds_ok"] is True


def test_generate_phase206_artifact_type():
    d = gen.generate(cycles=40, seed=206206, write=False)
    assert d["artifact_type"] == "PHASE206_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE"


def test_generate_phase206_evidence_refs_include_phase205():
    d = gen.generate(cycles=40, seed=206206, write=False)
    refs = d["evidence_refs"]
    assert any("PHASE205" in r for r in refs)
    assert any("phase206_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py" in r for r in refs)


def test_generate_phase206_cross_refs_include_composes():
    d = gen.generate(cycles=40, seed=206206, write=False)
    refs = d["cross_refs"]
    assert "Phase206AdaptiveToxicityResilientPostAttributionSealOrchestrator" in refs
    assert "Phase205AdaptiveToxicityResilientPostAttributionSealOrchestrator" in refs
    assert "composes=PHASE205,PHASE32" in refs