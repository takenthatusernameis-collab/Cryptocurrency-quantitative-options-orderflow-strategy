"""Gamma Exposure (GEX) calculations."""

from math import isfinite
from typing import Dict, List, Optional, Tuple

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


def calculate_net_gamma_exposure(chain: OptionsChain, spot_price: float) -> float:
    """Calculate net gamma exposure with proper sign convention.
    Calls contribute positive gamma exposure (dealers short calls -> long gamma),
    puts contribute negative gamma exposure (dealers short puts -> short gamma) in dealer positioning convention.
    Returns net GEX (sum across all strikes/expiries).
    """
    net_gex = 0.0
    for quote in chain.quotes:
        if quote.gamma is None or quote.open_interest is None:
            continue
        if quote.open_interest == 0:
            continue
        gamma = float(quote.gamma)
        oi = float(quote.open_interest)
        contract_size = float(getattr(quote.contract, "contract_size", 1.0))
        spot = float(spot_price) if spot_price > 0 else 0.0
        if not isfinite(gamma) or not isfinite(oi) or not isfinite(spot):
            continue
        gex = gamma * oi * contract_size * (spot ** 2) / 100.0
        if not isfinite(gex):
            continue
        if quote.contract.option_type.lower() == "put":
            net_gex -= abs(gex)
        else:
            net_gex += abs(gex)
    if not isfinite(net_gex):
        return 0.0
    return float(net_gex)


def calculate_gamma_notional_by_delta_bands(
    chain: OptionsChain,
    spot_price: float,
    atm_band: float = 0.1,
) -> Dict[str, float]:
    """Calculate gamma notional grouped by delta bands (ATM/OTM/ITM).
    OI/volume weighting applied. Returns dict with keys: 'atm', 'otm', 'itm', 'total'.
    """
    result = {"atm": 0.0, "otm": 0.0, "itm": 0.0, "total": 0.0}
    for quote in chain.quotes:
        if quote.gamma is None or quote.open_interest is None:
            continue
        if quote.open_interest == 0:
            continue
        gamma = float(quote.gamma)
        oi = float(quote.open_interest)
        vol = float(quote.volume) if quote.volume is not None else 0.0
        contract_size = float(getattr(quote.contract, "contract_size", 1.0))
        spot = float(spot_price) if spot_price > 0 else 0.0
        delta = float(quote.delta) if quote.delta is not None else None
        if not isfinite(gamma) or not isfinite(oi) or not isfinite(spot):
            continue
        gex = gamma * oi * contract_size * (spot ** 2) / 100.0
        if not isfinite(gex):
            continue
        if quote.contract.option_type.lower() == "put":
            gex = -abs(gex)
        else:
            gex = abs(gex)
        # Apply OI/volume weighting with numerical stability
        liq_weight = 1.0
        total_liq = oi + vol
        if total_liq > 0 and oi > 0:
            liq_weight = min(2.0, (oi + 0.3 * vol) / max(1.0, oi))
            if not isfinite(liq_weight) or liq_weight < 0:
                liq_weight = 1.0
        gex_weighted = gex * liq_weight
        if not isfinite(gex_weighted):
            continue
        # Classify by delta bands.
        # ATM is defined as |delta| near 0.5 (at-the-money), NOT near 0.
        # Calls: delta in (0, 1], OTM < 0.5, ATM ~ 0.5, ITM > 0.5
        # Puts:  delta in [-1, 0), OTM > -0.5, ATM ~ -0.5, ITM < -0.5
        if delta is not None and isfinite(delta):
            if quote.contract.option_type.lower() == "call":
                if delta >= (0.5 - atm_band) and delta <= (0.5 + atm_band):
                    result["atm"] += gex_weighted
                elif delta > (0.5 + atm_band):
                    result["itm"] += gex_weighted
                else:
                    result["otm"] += gex_weighted
            else:  # put
                if delta >= -(0.5 + atm_band) and delta <= -(0.5 - atm_band):
                    result["atm"] += gex_weighted
                elif delta < -(0.5 + atm_band):
                    result["itm"] += gex_weighted
                else:
                    result["otm"] += gex_weighted
        else:
            # Fallback by moneyness if delta missing
            moneyness = spot / quote.contract.strike if quote.contract.strike > 0 else 1.0
            if quote.contract.option_type.lower() == "call":
                if moneyness >= (1.0 - atm_band) and moneyness <= (1.0 + atm_band):
                    result["atm"] += gex_weighted
                elif moneyness > 1.0 + atm_band:
                    result["itm"] += gex_weighted
                else:
                    result["otm"] += gex_weighted
            else:  # put
                if moneyness >= (1.0 - atm_band) and moneyness <= (1.0 + atm_band):
                    result["atm"] += gex_weighted
                elif moneyness < 1.0 - atm_band:
                    result["itm"] += gex_weighted
                else:
                    result["otm"] += gex_weighted
        result["total"] += gex_weighted
    for k in ["atm", "otm", "itm", "total"]:
        if not isfinite(result[k]):
            result[k] = 0.0
    return result


