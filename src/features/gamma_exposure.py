"""Gamma Exposure (GEX) calculations."""

from typing import Dict, List

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote


def calculate_gamma_exposure(quote: OptionQuote, spot_price: float) -> float:
    """Calculate gamma exposure for a single option contract.
    Standard approximation: GEX notional ~ Gamma * OI * ContractSize * Spot^2 (scaled)
    """
    if quote.gamma is None or quote.open_interest is None:
        return 0.0
    if quote.open_interest == 0:
        return 0.0

    gamma = float(quote.gamma)
    oi = float(quote.open_interest)
    contract_size = float(getattr(quote.contract, "contract_size", 1.0))
    spot = float(spot_price) if spot_price > 0 else 0.0

    # GEX in terms of dollar gamma exposure (common convention)
    gex = gamma * oi * contract_size * (spot ** 2)

    if quote.contract.option_type.lower() == "put":
        gex = -abs(gex)
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
        strike = float(quote.contract.strike)
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
        if g1 == 0:
            return float(s1)
        if g2 == 0:
            return float(s2)
        if g1 * g2 < 0:  # Zero crossing
            ratio = abs(g1) / (abs(g1) + abs(g2))
            return float(s1 + ratio * (s2 - s1))

    return 0.0


def gamma_flip_level(chain: OptionsChain, spot_price: float) -> float:
    """Convenience function to find gamma flip level."""
    gex_by_strike = calculate_gex_by_strike(chain, spot_price)
    return find_gamma_flip_level(gex_by_strike)
