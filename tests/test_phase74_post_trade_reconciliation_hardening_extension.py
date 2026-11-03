from src.risk.phase74_autonomous_post_trade_reconciliation_hardening_extension import (
    Phase74AutonomousPostTradeReconciliationHardeningExtensionEngine,
    Phase74AutonomousPostTradeReconciliationHardeningExtensionConfig,
)


def test_phase74_post_trade_reconciliation_hardening_extension_smoke():
    eng = Phase74AutonomousPostTradeReconciliationHardeningExtensionEngine(
        Phase74AutonomousPostTradeReconciliationHardeningExtensionConfig(seed=7470, cycles=40)
    )
    rep = eng.run_post_trade_reconciliation_hardening_extension(cycles=40)
    assert rep["phase"] == "PHASE74_AUTONOMOUS_POST_TRADE_RECONCILIATION_HARDENING_EXTENSION_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    arts = eng.generate_artifacts(outdir="research_state")
    assert arts["gates_ok"] is True
