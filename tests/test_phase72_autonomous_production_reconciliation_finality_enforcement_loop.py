from src.integration.phase72_autonomous_production_reconciliation_finality_enforcement_loop import (
    Phase72AutonomousProductionReconciliationFinalityEnforcementLoop,
    Phase72AutonomousProductionReconciliationFinalityEnforcementLoopConfig,
)


def test_phase72_autonomous_production_reconciliation_finality_enforcement_loop_smoke():
    eng = Phase72AutonomousProductionReconciliationFinalityEnforcementLoop(Phase72AutonomousProductionReconciliationFinalityEnforcementLoopConfig(seed=7272, cycles=40))
    rep = eng.run_reconciliation_finality_enforcement(cycles=40)
    assert rep["phase"] == "PHASE72_AUTONOMOUS_PRODUCTION_RECONCILIATION_FINALITY_ENFORCEMENT_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
