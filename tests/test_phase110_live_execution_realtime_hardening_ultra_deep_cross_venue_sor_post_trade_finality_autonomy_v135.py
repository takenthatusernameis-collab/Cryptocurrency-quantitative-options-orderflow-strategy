import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV135Loop,
)


def _assert_domain_gates(g, prefix, start=133, end=86):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV135Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v135"
    assert res["seed"] == 1111215
    assert res["engine"] == "Phase110UltraDeepQuantEngineV138"
    _assert_domain_gates(g, "iv_surface", start=133)
    _assert_domain_gates(g, "of", start=133)
    _assert_domain_gates(g, "sor", start=133)
    _assert_domain_gates(g, "asf", start=133)
    _assert_domain_gates(g, "gdh", start=133)
    _assert_domain_gates(g, "shm", start=133)
    _assert_domain_gates(g, "cft", start=133)
    _assert_domain_gates(g, "ptf", start=133)
    _assert_domain_gates(g, "mm", start=133)
    _assert_domain_gates(g, "cap", start=133)
    _assert_domain_gates(g, "obs", start=133)
    _assert_domain_gates(g, "scr", start=133)
    assert g["composition_mm_v135"] is True
    assert g["composition_scr_v135"] is True
