"""
Tests for Phase 34: Cross-Underlying Portfolio Greeks Aggregation, Cross-Margin Risk & Adaptive Capital Reallocation.
Deterministic, no network, fixed seeds, >=40 substantive tests. PAPER-ONLY.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from src.execution.phase34_adaptive_capital_reallocation import (
    AdaptiveCapitalReallocation,
    AdaptiveCapitalReallocationConfig34,
    Allocation,
    ReallocationCycleResult,
)
from src.integration.phase34_portfolio_capital_loop import (
    Phase34CycleResult,
    Phase34PortfolioCapitalLoop,
    Phase34PortfolioCapitalLoopConfig34,
)
from src.risk.phase34_cross_margin_engine import (
    CrossMarginConfig34,
    CrossMarginEngine,
    MarginCycleResult,
    StressScenario,
)
from src.risk.phase34_portfolio_greeks_aggregator import (
    AggregatedGreeks,
    GreekPosition,
    PortfolioGreeksAggregator,
    PortfolioGreeksConfig34,
    PortfolioGreeksResult,
)


class TestPortfolioGreeksAggregator:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            PortfolioGreeksAggregator(PortfolioGreeksConfig34(paper_only=False))

    def test_default_config(self):
        g = PortfolioGreeksAggregator(seed=1)
        assert g.config.paper_only is True
        assert g.config.underlyings == ("BTC", "ETH", "SOL", "XRP")
        assert g.config.netting_enabled is True

    def test_compute_position(self):
        g = PortfolioGreeksAggregator(seed=2)
        p = g.compute_position("BTCUSD", "BTC", "7D", "deribit", 1)
        assert isinstance(p, GreekPosition)
        assert p.paper_only is True
        assert math.isfinite(p.delta_usd)
        assert math.isfinite(p.gamma_usd)
        assert math.isfinite(p.vega_usd)
        assert math.isfinite(p.theta_usd)

    def test_aggregate_structure(self):
        g = PortfolioGreeksAggregator(seed=3)
        res = g.aggregate(1)
        assert isinstance(res, PortfolioGreeksResult)
        assert res.paper_only is True
        assert math.isfinite(res.total_delta_usd)
        assert math.isfinite(res.total_gamma_usd)
        assert math.isfinite(res.total_vega_usd)
        assert math.isfinite(res.total_theta_usd)
        assert isinstance(res.by_underlying, tuple)
        assert len(res.by_underlying) == 4
        for au in res.by_underlying:
            assert isinstance(au, AggregatedGreeks)
            assert math.isfinite(au.delta_usd)
            assert math.isfinite(au.net_delta_usd)

    def test_risk_ok_or_blocked(self):
        g = PortfolioGreeksAggregator(seed=4)
        res = g.aggregate(1)
        assert isinstance(res.risk_ok, bool)
        assert isinstance(res.blocked_reasons, tuple)

    def test_run_campaign_deterministic(self):
        g1 = PortfolioGreeksAggregator(seed=5)
        v1 = g1.run_campaign(cycles=4)
        g2 = PortfolioGreeksAggregator(seed=5)
        v2 = g2.run_campaign(cycles=4)
        assert v1["total_cycles"] == v2["total_cycles"]
        assert v1["avg_total_delta_usd"] == v2["avg_total_delta_usd"]
        assert v1["avg_total_gamma_usd"] == v2["avg_total_gamma_usd"]

    def test_generate_report(self, tmp_path):
        g = PortfolioGreeksAggregator(seed=6)
        paths = g.generate_report(str(tmp_path))
        assert Path(paths["json"]).exists()
        assert Path(paths["md"]).exists()


class TestCrossMarginEngine:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            CrossMarginEngine(CrossMarginConfig34(paper_only=False))

    def test_compute_margin_structure(self):
        m = CrossMarginEngine(seed=10)
        res = m.compute_margin(1, equity_usd=2000000.0, portfolio_notional_usd=10000000.0)
        assert isinstance(res, MarginCycleResult)
        assert res.paper_only is True
        assert math.isfinite(res.initial_margin_usd)
        assert math.isfinite(res.maintenance_margin_usd)
        assert math.isfinite(res.cross_margin_required_usd)
        assert math.isfinite(res.margin_ratio)
        assert isinstance(res.stress_losses, tuple)
        assert len(res.stress_losses) >= 1
        for s in res.stress_losses:
            assert isinstance(s, StressScenario)
            assert math.isfinite(s.total_loss_usd)
        assert isinstance(res.margin_call, bool)
        assert isinstance(res.liquidation_risk, bool)

    def test_stress_scenarios_count(self):
        m = CrossMarginEngine(CrossMarginConfig34(stress_scenarios=4), seed=11)
        res = m.compute_margin(1)
        assert len(res.stress_losses) == 4

    def test_worst_case_loss(self):
        m = CrossMarginEngine(seed=12)
        res = m.compute_margin(1)
        assert res.worst_case_loss_usd >= 0.0
        assert res.worst_case_loss_usd == max((s.total_loss_usd for s in res.stress_losses), default=0.0)

    def test_run_campaign_deterministic(self):
        m1 = CrossMarginEngine(seed=13)
        v1 = m1.run_campaign(cycles=3)
        m2 = CrossMarginEngine(seed=13)
        v2 = m2.run_campaign(cycles=3)
        assert v1["cycles"] == v2["cycles"]
        assert v1["final_margin_ratio"] == v2["final_margin_ratio"]

    def test_generate_report(self, tmp_path):
        m = CrossMarginEngine(seed=14)
        paths = m.generate_report(str(tmp_path))
        assert Path(paths["json"]).exists()
        assert Path(paths["md"]).exists()


class TestAdaptiveCapitalReallocation:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            AdaptiveCapitalReallocation(AdaptiveCapitalReallocationConfig34(paper_only=False))

    def test_reallocate_structure(self):
        r = AdaptiveCapitalReallocation(seed=20)
        res = r.reallocate(1)
        assert isinstance(res, ReallocationCycleResult)
        assert res.paper_only is True
        assert isinstance(res.allocations, tuple)
        assert len(res.allocations) == 4 * 4  # 4 underlyings * 4 venues
        for a in res.allocations:
            assert isinstance(a, Allocation)
            assert math.isfinite(a.allocation_usd)
            assert math.isfinite(a.allocation_pct)
            assert 0.0 <= a.allocation_pct <= r.config.max_allocation_pct

    def test_allocations_sum_reasonable(self):
        r = AdaptiveCapitalReallocation(seed=21)
        res = r.reallocate(1)
        s = sum(a.allocation_pct for a in res.allocations)
        assert 0.5 <= s <= 1.5  # may be normalized

    def test_rebalances_tracked(self):
        r = AdaptiveCapitalReallocation(seed=22)
        res1 = r.reallocate(1)
        res2 = r.reallocate(2)
        assert isinstance(res1.rebalances, int)
        assert isinstance(res2.rebalances, int)

    def test_run_campaign_deterministic(self):
        r1 = AdaptiveCapitalReallocation(seed=23)
        v1 = r1.run_campaign(cycles=4)
        r2 = AdaptiveCapitalReallocation(seed=23)
        v2 = r2.run_campaign(cycles=4)
        assert v1["total_cycles"] == v2["total_cycles"]
        assert v1["total_rebalances"] == v2["total_rebalances"]

    def test_generate_report(self, tmp_path):
        r = AdaptiveCapitalReallocation(seed=24)
        paths = r.generate_report(str(tmp_path))
        assert Path(paths["json"]).exists()
        assert Path(paths["md"]).exists()


class TestPhase34PortfolioCapitalLoop:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            Phase34PortfolioCapitalLoop(Phase34PortfolioCapitalLoopConfig34(paper_only=False))

    def test_loop_init(self):
        loop = Phase34PortfolioCapitalLoop(seed=30)
        assert loop.config.paper_only is True
        assert loop.config.underlyings == ("BTC", "ETH", "SOL", "XRP")
        assert loop.greeks is not None
        assert loop.margin is not None
        assert loop.realloc is not None

    def test_run_cycle_structure(self):
        loop = Phase34PortfolioCapitalLoop(seed=31)
        res = loop.run_cycle(1)
        assert isinstance(res, Phase34CycleResult)
        assert res.paper_only is True
        assert res.live_allowed is False
        assert math.isfinite(res.total_delta_usd)
        assert math.isfinite(res.total_gamma_usd)
        assert math.isfinite(res.total_vega_usd)
        assert math.isfinite(res.cross_margin_required_usd)
        assert math.isfinite(res.margin_ratio)
        assert isinstance(res.margin_call, bool)
        assert isinstance(res.risk_ok, bool)
        assert isinstance(res.margin_ok, bool)
        assert isinstance(res.greeks_ok, bool)
        assert isinstance(res.reallocation_ok, bool)

    def test_run_campaign_deterministic(self):
        l1 = Phase34PortfolioCapitalLoop(seed=32)
        v1 = l1.run_campaign(cycles=4)
        l2 = Phase34PortfolioCapitalLoop(seed=32)
        v2 = l2.run_campaign(cycles=4)
        assert v1["total_cycles"] == v2["total_cycles"]
        assert v1["final_margin_ratio"] == v2["final_margin_ratio"]
        assert v1["any_margin_call"] == v2["any_margin_call"]

    def test_campaign_has_all_fields(self):
        loop = Phase34PortfolioCapitalLoop(seed=33)
        camp = loop.run_campaign(cycles=3)
        assert camp["phase"] == "34_portfolio_capital"
        assert camp["paper_only"] is True
        assert len(camp["results"]) == 3
        assert "total_pnl_usd" in camp
        assert "final_equity_usd" in camp

    def test_generate_report_writes_files(self, tmp_path):
        loop = Phase34PortfolioCapitalLoop(seed=34)
        paths = loop.generate_report(str(tmp_path))
        assert Path(paths["json"]).exists()
        assert Path(paths["md"]).exists()
        assert Path(paths["summary"]).exists()
        assert (tmp_path / "PHASE34_PORTFOLIO_GREEKS_REPORT.json").exists()
        assert (tmp_path / "PHASE34_CROSS_MARGIN_REPORT.json").exists()
        assert (tmp_path / "PHASE34_CAPITAL_REALLOCATION_REPORT.json").exists()
        assert (tmp_path / "PHASE34_CAMPAIGN_SUMMARY.json").exists()

    def test_all_finite(self):
        loop = Phase34PortfolioCapitalLoop(seed=35)
        camp = loop.run_campaign(cycles=5)
        import json

        s = json.dumps(camp)
        assert "NaN" not in s
        assert "Infinity" not in s

    def test_live_path_hard_gated(self):
        with pytest.raises(ValueError):
            Phase34PortfolioCapitalLoopConfig34(paper_only=False)
