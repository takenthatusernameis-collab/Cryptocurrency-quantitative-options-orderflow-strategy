from __future__ import annotations

import os

from src.risk.phase103_live_execution_realtime_hardening_ultra_deep_orderflow_sor_toxicity_gamma_dealer_hedging_cross_margin_fragmentation_post_trade_finality_resilience_compliance_latency_slippage_adverse_sel_liq_aware_failover_chaos_audit_tamper import (
    Phase103LiveExecutionRealtimeHardeningUltraDeepOrderflowSorToxicityGammaDealerHedgingCrossMarginFragmentationPostTradeFinalityResilienceComplianceLatencySlippageAdverseSelLiqAwareFailoverChaosAuditTamperLoop,
    Phase103Cfg,
    Phase103UltraDeepQuantExtension,
    Phase103UltraDeepQuantEngineV2,
    Phase103UltraDeepQuantEngineV3,
)


def test_phase103_ultra_deep_extension_engine():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    ext = Phase103UltraDeepQuantExtension(seed=123)
    v = ext.vpins_deep(64)
    g = ext.gamma_dealer_surface_deep(64)
    f = ext.fill_prob_slippage_joint(64)
    m = ext.cross_margin_stress_deep(64)
    c = ext.chaos_failover_deep(64)
    idem = ext.idempotent_replay_deep(64)
    aud = ext.tamper_audit_deep(64)
    assert len(v) == 64 and all(x["vpin"] >= 0.0 and x["vpin"] <= 1.0 for x in v)
    assert len(g) == 64 and all(x["hedge_need"] >= 0.0 for x in g)
    assert len(f) == 64 and all(0.0 < x["fill_prob"] < 1.0 for x in f)
    assert len(m) == 64 and all(0.0 < x["netting_eff"] <= 1.0 for x in m)
    assert len(c) == 64
    assert len(idem) == 64 and all(x["applied_once"] for x in idem)
    assert len(aud) == 64 and all(x["tamper_evident"] and x["paper_only"] for x in aud)


def test_phase103_ultra_deep_engine_v2():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV2(seed=103)
    fs = eng.fragmentation_sor_deep(128)
    vt = eng.vpin_adverse_selection_deep(128)
    gh = eng.gamma_dealer_inventory_hedge_deep(128)
    cm = eng.cross_margin_netting_stress_deep(128)
    pt = eng.post_trade_finality_recon_deep(128)
    ch = eng.chaos_failover_audit_deep(128)
    assert len(fs) == 128 and all(x["fragmentation_aware"] for x in fs)
    assert len(vt) == 128 and all("vpin" in x for x in vt)
    assert len(gh) == 128 and all(x["liq_adj_hedge"] >= x["hedge_need"] for x in gh)
    assert len(cm) == 128 and all(x["cross_venue_net"] for x in cm)
    assert len(pt) == 128 and all(x["atomic"] and x["idempotent"] for x in pt)
    assert len(ch) == 128 and all(x["tamper_evident"] and x["paper_only"] for x in ch)


def test_phase103_loop_generates_artifacts():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase103Cfg(cycles=48)
    loop = Phase103LiveExecutionRealtimeHardeningUltraDeepOrderflowSorToxicityGammaDealerHedgingCrossMarginFragmentationPostTradeFinalityResilienceComplianceLatencySlippageAdverseSelLiqAwareFailoverChaosAuditTamperLoop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep(cycles=48)
    assert res["phase"] == 103
    assert res["paper_only"] is True
    assert res["metrics"]["all_ok"] is True
    g = res["gates"]
    for k in ["evidence_chain", "orderflow_toxicity_aware", "cross_venue_sor_routing", "gamma_dealer_positioning_inventory_hedging", "liquidity_aware_hedge_sizing", "margin_collateral_netting", "settlement_finality_reconciliation_post_trade", "live_execution_readiness", "slippage_model_calibration_guard", "latency_slippage_deep_model", "autonomous_failover", "compliance_governance", "chaos_resilience", "idempotency_replay", "fill_probability_model", "stress_haircuts", "audit_trail_tamper_evident", "finite_numerics", "no_placeholders"]:
        assert g.get(k) is True


