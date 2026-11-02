from __future__ import annotations

from pathlib import Path

from src.liquidity.phase53_fragmentation_arb_engine import (
    Phase53FragmentationArbEngine,
    Phase53FragmentationConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase53_frag_init_paper_only() -> None:
    cfg = Phase53FragmentationConfig(seed=123, paper_only=True)
    eng = Phase53FragmentationArbEngine(cfg)
    assert eng.cfg.paper_only is True


def test_phase53_frag_campaign_and_artifacts(tmp_path: Path) -> None:
    eng = Phase53FragmentationArbEngine(Phase53FragmentationConfig(seed=777, cycles=25))
    rep = eng.run_campaign(cycles=25)
    assert rep["gates_ok"] is True
    assert rep["n_bases"] == 25
    art = eng.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert "phase" in s
