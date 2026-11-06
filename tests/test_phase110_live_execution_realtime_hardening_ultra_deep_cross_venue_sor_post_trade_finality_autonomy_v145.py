import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v145 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV145Loop,
)


def _assert_domain_gates(g, prefix, start=143, end=88):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v145():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV145Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v145"
    assert res["seed"] == 1111225
    assert res["engine"] == "Phase110UltraDeepQuantEngineV148"
    _assert_domain_gates(g, "iv_surface", start=143)
    _assert_domain_gates(g, "of", start=143)
    _assert_domain_gates(g, "sor", start=143)
    _assert_domain_gates(g, "asf", start=143)
    _assert_domain_gates(g, "gdh", start=143)
    _assert_domain_gates(g, "shm", start=143)
    _assert_domain_gates(g, "cft", start=143)
    _assert_domain_gates(g, "ptf", start=143)
    _assert_domain_gates(g, "mm", start=143)
    _assert_domain_gates(g, "cap", start=143)
    _assert_domain_gates(g, "obs", start=143)
    _assert_domain_gates(g, "scr", start=143)
    assert g["composition_mm_v145"] is True
    assert g["composition_scr_v145"] is True
