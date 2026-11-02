from __future__ import annotations

from pathlib import Path

from src.integration.phase53_cross_asset_delta_vol_hedge_fusion_loop import Phase53CrossAssetDeltaVolHedgeFusionLoop
from src.telemetry.serialization import serialize_metrics_strict


def test_phase53_loop_init_paper_only() -> None:
    loop = Phase53CrossAssetDeltaVolHedgeFusionLoop(seed=999, cycles=10)
    assert loop.paper_only is True


def test_phase53_loop_run_and_artifacts(tmp_path: Path) -> None:
    loop = Phase53CrossAssetDeltaVolHedgeFusionLoop(seed=53053, cycles=8, outdir=str(tmp_path))
    rep = loop.run()
    assert rep["gates_ok"] is True
    assert rep["paper_only"] is True
    assert rep["phase53_fragmentation_arb"]["gates_ok"] is True
    assert rep["phase53_inventory_skew"]["gates_ok"] is True
    assert rep["phase52_hedge_loop"]["gates_ok"] is True
    assert rep["phase51_alpha_fusion"]["gates_ok"] is True
    assert rep["phase51_sor"]["gates_ok"] is True
    assert Path(rep["json_path"]).exists()
    assert Path(rep["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s.get("phase") == "PHASE53_CROSS_ASSET_DELTA_VOL_HEDGE_FUSION_LOOP"


def test_phase53_loop_halt_and_rollback_on_breach() -> None:
    loop = Phase53CrossAssetDeltaVolHedgeFusionLoop(seed=53053, cycles=8)
    rep = loop.run()
    assert rep["gates_ok"] is True
    assert rep["halt_count"] == 0
    assert rep["rollback_count"] == 0
    assert rep["slo"]["evaluations"] > 0
