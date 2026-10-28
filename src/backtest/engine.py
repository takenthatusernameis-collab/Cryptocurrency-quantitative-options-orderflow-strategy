"""Event-driven backtesting engine."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from ..config import BacktestConfig


@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    side: str  # 'long' or 'short'


@dataclass
class Trade:
    symbol: str
    quantity: float
    price: float
    side: str  # 'buy' or 'sell'
    timestamp: datetime
    commission: float = 0.0


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


class BacktestEngine:
    def __init__(self, config: BacktestConfig = None, **kwargs):
        if config is None and kwargs:
            # Build config from kwargs
            config = BacktestConfig(**kwargs)
        elif config is None:
            config = BacktestConfig()
        self.config = config
        self.initial_capital = getattr(config, "initial_capital", 100000.0)
        self.cash = self.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [self.initial_capital]

    def execute_trade(self, symbol: str, quantity: float, price: float, side: str, timestamp: datetime) -> Trade:
        """Execute a trade with fees and slippage."""
        slippage = getattr(self.config, "slippage_bps", 0) / 10000.0
        if side == "buy":
            execution_price = price * (1 + slippage)
        else:
            execution_price = price * (1 - slippage)

        fee_rate = getattr(self.config, "fee_rate", 0.0)
        notional = quantity * execution_price
        commission = notional * fee_rate

        trade = Trade(
            symbol=symbol,
            quantity=quantity,
            price=execution_price,
            side=side,
            timestamp=timestamp,
            commission=commission,
        )

        if side == "buy":
            cost = notional + commission
            if cost > self.cash:
                raise ValueError("Insufficient cash")
            self.cash -= cost
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=execution_price,
                entry_time=timestamp,
                side="long",
            )
        else:  # sell
            if symbol not in self.positions:
                # Allow short selling if not present? For now follow existing behavior but be flexible
                raise ValueError("No position to sell")
            proceeds = notional - commission
            self.cash += proceeds
            del self.positions[symbol]

        self.trades.append(trade)
        return trade

    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """Calculate current equity."""
        equity = self.cash
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                if pos.side == "long":
                    equity += pos.quantity * current_prices[symbol]
                else:
                    equity -= pos.quantity * current_prices[symbol]
        return equity

    def calculate_metrics(self) -> BacktestResults:
        """Calculate performance metrics."""
        if not self.equity_curve:
            return BacktestResults()

        total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital if self.initial_capital != 0 else 0.0

        returns = []
        for i in range(1, len(self.equity_curve)):
            prev = self.equity_curve[i - 1]
            if prev == 0:
                continue
            ret = (self.equity_curve[i] - prev) / prev
            returns.append(ret)

        risk_free_rate = getattr(self.config, "risk_free_rate", 0.0)
        if returns:
            avg_return = sum(returns) / len(returns)
            var = sum((r - avg_return) ** 2 for r in returns) / len(returns)
            std_return = var ** 0.5
            if std_return > 0:
                sharpe_ratio = (avg_return - risk_free_rate / 252) / std_return * (252 ** 0.5)
            else:
                sharpe_ratio = 0.0
            # Sortino
            downside = [r for r in returns if r < 0]
            if downside:
                downside_var = sum((r) ** 2 for r in downside) / len(downside)
                downside_std = downside_var ** 0.5
                if downside_std > 0:
                    sortino_ratio = (avg_return - risk_free_rate / 252) / downside_std * (252 ** 0.5)
                else:
                    sortino_ratio = 0.0
            else:
                sortino_ratio = sharpe_ratio
        else:
            sharpe_ratio = 0.0
            sortino_ratio = 0.0

        # Max drawdown
        peak = self.equity_curve[0]
        max_dd = 0.0
        for value in self.equity_curve:
            if value > peak:
                peak = value
            if peak == 0:
                dd = 0.0
            else:
                dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        win_rate = 0.0
        profit_factor = 0.0
        calmar_ratio = (total_return / max_dd) if max_dd > 0 else 0.0

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
        )
