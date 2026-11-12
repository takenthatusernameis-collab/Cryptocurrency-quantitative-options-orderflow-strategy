from __future__ import annotations

import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase288_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase288AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase288AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase288_config_paper_only() -> None:
    cfg = Phase288AdaptiveToxicityResilientPostAttributionSealConfig(seed=288288)
    assert cfg.paper_only is True
    assert cfg.seed == 288288


def test_phase288_orchestrator_runs_paper_only() -> None:
    orch = Phase288AdaptiveToxicityResilientPostAttributionSealOrchestrator(
        Phase288AdaptiveToxicityResilientPostAttributionSealConfig(seed=288288, cycles=40)
    )
    rep = orch.run_post_attribution_seal_orchestration(cycles=40)
    assert rep["paper_only"] is True
    assert rep["live_trading_enabled"] is False
    assert rep["next9_unblocked"] is False
    assert rep["guards"]["paper_only"] is True
    assert rep["guards"]["live_trading_enabled"] is False
    assert rep["guards"]["next9_unblocked"] is False
    assert rep["composes"] == ["PHASE287", "PHASE32"]
    assert rep["upstream_phase287"] is True
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
