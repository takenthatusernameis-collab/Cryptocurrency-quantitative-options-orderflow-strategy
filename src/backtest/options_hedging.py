"""Delta-hedged options backtesting and P&L attribution.

Provides delta-hedged options P&L with dynamic rebalancing, hedge P&L,
theta/gamma P&L decomposition, and attribution across delta/gamma/vega/theta
with residual. All metrics finite-guarded and strict-serializable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from ..data.schemas import PricingInputs
from ..errors import BacktestError, NonFiniteResultError
from ..features.options_pricing import black_scholes, black_scholes_greeks
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, validate_finite


@dataclass
class HedgeStep:
    time: float  # years
    spot: float
    option_price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    stock_position: float  # shares held for delta hedge (short call => long delta shares? delta hedge convention)
    cash: float
    portfolio_value: float


def delta_hedged_option_pnl(
    spot_path: List[float],
    times: List[float],
    strike: float,
    rate: float,
    volatility: float,
    option_type: str,
    option_price_entry: Optional[float] = None,
    transaction_cost_bps: float = 0.0,
    rebalance_every_step: bool = True,
    seed: int = 42,
) -> Dict[str, Any]:
    """Simulate delta-hedged European option P&L path with P&L attribution.

    Convention: short 1 option, delta-hedge with underlying stock to be delta neutral.
    Rebalance at each step (or as specified). Returns attribution sums.
    """
    if len(spot_path) != len(times):
        raise BacktestError("spot_path and times must have same length",
                            context={"len_spot": len(spot_path), "len_times": len(times)})
    if len(spot_path) < 2:
        raise BacktestError("Need at least 2 points for delta-hedged simulation")
    # Entry
    t0 = float(times[0])
    s0 = float(spot_path[0])
    if t0 < 0.0:
        t0 = 0.0
    # Get entry price
    if option_price_entry is None:
        inp0 = PricingInputs(spot=s0, strike=float(strike), rate=float(rate),
                             volatility=float(volatility), time_to_expiry=max(t0, 1e-18),
                             option_type=option_type, seed=seed)
        out0 = black_scholes(inp0)
        option_price_entry = float(out0.price)
    else:
        option_price_entry = float(option_price_entry)
    # Short option: receive premium
    cash = float(option_price_entry)
    # Initial delta hedge
    inp_d = PricingInputs(spot=s0, strike=float(strike), rate=float(rate),
                          volatility=float(volatility), time_to_expiry=max(t0, 1e-18),
                          option_type=option_type, seed=seed)
    g0 = black_scholes_greeks(inp_d)
    delta0 = float(g0["delta"])
    # To delta hedge short option (delta_option), need +delta_option * shares?
    # Short call has negative delta exposure? delta of call positive, short call => delta negative position
    # Hedge by holding -delta_option_shares * delta? Better: stock_pos = -delta_option (for short 1 option)
    stock_pos = -delta0  # long stock if delta positive
    # Transaction cost on hedge
    if transaction_cost_bps > 0.0 and abs(stock_pos) > 0.0:
        cost = abs(stock_pos * s0) * (float(transaction_cost_bps) / 10000.0)
        cash -= cost
    # Track
    steps: List[HedgeStep] = []
    portfolio_values = []
    for i in range(len(spot_path)):
        t = float(times[i])
        s = float(spot_path[i])
        T = max(t, 1e-18) if i == len(spot_path) - 1 else max(t, 1e-18)  # keep time structure
        # price option
        inp_cur = PricingInputs(spot=s, strike=float(strike), rate=float(rate),
                                volatility=float(volatility), time_to_expiry=max(times[i], 1e-18) if times[i] >= 0 else 1e-18,
                                option_type=option_type, seed=seed)
        try:
            out_cur = black_scholes(inp_cur)
            opt_price = float(out_cur.price)
            g_cur = black_scholes_greeks(inp_cur)
        except Exception as e:
            raise NonFiniteResultError("Failed to price in hedge simulation", cause=e)
        # Mark to market
        option_value = -opt_price  # short option
        stock_value = stock_pos * s
        port_val = cash + stock_value + option_value
        portfolio_values.append(port_val)
        steps.append(HedgeStep(time=times[i], spot=s, option_price=opt_price,
                               delta=float(g_cur["delta"]), gamma=float(g_cur["gamma"]),
                               vega=float(g_cur["vega"]), theta=float(g_cur["theta"]),
                               stock_position=stock_pos, cash=cash,
                               portfolio_value=port_val))
        # Rebalance if not last
        if rebalance_every_step and i < len(spot_path) - 1:
            new_delta = float(g_cur["delta"])
            new_stock = -new_delta
            trade = new_stock - stock_pos
            if abs(trade) > 1e-18:
                cash -= trade * s  # buy/sell stock
                if transaction_cost_bps > 0.0:
                    cash -= abs(trade * s) * (float(transaction_cost_bps) / 10000.0)
                stock_pos = new_stock
    # Final value
    final_port = portfolio_values[-1] if portfolio_values else cash
    initial_port = portfolio_values[0] if portfolio_values else (option_price_entry - 0.0)  # rough
    total_pnl = final_port - (option_price_entry)  # compare to premium received (cash position basis)
    # Better attribution: use discrete approximation
    # Compute components
    delta_pnl = 0.0
    gamma_pnl = 0.0
    theta_pnl = 0.0
    vega_pnl = 0.0
    # Simple discrete decomposition
    for i in range(1, len(steps)):
        ds = steps[i].spot - steps[i - 1].spot
        dt = steps[i].time - steps[i - 1].time  # dt can be negative if going forward? times are forward; use abs or signed carefully
        dvol = 0.0  # assume constant vol
        # delta contribution on stock position
        delta_pnl += steps[i - 1].stock_position * ds + steps[i - 1].delta * ds  # rough hedge contribution
        gamma_pnl += 0.5 * steps[i - 1].gamma * (ds * ds)
        if dt != 0.0:
            theta_pnl += steps[i - 1].theta * dt
        vega_pnl += steps[i - 1].vega * dvol
    residual = total_pnl - (delta_pnl + gamma_pnl + theta_pnl + vega_pnl)
    attribution = {
        "delta_pnl": float(delta_pnl),
        "gamma_pnl": float(gamma_pnl),
        "theta_pnl": float(theta_pnl),
        "vega_pnl": float(vega_pnl),
        "residual": float(residual),
        "total_pnl": float(total_pnl),
        "sum_attribution": float(delta_pnl + gamma_pnl + theta_pnl + vega_pnl + residual),
    }
    result = {
        "total_pnl": float(total_pnl),
        "final_portfolio_value": float(final_port),
        "initial_option_premium": float(option_price_entry),
        "attribution": attribution,
        "hedge_steps": len(steps),
        "transaction_cost_bps": float(transaction_cost_bps),
    }
    return serialize_metrics_strict(result)
