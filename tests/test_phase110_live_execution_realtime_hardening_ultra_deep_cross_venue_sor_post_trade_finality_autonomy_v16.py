from __future__ import annotations

import os
import sys

sys.path.insert(0, "/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v16 import (  # noqa: E402
    Phase110Cfg,
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV16Loop,
)


def test_phase110_v16_ultra_deep() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase110Cfg(cycles=320, outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v16")
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV16Loop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v16(cycles=320)
    assert isinstance(res, dict)
    gates = res.get("gates", {})
    assert gates.get("all_ok") is True
    assert gates.get("iv_atm_otm_itm_coverage_deep") is True
    assert gates.get("orderflow_informed_detection_deep") is True
    assert gates.get("sor_latency_aware_routing_deep") is True
    assert gates.get("adverse_sel_confidence_interval_deep") is True
    assert gates.get("gamma_convexity_toxicity_adjusted_sizing") is True
    assert gates.get("jump_to_default_correlation_blowup_deep") is True
    assert gates.get("kill_switch_readiness_deep") is True
    assert gates.get("idempotent_replay_autoheal_deep") is True
    assert gates.get("finite_numerics") is True
    assert gates.get("no_placeholders") is True
