import os
os.environ["PHASE_QUICK_VERIFY"] = "1"

from src.integration.phase80_cross_venue_finality_post_trade_reconciliation_attestation_hardening_loop import (
    Phase80CrossVenueFinalityPostTradeReconciliationAttestationHardeningLoop,
    Phase80CrossVenueFinalityPostTradeReconciliationAttestationHardeningConfig,
)


def test_phase80_cross_venue_finality_post_trade_reconciliation_attestation_hardening_loop_smoke():
    eng = Phase80CrossVenueFinalityPostTradeReconciliationAttestationHardeningLoop(
        Phase80CrossVenueFinalityPostTradeReconciliationAttestationHardeningConfig(seed=80072, cycles=40)
    )
    rep = eng.run_cross_venue_finality_post_trade_reconciliation_attestation_hardening(cycles=40)
    assert rep["phase"] == "PHASE80_CROSS_VENUE_FINALITY_POST_TRADE_RECONCILIATION_ATTESTATION_HARDENING_LOOP"
    assert rep["paper_only"] is True
    assert rep["ok"] is True
    assert rep["gates"]["finality_enforced"] is True
    assert rep["gates"]["post_trade_reconciliation_ok"] is True
    assert rep["gates"]["attestation_chain_integrity_ok"] is True
    assert rep["gates"]["kill_switch_attestation_ok"] is True
    assert rep["gates"]["auto_derisk_on_breach"] is True