def _vectorized_gex(quotes: List[OptionQuote], spot_price: float) -> np.ndarray:
    """Vectorized per-quote GEX computation returning a float64 array.

    Mirrors the scalar `calculate_gamma_exposure` semantics exactly: missing
    gamma/OI, zero OI, non-finite inputs, and non-finite results all yield 0.0
    for that quote. Calls contribute positive GEX, puts negative.
    """
    n = len(quotes)
    out = np.zeros(n, dtype=np.float64)
    if n == 0:
        return out

    gamma = np.zeros(n, dtype=np.float64)
    oi = np.zeros(n, dtype=np.float64)
    contract_size = np.ones(n, dtype=np.float64)
    spot = float(spot_price) if spot_price is not None and spot_price > 0 else 0.0
    is_put = np.zeros(n, dtype=bool)

    for i, q in enumerate(quotes):
        g = q.gamma
        o = q.open_interest
        if g is None or o is None:
            continue
        gf = float(g)
        of = float(o)
        if not (isfinite(gf) and isfinite(of)):
            continue
        if of == 0:
            continue
        gamma[i] = gf
        oi[i] = of
        contract_size[i] = float(getattr(q.contract, "contract_size", 1.0))
        try:
            is_put[i] = str(q.contract.option_type).lower() == "put"
        except Exception:
            is_put[i] = False

    if not isfinite(spot) or spot <= 0.0:
        return out

    gex = gamma * oi * contract_size * (spot ** 2) / 100.0
    gex = np.where(np.isfinite(gex), gex, 0.0)
    gex = np.where(is_put, -np.abs(gex), np.abs(gex))
    return gex


def _vectorized_delta_weights(quotes: List[OptionQuote]) -> np.ndarray:
    """Vectorized delta weights (0.5 + 0.5*clamp(|delta|,0,1))."""
    n = len(quotes)
    w = np.full(n, 0.5, dtype=np.float64)
    for i, q in enumerate(quotes):
        d = q.delta
        if d is None:
            continue
        df = float(d)
        if not isfinite(df):
            continue
        w[i] = 0.5 + 0.5 * min(1.0, max(0.0, abs(df)))
    return w


def _vectorized_oi_vol_weights(quotes: List[OptionQuote]) -> np.ndarray:
    """Vectorized OI/volume liquidity weights (min(2.0, (oi+0.5*vol)/max(1.0,oi)))."""
    n = len(quotes)
    w = np.ones(n, dtype=np.float64)
    for i, q in enumerate(quotes):
        oi = float(q.open_interest) if q.open_interest is not None else 0.0
        vol = float(q.volume) if q.volume is not None else 0.0
        if not (isfinite(oi) and isfinite(vol)):
            continue
        total_liq = oi + vol
        if total_liq <= 0:
            continue
        denom = max(1.0, oi) if oi > 0 else (vol + 1.0)
        if denom <= 0:
            continue
        ww = (oi + 0.5 * vol) / denom
        if not isfinite(ww) or ww < 0:
            ww = 1.0
        w[i] = min(2.0, ww)
    return w


def calculate_total_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total gamma exposure across all options in chain."""
    if not chain.quotes:
        return 0.0
    arr = _vectorized_gex(chain.quotes, spot_price)
    total = float(arr.sum())
    if not isfinite(total):
        return 0.0
    return total


def calculate_total_gex_vectorized(chain: OptionsChain, spot_price: float) -> float:
    """Vectorized total gamma exposure (alias for `calculate_total_gex`).

    Provided for callers that want an explicit vectorized entry point; the
    result is identical to `calculate_total_gex`.
    """
    return calculate_total_gex(chain, spot_price)


def calculate_total_delta_weighted_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total delta-weighted gamma exposure (vectorized).

    Multiplies per-quote GEX by (0.5 + 0.5 * clamp(|delta|, 0, 1)) and sums.
    """
    if not chain.quotes:
        return 0.0
    base = _vectorized_gex(chain.quotes, spot_price)
    w = _vectorized_delta_weights(chain.quotes)
    out = base * w
    out = np.where(np.isfinite(out), out, base)
    total = float(out.sum())
    if not isfinite(total):
        return 0.0
    return total


def calculate_total_oi_volume_weighted_gex(chain: OptionsChain, spot_price: float) -> float:
    """Calculate total OI/volume weighted gamma exposure (vectorized)."""
    if not chain.quotes:
        return 0.0
    base = _vectorized_gex(chain.quotes, spot_price)
    w = _vectorized_oi_vol_weights(chain.quotes)
    out = base * w
    out = np.where(np.isfinite(out), out, base)
    total = float(out.sum())
    if not isfinite(total):
        return 0.0
    return total


