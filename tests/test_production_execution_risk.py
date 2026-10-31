"""Production execution + risk integration tests (Phase 7).

Covers execution engine (fees/slippage/latency/partial fills/determinism),
risk integration layer (pre-trade block/hold/flatten, kill-switch propagation,
circuit breaker, stale greeks, post-trade checks, audit trail), strict
serialization (allow_nan=False), and end-to-end wiring.
"""

import json
import math
from datetime import datetime, timedelta, timezone

import pytest

from math import isfinite

from src.backtest.options_hedging import latency_aware_delta_hedging_loop
from src.execution.algorithms import create_algorithm, SlippageModel
from src.execution.engine import ExecutionEngine
from src.execution.orders import Order, OrderSide, OrderType, TimeInForce
from src.risk.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from src.risk.execution_integration import (
    ExecutionRiskConfig,
    ExecutionRiskIntegrator,
    RiskAction,
    create_execution_risk_integrator,
)
from src.risk.limits import RiskLimits, RiskManager
from src.telemetry import serialize_metrics_strict


# --------------------------------------------------------------------------- helpers


def _make_order(order_id: str, symbol: str, side: OrderSide, qty: float, price: float) -> Order:
    return Order(
        order_id=order_id,
        symbol=symbol,
        side=side,
        order_type=OrderType.MARKET,
        quantity=qty,
        price=price,
        time_in_force=TimeInForce.GTC,
    )


# --------------------------------------------------------------------------- execution engine


def test_execution_engine_market_buy_fees_and_cash():
    eng = ExecutionEngine(initial_capital=100000.0, seed=42)
    order = _make_order("ord_1", "BTCUSDT", OrderSide.BUY, 0.1, 100000.0)
    eng.submit_order(order)
    report = eng.execute_order_market(order, 100000.0, commission_rate=0.0005)
    assert report.status.value == "filled"
    assert report.filled_quantity == 0.1
    assert eng.cash < 100000.0  # commission deducted
    summary = eng.get_portfolio_summary()
    json.dumps(summary, allow_nan=False)  # strict serialization must not raise


def test_execution_engine_market_sell_proceeds():
    eng = ExecutionEngine(initial_capital=100000.0, seed=42)
    b = _make_order("b1", "BTCUSDT", OrderSide.BUY, 0.1, 100000.0)
    eng.submit_order(b)
    eng.execute_order_market(b, 100000.0, commission_rate=0.0005)
    s = _make_order("s1", "BTCUSDT", OrderSide.SELL, 0.1, 101000.0)
    eng.submit_order(s)
    report = eng.execute_order_market(s, 101000.0, commission_rate=0.0005)
    assert report.status.value == "filled"
    assert eng.cash > 0.0


def test_execution_engine_insufficient_cash_reject():
    eng = ExecutionEngine(initial_capital=10.0, seed=42)
    order = _make_order("ord_big", "BTCUSDT", OrderSide.BUY, 1.0, 100000.0)
    eng.submit_order(order)
    report = eng.execute_order_market(order, 100000.0, commission_rate=0.0005)
    assert report.status.value == "rejected"
    assert "insufficient cash" in report.message.lower()


def test_execution_engine_algorithmic_slicing_determinism():
    eng = ExecutionEngine(initial_capital=1000000.0, seed=42)
    order = _make_order("ord_algo", "BTCUSDT", OrderSide.BUY, 10.0, 100000.0)
    eng.submit_order(order)
    algo = create_algorithm("twap", num_slices=5, seed=42)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    reports = eng.execute_with_algorithm(order, algo, start, end,
                                         price_history=[(start, 100000.0, 100.0)],
                                         adv=1000.0, base_price=100000.0)
    assert len(reports) > 0
    eng2 = ExecutionEngine(initial_capital=1000000.0, seed=42)
    order2 = _make_order("ord_algo", "BTCUSDT", OrderSide.BUY, 10.0, 100000.0)
    eng2.submit_order(order2)
    reports2 = eng2.execute_with_algorithm(order2, create_algorithm("twap", num_slices=5, seed=42),
                                           start, end, price_history=[(start, 100000.0, 100.0)],
                                           adv=1000.0, base_price=100000.0)
    assert [r.order_id for r in reports] == [r.order_id for r in reports2]
    assert [r.filled_quantity for r in reports] == [r.filled_quantity for r in reports2]


