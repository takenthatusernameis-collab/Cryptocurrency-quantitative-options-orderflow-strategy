from __future__ import annotations

import json
import os
from pathlib import Path


def test_phase101_live_execution_realtime_hardening(tmp_path: Path) -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    from src.risk.phase101_live_execution_realtime_hardening_orderflow_sor_toxicity_gamma_dealer_hedging_cross_margin_fragmentation_post_trade_finality_resilience_compliance import (
        Phase101LiveExecutionRealtimeHardeningOrderflowSorToxicityGammaDealerHedgingCrossMarginFragmentationPostTradeFinalityResilienceComplianceLoop,
        Phase101Cfg,
    )

    cfg = Phase101Cfg(outdir=str(tmp_path), cycles=48)
    loop = Phase101LiveExecutionRealtimeHardeningOrderflowSorToxicityGammaDealerHedgingCrossMarginFragmentationPostTradeFinalityResilienceComplianceLoop(cfg)
    res = loop.run_live_execution_realtime_hardening()
    assert res["phase"] == 101
    assert res["paper_only"] is True
    gates = res["gates"]
    assert gates["evidence_chain"] is True
    assert gates["orderflow_toxicity_aware"] is True
    assert gates["adverse_selection_guard"] is True
    assert gates["cross_venue_sor_routing"] is True
    assert gates["fragmentation_routing"] is True
    assert gates["gamma_dealer_positioning_inventory_hedging"] is True
    assert gates["liquidity_aware_hedge_sizing"] is True
    assert gates["margin_collateral_netting"] is True
    assert gates["settlement_finality_reconciliation_post_trade"] is True
    assert gates["live_execution_readiness"] is True
    assert gates["slippage_model_calibration_guard"] is True
    assert gates["autonomous_failover"] is True
    assert gates["compliance_governance"] is True
    assert gates["options_iv_greeks_surface"] is True
    assert gates["orderflow_microstructure"] is True
    assert gates["finite_numerics"] is True
    assert gates["no_placeholders"] is True
    assert gates["audit_trail_tamper_evident"] is True
    assert gates["realtime_sor_hardening"] is True
    assert gates["orderflow_toxicity_hardening"] is True
    assert gates["gamma_dealer_hedging_hardening"] is True
    assert gates["cross_margin_fragmentation_hardening"] is True
    assert gates["post_trade_finality_hardening"] is True
    assert gates["resilience_failover_hardening"] is True
    assert gates["compliance_governance_hardening"] is True
    assert gates["slippage_calibration_hardening"] is True
    assert gates["adverse_selection_hardening"] is True
    assert gates["liquidity_aware_hedge_hardening"] is True
    assert gates["all_ok"] is True
    p = tmp_path / "phase101_live_execution_realtime_hardening" / "PHASE101_RES_LATEST.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["phase"] == 101
