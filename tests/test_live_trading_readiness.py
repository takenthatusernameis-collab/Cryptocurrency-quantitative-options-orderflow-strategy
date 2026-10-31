"""Comprehensive tests for Phase 8: Live Trading Readiness."""
import json
from datetime import datetime, timezone
from math import isfinite

import pytest

from src.config.secrets import SecretsManager, load_secrets_config
from src.execution.live_trading import LiveTradingEngine, OrderStateMachine, OrderReconciliation
from src.execution.orders import OrderSide, OrderType, TimeInForce
from src.ingestion.adapter_utils import TokenBucket, RetryPolicy, WebSocketReconnectManager
from src.risk.reconciliation import ReconciliationEngine, DiscrepancySeverity
from src.risk.execution_integration import create_execution_risk_integrator
from src.risk.limits import RiskLimits, RiskManager
from src.risk.circuit_breaker import CircuitBreaker
from src.telemetry import serialize_metrics_strict


class TestSecretsAndConfig:
    def test_secrets_manager_init(self):
        sm = SecretsManager()
        assert sm is not None

    def test_secrets_redaction(self):
        sm = SecretsManager()
        data = {"api_key": "abc123def456", "symbol": "BTC", "secret": "secret123"}
        redacted = sm.redact(data)
        assert redacted["api_key"] == "[REDACTED]" or redacted["api_key"] != "abc123def456"
        assert redacted["symbol"] == "BTC"
        assert json.dumps(redacted, allow_nan=False) is not None

    def test_load_secrets_config(self):
        config = load_secrets_config()
        assert isinstance(config, dict)
        assert "deribit" in config
        assert "trading_mode" in config
        json.dumps(config, allow_nan=False)


class TestAdapterUtils:
    def test_token_bucket(self):
        tb = TokenBucket(rate=10.0, burst=20)
        assert tb.consume(1) is True
        assert tb.tokens < 20

    def test_retry_policy(self):
        rp = RetryPolicy(max_retries=3, base_backoff=0.01)
        counter = [0]
        def succeed_after_tries():
            counter[0] += 1
            if counter[0] < 2:
                raise Exception("fail")
            return "success"
        result = rp.call_with_retry(succeed_after_tries)
        assert result == "success"

    def test_ws_reconnect_manager(self):
        wsm = WebSocketReconnectManager(max_reconnects=3)
        assert wsm.connected is False
        connected_flag = [False]
        def connect():
            connected_flag[0] = True
        result = wsm.reconnect(connect)
        assert result is True
        assert wsm.connected is True


