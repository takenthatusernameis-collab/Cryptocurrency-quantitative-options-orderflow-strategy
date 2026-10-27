"""Volatility surface, skew, and term structure analysis."""

from typing import Dict, List

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote


def calculate_put_call_ratio(quotes: List[OptionQuote]) -> float:
    """Calculate put/call ratio by volume."""
    call_volume = sum(q.volume for q in quotes if q.contract.option_type.lower() == "call")
    put_volume = sum(q.volume for q in quotes if q.contract.option_type.lower() == "put")
    
    if call_volume == 0:
        return float("inf") if put_volume > 0 else 0.0
    return put_volume / call_volume


def calculate_put_call_oi_ratio(quotes: List[OptionQuote]) -> float:
    """Calculate put/call ratio by open interest."""
    call_oi = sum(q.open_interest for q in quotes if q.contract.option_type.lower() == "call")
    put_oi = sum(q.open_interest for q in quotes if q.contract.option_type.lower() == "put")
    
    if call_oi == 0:
        return float("inf") if put_oi > 0 else 0.0
    return put_oi / call_oi


def calculate_iv_skew(quotes: List[OptionQuote], spot_price: float) -> float:
    """Calculate volatility skew (25-delta put IV - 25-delta call IV)."""
    # Simplified skew calculation using OTM options
    otm_puts = []
    otm_calls = []
    
    for q in quotes:
        if q.mark_iv is None:
            continue
        moneyness = q.contract.strike / spot_price if spot_price > 0 else 1.0
        if q.contract.option_type.lower() == "put" and moneyness < 0.95:
            otm_puts.append(q.mark_iv)
        elif q.contract.option_type.lower() == "call" and moneyness > 1.05:
            otm_calls.append(q.mark_iv)
    
    if not otm_puts or not otm_calls:
        return 0.0
    
    avg_put_iv = sum(otm_puts) / len(otm_puts)
    avg_call_iv = sum(otm_calls) / len(otm_calls)
    return avg_put_iv - avg_call_iv


def calculate_max_pain(chain: OptionsChain) -> float:
    """Calculate max pain strike price."""
    if not chain.quotes:
        return 0.0
    
    strikes = set(q.contract.strike for q in chain.quotes)
    max_pain_strike = 0.0
    min_pain = float("inf")
    
    for strike in strikes:
        total_pain = 0.0
        for q in chain.quotes:
            if q.contract.option_type.lower() == "call":
                if q.contract.strike < strike:
                    total_pain += (strike - q.contract.strike) * q.open_interest
            else:  # put
                if q.contract.strike > strike:
                    total_pain += (q.contract.strike - strike) * q.open_interest
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = strike
    
    return max_pain_strike
