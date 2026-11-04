from __future__ import annotations

import os

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v22 import run_phase110_v22


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v22_phase_scoped():
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    res = run_phase110_v22()
    assert res.get("all_ok") is True
    gates = res.get("gates", {})
    assert gates.get("v25_deep_all_ok") is True
    assert gates.get("ok") is True
    assert res.get("version") == "v22"
