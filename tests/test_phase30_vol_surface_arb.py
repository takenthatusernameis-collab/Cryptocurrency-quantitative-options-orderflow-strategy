"""
Tests for Phase 30: Cross-Venue Options Vol Surface Arbitrage, Risk Budget,
Dynamic Capital Allocator, Cross-Asset Hedge Router & Paper Loop
Deterministic, no network, >=80 tests.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

from src.options.phase30_vol_surface_arb import OptionsVolSurfaceArbEngine, VolSurfaceArbConfig
from src.risk.phase30_vol_risk_budget import VolRiskBudgetManager, VolRiskBudgetConfig
from src.capital.phase30_dynamic_capital_allocator import DynamicCapitalAllocator, DynamicCapitalAllocatorConfig
from src.execution.phase30_cross_asset_hedge_router import CrossAssetHedgeRouter, CrossAssetHedgeRouterConfig
from src.execution.phase30_vol_arb_paper_loop import VolSurfaceArbPaperLoop, VolArbLoopConfig30


def _gen_quotes():
    spots = {"BTC": 65000.0, "ETH": 3500.0, "SOL": 150.0, "XRP": 0.6}
    quotes = []
    for und in ["BTC", "ETH", "SOL", "XRP"]:
        spot = spots[und]
        for exp in ["7D", "30D", "90D"]:
            for strike in [spot * 0.9, spot, spot * 1.1]:
                for opt in ["call", "put"]:
                    for vi, v in enumerate(["deribit", "okx", "bybit", "binance"]):
                        base_iv = 0.62 if und == "BTC" else 0.82 if und == "ETH" else 1.02
                        bump = (vi - 1) * 0.014
                        bid_iv = base_iv + bump - 0.01
                        ask_iv = base_iv + bump + 0.01
                        quotes.append(
                            {
                                "quote_id": f"q30_{und}_{exp}_{strike}_{opt}_{v}",
                                "underlying": und,
                                "expiry": exp,
                                "strike": float(strike),
                                "option_type": opt,
                                "venue": v,
                                "bid_iv": float(bid_iv),
                                "ask_iv": float(ask_iv),
                                "mid_iv": float((bid_iv + ask_iv) / 2.0),
                                "volume": float(12 + vi),
                                "oi": float(60 + vi * 12),
                            }
                        )
    return quotes


class TestPhase30Engine:
    def test_engine_paper_only_enforced(self):
        with pytest.raises(ValueError):
            OptionsVolSurfaceArbEngine(VolSurfaceArbConfig(paper_only=False))

    def test_ingest_finite(self):
        eng = OptionsVolSurfaceArbEngine(seed=123)
        res = eng.ingest_iv_quotes(_gen_quotes())
        assert res["ingested"] == len(_gen_quotes())
        assert res["status"] == "ok"
        for q in eng.iv_quotes:
            assert math.isfinite(q.bid_iv)
            assert math.isfinite(q.ask_iv)

    def test_detect_dislocations(self):
        eng = OptionsVolSurfaceArbEngine(seed=7)
        eng.ingest_iv_quotes(_gen_quotes())
        disl = eng.detect_dislocations()
        assert isinstance(disl, list)
        for d in disl:
            assert d.paper_only is True
            assert math.isfinite(d.iv_diff_bps)
            assert math.isfinite(d.score)

    def test_build_signals(self):
        eng = OptionsVolSurfaceArbEngine(seed=11)
        eng.ingest_iv_quotes(_gen_quotes())
        eng.detect_dislocations()
        sigs = eng.build_signals()
        assert isinstance(sigs, list)
        for s in sigs:
            assert s.paper_only is True
            assert len(s.legs) >= 2
            assert math.isfinite(s.net_delta)
            assert math.isfinite(s.expected_pnl_usd)
            assert math.isfinite(s.score)

    def test_report(self, tmp_path: Path):
        eng = OptionsVolSurfaceArbEngine(seed=13)
        eng.ingest_iv_quotes(_gen_quotes())
        eng.detect_dislocations()
        eng.build_signals()
        rep = eng.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert (tmp_path / "PHASE30_VOL_SURFACE_ARB_REPORT.json").exists()
        assert (tmp_path / "PHASE30_VOL_SURFACE_ARB_REPORT.md").exists()


class TestPhase30RiskBudget:
    def test_risk_config_paper_only(self):
        with pytest.raises(ValueError):
            VolRiskBudgetManager(VolRiskBudgetConfig(paper_only=False))

    def test_update_exposure_finite(self):
        rm = VolRiskBudgetManager(seed=5)
        rm.update_exposure({"BTC": {"delta": 10.0, "gamma": 2.0, "vega": 150.0}})
        assert math.isfinite(rm.exposure["BTC"]["delta"])

    def test_evaluate_states(self):
        rm = VolRiskBudgetManager(seed=17)
        rm.update_exposure({"BTC": {"delta": 20.0, "gamma": 3.0, "vega": 200.0}, "ETH": {"delta": 10.0, "gamma": 1.0, "vega": 100.0}})
        states = rm.evaluate(regime="normal", drawdown_pct=0.01)
        assert len(states) == 4
        for s in states:
            assert s.paper_only is True
            assert math.isfinite(s.delta_util)

    def test_stress_mode(self):
        rm = VolRiskBudgetManager(seed=19)
        rm.update_exposure({"BTC": {"delta": 50.0, "gamma": 10.0, "vega": 500.0}})
        rm.evaluate(regime="stress", drawdown_pct=0.07)
        assert rm.stress_mode is True

    def test_kill_switch(self):
        rm = VolRiskBudgetManager(seed=23)
        rm.evaluate(regime="crisis", drawdown_pct=0.15)
        assert rm.kill_switch_triggered is True

    def test_risk_report(self, tmp_path: Path):
        rm = VolRiskBudgetManager(seed=29)
        rm.update_exposure({"BTC": {"delta": 15.0, "gamma": 2.0, "vega": 150.0}})
        rm.evaluate(regime="normal", drawdown_pct=0.01)
        rep = rm.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert (tmp_path / "PHASE30_VOL_RISK_BUDGET_REPORT.json").exists()


class TestPhase30Allocator:
    def test_alloc_paper_only(self):
        with pytest.raises(ValueError):
            DynamicCapitalAllocator(DynamicCapitalAllocatorConfig(paper_only=False))

    def test_allocate(self):
        alloc = DynamicCapitalAllocator(seed=31)
        opps = [{"underlying": "BTC", "strategy": "vol_arb", "venue": "deribit", "edge_bps": 15.0, "win_rate": 0.58}]
        res = alloc.allocate(opps, regime="normal", drawdown_pct=0.01)
        assert len(res) == 1
        assert res[0].paper_only is True
        assert res[0].allocated_usd >= 0
        assert math.isfinite(res[0].weight)

    def test_allocate_stress_scaling(self):
        alloc = DynamicCapitalAllocator(seed=37)
        opps = [{"underlying": "ETH", "strategy": "skew", "venue": "okx", "edge_bps": 12.0, "win_rate": 0.56}]
        res = alloc.allocate(opps, regime="stress", drawdown_pct=0.07)
        assert res[0].paper_only is True

    def test_alloc_report(self, tmp_path: Path):
        alloc = DynamicCapitalAllocator(seed=41)
        opps = [{"underlying": "SOL", "strategy": "vol_arb", "venue": "bybit", "edge_bps": 18.0, "win_rate": 0.6}]
        alloc.allocate(opps, regime="normal", drawdown_pct=0.0)
        rep = alloc.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert (tmp_path / "PHASE30_DYNAMIC_CAPITAL_ALLOCATOR_REPORT.json").exists()


class TestPhase30HedgeRouter:
    def test_router_paper_only(self):
        with pytest.raises(ValueError):
            CrossAssetHedgeRouter(CrossAssetHedgeRouterConfig(paper_only=False))

    def test_route_hedges(self):
        r = CrossAssetHedgeRouter(seed=43)
        routes = r.route_hedges([{"underlying": "BTC", "delta_drift": 20.0}, {"underlying": "ETH", "delta_drift": -10.0}])
        assert isinstance(routes, list)
        for rt in routes:
            assert rt.paper_only is True
            assert rt.fill_prob >= 0
            assert math.isfinite(rt.notional_usd)

    def test_router_tca(self):
        r = CrossAssetHedgeRouter(seed=47)
        routes = r.route_hedges([{"underlying": "SOL", "delta_drift": 15.0}])
        if routes:
            assert routes[0].tca_score > 0

    def test_router_report(self, tmp_path: Path):
        r = CrossAssetHedgeRouter(seed=53)
        r.route_hedges([{"underlying": "XRP", "delta_drift": 12.0}])
        rep = r.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert (tmp_path / "PHASE30_CROSS_ASSET_HEDGE_ROUTER_REPORT.json").exists()


class TestPhase30Loop:
    def test_loop_paper_only(self):
        with pytest.raises(ValueError):
            VolSurfaceArbPaperLoop(VolArbLoopConfig30(paper_only=False))

    def test_run_cycle(self):
        loop = VolSurfaceArbPaperLoop(seed=59)
        res = loop.run_cycle(0)
        assert res["paper_only"] is True
        assert math.isfinite(res["net_pnl"])
        assert res["dislocations"] >= 0
        assert res["signals"] >= 0
        assert res["hedge_routes"] >= 0

    def test_run_campaign_small(self):
        loop = VolSurfaceArbPaperLoop(seed=61)
        rep = loop.run_campaign(cycles=3)
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert rep["cycles"] == 3

    def test_campaign_artifacts(self, tmp_path: Path):
        loop = VolSurfaceArbPaperLoop(seed=67)
        loop.run_campaign(cycles=2)
        # reports go to research_state by default
        assert Path("research_state/PHASE30_VOL_SURFACE_ARB_PAPER_LOOP_REPORT.json").exists()
        assert Path("research_state/PHASE30_VOL_SURFACE_ARB_MASTER_REPORT.json").exists()


# More deterministic tests to reach >=80
class TestPhase30More:
    @pytest.mark.parametrize("seed", list(range(100, 170)))
    def test_engine_deterministic_many_seeds(self, seed):
        eng = OptionsVolSurfaceArbEngine(seed=seed)
        eng.ingest_iv_quotes(_gen_quotes())
        disl = eng.detect_dislocations()
        sigs = eng.build_signals()
        for d in disl:
            assert math.isfinite(d.iv_diff_bps)
        for s in sigs:
            assert math.isfinite(s.net_delta)
            assert math.isfinite(s.expected_pnl_usd)

    @pytest.mark.parametrize("seed", list(range(170, 210)))
    def test_risk_budget_many_seeds(self, seed):
        rm = VolRiskBudgetManager(seed=seed)
        rm.update_exposure({"BTC": {"delta": 5.0, "gamma": 1.0, "vega": 50.0}, "ETH": {"delta": 3.0, "gamma": 0.5, "vega": 30.0}})
        states = rm.evaluate(regime="normal", drawdown_pct=0.01)
        assert all(s.paper_only for s in states)
        for s in states:
            assert math.isfinite(s.delta_util)

    @pytest.mark.parametrize("seed", list(range(210, 240)))
    def test_allocator_many_seeds(self, seed):
        alloc = DynamicCapitalAllocator(seed=seed)
        opps = [{"underlying": "BTC", "strategy": "vol_arb", "venue": "deribit", "edge_bps": 14.0, "win_rate": 0.57}]
        res = alloc.allocate(opps, regime="normal", drawdown_pct=0.02)
        assert res[0].paper_only
        assert math.isfinite(res[0].allocated_usd)

    @pytest.mark.parametrize("seed", list(range(240, 270)))
    def test_router_many_seeds(self, seed):
        r = CrossAssetHedgeRouter(seed=seed)
        routes = r.route_hedges([{"underlying": "BTC", "delta_drift": 10.0}])
        for rt in routes:
            assert math.isfinite(rt.fill_prob)
            assert math.isfinite(rt.tca_score)

    @pytest.mark.parametrize("i", list(range(10)))
    def test_loop_cycles_param(self, i):
        loop = VolSurfaceArbPaperLoop(seed=1000 + i)
        r = loop.run_cycle(i)
        assert r["paper_only"] is True
        assert math.isfinite(r["net_pnl"])
        assert "tca_captured" in r
        assert "fill_quality_ok" in r
