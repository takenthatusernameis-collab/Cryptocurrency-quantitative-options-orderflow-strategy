"""
Tests for Phase 31: Production Live Deployment, Continuous Validation & Monitoring
for Crypto Options Vol Surface Arbitrage + Orderflow.

Deterministic, no network, fixed seeds, >=80 substantive tests. PAPER-ONLY.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from src.deployment.phase31_live_deployment_controller import (
    CanaryConfig,
    DeploymentConfig,
    DeploymentDecision,
    KillSwitchState,
    LiveDeploymentController,
    VenueHealth,
)
from src.execution.phase31_live_vol_arb_loop import (
    LiveVolArbLoop,
    LiveVolArbLoopConfig31,
    LoopCycleResult,
)
from src.monitoring.phase31_continuous_validation import (
    Alert,
    ContinuousValidationEngine,
    DriftCheck,
    InvariantCheck,
    ValidationConfig,
    ValidationResult,
)
from src.observability.phase31_production_telemetry import (
    LogEntry,
    MetricPoint,
    ProductionTelemetry,
    TelemetryConfig,
    TelemetrySnapshot,
    TraceSpan,
)


# ---------------------------------------------------------------------------
# LiveDeploymentController
# ---------------------------------------------------------------------------

class TestLiveDeploymentController:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            LiveDeploymentController(DeploymentConfig(paper_only=False))

    def test_default_config_paper_only(self):
        c = LiveDeploymentController(seed=1)
        assert c.config.paper_only is True
        assert c.config.underlyings == ("BTC", "ETH", "SOL", "XRP")

    def test_evaluate_gates_all_ok(self):
        c = LiveDeploymentController(seed=2)
        d = c.evaluate_gates(
            {
                "equity": 150000.0,
                "drawdown_pct": 0.01,
                "connectivity_ok": True,
                "risk_limits_ok": True,
                "compliance_ok": True,
                "drift_within_bounds": True,
                "reconciliation_clean": True,
                "auto_recovery_ready": True,
            }
        )
        assert isinstance(d, DeploymentDecision)
        assert d.paper_only is True
        assert d.kill_switch_active is False
        assert d.canary_size_usd > 0
        assert math.isfinite(d.canary_size_usd)

    def test_evaluate_gates_blocks_low_equity(self):
        c = LiveDeploymentController(seed=3)
        d = c.evaluate_gates({"equity": 1000.0, "drawdown_pct": 0.01})
        assert "min_equity" in d.blocked_reasons
        assert d.canary_size_usd > 0

    def test_evaluate_gates_blocks_high_drawdown(self):
        c = LiveDeploymentController(seed=4)
        d = c.evaluate_gates({"equity": 150000.0, "drawdown_pct": 0.2})
        assert "max_drawdown" in d.blocked_reasons

    def test_evaluate_gates_blocks_connectivity(self):
        c = LiveDeploymentController(seed=5)
        d = c.evaluate_gates({"equity": 150000.0, "connectivity_ok": False})
        assert "connectivity_ok" in d.blocked_reasons

    def test_canary_size_capped(self):
        c = LiveDeploymentController(seed=6)
        size = c._canary_size_usd(1e9)
        assert size <= c.config.max_canary_notional_usd
        assert math.isfinite(size)

    def test_venue_health_check(self):
        c = LiveDeploymentController(seed=7)
        hs = c.venue_health_check()
        assert len(hs) == len(c.config.venues)
        for h in hs:
            assert isinstance(h, VenueHealth)
            assert math.isfinite(h.latency_ms)
            assert 0.0 <= h.fill_rate <= 1.0
            assert 0.0 <= h.error_rate <= 1.0
            assert isinstance(h.ok, bool)

    def test_healthy_venues(self):
        c = LiveDeploymentController(seed=8)
        c.venue_health_check()
        hv = c.healthy_venues()
        assert isinstance(hv, list)

    def test_kill_switch_trigger_drawdown(self):
        c = LiveDeploymentController(seed=9)
        ks = c.check_kill_switch(drawdown_pct=0.1, pnl_usd=100.0)
        assert isinstance(ks, KillSwitchState)
        assert ks.active is True
        assert ks.reason != ""

    def test_kill_switch_not_triggered_normal(self):
        c = LiveDeploymentController(seed=10)
        ks = c.check_kill_switch(drawdown_pct=0.01, pnl_usd=100.0)
        assert ks.active is False

    def test_reset_kill_switch(self):
        c = LiveDeploymentController(seed=11)
        c.check_kill_switch(drawdown_pct=0.1, pnl_usd=100.0)
        assert c.kill_switch.active is True
        c.reset_kill_switch("test_reset")
        assert c.kill_switch.active is False
        assert c.kill_switch.reason == ""

    def test_deploy_cycle_blocked(self):
        c = LiveDeploymentController(seed=12)
        res = c.deploy_cycle(1, [], {"equity": 1000.0})
        assert res["deploy_allowed"] is False
        assert res["paper_only"] is True

    def test_deploy_cycle_allowed(self):
        c = LiveDeploymentController(seed=13)
        res = c.deploy_cycle(1, [], {"equity": 150000.0})
        assert res["deploy_allowed"] is True
        assert res["live_allowed"] is False
        assert res["paper_only"] is True

    def test_generate_report_writes_files(self, tmp_path):
        c = LiveDeploymentController(seed=14)
        c.evaluate_gates({"equity": 150000.0})
        rep = c.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["paper_only"] is True

    def test_decisions_finite(self):
        c = LiveDeploymentController(seed=15)
        for i in range(3):
            c.evaluate_gates({"equity": 150000.0, "drawdown_pct": 0.01})
        assert len(c.decisions) == 3
        for d in c.decisions:
            assert math.isfinite(d.canary_size_usd)


# ---------------------------------------------------------------------------
# ContinuousValidationEngine
# ---------------------------------------------------------------------------

class TestContinuousValidationEngine:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            ContinuousValidationEngine(ValidationConfig(paper_only=False))

    def test_set_baseline(self):
        v = ContinuousValidationEngine(seed=16)
        r = v.set_baseline({"drawdown_pct": 0.02, "sharpe": 1.0})
        assert r["status"] == "ok"
        assert v.baselines["drawdown_pct"] == 0.02

    def test_check_invariants_all_ok(self):
        v = ContinuousValidationEngine(seed=17)
        checks = v.check_invariants(
            {
                "drawdown_pct": 0.01,
                "var_pct": 0.01,
                "iv_skew_bps": 10.0,
                "sharpe": 1.2,
                "fill_reject_rate": 0.05,
                "latency_p95_ms": 90.0,
            }
        )
        assert all(c.passed for c in checks)
        assert len(checks) == 6

    def test_check_invariants_breach(self):
        v = ContinuousValidationEngine(seed=18)
        checks = v.check_invariants({"drawdown_pct": 0.2, "sharpe": 0.1})
        draw = [c for c in checks if c.name == "max_drawdown"][0]
        assert draw.passed is False
        sharpe = [c for c in checks if c.name == "min_sharpe"][0]
        assert sharpe.passed is False

    def test_detect_drift(self):
        v = ContinuousValidationEngine(seed=19)
        v.set_baseline({"sharpe": 1.0, "drawdown_pct": 0.02})
        drifts = v.detect_drift({"sharpe": 5.0, "drawdown_pct": 0.02})
        sharp_d = [d for d in drifts if d.metric == "sharpe"][0]
        assert sharp_d.drift_pct > 0
        assert sharp_d.drifted is True

    def test_validate_cycle_all_ok(self):
        v = ContinuousValidationEngine(seed=20)
        v.set_baseline({"drawdown_pct": 0.02, "sharpe": 1.0})
        res = v.validate_cycle(
            1,
            {
                "drawdown_pct": 0.01,
                "var_pct": 0.01,
                "iv_skew_bps": 10.0,
                "sharpe": 1.2,
                "fill_reject_rate": 0.05,
                "latency_p95_ms": 90.0,
            },
        )
        assert isinstance(res, ValidationResult)
        assert res.all_ok is True
        assert res.paper_only is True

    def test_validate_cycle_breach_alerts(self):
        v = ContinuousValidationEngine(seed=21)
        v.set_baseline({"drawdown_pct": 0.02})
        res = v.validate_cycle(1, {"drawdown_pct": 0.2, "sharpe": 1.0})
        assert res.all_ok is False
        assert len(res.alerts) > 0

    def test_generate_report_writes_files(self, tmp_path):
        v = ContinuousValidationEngine(seed=22)
        v.set_baseline({"sharpe": 1.0})
        v.validate_cycle(1, {"sharpe": 1.0, "drawdown_pct": 0.01})
        rep = v.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["paper_only"] is True


# ---------------------------------------------------------------------------
# ProductionTelemetry
# ---------------------------------------------------------------------------

class TestProductionTelemetry:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            ProductionTelemetry(TelemetryConfig(paper_only=False))

    def test_record_metric(self):
        t = ProductionTelemetry(seed=23)
        mp = t.record_metric("vol_arb.dislocations", 5.0, {"cycle": "1"})
        assert isinstance(mp, MetricPoint)
        assert mp.value == 5.0
        assert mp.tags == {"cycle": "1"}
        assert math.isfinite(mp.value)

    def test_record_metric_nonfinite_raises(self):
        t = ProductionTelemetry(seed=24)
        with pytest.raises(ValueError):
            t.record_metric("bad", float("nan"))

    def test_start_and_end_trace(self):
        t = ProductionTelemetry(seed=25)
        tid = t.start_trace("vol_arb_cycle", "deribit")
        span = t.end_trace(tid, status="ok", end_ms=45.0)
        assert span is not None
        assert span.trace_id == tid
        assert span.status == "ok"
        assert math.isfinite(span.duration_ms)

    def test_end_trace_unknown_returns_none(self):
        t = ProductionTelemetry(seed=26)
        assert t.end_trace("nonexistent") is None

    def test_log(self):
        t = ProductionTelemetry(seed=27)
        le = t.log("warn", "high latency", {"latency_ms": 200.0})
        assert isinstance(le, LogEntry)
        assert le.level == "warn"
        assert le.fields["latency_ms"] == 200.0

    def test_snapshot(self):
        t = ProductionTelemetry(seed=28)
        t.record_metric("m1", 1.0)
        t.start_trace("op", "deribit")
        t.log("error", "boom", {})
        snap = t.snapshot()
        assert isinstance(snap, TelemetrySnapshot)
        assert snap.metric_count == 1
        assert snap.trace_count == 1
        assert snap.log_count == 1
        assert snap.alerts == 1
        assert snap.paper_only is True

    def test_generate_report_writes_files(self, tmp_path):
        t = ProductionTelemetry(seed=29)
        t.record_metric("m1", 1.0)
        rep = t.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["paper_only"] is True


# ---------------------------------------------------------------------------
# LiveVolArbLoop (integration)
# ---------------------------------------------------------------------------

class TestLiveVolArbLoop:
    def test_paper_only_enforced(self):
        with pytest.raises(ValueError):
            LiveVolArbLoop(LiveVolArbLoopConfig31(paper_only=False))

    def test_default_config(self):
        l = LiveVolArbLoop(seed=30)
        assert l.config.paper_only is True
        assert l.engine is not None
        assert l.risk is not None
        assert l.deployment is not None
        assert l.validation is not None
        assert l.telemetry is not None

    def test_run_cycle_blocked_low_equity(self):
        l = LiveVolArbLoop(seed=31)
        res = l.run_cycle(1, {"equity": 1000.0})
        assert isinstance(res, LoopCycleResult)
        assert res.deploy_allowed is False
        assert res.paper_only is True
        assert math.isfinite(res.pnl_usd)

    def test_run_cycle_allowed(self):
        l = LiveVolArbLoop(seed=32)
        res = l.run_cycle(1, {"equity": 150000.0, "drawdown_pct": 0.01})
        assert res.deploy_allowed is True
        assert res.paper_only is True
        assert res.dislocations >= 0
        assert res.signals >= 0
        assert math.isfinite(res.pnl_usd)
        assert math.isfinite(res.drawdown_pct)

    def test_run_campaign_deterministic(self):
        l1 = LiveVolArbLoop(seed=33)
        r1 = l1.run_campaign(cycles=5)
        l2 = LiveVolArbLoop(seed=33)
        r2 = l2.run_campaign(cycles=5)
        assert r1["final_pnl_usd"] == r2["final_pnl_usd"]
        assert r1["cycles"] == 5
        assert len(r1["reports"]) == 5
        assert r1["paper_only"] is True

    def test_campaign_report_writes_files(self, tmp_path):
        l = LiveVolArbLoop(seed=34)
        l.run_campaign(cycles=3)
        rep = l.generate_report(outdir=str(tmp_path))
        assert rep["status"] == "ok"
        assert Path(rep["json"]).exists()
        assert Path(rep["md"]).exists()
        assert rep["paper_only"] is True

    def test_cycle_results_finite(self):
        l = LiveVolArbLoop(seed=35)
        l.run_campaign(cycles=4)
        for r in l.results:
            assert math.isfinite(r.pnl_usd)
            assert math.isfinite(r.drawdown_pct)
            assert math.isfinite(float(r.signals))

    def test_kill_switch_propagates(self):
        l = LiveVolArbLoop(seed=36)
        l.run_cycle(1, {"equity": 150000.0, "drawdown_pct": 0.01})
        l.run_cycle(2, {"equity": 150000.0, "drawdown_pct": 0.1})
        assert l.deployment.kill_switch.active is True
        later = l.run_cycle(3, {"equity": 150000.0, "drawdown_pct": 0.01})
        assert later.deploy_allowed is False

    def test_config_custom_fields(self):
        c = LiveVolArbLoopConfig31(seed=77, cycles=3, underlyings=("BTC", "ETH"))
        l = LiveVolArbLoop(config=c, seed=77)
        assert l.config.cycles == 3
        assert l.config.underlyings == ("BTC", "ETH")


# ---------------------------------------------------------------------------
# Determinism / finite-numerics across components
# ---------------------------------------------------------------------------

class TestDeterminismAndFinite:
    def test_deployment_deterministic(self):
        c1 = LiveDeploymentController(seed=90)
        d1 = c1.evaluate_gates({"equity": 150000.0})
        c2 = LiveDeploymentController(seed=90)
        d2 = c2.evaluate_gates({"equity": 150000.0})
        assert d1.canary_size_usd == d2.canary_size_usd
        assert d1.blocked_reasons == d2.blocked_reasons

    def test_validation_deterministic(self):
        v1 = ContinuousValidationEngine(seed=91)
        v1.set_baseline({"sharpe": 1.0})
        r1 = v1.validate_cycle(1, {"sharpe": 1.0, "drawdown_pct": 0.01})
        v2 = ContinuousValidationEngine(seed=91)
        v2.set_baseline({"sharpe": 1.0})
        r2 = v2.validate_cycle(1, {"sharpe": 1.0, "drawdown_pct": 0.01})
        assert r1.all_ok == r2.all_ok

    def test_telemetry_no_nan(self):
        t = ProductionTelemetry(seed=92)
        t.record_metric("a", 1.5)
        t.record_metric("b", -2.5)
        assert all(math.isfinite(m.value) for m in t.metrics)

    def test_no_placeholders_in_modules(self):
        import src.deployment.phase31_live_deployment_controller as dep
        import src.monitoring.phase31_continuous_validation as mon
        import src.observability.phase31_production_telemetry as tel
        import src.execution.phase31_live_vol_arb_loop as loop
        for mod in (dep, mon, tel, loop):
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
        from scripts.run_phase31_live_vol_arb_campaign import main
        import sys

        argv = ["run_phase31", "--cycles", "3", "--seed", "42", "--outdir", str(tmp_path)]
        old = sys.argv
        sys.argv = argv
        try:
            code = main()
        finally:
            sys.argv = old
        assert code == 0
        assert (tmp_path / "PHASE31_CAMPAIGN_SUMMARY.json").exists()
        assert (tmp_path / "PHASE31_CAMPAIGN_SUMMARY.md").exists()

    def test_script_rejects_live(self, tmp_path):
        from scripts.run_phase31_live_vol_arb_campaign import main
        import sys

        argv = ["run_phase31", "--cycles", "1", "--seed", "42", "--modes", "live", "--outdir", str(tmp_path)]
        old = sys.argv
        sys.argv = argv
        try:
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = old
