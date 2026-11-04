from __future__ import annotations

import os
import sys

sys.path.insert(0, "/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v17 import (  # noqa: E402
    Phase110Cfg,
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV17Loop,
)


def test_phase110_v17_ultra_deep() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    cfg = Phase110Cfg(cycles=320, outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v17")
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV17Loop(cfg)
    res = loop.run_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v17(cycles=320)
    assert isinstance(res, dict)
    gates = res.get("gates", {})
    assert gates.get("all_ok") is True
    assert gates.get("iv_jump_diffusion_calibration_deep") is True
    assert gates.get("orderflow_queue_dynamics_deep") is True
    assert gates.get("sor_pareto_execution_frontier_deep") is True
    assert gates.get("adverse_sel_bayesian_posterior_deep") is True
    assert gates.get("gamma_scalping_timing_toxicity_deep") is True
    assert gates.get("contagion_network_spillover_deep") is True
    assert gates.get("bft_consensus_tamper_deep") is True
    assert gates.get("atomic_cross_venue_settlement_deep") is True
    assert gates.get("finite_numerics") is True
    assert gates.get("no_placeholders") is True
