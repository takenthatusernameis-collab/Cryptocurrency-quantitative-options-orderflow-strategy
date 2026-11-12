import os
import sys

os.environ["PHASE_QUICK_VERIFY"] = "1"
sys.setrecursionlimit(200000)

from src.hedging.phase278_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import (
    Phase278AdaptiveToxicityResilientPostAttributionSealConfig,
    Phase278AdaptiveToxicityResilientPostAttributionSealOrchestrator,
)


def test_phase278_paper_only_and_gates():
    cfg = Phase278AdaptiveToxicityResilientPostAttributionSealConfig(seed=278278, cycles=12)
    orch = Phase278AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    rep = orch.run_post_attribution_seal_orchestration(cycles=12)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["composes"] == ["PHASE277", "PHASE32"]
    assert rep["upstream_phase277"] is True
    assert rep["upstream_phase32"] is True
    assert len(rep["seal_attestations"]) > 0
    assert len(rep["seal_certifications"]) > 0
    assert len(rep["hedging_seal_attestations"]) > 0
    assert len(rep["cross_venue_seal_consistencies"]) > 0


def test_phase278_deterministic():
    cfg = Phase278AdaptiveToxicityResilientPostAttributionSealConfig(seed=278278, cycles=16)
    orch = Phase278AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    r1 = orch.run_post_attribution_seal_orchestration(cycles=16)
    orch2 = Phase278AdaptiveToxicityResilientPostAttributionSealOrchestrator(cfg)
    r2 = orch2.run_post_attribution_seal_orchestration(cycles=16)

    def strip(d):
        if isinstance(d, dict):
            return {k: strip(v) for k, v in d.items() if k != "timestamp"}
        if isinstance(d, list):
            return [strip(v) for v in d]
        return d

    assert strip(r1) == strip(r2)
