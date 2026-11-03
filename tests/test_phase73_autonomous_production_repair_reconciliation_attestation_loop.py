from src.integration.phase73_autonomous_production_repair_reconciliation_attestation_loop import (
    Phase73AutonomousProductionRepairReconciliationAttestationLoop,
    Phase73AutonomousProductionRepairReconciliationAttestationLoopConfig,
)


def test_phase73_autonomous_production_repair_reconciliation_attestation_loop_smoke():
    eng = Phase73AutonomousProductionRepairReconciliationAttestationLoop(Phase73AutonomousProductionRepairReconciliationAttestationLoopConfig(seed=7372, cycles=40))
    rep = eng.run_repair_reconciliation_attestation_loop(cycles=40)
    assert rep["phase"] == "PHASE73_AUTONOMOUS_PRODUCTION_REPAIR_RECONCILIATION_ATTESTATION_LOOP"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
