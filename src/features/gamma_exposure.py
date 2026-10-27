"""Gamma Exposure (GEX) calculations."""

from typing import Dict, List

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote


def calculate_gamma_exposure(quote: OptionQuote, spot_price: float) -> float:
    """Calculate gamma exposure for a single option contract."""
    if quote.gamma is None:
        return 0.0
    
    # GEX = Gamma * OI * Contract Size * Spot^2 (dealer gamma exposure convention)
    gex = quote.gamma * quote.open_interest * quote.contract.contract_size * (spot_price ** 2)
    
    # Calls and puts have opposite signs in some conventions
    # Using absolute dealer gamma exposure
    if quote.contract.option_type.lower() == "put":
        gex = -abs(gex)  # Puts often contribute negatively to dealer gamma
    else:
        gex = abs(gex)
    
    return gex


def calculate_total_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total gamma exposure across all options in chain."""
    total_gex = 0.0
    for quote in chain.quotes:
        total_gex += calculate_gamma_exposure(quote, spot_price)
    return total_gex


def calculate_gex_by_strike(chain: OptionsChain, spot_price: float) -> Dict[float, float]:
    """Calculate gamma exposure grouped by strike price."""
    gex_by_strike: Dict[float, float] = {}
    for quote in chain.quotes:
        strike = quote.contract.strike
        gex = calculate_gamma_exposure(quote, spot_price)
        if strike in gex_by_strike:
            gex_by_strike[strike] += gex
        else:
            gex_by_strike[strike] = gex
    return gex_by_strike


def find_gamma_flip_level(gex_by_strike: Dict[float, float]) -> float:
    """Find gamma flip level where GEX crosses zero."""
    if not gex_by_strike:
        return 0.0
    
    sorted_strikes = sorted(gex_by_strike.keys())
    for i in range(len(sorted_strikes) - 1):
        s1, s2 = sorted_strikes[i], sorted_strikes[i + 1]
        g1, g2 = gex_by_strike[s1], gex_by_strike[s2]
        if g1 * g2 < 0:  # Zero crossing
            # Linear interpolation
            ratio = abs(g1) / (abs(g1) + abs(g2))
            return s1 + ratio * (s2 - s1)
    
    return 0.0
