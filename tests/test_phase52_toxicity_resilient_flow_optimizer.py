from __future__ import annotations

from pathlib import Path

from src.orderflow.phase52_toxicity_resilient_flow_optimizer import (
    Phase52FlowOptimizerConfig,
    Phase52ToxicityResilientFlowOptimizer,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase52_flow_optimizer_init_paper_only() -> None:
    cfg = Phase52FlowOptimizerConfig(seed=123, paper_only=True)
    opt = Phase52ToxicityResilientFlowOptimizer(cfg)
    assert opt.cfg.paper_only is True


def test_phase52_flow_optimizer_optimize_and_artifacts(tmp_path: Path) -> None:
    opt = Phase52ToxicityResilientFlowOptimizer(Phase52FlowOptimizerConfig(seed=777, cycles=20))
    rep = opt.optimize_flow(cycles=20)
    assert rep["gates_ok"] is True
    assert rep["n_segments"] == 20
    assert rep["n_throttles"] == 20
    assert rep["n_routes"] == 20
    art = opt.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    # serialization roundtrip
    s = serialize_metrics_strict(rep)
    assert "phase" in s
