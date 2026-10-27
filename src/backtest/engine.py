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


class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.initial_capital = config.initial_capital
        self.cash = config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [config.initial_capital]

    def execute_trade(self, symbol: str, quantity: float, price: float, side: str, timestamp: datetime) -> Trade:
        """Execute a trade with fees and slippage."""
        # Apply slippage
        slippage = self.config.slippage_bps / 10000.0
        if side == "buy":
            execution_price = price * (1 + slippage)
        else:
            execution_price = price * (1 - slippage)
        
        # Calculate commission
        notional = quantity * execution_price
        commission = notional * self.config.fee_rate
        
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
        
        total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital
        
        # Calculate returns
        returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (self.equity_curve[i] - self.equity_curve[i - 1]) / self.equity_curve[i - 1]
            returns.append(ret)
        
        # Sharpe ratio (simplified, assuming daily returns)
        if returns:
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            if std_return > 0:
                sharpe_ratio = (avg_return - self.config.risk_free_rate / 252) / std_return * (252 ** 0.5)
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        # Max drawdown
        peak = self.equity_curve[0]
        max_dd = 0.0
        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        # Win rate
        winning_trades = 0
        if self.trades:
            # Simplified - would need entry/exit pairing for accurate win rate
            win_rate = 0.0
        else:
            win_rate = 0.0
        
        return BacktestResults(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=0.0,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=0.0,
            total_trades=len(self.trades),
            trades=self.trades,
            equity_curve=self.equity_curve,
        )