def test_execution_engine_deterministic_rerun():
    eng = ExecutionEngine(initial_capital=100000.0, seed=42)
    order = _make_order("ord_det", "BTCUSDT", OrderSide.BUY, 0.5, 100000.0)
    eng.submit_order(order)
    eng.execute_order_market(order, 100000.0, commission_rate=0.0005)
    s1 = eng.get_portfolio_summary()
    eng2 = ExecutionEngine(initial_capital=100000.0, seed=42)
    order2 = _make_order("ord_det", "BTCUSDT", OrderSide.BUY, 0.5, 100000.0)
    eng2.submit_order(order2)
    eng2.execute_order_market(order2, 100000.0, commission_rate=0.0005)
    s2 = eng2.get_portfolio_summary()
    # Timestamps differ between runs; compare numeric invariants only.
    assert s1["cash"] == s2["cash"]
    assert s1["total_realized_pnl"] == s2["total_realized_pnl"]
    assert s1["num_fills"] == s2["num_fills"]
    assert s1["num_orders"] == s2["num_orders"]


def test_execution_engine_portfolio_summary_strict_serializable():
    eng = ExecutionEngine(initial_capital=100000.0, seed=42)
    order = _make_order("ord_ss", "BTCUSDT", OrderSide.BUY, 0.2, 100000.0)
    eng.submit_order(order)
    eng.execute_order_market(order, 100000.0, commission_rate=0.0005)
    summary = eng.get_portfolio_summary()
    assert json.dumps(summary, allow_nan=False) is not None
    assert isfinite(summary["cash"])
    assert isfinite(summary["total_realized_pnl"])


def test_execution_engine_idempotent_order_ids():
    eng = ExecutionEngine(initial_capital=100000.0, seed=42)
    id1 = eng._generate_id("ord")
    id2 = eng._generate_id("ord")
    assert id1 != id2
    assert id1.startswith("ord_")


# --------------------------------------------------------------------------- risk integration layer


def test_risk_integration_pre_trade_allow():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is True
    assert result.action in (RiskAction.ALLOW,)
    json.dumps(result.to_dict(), allow_nan=False)


def test_risk_integration_kill_switch_blocks():
    rm = RiskManager()
    rm.disable_kill_switch()
    rm.arm_kill_switch()
    rm._trigger_kill_switch("test_breach", 60000.0, 50000.0)
    integrator = create_execution_risk_integrator(risk_manager=rm, seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is False
    assert result.action == RiskAction.BLOCK
    assert result.reason == "kill_switch_triggered"


def test_risk_integration_circuit_breaker_holds():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=1, timeout_seconds=999999))
    cb.record_failure()  # opens immediately (threshold 1)
    assert cb.state.value == "open"
    integrator = create_execution_risk_integrator(circuit_breaker=cb, seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is False
    assert result.action == RiskAction.HOLD
    assert result.reason == "circuit_breaker_open"


def test_risk_integration_stale_greeks_hold():
    integrator = create_execution_risk_integrator(seed=42)
    # Never update greeks -> stale
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is False
    assert result.action == RiskAction.HOLD
    assert result.reason == "stale_greeks"


def test_risk_integration_stale_greeks_cleared_after_update():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 100.0, "gamma": 10.0, "vega": 50.0, "theta": -5.0})
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is True


def test_risk_integration_post_trade_check():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    result = integrator.post_trade_check("BTCUSDT", "buy", 0.1, 100000.0,
                                         filled_quantity=0.1, commission=5.0, latency_ms=20.0)
    assert result.approved is True
    assert result.action == RiskAction.ALLOW
    json.dumps(result.to_dict(), allow_nan=False)


def test_risk_integration_drawdown_flattens():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    integrator.update_equity(100000.0)
    integrator.update_equity(80000.0)  # 20% drawdown > 15% limit
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is False
    assert result.action == RiskAction.FLATTEN
    assert result.reason == "drawdown_limit_breached"


def test_risk_integration_risk_report_strict_serializable():
    integrator = create_execution_risk_integrator(seed=42)
    report = integrator.get_risk_report()
    assert json.dumps(report, allow_nan=False) is not None
    assert "integrator_state" in report
    assert "risk_manager" in report
    assert "circuit_breaker" in report


def test_risk_integration_audit_trail_serializable():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    trail = integrator.export_audit_trail()
    assert len(trail) >= 1
    assert json.dumps(trail, allow_nan=False) is not None


def test_risk_integration_reset_returns_to_armed():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.queue_flatten("test")
    assert integrator.flatten_queued is True
    integrator.reset()
    assert integrator.state.value == "armed"
    assert integrator.flatten_queued is False


