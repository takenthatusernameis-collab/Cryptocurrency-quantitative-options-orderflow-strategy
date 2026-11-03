from src.hedging.phase77_adaptive_toxicity_resilient_cross_venue_gamma_hedge_orchestrator import (
    Phase77AdaptiveToxicityResilientCrossVenueGammaHedgeOrchestrator,
    Phase77AdaptiveToxicityResilientCrossVenueGammaHedgeOrchestratorConfig,
)


def test_phase77_adaptive_toxicity_resilient_cross_venue_gamma_hedge_orchestrator_smoke():
    eng = Phase77AdaptiveToxicityResilientCrossVenueGammaHedgeOrchestrator(
        Phase77AdaptiveToxicityResilientCrossVenueGammaHedgeOrchestratorConfig(seed=7702, cycles=40)
    )
    rep = eng.run_cross_venue_gamma_hedge_orchestration(cycles=40)
    assert rep["phase"] == "PHASE77_ADAPTIVE_TOXICITY_RESILIENT_CROSS_VENUE_GAMMA_HEDGE_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
