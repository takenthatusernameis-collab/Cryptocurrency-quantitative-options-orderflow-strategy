from __future__ import annotations

from pathlib import Path

from src.integration.phase53_cross_asset_delta_vol_hedge_fusion_loop import (
    Phase53CrossAssetDeltaVolHedgeFusionLoop,
)


def test_phase53_loop_init_paper_only() -> None:
    loop = Phase53CrossAssetDeltaVolHedgeFusionLoop(seed=53053, cycles=15, paper_only=True)
    assert loop.paper_only is True


def test_phase53_loop_run_and_artifacts(tmp_path: Path) -> None:
    loop = Phase53CrossAssetDeltaVolHedgeFusionLoop(seed=53153, cycles=20, paper_only=True, outdir=str(tmp_path))
    rep = loop.run()
    assert rep["gates_ok"] is True
    assert Path(rep["json_path"]).exists()
    assert Path(rep["md_path"]).exists()
