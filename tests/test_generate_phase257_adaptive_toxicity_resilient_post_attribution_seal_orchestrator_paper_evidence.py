import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from scripts.generate_phase257_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence import (
    generate,
    validate_artifact,
)


def test_phase257_generator_validates():
    d = generate(cycles=8, seed=257257, write=False)
    assert d["artifact_type"] == "PHASE257_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE"
    v, issues = validate_artifact(d)
    assert v is True, issues
    assert d["validation"]["valid"] is True
    assert d["validation"]["issues"] == []
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["campaign"]["composes"] == ["PHASE256", "PHASE32"]
    assert len(d["venue_symbol_coverage"]) == 12


def test_phase257_rejects_live():
    d = generate(cycles=8, seed=257257, write=False)
    bad = dict(d)
    bad["live_trading_enabled"] = True
    v, issues = validate_artifact(bad)
    assert v is False
    assert "must_not_enable_live_trading" in issues
