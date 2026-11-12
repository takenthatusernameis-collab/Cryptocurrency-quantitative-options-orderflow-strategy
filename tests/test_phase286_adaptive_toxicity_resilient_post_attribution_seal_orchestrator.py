from __future__ import annotations

import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase286_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase286AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase286AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase286_config_paper_only() -> None:
    cfg = Phase286AdaptiveToxicityResilientPostAttributionSealConfig(seed=286286)
    assert cfg.paper_only is True
    assert cfg.seed == 286286


def test_phase286_orchestrator_runs_paper_only() -> None:
    orch = Phase286AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase286AdaptiveToxicityResilientPostAttributionSealConfig(seed=286286, cycles=40)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=40)
    assert rep["paper_only"] is True
    assert rep["live_trading_enabled"] is False
    assert rep["next9_unblocked"] is False
    assert rep["guards"]["paper_only"] is True
    assert rep["guards"]["live_trading_enabled"] is False
    assert rep["guards"]["next9_unblocked"] is False
    assert rep["composes"] == ["PHASE285", "PHASE32"]
    assert rep["upstream_phase285"] is True
    assert rep["upstream_phase32"] is True
    assert rep["campaign"]["gates_ok"] is True
    assert rep["n_seal_attestations"] > 0
    assert rep["n_seal_certifications"] > 0
    assert rep["n_hedging_seal_attestations"] > 0
    assert rep["n_cross_venue_seal_consistencies"] > 0
    assert rep["deterministic"] is True
    assert rep["bounded"] is True
    assert rep["finite_probe"] is True
    assert rep["additive"] is True