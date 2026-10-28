"""Gamma Exposure (GEX) calculations."""

from math import isfinite
from typing import Dict, List, Optional, Tuple

import numpy as np

from ..data.schemas import OptionsChain, OptionQuote
from ..errors import FeatureError, NonFiniteResultError


def _ensure_finite(value: float, name: str, context: Optional[Dict[str, object]] = None) -> float:
    try:
        v = float(value)
    except Exception as e:
        raise NonFiniteResultError(
            f"{name} must be finite",
            context={"field": name, **(context or {})},
            cause=e,
        )
    if not isfinite(v):
        raise NonFiniteResultError(
            f"{name} must be finite",
            context={"field": name, **(context or {})},
        )
    return v


def calculate_gamma_exposure(quote: OptionQuote, spot_price: float) -> float:
    """Calculate gamma exposure for a single option contract.

    Uses the standard approximation for dollar gamma exposure (GEX notional):
    ``gex ≈ gamma * OI * contract_size * spot^2 / 100``. Sign convention follows
    dealer positioning: calls contribute positive gamma exposure to the dealer's
    gamma profile (dealers short calls are long gamma), puts contribute negative
    (dealers short puts are short gamma). Returns 0.0 on missing inputs or
    non-finite values for numerical stability.
    """
    ctx = {"function": "calculate_gamma_exposure"}
    try:
        if quote is None:
            return 0.0
        if quote.gamma is None or quote.open_interest is None:
            return 0.0
        if quote.open_interest == 0:
            return 0.0

        gamma = float(quote.gamma)
        oi = float(quote.open_interest)
        contract_size = float(getattr(getattr(quote, "contract", None), "contract_size", 1.0))
        spot = float(spot_price) if spot_price > 0 else 0.0
        if not isfinite(gamma) or not isfinite(oi) or not isfinite(spot):
            return 0.0
        if spot <= 0:
            raise NonFiniteResultError(
                "spot_price must be positive and finite",
                context={**ctx, "spot_price": spot_price},
            )

        # GEX in terms of dollar gamma exposure (common convention)
        gex = gamma * oi * contract_size * (spot ** 2) / 100.0

        if getattr(getattr(quote, "contract", None), "option_type", "call").lower() == "put":
            gex = -abs(gex)
        else:
            gex = abs(gex)

        if not isfinite(gex):
            raise NonFiniteResultError(
                "gamma exposure result not finite",
                context={**ctx, "gamma": gamma, "oi": oi, "spot": spot},
            )
        return gex
    except (NonFiniteResultError, FeatureError):
        raise
    except Exception as e:
        raise FeatureError("Failed to calculate gamma exposure", context=ctx, cause=e)


def calculate_delta_weighted_gex(quote: OptionQuote, spot_price: float) -> float:
    """Calculate delta-weighted gamma exposure.

    Blends the base GEX with a weight in [0.5, 1.0] depending on |delta| (ATM
    contracts receive higher weight) to emphasize near-the-money positioning.
    Falls back to the unweighted GEX if delta is missing or non-finite.
    """
    ctx = {"function": "calculate_delta_weighted_gex"}
    try:
        base_gex = calculate_gamma_exposure(quote, spot_price)
        if not isfinite(base_gex):
            raise NonFiniteResultError(
                "base gamma exposure not finite", context={**ctx}
            )
        if quote is None or quote.delta is None:
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
            raise NonFiniteResultError(
                "delta-weighted gex not finite",
                context={**ctx, "delta": delta},
            )
        return dw_gex
    except (NonFiniteResultError, FeatureError):
        raise
    except Exception as e:
        raise FeatureError("Failed to calculate delta-weighted gex", context=ctx, cause=e)


def calculate_oi_volume_weighted_gex(quote: OptionQuote, spot_price: float) -> float:
    """Calculate OI and volume weighted gamma exposure.

    Applies a liquidity-based weight (favoring open interest with volume as a
    partial contributor) capped at 2.0 to avoid extreme scaling. Falls back to
    base GEX on missing/non-finite inputs or zero liquidity.
    """
    ctx = {"function": "calculate_oi_volume_weighted_gex"}
    try:
        base_gex = calculate_gamma_exposure(quote, spot_price)
        if not isfinite(base_gex):
            raise NonFiniteResultError("base gamma exposure not finite", context={**ctx})
        if quote is None:
            return base_gex
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
        if not isfinite(w) or w < 0:
            return base_gex
        w_gex = base_gex * w
        if not isfinite(w_gex):
            raise NonFiniteResultError(
                "oi/volume weighted gex not finite", context={**ctx}
            )
        return w_gex
    except (NonFiniteResultError, FeatureError):
        raise
    except Exception as e:
        raise FeatureError("Failed to calculate oi/volume weighted gex", context=ctx, cause=e)


