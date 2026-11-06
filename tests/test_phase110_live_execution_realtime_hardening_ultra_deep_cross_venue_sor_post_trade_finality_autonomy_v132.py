import os

os.environ.setdefault("PHASE_QUICK_VERIFY", "1")

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v132 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV132Loop,
)


def _assert_domain_gates(g, prefix, start=130, end=83):
    for v in range(start, end - 1, -1):
        assert g[f"{prefix}_deep_v{v}"] is True, f"{prefix}_deep_v{v}"


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v132():
    loop = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV132Loop()
    res = loop.run()
    g = res["gates"]
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert g["all_ok"] is True
    assert res["version"] == "v132"
    assert res["seed"] == 1111212
    assert res["engine"] == "Phase110UltraDeepQuantEngineV135"
    _assert_domain_gates(g, "iv_surface", start=130)
    _assert_domain_gates(g, "of", start=130)
    _assert_domain_gates(g, "sor", start=130)
    _assert_domain_gates(g, "asf", start=130)
    _assert_domain_gates(g, "gdh", start=130)
    _assert_domain_gates(g, "shm", start=130)
    _assert_domain_gates(g, "cft", start=130)
    _assert_domain_gates(g, "ptf", start=130)
    _assert_domain_gates(g, "mm", start=130)
    _assert_domain_gates(g, "cap", start=130)
    _assert_domain_gates(g, "obs", start=130)
    _assert_domain_gates(g, "scr", start=130)
    assert g["composition_mm_v132"] is True
    assert g["composition_scr_v132"] is True
