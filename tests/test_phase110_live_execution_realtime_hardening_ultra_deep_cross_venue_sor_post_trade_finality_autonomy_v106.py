import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v106 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV106Loop,
)


def _assert_domain_gates(g, prefix, start=106, end=82):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v106():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV106Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v106"
    assert res["seed"] == 1111186
    assert res["engine"] == "Phase110UltraDeepQuantEngineV109"
    _assert_domain_gates(g, "iv_surface")
    _assert_domain_gates(g, "of")
    _assert_domain_gates(g, "sor")
    _assert_domain_gates(g, "asf")
    _assert_domain_gates(g, "gdh")
    _assert_domain_gates(g, "shm")
    _assert_domain_gates(g, "cft")
    _assert_domain_gates(g, "ptf")
    _assert_domain_gates(g, "mm")
    _assert_domain_gates(g, "cap")
    _assert_domain_gates(g, "obs")
    _assert_domain_gates(g, "scr")
    assert g["composition_mm_v106"] is True
    assert g["composition_scr_v106"] is True
