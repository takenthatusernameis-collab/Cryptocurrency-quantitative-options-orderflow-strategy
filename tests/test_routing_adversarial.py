"""Adversarial tests for multi-venue smart order routing and fill tracking."""

from __future__ import annotations

import math
import pytest

from src.errors import OrderError, RiskLimitError
from src.execution.orders import Order, OrderSide, OrderType, OrderFill
from src.execution.routing import (
    SmartOrderRouter,
    VenueType,
    VenueConfig,
    VenueQuote,
    RoutingDecision,
    FillTrackingRecord,
)


def test_routing_basic_single_venue():
    router = SmartOrderRouter()
    order = Order(order_id="o1", symbol="BTC", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=1.0)
    decision = router.route_order(order, adv=100.0)
    assert isinstance(decision, RoutingDecision)
    assert sum(decision.venue_allocations.values()) == pytest.approx(1.0, rel=1e-10)
    assert decision.participation_rate == pytest.approx(0.01, rel=1e-10)
    assert math.isfinite(decision.total_cost_bps)
    assert math.isfinite(decision.estimated_slippage_bps)


def test_routing_participation_cap_enforced():
    router = SmartOrderRouter(max_participation_rate=0.05)
    order = Order(order_id="o2", symbol="BTC", side=OrderSide.SELL, order_type=OrderType.MARKET, quantity=10.0)
    with pytest.raises(RiskLimitError):
        router.route_order(order, adv=100.0)  # 10% > 5% cap


def test_routing_with_quotes_multi_venue_splitting():
    router = SmartOrderRouter()
    quotes = [
        VenueQuote(venue=VenueType.DERIBIT, symbol="BTC", bid=50000.0, ask=50001.0, bid_size=100.0, ask_size=100.0),
        VenueQuote(venue=VenueType.OKX, symbol="BTC", bid=49999.5, ask=50000.5, bid_size=200.0, ask_size=200.0),
        VenueQuote(venue=VenueType.BINANCE, symbol="BTC", bid=50000.0, ask=50001.0, bid_size=150.0, ask_size=150.0),
    ]
    router.update_quotes(quotes)
    order = Order(order_id="o3", symbol="BTC", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=50.0)
    decision = router.route_order(order, adv=1000.0, allow_splitting=True)
    assert len(decision.venue_allocations) >= 1
    total = sum(decision.venue_allocations.values())
    assert total == pytest.approx(50.0, rel=1e-8)
    assert all(v >= 0 for v in decision.venue_allocations.values())


def test_routing_child_orders_and_fill_tracking():
    router = SmartOrderRouter()
    quotes = [
        VenueQuote(venue=VenueType.DERIBIT, symbol="BTC", bid=50000.0, ask=50001.0, bid_size=100.0, ask_size=100.0),
        VenueQuote(venue=VenueType.OKX, symbol="BTC", bid=50000.0, ask=50001.0, bid_size=100.0, ask_size=100.0),
    ]
    router.update_quotes(quotes)
    order = Order(order_id="parent1", symbol="BTC", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=20.0)
    decision = router.route_order(order, adv=500.0)
    children = router.create_child_orders(order, decision)
    assert len(children) >= 1
    # Simulate fills
    for venue, child in children.items():
        fill = OrderFill(fill_id=f"f_{venue.value}", order_id=child.order_id, symbol="BTC", quantity=child.quantity, price=50000.5, commission=child.quantity * 50000.5 * 0.0005)
        router.track_fill(venue, child.order_id, fill)
    status = router.get_fill_status(order.order_id)
    assert status["total_filled"] == pytest.approx(20.0, rel=1e-8)
    assert math.isfinite(status["avg_fill_price"])
    assert math.isfinite(status["total_commission"])


def test_routing_adversarial_nan_inf_inputs():
    router = SmartOrderRouter()
    order = Order(order_id="o4", symbol="BTC", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=1.0)
    with pytest.raises(Exception):
        router.route_order(order, adv=float('nan'))
    with pytest.raises(Exception):
        router.route_order(order, adv=float('inf'))


def test_routing_venue_config_validation():
    with pytest.raises(Exception):
        VenueConfig(venue=VenueType.DERIBIT, taker_fee_bps=float('nan'))
    with pytest.raises(Exception):
        VenueConfig(venue=VenueType.DERIBIT, max_order_size=-1.0)
    with pytest.raises(Exception):
        VenueConfig(venue=VenueType.DERIBIT, liquidity_score=1.5)


def test_routing_quote_validation():
    with pytest.raises(Exception):
        VenueQuote(venue=VenueType.DERIBIT, symbol="BTC", bid=-1.0, ask=50000, bid_size=1, ask_size=1)
    with pytest.raises(Exception):
        VenueQuote(venue=VenueType.DERIBIT, symbol="BTC", bid=50001, ask=50000, bid_size=1, ask_size=1)
    with pytest.raises(Exception):
        VenueQuote(venue=VenueType.DERIBIT, symbol="BTC", bid=50000, ask=50001, bid_size=float('nan'), ask_size=1)


def test_fill_tracking_record():
    rec = FillTrackingRecord(tracking_id="t1", parent_order_id="p1", venue=VenueType.DERIBIT, child_order_id="c1")
    fill = OrderFill(fill_id="f1", order_id="c1", symbol="BTC", quantity=0.5, price=50000.0, commission=12.5)
    rec.add_fill(fill)
    assert rec.filled_quantity == 0.5
    assert rec.avg_fill_price == 50000.0
    assert math.isfinite(rec.total_commission)
    rec.complete_fill()
    assert rec.status.value == "filled"


def test_routing_stats_serialization_safe():
    router = SmartOrderRouter()
    order = Order(order_id="o5", symbol="BTC", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=1.0)
    router.route_order(order, adv=100.0)
    stats = router.get_routing_stats()
    assert math.isfinite(stats["avg_cost_bps"])
    assert math.isfinite(stats["avg_slippage_bps"])
