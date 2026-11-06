import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v148 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV148Loop,
)


def _assert_domain_gates(g, prefix, start=146, end=88):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v148():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV148Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v148"
    assert res["seed"] == 1111228
    assert res["engine"] == "Phase110UltraDeepQuantEngineV151"
    _assert_domain_gates(g, "iv_surface", start=146)
    _assert_domain_gates(g, "of", start=146)
    _assert_domain_gates(g, "sor", start=146)
    _assert_domain_gates(g, "asf", start=146)
    _assert_domain_gates(g, "gdh", start=146)
    _assert_domain_gates(g, "shm", start=146)
    _assert_domain_gates(g, "cft", start=146)
    _assert_domain_gates(g, "ptf", start=146)
    _assert_domain_gates(g, "mm", start=146)
    _assert_domain_gates(g, "cap", start=146)
    _assert_domain_gates(g, "obs", start=146)
    _assert_domain_gates(g, "scr", start=146)
    assert g["composition_mm_v148"] is True
    assert g["composition_scr_v148"] is True
