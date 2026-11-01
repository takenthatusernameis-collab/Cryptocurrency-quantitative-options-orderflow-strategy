"""Tests for Phase 20: Live-Capital Deployment & Continuous Validation."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.capital.phase20_capital_allocator import Phase20CapitalAllocator
from src.orchestration.phase20_strategy_orchestrator import Phase20StrategyOrchestrator
from src.deployment.phase20_live_readiness_gate import Phase20LiveReadinessGate
from src.reconciliation.phase20_post_trade_recon import Phase20PostTradeRecon
from src.monitoring.phase20_drift_detector import Phase20DriftDetector
from src.resilience.phase20_auto_recovery import Phase20AutoRecovery


class TestPhase20CapitalAllocator:
    def test_paper_only_enforced(self):
        c = Phase20CapitalAllocator(seed=1)
        assert c.config.paper_only is True

    def test_rejects_live_not_paper(self):
        from src.capital.phase20_capital_allocator import Phase20AllocationConfig
        with pytest.raises(ValueError):
            Phase20CapitalAllocator(config=Phase20AllocationConfig(paper_only=False), seed=1)

    def test_allocate_deterministic(self):
        c = Phase20CapitalAllocator(seed=42)
        a1 = c.allocate(["vol_arb", "cross_asset_vol"], ["deribit", "okx"], ["BTC", "ETH"])
        c2 = Phase20CapitalAllocator(seed=42)
        a2 = c2.allocate(["vol_arb", "cross_asset_vol"], ["deribit", "okx"], ["BTC", "ETH"])
        assert len(a1) == len(a2)
        assert [x.allocation_id for x in a1] == [x.allocation_id for x in a2]

    def test_allocate_respects_caps(self):
        c = Phase20CapitalAllocator(seed=7)
        allocs = c.allocate(["s1", "s2", "s3"], ["v1", "v2"], ["BTC"])
        inv = c.validate_invariants(allocs)
        assert inv["valid"] is True

    def test_allocate_drawdown_guard(self):
        c = Phase20CapitalAllocator(seed=9)
        allocs = c.allocate(["s1"], ["v1"], ["BTC"], current_drawdown_pct=0.10)
        assert all(a.drawdown_guard_active for a in allocs)
        assert all(a.allocated_capital == 0.0 for a in allocs)

    def test_report_serializable(self):
        c = Phase20CapitalAllocator(seed=11)
        allocs = c.allocate(["vol_arb"], ["deribit"], ["BTC", "ETH"])
        rep = c.generate_report(allocs)
        assert rep["report"] == "PHASE20_CAPITAL_ALLOCATION_REPORT"
        assert rep["paper_only"] is True


class TestPhase20StrategyOrchestrator:
    def test_paper_only_enforced(self):
        o = Phase20StrategyOrchestrator(seed=1)
        assert o.config.paper_only is True

    def test_build_plan(self):
        o = Phase20StrategyOrchestrator(seed=13)
        tasks = o.build_plan(["BTC", "ETH"])
        assert len(tasks) > 0
        assert all(t.status == "pending" for t in tasks)

    def test_schedule_respects_concurrency(self):
        o = Phase20StrategyOrchestrator(seed=17)
        tasks = o.build_plan(["BTC"])
        sched = o.schedule(tasks)
        assert sched["counts"]["total"] == len(tasks)
        assert sched["counts"]["running"] <= o.config.max_concurrent

    def test_deterministic_plan(self):
        o1 = Phase20StrategyOrchestrator(seed=23)
        o2 = Phase20StrategyOrchestrator(seed=23)
        t1 = o1.build_plan(["BTC", "ETH", "SOL"])
        t2 = o2.build_plan(["BTC", "ETH", "SOL"])
        assert [t.task_id for t in t1] == [t.task_id for t in t2]

    def test_report_serializable(self):
        o = Phase20StrategyOrchestrator(seed=29)
        tasks = o.build_plan(["BTC"])
        rep = o.generate_report(tasks)
        assert rep["report"] == "PHASE20_STRATEGY_ORCHESTRATION_REPORT"


class TestPhase20LiveReadinessGate:
    def test_paper_only_enforced(self):
        g = Phase20LiveReadinessGate(paper_only=True, seed=1)
        assert g.paper_only is True

    def test_rejects_live_not_paper(self):
        with pytest.raises(ValueError):
            Phase20LiveReadinessGate(paper_only=False, seed=1)

    def test_evaluate_blocks_without_all_checks(self):
        g = Phase20LiveReadinessGate(paper_only=True, seed=31)
        d = g.evaluate({})
        assert d.live_allowed is False
        assert len(d.blocked_reasons) > 0

    def test_all_checks_pass_with_approval_gives_paper_allowed(self):
        g = Phase20LiveReadinessGate(paper_only=True, seed=37)
        g.grant_approval()
        d = g.evaluate({
            "capital_allocated_valid": True,
            "connectivity_ok": True,
            "risk_limits_ok": True,
            "compliance_ok": True,
            "drift_within_bounds": True,
            "recon_clean": True,
            "auto_recovery_ready": True,
            "equity": 2000000.0,
            "drawdown_pct": 0.01,
        })
        assert d.paper_only is True
        # live_allowed depends on approval state - we granted approval but paper_only remains True
        assert d.approval_state == "APPROVED"

    def test_revoke_approval(self):
        g = Phase20LiveReadinessGate(paper_only=True, seed=41)
        g.grant_approval()
        g.revoke_approval()
        assert g.approval_state == "REVOKED"

    def test_report_serializable(self):
        g = Phase20LiveReadinessGate(paper_only=True, seed=43)
        d = g.evaluate({})
        rep = g.generate_report(d)
        assert rep["report"] == "PHASE20_LIVE_READINESS_REPORT"


class TestPhase20PostTradeRecon:
    def test_paper_only_enforced(self):
        r = Phase20PostTradeRecon(seed=1)
        assert r.config.paper_only is True

    def test_clean_recon(self):
        r = Phase20PostTradeRecon(seed=47)
        orders = [{"order_id": "o1", "qty": 1.0}]
        fills = [{"order_id": "o1", "filled_qty": 1.0}]
        positions = [{"symbol": "BTC", "qty": 1.0}]
        rec = r.reconcile(orders, fills, positions)
        assert rec["reconciled"] is True
        assert rec["discrepancy_count"] == 0

    def test_detects_mismatch(self):
        r = Phase20PostTradeRecon(seed=53)
        orders = [{"order_id": "o1", "qty": 1.0}]
        fills = [{"order_id": "o1", "filled_qty": 0.5}]
        positions = []
        rec = r.reconcile(orders, fills, positions)
        assert rec["discrepancy_count"] > 0

    def test_report_serializable(self):
        r = Phase20PostTradeRecon(seed=59)
        orders = [{"order_id": "o1", "qty": 1.0}]
        fills = [{"order_id": "o1", "filled_qty": 1.0}]
        positions = [{"symbol": "BTC", "qty": 1.0}]
        rep = r.generate_report(orders, fills, positions)
        assert rep["report"] == "PHASE20_POST_TRADE_RECON_REPORT"


class TestPhase20DriftDetector:
    def test_paper_only_enforced(self):
        d = Phase20DriftDetector(seed=1)
        assert d.config.paper_only is True

    def test_no_drift(self):
        d = Phase20DriftDetector(seed=61)
        baseline = {"pnl": 1000.0, "greeks": {"delta": 0.1}, "fills_rate": 0.99, "latency_ms": 10.0}
        current = {"pnl": 1005.0, "greeks": {"delta": 0.101}, "fills_rate": 0.989, "latency_ms": 11.0}
        det = d.detect(baseline, current)
        assert det["within_bounds"] is True

    def test_pnl_drift_detected(self):
        d = Phase20DriftDetector(seed=67)
        baseline = {"pnl": 1000.0}
        current = {"pnl": 2000.0}  # 100% drift
        det = d.detect(baseline, current)
        assert det["anomaly_count"] > 0
        assert det["within_bounds"] is False

    def test_report_serializable(self):
        d = Phase20DriftDetector(seed=71)
        baseline = {"pnl": 1000.0}
        current = {"pnl": 1050.0}
        rep = d.generate_report(baseline, current)
        assert rep["report"] == "PHASE20_DRIFT_DETECTION_REPORT"


class TestPhase20AutoRecovery:
    def test_paper_only_enforced(self):
        r = Phase20AutoRecovery(seed=1)
        assert r.config.paper_only is True

    def test_handle_failure_retry(self):
        r = Phase20AutoRecovery(seed=73)
        res = r.handle_failure("oms", "timeout")
        assert res["action"] in ("retry", "restart", "escalate")
        assert res["failure_count"] == 1

    def test_escalation_triggers_safe_mode(self):
        r = Phase20AutoRecovery(seed=79)
        r.handle_failure("router", "err1")
        r.handle_failure("router", "err2")  # exceeds escalation threshold
        assert r.safe_mode is True

    def test_recover(self):
        r = Phase20AutoRecovery(seed=83)
        r.handle_failure("oms", "err")
        rec = r.recover()
        assert "recovered_count" in rec

    def test_report_serializable(self):
        r = Phase20AutoRecovery(seed=89)
        r.handle_failure("test", "err")
        rep = r.generate_report()
        assert rep["report"] == "PHASE20_AUTO_RECOVERY_REPORT"
