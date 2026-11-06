import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV134Loop,
)


def _assert_domain_gates(g, prefix, start=132, end=85):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV134Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v134"
    assert res["seed"] == 1111214
    assert res["engine"] == "Phase110UltraDeepQuantEngineV137"
    _assert_domain_gates(g, "iv_surface", start=132)
    _assert_domain_gates(g, "of", start=132)
    _assert_domain_gates(g, "sor", start=132)
    _assert_domain_gates(g, "asf", start=132)
    _assert_domain_gates(g, "gdh", start=132)
    _assert_domain_gates(g, "shm", start=132)
    _assert_domain_gates(g, "cft", start=132)
    _assert_domain_gates(g, "ptf", start=132)
    _assert_domain_gates(g, "mm", start=132)
    _assert_domain_gates(g, "cap", start=132)
    _assert_domain_gates(g, "obs", start=132)
    _assert_domain_gates(g, "scr", start=132)
    assert g["composition_mm_v134"] is True
    assert g["composition_scr_v134"] is True
