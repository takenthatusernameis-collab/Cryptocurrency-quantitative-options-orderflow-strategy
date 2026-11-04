from __future__ import annotations

import os
import sys

sys.path.insert(0, "/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v18 import (  # noqa: E402
    Phase110Cfg,
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV18Loop,
)


def test_phase110_v18_ultra_deep() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase110Cfg(cycles=320, outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v18")
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV18Loop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v18(cycles=320)
    assert isinstance(res, dict)
    gates = res.get("gates", {})
    assert gates.get("all_ok") is True
    assert gates.get("iv_american_bermudan_pricing_deep") is True
    assert gates.get("orderflow_dark_pool_inference_deep") is True
    assert gates.get("sor_reinforcement_learning_policy_deep") is True
    assert gates.get("adverse_sel_meta_learning_deep") is True
    assert gates.get("gamma_hedge_convexity_correction_deep") is True
    assert gates.get("jump_to_default_margin_addon_deep") is True
    assert gates.get("byzantine_fault_tolerance_quorum_deep") is True
    assert gates.get("settlement_dlt_bridge_finality_deep") is True
    assert gates.get("finite_numerics") is True
    assert gates.get("no_placeholders") is True
