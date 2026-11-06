import os

if str(os.environ.get("PHASE_QUICK_VERIFY", "")).lower() not in ("1", "true", "yes"):
    import pytest

    pytest.skip(
        "Phase110 v156 is a heavy ultra-deep campaign; set PHASE_QUICK_VERIFY=1 for quick verify",
        allow_module_level=True,
    )

from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v156 import (
    Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV156Loop,
)


def _assert_domain_gates(g, prefix, start=154, end=88):
    for v in range(start, end - 1, -1):
        k = f"{prefix}_deep_v{v}"
        assert g[k], k


def test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v156():
    res = Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV156Loop().run()
    assert res["version"] == "v156"
    assert res["seed"] == 1111236
    assert res["engine"] == "Phase110UltraDeepQuantEngineV159"
    assert res["all_ok"] is True
    assert res["finite_ok"] is True
    assert res["gates"]["all_ok"] is True
    g = res["gates"]
    for p in ("iv_surface", "of", "sor", "asf", "gdh", "shm", "cft", "ptf", "mm", "cap", "obs", "scr"):
        _assert_domain_gates(g, p, start=154, end=88)
    assert g["composition_mm_v156"] is True
    assert g["composition_scr_v156"] is True