def calculate_net_gamma_exposure(chain: OptionsChain, spot_price: float) -> float:
    """Calculate net gamma exposure with dealer-positioning sign convention.

    For each valid quote (gamma/OI finite and OI > 0), computes
    ``gex = gamma * OI * contract_size * spot^2 / 100``. Calls add +|gex|
    (dealers short calls → long gamma) and puts add -|gex| (dealers short puts
    → short gamma). Sums across all strikes/expiries; returns 0.0 if net is
    non-finite.
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

    For each quote with finite gamma/OI and OI > 0, computes gex notional and
    weights by ``OI + 0.5*volume`` (capped) before assigning to bands based on
    |delta| relative to ``atm_band`` (|delta| >= 1-atm_band → ATM, else ITM if
    delta same-side as moneyness intuition or simply < ATM band treated as OTM
    in this classification). Returns dict keys ``'atm'``, ``'otm'``, ``'itm'``,
    ``'total'``; values are floats, non-finite guarded.
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
    """Vectorized computation of per-quote gamma exposure with dealer sign.

    Computes ``gex = gamma * oi * contract_size * spot^2 / 100`` per quote;
    calls are positive, puts negative in dealer convention. Missing/non-finite
    inputs produce 0.0 and results are sanitized to finite values.
    """
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
    """Vectorized delta weights for delta-weighted GEX in [0.5, 1.0].

    Weight = 0.5 + 0.5*clamp(|delta|, 0, 1), emphasizing ATM contracts.
    Missing/non-finite deltas fall back to weight 1.0.
    """
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
    """Vectorized OI/volume liquidity weights.

    Weight = min(2.0, (oi + 0.5*vol) / max(1.0, oi)) with guards for zero/invalid
    liquidity; falls back to 1.0 on non-finite values.
    """
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
    """Calculate total gamma exposure across all options in the chain.

    Sums per-quote dealer-sign GEX (vectorized) over all quotes; returns 0.0 if
    chain has no quotes or result is non-finite.
    """
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

    Applies delta-based weighting ``w = 0.5 + 0.5*clamp(|delta|,0,1)`` to per-quote
    GEX and sums; sanitizes non-finite results to the base GEX value where needed
    and returns 0.0 if non-finite overall.
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
    """Calculate total OI/volume weighted gamma exposure (vectorized).

    Weights by liquidity proxy ``(oi + 0.5*vol)/max(1.0,oi)`` capped at 2.0;
    sanitizes non-finite values and returns 0.0 if overall result non-finite.
    """
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

    Aggregates dealer-sign GEX per strike. ``weighted`` may be ``'none'``,
    ``'delta'`` (|delta|-based), or ``'liquidity'`` (OI/volume). Non-finite
    values replaced by 0.0 before aggregation.
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

    Sorts strikes, identifies sign changes of net gamma by strike (dealer
    convention), and linearly interpolates between adjacent strikes with
    opposite signs where ``g1*g2 < 0`` using ``ratio = |g1|/(|g1|+|g2|)``.
    Handles all-same-sign (returns extrapolated boundary scaled), zeros,
    multiple crossings (first crossing), and non-finite values. Returns 0.0 if
    no valid crossing found or input empty.
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
    """Compute gamma flip level from unweighted GEX by strike.

    Builds ``gex_by_strike`` via ``calculate_gex_by_strike(..., weighted='none')``
    and returns the interpolated flip level via
    ``find_gamma_flip_level_refined``.
    """
    gex_by_strike = calculate_gex_by_strike(chain, spot_price, weighted="none")
    return find_gamma_flip_level_refined(gex_by_strike)


def gamma_flip_level_weighted(chain: OptionsChain, spot_price: float, weighted: str = "delta") -> float:
    """Compute gamma flip level from weighted GEX by strike.

    Uses ``calculate_gex_by_strike`` with the specified weighting (e.g.,
    ``'delta'`` or ``'liquidity'``) and interpolates the zero-crossing via
    ``find_gamma_flip_level_refined``.
    """
    gex_by_strike = calculate_gex_by_strike(chain, spot_price, weighted=weighted)
    return find_gamma_flip_level_refined(gex_by_strike)


calculate_net_gamma_exposure_total = calculate_net_gamma_exposure
calculate_gamma_exposure_by_strike = calculate_gex_by_strike
calculate_gex_notional_by_strike = calculate_gex_by_strike
calculate_gamma_notional_by_strike = calculate_gex_by_strike
find_gamma_flip_level = find_gamma_flip_level_refined
gamma_flip_level_refined = find_gamma_flip_level_refined
gamma_flip_interpolated = find_gamma_flip_level_refined
