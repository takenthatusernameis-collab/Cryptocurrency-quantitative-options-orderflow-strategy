import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v149 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV149Loop,
)


def _assert_domain_gates(g, prefix, start=147, end=88):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v149():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV149Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v149"
    assert res["seed"] == 1111229
    assert res["engine"] == "Phase110UltraDeepQuantEngineV152"
    _assert_domain_gates(g, "iv_surface", start=147)
    _assert_domain_gates(g, "of", start=147)
    _assert_domain_gates(g, "sor", start=147)
    _assert_domain_gates(g, "asf", start=147)
    _assert_domain_gates(g, "gdh", start=147)
    _assert_domain_gates(g, "shm", start=147)
    _assert_domain_gates(g, "cft", start=147)
    _assert_domain_gates(g, "ptf", start=147)
    _assert_domain_gates(g, "mm", start=147)
    _assert_domain_gates(g, "cap", start=147)
    _assert_domain_gates(g, "obs", start=147)
    _assert_domain_gates(g, "scr", start=147)
    assert g["composition_mm_v149"] is True
    assert g["composition_scr_v149"] is True
