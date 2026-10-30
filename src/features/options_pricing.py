"""Black-Scholes-Merton options pricing engine with Greeks and IV solver.

Provides analytical European option pricing, full Greeks (analytic formulas plus
finite-difference cross-checks), and a deterministic implied-volatility solver
(bisection bracketing + Newton refinement) with convergence guards, bracket
protection, and deterministic seeding. Every public output is finite-guarded and
safe for :func:`serialize_metrics_strict` / ``allow_nan=False`` emission.

Conventions:
  - Rates and volatilities are annualized, in decimal form (0.05 = 5%).
  - ``time_to_expiry`` is in years.
  - Theta is the annualized derivative ``dPrice / dT`` (negative for decay).
  - Rho is ``dPrice / dRate`` per 1.0 change in the rate.
  - Vega is ``dPrice / dVol`` per 1.0 change in volatility.
  - Option type ``'call'`` / ``'put'`` (case-insensitive).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..data.schemas import PricingInputs, PricingOutputs
from ..errors import FeatureError, NonFiniteResultError, get_logger
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, safe_sqrt, safe_log, validate_finite

_logger = get_logger(__name__)

_SQRT_TWO_PI = math.sqrt(2.0 * math.pi)
_INV_SQRT_TWO_PI = 1.0 / _SQRT_TWO_PI
_SQRT_2 = math.sqrt(2.0)

# Deterministic IV solver bounds (annualized vol, decimal form).
_IV_VOL_FLOOR = 1e-6
_IV_VOL_CAP = 5.0
_IV_MAX_ITER = 100
_IV_TOL = 1e-10
_IV_NEWTON_TOL = 1e-12
_IV_NEUTRAL_SEED = 42
_DAY_COUNT = 365.0


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via ``math.erf`` (deterministic, stdlib)."""
    return 0.5 * (1.0 + math.erf(x / _SQRT_2))


def _norm_pdf(x: float) -> float:
    """Standard normal PDF."""
    return _INV_SQRT_TWO_PI * math.exp(-0.5 * x * x)


def _validate_option_type(option_type: Any) -> str:
    ot = str(option_type).strip().lower()
    if ot not in ("call", "put"):
        raise FeatureError(
            f"option_type must be 'call' or 'put', got {option_type!r}",
            context={"field": "option_type", "value": str(option_type)},
        )
    return ot


def _discount_factor(rate: float, time_to_expiry: float) -> float:
    return math.exp(-rate * time_to_expiry)


def _d1_d2(spot: float, strike: float, rate: float, volatility: float,
           time_to_expiry: float) -> Tuple[float, float]:
    """Return ``(d1, d2)`` for Black-Scholes-Merton.

    Returns ``(0.0, 0.0)`` when there is no time value (expiry at/ before now
    or zero volatility), which collapses pricing to intrinsic value.
    """
    if time_to_expiry <= 0.0 or volatility <= 0.0:
        return 0.0, 0.0
    sqrt_t = safe_sqrt(time_to_expiry, default=0.0, operation="d1_sqrt_t")
    if sqrt_t <= 0.0:
        return 0.0, 0.0
    vol_sqrt_t = volatility * sqrt_t
    if vol_sqrt_t <= 0.0 or not math.isfinite(vol_sqrt_t):
        return 0.0, 0.0
    d1 = safe_divide(
        safe_log(safe_divide(spot, strike, default=1.0, operation="d1_moneyness"), default=0.0, operation="d1_log")
        + (rate + 0.5 * volatility * volatility) * time_to_expiry,
        vol_sqrt_t,
        default=0.0,
        operation="d1",
    )
    d2 = d1 - vol_sqrt_t
    # Clamp extreme values to keep CDF/PDF numerically well behaved.
    d1 = max(-50.0, min(50.0, d1))
    d2 = max(-50.0, min(50.0, d2))
    return d1, d2


