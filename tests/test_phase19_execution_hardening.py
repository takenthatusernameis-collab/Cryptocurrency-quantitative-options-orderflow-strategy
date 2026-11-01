"""Tests for Phase 19: Live-Capital Execution Hardening (paper->live gate, OMS, execution risk)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.execution.phase19_paper_live_gate import PaperLiveGate
from src.execution.phase19_order_manager import OrderManager, OrderState
from src.risk.phase19_execution_risk import ExecutionRiskEngine
from src.alpha.phase17_campaign import Phase17Campaign


class TestPhase19PaperLiveGate:
    def test_gate_paper_only_enforced(self):
        g = PaperLiveGate(paper_only=True, seed=123)
        assert g.paper_only is True

    def test_gate_rejects_live_not_paper(self):
        with pytest.raises(ValueError):
            PaperLiveGate(paper_only=False, seed=1)

    def test_gate_evaluate_blocks_live_without_acks(self):
        g = PaperLiveGate(paper_only=True, seed=42)
        d = g.evaluate(state={"equity": 150000, "total_notional": 50000, "drawdown_pct": 0.01,
                             "capital_ack": False, "risk_ack": False, "manual_approval": False,
                             "connectivity_ok": False, "compliance_ok": False},
                      intents_count=5, confirmations_count=3)
        assert d.paper_only is True
        assert d.live_allowed is False
        assert len(d.blocked_reasons) > 0

    def test_gate_all_acks_but_not_approved_state_no_live(self):
        g = PaperLiveGate(paper_only=True, seed=7)
        d = g.evaluate(state={"equity": 200000, "total_notional": 100000, "drawdown_pct": 0.02,
                             "capital_ack": True, "risk_ack": True, "manual_approval": True,
                             "connectivity_ok": True, "compliance_ok": True},
                      intents_count=10, confirmations_count=5)
        assert d.live_allowed is False

    def test_gate_grant_approval_with_all_acks_enables_live_path_logic(self):
        g = PaperLiveGate(paper_only=True, seed=9)
        g.grant_approval()
        d = g.evaluate(state={"equity": 200000, "total_notional": 100000, "drawdown_pct": 0.02,
                             "capital_ack": True, "risk_ack": True, "manual_approval": True,
                             "connectivity_ok": True, "compliance_ok": True},
                      intents_count=10, confirmations_count=5)
        assert d.approval_state == "APPROVED"
        assert d.paper_only is True

    def test_gate_min_equity_blocks(self):
        g = PaperLiveGate(paper_only=True, seed=11, min_equity=200000)
        d = g.evaluate(state={"equity": 150000, "total_notional": 50000, "drawdown_pct": 0.01,
                             "capital_ack": True, "risk_ack": True, "manual_approval": True,
                             "connectivity_ok": True, "compliance_ok": True}, intents_count=1, confirmations_count=1)
        assert "min_equity" in d.blocked_reasons

    def test_gate_drawdown_blocks(self):
        g = PaperLiveGate(paper_only=True, seed=13, max_drawdown_pct=0.05)
        d = g.evaluate(state={"equity": 150000, "total_notional": 50000, "drawdown_pct": 0.10,
                             "capital_ack": True, "risk_ack": True, "manual_approval": True,
                             "connectivity_ok": True, "compliance_ok": True}, intents_count=1, confirmations_count=1)
        assert "max_drawdown" in d.blocked_reasons

    def test_gate_report_serializable(self):
        g = PaperLiveGate(paper_only=True, seed=17)
        d = g.evaluate(state={"equity": 150000, "total_notional": 50000, "drawdown_pct": 0.01}, intents_count=2, confirmations_count=1)
        rep = g.generate_report(d)
        assert rep["report"] == "PHASE19_PAPER_LIVE_GATE_REPORT"
        assert rep["paper_only"] is True


class TestPhase19OrderManager:
    def test_oms_paper_only(self):
        oms = OrderManager(paper_only=True, seed=5)
        assert oms.paper_only is True

    def test_oms_rejects_live(self):
        with pytest.raises(ValueError):
            OrderManager(paper_only=False, seed=1)

    def test_create_order_idempotent(self):
        oms = OrderManager(paper_only=True, seed=23)
        intent = {"intent_id": "i1", "symbol": "BTC", "side": "buy", "qty": 0.01}
        o1 = oms.create_order(intent)
        o2 = oms.create_order(intent)
        assert o1.order_id == o2.order_id

    def test_order_lifecycle_new_submit_ack(self):
        oms = OrderManager(paper_only=True, seed=29)
        intent = {"intent_id": "i2", "symbol": "ETH", "side": "sell", "qty": 0.1}
        o = oms.create_order(intent)
        assert o.status == OrderState.NEW
        o2 = oms.submit(o.order_id)
        assert o2.status in (OrderState.SUBMITTED, OrderState.ACKED)

    def test_partial_and_full_fill(self):
        oms = OrderManager(paper_only=True, seed=31)
        intent = {"intent_id": "i3", "symbol": "SOL", "side": "buy", "qty": 1.0}
        o = oms.create_order(intent)
        oms.submit(o.order_id)
        o2 = oms.simulate_fill(o.order_id, fill_qty=0.3)
        assert o2.status == OrderState.PARTIALLY_FILLED
        o3 = oms.simulate_fill(o.order_id, fill_qty=0.7)
        assert o3.status == OrderState.FILLED
        assert o3.filled_qty >= 0.99

    def test_cancel_order(self):
        oms = OrderManager(paper_only=True, seed=37)
        intent = {"intent_id": "i4", "symbol": "BTC", "side": "buy", "qty": 0.05}
        o = oms.create_order(intent)
        oms.submit(o.order_id)
        o2 = oms.cancel(o.order_id)
        assert o2.status == OrderState.CANCELLED

    def test_reject_order(self):
        oms = OrderManager(paper_only=True, seed=41)
        intent = {"intent_id": "i5", "symbol": "XRP", "side": "sell", "qty": 10}
        o = oms.create_order(intent)
        o2 = oms.reject(o.order_id, reason="risk")
        assert o2.status == OrderState.REJECTED
        assert o2.reject_reason == "risk"

    def test_reconcile(self):
        oms = OrderManager(paper_only=True, seed=43)
        for i in range(5):
            intent = {"intent_id": f"ir{i}", "symbol": "BTC", "side": "buy", "qty": 0.01}
            o = oms.create_order(intent)
            oms.submit(o.order_id)
            oms.simulate_fill(o.order_id)
        rec = oms.reconcile()
        assert rec["reconciled"] is True
        assert rec["total_orders"] == 5
        assert rec["filled"] == 5

    def test_report_serializable(self):
        oms = OrderManager(paper_only=True, seed=47)
        intent = {"intent_id": "irx", "symbol": "ETH", "side": "buy", "qty": 0.01}
        o = oms.create_order(intent)
        oms.submit(o.order_id)
        oms.simulate_fill(o.order_id)
        rep = oms.generate_report()
        assert rep["report"] == "PHASE19_ORDER_MANAGEMENT_REPORT"
        assert rep["paper_only"] is True


class TestPhase19ExecutionRisk:
    def test_risk_paper_only(self):
        r = ExecutionRiskEngine(paper_only=True, seed=3)
        assert r.paper_only is True

    def test_risk_rejects_live(self):
        with pytest.raises(ValueError):
            ExecutionRiskEngine(paper_only=False, seed=1)

    def test_pre_trade_approve_small(self):
        r = ExecutionRiskEngine(paper_only=True, seed=53)
        intent = {"intent_id": "x1", "symbol": "BTC", "side": "buy", "qty": 0.01, "limit_price": 65000,
                  "delta_est": 10, "vega_est": 100, "gamma_est": 1, "theta_est": -100}
        res = r.pre_trade_check(intent, state={"total_notional": 10000}, venue="deribit")
        assert res["approved"] is True
        assert res["kill_switch"] is False

    def test_pre_trade_reject_notional_per_symbol(self):
        r = ExecutionRiskEngine(paper_only=True, seed=59, max_notional_per_symbol=5000)
        intent = {"intent_id": "x2", "symbol": "BTC", "side": "buy", "qty": 0.2, "limit_price": 65000}
        res = r.pre_trade_check(intent, state={"total_notional": 10000}, venue="deribit")
        assert res["approved"] is False

    def test_pre_trade_reject_delta_cap(self):
        r = ExecutionRiskEngine(paper_only=True, seed=61, max_delta=50)
        intent = {"intent_id": "x3", "symbol": "ETH", "side": "buy", "qty": 0.01, "limit_price": 3400,
                  "delta_est": 100}
        res = r.pre_trade_check(intent, state={"total_notional": 10000}, venue="okx")
        assert res["approved"] is False

    def test_pre_trade_reject_vega_cap(self):
        r = ExecutionRiskEngine(paper_only=True, seed=67, max_vega=1000)
        intent = {"intent_id": "x4", "symbol": "SOL", "side": "buy", "qty": 0.01, "limit_price": 150,
                  "vega_est": 5000}
        res = r.pre_trade_check(intent, state={"total_notional": 10000}, venue="binance")
        assert res["approved"] is False

    def test_pre_trade_reject_drawdown_kill(self):
        r = ExecutionRiskEngine(paper_only=True, seed=71, max_drawdown_pct=0.05)
        intent = {"intent_id": "x5", "symbol": "BTC", "side": "buy", "qty": 0.01, "limit_price": 65000}
        res = r.pre_trade_check(intent, state={"total_notional": 10000, "drawdown_pct": 0.10}, venue="deribit")
        assert res["approved"] is False
        assert r.kill_switch is True

    def test_post_trade_slippage_ok(self):
        r = ExecutionRiskEngine(paper_only=True, seed=73)
        res = r.post_trade_validate({"order_id": "o1", "filled_qty": 0.01, "fill_price": 100.0, "expected_price": 100.1})
        assert res["ok"] is True

    def test_post_trade_slippage_breach(self):
        r = ExecutionRiskEngine(paper_only=True, seed=79, max_slippage_bps=5)
        res = r.post_trade_validate({"order_id": "o2", "filled_qty": 0.01, "fill_price": 101.0, "expected_price": 100.0})
        assert res["ok"] is False

    def test_kill_switch_trigger(self):
        r = ExecutionRiskEngine(paper_only=True, seed=83)
        r.trigger_kill_switch("test")
        assert r.kill_switch is True

    def test_report_serializable(self):
        r = ExecutionRiskEngine(paper_only=True, seed=89)
        intent = {"intent_id": "xr", "symbol": "BTC", "side": "buy", "qty": 0.01, "limit_price": 65000,
                  "delta_est": 5, "vega_est": 50}
        r.pre_trade_check(intent, state={"total_notional": 1000}, venue="deribit")
        rep = r.generate_report()
        assert rep["report"] == "PHASE19_EXECUTION_RISK_REPORT"
        assert rep["paper_only"] is True


class TestPhase19Integration:
    def test_phase19_campaign_run_produces_artifacts(self, tmp_path):
        outdir = tmp_path / "out"
        outdir.mkdir(parents=True, exist_ok=True)
        res = subprocess.run(
            [sys.executable, "scripts/run_phase19_execution_hardening_campaign.py",
             "--symbols", "BTC", "ETH", "--seed", "123", "--outdir", str(outdir), "--cycles", "2"],
            cwd=str(Path(__file__).resolve().parents[1]),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert res.returncode == 0, res.stderr.decode()

        required = [
            outdir / "PHASE19_PAPER_LIVE_GATE_REPORT.json",
            outdir / "PHASE19_PAPER_LIVE_GATE_REPORT.md",
            outdir / "PHASE19_ORDER_MANAGEMENT_REPORT.json",
            outdir / "PHASE19_ORDER_MANAGEMENT_REPORT.md",
            outdir / "PHASE19_EXECUTION_RISK_REPORT.json",
            outdir / "PHASE19_EXECUTION_RISK_REPORT.md",
            outdir / "PHASE19_EXECUTION_HARDENING_MASTER_REPORT.json",
            outdir / "PHASE19_EXECUTION_HARDENING_MASTER_REPORT.md",
        ]
        for r in required:
            assert r.exists(), f"missing {r}"

        for r in required:
            if r.suffix == ".json":
                data = json.loads(r.read_text())
                assert isinstance(data, dict)

    def test_determinism_phase19_artifacts(self, tmp_path):
        out1 = tmp_path / "o1"
        out2 = tmp_path / "o2"
        out1.mkdir(parents=True, exist_ok=True)
        out2.mkdir(parents=True, exist_ok=True)
        repo = str(Path(__file__).resolve().parents[1])
        for out in [out1, out2]:
            res = subprocess.run(
                [sys.executable, "scripts/run_phase19_execution_hardening_campaign.py",
                 "--symbols", "BTC", "--seed", "777", "--outdir", str(out), "--cycles", "1"],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert res.returncode == 0, res.stderr.decode()

        for name in ["PHASE19_PAPER_LIVE_GATE_REPORT.json", "PHASE19_ORDER_MANAGEMENT_REPORT.json", "PHASE19_EXECUTION_RISK_REPORT.json"]:
            d1 = json.loads((out1 / name).read_text())
            d2 = json.loads((out2 / name).read_text())
            assert d1.get("seed") == d2.get("seed")
            assert d1.get("campaign") == d2.get("campaign")
            assert d1.get("paper_only") == d2.get("paper_only")
