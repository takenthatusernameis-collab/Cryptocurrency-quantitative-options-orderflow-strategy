"""Gamma Exposure (GEX) calculations."""

from math import isfinite
from typing import Dict, List, Optional

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote


def calculate_gamma_exposure(quote: OptionQuote, spot_price: float) -> float:
    """Calculate gamma exposure for a single option contract.
    Standard approximation: GEX notional ~ Gamma * OI * ContractSize * Spot^2 / 100
    """
    if quote.gamma is None or quote.open_interest is None:
        return 0.0
    if quote.open_interest == 0:
        return 0.0

    gamma = float(quote.gamma)
    oi = float(quote.open_interest)
    contract_size = float(getattr(quote.contract, "contract_size", 1.0))
    spot = float(spot_price) if spot_price > 0 else 0.0
    if not isfinite(gamma) or not isfinite(oi) or not isfinite(spot):
        return 0.0

    # GEX in terms of dollar gamma exposure (common convention)
    gex = gamma * oi * contract_size * (spot ** 2) / 100.0

    if quote.contract.option_type.lower() == "put":
        gex = -abs(gex)
    else:
        gex = abs(gex)

    if not isfinite(gex):
        return 0.0
    return gex


def calculate_delta_weighted_gex(quote: OptionQuote, spot_price: float) -> float:
    """Calculate delta-weighted gamma exposure.
    Delta-weighted GEX adjusts for moneyness via delta when available.
    Falls back to standard GEX if delta missing.
    """
    base_gex = calculate_gamma_exposure(quote, spot_price)
    if not isfinite(base_gex):
        return 0.0
    if quote.delta is None:
        return base_gex
    delta = float(quote.delta)
    if not isfinite(delta):
        return base_gex
    # Weight by absolute delta scaled to [0,1] to emphasize ATM
    weight = abs(delta)
    if weight < 0.0:
        weight = 0.0
    if weight > 1.0:
        weight = 1.0
    # Blend: emphasize contracts with higher |delta| (closer to ATM)
    dw_gex = base_gex * (0.5 + 0.5 * weight)
    if not isfinite(dw_gex):
        return base_gex
    return dw_gex


def calculate_oi_volume_weighted_gex(quote: OptionQuote, spot_price: float) -> float:
    """Calculate OI and volume weighted GEX."""
    base_gex = calculate_gamma_exposure(quote, spot_price)
    if not isfinite(base_gex):
        return 0.0
    oi = float(quote.open_interest) if quote.open_interest is not None else 0.0
    vol = float(quote.volume) if quote.volume is not None else 0.0
    if not isfinite(oi) or not isfinite(vol):
        return base_gex
    # Weight by liquidity proxy
    total_liq = oi + vol
    if total_liq <= 0:
        return base_gex
    # Normalized weight, cap to avoid extreme scaling
    w = min(2.0, (oi + 0.5 * vol) / (max(1.0, oi) if oi > 0 else (vol + 1.0)))
    w_gex = base_gex * w
    if not isfinite(w_gex):
        return base_gex
    return w_gex


def calculate_total_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total gamma exposure across all options in chain."""
    total_gex = 0.0
    for quote in chain.quotes:
        gex = calculate_gamma_exposure(quote, spot_price)
        if isfinite(gex):
            total_gex += gex
    return total_gex


def calculate_total_delta_weighted_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total delta-weighted gamma exposure."""
    total_gex = 0.0
    for quote in chain.quotes:
        gex = calculate_delta_weighted_gex(quote, spot_price)
        if isfinite(gex):
            total_gex += gex
    return total_gex


def calculate_total_oi_volume_weighted_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total OI/volume weighted gamma exposure."""
    total_gex = 0.0
    for quote in chain.quotes:
        gex = calculate_oi_volume_weighted_gex(quote, spot_price)
        if isfinite(gex):
            total_gex += gex
    return total_gex


def calculate_gex_by_strike(chain: OptionsChain, spot_price: float, weighted: str = "none") -> Dict[float, float]:
    """Calculate gamma exposure grouped by strike price.
    weighted: 'none', 'delta', or 'liquidity'
    """
    gex_by_strike: Dict[float, float] = {}
    for quote in chain.quotes:
        strike = float(quote.contract.strike)
        if weighted == "delta":
            gex = calculate_delta_weighted_gex(quote, spot_price)
        elif weighted == "liquidity":
            gex = calculate_oi_volume_weighted_gex(quote, spot_price)
        else:
            gex = calculate_gamma_exposure(quote, spot_price)
        if not isfinite(gex):
            continue
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
            flip = s1 + ratio * (s2 - s1)
            if isfinite(flip):
                return float(flip)

    return 0.0


def gamma_flip_level(chain: OptionsChain, spot_price: float) -> float:
    """Convenience function to find gamma flip level."""
    gex_by_strike = calculate_gex_by_strike(chain, spot_price)
    return find_gamma_flip_level(gex_by_strike)


def gamma_flip_level_weighted(chain: OptionsChain, spot_price: float, weighted: str = "delta") -> float:
    """Gamma flip level with weighted GEX."""
    gex_by_strike = calculate_gex_by_strike(chain, spot_price, weighted=weighted)
    return find_gamma_flip_level(gex_by_strike)