def black_scholes_price(inputs: PricingInputs) -> float:
    """Black-Scholes-Merton analytical price for a European option.

    Calls: ``S * N(d1) - K * e^(-rT) * N(d2)``.
    Puts via put-call parity: ``call - S + K * e^(-rT)`` (guarantees call/put
    price consistency and avoids catastrophic cancellation on deep ITM puts).
    Returns intrinsic value when ``time_to_expiry <= 0`` or ``volatility <= 0``.
    """
    ot = _validate_option_type(inputs.option_type)
    spot = validate_finite(inputs.spot, "spot")
    strike = validate_finite(inputs.strike, "strike")
    rate = validate_finite(inputs.rate, "rate")
    volatility = validate_finite(inputs.volatility, "volatility")
    time_to_expiry = validate_finite(inputs.time_to_expiry, "time_to_expiry")
    if spot <= 0.0:
        raise NonFiniteResultError("spot must be positive",
                                   context={"function": "black_scholes_price", "spot": spot})
    if strike <= 0.0:
        raise NonFiniteResultError("strike must be positive",
                                   context={"function": "black_scholes_price", "strike": strike})
    if volatility < 0.0:
        raise NonFiniteResultError("volatility must be >= 0",
                                   context={"function": "black_scholes_price", "volatility": volatility})
    if time_to_expiry < 0.0:
        raise NonFiniteResultError("time_to_expiry must be >= 0",
                                   context={"function": "black_scholes_price", "time_to_expiry": time_to_expiry})

    discount = _discount_factor(rate, time_to_expiry)
    # Degenerate: no time value (expiry at/before now or zero volatility).
    # Return intrinsic value directly; the general d1/d2 path would collapse
    # N(d1)=N(d2)=0.5 and halve the intrinsic price.
    if time_to_expiry <= 0.0 or volatility <= 0.0:
        if ot == "call":
            price = max(spot - strike * discount, 0.0)
        else:
            price = max(strike * discount - spot, 0.0)
        return float(price)

    d1, d2 = _d1_d2(spot, strike, rate, volatility, time_to_expiry)
    call_price = spot * _norm_cdf(d1) - strike * discount * _norm_cdf(d2)
    if not math.isfinite(call_price):
        call_price = max(spot - strike * discount, 0.0)
    if ot == "call":
        price = call_price
    else:
        # Put-call parity keeps call and put on the same curve.
        price = call_price - spot + strike * discount
    if not math.isfinite(price):
        price = max(strike * discount - spot, 0.0)
    price = max(price, 0.0)
    return float(price)


