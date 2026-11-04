from __future__ import annotations

import json
import os
from pathlib import Path


def test_phase96_cross_venue_atomic_rt_recon_hardening_loop(tmp_path: Path) -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    from src.risk.phase96_atomic_rt_recon_finality_lqbuf_sor_frag_gamma_liqprov_quorum_hash_custody_clearing_failover_slo_hardening import (
        Phase96CrossVenueAtomicSettlementFinalityNettingRealTimeReconLiqBufferAdversarialSorToxicFlowAdaptiveFragGammaInvHedgeRegimeLiqProvPaperLiveGateQuorumHashChainCustodyClearingAtomicReconFailoverComplianceGovPostTradeSloHardeningLoop,
        Phase96Cfg,
    )

    cfg = Phase96Cfg(outdir=str(tmp_path), cycles=16)
    loop = Phase96CrossVenueAtomicSettlementFinalityNettingRealTimeReconLiqBufferAdversarialSorToxicFlowAdaptiveFragGammaInvHedgeRegimeLiqProvPaperLiveGateQuorumHashChainCustodyClearingAtomicReconFailoverComplianceGovPostTradeSloHardeningLoop(cfg)
    res = loop.run_cross_venue_atomic_settlement_finality_netting_real_time_recon_liq_buffer_adversarial_sor_toxic_flow_adaptive_frag_gamma_inv_hedge_regime_liq_prov_paper_live_gate_quorum_hash_chain_custody_clearing_atomic_recon_failover_compliance_gov_post_trade_slo_hardening()
    assert res["phase"] == 96
    assert res["paper_only"] is True
    gates = res["gates"]
    assert gates["evidence_chain"] is True
    assert gates["custody_clearing"] is True
    assert gates["settlement/finality"] is True
    assert gates["margin/collateral"] is True
    assert gates["live_readiness"] is True
    assert gates["post_trade"] is True
    assert gates["stress_gate"] is True
    assert gates["autonomous_failover"] is True
    assert gates["compliance_governance"] is True
    assert gates["orderflow_toxicity_aware"] is True
    assert gates["cross_venue_sor_routing"] is True
    assert gates["gamma_dealer_positioning/inventory_hedging"] is True
    assert gates["gamma_inventory_hedging_regime_aware_liquidity_provision_stress"] is True
    assert gates["options_iv_greeks_surface"] is True
    assert gates["regime_aware_mm_hedging"] is True
    assert gates["fragmentation_routing"] is True
    assert gates["finality_settlement_reconciliation_post_trade_attestation"] is True
    assert gates["cross_venue_netting_finality_edge_cases"] is True
    assert gates["liquidation_buffer_stress_adversarial_fragmentation"] is True
    assert gates["sor_optimal_routing_toxic_flow_guards"] is True
    assert gates["paper_to_live_gate_attestation_quorum"] is True
    assert gates["deterministic_cross_venue_settlement_finality_hash_chain"] is True
    assert gates["atomic_recon_custody_clearing"] is True
    assert gates["real_time_recon"] is True
    assert gates["slo_hardening"] is True
    assert gates["finite_numerics"] is True
    assert gates["no_placeholders"] is True
    assert gates["all_ok"] is True
    outdir = Path(tmp_path) / "phase96_atomic_rt_recon_finality_lqbuf_sor_frag_gamma_liqprov_quorum_hash_custody_clearing_failover_slo_hardening"
    assert (outdir / "PHASE96_RES_LATEST.json").exists()
    assert (outdir / "PHASE96_RES_LATEST.md").exists()
    data = json.loads((outdir / "PHASE96_RES_LATEST.json").read_text())
    assert data["gates"]["all_ok"] is True
