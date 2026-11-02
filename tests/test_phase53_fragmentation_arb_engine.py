from __future__ import annotations

from pathlib import Path

from src.liquidity.phase53_fragmentation_arb_engine import (
    Phase53FragmentationArbConfig,
    Phase53FragmentationArbEngine,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase53_frag_arb_init_paper_only() -> None:
    cfg = Phase53FragmentationArbConfig(seed=123, paper_only=True)
    eng = Phase53FragmentationArbEngine(cfg)
    assert eng.cfg.paper_only is True


def test_phase53_frag_arb_run_and_artifacts(tmp_path: Path) -> None:
    eng = Phase53FragmentationArbEngine(Phase53FragmentationArbConfig(seed=777, cycles=12))
    rep = eng.run_campaign(cycles=12)
    assert rep["gates_ok"] is True
    assert rep["paper_only"] is True
    assert rep["n_basis_observations"] == 12 * 6
    assert rep["halted_by_kill_switch"] is False
    art = eng.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s.get("phase") == "PHASE53_FRAGMENTATION_ARB_ENGINE"


def test_phase53_frag_arb_determinism() -> None:
    a = Phase53FragmentationArbEngine(Phase53FragmentationArbConfig(seed=4242, cycles=8)).run_campaign(cycles=8)
    b = Phase53FragmentationArbEngine(Phase53FragmentationArbConfig(seed=4242, cycles=8)).run_campaign(cycles=8)
    assert a == b