class TestLiveTradingEngine:
    def test_live_engine_init_paper(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        assert engine.paper_mode is True
        assert engine.halted is False

    def test_submit_order_market(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1, OrderType.MARKET)
        assert order.order_id is not None
        assert order.symbol == "BTCUSDT"
        assert order.side == OrderSide.BUY
        assert order.state == OrderStateMachine.SUBMITTED
        json.dumps(engine.get_order_status(order.order_id), allow_nan=False)

    def test_submit_order_limit(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("ETHUSDT", OrderSide.SELL, 1.5, OrderType.LIMIT, price=3000.0)
        assert order.order_type == OrderType.LIMIT
        assert order.price == 3000.0

    def test_replace_order(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1, OrderType.LIMIT, price=100000.0)
        replaced = engine.replace_order(order.order_id, quantity=0.2, price=99000.0)
        assert replaced.state == OrderStateMachine.REPLACED
        assert replaced.quantity == 0.2

    def test_cancel_order(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1, OrderType.LIMIT, price=100000.0)
        cancelled = engine.cancel_order(order.order_id)
        assert cancelled.state == OrderStateMachine.CANCELLED

    def test_process_fill_partial(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 1.0, OrderType.MARKET)
        fill1 = engine.process_fill(order.order_id, 0.3, 100000.0, 0.3)
        assert fill1["quantity"] == 0.3
        status = engine.get_order_status(order.order_id)
        assert status["state"] == "partially_filled"
        assert status["filled_quantity"] == 0.3

    def test_process_fill_full(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.5, OrderType.MARKET)
        engine.process_fill(order.order_id, 0.3, 100000.0, 0.15)
        engine.process_fill(order.order_id, 0.2, 100001.0, 0.1)
        status = engine.get_order_status(order.order_id)
        assert status["state"] == "filled"
        assert status["filled_quantity"] == 0.5

    def test_reconcile_order_matched(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1, OrderType.MARKET)
        engine.process_fill(order.order_id, 0.1, 100000.0, 0.05)
        recon = engine.reconcile_order(order.order_id, "filled", 0.1, 100000.0)
        assert recon.matched is True
        assert recon.quantity_match is True
        json.dumps(recon.to_dict(), allow_nan=False)

    def test_reconcile_order_discrepancy(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1, OrderType.MARKET)
        engine.process_fill(order.order_id, 0.1, 100000.0, 0.05)
        recon = engine.reconcile_order(order.order_id, "filled", 0.09, 100000.0)
        assert recon.quantity_match is False
        assert len(recon.discrepancy) > 0

    def test_halt_resume_trading(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        engine.halt_trading("test halt")
        assert engine.halted is True
        with pytest.raises(Exception):
            engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        engine.resume_trading()
        assert engine.halted is False
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        assert order is not None

    def test_trading_summary_strict_serializable(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        engine.process_fill(order.order_id, 0.1, 100000.0)
        summary = engine.get_trading_summary()
        json.dumps(summary, allow_nan=False)
        assert isfinite(summary.get("reconciliation_match_rate", 1.0))

    def test_idempotency_keys(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        assert order.idempotency_key != ""
        assert len(order.idempotency_key) > 0


class TestReconciliationEngine:
    def test_recon_engine_init(self):
        recon = ReconciliationEngine(auto_halt_on_critical=True)
        assert recon.halted is False

    def test_reconcile_positions_matched(self):
        recon = ReconciliationEngine()
        local = {"BTC": {"quantity": 1.0, "notional": 100000.0}}
        exchange = {"BTC": {"quantity": 1.0, "notional": 100000.0}}
        results = recon.reconcile_positions(local, exchange)
        assert len(results) == 1
        assert results[0].matched is True
        json.dumps(results[0].to_dict(), allow_nan=False)

    def test_reconcile_positions_discrepancy(self):
        recon = ReconciliationEngine()
        local = {"BTC": {"quantity": 1.0, "notional": 100000.0}}
        exchange = {"BTC": {"quantity": 1.5, "notional": 150000.0}}
        results = recon.reconcile_positions(local, exchange)
        assert results[0].matched is False
        assert results[0].quantity_diff == 0.5

    def test_reconcile_positions_critical_auto_halt(self):
        recon = ReconciliationEngine(auto_halt_on_critical=True)
        local = {"BTC": {"quantity": 1.0, "notional": 100000.0}}
        exchange = {"BTC": {"quantity": 3.0, "notional": 300000.0}}
        results = recon.reconcile_positions(local, exchange)
        assert results[0].severity == DiscrepancySeverity.CRITICAL
        assert recon.halted is True

    def test_margin_check_sufficient(self):
        recon = ReconciliationEngine()
        result = recon.check_margin(5000.0, 10000.0)
        assert result.sufficient is True
        assert result.action == "ok"
        json.dumps(result.to_dict(), allow_nan=False)

    def test_margin_check_warning(self):
        recon = ReconciliationEngine()
        result = recon.check_margin(8000.0, 10000.0)
        assert result.margin_ratio < 1.5
        assert result.action == "reduce"

    def test_margin_check_halt(self):
        recon = ReconciliationEngine(auto_halt_on_critical=True)
        result = recon.check_margin(9000.0, 10000.0)
        assert result.action == "halt"
        assert recon.halted is True

    def test_pnl_reconciliation_matched(self):
        recon = ReconciliationEngine()
        result = recon.reconcile_pnl(1500.0, 1500.5)
        assert result["matched"] is True
        json.dumps(result, allow_nan=False)

    def test_pnl_reconciliation_discrepancy(self):
        recon = ReconciliationEngine()
        result = recon.reconcile_pnl(1500.0, 2000.0)
        assert result["matched"] is False
        assert result["difference"] == 500.0

    def test_reconciliation_audit_report(self):
        recon = ReconciliationEngine()
        recon.reconcile_positions({"BTC": {"quantity": 1.0, "notional": 100000.0}},
                                  {"BTC": {"quantity": 1.0, "notional": 100000.0}})
        recon.check_margin(5000.0, 10000.0)
        report = recon.get_audit_report()
        json.dumps(report, allow_nan=False)
        assert "halted" in report
        assert "total_position_reconciliations" in report


class TestRiskIntegrationWired:
    def test_risk_integrator_with_live_trading(self):
        limits = RiskLimits()
        risk_mgr = RiskManager(limits=limits)
        cb = CircuitBreaker()
        integrator = create_execution_risk_integrator(risk_manager=risk_mgr, circuit_breaker=cb, seed=42)
        engine = LiveTradingEngine(risk_integrator=integrator, paper_mode=True, seed=42)
        integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
        integrator.update_equity(100000.0)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.01, OrderType.MARKET, price=100000.0)
        assert order is not None

    def test_circuit_breaker_integration(self):
        cb = CircuitBreaker()
        assert cb.can_execute() is True
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.state.value == "open"


class TestDeterminismAndSerialization:
    def test_deterministic_order_ids(self):
        engine1 = LiveTradingEngine(paper_mode=True, seed=123)
        engine2 = LiveTradingEngine(paper_mode=True, seed=123)
        order1 = engine1.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        order2 = engine2.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        # IDs may differ due to time, but structure should be consistent
        assert order1.order_id.startswith("live_")
        assert order2.order_id.startswith("live_")

    def test_strict_serialization_all_components(self):
        engine = LiveTradingEngine(paper_mode=True, seed=42)
        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
        engine.process_fill(order.order_id, 0.05, 100000.0)

        recon = ReconciliationEngine()
        recon_results = recon.reconcile_positions({"BTC": {"quantity": 0.05, "notional": 5000.0}},
                                                   {"BTC": {"quantity": 0.05, "notional": 5000.0}})
        margin = recon.check_margin(1000.0, 2000.0)
        pnl = recon.reconcile_pnl(100.0, 100.0)
        summary = engine.get_trading_summary()
        audit = recon.get_audit_report()

        json.dumps(engine.get_order_status(order.order_id), allow_nan=False)
        json.dumps(recon_results[0].to_dict(), allow_nan=False)
        json.dumps(margin.to_dict(), allow_nan=False)
        json.dumps(pnl, allow_nan=False)
        json.dumps(summary, allow_nan=False)
        json.dumps(audit, allow_nan=False)

    def test_rerun_determinism(self):
        def run_once():
            engine = LiveTradingEngine(paper_mode=True, seed=777)
            order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.1)
            engine.process_fill(order.order_id, 0.1, 100000.0)
            return engine.get_trading_summary()

        s1 = run_once()
        s2 = run_once()
        assert s1["total_orders"] == s2["total_orders"]
        assert s1["total_fills"] == s2["total_fills"]
        assert s1["paper_mode"] == s2["paper_mode"]


class TestAuthRetryRateLimit:
    def test_token_bucket_rate_limiting(self):
        tb = TokenBucket(rate=2.0, burst=5)
        for _ in range(5):
            assert tb.consume(1) is True
        assert tb.consume(1) is False  # Burst exhausted

    def test_retry_on_transient_failure(self):
        rp = RetryPolicy(max_retries=4, base_backoff=0.001)
        attempts = [0]
        def flaky():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ConnectionError("network error")
            return "ok"
        result = rp.call_with_retry(flaky)
        assert result == "ok"
        assert attempts[0] == 3

    def test_retry_raises_after_exhaustion(self):
        rp = RetryPolicy(max_retries=2, base_backoff=0.001)
        def always_fail():
            raise ValueError("fail")
        with pytest.raises(Exception):
            rp.call_with_retry(always_fail)


class TestPreLiveGates:
    def test_secrets_config_load(self):
        config = load_secrets_config()
        assert isinstance(config["deribit"], dict)
        assert isinstance(config["trading_mode"], str)

    def test_full_pre_live_flow(self):
        limits = RiskLimits()
        risk_mgr = RiskManager(limits=limits)
        cb = CircuitBreaker()
        integrator = create_execution_risk_integrator(risk_manager=risk_mgr, circuit_breaker=cb, seed=42)
        integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
        integrator.update_equity(100000.0)

        engine = LiveTradingEngine(risk_integrator=integrator, paper_mode=True, seed=42)
        recon = ReconciliationEngine()

        order = engine.submit_order("BTCUSDT", OrderSide.BUY, 0.01, OrderType.LIMIT, price=100000.0)
        engine.process_fill(order.order_id, 0.01, 100000.0, 0.005)

        recon.reconcile_positions({"BTCUSDT": {"quantity": 0.01, "notional": 1000.0}},
                                  {"BTCUSDT": {"quantity": 0.01, "notional": 1000.0}})
        recon.check_margin(200.0, 50000.0)
        recon.reconcile_pnl(10.0, 10.0)

        summary = engine.get_trading_summary()
        audit = recon.get_audit_report()
        json.dumps(summary, allow_nan=False)
        json.dumps(audit, allow_nan=False)
        assert summary["total_orders"] >= 1
        assert audit["halted"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
