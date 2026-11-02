from __future__ import annotations

from pathlib import Path

from src.marketmaking.phase53_adaptive_inventory_skew_engine import (
    Phase53InventorySkewConfig,
    Phase53AdaptiveInventorySkewEngine,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase53_skew_init_paper_only() -> None:
    cfg = Phase53InventorySkewConfig(seed=123, paper_only=True)
    eng = Phase53AdaptiveInventorySkewEngine(cfg)
    assert eng.cfg.paper_only is True


def test_phase53_skew_campaign_and_artifacts(tmp_path: Path) -> None:
    eng = Phase53AdaptiveInventorySkewEngine(Phase53InventorySkewConfig(seed=888, cycles=30))
    rep = eng.run_campaign(cycles=30)
    assert rep["gates_ok"] is True
    assert rep["n_skews"] == 30
    art = eng.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert "phase" in s
