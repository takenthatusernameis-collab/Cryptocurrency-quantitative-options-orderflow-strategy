import os

if str(os.environ.get("PHASE_QUICK_VERIFY", "")).lower() not in ("1", "true", "yes"):
    import pytest

    pytest.skip(
        "Phase110 v154 is a heavy ultra-deep campaign; set PHASE_QUICK_VERIFY=1 for quick verify",
        allow_module_level=True,
    )

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v154 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV154Loop,
)


def _assert_domain_gates(g, prefix, start=152, end=88):
    for v in range(start, end - 1, -1):
        k = f"{prefix}_deep_v{v}"
        assert g[k], k


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v154():
    res = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV154Loop().run()
    assert res["version"] == "v154"
    assert res["seed"] == 1111234
    assert res["engine"] == "Phase110UltraDeepQuantEngineV157"
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert res["gates"]["all_ok"] is True
    g = res["gates"]
    for p in ("iv_surface", "of", "sor", "asf", "gdh", "shm", "cft", "ptf", "mm", "cap", "obs", "scr"):
        _assert_domain_gates(g, p, start=152, end=88)
    assert g["composition_mm_v154"] is True
    assert g["composition_scr_v154"] is True
