from __future__ import annotations

from pathlib import Path

from src.integration.phase52_adaptive_hedge_execution_loop import Phase52AdaptiveHedgeExecutionLoop
from src.telemetry.serialization import serialize_metrics_strict


def test_phase52_loop_init_paper_only() -> None:
    loop = Phase52AdaptiveHedgeExecutionLoop(seed=999, cycles=10)
    assert loop.paper_only is True


def test_phase52_loop_run_and_artifacts(tmp_path: Path) -> None:
    loop = Phase52AdaptiveHedgeExecutionLoop(seed=52052, cycles=12, outdir=str(tmp_path))
    rep = loop.run()
    assert rep["gates_ok"] is True
    assert rep["phase52_flow_optimizer"]["gates_ok"] is True
    assert rep["phase52_liquidity_allocator"]["gates_ok"] is True
    assert rep["phase51_alpha_fusion"]["gates_ok"] is True
    assert rep["phase51_sor"]["gates_ok"] is True
    assert rep["phase50_mm"]["gates_ok"] is True
    assert rep["phase50_rv"]["gates_ok"] is True
    assert Path(rep["json_path"]).exists()
    assert Path(rep["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s.get("phase") == "PHASE52_ADAPTIVE_HEDGE_EXECUTION_LOOP"
