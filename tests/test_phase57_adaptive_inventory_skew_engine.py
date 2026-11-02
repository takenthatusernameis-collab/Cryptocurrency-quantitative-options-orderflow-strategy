from __future__ import annotations

from pathlib import Path

from src.marketmaking.phase57_adaptive_inventory_skew_engine import (
    Phase57AdaptiveInventorySkewEngine,
    Phase57SkewConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase57_skew_init_paper_only() -> None:
    cfg = Phase57SkewConfig(seed=2)
    s = Phase57AdaptiveInventorySkewEngine(cfg)
    assert s.cfg.paper_only is True


def test_phase57_skew_rejects_live() -> None:
    try:
        Phase57SkewConfig(seed=2, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase57_skew(tmp_path: Path) -> None:
    s = Phase57AdaptiveInventorySkewEngine(Phase57SkewConfig(seed=22))
    rep = s.skew(inventory=100.0, gamma=0.12, vega=0.08, toxicity=0.2)
    assert rep["phase"] == "PHASE57_ADAPTIVE_INVENTORY_SKEW_ENGINE"
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["integration"] == "Phase50+Phase53+Phase56"
    assert rep["within_bands"] is True
    art = s.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    ss = serialize_metrics_strict(rep)
    assert ss["finite"] is True
