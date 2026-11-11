from __future__ import annotations

import os

os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.hedging.phase207_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase207AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase207AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase207_paper_only_hard_gate() -> None:
    try:
        Phase207AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)
        assert False, "paper_only False must raise"
    except ValueError:
        pass


def test_phase207_run_smoke_quick() -> None:
    orch = Phase207AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase207AdaptiveToxicityResilientPostAttributionSealConfig(seed=207207, cycles=40)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=40)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["live_trading_enabled"] is False
    assert rep["next9_unblocked"] is False
    assert "PHASE206" in rep.get("composes", []) and "PHASE32" in rep.get("composes", [])
    assert rep.get("bounds_ok") is True
    assert rep.get("deterministic") is True
    assert int(rep.get("n_seal_attestations") or 0) > 0
    assert int(rep.get("n_hedging_seal_attestations") or 0) > 0
