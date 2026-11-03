import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.hedging.phase78_integrated_gamma_inventory_hedge_orchestrator import (
    Phase78IntegratedGammaInventoryHedgeOrchestrator,
    Phase78IntegratedGammaInventoryHedgeOrchestratorConfig,
)


def test_phase78_integrated_gamma_inventory_hedge_orchestrator_smoke():
    eng = Phase78IntegratedGammaInventoryHedgeOrchestrator(
        Phase78IntegratedGammaInventoryHedgeOrchestratorConfig(seed=7802, cycles=40)
    )
    rep = eng.run_integrated_gamma_inventory_hedging(cycles=40)
    assert rep["phase"] == "PHASE78_INTEGRATED_GAMMA_INVENTORY_HEDGE_ORCHESTRATOR"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["cross_venue_hedge_ok"] is True
