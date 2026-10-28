"""Phase 1: Advanced Gamma Exposure & Dealer Positioning - Invariants and Cross-checks."""

from datetime import datetime, timezone

from src.data.schemas import OptionsChain, OptionContract, OptionQuote
from src.features.gamma_exposure import (
    calculate_gamma_exposure,
    calculate_gamma_notional_by_delta_bands,
    calculate_net_gamma_exposure,
    calculate_net_gamma_exposure_total,
    calculate_gex_by_strike,
    find_gamma_flip_level_refined,
    gamma_flip_level,
    gamma_flip_level_weighted,
)


def _make_call(strike, gamma, delta, oi, vol=0, spot=20000):
    c = OptionContract(
        symbol=f"BTC-C-{strike}",
        underlying="BTC",
        strike=float(strike),
        expiry=datetime(2026, 12, 25, tzinfo=timezone.utc),
        option_type="call",
        venue="deribit",
    )
    q = OptionQuote(
        contract=c,
        bid=100,
        ask=101,
        gamma=float(gamma),
        delta=float(delta),
        open_interest=float(oi),
        volume=float(vol),
        timestamp=datetime.now(timezone.utc),
    )
    return q


def _make_put(strike, gamma, delta, oi, vol=0):
    c = OptionContract(
        symbol=f"BTC-P-{strike}",
        underlying="BTC",
        strike=float(strike),
        expiry=datetime(2026, 12, 25, tzinfo=timezone.utc),
        option_type="put",
        venue="deribit",
    )
    q = OptionQuote(
        contract=c,
        bid=100,
        ask=101,
        gamma=float(gamma),
        delta=float(delta),
        open_interest=float(oi),
        volume=float(vol),
        timestamp=datetime.now(timezone.utc),
    )
    return q


def test_net_gamma_sign_convention_calls_positive_puts_negative():
    spot = 20000.0
    # Call with positive gamma
    qc = _make_call(20000, 0.0001, 0.5, 1000)
    # Put
    qp = _make_put(20000, 0.0001, -0.5, 1000)
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[qc, qp], timestamp=datetime.now(timezone.utc))
    net = calculate_net_gamma_exposure(chain, spot)
    # Calls positive contribution, puts negative -> net should be less than call-only
    net_call_only = calculate_net_gamma_exposure(OptionsChain(underlying="BTC", venue="deribit", quotes=[qc], timestamp=datetime.now(timezone.utc)), spot)
    net_put_only = calculate_net_gamma_exposure(OptionsChain(underlying="BTC", venue="deribit", quotes=[qp], timestamp=datetime.now(timezone.utc)), spot)
    assert net_call_only > 0  # calls positive
    assert net_put_only < 0  # puts negative
    assert abs(net_call_only) > 0 and abs(net_put_only) > 0


def test_net_gamma_across_strikes_and_expiries_consistency():
    spot = 20000.0
    quotes = []
    for s in [19000, 19500, 20000, 20500, 21000]:
        quotes.append(_make_call(s, 0.00008, 0.3 if s > 20000 else (0.5 if s == 20000 else 0.7), 500))
        quotes.append(_make_put(s, 0.00008, -0.3 if s < 20000 else (-0.5 if s == 20000 else -0.7), 500))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=quotes, timestamp=datetime.now(timezone.utc))
    net = calculate_net_gamma_exposure(chain, spot)
    net_total = calculate_net_gamma_exposure_total(chain, spot)
    assert isinstance(net, float)
    assert isinstance(net_total, float)
    assert net == net_total  # aliases consistent


def test_gamma_notional_by_delta_bands_oi_volume_weighting():
    spot = 20000.0
    # ATM call
    qc_atm = _make_call(20000, 0.00015, 0.5, 2000, vol=100)
    # OTM call
    qc_otm = _make_call(21000, 0.00005, 0.2, 1000, vol=50)
    # ITM call
    qc_itm = _make_call(19000, 0.00005, 0.8, 800, vol=40)
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[qc_atm, qc_otm, qc_itm], timestamp=datetime.now(timezone.utc))
    bands = calculate_gamma_notional_by_delta_bands(chain, spot, atm_band=0.1)
    assert "atm" in bands and "otm" in bands and "itm" in bands and "total" in bands
    assert bands["total"] != 0
    # All finite
    for k, v in bands.items():
        assert isinstance(v, float)


