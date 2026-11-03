from src.risk.phase72_autonomous_margin_collateral_reconciliation_engine import (
    Phase72AutonomousMarginCollateralReconciliationEngine,
    Phase72AutonomousMarginCollateralReconciliationConfig,
)


def test_phase72_margin_collateral_reconciliation_engine_smoke():
    eng = Phase72AutonomousMarginCollateralReconciliationEngine(Phase72AutonomousMarginCollateralReconciliationConfig(seed=7270, cycles=40))
    rep = eng.run_margin_collateral_reconciliation(cycles=40)
    assert rep["phase"] == "PHASE72_AUTONOMOUS_MARGIN_COLLATERAL_RECONCILIATION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
