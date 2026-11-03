from src.settlement.phase72_finality_settlement_enforcement_engine import (
    Phase72FinalitySettlementEnforcementEngine,
    Phase72FinalitySettlementEnforcementConfig,
)


def test_phase72_finality_settlement_enforcement_engine_smoke():
    eng = Phase72FinalitySettlementEnforcementEngine(Phase72FinalitySettlementEnforcementConfig(seed=7271, cycles=40))
    rep = eng.run_finality_settlement_enforcement(cycles=40)
    assert rep["phase"] == "PHASE72_FINALITY_SETTLEMENT_ENFORCEMENT_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
