import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v142 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV142Loop,
)


def _assert_domain_gates(g, prefix, start=140, end=88):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v142():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV142Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v142"
    assert res["seed"] == 1111222
    assert res["engine"] == "Phase110UltraDeepQuantEngineV145"
    _assert_domain_gates(g, "iv_surface", start=140)
    _assert_domain_gates(g, "of", start=140)
    _assert_domain_gates(g, "sor", start=140)
    _assert_domain_gates(g, "asf", start=140)
    _assert_domain_gates(g, "gdh", start=140)
    _assert_domain_gates(g, "shm", start=140)
    _assert_domain_gates(g, "cft", start=140)
    _assert_domain_gates(g, "ptf", start=140)
    _assert_domain_gates(g, "mm", start=140)
    _assert_domain_gates(g, "cap", start=140)
    _assert_domain_gates(g, "obs", start=140)
    _assert_domain_gates(g, "scr", start=140)
    assert g["composition_mm_v142"] is True
    assert g["composition_scr_v142"] is True