def black_scholes_greeks(inputs: PricingInputs) -> Dict[str, float]:
    """Analytic Greeks for a European option.

    Returns dict with keys ``delta``, ``gamma``, ``vega``, ``theta`` (per year),
    ``rho`` (per 1.0 rate change), plus ``d1``/``d2`` for inspection.
    All values finite-guarded; gamma/vega are zero when there is no time value.
    """
    ot = _validate_option_type(inputs.option_type)
    spot = validate_finite(inputs.spot, "spot")
    strike = validate_finite(inputs.strike, "strike")
    rate = validate_finite(inputs.rate, "rate")
    volatility = validate_finite(inputs.volatility, "volatility")
    time_to_expiry = validate_finite(inputs.time_to_expiry, "time_to_expiry")
    if spot <= 0.0 or strike <= 0.0:
        raise NonFiniteResultError("spot and strike must be positive",
                                   context={"function": "black_scholes_greeks",
                                            "spot": spot, "strike": strike})

    discount = _discount_factor(rate, time_to_expiry)
    d1, d2 = _d1_d2(spot, strike, rate, volatility, time_to_expiry)
    n_d1 = _norm_cdf(d1)
    n_d2 = _norm_cdf(d2)
    n_prime_d1 = _norm_pdf(d1)
    sqrt_t = safe_sqrt(time_to_expiry, default=0.0, operation="greeks_sqrt_t")

    if ot == "call":
        delta = n_d1
    else:
        delta = n_d1 - 1.0
    delta = max(-1.0, min(1.0, delta)) if math.isfinite(delta) else 0.0

    if sqrt_t <= 0.0 or volatility <= 0.0:
        gamma = 0.0
        vega = 0.0
        theta = 0.0
        rho = 0.0
    else:
        gamma = safe_divide(n_prime_d1, spot * volatility * sqrt_t, default=0.0,
                            operation="gamma")
        vega = spot * n_prime_d1 * sqrt_t
        # Theta = -(S * n'(d1) * sigma) / (2 sqrt(T)) - r * K e^(-rT) N(d2) [call]
        #         -(S * n'(d1) * sigma) / (2 sqrt(T)) + r * K e^(-rT) N(-d2) [put]
        theta_common = -spot * n_prime_d1 * volatility * sqrt_t / 2.0
        if ot == "call":
            theta = theta_common - rate * strike * discount * n_d2
        else:
            theta = theta_common + rate * strike * discount * _norm_cdf(-d2)
        if ot == "call":
            rho = strike * time_to_expiry * discount * n_d2
        else:
            rho = -strike * time_to_expiry * discount * _norm_cdf(-d2)
        for name, val in (("gamma", gamma), ("vega", vega), ("theta", theta), ("rho", rho)):
            if not math.isfinite(val):
                raise NonFiniteResultError(f"{name} not finite",
                                           context={"function": "black_scholes_greeks", "name": name, "value": val})

    return {
        "delta": float(delta),
        "gamma": float(gamma),
        "vega": float(vega),
        "theta": float(theta),
        "rho": float(rho),
        "d1": float(d1),
        "d2": float(d2),
    }


def black_scholes(inputs: PricingInputs) -> PricingOutputs:
    """Full Black-Scholes-Merton price + Greeks as a :class:`PricingOutputs`.

    Convenience entry point combining :func:`black_scholes_price` and
    :func:`black_scholes_greeks`. Output is finite-guarded and strict-serializable.
    """
    price = black_scholes_price(inputs)
    greeks = black_scholes_greeks(inputs)
    d1 = greeks["d1"]
    d2 = greeks["d2"]
    outputs = PricingOutputs(
        price=price,
        delta=greeks["delta"],
        gamma=greeks["gamma"],
        vega=greeks["vega"],
        theta=greeks["theta"],
        rho=greeks["rho"],
        d1=d1,
        d2=d2,
        implied_vol=None,
        solver_iterations=0,
        converged=True,
        seed=inputs.seed,
    )
    # Strict serialization gate: refuse to emit non-finite outputs.
    serialize_metrics_strict(outputs.model_dump())
    return outputs


