from __future__ import annotations

from pathlib import Path

from src.flow.phase56_cross_venue_options_flow_synthesizer import (
    Phase56CrossVenueOptionsFlowSynthesizer,
    Phase56FlowSynthConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase56_flow_init_paper_only() -> None:
    cfg = Phase56FlowSynthConfig(seed=1)
    s = Phase56CrossVenueOptionsFlowSynthesizer(cfg)
    assert s.cfg.paper_only is True


def test_phase56_flow_rejects_live() -> None:
    try:
        Phase56FlowSynthConfig(seed=1, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase56_flow_synthesize_deterministic(tmp_path: Path) -> None:
    s = Phase56CrossVenueOptionsFlowSynthesizer(Phase56FlowSynthConfig(seed=7))
    rep = s.synthesize({"deribit": {"bid_vol": 120, "ask_vol": 100, "toxicity": 0.12}})
    assert rep["phase"] == "PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER"
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    assert rep["integration"] == "Phase50+Phase51+Phase52+Phase53+Phase54"
    art = s.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    ss = serialize_metrics_strict(rep)
    assert ss["deterministic"] is True
