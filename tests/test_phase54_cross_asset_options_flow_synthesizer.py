from __future__ import annotations

from pathlib import Path

from src.flow.phase54_cross_asset_options_flow_synthesizer import (
    Phase54CrossAssetOptionsFlowSynthesizer,
    Phase54FlowSynthConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase54_flow_synth_init_paper_only() -> None:
    cfg = Phase54FlowSynthConfig(seed=123, paper_only=True)
    eng = Phase54CrossAssetOptionsFlowSynthesizer(cfg)
    assert eng.cfg.paper_only is True


def test_phase54_flow_synth_init_rejects_live() -> None:
    try:
        Phase54FlowSynthConfig(seed=123, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase54_flow_synth_weights_must_sum_to_one() -> None:
    try:
        Phase54FlowSynthConfig(
            seed=123,
            regime_fusion_weight_flow=0.5,
            regime_fusion_weight_tox=0.3,
            regime_fusion_weight_arb=0.1,
        )
    except ValueError:
        return
    raise AssertionError("regime fusion weights must sum to 1.0")


def test_phase54_flow_synth_campaign_and_artifacts(tmp_path: Path) -> None:
    eng = Phase54CrossAssetOptionsFlowSynthesizer(Phase54FlowSynthConfig(seed=777, cycles=20))
    rep = eng.run_campaign(cycles=20)
    assert rep["gates_ok"] is True
    assert isinstance(rep["slo_ok"], bool)
    assert rep["n_syntheses"] == 20
    assert rep["n_routes"] == 20
    assert 0.0 <= rep["avg_regime_fusion_score"] <= 1.0
    assert 0.0 <= rep["avg_toxicity"] <= 1.0
    art = eng.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s["phase"] == "PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER"
    assert s["paper_only"] is True


def test_phase54_flow_synth_finite_numerics(tmp_path: Path) -> None:
    eng = Phase54CrossAssetOptionsFlowSynthesizer(Phase54FlowSynthConfig(seed=555, cycles=15))
    rep = eng.run_campaign(cycles=15)
    s = serialize_metrics_strict(rep)
    assert "gates_ok" in s
