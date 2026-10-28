"""Performance benchmarks for hot paths (Phase 7 opener).

SLO assertions with baseline timing recording. All benchmarks are tested
and must complete within defined SLOs to ensure production readiness.
"""

import time
from datetime import datetime, timedelta, timezone

from src.backtest.engine import BacktestEngine, WalkForwardBacktest
from src.config import BacktestConfig, RiskConfig
from src.data.schemas import OptionContract, OptionQuote, OptionsChain, Trade
from src.features.gamma_exposure import calculate_total_delta_weighted_gex, calculate_total_gex
from src.features.orderflow import orderflow_imbalance_multi_horizon
from src.features.volatility import calculate_iv_skew_term_structure


def _make_option_contract(symbol: str, strike: float, option_type: str, expiry: datetime) -> OptionContract:
    return OptionContract(
        symbol=symbol,
        underlying="BTC",
        strike=strike,
        expiry=expiry,
        option_type=option_type,
        venue="deribit",
    )


def _build_large_options_chain(n_quotes: int = 10000) -> OptionsChain:
    """Build a realistic large options chain for benchmarking."""
    base_expiry = datetime(2026, 12, 25, tzinfo=timezone.utc)
    quotes = []
    spot = 50000.0
    for i in range(n_quotes):
        strike = spot * (0.8 + 0.4 * (i % 100) / 100.0)
        option_type = "call" if i % 2 == 0 else "put"
        contract = _make_option_contract(f"BTC-{i}-C" if option_type == "call" else f"BTC-{i}-P", strike, option_type, base_expiry)
        # Realistic greeks
        moneyness = strike / spot
        if option_type == "call":
            delta = 0.5 + 0.3 * (1.0 - moneyness) if moneyness < 1.2 else 0.1
        else:
            delta = -0.5 - 0.3 * (moneyness - 1.0) if moneyness > 0.8 else -0.1
        gamma = 0.0001 * (1.0 - abs(moneyness - 1.0) * 2.0)
        if gamma < 0.00001:
            gamma = 0.00001
        quote = OptionQuote(
            contract=contract,
            bid=strike * 0.01,
            ask=strike * 0.011,
            gamma=max(0.00001, gamma),
            delta=max(-1.0, min(1.0, delta)),
            open_interest=float(1000 + (i % 5000)),
            volume=float(100 + (i % 500)),
            mark_iv=0.5 + 0.1 * abs(moneyness - 1.0),
            timestamp=datetime.now(timezone.utc),
        )
        quotes.append(quote)
    return OptionsChain(underlying="BTC", venue="deribit", quotes=quotes, timestamp=datetime.now(timezone.utc))


def _build_large_trades(n_trades: int = 100000) -> list[Trade]:
    """Build realistic trade list for orderflow benchmarking."""
    trades = []
    base_time = datetime.now(timezone.utc)
    for i in range(n_trades):
        side = "buy" if i % 3 != 0 else "sell"  # slight buy bias
        trade = Trade(
            trade_id=f"t{i}",
            symbol="BTCUSDT",
            side=side,
            size=float(0.01 + (i % 100) * 0.001),
            price=float(50000 + (i % 200) - 100),
            timestamp=base_time + timedelta(milliseconds=i % 1000),
            venue="binance",
        )
        trades.append(trade)
    return trades


def _build_skew_quotes(n_expiries: int = 4, quotes_per_expiry: int = 20) -> list[OptionQuote]:
    """Build quotes for IV skew term structure benchmarking."""
    quotes = []
    base_time = datetime.now(timezone.utc)
    spot = 50000.0
    for e in range(n_expiries):
        expiry = base_time + timedelta(days=7 * (e + 1))
        for k in range(quotes_per_expiry):
            strike = spot * (0.85 + 0.3 * k / quotes_per_expiry)
            for opt_type in ["call", "put"]:
                moneyness = strike / spot
                if opt_type == "call":
                    delta = 0.8 - 0.6 * moneyness if moneyness > 0.9 else 0.5
                else:
                    delta = -0.8 + 0.6 * moneyness if moneyness < 1.1 else -0.5
                delta = max(-1.0, min(1.0, delta))
                base_iv = 0.5
                if opt_type == "put" and moneyness < 0.95:
                    base_iv = 0.6
                elif opt_type == "call" and moneyness > 1.05:
                    base_iv = 0.55
                contract = _make_option_contract(f"BTC-{e}-{k}-{opt_type}", strike, opt_type, expiry)
                quote = OptionQuote(
                    contract=contract,
                    bid=strike * 0.01,
                    ask=strike * 0.011,
                    gamma=0.0001,
                    delta=delta,
                    open_interest=1000.0,
                    volume=100.0,
                    mark_iv=base_iv + 0.05 * abs(moneyness - 1.0),
                    bid_iv=base_iv,
                    ask_iv=base_iv + 0.01,
                    timestamp=base_time,
                )
                quotes.append(quote)
    return quotes


