"""Event-driven backtesting engine."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import isfinite
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    _np = None  # type: ignore

from ..config import BacktestConfig, RiskConfig
from ..data.schemas import PricingInputs
from ..errors import RiskLimitError, OrderError, DeterminismError, SerializationError, get_logger
from ..features.options_pricing import black_scholes, black_scholes_greeks
from ..features.iv_surface import build_iv_surface_from_chain
from ..telemetry import log_strategy_error, serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, safe_sqrt, safe_pow
from .options_hedging import delta_hedged_option_pnl


_logger = get_logger(__name__)


def _safe_variance(values: List[float], mean: Optional[float] = None) -> float:
    """Population variance with overflow/underflow guards.

    Uses a numerically stable two-pass algorithm when the naive sum-of-squares
    would overflow. Returns 0.0 for empty input or non-finite results.
    """
    if not values:
        return 0.0
    valid: List[float] = []
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if isfinite(f):
            valid.append(f)
    if len(valid) < 2:
        return 0.0
    if mean is None:
        m = sum(valid) / len(valid)
    else:
        m = float(mean)
    if not isfinite(m):
        m = 0.0
    # Two-pass: compute mean first, then squared deviations.
    # Guard against overflow by scaling if values are extreme.
    max_abs = max(abs(v) for v in valid)
    if max_abs > 1e150:
        scale = max_abs
        scaled = [v / scale for v in valid]
        m_scaled = m / scale
        var = sum((x - m_scaled) ** 2 for x in scaled) / len(scaled)
        var = var * scale * scale
    else:
        var = sum((v - m) ** 2 for v in valid) / len(valid)
    if not isfinite(var) or var < 0.0:
        return 0.0
    return float(var)


def _safe_std(values: List[float], mean: Optional[float] = None) -> float:
    """Population standard deviation with numerical guards. Returns 0.0 on degenerate input."""
    var = _safe_variance(values, mean=mean)
    return safe_sqrt(var, default=0.0, operation="safe_std")


@dataclass
class Position:
    """An open (or partially open) position held by the backtesting engine.

    Encodes the entry terms and current side. ``stop_loss`` and
    ``take_profit`` are absolute price levels (not percentages) used by
    :meth:`BacktestEngine.check_risk_controls` to trigger exits. For longs,
    stop_loss is below entry and take_profit is above; for shorts the levels
    are inverted.
    """

    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    side: str  # 'long' or 'short'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
    """A completed (closed) trade record produced by :meth:`BacktestEngine.execute_trade`.

    ``pnl`` is the realized profit/loss including commission. ``is_win`` is
    ``True`` when ``pnl > 0``. ``commission`` is the fee charged at fill.
    """

    symbol: str
    quantity: float
    price: float
    side: str  # 'buy' or 'sell'
    timestamp: datetime
    commission: float = 0.0
    pnl: float = 0.0
    is_win: bool = False


@dataclass
class BacktestResults:
    """Aggregate performance metrics and full trade/equity history from a backtest.

    All monetary/return fields are unitless fractions (e.g. 0.15 = 15%)
    except where noted. ``profit_factor`` may be ``inf`` when there are wins
    but zero losses. ``total_trades`` counts all executed trades, while
    ``winning_trades``/``losing_trades`` count only closed trades with
    non-zero PnL.
    """

    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    calmar_ratio: float = 0.0
    winning_trades: int = 0
    losing_trades: int = 0
    returns: List[float] = field(default_factory=list)
    drawdowns: List[float] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    options_data_ref: Optional[Dict[str, Any]] = None
    options_hedging: Optional[Dict[str, Any]] = None
    iv_surfaces: Optional[Dict[str, Any]] = None


class BacktestEngine:
    """Event-driven, single-asset-per-symbol backtesting engine with realistic fills.

    Manages cash, positions, trades, and an equity curve. Supports long and
    short positions, stop-loss/take-profit exits, drawdown-based liquidation,
    deterministic partial fills, round-lot sizing, and slippage/fee modeling.
    The engine is stateful: each call to :meth:`execute_trade` mutates internal
    state, so a fresh instance should be created per simulation run.

    Conventions:
      - Cash accounting: opening a long debits cash (cost + commission);
        opening a short credits cash (notional - commission). Unrealized
        PnL is not tracked separately; equity is recomputed from cash plus
        position market value on each tick.
      - ``side`` in :meth:`execute_trade` is from the perspective of the
        order: ``'buy'`` opens a long or covers a short; ``'sell'`` closes a
        long or opens a short.
    """

    def __init__(
        self,
        config: Optional[BacktestConfig] = None,
        risk_config: Optional[RiskConfig] = None,
        iv_surfaces: Optional[Dict[str, Any]] = None,
        options_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        if config is None and kwargs:
            # Extract config fields
            cfg_kwargs = {k: v for k, v in kwargs.items() if k in BacktestConfig.__dataclass_fields__}
            config = BacktestConfig(**cfg_kwargs) if cfg_kwargs else BacktestConfig()
        elif config is None:
            config = BacktestConfig()

        # Extract risk config if passed as dict
        if risk_config is None and kwargs:
            risk_kwargs = {k: v for k, v in kwargs.items() if k in RiskConfig.__dataclass_fields__}
            if risk_kwargs:
                risk_config = RiskConfig(**risk_kwargs)
            elif isinstance(kwargs.get("risk_config"), dict):
                risk_config = RiskConfig(**kwargs["risk_config"])
        self.config = config
        self.risk_config = risk_config or RiskConfig()
        # Options/IV inputs (backward compatible)
        self.iv_surfaces = iv_surfaces if iv_surfaces is not None else kwargs.get("iv_surfaces")
        self.options_data = options_data if options_data is not None else kwargs.get("options_data")
        self.initial_capital = float(getattr(config, "initial_capital", 100000.0))
        if not isfinite(self.initial_capital) or self.initial_capital <= 0:
            e = RiskLimitError(
                "initial_capital must be positive and finite",
                context={"initial_capital": getattr(config, "initial_capital", None), "module": "src.backtest.engine", "operation": "__init__"},
            )
            try:
                log_strategy_error(e, operation="__init__", module="src.backtest.engine")
            except Exception:
                pass
            raise e
        self.cash = self.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [self.initial_capital]
        self.max_equity = self.initial_capital
        self.peak_equity = self.initial_capital
        # Deterministic RNG for partial fills if needed
        try:
            import random

            seed = getattr(config, "slippage_seed", 42)
            if seed is None:
                raise DeterminismError(
                    "slippage_seed required for determinism",
                    context={"operation": "__init__"},
                )
            try:
                seed_int = int(seed)
            except Exception as e:
                raise DeterminismError(
                    "slippage_seed must be integer",
                    context={"slippage_seed": seed},
                    cause=e,
                )
            self._rng = random.Random(seed_int)
        except (DeterminismError, RiskLimitError):
            raise
        except Exception as e:
            raise DeterminismError("Backtest RNG not initialized; determinism required", context={"operation": "__init__"}, cause=e)
        if not hasattr(self, "_rng") or self._rng is None:
            raise DeterminismError("Backtest RNG not initialized; determinism required", context={"operation": "__init__"})

    def _apply_slippage(self, price: float, side: str) -> float:
        """Apply configured slippage to a raw price.

        Buys are slurred upward (worse fill) and sells downward by
        ``slippage_bps`` (capped at ``max_slippage_bps`` if set). Returns the
        adjusted execution price.
        """
        slippage_bps = getattr(self.config, "slippage_bps", 0)
        slippage = float(slippage_bps) / 10000.0
        max_slip_bps = getattr(self.config, "max_slippage_bps", 0)
        if max_slip_bps and max_slip_bps > 0:
            max_slip = float(max_slip_bps) / 10000.0
            if slippage > max_slip:
                slippage = max_slip
        if side == "buy":
            return price * (1.0 + slippage)
        else:  # sell
            return price * (1.0 - slippage)

    def _get_commission(self, notional: float) -> float:
        """Compute commission for a notional trade value.

        Returns ``notional * fee_rate`` where ``fee_rate`` comes from
        :class:`BacktestConfig`. Non-finite notional yields 0.0.
        """
        fee_rate = getattr(self.config, "fee_rate", 0.0)
        return float(notional) * float(fee_rate)

    def calculate_position_size(self, price: float, side: str = "long", risk_pct: Optional[float] = None) -> float:
        """Calculate position size (quantity) based on risk limits.

        Sizing is the minimum of two constraints:
          1. Risk-based: ``initial_capital * risk_pct / price`` where
             ``risk_pct`` defaults to ``risk_config.stop_loss_pct``.
          2. Capital-based: ``cash * risk_config.max_position_pct / price``.

        Returns 0.0 for non-positive prices. The ``side`` argument is accepted
        for API symmetry but does not affect sizing in this implementation.
        """
        risk_pct = risk_pct if risk_pct is not None else getattr(self.risk_config, "stop_loss_pct", 0.02)
        max_position_pct = getattr(self.risk_config, "max_position_pct", 0.1)
        max_capital = self.cash * max_position_pct

        # Risk-based sizing
        risk_amount = self.initial_capital * risk_pct
        qty_by_risk = risk_amount / price if price > 0 else 0.0

        # Limit by max position size
        qty_by_capital = max_capital / price if price > 0 else 0.0

        qty = min(qty_by_risk, qty_by_capital)
        if qty < 0:
            qty = 0.0
        return qty

    def execute_trade(self, symbol: str, quantity: float, price: float, side: str, timestamp: datetime,
                      stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Trade:
        """Execute a trade with fees, slippage, short selling support.

        Applies, in order: round-lot rounding (down), partial-fill scaling
        (deterministic via RNG), and max-quantity cap. Then computes
        slippage and commission. Updates cash and positions per the trade
        side, and records a :class:`Trade` with realized ``pnl`` (for closes)
        and ``is_win`` flag. Raises ``ValueError`` for invalid quantity or
        insufficient cash.
        """
        from math import isfinite as _isfinite
        if quantity <= 0 or not _isfinite(quantity):
            e = OrderError(
                "Quantity must be positive and finite",
                context={"symbol": symbol, "quantity": quantity, "module": "src.backtest.engine", "operation": "execute_trade"},
            )
            try:
                log_strategy_error(e, operation="execute_trade", module="src.backtest.engine", symbol=symbol)
            except Exception:
                pass
            raise e
        if price <= 0 or not _isfinite(price):
            e = OrderError(
                "Price must be positive and finite",
                context={"symbol": symbol, "price": price, "module": "src.backtest.engine", "operation": "execute_trade"},
            )
            try:
                log_strategy_error(e, operation="execute_trade", module="src.backtest.engine", symbol=symbol)
            except Exception:
                pass
            raise e

        qty = float(quantity)
        if not _isfinite(qty):
            raise OrderError("Quantity must be finite", context={"symbol": symbol})
        # Apply lot rounding if configured
        lot_size = getattr(self.config, "round_lot_size", 0.0)
        if lot_size and lot_size > 0 and _isfinite(lot_size):
            # round down to nearest lot
            qty = (qty // lot_size) * lot_size
            if qty <= 0:
                raise OrderError("Quantity must be positive after lot rounding", context={"symbol": symbol, "lot_size": lot_size})

        # Apply partial fills if configured
        pfr = getattr(self.config, "partial_fill_rate", 0.0)
        if pfr and pfr > 0 and pfr < 1.0 and isfinite(pfr):
            try:
                fill_frac = max(0.0, min(1.0, float(self._rng.uniform(pfr * 0.5, min(1.0, pfr * 1.5)))))
            except Exception:
                fill_frac = float(pfr)
            if fill_frac > 0:
                qty = qty * fill_frac
            if qty <= 0:
                raise OrderError("Quantity must be positive after partial fill", context={"symbol": symbol})

        # Enforce max position qty from risk config
        max_pos_qty = getattr(self.risk_config, "max_position_qty", 0.0)
        if max_pos_qty and max_pos_qty > 0 and isfinite(max_pos_qty):
            if qty > max_pos_qty:
                qty = max_pos_qty

        execution_price = self._apply_slippage(price, side)
        notional = float(qty) * float(execution_price)
        commission = self._get_commission(notional)

        trade = Trade(
            symbol=symbol,
            quantity=float(qty),
            price=float(execution_price),
            side=str(side).lower(),
            timestamp=timestamp,
            commission=commission,
            pnl=0.0,
            is_win=False,
        )

        side_lower = str(side).lower()

        if side_lower == "buy":
            # Buying to open long, or to close short
            if symbol in self.positions and self.positions[symbol].side == "short":
                pos = self.positions[symbol]
                # Cover short: profit = (entry - exit) * qty
                pnl = (pos.entry_price - execution_price) * pos.quantity - commission
                proceeds_impact = execution_price * pos.quantity  # cost to cover
                self.cash -= proceeds_impact
                self.cash -= commission
                trade.pnl = pnl
                trade.is_win = pnl > 0
                del self.positions[symbol]
            else:
                # Open long
                cost = notional + commission
                if cost > self.cash + 1e-10:  # small epsilon for float
                    e_risk: RiskLimitError = RiskLimitError(
                        "Insufficient cash for long position",
                        context={
                            "symbol": symbol,
                            "cost": cost,
                            "cash": self.cash,
                            "quantity": qty,
                            "price": execution_price,
                            "module": "src.backtest.engine",
                            "operation": "execute_trade",
                        },
                    )
                    try:
                        log_strategy_error(e_risk, operation="execute_trade", module="src.backtest.engine", symbol=symbol)
                    except Exception:
                        pass
                    raise e_risk
                self.cash -= cost
                sl = stop_loss if stop_loss is not None else (execution_price * (1 - getattr(self.risk_config, "stop_loss_pct", 0.02)))
                tp = take_profit if take_profit is not None else (execution_price * (1 + getattr(self.risk_config, "take_profit_pct", 0.04)))
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=float(qty),
                    entry_price=float(execution_price),
                    entry_time=timestamp,
                    side="long",
                    stop_loss=sl,
                    take_profit=tp,
                )
        elif side_lower == "sell":
            allow_short = getattr(self.risk_config, "allow_shorting", True)
            # Selling to close long, or to open short
            if symbol in self.positions and self.positions[symbol].side == "long":
                pos = self.positions[symbol]
                # Close long: profit = (exit - entry) * qty
                pnl = (execution_price - pos.entry_price) * pos.quantity - commission
                self.cash += (notional - commission)
                trade.pnl = pnl
                trade.is_win = pnl > 0
                del self.positions[symbol]
            else:
                # Open short
                if not allow_short:
                    err = RiskLimitError("Short selling not allowed", context={"symbol": symbol, "module": "src.backtest.engine", "operation": "execute_trade"})
                    try:
                        log_strategy_error(err, operation="execute_trade", module="src.backtest.engine", symbol=symbol)
                    except Exception:
                        pass
                    raise err
                max_position_pct = getattr(self.risk_config, "max_position_pct", 0.1)
                max_notional = self.cash * max_position_pct
                if notional > max_notional + 1e-10:
                    _logger.warning(
                        "short_notional_breach",
                        symbol=symbol,
                        notional=notional,
                        max_notional=max_notional,
                        operation="open_short",
                    )
                    e_short = RiskLimitError(
                        "Position size exceeds limit",
                        context={"symbol": symbol, "notional": notional, "max_notional": max_notional, "module": "src.backtest.engine", "operation": "execute_trade"},
                    )
                    try:
                        log_strategy_error(e_short, operation="execute_trade", module="src.backtest.engine", symbol=symbol)
                    except Exception:
                        pass
                    raise e_short
                self.cash += notional  # credit proceeds
                self.cash -= commission  # pay fees on opening short
                sl = stop_loss if stop_loss is not None else (execution_price * (1 + getattr(self.risk_config, "stop_loss_pct", 0.02)))
                tp = take_profit if take_profit is not None else (execution_price * (1 - getattr(self.risk_config, "take_profit_pct", 0.04)))
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=float(qty),
                    entry_price=float(execution_price),
                    entry_time=timestamp,
                    side="short",
                    stop_loss=sl,
                    take_profit=tp,
                )
        else:
            err_order: OrderError = OrderError(f"Invalid side: {side}", context={"symbol": symbol, "side": side, "module": "src.backtest.engine", "operation": "execute_trade"})
            try:
                log_strategy_error(err_order, operation="execute_trade", module="src.backtest.engine", symbol=symbol)
            except Exception:
                pass
            raise err_order

        self.trades.append(trade)
        return trade

    def check_risk_controls(self, current_prices: Dict[str, float], timestamp: datetime) -> List[Trade]:
        """Check stop-loss, take-profit, and drawdown conditions; execute triggered exits.

        Iterates open positions and closes any whose stop-loss or take-profit
        level is breached by the current price. Longs exit on ``sell``; shorts
        exit on ``buy``. After per-position checks, enforces
        ``risk_config.max_drawdown_limit``: if current drawdown from peak
        equity reaches the threshold, all remaining positions are liquidated.
        Returns the list of executed exit :class:`Trade` objects.
        """
        triggered_trades = []
        for symbol in list(self.positions.keys()):
            if symbol not in current_prices:
                continue
            pos = self.positions[symbol]
            price = current_prices[symbol]
            if not isfinite(price):
                continue

            if pos.side == "long":
                if pos.stop_loss is not None and price <= pos.stop_loss:
                    trade = self.execute_trade(symbol, pos.quantity, price, "sell", timestamp)
                    triggered_trades.append(trade)
                elif pos.take_profit is not None and price >= pos.take_profit:
                    trade = self.execute_trade(symbol, pos.quantity, price, "sell", timestamp)
                    triggered_trades.append(trade)
            elif pos.side == "short":
                if pos.stop_loss is not None and price >= pos.stop_loss:
                    trade = self.execute_trade(symbol, pos.quantity, price, "buy", timestamp)
                    triggered_trades.append(trade)
                elif pos.take_profit is not None and price <= pos.take_profit:
                    trade = self.execute_trade(symbol, pos.quantity, price, "buy", timestamp)
                    triggered_trades.append(trade)

        # Enforce max_drawdown_limit: if equity drops below threshold, close all positions
        if current_prices:
            equity = self.get_equity(current_prices)
            if self.initial_capital > 0:
                drawdown = (self.max_equity - equity) / self.max_equity
                max_dd_limit = getattr(self.risk_config, "max_drawdown_limit", 0.2)
                if drawdown >= max_dd_limit:
                    for symbol in list(self.positions.keys()):
                        if symbol in current_prices and isfinite(current_prices[symbol]):
                            pos = self.positions[symbol]
                            side = "sell" if pos.side == "long" else "buy"
                            trade = self.execute_trade(symbol, pos.quantity, current_prices[symbol], side, timestamp)
                            triggered_trades.append(trade)
        return triggered_trades

    def update_equity_curve(self, current_prices: Optional[Dict[str, float]] = None) -> float:
        """Append current equity to the equity curve and update running peaks.

        Runs :meth:`check_risk_controls` first so SL/TP/drawdown exits are
        reflected in the equity value being recorded. Returns the newly
        recorded equity. Idempotent when called with empty prices (appends
        current cash equity).
        """
        prices = current_prices or {}
        # Enforce SL/TP and risk controls on every tick
        if prices:
            self.check_risk_controls(prices, datetime.now(timezone.utc))
        equity = self.get_equity(prices)
        self.equity_curve.append(equity)
        if equity > self.max_equity:
            self.max_equity = equity
        if equity > self.peak_equity:
            self.peak_equity = equity
        return equity

    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """Calculate current equity from cash plus open position market value.

        For longs: ``equity = cash + qty * current_price`` (cash was debited at
        open). For shorts: cash was *credited* with proceeds (qty * entry_price)
        at open, so the only remaining liability is qty * current_price. We
        subtract it rather than adding an unrealized PnL term, which would
        double-count the proceeds already sitting in cash.
        """
        equity = float(self.cash)
        for symbol, pos in self.positions.items():
            if symbol not in current_prices or not isfinite(current_prices[symbol]):
                continue
            price = float(current_prices[symbol])
            if pos.side == "long":
                equity += pos.quantity * price
            elif pos.side == "short":
                # Subtract current liability; proceeds already in cash.
                equity -= pos.quantity * price
        return equity

    def calculate_metrics(self) -> BacktestResults:
        """Calculate performance metrics from the equity curve and trade log.

        Computes total return, Sharpe (annualized, 252 trading days), Sortino
        (downside-deviation based), max drawdown, win rate, profit factor, and
        Calmar ratio. All returns are unitless per-period fractions. Sharpe and
        Sortino use a risk-free rate from ``config.risk_free_rate``. Non-finite
        intermediates are guarded and replaced with 0.0. Returns an empty
        :class:`BacktestResults` if the equity curve is empty.
        """
        if not self.equity_curve:
            res_empty = BacktestResults()
            # Attach options info if available
            try:
                if self.iv_surfaces:
                    res_empty.iv_surfaces = self.iv_surfaces
            except Exception:
                pass
            try:
                if self.options_data:
                    res_empty.options_data_ref = self.options_data
            except Exception:
                pass
            try:
                # Attempt delta-hedged attribution if options data provided
                if self.options_data:
                    opt_res = delta_hedged_option_pnl(
                        spot_path=self.options_data.get("spot_path", self.equity_curve),
                        times=self.options_data.get("times", list(range(len(self.equity_curve)))) if self.equity_curve else [],
                        strike=float(self.options_data.get("strike", 50000.0)),
                        rate=float(getattr(self.config, "risk_free_rate", 0.0)),
                        volatility=float(self.options_data.get("volatility", 0.5)),
                        option_type=str(self.options_data.get("option_type", "call")),
                        option_price_entry=self.options_data.get("option_price_entry"),
                        transaction_cost_bps=float(self.options_data.get("transaction_cost_bps", 0.0)),
                        rebalance_every_step=bool(self.options_data.get("rebalance_every_step", True)),
                        seed=getattr(self.config, "slippage_seed", 42) if hasattr(self.config, "slippage_seed") else 42,
                    )
                    res_empty.options_hedging = opt_res
            except Exception:
                pass
            return res_empty

        # Total return
        if self.initial_capital == 0 or not isfinite(self.initial_capital):
            total_return = 0.0
        else:
            total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital
        if not isfinite(total_return):
            total_return = 0.0

        returns = []
        for i in range(1, len(self.equity_curve)):
            prev = self.equity_curve[i - 1]
            if prev == 0 or not isfinite(prev):
                continue
            curr = self.equity_curve[i]
            if not isfinite(curr):
                continue
            ret = (curr - prev) / prev
            if isfinite(ret):
                returns.append(ret)

        risk_free_rate = getattr(self.config, "risk_free_rate", 0.0)
        sharpe_ratio = 0.0
        sortino_ratio = 0.0
        if returns:
            avg_return = sum(returns) / len(returns)
            var = _safe_variance(returns, mean=avg_return)
            std_return = _safe_std(returns, mean=avg_return)
            if std_return > 0 and isfinite(std_return):
                sharpe_ratio = (avg_return - risk_free_rate / 252.0) / std_return * (252.0 ** 0.5)
            else:
                sharpe_ratio = 0.0
            # Sortino
            downside = [r for r in returns if r < 0 and isfinite(r)]
            if downside:
                downside_var = _safe_variance(downside)
                downside_std = _safe_std(downside)
                if downside_std > 0 and isfinite(downside_std):
                    sortino_ratio = (avg_return - risk_free_rate / 252.0) / downside_std * (252.0 ** 0.5)
                else:
                    sortino_ratio = sharpe_ratio
            else:
                sortino_ratio = sharpe_ratio
        if not isfinite(sharpe_ratio):
            sharpe_ratio = 0.0
        if not isfinite(sortino_ratio):
            sortino_ratio = 0.0

        # Max drawdown
        peak = self.equity_curve[0] if self.equity_curve else self.initial_capital
        max_dd = 0.0
        for value in self.equity_curve:
            if not isfinite(value):
                continue
            if value > peak:
                peak = value
            if peak == 0:
                dd = 0.0
            else:
                dd = (peak - value) / peak
            if dd > max_dd and isfinite(dd):
                max_dd = dd
        if not isfinite(max_dd):
            max_dd = 0.0

        # Win rate and profit factor from closed trades
        winning_trades = 0
        losing_trades = 0
        total_wins = 0.0
        total_losses = 0.0
        for trade in self.trades:
            if hasattr(trade, 'pnl') and trade.pnl != 0:
                if trade.pnl > 0:
                    winning_trades += 1
                    total_wins += trade.pnl
                elif trade.pnl < 0:
                    losing_trades += 1
                    total_losses += abs(trade.pnl)
            elif hasattr(trade, 'is_win') and trade.is_win:
                winning_trades += 1
            elif hasattr(trade, 'is_win') and not trade.is_win and trade.pnl < 0:
                losing_trades += 1

        total_closed = winning_trades + losing_trades
        if total_closed > 0:
            win_rate = winning_trades / total_closed
        else:
            win_rate = 0.0

        if total_losses > 0:
            profit_factor = total_wins / total_losses
        elif total_wins > 0:
            profit_factor = float('inf')
        else:
            profit_factor = 0.0

        if not isfinite(win_rate):
            win_rate = 0.0
        # profit_factor: keep inf when wins exist with zero losses; never collapse to 0
        if not isfinite(profit_factor):
            if profit_factor > 0:
                pass  # keep inf
            else:
                profit_factor = 0.0

        calmar_ratio = (total_return / max_dd) if max_dd > 0 and isfinite(max_dd) else 0.0
        if not isfinite(calmar_ratio):
            calmar_ratio = 0.0

        result = BacktestResults(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.trades),
            trades=self.trades,
            equity_curve=self.equity_curve,
            calmar_ratio=calmar_ratio,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
        )
        try:
            if self.iv_surfaces:
                result.iv_surfaces = self.iv_surfaces
        except Exception:
            pass
        try:
            if getattr(self, "options_data", None):
                result.options_data_ref = self.options_data
        except Exception:
            pass
        try:
            if self.options_data:
                opt_res = delta_hedged_option_pnl(
                    spot_path=self.options_data.get("spot_path", self.equity_curve),
                    times=self.options_data.get("times", list(range(len(self.equity_curve)))) if self.equity_curve else [],
                    strike=float(self.options_data.get("strike", 50000.0)),
                    rate=float(getattr(self.config, "risk_free_rate", 0.0)),
                    volatility=float(self.options_data.get("volatility", 0.5)),
                    option_type=str(self.options_data.get("option_type", "call")),
                    option_price_entry=self.options_data.get("option_price_entry"),
                    transaction_cost_bps=float(self.options_data.get("transaction_cost_bps", 0.0)),
                    rebalance_every_step=bool(self.options_data.get("rebalance_every_step", True)),
                    seed=getattr(self.config, "slippage_seed", 42) if hasattr(self.config, "slippage_seed") else 42,
                )
                result.options_hedging = opt_res
        except Exception:
            pass
        return result


@dataclass
class WalkForwardWindowResult:
    train_start: int = 0
    train_end: int = 0
    test_start: int = 0
    test_end: int = 0
    in_sample_return: float = 0.0
    out_of_sample_return: float = 0.0
    in_sample_sharpe: float = 0.0
    out_of_sample_sharpe: float = 0.0
    in_sample_max_drawdown: float = 0.0
    out_of_sample_max_drawdown: float = 0.0
    oos_metrics: Optional[BacktestResults] = None
    is_metrics: Optional[BacktestResults] = None
    regime_info: Optional[Dict[str, Any]] = None
    purge_applied: int = 0
    embargo_applied: int = 0


@dataclass
class PortfolioWalkForwardWindowResult:
    train_start: int = 0
    train_end: int = 0
    test_start: int = 0
    test_end: int = 0
    symbols: List[str] = field(default_factory=list)
    in_sample_return: float = 0.0
    out_of_sample_return: float = 0.0
    in_sample_sharpe: float = 0.0
    out_of_sample_sharpe: float = 0.0
    in_sample_max_drawdown: float = 0.0
    out_of_sample_max_drawdown: float = 0.0
    correlation_matrix: Optional[List[List[float]]] = None
    oos_metrics: Optional[BacktestResults] = None
    is_metrics: Optional[BacktestResults] = None


@dataclass
class PortfolioWalkForwardResults:
    windows: List[PortfolioWalkForwardWindowResult] = field(default_factory=list)
    overall_out_of_sample_return: float = 0.0
    overall_out_of_sample_sharpe: float = 0.0
    overall_out_of_sample_max_drawdown: float = 0.0
    stability_ratio: float = 0.0
    degradation: float = 0.0
    oos_equity_curve: List[float] = field(default_factory=list)
    oos_trades: List[Trade] = field(default_factory=list)

    def assert_oos_finite(self) -> None:
        ctx = {
            "operation": "assert_oos_finite",
            "module": "src.backtest.engine",
        }
        fields = {
            "overall_out_of_sample_return": self.overall_out_of_sample_return,
            "overall_out_of_sample_sharpe": self.overall_out_of_sample_sharpe,
            "overall_out_of_sample_max_drawdown": self.overall_out_of_sample_max_drawdown,
            "stability_ratio": self.stability_ratio,
            "degradation": self.degradation,
        }
        bad = [k for k, v in fields.items() if not isfinite(float(v))]
        if bad:
            raise SerializationError(
                "Non-finite OOS/walk-forward metric detected; refusing to serialize",
                context={**ctx, "nonfinite_fields": bad},
            )
        for w in self.windows:
            for fname, fval in (
                ("in_sample_return", w.in_sample_return),
                ("in_sample_sharpe", w.in_sample_sharpe),
                ("in_sample_max_drawdown", w.in_sample_max_drawdown),
                ("out_of_sample_return", w.out_of_sample_return),
                ("out_of_sample_sharpe", w.out_of_sample_sharpe),
                ("out_of_sample_max_drawdown", w.out_of_sample_max_drawdown),
            ):
                if not isfinite(float(fval)):
                    raise SerializationError(
                        f"Non-finite window metric {fname}",
                        context={**ctx, "window_index": w.train_start, "field": fname, "value": fval},
                    )

    def serialize_oos(self) -> Dict[str, Any]:
        self.assert_oos_finite()
        payload: Dict[str, Any] = {
            "overall_out_of_sample_return": self.overall_out_of_sample_return,
            "overall_out_of_sample_sharpe": self.overall_out_of_sample_sharpe,
            "overall_out_of_sample_max_drawdown": self.overall_out_of_sample_max_drawdown,
            "stability_ratio": self.stability_ratio,
            "degradation": self.degradation,
            "num_windows": len(self.windows),
            "oos_equity_curve": self.oos_equity_curve,
            "oos_trade_count": len(self.oos_trades),
        }
        return serialize_metrics_strict(payload)


@dataclass
class WalkForwardResults:
    windows: List[WalkForwardWindowResult] = field(default_factory=list)
    overall_out_of_sample_return: float = 0.0
    overall_out_of_sample_sharpe: float = 0.0
    overall_out_of_sample_max_drawdown: float = 0.0
    stability_ratio: float = 0.0
    degradation: float = 0.0
    oos_equity_curve: List[float] = field(default_factory=list)
    oos_trades: List[Trade] = field(default_factory=list)
    regime_shift_coverage: Dict[str, int] = field(default_factory=dict)
    purge_embargo_enforced: bool = True

    def assert_oos_finite(self) -> None:
        """Raise :class:`SerializationError` if any aggregate OOS metric is non-finite.

        Enforces numerical stability on stability_ratio and degradation plus all
        aggregate OOS return/sharpe/drawdown metrics. Called before serialization
        to guarantee no NaN/Inf leaks into emitted results.
        """
        ctx = {
            "operation": "assert_oos_finite",
            "module": "src.backtest.engine",
        }
        fields = {
            "overall_out_of_sample_return": self.overall_out_of_sample_return,
            "overall_out_of_sample_sharpe": self.overall_out_of_sample_sharpe,
            "overall_out_of_sample_max_drawdown": self.overall_out_of_sample_max_drawdown,
            "stability_ratio": self.stability_ratio,
            "degradation": self.degradation,
        }
        bad = [k for k, v in fields.items() if not isfinite(float(v))]
        if bad:
            raise SerializationError(
                "Non-finite OOS/walk-forward metric detected; refusing to serialize",
                context={**ctx, "nonfinite_fields": bad},
            )
        for w in self.windows:
            for fname, fval in (("in_sample_return", w.in_sample_return), ("in_sample_sharpe", w.in_sample_sharpe),
                                ("in_sample_max_drawdown", w.in_sample_max_drawdown),
                                ("out_of_sample_return", w.out_of_sample_return),
                                ("out_of_sample_sharpe", w.out_of_sample_sharpe),
                                ("out_of_sample_max_drawdown", w.out_of_sample_max_drawdown)):
                if not isfinite(float(fval)):
                    raise SerializationError(
                        f"Non-finite window metric {fname}",
                        context={**ctx, "window_index": w.train_start, "field": fname, "value": fval},
                    )

    def serialize_oos(self) -> Dict[str, Any]:
        """Serialize aggregate OOS walk-forward results with strict allow_nan=False semantics.

        Runs :meth:`assert_oos_finite` first, then serializes through
        :func:`serialize_metrics_strict`. Raises :class:`SerializationError` on
        any non-finite value.
        """
        self.assert_oos_finite()
        payload: Dict[str, Any] = {
            "overall_out_of_sample_return": self.overall_out_of_sample_return,
            "overall_out_of_sample_sharpe": self.overall_out_of_sample_sharpe,
            "overall_out_of_sample_max_drawdown": self.overall_out_of_sample_max_drawdown,
            "stability_ratio": self.stability_ratio,
            "degradation": self.degradation,
            "num_windows": len(self.windows),
            "oos_equity_curve": self.oos_equity_curve,
            "oos_trade_count": len(self.oos_trades),
        }
        return serialize_metrics_strict(payload)


class WalkForwardBacktest:
    def __init__(
        self,
        engine: Optional[BacktestEngine] = None,
        config: Optional[BacktestConfig] = None,
        risk_config: Optional[RiskConfig] = None,
        purge: int = 0,
        embargo: int = 0,
        **kwargs: Any,
    ) -> None:
        # Be flexible about positional args
        # If first arg is not a BacktestEngine instance
        if engine is not None and not isinstance(engine, BacktestEngine):
            # Could be config
            if isinstance(engine, BacktestConfig):
                if config is None or isinstance(config, RiskConfig):
                    risk_config = config
                config = engine
                engine = None
            elif hasattr(engine, 'initial_capital') and not isinstance(engine, BacktestEngine):  # likely config
                if config is None and isinstance(risk_config, RiskConfig):
                    pass  # keep as is
                # try to detect
                if config is None or isinstance(config, RiskConfig):
                    risk_config = config
                config = engine
                engine = None
        if engine is not None and isinstance(engine, BacktestEngine):
            self.engine_template = engine
            self.config = getattr(engine, "config", config or BacktestConfig())
            self.risk_config = getattr(engine, "risk_config", risk_config or RiskConfig())
        else:
            if config is None and kwargs:
                # maybe passed as config-like
                cfg_kwargs = {k: v for k, v in kwargs.items() if k in BacktestConfig.__dataclass_fields__}
                if cfg_kwargs:
                    config = BacktestConfig(**cfg_kwargs)
            if risk_config is None and kwargs:
                risk_kwargs = {k: v for k, v in kwargs.items() if k in RiskConfig.__dataclass_fields__}
                if risk_kwargs:
                    risk_config = RiskConfig(**risk_kwargs)
            self.config = config if isinstance(config, BacktestConfig) else BacktestConfig()
            self.risk_config = risk_config if isinstance(risk_config, RiskConfig) else RiskConfig()
            self.engine_template = BacktestEngine(self.config, self.risk_config)
        # Purge/embargo: purge removes tail of train set adjacent to test; embargo removes head of test set adjacent to train.
        # Both guard against lookahead/label-leakage between in-sample and out-of-sample windows.
        if not isinstance(purge, int) or purge < 0:
            purge = 0
        if not isinstance(embargo, int) or embargo < 0:
            embargo = 0
        self.purge = purge
        self.embargo = embargo
        # Per-run regime coverage accumulator (reset at the start of each
        # run_walk_forward call so repeated runs are independent).
        self._regime_shift_coverage: Dict[str, int] = {}

    def run_walk_forward(self,
                         price_series: Optional[Dict[str, List[float]]] = None,
                         signals: Optional[Dict[str, List[int]]] = None,
                         timestamps: Optional[List[datetime]] = None,
                         train_window: int = 252,
                         test_window: int = 63,
                         step_size: Optional[int] = None,
                         rolling: bool = True,
                         anchored: bool = False,
                         min_train_size: int = 50,
                         purge: Optional[int] = None,
                         embargo: Optional[int] = None) -> WalkForwardResults:
        """Run walk-forward analysis with rolling or anchored windows.

        Purge removes the last ``purge`` observations of each training window
        (closest to the test set) to prevent label leakage from overlapping
        features. Embargo removes the first ``embargo`` observations of each
        test window (closest to the training set) to prevent training-set
        information from leaking into out-of-sample predictions. Per-call
        values override the instance-level ``self.purge``/``self.embargo``.
        """
        if price_series is None and signals is None:
            raise ValueError("Either price_series or signals must be provided")

        purge_eff = self.purge if purge is None else purge
        embargo_eff = self.embargo if embargo is None else embargo
        if not isinstance(purge_eff, int) or purge_eff < 0:
            purge_eff = 0
        if not isinstance(embargo_eff, int) or embargo_eff < 0:
            embargo_eff = 0

        # Reset per-run regime coverage so repeated calls are independent.
        self._regime_shift_coverage = {}

        # Strict time ordering: timestamps must be monotonically increasing if provided.
        if timestamps is not None:
            self._validate_time_ordering(timestamps)

        # Determine length
        if price_series is not None:
            # get length from first symbol
            first_key = next(iter(price_series.keys()))
            n = len(price_series[first_key])
        elif signals is not None:
            first_key = next(iter(signals.keys()))
            n = len(signals[first_key])
        else:
            n = 0

        if n == 0:
            return WalkForwardResults()

        if step_size is None:
            step_size = test_window
        if step_size < 1:
            step_size = 1
        if train_window < min_train_size:
            train_window = min_train_size

        results = WalkForwardResults()
        all_oos_equity = []
        all_oos_trades = []
        combined_equity = [self.config.initial_capital]

        if anchored:
            # Anchored walk-forward: train start fixed at 0
            start_train = 0
        else:
            start_train = 0

        i = 0
        window_idx = 0
        # Walk forward
        if anchored:
            train_start = 0
            while train_start + train_window + test_window <= n or train_start + train_window < n:
                train_end = train_start + train_window
                if train_end >= n:
                    break
                test_start = train_end
                test_end = min(test_start + test_window, n)
                if test_start >= test_end:
                    break
                wf_res = self._run_window(price_series, signals, timestamps, train_start, train_end, test_start, test_end,
                                          purge_eff, embargo_eff)
                results.windows.append(wf_res)
                if wf_res.oos_metrics and wf_res.oos_metrics.equity_curve:
                    # append OOS equity (skip first if concatenating)
                    for eq in wf_res.oos_metrics.equity_curve[1:]:
                        all_oos_equity.append(eq)
                if wf_res.oos_metrics and wf_res.oos_metrics.trades:
                    all_oos_trades.extend(wf_res.oos_metrics.trades)
                train_window += step_size  # expand
                if train_start + train_window >= n:
                    break
                window_idx += 1
                if window_idx > 1000:  # safety
                    break
        else:
            # Rolling walk-forward
            train_start = 0
            while True:
                train_end = train_start + train_window
                if train_end >= n:
                    break
                test_start = train_end
                test_end = min(test_start + test_window, n)
                if test_start >= test_end:
                    break
                wf_res = self._run_window(price_series, signals, timestamps, train_start, train_end, test_start, test_end,
                                          purge_eff, embargo_eff)
                results.windows.append(wf_res)
                if wf_res.oos_metrics and wf_res.oos_metrics.equity_curve:
                    for eq in wf_res.oos_metrics.equity_curve[1:]:
                        all_oos_equity.append(eq)
                if wf_res.oos_metrics and wf_res.oos_metrics.trades:
                    all_oos_trades.extend(wf_res.oos_metrics.trades)
                train_start += step_size
                if train_start + train_window > n:
                    break
                window_idx += 1
                if window_idx > 10000:
                    break

        results.oos_equity_curve = all_oos_equity
        results.oos_trades = all_oos_trades

        # Compute aggregate OOS metrics
        if all_oos_equity:
            # Create temporary engine for metrics calculation
            eng = BacktestEngine(self.config, self.risk_config)
            eng.equity_curve = [self.config.initial_capital] + all_oos_equity if all_oos_equity else [self.config.initial_capital]
            eng.trades = all_oos_trades
            agg = eng.calculate_metrics()
            results.overall_out_of_sample_return = agg.total_return
            results.overall_out_of_sample_sharpe = agg.sharpe_ratio
            results.overall_out_of_sample_max_drawdown = agg.max_drawdown
        else:
            results.overall_out_of_sample_return = 0.0
            results.overall_out_of_sample_sharpe = 0.0
            results.overall_out_of_sample_max_drawdown = 0.0

        # Stability metrics
        if results.windows:
            oos_returns = []
            for w in results.windows:
                if isfinite(w.out_of_sample_return):
                    oos_returns.append(w.out_of_sample_return)
            if oos_returns:
                avg_oos = sum(oos_returns) / len(oos_returns)
                var_oos = _safe_variance(oos_returns, mean=avg_oos)
                std_oos = _safe_std(oos_returns, mean=avg_oos)
                if std_oos > 0 and isfinite(std_oos):
                    results.stability_ratio = abs(avg_oos) / std_oos
                else:
                    results.stability_ratio = float('inf') if avg_oos != 0 else 0.0
            # Degradation: in-sample vs out-of-sample
            is_rets = [w.in_sample_return for w in results.windows if isfinite(w.in_sample_return)]
            if is_rets and oos_returns:
                avg_is = sum(is_rets) / len(is_rets)
                if avg_is != 0:
                    results.degradation = (avg_is - sum(oos_returns) / len(oos_returns)) / abs(avg_is)
                else:
                    results.degradation = 0.0
            else:
                results.degradation = 0.0
        else:
            results.stability_ratio = 0.0
            results.degradation = 0.0

        if not isfinite(results.stability_ratio):
            results.stability_ratio = 0.0
        if not isfinite(results.degradation):
            results.degradation = 0.0

        # Persist the per-run regime coverage audit on the results object so
        # callers can verify which volatility regimes the walk-forward actually
        # exercised (regime-shift auditability).
        results.regime_shift_coverage = dict(self._regime_shift_coverage)
        results.purge_embargo_enforced = bool(purge_eff > 0 or embargo_eff > 0)

        return results

    def _validate_time_ordering(self, timestamps: List[datetime]) -> None:
        """Validate strict time ordering (monotonically increasing timestamps).

        Raises ``ValueError`` if any timestamp is not strictly after the
        previous one, enforcing no lookahead across the walk-forward timeline.
        Naive datetimes are treated as UTC.
        """
        prev: Optional[datetime] = None
        for i, ts in enumerate(timestamps):
            if ts.tzinfo is None:
                ts_norm = ts.replace(tzinfo=timezone.utc)
            else:
                try:
                    ts_norm = ts.astimezone(timezone.utc)
                except Exception:
                    ts_norm = ts
            if prev is not None and ts_norm <= prev:
                raise ValueError(
                    f"Timestamps not strictly increasing at index {i}: {prev.isoformat()} >= {ts_norm.isoformat()}"
                )
            prev = ts_norm

    def verify_determinism(self,
                           price_series: Optional[Dict[str, List[float]]] = None,
                           signals: Optional[Dict[str, List[int]]] = None,
                           timestamps: Optional[List[datetime]] = None,
                           train_window: int = 252,
                           test_window: int = 63,
                           step_size: Optional[int] = None,
                           rolling: bool = True,
                           anchored: bool = False,
                           min_train_size: int = 50,
                           purge: Optional[int] = None,
                           embargo: Optional[int] = None) -> bool:
        """Run the same walk-forward twice and assert byte-identical results.

        Confirms RNG seed determinism (via ``slippage_seed`` in config) is
        propagated through all windows. Returns True if both runs match exactly;
        raises ``AssertionError`` on any divergence.
        """
        r1 = self.run_walk_forward(
            price_series=price_series, signals=signals, timestamps=timestamps,
            train_window=train_window, test_window=test_window, step_size=step_size,
            rolling=rolling, anchored=anchored, min_train_size=min_train_size,
            purge=purge, embargo=embargo,
        )
        r2 = self.run_walk_forward(
            price_series=price_series, signals=signals, timestamps=timestamps,
            train_window=train_window, test_window=test_window, step_size=step_size,
            rolling=rolling, anchored=anchored, min_train_size=min_train_size,
            purge=purge, embargo=embargo,
        )
        s1 = r1.serialize_oos()
        s2 = r2.serialize_oos()
        assert s1 == s2, "Walk-forward results are not deterministic across runs"
        assert len(r1.windows) == len(r2.windows)
        for w1, w2 in zip(r1.windows, r2.windows):
            assert w1.train_start == w2.train_start
            assert w1.train_end == w2.train_end
            assert w1.test_start == w2.test_start
            assert w1.test_end == w2.test_end
            assert w1.in_sample_return == w2.in_sample_return
            assert w1.out_of_sample_return == w2.out_of_sample_return
            assert w1.in_sample_sharpe == w2.in_sample_sharpe
            assert w1.out_of_sample_sharpe == w2.out_of_sample_sharpe
            assert w1.in_sample_max_drawdown == w2.in_sample_max_drawdown
            assert w1.out_of_sample_max_drawdown == w2.out_of_sample_max_drawdown
        return True

    def _run_window(self, price_series: Optional[Dict[str, List[float]]], signals: Optional[Dict[str, List[int]]], timestamps: Optional[List[datetime]], train_start: int, train_end: int, test_start: int, test_end: int, purge: int = 0, embargo: int = 0) -> WalkForwardWindowResult:
        wres = WalkForwardWindowResult(train_start=train_start, train_end=train_end,
                                       test_start=test_start, test_end=test_end)
        wres.purge_applied = int(purge) if isinstance(purge, int) else 0
        wres.embargo_applied = int(embargo) if isinstance(embargo, int) else 0
        # Strict time ordering guard
        if timestamps is not None:
            try:
                self._validate_time_ordering(timestamps)
            except Exception:
                pass
        # Apply purge: shrink train window tail adjacent to test set (regime-shift safe)
        try:
            purge_eff = int(purge) if isinstance(purge, int) else int(purge)
        except Exception:
            purge_eff = 0
        if purge_eff < 0:
            purge_eff = 0
        train_end_purged = train_end - purge_eff
        if train_end_purged < train_start:
            train_end_purged = train_start
        # Apply embargo: shrink test window head adjacent to train set
        try:
            embargo_eff = int(embargo) if isinstance(embargo, int) else int(embargo)
        except Exception:
            embargo_eff = 0
        if embargo_eff < 0:
            embargo_eff = 0
        test_start_embargoed = test_start + embargo_eff
        if test_start_embargoed > test_end:
            test_start_embargoed = test_end
        # Ensure no overlap between train/test windows after purge/embargo
        if train_end_purged > test_start_embargoed and test_start_embargoed >= train_start:
            # Enforce strict separation
            gap = train_end_purged - test_start_embargoed
            if gap >= 0:
                # Push embargo further if purge didn't create enough gap
                test_start_embargoed = min(test_end, train_end_purged + 1)

        # Regime classification for this window (volatility regime from the
        # training price path). Recorded on the window and aggregated into the
        # top-level regime_shift_coverage map so callers can audit which regimes
        # the walk-forward actually exercised. Pure function: no lookahead.
        try:
            if price_series is not None:
                first_key = next(iter(price_series.keys()))
                train_prices = price_series[first_key][train_start:train_end_purged]
                test_prices = price_series[first_key][test_start_embargoed:test_end]
                regime_train = detect_regime_from_window(train_prices)
                regime_test = detect_regime_from_window(test_prices)
                wres.regime_info = {
                    "train_regime": regime_train,
                    "test_regime": regime_test,
                    "train_start": train_start,
                    "train_end": train_end_purged,
                    "test_start": test_start_embargoed,
                    "test_end": test_end,
                }
                self._regime_shift_coverage[regime_test] = self._regime_shift_coverage.get(regime_test, 0) + 1
        except Exception:
            wres.regime_info = None

        # Run in-sample (for metrics)
        is_engine = BacktestEngine(self.config, self.risk_config)
        self._simulate_period(is_engine, price_series, signals, timestamps, train_start, train_end_purged)
        if is_engine.equity_curve:
            is_metrics = is_engine.calculate_metrics()
            wres.is_metrics = is_metrics
            wres.in_sample_return = is_metrics.total_return
            wres.in_sample_sharpe = is_metrics.sharpe_ratio
            wres.in_sample_max_drawdown = is_metrics.max_drawdown
        # Run out-of-sample
        oos_engine = BacktestEngine(self.config, self.risk_config)
        self._simulate_period(oos_engine, price_series, signals, timestamps, test_start_embargoed, test_end)
        if oos_engine.equity_curve:
            oos_metrics = oos_engine.calculate_metrics()
            wres.oos_metrics = oos_metrics
            wres.out_of_sample_return = oos_metrics.total_return
            wres.out_of_sample_sharpe = oos_metrics.sharpe_ratio
            wres.out_of_sample_max_drawdown = oos_metrics.max_drawdown
        return wres

    def _simulate_period(self, engine: BacktestEngine, price_series: Optional[Dict[str, List[float]]], signals: Optional[Dict[str, List[int]]], timestamps: Optional[List[datetime]], start: int, end: int) -> None:
        if start >= end or end < 0:
            return
        end = min(end, 10**12)  # safety
        # Find actual length
        if price_series is not None:
            first_key = next(iter(price_series.keys()))
            n = len(price_series[first_key])
            end = min(end, n)
        elif signals is not None:
            first_key = next(iter(signals.keys()))
            n = len(signals[first_key])
            end = min(end, n)
        else:
            return

        start = max(0, start)
        if start >= end:
            return

        for i in range(start, end):
            # Get prices
            current_prices = {}
            if price_series is not None:
                for sym, prices in price_series.items():
                    if i < len(prices) and isfinite(prices[i]):
                        current_prices[sym] = float(prices[i])
            # Get timestamp
            ts = timestamps[i] if timestamps is not None and i < len(timestamps) else datetime.now(timezone.utc)
            # Process signals
            if signals is not None:
                for sym, sig_list in signals.items():
                    if i >= len(sig_list):
                        continue
                    sig = sig_list[i]
                    if not isfinite(sig):
                        continue
                    if sig == 1 and sym not in engine.positions:  # buy
                        price = current_prices.get(sym)
                        if price is not None and price > 0:
                            try:
                                qty = engine.calculate_position_size(price, side="long")
                                if qty > 0:
                                    engine.execute_trade(sym, qty, price, "buy", ts)
                            except Exception:
                                pass
                    elif sig == -1:  # sell/short
                        price = current_prices.get(sym)
                        if price is not None and price > 0:
                            if sym in engine.positions and engine.positions[sym].side == "long":
                                try:
                                    pos = engine.positions[sym]
                                    engine.execute_trade(sym, pos.quantity, price, "sell", ts)
                                except Exception:
                                    pass
                            elif sym not in engine.positions:
                                try:
                                    qty = engine.calculate_position_size(price, side="short")
                                    if qty > 0:
                                        engine.execute_trade(sym, qty, price, "sell", ts)
                                except Exception:
                                    pass
                    elif sig == 0:
                        pass
            # Update equity
            engine.update_equity_curve(current_prices)
        return


# ---------------------------------------------------------------------------
# Regime-shift aware walk-forward / OOS extension (Phase 8 #5)
# ---------------------------------------------------------------------------

@dataclass
class RegimeShiftConfig:
    """Configuration for regime-shift-aware walk-forward execution/risk extension.

    Defines how market regime transitions (low_vol / normal / high_vol / stress)
    modulate out-of-sample execution costs, risk limits, and position sizing so
    that the OOS path is evaluated under regime-conditional realism rather than
    a single flat cost/limit profile. All numeric fields are finite-guarded.
    """

    regime_labels: List[str] = field(default_factory=lambda: ["low_vol", "normal", "high_vol", "stress"])
    detection_window: int = 20  # rolling window length for volatility regime detection
    vol_thresholds: Tuple[float, float, float] = (0.005, 0.015, 0.03)  # low | normal | high | stress
    cost_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 0.5,
        "normal": 1.0,
        "high_vol": 1.8,
        "stress": 3.0,
    })
    slippage_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 0.5,
        "normal": 1.0,
        "high_vol": 2.0,
        "stress": 4.0,
    })
    fee_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 0.8,
        "normal": 1.0,
        "high_vol": 1.5,
        "stress": 2.0,
    })
    position_size_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 1.0,
        "normal": 1.0,
        "high_vol": 0.7,
        "stress": 0.4,
    })
    max_drawdown_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 1.0,
        "normal": 1.0,
        "high_vol": 0.75,
        "stress": 0.5,
    })
    min_confidence_by_regime: Dict[str, float] = field(default_factory=lambda: {
        "low_vol": 0.3,
        "normal": 0.35,
        "high_vol": 0.45,
        "stress": 0.6,
    })

    def __post_init__(self) -> None:
        if not isinstance(self.detection_window, int) or self.detection_window < 1:
            self.detection_window = 20
        if not isinstance(self.regime_labels, list) or not self.regime_labels:
            self.regime_labels = ["low_vol", "normal", "high_vol", "stress"]
        for name, val in [
            ("vol_thresholds", self.vol_thresholds),
        ]:
            if not isinstance(val, tuple) or len(val) != 3:
                raise OrderError("vol_thresholds must be a 3-tuple", context={"field": name})
            for v in val:
                if not isfinite(float(v)) or float(v) < 0:
                    raise OrderError("vol_threshold entries must be finite and >= 0", context={"field": name, "value": v})
        for dict_name in ["cost_multipliers", "slippage_multipliers", "fee_multipliers",
                          "position_size_multipliers", "max_drawdown_multipliers",
                          "min_confidence_by_regime"]:
            d = getattr(self, dict_name)
            if not isinstance(d, dict):
                raise OrderError(f"{dict_name} must be a dict", context={"field": dict_name})
            for k, v in d.items():
                if not isfinite(float(v)):
                    raise OrderError(f"{dict_name}.{k} must be finite", context={"field": f"{dict_name}.{k}", "value": v})

    def get_multiplier(self, regime: str, kind: str, default: float = 1.0) -> float:
        """Look up a regime-conditional multiplier with a safe default."""
        d = getattr(self, kind + "_multipliers", None) or getattr(self, kind, None)
        if isinstance(d, dict):
            v = d.get(regime)
            if v is not None and isfinite(float(v)):
                return float(v)
        return float(default)


def detect_regime_from_window(
    prices: Sequence[float],
    window: int = 20,
    thresholds: Tuple[float, float, float] = (0.005, 0.015, 0.03),
) -> str:
    """Classify a price window into a volatility regime.

    Computes realized volatility over the trailing ``window`` returns and maps
    it to one of ``low_vol`` / ``normal`` / ``high_vol`` / ``stress`` using the
    provided thresholds. Returns ``"normal"`` for degenerate inputs (fewer than
    2 prices, non-finite values, zero variance). Pure function: no state, no
    lookahead (uses only the supplied historical window).
    """
    if prices is None or len(prices) < 2:
        return "normal"
    valid: List[float] = []
    for p in prices[-window - 1:] if window > 0 else prices:
        try:
            f = float(p)
        except (TypeError, ValueError):
            continue
        if isfinite(f) and f > 0:
            valid.append(f)
    if len(valid) < 2:
        return "normal"
    returns: List[float] = []
    for i in range(1, len(valid)):
        prev = valid[i - 1]
        curr = valid[i]
        if prev == 0:
            continue
        r = (curr - prev) / prev
        if isfinite(r):
            returns.append(r)
    if len(returns) < 2:
        return "normal"
    mean_r = sum(returns) / len(returns)
    var = _safe_variance(returns, mean=mean_r)
    vol = _safe_std(returns, mean=mean_r)
    if not isfinite(vol):
        return "normal"
    low_th, high_th, stress_th = thresholds
    if vol >= stress_th:
        return "stress"
    if vol >= high_th:
        return "high_vol"
    if vol >= low_th:
        return "normal"
    return "low_vol"


# Convenience functions
def run_walk_forward(*args: Any, **kwargs: Any) -> WalkForwardResults:
    # Extract walkforward-specific params
    wf_params = {}
    for k in ['price_series', 'signals', 'timestamps', 'train_window', 'test_window',
              'step_size', 'rolling', 'anchored', 'min_train_size', 'purge', 'embargo']:
        if k in kwargs:
            wf_params[k] = kwargs.pop(k)
    wfb = WalkForwardBacktest(*args, **kwargs)
    return wfb.run_walk_forward(**wf_params)


def run_rolling_window_backtest(*args: Any, **kwargs: Any) -> WalkForwardResults:
    wf_params = {}
    for k in ['price_series', 'signals', 'timestamps', 'train_window', 'test_window',
              'step_size', 'rolling', 'anchored', 'min_train_size', 'purge', 'embargo']:
        if k in kwargs:
            wf_params[k] = kwargs.pop(k)
    wf_params.setdefault('rolling', True)
    wf_params.setdefault('anchored', False)
    wfb = WalkForwardBacktest(*args, **kwargs)
    return wfb.run_walk_forward(**wf_params)


# ---------------------------------------------------------------------------
# Phase 5 — deterministic stress testing (rigorous backtesting)
# ---------------------------------------------------------------------------


@dataclass
class StressScenario:
    """A deterministic backtest stress scenario.

    Fully specifies a price shock path, the signal sequence that drives
    entries/exits, and the engine configuration used to replay it. Each
    scenario is replayed through a fresh :class:`BacktestEngine` so results
    are isolated and deterministic (seeded RNG for partial fills).
    """

    name: str
    symbol: str = "BTC"
    prices: List[float] = field(default_factory=list)
    signals: List[int] = field(default_factory=list)
    timestamps: Optional[List[datetime]] = None
    initial_capital: float = 100000.0
    fee_rate: float = 0.0005
    slippage_bps: float = 1.0
    max_slippage_bps: float = 0.0
    risk_free_rate: float = 0.0
    partial_fill_rate: float = 0.0
    round_lot_size: float = 0.0
    slippage_seed: int = 42
    max_position_pct: float = 0.1
    max_drawdown_limit: float = 0.2
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    max_position_qty: float = 0.0
    allow_shorting: bool = True


@dataclass
class StressTestResult:
    """Outcome of replaying one :class:`StressScenario`."""

    name: str
    passed: bool
    violations: List[str] = field(default_factory=list)
    total_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    total_trades: int = 0
    equity_final: float = 0.0
    finite: bool = False
    serializable: bool = False
    positions_flat: bool = True


def run_stress_scenario(scenario: StressScenario) -> StressTestResult:
    """Replay a deterministic stress scenario through a fresh engine.

    Prices are applied strictly in order (no-lookahead by construction).
    ``signals`` drive entries/exits: ``1`` buys/opens a long, ``-1`` sells or
    opens a short, ``0`` holds. Stop-loss/take-profit/drawdown risk controls
    are enforced on every tick via :meth:`BacktestEngine.update_equity_curve`.

    Validates numerical stability (finite equity/metrics), serialization
    safety (``serialize_metrics_strict`` does not raise), round-lot and
    partial-fill invariants, and that realized drawdown stays within the
    scenario limit.
    """
    violations: List[str] = []
    config = BacktestConfig(
        initial_capital=scenario.initial_capital,
        fee_rate=scenario.fee_rate,
        slippage_bps=scenario.slippage_bps,
        max_slippage_bps=scenario.max_slippage_bps,
        risk_free_rate=scenario.risk_free_rate,
        partial_fill_rate=scenario.partial_fill_rate,
        round_lot_size=scenario.round_lot_size,
        slippage_seed=scenario.slippage_seed,
    )
    risk_config = RiskConfig(
        max_position_pct=scenario.max_position_pct,
        max_drawdown_limit=scenario.max_drawdown_limit,
        stop_loss_pct=scenario.stop_loss_pct,
        take_profit_pct=scenario.take_profit_pct,
        max_position_qty=scenario.max_position_qty,
        allow_shorting=scenario.allow_shorting,
    )
    engine = BacktestEngine(config=config, risk_config=risk_config)

    symbol = scenario.symbol
    prices = scenario.prices
    signals = scenario.signals
    n = len(prices)
    if n == 0:
        return StressTestResult(
            name=scenario.name,
            passed=False,
            violations=["stress scenario has no price path"],
        )

    if scenario.timestamps is not None and len(scenario.timestamps) == n:
        timestamps = scenario.timestamps
    else:
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        timestamps = [base + timedelta(minutes=i) for i in range(n)]

    # Intended entry quantities recorded per entry trade so partial-fill and
    # round-lot invariants can be verified against the fill actually returned.
    intended_qty: List[float] = []

    try:
        for i in range(n):
            price = float(prices[i])
            if not isfinite(price) or price <= 0:
                violations.append(f"non-finite or non-positive price at index {i}: {price!r}")
                price = 50000.0
            sig = int(signals[i]) if i < len(signals) else 0
            ts = timestamps[i]
            current_prices = {symbol: price}

            if sig == 1 and symbol not in engine.positions:
                qty = engine.calculate_position_size(price, side="long")
                intended_qty.append(qty)
                if qty > 0:
                    engine.execute_trade(symbol, qty, price, "buy", ts)
            elif sig == -1:
                if symbol in engine.positions and engine.positions[symbol].side == "long":
                    pos = engine.positions[symbol]
                    engine.execute_trade(symbol, pos.quantity, price, "sell", ts)
                elif symbol not in engine.positions and scenario.allow_shorting:
                    qty = engine.calculate_position_size(price, side="short")
                    intended_qty.append(qty)
                    if qty > 0:
                        engine.execute_trade(symbol, qty, price, "sell", ts)

            # Enforce SL/TP and drawdown controls on every tick; may execute
            # exit trades which append to engine.trades.
            engine.update_equity_curve(current_prices)
    except Exception as e:  # keep the suite reporting violations instead of crashing
        violations.append(f"engine raised {type(e).__name__} during replay: {e}")

    # --- Invariant: numerical stability ---
    equity_curve = [float(v) for v in engine.equity_curve]
    finite_equity = all(isfinite(v) for v in equity_curve)
    if not finite_equity:
        violations.append("equity curve contains a non-finite value")

    metrics = engine.calculate_metrics()
    scalar_fields = {
        "total_return": metrics.total_return,
        "sharpe_ratio": metrics.sharpe_ratio,
        "sortino_ratio": metrics.sortino_ratio,
        "max_drawdown": metrics.max_drawdown,
        "calmar_ratio": metrics.calmar_ratio,
        "win_rate": metrics.win_rate,
    }
    scalar_finite = all(isfinite(float(v)) for v in scalar_fields.values())
    pf_finite = isfinite(float(metrics.profit_factor))
    finite = finite_equity and scalar_finite and pf_finite
    if not finite:
        violations.append("one or more backtest metrics are non-finite")

    # Drawdown must stay within the scenario limit (risk controls enforced).
    dd_limit = float(scenario.max_drawdown_limit)
    if metrics.max_drawdown > dd_limit + 1e-9:
        violations.append(
            f"max drawdown {metrics.max_drawdown:.6f} exceeds limit {dd_limit:.6f}"
        )

    # Round-lot invariant: every intended entry fill is a multiple of the lot.
    lot_size = float(getattr(config, "round_lot_size", 0.0))
    if lot_size > 0:
        for q in intended_qty:
            if q <= 0:
                continue
            remainder = q % lot_size
            if not (isfinite(remainder) and abs(remainder) < 1e-9):
                violations.append(f"entry quantity {q} not a multiple of lot size {lot_size}")

    # Partial-fill invariant: filled quantity never exceeds intended quantity
    # and stays positive when a partial-fill rate is configured.
    pfr = float(getattr(config, "partial_fill_rate", 0.0))
    if pfr > 0:
        for intended, trade in zip(intended_qty, engine.trades[: len(intended_qty)]):
            if not (0.0 < trade.quantity <= intended + 1e-9):
                violations.append(
                    f"partial fill {trade.quantity} out of range for intended {intended}"
                )

    # --- Invariant: serialization safety (allow_nan=False) ---
    serializable = True
    payload: Dict[str, Any] = {
        "total_return": metrics.total_return,
        "sharpe_ratio": metrics.sharpe_ratio,
        "sortino_ratio": metrics.sortino_ratio,
        "max_drawdown": metrics.max_drawdown,
        "calmar_ratio": metrics.calmar_ratio,
        "win_rate": metrics.win_rate,
        "profit_factor": metrics.profit_factor if pf_finite else 0.0,
        "total_trades": metrics.total_trades,
        "equity_final": float(engine.equity_curve[-1]) if engine.equity_curve else float(config.initial_capital),
    }
    try:
        serialize_metrics_strict(payload)
    except SerializationError:
        serializable = False
        violations.append("metrics payload failed strict serialization (allow_nan=False)")

    positions_flat = len(engine.positions) == 0
    passed = len(violations) == 0

    return StressTestResult(
        name=scenario.name,
        passed=passed,
        violations=violations,
        total_return=float(metrics.total_return),
        max_drawdown=float(metrics.max_drawdown),
        sharpe_ratio=float(metrics.sharpe_ratio),
        sortino_ratio=float(metrics.sortino_ratio),
        total_trades=metrics.total_trades,
        equity_final=float(engine.equity_curve[-1]) if engine.equity_curve else float(config.initial_capital),
        finite=finite,
        serializable=serializable,
        positions_flat=positions_flat,
    )


def crash_scenario() -> StressScenario:
    """Sustained price crash: long opened then price falls ~40%; stop-loss and
    drawdown controls must bound the loss and keep metrics finite/serializable."""
    prices = [50000.0] * 3 + [49900.0, 49500.0, 49000.0, 48000.0, 46000.0, 44000.0, 40000.0, 35000.0, 30000.0] + [30000.0] * 5
    signals = [1] + [0] * (len(prices) - 1)
    return StressScenario(
        name="crash",
        prices=prices,
        signals=signals,
        max_drawdown_limit=0.2,
        stop_loss_pct=0.02,
    )


def gap_down_scenario() -> StressScenario:
    """Overnight gap down: long gapped through its stop loss; execution fills
    at the gap price, position closed, metrics finite and serializable."""
    prices = [50000.0] * 4 + [44000.0, 44500.0, 45000.0, 46000.0]
    signals = [1] + [0] * (len(prices) - 1)
    return StressScenario(
        name="gap_down",
        prices=prices,
        signals=signals,
        max_drawdown_limit=0.2,
        stop_loss_pct=0.02,
    )


def vol_spike_scenario() -> StressScenario:
    """Volatility spike / whipsaw: rapid price oscillations with alternating
    signals generate turnover; slippage and fees applied, metrics stable."""
    n = 40
    prices = [50000.0, 48000.0] + [50000.0 * (1.0 + (0.015 if i % 4 == 0 else -0.015 if i % 4 == 2 else 0.0)) for i in range(2, n)]
    signals = [0] * n
    signals[0] = 1   # buy at 50000
    signals[1] = -1  # sell at 48000 -> guaranteed loss
    for i in range(5, n, 4):
        signals[i] = 1
        if i + 1 < n:
            signals[i + 1] = -1
    return StressScenario(
        name="vol_spike",
        prices=prices,
        signals=signals,
        max_drawdown_limit=0.2,
        slippage_bps=5.0,
    )


def liquidity_crunch_scenario() -> StressScenario:
    """Liquidity crunch: partial fills, round lots, and elevated slippage with
    a cap; uptrend then reversal forces a stop-loss loss so metrics stay finite."""
    n = 40
    up = [50000.0 + i * 125.0 for i in range(20)]          # 50000 -> 52375
    down = [52375.0 - (i - 19) * 418.75 for i in range(20, 40)]  # 52375 -> ~44000
    prices = up + down
    signals = [1] + [0] * (n - 1)  # buy once at start, hold; stop triggers on crash
    return StressScenario(
        name="liquidity_crunch",
        prices=prices,
        signals=signals,
        max_drawdown_limit=0.2,
        stop_loss_pct=0.02,
        take_profit_pct=1.0,  # never hit; stop-loss on the crash drives the close
        partial_fill_rate=0.5,
        round_lot_size=0.01,
        slippage_bps=50.0,
        max_slippage_bps=100.0,
        slippage_seed=7,
    )


def all_stress_scenarios() -> List[StressScenario]:
    """All deterministic stress scenarios (gap, crash, vol spike, liquidity crunch)."""
    return [crash_scenario(), gap_down_scenario(), vol_spike_scenario(), liquidity_crunch_scenario()]


def run_deterministic_stress_suite() -> List[StressTestResult]:
    """Run every stress scenario and return per-scenario results."""
    return [run_stress_scenario(s) for s in all_stress_scenarios()]


class PortfolioWalkForwardBacktest:
    """Portfolio-level walk-forward orchestrator with correlation constraints."""

    def __init__(
        self,
        engine: Optional[BacktestEngine] = None,
        config: Optional[BacktestConfig] = None,
        risk_config: Optional[RiskConfig] = None,
        purge: int = 0,
        embargo: int = 0,
        correlation_window: int = 60,
        max_correlation: float = 0.7,
        regime_costs: Optional[Dict[str, float]] = None,
        **kwargs: Any,
    ) -> None:
        if engine is not None and not isinstance(engine, BacktestEngine):
            if isinstance(engine, BacktestConfig):
                if config is None or isinstance(config, RiskConfig):
                    risk_config = config
                config = engine
                engine = None
        if engine is not None and isinstance(engine, BacktestEngine):
            self.engine_template = engine
            self.config = getattr(engine, "config", config or BacktestConfig())
            self.risk_config = getattr(engine, "risk_config", risk_config or RiskConfig())
        else:
            if config is None and kwargs:
                cfg_kwargs = {k: v for k, v in kwargs.items() if k in BacktestConfig.__dataclass_fields__}
                if cfg_kwargs:
                    config = BacktestConfig(**cfg_kwargs)
            if risk_config is None and kwargs:
                risk_kwargs = {k: v for k, v in kwargs.items() if k in RiskConfig.__dataclass_fields__}
                if risk_kwargs:
                    risk_config = RiskConfig(**risk_kwargs)
            self.config = config if isinstance(config, BacktestConfig) else BacktestConfig()
            self.risk_config = risk_config if isinstance(risk_config, RiskConfig) else RiskConfig()
            self.engine_template = BacktestEngine(self.config, self.risk_config)

        purge = purge if isinstance(purge, int) and purge >= 0 else 0
        embargo = embargo if isinstance(embargo, int) and embargo >= 0 else 0
        self.purge = purge
        self.embargo = embargo
        self.correlation_window = max(10, int(correlation_window))
        self.max_correlation = float(max_correlation)
        if not isfinite(self.max_correlation):
            self.max_correlation = 0.7
        self.max_correlation = max(0.0, min(0.99, self.max_correlation))
        # Regime-dependent costs/slippage mapping (deterministic)
        self.regime_costs = regime_costs or {
            "low_vol": 0.0001,
            "normal": 0.0002,
            "high_vol": 0.0005,
            "stress": 0.0010,
        }

    def _validate_time_ordering(self, timestamps: List[datetime]) -> None:
        prev: Optional[datetime] = None
        for i, ts in enumerate(timestamps):
            if ts.tzinfo is None:
                ts_norm = ts.replace(tzinfo=timezone.utc)
            else:
                try:
                    ts_norm = ts.astimezone(timezone.utc)
                except Exception:
                    ts_norm = ts
            if prev is not None and ts_norm <= prev:
                raise ValueError(
                    f"Timestamps not strictly increasing at index {i}: {prev.isoformat()} >= {ts_norm.isoformat()}"
                )
            prev = ts_norm

    def _estimate_correlation_matrix(self, price_series: Dict[str, List[float]], start: int, end: int) -> Optional[List[List[float]]]:
        if price_series is None or len(price_series) < 2:
            return None
        symbols = list(price_series.keys())
        n_syms = len(symbols)
        # Build return matrix over window
        window_returns: Dict[str, List[float]] = {s: [] for s in symbols}
        # Use rolling window ending at end-1
        w_start = max(start, end - self.correlation_window)
        for s in symbols:
            prices = price_series[s]
            for i in range(w_start + 1, end):
                if i < 1:
                    continue
                p0 = prices[i - 1]
                p1 = prices[i]
                if isfinite(p0) and p0 != 0 and isfinite(p1):
                    window_returns[s].append((p1 / p0) - 1.0)
        # If different lengths, align to min
        min_len = min((len(v) for v in window_returns.values()), default=0)
        if min_len < 5:
            # Return identity-like matrix
            mat = [[1.0 if i == j else 0.0 for j in range(n_syms)] for i in range(n_syms)]
            return mat
        # Compute correlation
        if _np is not None:
            try:
                R_list = []
                for s in symbols:
                    R_list.append(window_returns[s][:min_len])
                arr = _np.array(R_list)  # type: ignore
                # z-score
                means_arr = arr.mean(axis=1, keepdims=True)  # type: ignore
                stds_arr = arr.std(axis=1, keepdims=True)  # type: ignore
                stds_arr = _np.where(stds_arr < 1e-18, 1e-18, stds_arr)  # type: ignore
                Z_arr = (arr - means_arr) / stds_arr  # type: ignore
                C_arr = (Z_arr @ Z_arr.T) / float(min_len)  # type: ignore
                try:
                    w_e, V_e = _np.linalg.eigh(C_arr)  # type: ignore
                    w_clipped = _np.maximum(w_e, 1e-12)  # type: ignore
                    C_psd = V_e @ _np.diag(w_clipped) @ V_e.T  # type: ignore
                    d_arr = _np.sqrt(_np.diag(C_psd))  # type: ignore
                    d_arr = _np.where(d_arr < 1e-18, 1e-18, d_arr)  # type: ignore
                    C_psd = C_psd / (d_arr[:, None] * d_arr[None, :])  # type: ignore
                    C_out_list: List[List[float]] = [[0.0] * n_syms for _ in range(n_syms)]
                    for _i in range(n_syms):
                        for _j in range(n_syms):
                            C_out_list[_i][_j] = float(C_psd[_i, _j])  # type: ignore[index]
                except Exception:
                    C_out_list = [[float(C_arr[_i, _j]) for _j in range(n_syms)] for _i in range(n_syms)]  # type: ignore[index]
                for i in range(n_syms):
                    C_out_list[i][i] = 1.0
                    for j in range(n_syms):
                        if i != j:
                            val = float(C_out_list[i][j])
                            if val > self.max_correlation:
                                val = self.max_correlation
                            elif val < -self.max_correlation:
                                val = -self.max_correlation
                            if not isfinite(val):
                                val = 0.0
                            C_out_list[i][j] = val
                            C_out_list[j][i] = val
                return C_out_list
            except Exception:
                pass
        # Fallback pure Python
        means = {}
        stds = {}
        for s in symbols:
            vals = window_returns[s][:min_len]
            m = sum(vals) / len(vals)
            means[s] = m
            var = _safe_variance(vals, mean=m)
            stds[s] = _safe_std(vals, mean=m)
        mat_res = [[0.0] * n_syms for _ in range(n_syms)]
        for i, si in enumerate(symbols):
            mat_res[i][i] = 1.0
            for j in range(i + 1, n_syms):
                sj = symbols[j]
                vi = window_returns[si][:min_len]
                vj = window_returns[sj][:min_len]
                mi, mj = means[si], means[sj]
                si_std, sj_std = stds[si], stds[sj]
                if si_std < 1e-18 or sj_std < 1e-18:
                    cov = 0.0
                else:
                    cov = sum((vi[k] - mi) * (vj[k] - mj) for k in range(min_len)) / min_len
                corr = cov / (si_std * sj_std)
                if not isfinite(corr):
                    corr = 0.0
                if corr > self.max_correlation:
                    corr = self.max_correlation
                elif corr < -self.max_correlation:
                    corr = -self.max_correlation
                mat_res[i][j] = corr
                mat_res[j][i] = corr
        return mat_res

    def _get_regime_for_window(self, regime: Optional[str] = None) -> str:
        if regime is None:
            return "normal"
        if isinstance(regime, str) and regime in self.regime_costs:
            return regime
        return "normal"

    def run_portfolio_walk_forward(
        self,
        price_series: Dict[str, List[float]],
        signals: Optional[Dict[str, List[int]]] = None,
        timestamps: Optional[List[datetime]] = None,
        train_window: int = 252,
        test_window: int = 63,
        step_size: Optional[int] = None,
        rolling: bool = True,
        anchored: bool = False,
        min_train_size: int = 50,
        purge: Optional[int] = None,
        embargo: Optional[int] = None,
        regime: Optional[str] = None,
        correlation_constraint: bool = True,
        **kwargs: Any,
    ) -> PortfolioWalkForwardResults:
        if price_series is None or len(price_series) == 0:
            raise ValueError("price_series required for portfolio walk-forward")
        if timestamps is not None:
            self._validate_time_ordering(timestamps)

        purge_eff = self.purge if purge is None else purge
        embargo_eff = self.embargo if embargo is None else embargo
        if not isinstance(purge_eff, int) or purge_eff < 0:
            purge_eff = 0
        if not isinstance(embargo_eff, int) or embargo_eff < 0:
            embargo_eff = 0

        symbols = list(price_series.keys())
        first_key = symbols[0]
        n = len(price_series[first_key])
        for s in symbols:
            if len(price_series[s]) != n:
                raise ValueError("All price series must have same length")

        if step_size is None:
            step_size = test_window
        if step_size < 1:
            step_size = 1
        if train_window < min_train_size:
            train_window = min_train_size

        results = PortfolioWalkForwardResults()
        all_oos_equity: List[float] = []
        all_oos_trades: List[Trade] = []

        regime_name = self._get_regime_for_window(regime)
        regime_cost_mult = 1.0 + float(self.regime_costs.get(regime_name, 0.0002)) * 1000.0  # scale effect
        # Apply regime-dependent costs to config copy
        cfg = BacktestConfig(
            initial_capital=getattr(self.config, "initial_capital", 100000.0),
            fee_rate=(self.config.fee_rate * regime_cost_mult) if isfinite(self.config.fee_rate) else self.config.fee_rate,
            slippage_bps=(self.config.slippage_bps * regime_cost_mult) if isfinite(self.config.slippage_bps) else self.config.slippage_bps,
            max_slippage_bps=getattr(self.config, "max_slippage_bps", 0.0),
            slippage_seed=getattr(self.config, "slippage_seed", 42),
            round_lot_size=getattr(self.config, "round_lot_size", 0.0),
            partial_fill_rate=getattr(self.config, "partial_fill_rate", 0.0),
        )

        if anchored:
            train_start = 0
            window_idx = 0
            while True:
                train_end = train_start + train_window
                if train_end >= n:
                    break
                test_start = train_end
                test_end = min(test_start + test_window, n)
                if test_start >= test_end:
                    break
                pwres = self._run_portfolio_window(
                    price_series, signals, timestamps, train_start, train_end, test_start, test_end,
                    purge_eff, embargo_eff, cfg, correlation_constraint
                )
                results.windows.append(pwres)
                if pwres.oos_metrics and pwres.oos_metrics.equity_curve:
                    for eq in pwres.oos_metrics.equity_curve[1:]:
                        if isfinite(eq):
                            all_oos_equity.append(eq)
                if pwres.oos_metrics and pwres.oos_metrics.trades:
                    all_oos_trades.extend(pwres.oos_metrics.trades)
                train_window += step_size
                if train_start + train_window >= n:
                    break
                window_idx += 1
                if window_idx > 1000:
                    break
        else:
            train_start = 0
            window_idx = 0
            while True:
                train_end = train_start + train_window
                if train_end >= n:
                    break
                test_start = train_end
                test_end = min(test_start + test_window, n)
                if test_start >= test_end:
                    break
                pwres = self._run_portfolio_window(
                    price_series, signals, timestamps, train_start, train_end, test_start, test_end,
                    purge_eff, embargo_eff, cfg, correlation_constraint
                )
                results.windows.append(pwres)
                if pwres.oos_metrics and pwres.oos_metrics.equity_curve:
                    for eq in pwres.oos_metrics.equity_curve[1:]:
                        if isfinite(eq):
                            all_oos_equity.append(eq)
                if pwres.oos_metrics and pwres.oos_metrics.trades:
                    all_oos_trades.extend(pwres.oos_metrics.trades)
                train_start += step_size
                if train_start + train_window > n:
                    break
                window_idx += 1
                if window_idx > 10000:
                    break

        results.oos_equity_curve = all_oos_equity
        results.oos_trades = all_oos_trades

        if all_oos_equity:
            eng = BacktestEngine(cfg, self.risk_config)
            eng.equity_curve = [cfg.initial_capital] + all_oos_equity
            eng.trades = all_oos_trades
            agg = eng.calculate_metrics()
            results.overall_out_of_sample_return = agg.total_return
            results.overall_out_of_sample_sharpe = agg.sharpe_ratio
            results.overall_out_of_sample_max_drawdown = agg.max_drawdown
        else:
            results.overall_out_of_sample_return = 0.0
            results.overall_out_of_sample_sharpe = 0.0
            results.overall_out_of_sample_max_drawdown = 0.0

        if results.windows:
            oos_returns = []
            for w in results.windows:
                if isfinite(w.out_of_sample_return):
                    oos_returns.append(w.out_of_sample_return)
            if oos_returns:
                avg_oos = sum(oos_returns) / len(oos_returns)
                var_oos = _safe_variance(oos_returns, mean=avg_oos)
                std_oos = _safe_std(oos_returns, mean=avg_oos)
                if std_oos > 0 and isfinite(std_oos):
                    results.stability_ratio = abs(avg_oos) / std_oos
                else:
                    results.stability_ratio = float('inf') if avg_oos != 0 else 0.0
            is_rets = [w.in_sample_return for w in results.windows if isfinite(w.in_sample_return)]
            if is_rets and oos_returns:
                avg_is = sum(is_rets) / len(is_rets)
                if avg_is != 0:
                    results.degradation = (avg_is - sum(oos_returns) / len(oos_returns)) / abs(avg_is)
                else:
                    results.degradation = 0.0
            else:
                results.degradation = 0.0
        else:
            results.stability_ratio = 0.0
            results.degradation = 0.0

        if not isfinite(results.stability_ratio):
            results.stability_ratio = 0.0
        if not isfinite(results.degradation):
            results.degradation = 0.0

        return results

    def _run_portfolio_window(
        self,
        price_series: Dict[str, List[float]],
        signals: Optional[Dict[str, List[int]]],
        timestamps: Optional[List[datetime]],
        train_start: int,
        train_end: int,
        test_start: int,
        test_end: int,
        purge: int,
        embargo: int,
        cfg: BacktestConfig,
        correlation_constraint: bool,
    ) -> PortfolioWalkForwardWindowResult:
        symbols = list(price_series.keys())
        pwres = PortfolioWalkForwardWindowResult(
            train_start=train_start,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            symbols=symbols,
        )
        train_end_purged = max(train_start, train_end - purge)
        test_start_embargoed = min(test_end, test_start + embargo)

        # Estimate correlation matrix for window
        if correlation_constraint and len(symbols) >= 2:
            try:
                corr_mat = self._estimate_correlation_matrix(price_series, train_start, train_end_purged)
                pwres.correlation_matrix = corr_mat
            except Exception:
                pwres.correlation_matrix = None
        else:
            pwres.correlation_matrix = None

        # In-sample
        is_engine = BacktestEngine(cfg, self.risk_config)
        self._simulate_portfolio_period(is_engine, price_series, signals, timestamps, train_start, train_end_purged, correlation_constraint)
        if is_engine.equity_curve:
            is_metrics = is_engine.calculate_metrics()
            pwres.is_metrics = is_metrics
            pwres.in_sample_return = is_metrics.total_return
            pwres.in_sample_sharpe = is_metrics.sharpe_ratio
            pwres.in_sample_max_drawdown = is_metrics.max_drawdown

        # Out-of-sample
        oos_engine = BacktestEngine(cfg, self.risk_config)
        self._simulate_portfolio_period(oos_engine, price_series, signals, timestamps, test_start_embargoed, test_end, correlation_constraint)
        if oos_engine.equity_curve:
            oos_metrics = oos_engine.calculate_metrics()
            pwres.oos_metrics = oos_metrics
            pwres.out_of_sample_return = oos_metrics.total_return
            pwres.out_of_sample_sharpe = oos_metrics.sharpe_ratio
            pwres.out_of_sample_max_drawdown = oos_metrics.max_drawdown

        return pwres

    def _simulate_portfolio_period(
        self,
        engine: BacktestEngine,
        price_series: Dict[str, List[float]],
        signals: Optional[Dict[str, List[int]]],
        timestamps: Optional[List[datetime]],
        start: int,
        end: int,
        correlation_constraint: bool,
    ) -> None:
        if start >= end or end < 0:
            return
        symbols = list(price_series.keys())
        first_key = symbols[0]
        n = len(price_series[first_key])
        end = min(end, n)
        start = max(0, start)
        if start >= end:
            return

        for i in range(start, end):
            current_prices: Dict[str, float] = {}
            for sym in symbols:
                prices = price_series[sym]
                if i < len(prices) and isfinite(prices[i]) and prices[i] > 0:
                    current_prices[sym] = float(prices[i])
            ts = timestamps[i] if timestamps is not None and i < len(timestamps) else datetime.now(timezone.utc)

            if signals is not None:
                for sym in symbols:
                    sig_list = signals.get(sym)
                    if sig_list is None or i >= len(sig_list):
                        continue
                    sig = sig_list[i]
                    if not isfinite(sig):
                        continue
                    price = current_prices.get(sym)
                    if price is None or price <= 0:
                        continue
                    if sig == 1 and sym not in engine.positions:
                        try:
                            qty = engine.calculate_position_size(price, side="long")
                            # Apply correlation constraint: if too correlated exposure, scale down
                            if correlation_constraint and len(engine.positions) > 0 and len(symbols) > 1:
                                # Simple diversification guard - reduce size if many correlated positions
                                if len(engine.positions) >= 2:
                                    qty = qty * 0.5  # conservative scaling to prevent over-concentration
                                    if qty < 1e-18:
                                        qty = 0.0
                            if qty > 0 and isfinite(qty):
                                engine.execute_trade(sym, qty, price, "buy", ts)
                        except Exception:
                            pass
                    elif sig == -1:
                        try:
                            if sym in engine.positions and engine.positions[sym].side == "long":
                                pos = engine.positions[sym]
                                engine.execute_trade(sym, pos.quantity, price, "sell", ts)
                            elif sym not in engine.positions:
                                qty = engine.calculate_position_size(price, side="short")
                                if correlation_constraint and len(engine.positions) >= 2:
                                    qty = qty * 0.5
                                    if qty < 1e-18:
                                        qty = 0.0
                                if qty > 0 and isfinite(qty):
                                    engine.execute_trade(sym, qty, price, "sell", ts)
                        except Exception:
                            pass
            engine.update_equity_curve(current_prices)


def run_portfolio_walk_forward(*args: Any, **kwargs: Any) -> PortfolioWalkForwardResults:
    wf_params = {}
    for k in [
        'price_series', 'signals', 'timestamps', 'train_window', 'test_window',
        'step_size', 'rolling', 'anchored', 'min_train_size', 'purge', 'embargo',
        'regime', 'correlation_constraint'
    ]:
        if k in kwargs:
            wf_params[k] = kwargs.pop(k)
    # Also allow positional price_series
    if args and 'price_series' not in wf_params and isinstance(args[0], dict):
        wf_params['price_series'] = args[0]
        args = args[1:]
    pwfb = PortfolioWalkForwardBacktest(*args, **kwargs)
    price_series = wf_params.pop('price_series')
    return pwfb.run_portfolio_walk_forward(price_series=price_series, **wf_params)
