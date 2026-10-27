"""Data validation utilities."""

from typing import List

from ..data.schemas import OptionQuote, Trade


def validate_option_quote(quote: OptionQuote) -> bool:
    """Validate option quote data."""
    if quote.bid < 0 or quote.ask < 0:
        return False
    if quote.bid > quote.ask and quote.bid > 0 and quote.ask > 0:
        return False
    if quote.contract.strike <= 0:
        return False
    return True


def validate_trade(trade: Trade) -> bool:
    """Validate trade data."""
    if trade.price <= 0:
        return False
    if trade.size <= 0:
        return False
    if trade.side.lower() not in ["buy", "sell"]:
        return False
    return True


def validate_quotes_batch(quotes: List[OptionQuote]) -> List[OptionQuote]:
    """Filter valid quotes from batch."""
    return [q for q in quotes if validate_option_quote(q)]


def validate_trades_batch(trades: List[Trade]) -> List[Trade]:
    """Filter valid trades from batch."""
    return [t for t in trades if validate_trade(t)]