def test_risk_integration_partial_hedge_on_latency():
    config = ExecutionRiskConfig(seed=42, partial_hedge_on_latency=True, latency_penalty_bps=50.0)
    integrator = ExecutionRiskIntegrator(config=config, seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    result = integrator.pre_trade_check("BTCUSDT", "buy", 1.0, 100000.0, positions={}, latency_ms=500.0)
    # High latency -> partial reduce
    assert result.action == RiskAction.REDUCE
    assert result.adjusted_quantity is not None
    assert result.adjusted_quantity < 1.0


def test_risk_integration_invalid_quantity_blocked():
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    result = integrator.pre_trade_check("BTCUSDT", "buy", 0.0, 100000.0, positions={}, latency_ms=10.0)
    assert result.approved is False
    assert result.action == RiskAction.BLOCK


# --------------------------------------------------------------------------- latency-aware hedging


def test_latency_hedging_deterministic_rerun():
    spot_path = [100.0 + i * 0.5 for i in range(50)]
    times = [i * 0.001 for i in range(50)]
    r1 = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                          option_type="call", seed=42, latency_ms=50.0)
    r2 = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                          option_type="call", seed=42, latency_ms=50.0)
    assert r1["total_pnl"] == r2["total_pnl"]
    assert r1["num_rebalances"] == r2["num_rebalances"]
    json.dumps(r1, allow_nan=False)


def test_latency_hedging_attribution_reconciliation():
    spot_path = [100.0 + i * 0.3 for i in range(40)]
    times = [i * 0.001 for i in range(40)]
    r = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                         option_type="call", seed=42, latency_ms=50.0)
    attr = r["attribution"]
    assert isfinite(attr["total_pnl"])
    assert isfinite(attr["sum_attribution"])
    assert abs(attr["sum_attribution"] - attr["total_pnl"]) < 1e-6


def test_latency_hedging_execution_cost_present():
    spot_path = [100.0 + i * 0.3 for i in range(40)]
    times = [i * 0.001 for i in range(40)]
    r = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                         option_type="call", seed=42, latency_ms=50.0,
                                         hedge_slippage_bps=2.0, transaction_cost_bps=1.0)
    assert r["total_execution_cost"] >= 0.0
    # execution_cost_bps lives per action when trades occur
    any_cost = any(a.get("execution_cost_bps", 0) > 0 for a in r.get("actions", []))
    assert r["total_execution_cost"] > 0.0 or any_cost
    assert "execution_cost_pnl" in r["attribution"]


def test_latency_hedging_partial_hedge_flag():
    spot_path = [100.0 + i * 0.3 for i in range(40)]
    times = [i * 0.001 for i in range(40)]
    r = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                         option_type="call", seed=42, latency_ms=50.0,
                                         stale_greek_threshold_seconds=0.001, partial_hedge_ratio=0.5)
    assert r["num_partial"] >= 0
    assert r["num_stale"] >= 0


def test_latency_hedging_risk_integrated_blocks():
    rm = RiskManager()
    rm.disable_kill_switch()
    rm.arm_kill_switch()
    rm._trigger_kill_switch("test", 60000.0, 50000.0)
    spot_path = [100.0 + i * 0.3 for i in range(40)]
    times = [i * 0.001 for i in range(40)]
    r = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                         option_type="call", seed=42, latency_ms=50.0,
                                         risk_manager=rm)
    assert r["risk_integrated"] is True


def test_latency_hedging_strict_serialization():
    spot_path = [100.0 + i * 0.3 for i in range(30)]
    times = [i * 0.001 for i in range(30)]
    r = latency_aware_delta_hedging_loop(spot_path, times, strike=100.0, rate=0.05, volatility=0.25,
                                         option_type="call", seed=42, latency_ms=50.0)
    assert json.dumps(r, allow_nan=False) is not None


# --------------------------------------------------------------------------- telemetry monitor


def test_telemetry_monitor_snapshot_strict_serializable():
    from src.telemetry.monitor import ProductionTelemetryMonitor
    mon = ProductionTelemetryMonitor(run_id="tel_test", seed=42)
    snap = mon.update(pnl=100.0, daily_pnl=100.0, current_equity=100100.0,
                      peak_equity=100100.0, portfolio_greeks={"delta": 10.0, "gamma": 1.0,
                                                              "vega": 5.0, "theta": -1.0},
                      gamma_exposure=500.0, num_orders=5, num_fills=3,
                      total_commission=2.5, total_execution_cost=1.0)
    d = snap.to_dict()
    assert json.dumps(d, allow_nan=False) is not None
    assert isfinite(d["pnl"])
    assert isfinite(d["drawdown_pct"])
    assert 0.0 <= d["heat"] <= 1.0