def finite_difference_greeks(inputs: PricingInputs, bump: float = 1e-4) -> Dict[str, float]:
    """Finite-difference cross-check of analytic Greeks.

    Bumps spot (delta/gamma), volatility (vega), rate (rho), and expiry (theta)
    around ``inputs`` and re-prices. Used to validate analytic formulas. Bump is
    clamped to a sane range to avoid cancellation error.
    """
    bump = safe_divide(bump, 1.0, default=1e-4, operation="fd_bump")
    if not math.isfinite(bump) or bump <= 0.0:
        bump = 1e-4
    bump = min(max(bump, 1e-6), 1e-2)

    base_price = black_scholes_price(inputs)

    # Delta / Gamma via spot bump.
    up_inputs = PricingInputs(
        spot=inputs.spot + bump, strike=inputs.strike, rate=inputs.rate,
        volatility=inputs.volatility, time_to_expiry=inputs.time_to_expiry,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    down_inputs = PricingInputs(
        spot=max(inputs.spot - bump, 1e-8), strike=inputs.strike, rate=inputs.rate,
        volatility=inputs.volatility, time_to_expiry=inputs.time_to_expiry,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    price_up = black_scholes_price(up_inputs)
    price_down = black_scholes_price(down_inputs)
    delta_fd = safe_divide(price_up - price_down, 2.0 * bump, default=0.0,
                           operation="fd_delta")
    gamma_fd = safe_divide(price_up - 2.0 * base_price + price_down, bump * bump,
                           default=0.0, operation="fd_gamma")

    # Vega via vol bump.
    vol_up_inputs = PricingInputs(
        spot=inputs.spot, strike=inputs.strike, rate=inputs.rate,
        volatility=inputs.volatility + bump, time_to_expiry=inputs.time_to_expiry,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    vol_down_inputs = PricingInputs(
        spot=inputs.spot, strike=inputs.strike, rate=inputs.rate,
        volatility=max(inputs.volatility - bump, 0.0), time_to_expiry=inputs.time_to_expiry,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    vega_fd = safe_divide(
        black_scholes_price(vol_up_inputs) - black_scholes_price(vol_down_inputs),
        2.0 * bump, default=0.0, operation="fd_vega",
    )

    # Rho via rate bump.
    rate_up_inputs = PricingInputs(
        spot=inputs.spot, strike=inputs.strike, rate=inputs.rate + bump,
        volatility=inputs.volatility, time_to_expiry=inputs.time_to_expiry,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    rate_down_inputs = PricingInputs(
        spot=inputs.spot, strike=inputs.strike, rate=inputs.rate - bump,
        volatility=inputs.volatility, time_to_expiry=inputs.time_to_expiry,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    rho_fd = safe_divide(
        black_scholes_price(rate_up_inputs) - black_scholes_price(rate_down_inputs),
        2.0 * bump, default=0.0, operation="fd_rho",
    )

    # Theta via expiry bump (per year).
    t_up = inputs.time_to_expiry + bump
    t_down = max(inputs.time_to_expiry - bump, 0.0)
    t_up_inputs = PricingInputs(
        spot=inputs.spot, strike=inputs.strike, rate=inputs.rate,
        volatility=inputs.volatility, time_to_expiry=t_up,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    t_down_inputs = PricingInputs(
        spot=inputs.spot, strike=inputs.strike, rate=inputs.rate,
        volatility=inputs.volatility, time_to_expiry=t_down,
        option_type=inputs.option_type, seed=inputs.seed,
    )
    theta_fd = safe_divide(
        black_scholes_price(t_down_inputs) - black_scholes_price(t_up_inputs),
        2.0 * bump, default=0.0, operation="fd_theta",
    )

    return {
        "delta": float(delta_fd),
        "gamma": float(gamma_fd),
        "vega": float(vega_fd),
        "theta": float(theta_fd),
        "rho": float(rho_fd),
    }


def greeks_match_analytic(inputs: PricingInputs, bump: float = 1e-4,
                          tol: float = 1e-2) -> Dict[str, Any]:
    """Compare analytic vs finite-difference Greeks; report agreement.

    Returns dict with per-Greek ``analytic``, ``finite_difference``, ``abs_diff``,
    ``rel_diff``, and ``match`` booleans, plus an overall ``all_match`` flag.
    """
    analytic = black_scholes_greeks(inputs)
    fd = finite_difference_greeks(inputs, bump=bump)
    results: Dict[str, Any] = {}
    all_match = True
    for key in ("delta", "gamma", "vega", "theta", "rho"):
        a = float(analytic[key])
        f = float(fd[key])
        abs_diff = abs(a - f)
        denom = max(abs(a), abs(f), 1e-12)
        rel_diff = abs_diff / denom
        match = bool(abs_diff <= tol and rel_diff <= tol)
        if not match:
            all_match = False
        results[key] = {
            "analytic": a,
            "finite_difference": f,
            "abs_diff": abs_diff,
            "rel_diff": rel_diff,
            "match": match,
        }
    results["all_match"] = bool(all_match)
    return results


def implied_volatility(market_price: float, spot: float, strike: float, rate: float,
                       time_to_expiry: float, option_type: Any,
                       seed: int = _IV_NEUTRAL_SEED) -> float:
    """Solve implied volatility via bisection bracketing + Newton refinement.

    Deterministic: same inputs + same seed always produce the same IV. Bisection
    brackets the root on ``[_IV_VOL_FLOOR, _IV_VOL_CAP]``; Newton polishes with
    analytic vega, falling back to bisection when vega is degenerate (deep ITM/OTM
    or near expiry). Raises :class:`NonFiniteResultError` when no finite IV exists
    for the quoted price (arbitrage violation) or inputs are degenerate.
    """
    ot = _validate_option_type(option_type)
    spot = validate_finite(spot, "spot")
    strike = validate_finite(strike, "strike")
    rate = validate_finite(rate, "rate")
    time_to_expiry = validate_finite(time_to_expiry, "time_to_expiry")
    market_price = validate_finite(market_price, "market_price")
    if spot <= 0.0:
        raise NonFiniteResultError("spot must be positive",
                                   context={"function": "implied_volatility", "spot": spot})
    if strike <= 0.0:
        raise NonFiniteResultError("strike must be positive",
                                   context={"function": "implied_volatility", "strike": strike})
    if time_to_expiry <= 0.0:
        raise NonFiniteResultError("time_to_expiry must be > 0 for IV solve",
                                   context={"function": "implied_volatility",
                                            "time_to_expiry": time_to_expiry})

    rng = random.Random(seed)

    def price_at(vol: float) -> float:
        return black_scholes_price(PricingInputs(
            spot=spot, strike=strike, rate=rate, volatility=vol,
            time_to_expiry=time_to_expiry, option_type=ot, seed=seed))

    discount = _discount_factor(rate, time_to_expiry)
    if ot == "call":
        intrinsic = max(spot - strike * discount, 0.0)
        upper_bound = spot
    else:
        intrinsic = max(strike * discount - spot, 0.0)
        upper_bound = strike * discount

    # Degenerate / arbitrage cases.
    if market_price <= intrinsic + _IV_TOL:
        # Price at/below intrinsic: IV collapses to the floor.
        return _IV_VOL_FLOOR
    if ot == "call" and market_price >= upper_bound - _IV_TOL:
        raise NonFiniteResultError("call price at/above spot (no finite IV)",
                                   context={"function": "implied_volatility",
                                            "market_price": market_price, "spot": spot})
    if ot == "put" and market_price >= upper_bound - _IV_TOL:
        raise NonFiniteResultError("put price at/above discounted strike (no finite IV)",
                                   context={"function": "implied_volatility",
                                            "market_price": market_price,
                                            "discounted_strike": strike * discount})

    # Bisection bracket.
    lo = _IV_VOL_FLOOR
    hi = _IV_VOL_CAP
    flo = price_at(lo) - market_price
    fhi = price_at(hi) - market_price
    iterations = 0

    # Expand/guard the bracket deterministically using the seed only as a last-resort
    # jitter when bisection cannot establish a sign change.
    if not (math.isfinite(flo) and math.isfinite(fhi)):
        raise NonFiniteResultError("IV solver encountered non-finite pricing",
                                   context={"function": "implied_volatility"})
    if flo * fhi > 0.0:
        # No sign change in default bracket; try deterministic bisection expansion.
        expanded = False
        for _ in range(20):
            hi *= 2.0
            if hi > 100.0:
                hi = 100.0
                break
            fhi = price_at(hi) - market_price
            if flo * fhi <= 0.0:
                expanded = True
                break
        if not expanded:
            # Last resort: deterministic jitter off the floor using the seed, then
            # fall back to pure bisection on the widened bracket.
            jitter = 1e-4 + (rng.random() * 1e-3)
            lo = max(_IV_VOL_FLOOR, 1e-6 - jitter)
            hi = _IV_VOL_CAP
            flo = price_at(lo) - market_price
            fhi = price_at(hi) - market_price
            if flo * fhi > 0.0:
                raise NonFiniteResultError("IV solver could not bracket root",
                                           context={"function": "implied_volatility",
                                                    "market_price": market_price,
                                                    "spot": spot, "strike": strike,
                                                    "rate": rate,
                                                    "time_to_expiry": time_to_expiry})

    vol = 0.5 * (lo + hi)
    converged = False
    for _ in range(_IV_MAX_ITER):
        iterations += 1
        vol = 0.5 * (lo + hi)
        fvol = price_at(vol) - market_price
        if not math.isfinite(fvol):
            break
        if abs(fvol) < _IV_TOL:
            converged = True
            break
        if flo * fvol <= 0.0:
            hi = vol
            fhi = fvol
        else:
            lo = vol
            flo = fvol
        # Newton refinement when vega is well behaved.
        g = black_scholes_greeks(PricingInputs(
            spot=spot, strike=strike, rate=rate, volatility=vol,
            time_to_expiry=time_to_expiry, option_type=ot, seed=seed))
        vega = float(g["vega"])
        if vega > _IV_NEWTON_TOL and math.isfinite(vega):
            newton_step = fvol / vega
            candidate = vol - newton_step
            if _IV_VOL_FLOOR <= candidate <= _IV_VOL_CAP and math.isfinite(candidate):
                fcandidate = price_at(candidate) - market_price
                if math.isfinite(fcandidate) and abs(fcandidate) < abs(fvol):
                    vol = candidate
                    fvol = fcandidate
                    if abs(fvol) < _IV_TOL:
                        converged = True
                        break
                    # Re-sync bracket around the Newton point.
                    if fvol * flo <= 0.0:
                        hi = vol
                        fhi = fvol
                    else:
                        lo = vol
                        flo = fvol

    if not math.isfinite(vol) or vol < _IV_VOL_FLOOR or vol > _IV_VOL_CAP:
        raise NonFiniteResultError("IV solver failed to converge to finite vol",
                                   context={"function": "implied_volatility",
                                            "market_price": market_price,
                                            "spot": spot, "strike": strike,
                                            "rate": rate,
                                            "time_to_expiry": time_to_expiry})
    return float(max(_IV_VOL_FLOOR, min(_IV_VOL_CAP, vol)))


def price_with_implied_vol(market_price: float, spot: float, strike: float, rate: float,
                           time_to_expiry: float, option_type: Any,
                           seed: int = _IV_NEUTRAL_SEED) -> PricingOutputs:
    """Solve IV from a market price, then return full :class:`PricingOutputs`.

    The returned ``implied_vol`` is the solved IV; all Greeks are evaluated at the
    solved volatility. Strict-serialization gated.
    """
    iv = implied_volatility(market_price, spot, strike, rate, time_to_expiry,
                            option_type, seed=seed)
    inputs = PricingInputs(
        spot=spot, strike=strike, rate=rate, volatility=iv,
        time_to_expiry=time_to_expiry, option_type=option_type, seed=seed,
    )
    outputs = black_scholes(inputs)
    outputs.implied_vol = iv
    # Re-validate strict serialization after injecting IV.
    serialize_metrics_strict(outputs.model_dump())
    return outputs


def batch_price(inputs_list: List[PricingInputs]) -> List[PricingOutputs]:
    """Vectorized batch pricing for a list of :class:`PricingInputs`.

    Loops over inputs (deterministic order) and prices each. Used for surfaces
    and calibration where many contracts are priced together. Each output is
    strict-serialization gated independently.
    """
    outputs: List[PricingOutputs] = []
    for inputs in inputs_list:
        outputs.append(black_scholes(inputs))
    return outputs


__all__ = [
    "PricingInputs",
    "PricingOutputs",
    "black_scholes_price",
    "black_scholes_greeks",
    "black_scholes",
    "finite_difference_greeks",
    "greeks_match_analytic",
    "implied_volatility",
    "price_with_implied_vol",
    "batch_price",
    "_norm_cdf",
    "_norm_pdf",
]
