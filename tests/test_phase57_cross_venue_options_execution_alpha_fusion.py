from __future__ import annotations

from pathlib import Path

from src.alpha.phase57_cross_venue_options_execution_alpha_fusion import (
    Phase57AlphaFusionConfig,
    Phase57CrossVenueOptionsExecutionAlphaFusion,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase57_alpha_init_paper_only() -> None:
    cfg = Phase57AlphaFusionConfig(seed=1)
    a = Phase57CrossVenueOptionsExecutionAlphaFusion(cfg)
    assert a.cfg.paper_only is True


def test_phase57_alpha_rejects_live() -> None:
    try:
        Phase57AlphaFusionConfig(seed=1, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase57_alpha_fuse(tmp_path: Path) -> None:
    a = Phase57CrossVenueOptionsExecutionAlphaFusion(Phase57AlphaFusionConfig(seed=21))
    rep = a.fuse()
    assert rep["phase"] == "PHASE57_CROSS_VENUE_OPTIONS_EXECUTION_ALPHA_FUSION"
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    assert rep["integration"] == "Phase48+Phase51+Phase54+Phase56"
    art = a.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    ss = serialize_metrics_strict(rep)
    assert ss["deterministic"] is True