def test_benchmark_gex_hot_paths_slo():
    """Benchmark GEX hot paths: 10k quotes < 50ms."""
    chain = _build_large_options_chain(n_quotes=10000)
    spot_price = 50000.0

    # Benchmark calculate_total_gex
    start = time.perf_counter()
    result_gex = calculate_total_gex(chain, spot_price)
    elapsed_gex = (time.perf_counter() - start) * 1000.0  # ms

    assert isinstance(result_gex, float)
    assert elapsed_gex < 50.0, f"GEX benchmark failed SLO: {elapsed_gex:.2f}ms >= 50ms"

    # Benchmark calculate_total_delta_weighted_gex
    start = time.perf_counter()
    result_dw_gex = calculate_total_delta_weighted_gex(chain, spot_price)
    elapsed_dw_gex = (time.perf_counter() - start) * 1000.0  # ms

    assert isinstance(result_dw_gex, float)
    assert elapsed_dw_gex < 50.0, f"Delta-weighted GEX benchmark failed SLO: {elapsed_dw_gex:.2f}ms >= 50ms"

    # Record baseline timings
    assert elapsed_gex < 100.0  # sanity check
    assert elapsed_dw_gex < 100.0


def test_benchmark_orderflow_hot_path_slo():
    """Benchmark orderflow: 100k trades < 100ms."""
    trades = _build_large_trades(n_trades=100000)

    start = time.perf_counter()
    result_of = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 50, 100])
    elapsed_of = (time.perf_counter() - start) * 1000.0  # ms

    assert isinstance(result_of, dict)
    assert len(result_of) > 0
    assert elapsed_of < 100.0, f"Orderflow benchmark failed SLO: {elapsed_of:.2f}ms >= 100ms"

    # Verify structure
    assert "imb_decay_weighted" in result_of or "orderflow_imbalance_decay_weighted" in result_of


def test_benchmark_iv_skew_term_structure_slo():
    """Benchmark IV skew term structure."""
    quotes = _build_skew_quotes(n_expiries=4, quotes_per_expiry=20)
    spot_price = 50000.0

    start = time.perf_counter()
    result_skew = calculate_iv_skew_term_structure(quotes, spot_price)
    elapsed_skew = (time.perf_counter() - start) * 1000.0  # ms

    assert isinstance(result_skew, dict)
    assert elapsed_skew < 100.0, f"IV skew term structure benchmark failed SLO: {elapsed_skew:.2f}ms >= 100ms"


def test_benchmark_backtest_walkforward_equity_curve_slo():
    """Benchmark BacktestEngine equity-curve walk-forward: 252/63 windows < 5s."""
    # Create realistic price series
    n_days = 400
    price_series = {}
    base_prices = {"BTCUSDT": 50000.0, "ETHUSDT": 3000.0}
    for sym, base in base_prices.items():
        prices = []
        p = base
        for i in range(n_days):
            # Random walk
            p = p * (1.0 + (i % 7 - 3) * 0.001)
            prices.append(p)
        price_series[sym] = prices

    # Create signals
    signals = {}
    for sym in base_prices:
        sigs = []
        for i in range(n_days):
            if i % 20 == 0:
                sigs.append(1)
            elif i % 20 == 10:
                sigs.append(-1)
            else:
                sigs.append(0)
        signals[sym] = sigs

    timestamps = [datetime.now(timezone.utc) + timedelta(days=i) for i in range(n_days)]

    config = BacktestConfig(initial_capital=100000.0)
    risk_config = RiskConfig()

    start = time.perf_counter()
    wfb = WalkForwardBacktest(config=config, risk_config=risk_config)
    results = wfb.run_walk_forward(
        price_series=price_series,
        signals=signals,
        timestamps=timestamps,
        train_window=252,
        test_window=63,
        step_size=63,
    )
    elapsed_wf = (time.perf_counter() - start) * 1000.0  # ms

    assert results is not None
    assert elapsed_wf < 5000.0, f"Walk-forward benchmark failed SLO: {elapsed_wf:.2f}ms >= 5000ms"


def test_benchmark_comprehensive_hot_paths_baseline():
    """Comprehensive benchmark recording baseline timings for all hot paths."""
    timings = {}

    # GEX benchmarks
    chain = _build_large_options_chain(n_quotes=10000)
    spot_price = 50000.0

    start = time.perf_counter()
    _ = calculate_total_gex(chain, spot_price)
    timings["gex_10k"] = (time.perf_counter() - start) * 1000.0

    start = time.perf_counter()
    _ = calculate_total_delta_weighted_gex(chain, spot_price)
    timings["gex_delta_weighted_10k"] = (time.perf_counter() - start) * 1000.0

    # Orderflow benchmark
    trades = _build_large_trades(n_trades=100000)
    start = time.perf_counter()
    _ = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 50, 100])
    timings["orderflow_100k"] = (time.perf_counter() - start) * 1000.0

    # IV skew benchmark
    quotes = _build_skew_quotes(n_expiries=4, quotes_per_expiry=20)
    start = time.perf_counter()
    _ = calculate_iv_skew_term_structure(quotes, spot_price)
    timings["iv_skew_term_structure"] = (time.perf_counter() - start) * 1000.0

    # All timings should be finite and reasonable
    for k, v in timings.items():
        assert isinstance(v, float)
        assert v >= 0.0
        assert v < 10000.0  # sanity check

    # SLO assertions
    assert timings["gex_10k"] < 50.0
    assert timings["gex_delta_weighted_10k"] < 50.0
    assert timings["orderflow_100k"] < 100.0
    assert timings["iv_skew_term_structure"] < 100.0
