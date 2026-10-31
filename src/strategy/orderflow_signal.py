"""Orderflow-based trading signal."""

from typing import Dict, Any

from ..data.schemas import OptionsChain, OrderflowSnapshot
from ..features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance
from ..features.volatility import calculate_put_call_ratio, calculate_iv_skew, calculate_max_pain


def generate_orderflow_signal(
    orderflow: OrderflowSnapshot,
    options_chain: OptionsChain,
    spot: float,
    threshold: float = 0.001,
) -> Dict[str, Any]:
    """Generate trading signal from orderflow and options data."""
    cum_delta = calculate_cumulative_delta(orderflow.trades)
    of_imb = calculate_orderflow_imbalance(orderflow.trades)
    pcr = calculate_put_call_ratio(options_chain.quotes)
    iv_skew = calculate_iv_skew(options_chain.quotes, spot)
    max_pain = calculate_max_pain(options_chain)

    # More flexible for synthetic/testing
    signal = 0  # -1 sell, 0 neutral, 1 buy
    strength = abs(of_imb)

    if of_imb > threshold:
        signal = 1
        strength = min(strength, 1.0)
    elif of_imb < -threshold:
        signal = -1
        strength = min(abs(strength), 1.0)
    elif cum_delta > 0:
        signal = 1
        strength = 0.1
    elif cum_delta < 0:
        signal = -1
        strength = 0.1

    return {
        "signal": signal,
        "strength": strength,
        "cum_delta": cum_delta,
        "orderflow_imbalance": of_imb,
        "put_call_ratio": pcr,
        "iv_skew": iv_skew,
        "max_pain": max_pain,
    }
