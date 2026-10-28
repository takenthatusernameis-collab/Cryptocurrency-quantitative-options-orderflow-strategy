"""Phase 6: Vectorization audit — numerical equivalence between vectorized
and scalar code paths across features (gamma exposure, orderflow, volatility,
liquidity). Asserts the vectorized hot paths produce identical results to the
scalar reference implementations on randomized chains/trades, and that every
public vectorized entry point is exported from src/features/__init__.py.
"""

from math import isfinite

import numpy as np
import pytest
from datetime import datetime, timezone

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, Trade

from src.features import (
    calculate_cumulative_delta,
    calculate_cumulative_delta_vectorized,
    calculate_delta_weighted_gex,
    calculate_gamma_exposure,
    calculate_iv_skew,
    calculate_iv_skew_vectorized,
    calculate_max_pain,
    calculate_max_pain_vectorized,
    calculate_oi_volume_weighted_gex,
    calculate_orderflow_imbalance,
    calculate_orderflow_imbalance_vectorized,
    calculate_put_call_ratio,
    calculate_put_call_ratio_vectorized,
    calculate_signed_volume,
    calculate_signed_volume_vectorized,
    calculate_total_delta_weighted_gex,
    calculate_total_gex,
    calculate_total_oi_volume_weighted_gex,
    calculate_chain_liquidity_metrics,
    calculate_chain_liquidity_metrics_vectorized,
)
from src.features import __all__ as features_all


RNG = np.random.default_rng(20261028)
NOW = datetime.now(timezone.utc)
SPOT = 20000.0


def _rand_quote(strike, option_type, gamma=None, delta=None, oi=None, vol=None,
                bid=100.0, ask=101.0, mark_iv=None):
    c = OptionContract(
        symbol=f"{option_type[0]}-{strike}",
        underlying="BTC",
        strike=float(strike),
        expiry=datetime(2026, 12, 25, tzinfo=timezone.utc),
        option_type=option_type,
        venue="deribit",
        contract_size=1.0,
    )
    return OptionQuote(
        contract=c,
        bid=bid,
        ask=ask,
        gamma=gamma if gamma is not None else float(RNG.uniform(0.00005, 0.0005)),
        delta=delta if delta is not None else float(RNG.uniform(-1.0, 1.0)),
        open_interest=oi if oi is not None else float(RNG.integers(0, 5000)),
        volume=vol if vol is not None else float(RNG.integers(0, 5000)),
        mark_iv=mark_iv if mark_iv is not None else float(RNG.uniform(0.4, 1.2)),
        timestamp=NOW,
    )


def _rand_chain(n_quotes=60):
    strikes = np.sort(RNG.choice(np.linspace(15000.0, 25000.0, 201), size=n_quotes, replace=False))
    types = RNG.choice(["call", "put"], size=n_quotes)
    quotes = [_rand_quote(s, t) for s, t in zip(strikes, types)]
    return OptionsChain(underlying="BTC", venue="deribit", quotes=quotes, timestamp=NOW)


def _rand_trades(n_trades=200):
    sides = RNG.choice(["buy", "sell"], size=n_trades)
    sizes = RNG.uniform(0.1, 5.0, size=n_trades)
    prices = RNG.uniform(19000.0, 21000.0, size=n_trades)
    return [
        Trade(
            trade_id=str(i),
            symbol="BTC",
            venue="deribit",
            price=float(prices[i]),
            size=float(sizes[i]),
            side=sides[i],
            timestamp=NOW,
        )
        for i in range(n_trades)
    ]


def _approx(a, b, tol=1e-9):
    if isfinite(a) and isfinite(b):
        return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
    return a == b  # both inf / both nan handled by callers


# --------------------------------------------------------------------------- #
# Gamma exposure equivalence (vectorized total vs scalar per-quote sum)
# --------------------------------------------------------------------------- #

def test_vectorized_total_gex_matches_scalar_sum():
    chain = _rand_chain()
    vectorized = calculate_total_gex(chain, SPOT)
    scalar = sum(calculate_gamma_exposure(q, SPOT) for q in chain.quotes)
    assert isfinite(vectorized) and isfinite(scalar)
    assert _approx(vectorized, scalar)


def test_vectorized_delta_weighted_gex_matches_scalar_sum():
    chain = _rand_chain()
    vectorized = calculate_total_delta_weighted_gex(chain, SPOT)
    scalar = sum(calculate_delta_weighted_gex(q, SPOT) for q in chain.quotes)
    assert isfinite(vectorized) and isfinite(scalar)
    assert _approx(vectorized, scalar)


