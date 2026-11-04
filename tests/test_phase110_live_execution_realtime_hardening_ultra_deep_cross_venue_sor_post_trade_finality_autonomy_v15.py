from __future__ import annotations

import os
import sys

sys.path.insert(0, "/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v15 import (  # noqa: E402
    Phase110Cfg,
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV15Loop,
)


def test_phase110_v15_ultra_deep() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase110Cfg(cycles=320, outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v15")
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV15Loop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v15(cycles=320)
    assert isinstance(res, dict)
    gates = res.get("gates", {})
    assert gates.get("all_ok") is True
    assert gates.get("iv_real_time_calibration_deep") is True
    assert gates.get("orderflow_hft_signature_deep") is True
    assert gates.get("sor_realtime_routing_optimizer_deep") is True
    assert gates.get("asf_regime_switching_slippage_deep") is True
    assert gates.get("gdh_vol_surface_hedge_optimizer") is True
    assert gates.get("shm_intraday_margin_monitor_deep") is True
    assert gates.get("cft_autonomous_remediation_deep") is True
    assert gates.get("ptf_atomic_cross_venue_settlement_deep") is True
    assert gates.get("finite_numerics") is True
    assert gates.get("no_placeholders") is True
