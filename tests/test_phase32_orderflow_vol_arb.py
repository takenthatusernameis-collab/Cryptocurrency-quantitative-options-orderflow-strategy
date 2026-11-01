"""
Tests for Phase 32: Production-Grade Orderflow Microstructure + Crypto Options
Cross-Venue Execution Quality & Live Risk Controls.

Deterministic, no network, fixed seeds, >=40 substantive tests. PAPER-ONLY.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from src.execution.phase32_execution_quality import (
    ExecutionQualityEngine,
    ExecutionQualityConfig32,
    SlippageEstimate,
    TCAResult,
    VenueComparison,
    ExecutionQualityCycleResult,
)
from src.integration.phase32_vol_arb_orderflow_loop import (
    VolArbOrderflowLoop,
    VolArbOrderflowLoopConfig32,
    VolArbOrderflowCycleResult,
)
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrator,
    OrderflowAlphaIntegrationConfig32,
    OrderflowAlphaIntegrationResult,
    IntegrationCycleResult,
)
from src.risk.phase32_live_risk_controls import (
    LiveRiskControls,
    LiveRiskControlsConfig32,
    PositionLimitResult,
    KillSwitchCoordination,
    LiveRiskCycleResult,
)


# ---------------------------------------------------------------------------
# OrderflowAlphaIntegrator
# ---------------------------------------------------------------------------

class TestOrderflowAlphaIntegrator:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            OrderflowAlphaIntegrator(
                OrderflowAlphaIntegrationConfig32(paper_only=False)
            )

    def test_default_config_paper_only(self):
        i = OrderflowAlphaIntegrator(seed=1)
        assert i.config.paper_only is True
        assert i.config.underlyings == ("BTC", "ETH", "SOL", "XRP")
        assert i.alpha_engine is not None

    def test_custom_config(self):
        c = OrderflowAlphaIntegrationConfig32(
            seed=7, cycles=3, underlyings=("BTC", "ETH"), orderflow_weight=0.7
        )
        i = OrderflowAlphaIntegrator(config=c, seed=7)
        assert i.config.cycles == 3
        assert i.config.underlyings == ("BTC", "ETH")
        assert i.config.orderflow_weight == 0.7

    def test_integrate_cycle_structure(self):
        i = OrderflowAlphaIntegrator(seed=2)
        res = i.integrate_cycle(1, {"equity": 150000.0})
        assert isinstance(res, IntegrationCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert res.snapshots_processed == len(i.config.underlyings) * len(i.config.venues)
        assert res.candidates >= 0
        assert math.isfinite(res.avg_fused_score)
        assert math.isfinite(res.max_fused_score)
        assert 0.0 <= res.avg_fused_score <= 1.0
        assert 0.0 <= res.max_fused_score <= 1.0

    def test_integrated_result_fields(self):
        i = OrderflowAlphaIntegrator(seed=3)
        res = i.integrate_cycle(1)
        assert len(i.results) == 1
        for r in i._history:
            assert isinstance(r, OrderflowAlphaIntegrationResult)
            assert r.paper_only is True
            assert math.isfinite(r.fused_score)
            assert math.isfinite(r.orderflow_score)
            assert math.isfinite(r.vol_arb_score)
            assert math.isfinite(r.decay_factor)
            assert 0.0 <= r.decay_factor <= 1.0
            assert math.isfinite(r.cumulative_delta)
            assert math.isfinite(r.imbalance)
            assert math.isfinite(r.vpin_lite)
            assert math.isfinite(r.absorption_score)
            assert math.isfinite(r.sweep_score)

    def test_decay_reduces_over_cycles(self):
        i = OrderflowAlphaIntegrator(seed=4)
        first = None
        for c in range(1, 6):
            r = i.integrate_cycle(c)
            if first is None:
                first = r
        last = i.results[-1]
        assert last.max_fused_score <= first.max_fused_score + 1e-9

    def test_confirmed_subset_of_candidates(self):
        i = OrderflowAlphaIntegrator(seed=5)
        i.integrate_cycle(1)
        confirmed = [r for r in i._history if r.confirmed]
        assert len(confirmed) <= len(i._history)
        for r in confirmed:
            assert r.fused_score >= i.config.min_fused_score

    def test_generate_report_writes_files(self, tmp_path):
        i = OrderflowAlphaIntegrator(seed=6)
        i.run_campaign(cycles=3)
        rep = i.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["total_candidates"] >= 0

    def test_deterministic(self):
        i1 = OrderflowAlphaIntegrator(seed=7)
        r1 = i1.run_campaign(cycles=4)
        i2 = OrderflowAlphaIntegrator(seed=7)
        r2 = i2.run_campaign(cycles=4)
        assert r1["total_candidates"] == r2["total_candidates"]
        assert r1["total_confirmed"] == r2["total_confirmed"]
        assert r1["final_avg_fused_score"] == r2["final_avg_fused_score"]

    def test_all_finite(self):
        i = OrderflowAlphaIntegrator(seed=8)
        i.run_campaign(cycles=5)
        for r in i.results:
            assert math.isfinite(r.avg_fused_score)
            assert math.isfinite(r.max_fused_score)
            assert math.isfinite(r.total_cumulative_delta)


# ---------------------------------------------------------------------------
# ExecutionQualityEngine
# ---------------------------------------------------------------------------

class TestExecutionQualityEngine:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            ExecutionQualityEngine(ExecutionQualityConfig32(paper_only=False))

    def test_default_config_paper_only(self):
        e = ExecutionQualityEngine(seed=11)
        assert e.config.paper_only is True
        assert e.config.venues == ("deribit", "okx", "bybit", "binance")

    def test_estimate_slippage_structure(self):
        e = ExecutionQualityEngine(seed=12)
        est = e.estimate_slippage("ETH", "buy", 50000.0, "deribit", 1, mid_price=4000.0)
        assert isinstance(est, SlippageEstimate)
        assert est.symbol == "ETH"
        assert est.side == "buy"
        assert est.venue == "deribit"
        assert est.paper_only is True
        assert math.isfinite(est.slippage_bps)
        assert math.isfinite(est.expected_fill_price)
        assert math.isfinite(est.latency_ms)
        assert math.isfinite(est.fill_rate)
        assert math.isfinite(est.total_cost_bps)
        assert 0.0 <= est.fill_rate <= 1.0
        assert est.slippage_bps >= 0.0
        assert est.total_cost_bps >= 0.0

    def test_slippage_bounded(self):
        e = ExecutionQualityEngine(seed=13)
        for v in e.config.venues:
            est = e.estimate_slippage("BTC", "sell", 1_000_000.0, v, 2, mid_price=65000.0)
            assert est.slippage_bps <= e.config.max_slippage_bps + 1e-9

    def test_tca_per_fill_structure(self):
        e = ExecutionQualityEngine(seed=14)
        tca = e.tca_per_fill(
            "f1", "ETH", "buy", "deribit", 50000.0, 4000.0, 4000.08, 1
        )
        assert isinstance(tca, TCAResult)
        assert tca.fill_id == "f1"
        assert tca.paper_only is True
        assert math.isfinite(tca.realized_slippage_bps)
        assert math.isfinite(tca.timing_cost_bps)
        assert math.isfinite(tca.fee_bps)
        assert math.isfinite(tca.total_cost_bps)
        assert math.isfinite(tca.mid_price)
        assert math.isfinite(tca.fill_price)

    def test_compare_venues_ranked(self):
        e = ExecutionQualityEngine(seed=15)
        comps = e.compare_venues("ETH", "buy", 50000.0, 1, mid_price=4000.0)
        assert len(comps) == len(e.config.venues)
        ranks = [c.rank for c in comps]
        assert sorted(ranks) == list(range(1, len(comps) + 1))
        for c in comps:
            assert isinstance(c, VenueComparison)
            assert math.isfinite(c.slippage_bps)
            assert math.isfinite(c.latency_ms)
            assert math.isfinite(c.total_cost_bps)
            assert math.isfinite(c.quality_score)
            assert 0.0 <= c.quality_score <= 1.0
        # best venue has lowest total cost
        assert comps[0].total_cost_bps <= comps[-1].total_cost_bps + 1e-9

    def test_run_cycle_structure(self):
        e = ExecutionQualityEngine(seed=16)
        res = e.run_cycle(1, {"side": "buy", "notional_usd": 50000.0, "mid_price": 4000.0, "symbol": "ETH"})
        assert isinstance(res, ExecutionQualityCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert res.slippage_estimates == len(e.config.venues)
        assert math.isfinite(res.avg_slippage_bps)
        assert math.isfinite(res.max_slippage_bps)
        assert math.isfinite(res.avg_total_cost_bps)
        assert res.venues_compared == len(e.config.venues)
        assert res.best_venue in e.config.venues

    def test_generate_report_writes_files(self, tmp_path):
        e = ExecutionQualityEngine(seed=17)
        e.run_campaign(cycles=3)
        rep = e.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert len(rep["report"]["venue_rankings"]) == len(e.config.venues)

    def test_deterministic(self):
        e1 = ExecutionQualityEngine(seed=18)
        r1 = e1.run_campaign(cycles=4)
        e2 = ExecutionQualityEngine(seed=18)
        r2 = e2.run_campaign(cycles=4)
        assert r1["total_slippage_estimates"] == r2["total_slippage_estimates"]
        assert r1["final_avg_slippage_bps"] == r2["final_avg_slippage_bps"]

    def test_all_finite(self):
        e = ExecutionQualityEngine(seed=19)
        e.run_campaign(cycles=5)
        for r in e.results:
            assert math.isfinite(r.avg_slippage_bps)
            assert math.isfinite(r.max_slippage_bps)
            assert math.isfinite(r.avg_total_cost_bps)


# ---------------------------------------------------------------------------
# LiveRiskControls
# ---------------------------------------------------------------------------

class TestLiveRiskControls:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            LiveRiskControls(LiveRiskControlsConfig32(paper_only=False))

    def test_default_config_paper_only(self):
        r = LiveRiskControls(seed=21)
        assert r.config.paper_only is True
        assert r.config.max_leverage == 5.0
        assert r.deployment_controller is not None

    def test_check_position_limits_allowed(self):
        r = LiveRiskControls(seed=22)
        res = r.check_position_limits("BTC", "buy", 20000.0, equity=150000.0)
        assert isinstance(res, PositionLimitResult)
        assert res.paper_only is True
        assert math.isfinite(res.notional_usd)
        assert math.isfinite(res.leverage)
        assert math.isfinite(res.margin_usage_pct)
        assert res.allowed is True
        assert res.blocked_reasons == ()

    def test_check_position_limits_blocked_notional(self):
        r = LiveRiskControls(seed=23)
        res = r.check_position_limits("BTC", "buy", 2_000_000.0, equity=150000.0)
        assert res.allowed is False
        assert "max_position_notional" in res.blocked_reasons

    def test_check_position_limits_blocked_leverage(self):
        r = LiveRiskControls(seed=24)
        res = r.check_position_limits("ETH", "buy", 1_000_000.0, equity=100000.0)
        assert res.allowed is False
        assert "max_leverage" in res.blocked_reasons

    def test_check_position_limits_blocked_drawdown(self):
        r = LiveRiskControls(seed=25)
        r.drawdown_pct = 0.15
        res = r.check_position_limits("BTC", "buy", 50000.0, equity=150000.0)
        assert res.allowed is False
        assert "max_drawdown" in res.blocked_reasons

    def test_coordinate_kill_switch_structure(self):
        r = LiveRiskControls(seed=26)
        ks = r.coordinate_kill_switch(drawdown_pct=0.01, pnl_usd=100.0)
        assert isinstance(ks, KillSwitchCoordination)
        assert ks.paper_only is True
        assert isinstance(ks.kill_switch_active, bool)
        assert isinstance(ks.coordinated_with_phase31, bool)
        assert math.isfinite(float(ks.cycles_blocked))

    def test_coordinate_kill_switch_triggered_drawdown(self):
        r = LiveRiskControls(seed=27)
        ks = r.coordinate_kill_switch(drawdown_pct=0.2, pnl_usd=100.0)
        assert ks.kill_switch_active is True

    def test_coordinate_kill_switch_triggered_pnl(self):
        r = LiveRiskControls(seed=28)
        ks = r.coordinate_kill_switch(drawdown_pct=0.01, pnl_usd=-100_000.0)
        assert ks.kill_switch_active is True

    def test_run_cycle_structure(self):
        r = LiveRiskControls(seed=29)
        res = r.run_cycle(
            1,
            {
                "equity": 150000.0,
                "drawdown_pct": 0.01,
                "pnl_usd": 100.0,
                "daily_loss_usd": 0.0,
                "positions": [
                    {"symbol": "BTC", "side": "buy", "notional_usd": 50000.0},
                    {"symbol": "ETH", "side": "sell", "notional_usd": 30000.0},
                ],
            },
        )
        assert isinstance(res, LiveRiskCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert res.positions_checked == 2
        assert math.isfinite(res.drawdown_pct)
        assert math.isfinite(res.margin_usage_pct)
        assert math.isfinite(res.leverage)
        assert isinstance(res.risk_ok, bool)
        assert isinstance(res.kill_switch_active, bool)

    def test_run_cycle_blocks_oversized(self):
        r = LiveRiskControls(seed=30)
        res = r.run_cycle(
            1,
            {
                "equity": 150000.0,
                "drawdown_pct": 0.01,
                "pnl_usd": 100.0,
                "daily_loss_usd": 0.0,
                "positions": [
                    {"symbol": "BTC", "side": "buy", "notional_usd": 2_000_000.0}
                ],
            },
        )
        assert res.positions_blocked >= 1
        assert res.risk_ok is False

    def test_generate_report_writes_files(self, tmp_path):
        r = LiveRiskControls(seed=31)
        r.run_campaign(cycles=3)
        rep = r.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["final_risk_ok"] is True

    def test_deterministic(self):
        r1 = LiveRiskControls(seed=32)
        v1 = r1.run_campaign(cycles=4)
        r2 = LiveRiskControls(seed=32)
        v2 = r2.run_campaign(cycles=4)
        assert v1["total_positions_checked"] == v2["total_positions_checked"]
        assert v1["final_drawdown_pct"] == v2["final_drawdown_pct"]

    def test_all_finite(self):
        r = LiveRiskControls(seed=33)
        r.run_campaign(cycles=5)
        for res in r.results:
            assert math.isfinite(res.drawdown_pct)
            assert math.isfinite(res.margin_usage_pct)
            assert math.isfinite(res.leverage)


# ---------------------------------------------------------------------------
# VolArbOrderflowLoop (integration)
# ---------------------------------------------------------------------------

class TestVolArbOrderflowLoop:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            VolArbOrderflowLoop(VolArbOrderflowLoopConfig32(paper_only=False))

    def test_default_config(self):
        l = VolArbOrderflowLoop(seed=34)
        assert l.config.paper_only is True
        assert l.loop31 is not None
        assert l.orderflow is not None
        assert l.execution is not None
        assert l.risk is not None

    def test_run_cycle_structure(self):
        l = VolArbOrderflowLoop(seed=35)
        res = l.run_cycle(1, {"equity": 150000.0, "drawdown_pct": 0.01, "pnl_usd": 0.0})
        assert isinstance(res, VolArbOrderflowCycleResult)
        assert res.cycle == 1
        assert res.paper_only is True
        assert isinstance(res.deploy_allowed, bool)
        assert isinstance(res.kill_switch_active, bool)
        assert isinstance(res.risk_ok, bool)
        assert res.dislocations >= 0
        assert res.signals >= 0
        assert res.orderflow_candidates >= 0
        assert res.orderflow_confirmed >= 0
        assert res.orderflow_confirmed <= res.orderflow_candidates
        assert math.isfinite(res.pnl_usd)
        assert math.isfinite(res.drawdown_pct)
        assert math.isfinite(res.avg_slippage_bps)
        assert math.isfinite(res.max_slippage_bps)
        assert math.isfinite(res.avg_total_cost_bps)
        assert res.best_venue in l.config.venues

    def test_run_campaign_deterministic(self):
        l1 = VolArbOrderflowLoop(seed=36)
        r1 = l1.run_campaign(cycles=5)
        l2 = VolArbOrderflowLoop(seed=36)
        r2 = l2.run_campaign(cycles=5)
        assert r1["final_pnl_usd"] == r2["final_pnl_usd"]
        assert r1["cycles"] == 5
        assert len(r1["reports"]) == 5
        assert r1["paper_only"] is True
        assert r1["total_signals"] == r2["total_signals"]
        assert r1["total_orderflow_confirmed"] == r2["total_orderflow_confirmed"]

    def test_campaign_report_writes_files(self, tmp_path):
        l = VolArbOrderflowLoop(seed=37)
        l.run_campaign(cycles=3)
        rep = l.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert rep["paper_only"] is True
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["report"]["kill_switch_active"] is False

    def test_cycle_results_finite(self):
        l = VolArbOrderflowLoop(seed=38)
        l.run_campaign(cycles=4)
        for r in l.results:
            assert math.isfinite(r.pnl_usd)
            assert math.isfinite(r.drawdown_pct)
            assert math.isfinite(r.avg_slippage_bps)
            assert math.isfinite(r.max_slippage_bps)
            assert math.isfinite(r.avg_total_cost_bps)

    def test_kill_switch_blocks_deploy(self):
        l = VolArbOrderflowLoop(seed=39)
        l.run_cycle(1, {"equity": 150000.0, "drawdown_pct": 0.01, "pnl_usd": 0.0})
        l.run_cycle(2, {"equity": 150000.0, "drawdown_pct": 0.2, "pnl_usd": 0.0})
        assert l.loop31.deployment.kill_switch.active is True
        later = l.run_cycle(3, {"equity": 150000.0, "drawdown_pct": 0.01, "pnl_usd": 0.0})
        assert later.deploy_allowed is False


# ---------------------------------------------------------------------------
# Determinism / finite numerics / no placeholders across modules
# ---------------------------------------------------------------------------

class TestDeterminismAndFinite:
    def test_orderflow_deterministic(self):
        i1 = OrderflowAlphaIntegrator(seed=90)
        d1 = i1.run_campaign(cycles=3)
        i2 = OrderflowAlphaIntegrator(seed=90)
        d2 = i2.run_campaign(cycles=3)
        assert d1["total_candidates"] == d2["total_candidates"]

    def test_execution_deterministic(self):
        e1 = ExecutionQualityEngine(seed=91)
        v1 = e1.run_campaign(cycles=3)
        e2 = ExecutionQualityEngine(seed=91)
        v2 = e2.run_campaign(cycles=3)
        assert v1["final_avg_slippage_bps"] == v2["final_avg_slippage_bps"]

    def test_risk_deterministic(self):
        r1 = LiveRiskControls(seed=92)
        k1 = r1.run_campaign(cycles=3)
        r2 = LiveRiskControls(seed=92)
        k2 = r2.run_campaign(cycles=3)
        assert k1["final_drawdown_pct"] == k2["final_drawdown_pct"]

    def test_no_placeholders_in_modules(self):
        import src.execution.phase32_execution_quality as eq
        import src.integration.phase32_vol_arb_orderflow_loop as integ
        import src.orderflow.phase32_orderflow_alpha_integration as of
        import src.risk.phase32_live_risk_controls as risk
        for mod in (eq, integ, of, risk):
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
        from scripts.run_phase32_orderflow_vol_arb_campaign import main
        import sys

        argv = [
            "run_phase32",
            "--cycles",
            "3",
            "--seed",
            "42",
            "--outdir",
            str(tmp_path),
        ]
        old = sys.argv
        sys.argv = argv
        try:
            code = main()
        finally:
            sys.argv = old
        assert code == 0
        assert (tmp_path / "PHASE32_CAMPAIGN_SUMMARY.json").exists()
        assert (tmp_path / "PHASE32_CAMPAIGN_SUMMARY.md").exists()
        for art in (
            "PHASE32_ORDERFLOW_ALPHA_REPORT.json",
            "PHASE32_EXECUTION_QUALITY_REPORT.json",
            "PHASE32_LIVE_RISK_REPORT.json",
            "PHASE32_VOL_ARB_ORDERFLOW_LOOP_REPORT.json",
        ):
            assert (tmp_path / art).exists(), art

    def test_script_rejects_live(self, tmp_path):
        from scripts.run_phase32_orderflow_vol_arb_campaign import main
        import sys

        argv = [
            "run_phase32",
            "--cycles",
            "1",
            "--seed",
            "42",
            "--modes",
            "live",
            "--outdir",
            str(tmp_path),
        ]
        old = sys.argv
        sys.argv = argv
        try:
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = old