def calculate_gex_by_strike(chain: OptionsChain, spot_price: float, weighted: str = "none") -> Dict[float, float]:
    """Calculate gamma exposure grouped by strike price (vectorized).

    weighted: 'none', 'delta', or 'liquidity'
    """
    if not chain.quotes:
        return {}
    strikes = np.array([float(q.contract.strike) for q in chain.quotes], dtype=np.float64)
    base = _vectorized_gex(chain.quotes, spot_price)
    if weighted == "delta":
        w = _vectorized_delta_weights(chain.quotes)
        base = base * w
    elif weighted == "liquidity":
        w = _vectorized_oi_vol_weights(chain.quotes)
        base = base * w
    base = np.where(np.isfinite(base), base, 0.0)
    out: Dict[float, float] = {}
    for strike, gex in zip(strikes.tolist(), base.tolist()):
        if strike in out:
            out[strike] += gex
        else:
            out[strike] = gex
    return out


def calculate_gex_by_strike_vectorized(chain: OptionsChain, spot_price: float, weighted: str = "none") -> Dict[float, float]:
    """Vectorized alias for `calculate_gex_by_strike`."""
    return calculate_gex_by_strike(chain, spot_price, weighted=weighted)


def find_gamma_flip_level_refined(gex_by_strike: Dict[float, float]) -> float:
    """Refined gamma flip interpolation with robust edge-case handling.
    Handles all-positive/all-negative GEX, multiple crossings, and numerical issues.
    """
    if not gex_by_strike:
        return 0.0

    sorted_strikes = sorted(gex_by_strike.keys())
    # Check all same sign
    signs = []
    for s in sorted_strikes:
        g = gex_by_strike[s]
        if not isfinite(g) or abs(g) < 1e-18:
            signs.append(0)
        elif g > 0:
            signs.append(1)
        else:
            signs.append(-1)
    # If all non-negative or all non-positive, find where it would cross zero
    # For all negative GEX, flip might be below lowest strike? Or return interpolated
    # For all positive, flip above highest strike? But return sensible value
    non_zero_signs = [s for s in signs if s != 0]
    if len(non_zero_signs) == 0:
        return float(sorted_strikes[len(sorted_strikes) // 2]) if sorted_strikes else 0.0
    # Check if all same sign
    all_same = all(x == non_zero_signs[0] for x in non_zero_signs)
    if all_same:
        # All positive: gamma flip is below the lowest strike with positive GEX? Unusual
        # All negative: gamma flip above highest strike? Try to find boundary
        if non_zero_signs[0] > 0:  # all positive
            # Return slightly below lowest strike for consistency
            return float(sorted_strikes[0] * 0.995)
        else:  # all negative
            return float(sorted_strikes[-1] * 1.005)

    for i in range(len(sorted_strikes) - 1):
        s1, s2 = sorted_strikes[i], sorted_strikes[i + 1]
        g1, g2 = gex_by_strike[s1], gex_by_strike[s2]
        if not isfinite(g1) or not isfinite(g2):
            continue
        if abs(g1) < 1e-18:
            return float(s1)
        if abs(g2) < 1e-18:
            return float(s2)
        if g1 * g2 < 0:  # Zero crossing
            denom = abs(g1) + abs(g2)
            if denom == 0 or not isfinite(denom):
                ratio = 0.5
            else:
                ratio = abs(g1) / denom
            flip = s1 + ratio * (s2 - s1)
            if isfinite(flip):
                return float(flip)
    return 0.0


gamma_flip_level_refined = find_gamma_flip_level_refined


def gamma_flip_level(chain: OptionsChain, spot_price: float) -> float:
    """Convenience function to find gamma flip level."""
    gex_by_strike = calculate_gex_by_strike(chain, spot_price)
    return find_gamma_flip_level_refined(gex_by_strike)


def gamma_flip_level_weighted(chain: OptionsChain, spot_price: float, weighted: str = "delta") -> float:
    """Gamma flip level with weighted GEX."""
    gex_by_strike = calculate_gex_by_strike(chain, spot_price, weighted=weighted)
    return find_gamma_flip_level_refined(gex_by_strike)


calculate_net_gamma_exposure_total = calculate_net_gamma_exposure
calculate_gamma_exposure_by_strike = calculate_gex_by_strike
calculate_gex_notional_by_strike = calculate_gex_by_strike
calculate_gamma_notional_by_strike = calculate_gex_by_strike
find_gamma_flip_level = find_gamma_flip_level_refined
gamma_flip_level_refined = find_gamma_flip_level_refined
gamma_flip_interpolated = find_gamma_flip_level_refined
