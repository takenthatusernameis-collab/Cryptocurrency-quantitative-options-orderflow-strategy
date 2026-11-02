"""
Tests for Phase 48: Regime-Conditional Options Strategies & Orderflow Signal Fusion Engine.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.alpha.phase48_regime_conditional_options_engine import (
    Phase48Config,
    Phase48RegimeConditionalOptionsEngine,
    MarketRegime,
    OptionStrategyType,
)


def test_phase48_config_paper_only_hard_gate():
    try:
        Phase48Config(paper_only=False)
        assert False, "should have raised"
    except Exception:
        pass


def test_phase48_engine_paper_only_hard_gate():
    try:
        Phase48RegimeConditionalOptionsEngine(paper_only=False)
        assert False, "should have raised"
    except Exception:
        pass


def test_phase48_engine_init_and_structure():
    eng = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=123, paper_only=True, cycles=5))
    assert eng.paper_only is True
    assert eng.cfg.cycles == 5


def test_phase48_regime_classification():
    eng = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=48048, paper_only=True, cycles=10))
    regimes = []
    for c in range(1, 6):
        r = eng._regime_from_state(c)
        regimes.append(r.regime)
        assert r.paper_only is True
        assert 0.0 <= r.confidence <= 1.0
    assert all(r in [m.value for m in MarketRegime] for r in regimes)


def test_phase48_orderflow_fusion():
    eng = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=48048, paper_only=True, cycles=10))
    for c in range(1, 4):
        for u in eng.cfg.underlyings:
            of = eng._fuse_orderflow(u, "deribit", c)
            assert of.paper_only is True
            assert 0.0 <= of.orderflow_score <= 1.0
            assert 0.0 <= of.toxicity_score <= 1.0


def test_phase48_strategy_selection():
    eng = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=48048, paper_only=True, cycles=10))
    from src.alpha.phase48_regime_conditional_options_engine import RegimeSignal
    r_crest = eng._regime_from_state(1)
    of = eng._fuse_orderflow("BTC", "deribit", 1)
    st, conf = eng._select_strategy(r_crest, of)
    assert st in [s.value for s in OptionStrategyType]
    assert 0.0 <= conf <= 1.0


def test_phase48_run_campaign():
    eng = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=48048, paper_only=True, cycles=12))
    rep = eng.run_campaign(cycles=12)
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["n_alphas"] >= 0
    assert rep["phase"] == "PHASE48_REGIME_CONDITIONAL_OPTIONS_ENGINE"


def test_phase48_generate_reports(tmp_path):
    eng = Phase48RegimeConditionalOptionsEngine(Phase48Config(seed=48048, paper_only=True, cycles=8, outdir=str(tmp_path)))
    eng.run_campaign(cycles=8)
    paths = eng.generate_reports(outdir=str(tmp_path))
    assert "json" in paths and "md" in paths
    j = Path(paths["json"])
    m = Path(paths["md"])
    assert j.exists() and m.exists()
    data = json.loads(j.read_text())
    assert data["paper_only"] is True