def _assert_all_finite_ok(rows):
    assert all(x.get("finite") is True and x.get("ok") is True for x in rows)


def test_phase103_v3_iv_surface_greeks():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV3(seed=777)
    rows = eng.iv_surface_greeks_deep(256)
    assert len(rows) == 256
    assert all(0.05 <= x["iv"] <= 2.5 for x in rows)
    assert all(0.0 <= x["delta"] <= 1.0 for x in rows)
    assert all(x["gamma"] >= 0.0 and x["vega"] >= 0.0 for x in rows)
    _assert_all_finite_ok(rows)


def test_phase103_v3_orderflow_microstructure_vpin():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV3(seed=888)
    rows = eng.orderflow_microstructure_deep(256)
    assert len(rows) == 256
    assert all(0.0 <= x["vpin"] <= 0.9 for x in rows)
    assert all(x["adverse_sel_cost_bps"] >= 0.0 for x in rows)
    _assert_all_finite_ok(rows)


def test_phase103_v3_adverse_sel_slippage_fill_joint():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV3(seed=999)
    rows = eng.adverse_sel_slippage_fill_joint(256)
    assert len(rows) == 256
    assert all(0.0 < x["fill_prob"] < 1.0 for x in rows)
    assert all(x["slip_bps"] >= 0.0 and x["adv_sel_bps"] >= 0.0 for x in rows)
    assert all(x["expected_cost_bps"] >= 0.0 for x in rows)
    _assert_all_finite_ok(rows)


def test_phase103_v3_gamma_dealer_hedge_toxicity_adjusted():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV3(seed=111)
    rows = eng.gamma_dealer_hedge_toxicity_adjusted(256)
    assert len(rows) == 256
    assert all(x["liq_adj_hedge"] >= x["base_hedge"] for x in rows)
    assert all(0.0 <= x["delta_hedge_ratio"] <= 1.0 for x in rows)
    _assert_all_finite_ok(rows)


def test_phase103_v3_stress_haircut_margin():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV3(seed=222)
    rows = eng.stress_haircut_margin_deep(256)
    assert len(rows) == 256
    assert all(x["margin_ratio"] >= 1.0 for x in rows)
    assert all(0.35 <= x["netting_eff"] <= 1.0 for x in rows)
    _assert_all_finite_ok(rows)


def test_phase103_v3_chaos_failover_tamper_chain():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    eng = Phase103UltraDeepQuantEngineV3(seed=333)
    rows = eng.chaos_failover_tamper_deep(256)
    assert len(rows) == 256
    assert all(x["tamper_evident"] and x["paper_only"] for x in rows)
    assert all(rows[i]["hash"] != rows[i - 1]["hash"] for i in range(1, len(rows)))
    _assert_all_finite_ok(rows)


def test_phase103_v3_loop_gates():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase103Cfg(cycles=40)
    loop = Phase103LiveExecutionRealtimeHardeningUltraDeepOrderflowSorToxicityGammaDealerHedgingCrossMarginFragmentationPostTradeFinalityResilienceComplianceLatencySlippageAdverseSelLiqAwareFailoverChaosAuditTamperLoop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep(cycles=40)
    assert res["phase"] == 103
    assert res["paper_only"] is True
    assert res["metrics"]["all_ok"] is True
    g = res["gates"]
    for k in ["iv_surface_greeks", "orderflow_microstructure_vpin", "adverse_sel_slippage_fill_joint", "gamma_dealer_hedge_toxicity_adjusted", "stress_haircut_margin", "chaos_failover_tamper", "finite_numerics", "no_placeholders"]:
        assert g.get(k) is True
