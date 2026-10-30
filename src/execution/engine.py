"""Execution engine consuming composite signals into sized orders."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from math import isfinite
from typing import Any, Dict, List, Optional

from ..errors import OrderError, RiskLimitError, get_logger
from ..signals.composite import Signal, CompositeSignalGenerator
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, clamp
from .orders import Order, OrderSide, OrderType, OrderStatus, TimeInForce, OrderFill, PositionState, ExecutionReport
from .algorithms import ExecutionAlgorithm, create_algorithm, SlippageModel


_logger = get_logger(__name__)

# Production-grade PnL/clamp bounds: prevents Inf/NaN from propagating into
# portfolio summaries when a PositionState holds a non-finite realized or
# unrealized PnL (e.g. from an adversarial fill or internal drift). Values are
# clamped to a large-but-finite bound so strict serialization (allow_nan=False)
# can never fail on a summary produced by this engine.
_PNL_BOUND = 1e18


def _safe_position_value(values: List[Any]) -> float:
    """Sum ``values`` with non-finite entries coerced to 0.0.

    Each entry is converted to float; non-convertible or non-finite entries
    contribute 0.0. The running total is clamped to ``[-_PNL_BOUND, _PNL_BOUND]``
    so overflow cannot occur. Returns a finite float.
    """
    total = 0.0
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if not isfinite(f):
            continue
        total += f
    if not isfinite(total):
        return 0.0
    if total > _PNL_BOUND:
        return _PNL_BOUND
    if total < -_PNL_BOUND:
        return -_PNL_BOUND
    return total


def _safe_position_state_summary(p: "PositionState") -> Dict[str, float]:
    """Return a finite, serialization-safe summary dict for a PositionState.

    Realized/unrealized PnL and total commission are individually clamped to
    finite bounds before summation so a single bad position cannot poison the
    whole portfolio summary.
    """
    realized = float(p.realized_pnl) if isfinite(float(p.realized_pnl)) else 0.0
    unrealized = float(p.unrealized_pnl) if isfinite(float(p.unrealized_pnl)) else 0.0
    commission = float(p.total_commission) if isfinite(float(p.total_commission)) else 0.0
    if realized > _PNL_BOUND:
        realized = _PNL_BOUND
    elif realized < -_PNL_BOUND:
        realized = -_PNL_BOUND
    if unrealized > _PNL_BOUND:
        unrealized = _PNL_BOUND
    elif unrealized < -_PNL_BOUND:
        unrealized = -_PNL_BOUND
    if commission < 0.0:
        commission = 0.0
    elif commission > _PNL_BOUND:
        commission = _PNL_BOUND
    return {
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_commission": commission,
    }


class ExecutionEngine:
    """Deterministic execution engine that consumes composite signals."""

    def __init__(
        self,
        initial_capital: float = 100000.0,
        risk_config: Optional[Any] = None,
        slippage_model: Optional[SlippageModel] = None,
        default_algo: str = "twap",
        seed: int = 42,
    ):
        if not isfinite(float(initial_capital)) or float(initial_capital) <= 0:
            raise RiskLimitError("initial_capital must be positive and finite", context={"initial_capital": initial_capital})
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise OrderError("seed must be integer for determinism", context={"seed": seed})
        self.initial_capital = float(initial_capital)
        self.cash = float(initial_capital)
        self.risk_config = risk_config
        self.slippage_model = slippage_model or SlippageModel()
        self.default_algo = default_algo
        self.seed = int(seed)

        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, PositionState] = {}
        self.fills: List[OrderFill] = []
        self.reports: List[ExecutionReport] = []
        self.equity_history: List[float] = [self.initial_capital]
        self._id_counter: int = 0

    def _generate_id(self, prefix: str = "ord") -> str:
        """Deterministic ID generator (seeded counter + hash).

        Replaces ``uuid.uuid4()`` so repeated runs with identical inputs
        produce byte-identical order/fill/report identifiers. The counter is
        incremented per call; the hash binds the sequence position to the
        engine seed for cross-run stability.
        """
        self._id_counter += 1
        payload = f"{int(self.seed)}|{prefix}|{self._id_counter}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

    def create_order_from_signal(
        self,
        signal: Signal,
        spot_price: float,
        risk_pct: float = 0.02,
        max_position_pct: float = 0.1,
        order_type: OrderType = OrderType.MARKET,
    ) -> Optional[Order]:
        """Convert composite signal into sized order."""
        if signal is None:
            return None
        if not isfinite(spot_price) or spot_price <= 0:
            raise OrderError("spot_price must be positive and finite", context={"symbol": getattr(signal, "symbol", None)})
        if not isfinite(risk_pct) or risk_pct <= 0 or risk_pct > 1.0:
            raise OrderError("risk_pct must be in (0,1]", context={"risk_pct": risk_pct})
        if not isfinite(max_position_pct) or max_position_pct <= 0 or max_position_pct > 1.0:
            raise OrderError("max_position_pct must be in (0,1]", context={"max_position_pct": max_position_pct})

        direction = str(getattr(signal, "direction", "neutral")).lower()
        confidence = clamp(getattr(signal, "confidence", 0.0), 0.0, 1.0)
        if direction == "neutral" or confidence < 1e-12:
            return None

        # Position sizing
        risk_amount = self.initial_capital * float(risk_pct)
        qty_by_risk = safe_divide(risk_amount, spot_price, 0.0)
        max_capital = self.cash * float(max_position_pct)
        qty_by_capital = safe_divide(max_capital, spot_price, 0.0)
        qty = min(qty_by_risk, qty_by_capital) * confidence
        # Use a large finite upper bound instead of float("inf") to avoid
        # clamp returning default 0.0 when the upper bound is non-finite.
        qty = clamp(qty, 0.0, 1e18)
        if qty < 1e-18:
            return None

        side = OrderSide.BUY if direction == "long" else OrderSide.SELL
        order_id = self._generate_id("ord")
        order = Order(
            order_id=order_id,
            symbol=str(signal.symbol),
            side=side,
            order_type=order_type,
            quantity=float(qty),
            price=float(spot_price) if order_type != OrderType.MARKET else None,
            time_in_force=TimeInForce.GTC,
            tags={"source": "composite_signal", "regime": getattr(signal, "regime", "unknown")},
            metadata={"confidence": float(confidence), "strength": float(getattr(signal, "strength", 0.0))},
        )
        self.orders[order_id] = order
        return order

    def submit_order(self, order: Order) -> ExecutionReport:
        if order.order_id not in self.orders:
            self.orders[order.order_id] = order
        order.submit()
        report = ExecutionReport(
            report_id=self._generate_id("rpt"),
            order_id=order.order_id,
            symbol=order.symbol,
            status=order.status,
            filled_quantity=order.filled_quantity,
            remaining_quantity=order.remaining_quantity,
            avg_fill_price=order.avg_fill_price,
            message="Order submitted",
        )
        self.reports.append(report)
        return report

    def execute_order_market(self, order: Order, fill_price: float, commission_rate: float = 0.0005) -> ExecutionReport:
        """Execute market order immediately with slippage."""
        if not isfinite(fill_price) or fill_price <= 0:
            raise OrderError("fill_price must be positive and finite", context={"order_id": order.order_id})
        if not isfinite(commission_rate) or commission_rate < 0 or commission_rate > 1:
            raise OrderError("commission_rate must be in [0,1]", context={"commission_rate": commission_rate})

        if order.order_id not in self.orders:
            self.orders[order.order_id] = order
        order.submit()

        # Apply slippage
        slip_bps = self.slippage_model.estimate_slippage_bps(order.side, order.quantity, order.quantity * 100, 0.01)
        slip = slip_bps / 10000.0
        if order.side == OrderSide.BUY:
            exec_price = fill_price * (1.0 + slip)
        else:
            exec_price = fill_price * (1.0 - slip)
        if exec_price <= 0 or not isfinite(exec_price):
            exec_price = fill_price

        notional = order.quantity * exec_price
        commission = notional * float(commission_rate)

        # Check cash for buys
        if order.side == OrderSide.BUY:
            if notional + commission > self.cash + 1e-12:
                order.reject("Insufficient cash")
                report = ExecutionReport(
                    report_id=self._generate_id("rpt"),
                    order_id=order.order_id,
                    symbol=order.symbol,
                    status=order.status,
                    filled_quantity=order.filled_quantity,
                    remaining_quantity=order.remaining_quantity,
                    avg_fill_price=order.avg_fill_price,
                    commission=commission,
                    message="Rejected: insufficient cash",
                )
                self.reports.append(report)
                return report
            self.cash -= (notional + commission)
        else:  # SELL
            self.cash += (notional - commission)

        fill = OrderFill(
            fill_id=self._generate_id("fill"),
            order_id=order.order_id,
            symbol=order.symbol,
            quantity=order.quantity,
            price=exec_price,
            commission=commission,
            liquidity="taker",
        )
        order.add_fill(fill)
        self.fills.append(fill)

        # Update position
        if order.symbol not in self.positions:
            self.positions[order.symbol] = PositionState(symbol=order.symbol)
        self.positions[order.symbol].update_fill(order.side, order.quantity, exec_price, commission)

        report = ExecutionReport(
            report_id=self._generate_id("rpt"),
            order_id=order.order_id,
            symbol=order.symbol,
            status=order.status,
            filled_quantity=order.filled_quantity,
            remaining_quantity=order.remaining_quantity,
            avg_fill_price=order.avg_fill_price,
            commission=commission,
            message="Filled",
        )
        self.reports.append(report)
        return report

    def execute_with_algorithm(
        self,
        order: Order,
        algo: ExecutionAlgorithm,
        start_time: datetime,
        end_time: datetime,
        price_history: Optional[List[Any]] = None,
        adv: float = 0.0,
        base_price: float = 100.0,
    ) -> List[ExecutionReport]:
        """Execute order using algorithm with slicing."""
        if order.order_id not in self.orders:
            self.orders[order.order_id] = order
        order.submit()

        slices = algo.generate_slices(order, start_time, end_time, price_history, adv)
        reports = []
        for sl in slices:
            if sl.quantity <= 0:
                continue
            # Simulate fill
            px = base_price
            if price_history and len(price_history) > 0:
                # Use last price
                try:
                    px = float(price_history[-1][1]) if isinstance(price_history[-1], (tuple, list)) else base_price
                except Exception:
                    px = base_price
            slip_bps = self.slippage_model.estimate_slippage_bps(order.side, sl.quantity, adv, sl.participation_rate)
            slip = slip_bps / 10000.0
            if order.side == OrderSide.BUY:
                exec_px = px * (1.0 + slip)
            else:
                exec_px = px * (1.0 - slip)
            if exec_px <= 0 or not isfinite(exec_px):
                exec_px = px
            commission = sl.quantity * exec_px * 0.0005
            notional = sl.quantity * exec_px
            if order.side == OrderSide.BUY:
                if notional + commission > self.cash + 1e-12:
                    continue  # skip slice
                self.cash -= (notional + commission)
            else:
                self.cash += (notional - commission)
            fill = OrderFill(
                fill_id=self._generate_id("fill"),
                order_id=order.order_id,
                symbol=order.symbol,
                quantity=sl.quantity,
                price=exec_px,
                commission=commission,
                liquidity="taker",
            )
            try:
                order.add_fill(fill)
                self.fills.append(fill)
                if order.symbol not in self.positions:
                    self.positions[order.symbol] = PositionState(symbol=order.symbol)
                self.positions[order.symbol].update_fill(order.side, sl.quantity, exec_px, commission)
            except Exception:
                continue
            rpt = ExecutionReport(
                report_id=self._generate_id("rpt"),
                order_id=order.order_id,
                symbol=order.symbol,
                status=order.status,
                filled_quantity=order.filled_quantity,
                remaining_quantity=order.remaining_quantity,
                avg_fill_price=order.avg_fill_price,
                commission=commission,
                message=f"Sliced fill via {algo.name}",
            )
            self.reports.append(rpt)
            reports.append(rpt)
        return reports

    def mark_to_market_all(self, prices: Dict[str, float]) -> float:
        total_unrealized = 0.0
        for sym, pos in self.positions.items():
            px = prices.get(sym)
            if px is not None and isfinite(px) and px > 0:
                total_unrealized += pos.mark_to_market(float(px))
        # Equity = cash + market value of all open positions.
        # For long positions quantity>0 contributes +qty*px; for shorts
        # quantity<0 contributes -|qty|*px (liability). Cash accounting on
        # open short already credited proceeds, so no double counting.
        equity = float(self.cash)
        for sym, pos in self.positions.items():
            px = prices.get(sym)
            if px is not None and isfinite(px) and px > 0:
                equity += float(pos.quantity) * float(px)
            else:
                # Fall back to avg entry price when mark price is unavailable;
                # guard against a non-finite entry price so equity stays finite.
                entry = float(pos.avg_entry_price)
                equity += float(pos.quantity) * (entry if isfinite(entry) else 0.0)
        # Never let non-finite equity propagate into the equity history: clamp
        # to the initial capital as a safe floor so downstream metrics and
        # serialization (allow_nan=False) cannot break.
        if not isfinite(equity):
            equity = float(self.initial_capital)
        self.equity_history.append(float(equity))
        return float(equity)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        # Guard every position-derived PnL/commission value against non-finite
        # drift so the summary is always strict-serializable (allow_nan=False).
        # A single corrupted PositionState must not poison the whole summary.
        safe_positions: Dict[str, Dict[str, float]] = {}
        for k, v in self.positions.items():
            safe_positions[k] = _safe_position_state_summary(v)
        total_realized = _safe_position_value([s["realized_pnl"] for s in safe_positions.values()])
        total_unrealized = _safe_position_value([s["unrealized_pnl"] for s in safe_positions.values()])
        total_commission = _safe_position_value([s["total_commission"] for s in safe_positions.values()])
        active_positions = [p for p in self.positions.values() if abs(p.quantity) > 1e-18]
        return serialize_metrics_strict({
            "initial_capital": float(self.initial_capital),
            "cash": float(self.cash),
            "num_orders": len(self.orders),
            "num_positions": len(active_positions),
            "num_fills": len(self.fills),
            "total_realized_pnl": total_realized,
            "total_unrealized_pnl": total_unrealized,
            "total_commission": total_commission,
            "positions": {k: v.to_dict() for k, v in self.positions.items()},
        })
