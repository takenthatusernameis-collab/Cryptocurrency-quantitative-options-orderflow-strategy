from __future__ import annotations

from pathlib import Path

from src.risk.phase57_production_circuit_breakers import (
    Phase57CircuitConfig,
    Phase57ProductionCircuitBreakers,
)
from src.telemetry.serialization import serialize_metrics_strict


def test_phase57_cb_init_paper_only() -> None:
    cfg = Phase57CircuitConfig(seed=3)
    cb = Phase57ProductionCircuitBreakers(cfg)
    assert cb.cfg.paper_only is True


def test_phase57_cb_rejects_live() -> None:
    try:
        Phase57CircuitConfig(seed=3, paper_only=False)
    except ValueError:
        return
    raise AssertionError("paper_only=False must be rejected")


def test_phase57_cb_ok(tmp_path: Path) -> None:
    cb = Phase57ProductionCircuitBreakers(Phase57CircuitConfig(seed=23))
    rep = cb.evaluate()
    assert rep["phase"] == "PHASE57_PRODUCTION_CIRCUIT_BREAKERS"
    assert rep["paper_only"] is True
    assert rep["live_path_hard_gated"] is True
    assert rep["halted"] is False
    assert rep["auto_halt_triggered"] is False
    assert rep["composed_phases"] == "17-56"
    assert rep["integration"] == "Phase45+Phase54+Phase55+Phase56"
    art = cb.generate_artifacts(outdir=str(tmp_path))
    assert Path(art["json_path"]).exists()
    assert Path(art["md_path"]).exists()
    ss = serialize_metrics_strict(rep)
    assert ss["deterministic"] is True


def test_phase57_cb_halt(tmp_path: Path) -> None:
    cb = Phase57ProductionCircuitBreakers(Phase57CircuitConfig(seed=29))
    rep = cb.evaluate({"drawdown_pct": 0.15, "latency_ms_p99": 300.0, "toxicity": 0.6, "risk_breach": 1.0})
    assert rep["halted"] is True
    assert rep["auto_halt_triggered"] is True
    assert len(rep["breaches"]) >= 2
