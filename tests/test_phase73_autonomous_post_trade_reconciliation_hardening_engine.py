from src.risk.phase73_autonomous_post_trade_reconciliation_hardening_engine import (
    Phase73AutonomousPostTradeReconciliationHardeningEngine,
    Phase73AutonomousPostTradeReconciliationHardeningConfig,
)


def test_phase73_post_trade_reconciliation_hardening_engine_smoke():
    eng = Phase73AutonomousPostTradeReconciliationHardeningEngine(Phase73AutonomousPostTradeReconciliationHardeningConfig(seed=7370, cycles=40))
    rep = eng.run_post_trade_reconciliation_hardening(cycles=40)
    assert rep["phase"] == "PHASE73_AUTONOMOUS_POST_TRADE_RECONCILIATION_HARDENING_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
