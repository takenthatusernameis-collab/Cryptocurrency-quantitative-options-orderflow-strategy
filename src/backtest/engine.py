"""Event-driven backtesting engine."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Dict, List, Optional

from ..config import BacktestConfig, RiskConfig


@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    side: str  # 'long' or 'short'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Trade:
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


class BacktestEngine:
    def __init__(self, config: BacktestConfig = None, risk_config: RiskConfig = None, **kwargs):
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
        self.initial_capital = float(getattr(config, "initial_capital", 100000.0))
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
            self._rng = random.Random(int(seed) if seed is not None else 42)
        except Exception:
            import random

            self._rng = random.Random(42)

    def _apply_slippage(self, price: float, side: str) -> float:
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
        fee_rate = getattr(self.config, "fee_rate", 0.0)
        return float(notional) * float(fee_rate)

    def calculate_position_size(self, price: float, side: str = "long", risk_pct: float = None) -> float:
        """Calculate position size based on risk limits."""
        risk_pct = risk_pct if risk_pct is not None else getattr(self.risk_config, "stop_loss_pct", 0.02)
        max_position_pct = getattr(self.risk_config, "max_position_pct", 0.1)
        max_capital = self.cash * max_position_pct

        # Risk-based sizing
        risk_amount = self.initial_capital * risk_pct
        qty_by_risk = risk_amount / price if price > 0 else 0

        # Limit by max position size
        qty_by_capital = max_capital / price if price > 0 else 0

        qty = min(qty_by_risk, qty_by_capital)
        if qty < 0:
            qty = 0
        return qty

    def execute_trade(self, symbol: str, quantity: float, price: float, side: str, timestamp: datetime,
                      stop_loss: float = None, take_profit: float = None) -> Trade:
        """Execute a trade with fees, slippage, short selling support."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        qty = float(quantity)
        # Apply lot rounding if configured
        lot_size = getattr(self.config, "round_lot_size", 0.0)
        if lot_size and lot_size > 0 and isfinite(lot_size):
            # round down to nearest lot
            qty = (qty // lot_size) * lot_size
            if qty <= 0:
                raise ValueError("Quantity must be positive after lot rounding")

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
                raise ValueError("Quantity must be positive after partial fill")

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
                    raise ValueError("Insufficient cash")
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
                    raise ValueError("Short selling not allowed")
                max_position_pct = getattr(self.risk_config, "max_position_pct", 0.1)
                max_notional = self.cash * max_position_pct
                if notional > max_notional + 1e-10:
                    raise ValueError(f"Short notional {notional} exceeds max_position_pct limit {max_notional}")
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
            raise ValueError(f"Invalid side: {side}")

        self.trades.append(trade)
        return trade

    def check_risk_controls(self, current_prices: Dict[str, float], timestamp: datetime) -> List[Trade]:
        """Check stop-loss and take-profit conditions."""
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

    def update_equity_curve(self, current_prices: Dict[str, float] = None):
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
        """Calculate current equity.

        For longs: equity = cash + qty * current_price (cash was debited at open).
        For shorts: cash was *credited* with proceeds (qty * entry_price) at open,
        so the only remaining liability is qty * current_price. We subtract it
        rather than adding an unrealized PnL term, which would double-count the
        proceeds already sitting in cash.
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
        """Calculate performance metrics."""
        if not self.equity_curve:
            return BacktestResults()

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
            var = sum((r - avg_return) ** 2 for r in returns) / len(returns)
            std_return = var ** 0.5 if var >= 0 else 0.0
            if std_return > 0 and isfinite(std_return):
                sharpe_ratio = (avg_return - risk_free_rate / 252.0) / std_return * (252.0 ** 0.5)
            else:
                sharpe_ratio = 0.0
            # Sortino
            downside = [r for r in returns if r < 0 and isfinite(r)]
            if downside:
                downside_var = sum((r) ** 2 for r in downside) / len(downside)
                downside_std = downside_var ** 0.5 if downside_var >= 0 else 0.0
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

        return BacktestResults(
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
