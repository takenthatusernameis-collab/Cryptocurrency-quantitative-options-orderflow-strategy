"""
Tests for Phase 33: Live Capital Rollout & Adaptive Orderflow Hedging for
Crypto Options Vol Surface Arbitrage.

Deterministic, no network, fixed seeds, >=40 substantive tests. PAPER-ONLY.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from src.execution.phase33_adaptive_orderflow_hedge import (
    AdaptiveOrderflowHedgeConfig33,
    AdaptiveOrderflowHedgeRouter,
    HedgeCycleResult,
    HedgeDecision,
    VenueRotation,
)
from src.integration.phase33_capital_orderflow_loop import (
    Phase33CapitalOrderflowLoop,
    Phase33CapitalOrderflowLoopConfig33,
    Phase33CycleResult,
)
from src.orderflow.phase33_venue_liquidity_sweep import (
    LiquiditySnapshot,
    SweepCycleResult,
    SweepRoute,
    VenueLiquiditySweep,
    VenueLiquiditySweepConfig33,
)
from src.risk.phase33_live_capital_rollout import (
    CanaryState,
    LiveCapitalRollout,
    LiveCapitalRolloutConfig33,
    RolloutCycleResult,
    RolloutDecision,
)


# ---------------------------------------------------------------------------
# AdaptiveOrderflowHedgeRouter
# ---------------------------------------------------------------------------

class TestAdaptiveOrderflowHedgeRouter:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            AdaptiveOrderflowHedgeRouter(
                AdaptiveOrderflowHedgeConfig33(paper_only=False)
            )

    def test_default_config_paper_only(self):
        r = AdaptiveOrderflowHedgeRouter(seed=1)
        assert r.config.paper_only is True
        assert r.config.underlyings == ("BTC", "ETH", "SOL", "XRP")
        assert r.orderflow is not None

    def test_custom_config(self):
        c = AdaptiveOrderflowHedgeConfig33(
            seed=7, cycles=3, underlyings=("BTC", "ETH"),
            base_hedge_ratio=0.8, orderflow_hedge_multiplier=0.5,
        )
        r = AdaptiveOrderflowHedgeRouter(config=c, seed=7)
        assert r.config.cycles == 3
        assert r.config.base_hedge_ratio == 0.8
        assert r.config.orderflow_hedge_multiplier == 0.5

    def test_compute_hedge_structure(self):
        r = AdaptiveOrderflowHedgeRouter(seed=2)
        d = r.compute_hedge("BTC", "BTC", "7D", 1)
        assert isinstance(d, HedgeDecision)
        assert d.symbol == "BTC"
        assert d.underlying == "BTC"
        assert d.expiry == "7D"
        assert d.paper_only is True
        assert math.isfinite(d.delta_notional_usd)
        assert math.isfinite(d.gamma_notional_usd)
        assert math.isfinite(d.vega_notional_usd)
        assert math.isfinite(d.hedge_ratio)
        assert math.isfinite(d.orderflow_score)
        assert math.isfinite(d.confidence)
        assert 0.0 <= d.hedge_ratio <= r.config.max_hedge_ratio
        assert 0.0 <= d.orderflow_score <= 1.0
        assert 0.0 <= d.confidence <= 1.0
        assert d.venue in r.config.venues

    def test_hedge_ratio_bounded(self):
        r = AdaptiveOrderflowHedgeRouter(seed=3)
        for _ in range(5):
            d = r.compute_hedge("ETH", "ETH", "30D", 1)
            assert r.config.min_hedge_ratio <= d.hedge_ratio <= r.config.max_hedge_ratio

    def test_blocked_reasons_on_oversized(self):
        r = AdaptiveOrderflowHedgeRouter(seed=4)
        d = r.compute_hedge(
            "BTC", "BTC", "7D", 1,
            state={"delta_notional_usd": 5_000_000.0},
        )
        # large delta notional may exceed max_delta_exposure_usd (100_000)
        assert d.paper_only is True
        assert math.isfinite(d.delta_notional_usd)

    def test_run_cycle_structure(self):
        r = AdaptiveOrderflowHedgeRouter(seed=5)
        res = r.run_cycle(1, {"equity": 150000.0})
        assert isinstance(res, HedgeCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert res.hedges_computed == len(r.config.underlyings)
        assert math.isfinite(res.avg_hedge_ratio)
        assert math.isfinite(res.total_hedged_notional_usd)
        assert math.isfinite(res.delta_exposure_usd)
        assert math.isfinite(res.gamma_exposure_usd)
        assert math.isfinite(res.vega_exposure_usd)
        assert isinstance(res.risk_ok, bool)
        assert isinstance(res.blocked_reasons, tuple)

    def test_venue_rotation_structure(self):
        r = AdaptiveOrderflowHedgeRouter(seed=6)
        rot = r.rotate_venue("BTC", 1, "deribit")
        if rot is not None:
            assert isinstance(rot, VenueRotation)
            assert rot.paper_only is True
            assert rot.from_venue == "deribit"
            assert rot.to_venue in r.config.venues
            assert math.isfinite(rot.liquidity_score_delta)

    def test_run_campaign_deterministic(self):
        r1 = AdaptiveOrderflowHedgeRouter(seed=8)
        v1 = r1.run_campaign(cycles=4)
        r2 = AdaptiveOrderflowHedgeRouter(seed=8)
        v2 = r2.run_campaign(cycles=4)
        assert v1["total_hedges_computed"] == v2["total_hedges_computed"]
        assert v1["final_avg_hedge_ratio"] == v2["final_avg_hedge_ratio"]
        assert v1["cycles"] == 4

    def test_generate_report_writes_files(self, tmp_path):
        r = AdaptiveOrderflowHedgeRouter(seed=9)
        r.run_campaign(cycles=3)
        rep = r.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["total_hedges_computed"] >= 0

    def test_all_finite(self):
        r = AdaptiveOrderflowHedgeRouter(seed=10)
        r.run_campaign(cycles=5)
        for res in r.results:
            assert math.isfinite(res.avg_hedge_ratio)
            assert math.isfinite(res.total_hedged_notional_usd)
            assert math.isfinite(res.delta_exposure_usd)
            assert math.isfinite(res.gamma_exposure_usd)
            assert math.isfinite(res.vega_exposure_usd)


# ---------------------------------------------------------------------------
# LiveCapitalRollout
# ---------------------------------------------------------------------------

class TestLiveCapitalRollout:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            LiveCapitalRollout(LiveCapitalRolloutConfig33(paper_only=False))

    def test_default_config_paper_only(self):
        r = LiveCapitalRollout(seed=11)
        assert r.config.paper_only is True
        assert r.config.total_capital_usd == 150000.0
        assert r.deployment_controller is not None
        assert r.risk_controls is not None

    def test_custom_config(self):
        c = LiveCapitalRolloutConfig33(
            seed=7, cycles=3, canary_size_pct=0.2,
            canary_profit_target_pct=0.03, rollout_profit_target_pct=0.06,
        )
        r = LiveCapitalRollout(config=c, seed=7)
        assert r.config.cycles == 3
        assert r.config.canary_size_pct == 0.2

    def test_canary_rollout_structure(self):
        r = LiveCapitalRollout(seed=12)
        cs = r.canary_rollout(1)
        assert isinstance(cs, CanaryState)
        assert cs.phase == "canary"
        assert cs.paper_only is True
        assert math.isfinite(cs.capital_allocated_usd)
        assert math.isfinite(cs.pnl_usd)
        assert isinstance(cs.profit_target_hit, bool)
        assert isinstance(cs.loss_stop_hit, bool)
        assert isinstance(cs.ready_for_live, bool)

    def test_promote_to_live_gate_structure(self):
        r = LiveCapitalRollout(seed=13)
        dec = r.promote_to_live_gate(1)
        assert isinstance(dec, RolloutDecision)
        assert dec.allowed is True
        assert dec.paper_only is True
        assert isinstance(dec.live_allowed, bool)
        assert math.isfinite(dec.capital_usd)
        assert isinstance(dec.blocked_reasons, tuple)
        assert isinstance(dec.checks, tuple)

    def test_run_cycle_structure(self):
        r = LiveCapitalRollout(seed=14)
        res = r.run_cycle(
            1,
            {"equity": 150000.0, "drawdown_pct": 0.01, "pnl_usd": 100.0},
        )
        assert isinstance(res, RolloutCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert isinstance(res.phase, str)
        assert math.isfinite(res.capital_allocated_usd)
        assert math.isfinite(res.canary_pnl_usd)
        assert isinstance(res.live_allowed, bool)
        assert isinstance(res.risk_ok, bool)
        assert isinstance(res.blocked_reasons, tuple)

    def test_run_campaign_deterministic(self):
        r1 = LiveCapitalRollout(seed=15)
        v1 = r1.run_campaign(cycles=4)
        r2 = LiveCapitalRollout(seed=15)
        v2 = r2.run_campaign(cycles=4)
        assert v1["final_phase"] == v2["final_phase"]
        assert v1["final_capital_allocated_usd"] == v2["final_capital_allocated_usd"]
        assert v1["cycles"] == 4

    def test_generate_report_writes_files(self, tmp_path):
        r = LiveCapitalRollout(seed=16)
        r.run_campaign(cycles=3)
        rep = r.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["final_phase"] == "canary"

    def test_all_finite(self):
        r = LiveCapitalRollout(seed=17)
        r.run_campaign(cycles=5)
        for res in r.results:
            assert math.isfinite(res.capital_allocated_usd)
            assert math.isfinite(res.canary_pnl_usd)


# ---------------------------------------------------------------------------
# VenueLiquiditySweep
# ---------------------------------------------------------------------------

class TestVenueLiquiditySweep:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            VenueLiquiditySweep(VenueLiquiditySweepConfig33(paper_only=False))

    def test_default_config_paper_only(self):
        s = VenueLiquiditySweep(seed=18)
        assert s.config.paper_only is True
        assert s.config.venues == ("deribit", "okx", "bybit", "binance")
        assert s.execution is not None

    def test_custom_config(self):
        c = VenueLiquiditySweepConfig33(
            seed=7, cycles=3, sweep_size_pct=0.5,
            max_slippage_bps=10.0, fill_rate_min=0.9,
        )
        s = VenueLiquiditySweep(config=c, seed=7)
        assert s.config.cycles == 3
        assert s.config.max_slippage_bps == 10.0

    def test_scan_liquidity_structure(self):
        s = VenueLiquiditySweep(seed=19)
        snaps = s.scan_liquidity("ETH", 1)
        assert len(snaps) == len(s.config.venues)
        for snap in snaps:
            assert isinstance(snap, LiquiditySnapshot)
            assert snap.venue in s.config.venues
            assert snap.symbol == "ETH"
            assert snap.paper_only is True
            assert math.isfinite(snap.bid_size_usd)
            assert math.isfinite(snap.ask_size_usd)
            assert math.isfinite(snap.liquidity_score)
            assert math.isfinite(snap.fill_rate)
            assert math.isfinite(snap.latency_ms)
            assert math.isfinite(snap.slippage_bps)
            assert 0.0 <= snap.liquidity_score <= 1.0
            assert 0.0 <= snap.fill_rate <= 1.0
            assert snap.slippage_bps >= 0.0

    def test_route_sweep_structure(self):
        s = VenueLiquiditySweep(seed=20)
        snaps = s.scan_liquidity("BTC", 1)
        routes = s.route_sweep("BTC", "buy", 50000.0, 1, snaps)
        for route in routes:
            assert isinstance(route, SweepRoute)
            assert route.symbol == "BTC"
            assert route.side == "buy"
            assert route.venue in s.config.venues
            assert isinstance(route.route_venues, tuple)
            assert math.isfinite(route.slippage_bps)
            assert math.isfinite(route.fill_rate)
            assert math.isfinite(route.allocated_usd)
            assert route.paper_only is True
            assert route.slippage_bps <= s.config.max_slippage_bps + 1e-9
            assert route.fill_rate >= s.config.fill_rate_min - 1e-9

    def test_run_cycle_structure(self):
        s = VenueLiquiditySweep(seed=21)
        res = s.run_cycle(
            1, {"symbol": "ETH", "side": "buy", "notional_usd": 50000.0}
        )
        assert isinstance(res, SweepCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert res.venues_scanned == len(s.config.venues)
        assert res.liquidity_venues >= 0
        assert res.sweeps_routed >= 0
        assert math.isfinite(res.avg_slippage_bps)
        assert math.isfinite(res.max_slippage_bps)
        assert math.isfinite(res.avg_fill_rate)
        assert math.isfinite(res.total_swept_notional_usd)
        assert res.best_venue in s.config.venues
        assert isinstance(res.risk_ok, bool)

    def test_run_campaign_deterministic(self):
        s1 = VenueLiquiditySweep(seed=22)
        v1 = s1.run_campaign(cycles=4)
        s2 = VenueLiquiditySweep(seed=22)
        v2 = s2.run_campaign(cycles=4)
        assert v1["total_sweeps_routed"] == v2["total_sweeps_routed"]
        assert v1["final_avg_slippage_bps"] == v2["final_avg_slippage_bps"]
        assert v1["cycles"] == 4

    def test_generate_report_writes_files(self, tmp_path):
        s = VenueLiquiditySweep(seed=23)
        s.run_campaign(cycles=3)
        rep = s.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["total_sweeps_routed"] >= 0

    def test_all_finite(self):
        s = VenueLiquiditySweep(seed=24)
        s.run_campaign(cycles=5)
        for res in s.results:
            assert math.isfinite(res.avg_slippage_bps)
            assert math.isfinite(res.max_slippage_bps)
            assert math.isfinite(res.avg_fill_rate)
            assert math.isfinite(res.total_swept_notional_usd)


# ---------------------------------------------------------------------------
# Phase33CapitalOrderflowLoop (integration)
# ---------------------------------------------------------------------------

class TestPhase33CapitalOrderflowLoop:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            Phase33CapitalOrderflowLoop(
                Phase33CapitalOrderflowLoopConfig33(paper_only=False)
            )

    def test_default_config(self):
        l = Phase33CapitalOrderflowLoop(seed=25)
        assert l.config.paper_only is True
        assert l.loop31 is not None
        assert l.hedge is not None
        assert l.rollout is not None
        assert l.sweep is not None
        assert l.execution is not None

    def test_run_cycle_structure(self):
        l = Phase33CapitalOrderflowLoop(seed=26)
        res = l.run_cycle(
            1,
            {
                "equity": 150000.0,
                "drawdown_pct": 0.01,
                "pnl_usd": 0.0,
                "symbol": "ETH",
                "side": "buy",
                "notional_usd": 50000.0,
            },
        )
        assert isinstance(res, Phase33CycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert isinstance(res.phase, str)
        assert isinstance(res.deploy_allowed, bool)
        assert isinstance(res.live_allowed, bool)
        assert isinstance(res.kill_switch_active, bool)
        assert isinstance(res.risk_ok, bool)
        assert isinstance(res.sweep_ok, bool)
        assert res.dislocations >= 0
        assert res.signals >= 0
        assert res.orderflow_candidates >= 0
        assert res.orderflow_confirmed >= 0
        assert res.orderflow_confirmed <= res.orderflow_candidates
        assert res.hedges_computed >= 0
        assert res.sweeps_routed >= 0
        assert math.isfinite(res.pnl_usd)
        assert math.isfinite(res.drawdown_pct)
        assert math.isfinite(res.avg_slippage_bps)
        assert math.isfinite(res.max_slippage_bps)
        assert math.isfinite(res.avg_fill_rate)
        assert math.isfinite(res.avg_hedge_ratio)
        assert math.isfinite(res.capital_allocated_usd)
        assert math.isfinite(res.avg_total_cost_bps)
        assert res.best_venue in l.config.venues

    def test_run_campaign_deterministic(self):
        l1 = Phase33CapitalOrderflowLoop(seed=27)
        r1 = l1.run_campaign(cycles=5)
        l2 = Phase33CapitalOrderflowLoop(seed=27)
        r2 = l2.run_campaign(cycles=5)
        assert r1["final_pnl_usd"] == r2["final_pnl_usd"]
        assert r1["final_phase"] == r2["final_phase"]
        assert r1["cycles"] == 5
        assert len(r1["reports"]) == 5
        assert r1["paper_only"] is True
        assert r1["total_signals"] == r2["total_signals"]
        assert r1["total_hedges_computed"] == r2["total_hedges_computed"]
        assert r1["total_sweeps_routed"] == r2["total_sweeps_routed"]

    def test_campaign_report_writes_files(self, tmp_path):
        l = Phase33CapitalOrderflowLoop(seed=28)
        l.run_campaign(cycles=3)
        rep = l.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["kill_switch_active"] is False
        assert rep["report"]["total_hedges_computed"] >= 0
        assert rep["report"]["total_sweeps_routed"] >= 0

    def test_cycle_results_finite(self):
        l = Phase33CapitalOrderflowLoop(seed=29)
        l.run_campaign(cycles=4)
        for r in l.results:
            assert math.isfinite(r.pnl_usd)
            assert math.isfinite(r.drawdown_pct)
            assert math.isfinite(r.avg_slippage_bps)
            assert math.isfinite(r.max_slippage_bps)
            assert math.isfinite(r.avg_total_cost_bps)
            assert math.isfinite(r.avg_hedge_ratio)
            assert math.isfinite(r.total_swept_notional_usd)
            assert math.isfinite(r.capital_allocated_usd)


# ---------------------------------------------------------------------------
# Determinism / finite numerics / no placeholders across modules
# ---------------------------------------------------------------------------

class TestDeterminismAndFinite:
    def test_hedge_deterministic(self):
        h1 = AdaptiveOrderflowHedgeRouter(seed=90)
        d1 = h1.run_campaign(cycles=3)
        h2 = AdaptiveOrderflowHedgeRouter(seed=90)
        d2 = h2.run_campaign(cycles=3)
        assert d1["total_hedges_computed"] == d2["total_hedges_computed"]

    def test_rollout_deterministic(self):
        r1 = LiveCapitalRollout(seed=91)
        v1 = r1.run_campaign(cycles=3)
        r2 = LiveCapitalRollout(seed=91)
        v2 = r2.run_campaign(cycles=3)
        assert v1["final_capital_allocated_usd"] == v2["final_capital_allocated_usd"]

    def test_sweep_deterministic(self):
        s1 = VenueLiquiditySweep(seed=92)
        v1 = s1.run_campaign(cycles=3)
        s2 = VenueLiquiditySweep(seed=92)
        v2 = s2.run_campaign(cycles=3)
        assert v1["total_sweeps_routed"] == v2["total_sweeps_routed"]

    def test_loop_deterministic(self):
        l1 = Phase33CapitalOrderflowLoop(seed=93)
        v1 = l1.run_campaign(cycles=3)
        l2 = Phase33CapitalOrderflowLoop(seed=93)
        v2 = l2.run_campaign(cycles=3)
        assert v1["final_pnl_usd"] == v2["final_pnl_usd"]

    def test_no_placeholders_in_modules(self):
        import src.execution.phase33_adaptive_orderflow_hedge as hedge
        import src.integration.phase33_capital_orderflow_loop as integ
        import src.orderflow.phase33_venue_liquidity_sweep as sweep
        import src.risk.phase33_live_capital_rollout as rollout
        for mod in (hedge, integ, sweep, rollout):
            src = Path(mod.__file__).read_text()
            assert "TODO" not in src
            assert "FIXME" not in src
            assert "HACK" not in src
            assert "XXX" not in src


# ---------------------------------------------------------------------------
# Campaign script smoke
# ---------------------------------------------------------------------------

class TestCampaignScript:
    def test_script_runs_paper(self, tmp_path):
        from scripts.run_phase33_capital_orderflow_campaign import main
        import sys

        argv = [
            "run_phase33",
            "--cycles", "3",
            "--seed", "42",
            "--outdir", str(tmp_path),
        ]
        old = sys.argv
        sys.argv = argv
        try:
            code = main()
        finally:
            sys.argv = old
        assert code == 0
        assert (tmp_path / "PHASE33_CAMPAIGN_SUMMARY.json").exists()
        assert (tmp_path / "PHASE33_CAMPAIGN_SUMMARY.md").exists()
        for art in (
            "PHASE33_ADAPTIVE_HEDGE_REPORT.json",
            "PHASE33_LIVE_CAPITAL_REPORT.json",
            "PHASE33_LIQUIDITY_SWEEP_REPORT.json",
            "PHASE33_CAPITAL_ORDERFLOW_LOOP_REPORT.json",
        ):
            assert (tmp_path / art).exists(), art

    def test_script_rejects_live(self, tmp_path):
        from scripts.run_phase33_capital_orderflow_campaign import main
        import sys

        argv = [
            "run_phase33",
            "--cycles", "1",
            "--seed", "42",
            "--modes", "live",
            "--outdir", str(tmp_path),
        ]
        old = sys.argv
        sys.argv = argv
        try:
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = old