def test_vectorized_oi_vol_weighted_gex_matches_scalar_sum():
    chain = _rand_chain()
    vectorized = calculate_total_oi_volume_weighted_gex(chain, SPOT)
    scalar = sum(calculate_oi_volume_weighted_gex(q, SPOT) for q in chain.quotes)
    assert isfinite(vectorized) and isfinite(scalar)
    assert _approx(vectorized, scalar)


def test_vectorized_gex_empty_chain():
    empty = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=NOW)
    assert calculate_total_gex(empty, SPOT) == 0.0
    assert calculate_total_delta_weighted_gex(empty, SPOT) == 0.0
    assert calculate_total_oi_volume_weighted_gex(empty, SPOT) == 0.0


# --------------------------------------------------------------------------- #
# Orderflow equivalence (vectorized vs scalar)
# --------------------------------------------------------------------------- #

def test_vectorized_cumulative_delta_matches_scalar():
    trades = _rand_trades()
    assert _approx(calculate_cumulative_delta_vectorized(trades), calculate_cumulative_delta(trades))
    assert calculate_cumulative_delta_vectorized([]) == 0.0


def test_vectorized_signed_volume_matches_scalar():
    trades = _rand_trades()
    assert _approx(calculate_signed_volume_vectorized(trades), calculate_signed_volume(trades))
    assert calculate_signed_volume_vectorized([]) == 0.0


def test_vectorized_orderflow_imbalance_matches_scalar():
    trades = _rand_trades()
    for window in (None, 10, 50, 100, 1000):
        w = len(trades) if window is None else window
        v = calculate_orderflow_imbalance_vectorized(trades, window=w)
        s = calculate_orderflow_imbalance(trades, window=w)
        assert isfinite(v) and isfinite(s)
        assert -1.0 <= v <= 1.0 and -1.0 <= s <= 1.0
        assert _approx(v, s)


# --------------------------------------------------------------------------- #
# Volatility surface equivalence (vectorized vs scalar)
# --------------------------------------------------------------------------- #

def test_vectorized_put_call_ratio_matches_scalar():
    chain = _rand_chain()
    assert _approx(calculate_put_call_ratio_vectorized(chain.quotes), calculate_put_call_ratio(chain.quotes))
    assert calculate_put_call_ratio_vectorized([]) == 0.0


def test_vectorized_iv_skew_matches_scalar():
    chain = _rand_chain()
    assert _approx(calculate_iv_skew_vectorized(chain.quotes, SPOT), calculate_iv_skew(chain.quotes, SPOT))
    assert calculate_iv_skew_vectorized([], SPOT) == 0.0


def test_vectorized_max_pain_matches_scalar():
    chain = _rand_chain()
    v = calculate_max_pain_vectorized(chain)
    s = calculate_max_pain(chain)
    assert isfinite(v) and isfinite(s)
    assert _approx(v, s)
    assert calculate_max_pain_vectorized(OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=NOW)) == 0.0


# --------------------------------------------------------------------------- #
# Liquidity equivalence (vectorized vs scalar alias)
# --------------------------------------------------------------------------- #

def test_vectorized_chain_liquidity_metrics_matches_scalar():
    chain = _rand_chain()
    v = calculate_chain_liquidity_metrics_vectorized(chain)
    s = calculate_chain_liquidity_metrics(chain)
    assert set(v.keys()) == set(s.keys())
    for k in v:
        assert isfinite(v[k]) and isfinite(s[k])
        assert _approx(v[k], s[k])


# --------------------------------------------------------------------------- #
# Exports: every public vectorized entry point reachable from src.features
# --------------------------------------------------------------------------- #

VECTORIZED_ENTRY_POINTS = [
    "calculate_cumulative_delta_vectorized",
    "calculate_signed_volume_vectorized",
    "calculate_orderflow_imbalance_vectorized",
    "calculate_put_call_ratio_vectorized",
    "calculate_iv_skew_vectorized",
    "calculate_max_pain_vectorized",
    "calculate_total_gex_vectorized",
    "calculate_total_delta_weighted_gex",
    "calculate_total_oi_volume_weighted_gex",
    "calculate_gex_by_strike_vectorized",
    "calculate_chain_liquidity_metrics_vectorized",
]


def test_vectorized_entry_points_exported():
    for name in VECTORIZED_ENTRY_POINTS:
        assert name in features_all, f"vectorized entry point not exported: {name}"
        # importable attribute
        mod = __import__("src.features", fromlist=[name])
        assert hasattr(mod, name), f"vectorized entry point not importable: {name}"


def test_no_loop_gaps_in_features_init():
    """Sanity: __init__ exposes the vectorized aliases (audit completeness)."""
    assert "calculate_total_gex_vectorized" in features_all
    assert "calculate_cumulative_delta_vectorized" in features_all
    assert "calculate_orderflow_imbalance_vectorized" in features_all
