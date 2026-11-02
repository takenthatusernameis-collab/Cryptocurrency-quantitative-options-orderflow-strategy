from __future__ import annotations

from pathlib import Path

from src.hedging.phase56_latency_aware_delta_hedger import (
    Phase56DeltaHedgeConfig,
    Phase56LatencyAwareDeltaHedger,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase56_hedger_init_paper_only() -> None:
    cfg = Phase56DeltaHedgeConfig(seed=2)
    h = Phase56LatencyAwareDeltaHedger(cfg)
    assert h.cfg.paper_only is True


def test_phase56_hedger_rejects_live() -> None:
    try:
        Phase56DeltaHedgeConfig(seed=2, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase56_hedger_hedge_deterministic(tmp_path: Path) -> None:
    h = Phase56LatencyAwareDeltaHedger(Phase56DeltaHedgeConfig(seed=11))
    rep = h.hedge(delta_exposure=15.0)
    assert rep["phase"] == "PHASE56_LATENCY_AWARE_DELTA_HEDGER"
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["domain_focus"].startswith("crypto_options_orderflow")
    assert rep["integration"] == "Phase42+Phase49+Phase50+Phase52+Phase54"
    assert rep["hard_limits_ok"] is True
    assert rep["hedge_notional"] <= h.cfg.max_hedge_notional
    art = h.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    ss = serialize_metrics_strict(rep)
    assert ss["finite"] is True
