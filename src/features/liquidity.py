"""Liquidity metrics for options and markets."""

from math import isfinite
from typing import Dict, List

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote


def calculate_bid_ask_spread(quote: OptionQuote) -> float:
    """Calculate bid-ask spread."""
    bid = float(quote.bid) if quote.bid is not None else 0.0
    ask = float(quote.ask) if quote.ask is not None else 0.0
    if not isfinite(bid) or not isfinite(ask) or bid < 0 or ask < 0:
        return 0.0
    if ask < bid:
        # Swap if inverted
        bid, ask = ask, bid
    spread = ask - bid
    if not isfinite(spread) or spread < 0:
        return 0.0
    return spread


def calculate_mid_price(quote: OptionQuote) -> float:
    """Calculate mid price."""
    bid = float(quote.bid) if quote.bid is not None else 0.0
    ask = float(quote.ask) if quote.ask is not None else 0.0
    if not isfinite(bid) or not isfinite(ask):
        return float(quote.mark) if quote.mark is not None and isfinite(quote.mark) else 0.0
    if bid <= 0 and ask <= 0:
        return float(quote.mark) if quote.mark is not None and isfinite(quote.mark) else 0.0
    if bid <= 0:
        return ask
    if ask <= 0:
        return bid
    if ask < bid:
        bid, ask = ask, bid
    mid = (bid + ask) / 2.0
    if not isfinite(mid) or mid <= 0:
        return float(quote.mark) if quote.mark is not None and isfinite(quote.mark) else 0.0
    return mid


def calculate_relative_spread(quote: OptionQuote) -> float:
    """Calculate relative bid-ask spread."""
    spread = calculate_bid_ask_spread(quote)
    mid = calculate_mid_price(quote)
    if not isfinite(spread) or not isfinite(mid) or mid <= 0:
        return 0.0
    rel = spread / mid
    if not isfinite(rel) or rel < 0:
        return 0.0
    return rel


def calculate_effective_spread_proxy(quote: OptionQuote) -> float:
    """Calculate effective spread proxy using mid and last/mark."""
    spread = calculate_bid_ask_spread(quote)
    mid = calculate_mid_price(quote)
    last = float(quote.last) if quote.last is not None else None
    mark = float(quote.mark) if quote.mark is not None else None
    ref = last if last is not None and isfinite(last) else mark
    if ref is None or not isfinite(ref) or mid <= 0:
        return spread
    # Effective spread proxy ~ 2*|price - mid|
    eff = 2.0 * abs(ref - mid)
    if not isfinite(eff) or eff < 0:
        return spread
    # Blend with quoted spread
    return (eff + spread) / 2.0


def calculate_liquidity_score(quote: OptionQuote) -> float:
    """Calculate composite liquidity score (higher is more liquid)."""
    rel_spread = calculate_relative_spread(quote)
    oi = float(quote.open_interest) if quote.open_interest is not None else 0.0
    vol = float(quote.volume) if quote.volume is not None else 0.0
    if not isfinite(oi):
        oi = 0.0
    if not isfinite(vol):
        vol = 0.0
    # Score: penalize wide spreads, reward OI/volume
    spread_penalty = 1.0 / (1.0 + rel_spread * 100.0)  # Scale spreads
    liq_boost = min(1.0, (oi + vol) / 10000.0)  # Normalize
    score = spread_penalty * (0.5 + 0.5 * liq_boost)
    if not isfinite(score) or score < 0:
        score = 0.0
    if score > 1.0:
        score = 1.0
    return score


def calculate_chain_liquidity_metrics_vectorized(chain: OptionsChain) -> Dict[str, float]:
    """Vectorized aggregate liquidity metrics (identical to `calculate_chain_liquidity_metrics`)."""
    if not chain.quotes:
        return {
            "avg_bid_ask_spread": 0.0,
            "avg_relative_spread": 0.0,
            "avg_effective_spread": 0.0,
            "avg_liquidity_score": 0.0,
            "total_oi": 0.0,
            "total_volume": 0.0,
        }
    n = len(chain.quotes)
    spreads = np.zeros(n, dtype=np.float64)
    rel_spreads = np.zeros(n, dtype=np.float64)
    eff_spreads = np.zeros(n, dtype=np.float64)
    scores = np.zeros(n, dtype=np.float64)
    total_oi = 0.0
    total_volume = 0.0
    for i, q in enumerate(chain.quotes):
        spreads[i] = calculate_bid_ask_spread(q)
        rel_spreads[i] = calculate_relative_spread(q)
        eff_spreads[i] = calculate_effective_spread_proxy(q)
        scores[i] = calculate_liquidity_score(q)
        if q.open_interest is not None and isfinite(q.open_interest):
            total_oi += float(q.open_interest)
        if q.volume is not None and isfinite(q.volume):
            total_volume += float(q.volume)
    return {
        "avg_bid_ask_spread": float(spreads.mean()) if n else 0.0,
        "avg_relative_spread": float(rel_spreads.mean()) if n else 0.0,
        "avg_effective_spread": float(eff_spreads.mean()) if n else 0.0,
        "avg_liquidity_score": float(scores.mean()) if n else 0.0,
        "total_oi": total_oi,
        "total_volume": total_volume,
    }


def calculate_chain_liquidity_metrics(chain: OptionsChain) -> Dict[str, float]:
    """Calculate aggregate liquidity metrics for options chain (vectorized)."""
    return calculate_chain_liquidity_metrics_vectorized(chain)