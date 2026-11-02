from __future__ import annotations

from pathlib import Path

from src.execution.phase52_realtime_liquidity_allocator import (
    Phase52AllocatorConfig,
    Phase52RealtimeLiquidityAllocator,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase52_allocator_init_paper_only() -> None:
    cfg = Phase52AllocatorConfig(seed=456, paper_only=True)
    alloc = Phase52RealtimeLiquidityAllocator(cfg)
    assert alloc.cfg.paper_only is True


def test_phase52_allocator_allocate_and_artifacts(tmp_path: Path) -> None:
    alloc = Phase52RealtimeLiquidityAllocator(Phase52AllocatorConfig(seed=888, cycles=15))
    rep = alloc.allocate(cycles=15)
    assert rep["gates_ok"] is True
    assert rep["n_allocations"] > 0
    assert rep["n_slices"] > 0
    assert rep["n_tca"] == 15
    art = alloc.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert "phase" in s
