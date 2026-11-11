import os
os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.hedging.phase235_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase235AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase235AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase235_paper_only_guard():
    try:
        Phase235AdaptiveToxicityResilientPostAttributionSealConfig(paper_only=False)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_phase235_runs_paper_only():
    cfg = Phase235AdaptiveToxicityResilientPostAttributionSealConfig(seed=235235, cycles=8, paper_only=True)
    orch = Phase235AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=8)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["composes"] == ["PHASE234", "PHASE32"]
    assert rep["phase"] == "PHASE235_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"
    assert rep["n_seal_attestations"] > 0
    assert rep["n_hedging_seal_attestations"] > 0
    assert rep["upstream_phase234"] is True


def test_phase235_deterministic_quick():
    cfg = Phase235AdaptiveToxicityResilientPostAttributionSealConfig(seed=235235, cycles=6, paper_only=True)
    r1 = Phase235AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg).run_post_attribution_seal_orchestration(cycles=6)
    r2 = Phase235AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg).run_post_attribution_seal_orchestration(cycles=6)
    for k in ("avg_cross_venue_ok", "avg_seal_pass_rate", "n_seal_attestations", "n_hedging_seal_attestations"):
        assert r1[k] == r2[k]
