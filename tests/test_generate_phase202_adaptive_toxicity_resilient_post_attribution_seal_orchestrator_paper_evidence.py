from __future__ import annotations

import json
import os

os.environ["PHASE_QUICK_VERIFY"] = "1"

from scripts.generate_phase202_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence import (  # noqa: E402
    generate,
    validate_artifact,
)


def test_phase202_generate_no_write_smoke() -> None:
    d = generate(cycles=12, seed=202202, write=False)
    assert d["artifact_type"].startswith("PHASE202_")
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["campaign"]["gates_ok"] is True
    assert "PHASE201" in d["campaign"]["composes"]
    assert "PHASE32" in d["campaign"]["composes"]
    ok, issues = validate_artifact(d)
    assert ok, issues
    assert len(d["venue_symbol_coverage"]) == 12


def test_phase202_validate_artifact_rejects_live() -> None:
    d = generate(cycles=12, seed=202202, write=False)
    bad = dict(d)
    bad["live_trading_enabled"] = True
    bad["validation"] = {"valid": False, "issues": []}
    ok, issues = validate_artifact(bad)
    assert not ok
    assert "must_not_enable_live_trading" in issues
