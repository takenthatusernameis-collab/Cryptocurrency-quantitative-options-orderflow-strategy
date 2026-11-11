from __future__ import annotations

import os

os.environ["PHASE_QUICK_VERIFY"] = "1"

from scripts.generate_phase205_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence import (
    generate,
    validate_artifact,
)


def test_phase205_generate_quick_no_write() -> None:
    d = generate(cycles=40, seed=205205, write=False)
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["campaign"]["gates_ok"] is True
    comp = d["campaign"].get("composes") or []
    assert "PHASE204" in comp and "PHASE32" in comp
    ok, issues = validate_artifact(d)
    assert ok, issues
    assert len(d["venue_symbol_coverage"]) == 12
    assert d["risk_posture"]["all_coverage_gates_ok"] is True
