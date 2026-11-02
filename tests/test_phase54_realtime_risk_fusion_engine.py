from __future__ import annotations

from pathlib import Path

from src.risk.phase54_realtime_risk_fusion_engine import (
    Phase54RealtimeRiskFusionEngine,
    Phase54RiskFusionConfig,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase54_risk_fusion_init_paper_only() -> None:
    cfg = Phase54RiskFusionConfig(seed=123, paper_only=True)
    eng = Phase54RealtimeRiskFusionEngine(cfg)
    assert eng.cfg.paper_only is True


def test_phase54_risk_fusion_init_rejects_live() -> None:
    try:
        Phase54RiskFusionConfig(seed=123, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase54_risk_fusion_thresholds_validated() -> None:
    try:
        Phase54RiskFusionConfig(
            seed=123,
            fused_risk_caution=0.8,
            fused_risk_halt=0.5,
        )
    except ValueError:
        return
    raise AssertionError("fused risk thresholds must satisfy caution < halt")


def test_phase54_risk_fusion_campaign_and_artifacts(tmp_path: Path) -> None:
    eng = Phase54RealtimeRiskFusionEngine(Phase54RiskFusionConfig(seed=777, cycles=20))
    rep = eng.run_campaign(cycles=20)
    assert rep["gates_ok"] is True
    assert isinstance(rep["slo_ok"], bool)
    assert rep["risk_cycles_ok"] is True
    assert rep["critical_breaches"] == 0
    assert rep["kill_switch_triggered"] is False
    assert rep["n_cycles"] == 20
    assert 0.0 <= rep["avg_fused_risk_score"] <= 1.0
    assert 0.0 <= rep["avg_adaptive_throttle"] <= 1.0
    art = eng.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    s = serialize_metrics_strict(rep)
    assert s["phase"] == "PHASE54_REALTIME_RISK_FUSION_ENGINE"
    assert s["paper_only"] is True


def test_phase54_risk_fusion_finite_numerics(tmp_path: Path) -> None:
    eng = Phase54RealtimeRiskFusionEngine(Phase54RiskFusionConfig(seed=555, cycles=10))
    rep = eng.run_campaign(cycles=10)
    s = serialize_metrics_strict(rep)
    assert "gates_ok" in s