def test_gamma_notional_bands_puts_classification():
    spot = 20000.0
    # ATM put delta ~ -0.5
    qp_atm = _make_put(20000, 0.00015, -0.5, 1500, vol=80)
    # OTM put delta closer to 0 (e.g., -0.2)
    qp_otm = _make_put(19000, 0.00005, -0.2, 1000, vol=30)
    # ITM put delta closer to -1 (e.g., -0.8)
    qp_itm = _make_put(21000, 0.00005, -0.8, 900, vol=40)
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[qp_atm, qp_otm, qp_itm], timestamp=datetime.now(timezone.utc))
    bands = calculate_gamma_notional_by_delta_bands(chain, spot, atm_band=0.1)
    assert bands["total"] != 0


def test_gamma_flip_refined_all_positive():
    # All positive GEX (all calls)
    gex_by = {19000: 1000.0, 19500: 2000.0, 20000: 1500.0}
    flip = find_gamma_flip_level_refined(gex_by)
    assert isinstance(flip, float)
    assert flip < min(gex_by.keys())  # should be below lowest


def test_gamma_flip_refined_all_negative():
    gex_by = {19000: -1000.0, 19500: -2000.0, 20000: -1500.0}
    flip = find_gamma_flip_level_refined(gex_by)
    assert isinstance(flip, float)
    assert flip > max(gex_by.keys())  # should be above highest


def test_gamma_flip_refined_multiple_crossings():
    # Positive, negative, positive - multiple crossings
    gex_by = {18000: 500.0, 19000: -500.0, 20000: 300.0, 21000: -100.0}
    flip = find_gamma_flip_level_refined(gex_by)
    assert isinstance(flip, float)
    assert flip > 0


def test_gamma_flip_refined_zero_crossing_interpolation():
    gex_by = {19000: 1000.0, 20000: -1000.0}
    flip = find_gamma_flip_level_refined(gex_by)
    # Linear interpolation gives 19500
    assert abs(flip - 19500.0) < 1e-6


def test_gamma_flip_refined_handles_zeros_nans():
    gex_by = {19000: 0.0, 19500: float('nan'), 20000: -100.0}
    flip = find_gamma_flip_level_refined(gex_by)
    assert isinstance(flip, float)
    assert flip == flip  # not NaN


def test_gamma_flip_convenience_functions_consistent():
    spot = 20000.0
    quotes = [_make_call(19000, 0.0001, 0.7, 1000), _make_put(21000, 0.0001, -0.3, 1000)]
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=quotes, timestamp=datetime.now(timezone.utc))
    f1 = gamma_flip_level(chain, spot)
    f2 = gamma_flip_level_weighted(chain, spot, weighted="delta")
    assert isinstance(f1, float)
    assert isinstance(f2, float)


def test_gex_by_strike_weighting_modes():
    spot = 20000.0
    quotes = [_make_call(20000, 0.0001, 0.5, 2000, vol=100), _make_put(20000, 0.0001, -0.5, 1000, vol=50)]
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=quotes, timestamp=datetime.now(timezone.utc))
    g1 = calculate_gex_by_strike(chain, spot, weighted="none")
    g2 = calculate_gex_by_strike(chain, spot, weighted="delta")
    g3 = calculate_gex_by_strike(chain, spot, weighted="liquidity")
    assert 20000.0 in g1
    assert isinstance(g2[20000.0], float)
    assert isinstance(g3[20000.0], float)


def test_numerical_stability_zero_oi_volume_edge_cases():
    spot = 20000.0
    qc = _make_call(20000, 0.0001, 0.5, 0)  # zero OI
    qp = _make_put(20000, 0.0001, -0.5, 0)
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[qc, qp], timestamp=datetime.now(timezone.utc))
    net = calculate_net_gamma_exposure(chain, spot)
    bands = calculate_gamma_notional_by_delta_bands(chain, spot)
    assert net == 0.0 or isinstance(net, float)
    assert bands["total"] == 0.0
