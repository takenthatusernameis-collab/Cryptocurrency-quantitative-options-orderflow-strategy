from __future__ import annotations

import os
import sys

sys.path.insert(0, "/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v9 import (  # noqa: E402
    Phase110CfgV9,
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV9Loop,
)


def test_phase110_v9_hardened_ultra_deep() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase110CfgV9(cycles=240)
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV9Loop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v9(cycles=240)
    assert isinstance(res, dict)
    gates = res.get("gates", {})
    assert gates.get("all_ok") is True
    assert gates.get("evidence_chain") is True
    assert gates.get("orderflow_toxicity_aware") is True
    assert gates.get("cross_venue_sor_routing") is True
    assert gates.get("gamma_dealer_positioning_inventory_hedging") is True
    assert gates.get("fragmentation_routing") is True
    assert gates.get("margin_collateral_netting") is True
    assert gates.get("settlement_finality_reconciliation_post_trade") is True
    assert gates.get("live_execution_readiness") is True
    assert gates.get("slippage_model_calibration_guard") is True
    assert gates.get("latency_slippage_deep_model") is True
    assert gates.get("adverse_selection_guard") is True
    assert gates.get("liquidity_aware_hedge_sizing") is True
    assert gates.get("autonomous_failover") is True
    assert gates.get("compliance_governance") is True
    assert gates.get("chaos_resilience") is True
    assert gates.get("idempotency_replay") is True
    assert gates.get("fill_probability_model") is True
    assert gates.get("stress_haircuts") is True
    assert gates.get("iv_surface_greeks") is True
    assert gates.get("orderflow_microstructure") is True
    assert gates.get("orderflow_microstructure_vpin") is True
    assert gates.get("adverse_sel_slippage_fill_joint") is True
    assert gates.get("gamma_dealer_hedge_toxicity_adjusted") is True
    assert gates.get("stress_haircut_margin") is True
    assert gates.get("chaos_failover_tamper") is True
    assert gates.get("cross_venue_routing_toxicity") is True
    assert gates.get("post_trade_finality_reconciliation") is True
    assert gates.get("finite_numerics") is True
    assert gates.get("no_placeholders") is True
    assert gates.get("audit_trail_tamper_evident") is True
    assert gates.get("iv_calibration_guard") is True
    assert gates.get("smile_skew_term_arb_sanity") is True
    assert gates.get("orderflow_toxicity_regime_classification") is True
    assert gates.get("adverse_sel_slippage_fill_liquidity_regime_joint") is True
    assert gates.get("gamma_dealer_hedge_convexity_basis_rates") is True
    assert gates.get("cross_margin_correlated_crisis_stress_haircuts") is True
    assert gates.get("post_trade_idempotent_replay_finality") is True
    assert gates.get("autonomous_resilience_compliance_governance") is True
    assert gates.get("live_readiness_latency_p99") is True
    assert gates.get("live_readiness_error_rate") is True
    assert gates.get("live_readiness_pass_rate") is True
