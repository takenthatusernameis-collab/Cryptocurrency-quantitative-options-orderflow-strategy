from __future__ import annotations

import math

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


def test_phase53_skew_run_and_artifacts(tmp_path: Path) -> None:
    eng = Phase53AdaptiveInventorySkewEngine(Phase53InventorySkewConfig(seed=777, cycles=12))
    rep = eng.run_campaign(cycles=12)
    assert rep["gates_ok"] is True
    assert rep["paper_only"] is True
    assert rep["n_quotes"] == 12 * 3 * 4 * 4
    assert rep["halted_by_kill_switch"] is False
    for q in eng.quotes:
        assert q["ask"] > q["bid"]
        assert q["spread_bps"] >= eng.cfg.min_spread_bps
    art = eng.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s.get("phase") == "PHASE53_ADAPTIVE_INVENTORY_SKEW_ENGINE"


def test_phase53_skew_determinism_and_finite() -> None:
    a = Phase53AdaptiveInventorySkewEngine(Phase53InventorySkewConfig(seed=4242, cycles=8)).run_campaign(cycles=8)
    b = Phase53AdaptiveInventorySkewEngine(Phase53InventorySkewConfig(seed=4242, cycles=8)).run_campaign(cycles=8)
    assert a == b
    eng = Phase53AdaptiveInventorySkewEngine(Phase53InventorySkewConfig(seed=9, cycles=5))
    rep = eng.run_campaign(cycles=5)
    assert rep["gates_ok"] is True
    assert all(math.isfinite(q["bid"]) and math.isfinite(q["ask"]) for q in eng.quotes)
    assert all(math.isfinite(s["max_abs_inventory"]) for s in eng.inventory_snapshots)