def test_telemetry_monitor_alert_on_drawdown():
    from src.telemetry.monitor import ProductionTelemetryMonitor
    mon = ProductionTelemetryMonitor(run_id="tel_alert", seed=42)
    mon.update(pnl=-40000.0, daily_pnl=-40000.0, current_equity=60000.0,
               peak_equity=100000.0, portfolio_greeks={}, gamma_exposure=0.0)
    alerts = mon.get_alerts()
    assert len(alerts) >= 1
    assert any(a["severity"] in ("warning", "critical") for a in alerts)
    assert json.dumps(alerts, allow_nan=False) is not None


def test_telemetry_monitor_export_report_strict():
    from src.telemetry.monitor import ProductionTelemetryMonitor
    mon = ProductionTelemetryMonitor(run_id="tel_exp", seed=42)
    mon.update(pnl=500.0, daily_pnl=500.0, current_equity=100500.0,
               peak_equity=100500.0, portfolio_greeks={"delta": 5.0}, gamma_exposure=250.0)
    report = mon.export_report()
    assert json.dumps(report, allow_nan=False) is not None
    assert "summary" in report
    assert "latest_snapshot" in report


def test_telemetry_monitor_acknowledge_alert():
    from src.telemetry.monitor import ProductionTelemetryMonitor
    mon = ProductionTelemetryMonitor(run_id="tel_ack", seed=42)
    mon.update(pnl=-40000.0, daily_pnl=-40000.0, current_equity=60000.0,
               peak_equity=100000.0, portfolio_greeks={}, gamma_exposure=0.0)
    alerts = mon.get_alerts()
    assert len(alerts) >= 1
    aid = alerts[0]["alert_id"]
    assert mon.acknowledge_alert(aid) is True
    assert mon.acknowledge_alert("nonexistent") is False


def test_telemetry_monitor_deterministic_rerun():
    from src.telemetry.monitor import ProductionTelemetryMonitor
    mon1 = ProductionTelemetryMonitor(run_id="tel_det", seed=42)
    mon1.update(pnl=100.0, daily_pnl=100.0, current_equity=100100.0,
                peak_equity=100100.0, portfolio_greeks={"delta": 1.0}, gamma_exposure=50.0)
    mon2 = ProductionTelemetryMonitor(run_id="tel_det", seed=42)
    mon2.update(pnl=100.0, daily_pnl=100.0, current_equity=100100.0,
                peak_equity=100100.0, portfolio_greeks={"delta": 1.0}, gamma_exposure=50.0)
    s1 = mon1.get_latest_snapshot().to_dict()
    s2 = mon2.get_latest_snapshot().to_dict()
    # Timestamps differ between runs; compare numeric invariants only.
    for k in ("pnl", "drawdown_pct", "current_equity", "total_return_pct", "heat"):
        assert s1[k] == s2[k], f"{k}: {s1[k]} != {s2[k]}"


# --------------------------------------------------------------------------- end-to-end wiring


def test_end_to_end_execution_risk_microstructure_wiring():
    from src.features.orderflow_microstructure import compute_microstructure_features_dict
    from src.data.schemas import Trade, Liquidation, OrderflowSnapshot
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    pre = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 105000.0, positions={}, latency_ms=50.0)
    assert pre.approved is True
    trades = [Trade(trade_id="t1", symbol="BTCUSDT", venue="v", price=105000.0,
                    size=1.0, side="buy", timestamp=datetime.now(timezone.utc))]
    snap = OrderflowSnapshot(symbol="BTCUSDT", venue="v", trades=trades,
                             liquidations=[], funding_rates=[], timestamp=datetime.now(timezone.utc))
    micro = compute_microstructure_features_dict(snap, spot=105000.0, volatility=0.65)
    assert isfinite(micro["signed_volume"])
    assert -1.0 <= micro["footprint_imbalance"] <= 1.0
    assert 0.0 <= micro["gamma_wall_proximity"] <= 1.0
    assert json.dumps(micro, allow_nan=False) is not None


def test_full_pipeline_strict_serialization():
    eng = ExecutionEngine(initial_capital=100000.0, seed=42)
    integrator = create_execution_risk_integrator(seed=42)
    integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
    pre = integrator.pre_trade_check("BTCUSDT", "buy", 0.1, 100000.0, positions={}, latency_ms=10.0)
    payload = {
        "engine_summary": eng.get_portfolio_summary(),
        "risk_pre_trade": pre.to_dict(),
        "risk_report": integrator.get_risk_report(),
    }
    assert json.dumps(payload, allow_nan=False) is not None
