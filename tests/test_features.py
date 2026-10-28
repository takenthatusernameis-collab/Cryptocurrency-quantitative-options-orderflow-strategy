from datetime import datetime, timezone

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, Trade
from src.features.gamma_exposure import (
    calculate_gamma_exposure,
    calculate_gex_by_strike,
    calculate_delta_weighted_gex,
    calculate_total_delta_weighted_gex,
    gamma_flip_level_weighted,
)
from src.features.liquidity import (
    calculate_bid_ask_spread,
    calculate_mid_price,
    calculate_relative_spread,
    calculate_liquidity_score,
    calculate_chain_liquidity_metrics,
)
from src.features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance
from src.features.volatility import calculate_put_call_ratio, calculate_max_pain


def test_gamma_exposure_calculation():
    contract = OptionContract(
        symbol="BTC-28OCT22-20000-C",
        underlying="BTC",
        strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue="deribit",
    )
    quote = OptionQuote(
        contract=contract,
        bid=100.0,
        ask=110.0,
        gamma=0.0001,
        open_interest=1000.0,
        volume=100.0,
        timestamp=datetime.now(timezone.utc),
    )
    gex = calculate_gamma_exposure(quote, 20000.0)
    assert isinstance(gex, float)


def test_delta_weighted_gex_uses_delta():
    contract = OptionContract(
        symbol="BTC-28OCT22-20000-C",
        underlying="BTC",
        strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue="deribit",
    )
    quote = OptionQuote(
        contract=contract,
        bid=100.0,
        ask=110.0,
        gamma=0.0002,
        delta=0.5,
        open_interest=500.0,
        volume=50.0,
        timestamp=datetime.now(timezone.utc),
    )
    gex = calculate_gamma_exposure(quote, 20000.0)
    gex_dw = calculate_delta_weighted_gex(quote, 20000.0)
    assert isinstance(gex_dw, float)
    assert gex_dw != 0.0 or gex == 0.0


def test_gamma_exposure_chain_delta_weighted_total():
    contract = OptionContract(
        symbol="BTC-28OCT22-20000-C",
        underlying="BTC",
        strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue="deribit",
    )
    quote = OptionQuote(
        contract=contract,
        bid=100.0,
        ask=110.0,
        gamma=0.0001,
        delta=0.6,
        open_interest=2000.0,
        volume=200.0,
        timestamp=datetime.now(timezone.utc),
    )
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[quote], timestamp=datetime.now(timezone.utc))
    total_dw = calculate_total_delta_weighted_gex(chain, 20000.0)
    assert isinstance(total_dw, float)
    assert total_dw >= 0.0  # call gives positive contribution in magnitude convention


def test_gamma_flip_level_weighted():
    c1 = OptionContract(symbol="BTC-C1", underlying="BTC", strike=19000.0, expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="call", venue="deribit")
    c2 = OptionContract(symbol="BTC-P1", underlying="BTC", strike=21000.0, expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="put", venue="deribit")
    q1 = OptionQuote(contract=c1, bid=500, ask=510, gamma=0.0001, delta=0.8, open_interest=1000, volume=10, timestamp=datetime.now(timezone.utc))
    q2 = OptionQuote(contract=c2, bid=400, ask=410, gamma=0.00015, delta=-0.3, open_interest=1500, volume=20, timestamp=datetime.now(timezone.utc))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[q1, q2], timestamp=datetime.now(timezone.utc))
    flip = gamma_flip_level_weighted(chain, 20000.0, weighted="delta")
    assert isinstance(flip, float)


def test_liquidity_metrics():
    contract = OptionContract(
        symbol="BTC-28OCT22-20000-C",
        underlying="BTC",
        strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue="deribit",
    )
    quote = OptionQuote(
        contract=contract,
        bid=100.0,
        ask=110.0,
        last=105.0,
        open_interest=1000.0,
        volume=500.0,
        timestamp=datetime.now(timezone.utc),
    )
    spread = calculate_bid_ask_spread(quote)
    mid = calculate_mid_price(quote)
    rel = calculate_relative_spread(quote)
    score = calculate_liquidity_score(quote)
    assert spread == 10.0
    assert mid == 105.0
    assert rel > 0
    assert 0 <= score <= 1
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[quote], timestamp=datetime.now(timezone.utc))
    metrics = calculate_chain_liquidity_metrics(chain)
    assert "avg_bid_ask_spread" in metrics
    assert "avg_liquidity_score" in metrics
    assert metrics["total_oi"] == 1000.0


def test_cumulative_delta():
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    delta = calculate_cumulative_delta(trades)
    assert delta == 0.5


def test_orderflow_imbalance():
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="3", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    imb = calculate_orderflow_imbalance(trades)
    assert imb == 0.5  # (1.5 - 0.5) / 2.0 = 0.5


def test_put_call_ratio():
    contracts_call = OptionContract(
        symbol="BTC-C", underlying="BTC", strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="call", venue="deribit"
    )
    contracts_put = OptionContract(
        symbol="BTC-P", underlying="BTC", strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="put", venue="deribit"
    )
    quotes = [
        OptionQuote(contract=contracts_call, bid=100, ask=110, volume=1000, timestamp=datetime.now(timezone.utc)),
        OptionQuote(contract=contracts_put, bid=90, ask=100, volume=500, timestamp=datetime.now(timezone.utc)),
    ]
    pcr = calculate_put_call_ratio(quotes)
    assert pcr == 0.5


def test_calculate_cumulative_delta_robust():
    from src.features.orderflow import calculate_cumulative_delta_robust, cumulative_delta, robust_cumulative_delta
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=2.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="sell", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="3", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="Buy", timestamp=datetime.now(timezone.utc)),
    ]
    delta = calculate_cumulative_delta_robust(trades)
    assert delta == 1.5  # 2 - 1 + 0.5
    # window
    delta_w = calculate_cumulative_delta_robust(trades, window=2)
    assert delta_w == -0.5  # last 2: -1 + 0.5
    assert calculate_cumulative_delta_robust([]) == 0.0
    assert cumulative_delta is calculate_cumulative_delta
    assert robust_cumulative_delta is calculate_cumulative_delta_robust


def test_calculate_vwap_adjusted_delta():
    from src.features.orderflow import calculate_vwap_adjusted_delta
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=21000.0, size=1.0, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    vwap_adj = calculate_vwap_adjusted_delta(trades)
    assert isinstance(vwap_adj, float)
    assert calculate_vwap_adjusted_delta([]) == 0.0
    # with non-finite values
    trades_bad = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=float('inf'), size=float('nan'), side="buy", timestamp=datetime.now(timezone.utc)),
    ]
    res = calculate_vwap_adjusted_delta(trades_bad)
    assert isinstance(res, float)


def test_calculate_delta_adjusted_flow():
    from src.features.orderflow import calculate_delta_adjusted_flow
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    res = calculate_delta_adjusted_flow(trades, spot_price=20000.0)
    assert abs(res - 0.5/20000.0) < 1e-18
    res2 = calculate_delta_adjusted_flow(trades, spot_price=None)
    assert res2 == 0.5
    res3 = calculate_delta_adjusted_flow(trades, spot_price=0)
    assert res3 == 0.5


def test_calculate_signed_volume():
    from src.features.orderflow import calculate_signed_volume
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=0.3, side="sell", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="3", symbol="BTC", venue="deribit", price=20000.0, size=0.2, side="BUY", timestamp=datetime.now(timezone.utc)),
    ]
    sv = calculate_signed_volume(trades)
    assert abs(sv - 0.9) < 1e-12
    assert calculate_signed_volume([]) == 0.0
    sv_w = calculate_signed_volume(trades, window=2)
    assert abs(sv_w - (-0.1)) < 1e-12


def test_orderflow_imbalance_multi_horizon():
    from src.features.orderflow import (
        orderflow_imbalance_multi_horizon,
        imbalance_multi_horizon,
        orderflow_imbalance_multihorizon,
        multi_horizon_orderflow_imbalance,
        calculate_orderflow_imbalance,
    )
    from math import isfinite

    trades = [
        Trade(
            trade_id=str(i),
            symbol="BTC",
            venue="deribit",
            price=20000.0,
            size=1.0,
            side="buy" if i % 3 != 0 else "sell",
            timestamp=datetime.now(timezone.utc),
        )
        for i in range(20)
    ]
    res = orderflow_imbalance_multi_horizon(trades)
    assert isinstance(res, dict)
    assert "imb_decay_weighted" in res
    assert imbalance_multi_horizon is orderflow_imbalance_multi_horizon
    assert orderflow_imbalance_multihorizon is orderflow_imbalance_multi_horizon
    assert multi_horizon_orderflow_imbalance is orderflow_imbalance_multi_horizon
    # horizons with zeros/negatives
    res2 = orderflow_imbalance_multi_horizon(trades, horizons=[0, -1, 5])
    assert "imb_decay_weighted" in res2
    res3 = orderflow_imbalance_multi_horizon([], horizons=[1, 2, 3])
    assert res3["imb_decay_weighted"] == 0.0
    assert isinstance(res, dict)
    assert "imb_decay_weighted" in res
    assert imbalance_multi_horizon is orderflow_imbalance_multi_horizon
    assert orderflow_imbalance_multihorizon is orderflow_imbalance_multi_horizon
    assert multi_horizon_orderflow_imbalance is orderflow_imbalance_multi_horizon
    # horizons with zeros/negatives
    res2 = orderflow_imbalance_multi_horizon(trades, horizons=[0, -1, 5])
    assert "imb_decay_weighted" in res2
    res3 = orderflow_imbalance_multi_horizon([], horizons=[1, 2, 3])
    assert res3["imb_decay_weighted"] == 0.0

    # Property/invariants: all values in [-1,1], decay weighted normalized
    res4 = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 50, 100])
    for k, v in res4.items():
        if isinstance(v, float):
            assert -1.0 - 1e-12 <= v <= 1.0 + 1e-12
            assert isfinite(v)
    # Cross-consistency with calculate_orderflow_imbalance
    for h in [1, 10, 50]:
        assert abs(res4.get(f"imb_{h}", 0.0) - calculate_orderflow_imbalance(trades, window=h)) < 1e-12
    # Mean and decay weighted exist
    assert "imb_mean" in res4
    # Decay behavior: shorter horizons get more weight if ordered as given
    # Edge cases
    trades_all_buy = [
        Trade(trade_id=str(i), symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc))
        for i in range(10)
    ]
    res_buy = orderflow_imbalance_multi_horizon(trades_all_buy, horizons=[1, 5, 10])
    assert res_buy["imb_decay_weighted"] >= 0.99  # all buys -> imbalance ~1
    # All sells
    trades_all_sell = [
        Trade(trade_id=str(i), symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="sell", timestamp=datetime.now(timezone.utc))
        for i in range(10)
    ]
    res_sell = orderflow_imbalance_multi_horizon(trades_all_sell, horizons=[1, 5, 10])
    assert res_sell["imb_decay_weighted"] <= -0.99
    # Decay parameter
    res_d1 = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 100], decay=0.1)
    res_d2 = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 100], decay=1.0)
    assert "imb_decay_weighted" in res_d1 and "imb_decay_weighted" in res_d2
    # Non-finite/invalid inputs
    from math import inf, nan
    trades_bad = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=inf, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=nan, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    res_bad = orderflow_imbalance_multi_horizon(trades_bad, horizons=[1, 2])
    for v in res_bad.values():
        if isinstance(v, float):
            assert isfinite(v)
            assert -1.0 <= v <= 1.0


def test_delta_divergence_vs_price():
    from src.features.orderflow import delta_divergence_vs_price
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20100.0, size=0.5, side="buy", timestamp=datetime.now(timezone.utc)),
    ]
    div = delta_divergence_vs_price(trades, price_series=[20000.0, 20100.0])
    assert isinstance(div, float)
    div2 = delta_divergence_vs_price([], price_series=[1,2])
    assert div2 == 0.0
    div3 = delta_divergence_vs_price(trades, price_series=[20000.0])
    assert isinstance(div3, float)


def test_absorption_detection():
    from src.features.orderflow import absorption_detection
    trades = [
        Trade(trade_id=str(i), symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc))
        for i in range(10)
    ]
    trades[0] = Trade(trade_id="0", symbol="BTC", venue="deribit", price=20000.0, size=5.0, side="buy", timestamp=datetime.now(timezone.utc))
    res = absorption_detection(trades, threshold=2.0)
    assert isinstance(res, float)
    assert absorption_detection([]) == 0.0
    assert absorption_detection([trades[0]], threshold=2.0) == 0.0  # < 3


def test_vpin_style_toxicity():
    from src.features.orderflow import vpin_style_toxicity, vpin_toxicity
    trades = []
    for i in range(200):
        side = "buy" if i % 2 == 0 else "sell"
        trades.append(Trade(trade_id=str(i), symbol="BTC", venue="deribit", price=20000.0 + i*0.1, size=1.0, side=side, timestamp=datetime.now(timezone.utc)))
    res = vpin_style_toxicity(trades, bucket_size=50)
    assert isinstance(res, float)
    assert 0.0 <= res <= 1.0
    assert vpin_toxicity is vpin_style_toxicity
    assert vpin_style_toxicity([], bucket_size=50) == 0.0
    # small number of trades
    small = trades[:10]
    assert vpin_style_toxicity(small, bucket_size=50) == 0.0


def test_detect_aggressive_flow():
    from src.features.orderflow import detect_aggressive_flow, trade_intensity
    trades = []
    for i in range(50):
        trades.append(Trade(trade_id=str(i), symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy" if i < 40 else "sell", timestamp=datetime.now(timezone.utc)))
    # make some aggressive
    trades[0] = Trade(trade_id="0", symbol="BTC", venue="deribit", price=20000.0, size=10.0, side="buy", timestamp=datetime.now(timezone.utc))
    res = detect_aggressive_flow(trades, window=50)
    assert isinstance(res, float)
    assert -1.0 <= res <= 1.0
    assert trade_intensity is detect_aggressive_flow
    assert detect_aggressive_flow([]) == 0.0
    assert detect_aggressive_flow([trades[0]]) == 0.0


def test_orderflow_edge_cases_non_finite():
    from src.features.orderflow import (
        calculate_cumulative_delta,
        calculate_cumulative_delta_robust,
        calculate_vwap_adjusted_delta,
        calculate_signed_volume,
        calculate_orderflow_imbalance,
    )
    # non-finite sizes
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=float('nan'), side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=float('inf'), side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    # Our functions may not filter all these; ensure they return finite values
    for fn in [calculate_cumulative_delta, calculate_cumulative_delta_robust, calculate_vwap_adjusted_delta, calculate_signed_volume]:
        res = fn(trades)
        assert isinstance(res, float)
        assert res == res  # not nan
    res = calculate_orderflow_imbalance(trades)
    assert isinstance(res, float)


def test_orderflow_imbalance_multi_horizon_production_hardening():
    from math import inf, nan, isfinite

    from src.features.orderflow import (
        orderflow_imbalance_multi_horizon,
        calculate_orderflow_imbalance,
    )

    def mk_trades(sides_sizes):
        return [
            Trade(
                trade_id=str(i),
                symbol="BTC",
                venue="deribit",
                price=20000.0,
                size=sz,
                side=sd,
                timestamp=datetime.now(timezone.utc),
            )
            for i, (sd, sz) in enumerate(sides_sizes)
        ]

    # --- normalization invariants: all numeric outputs finite and in [-1, 1] ---
    trades = mk_trades([("buy", 1.0), ("sell", 0.5), ("buy", 1.0), ("sell", 1.5)] * 5)
    res = orderflow_imbalance_multi_horizon(trades, horizons=[1, 5, 10, 50, 100], decay=0.3)
    for k, v in res.items():
        if isinstance(v, float):
            assert isfinite(v), f"{k} non-finite: {v}"
            assert -1.0 <= v <= 1.0, f"{k} out of range: {v}"
        elif isinstance(v, list):
            for x in v:
                assert isfinite(x) and -1.0 <= x <= 1.0, f"{k} weight out of range: {x}"

    # --- decay weights sum to 1 ---
    w = res["decay_weights"]
    assert abs(sum(w) - 1.0) < 1e-12
    assert all(0.0 <= x <= 1.0 for x in w)

    # --- cross-consistency: imb_h == calculate_orderflow_imbalance(window=h) ---
    for h in [1, 5, 10, 50, 100]:
        assert abs(res[f"imb_{h}"] - calculate_orderflow_imbalance(trades, window=h)) < 1e-12
        assert res[f"imb_{h}"] == res[f"orderflow_imbalance_{h}"]

    # --- all buys / all sells near +/-1 ---
    all_buy = mk_trades([("buy", 1.0)] * 10)
    res_buy = orderflow_imbalance_multi_horizon(all_buy, horizons=[1, 5, 10])
    assert res_buy["imb_decay_weighted"] >= 0.99
    all_sell = mk_trades([("sell", 1.0)] * 10)
    res_sell = orderflow_imbalance_multi_horizon(all_sell, horizons=[1, 5, 10])
    assert res_sell["imb_decay_weighted"] <= -0.99

    # --- decay behavior: higher decay shifts weight toward shorter horizons ---
    res_d_low = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 100], decay=0.1)
    res_d_high = orderflow_imbalance_multi_horizon(trades, horizons=[1, 10, 100], decay=1.0)
    assert isfinite(res_d_low["imb_decay_weighted"])
    assert isfinite(res_d_high["imb_decay_weighted"])
    assert res_d_high["decay_weights"][0] > res_d_low["decay_weights"][0]

    # --- empty / None / invalid inputs ---
    assert orderflow_imbalance_multi_horizon(None)["imb_decay_weighted"] == 0.0
    assert orderflow_imbalance_multi_horizon([], horizons=[1, 2, 3])["imb_decay_weighted"] == 0.0
    res_inv = orderflow_imbalance_multi_horizon(trades, horizons=[0, -1, "x", 2.5, None])
    assert "imb_2" in res_inv  # only valid positive int (2.5 -> 2) survives sanitization

    # --- mixed NaN/inf sizes filtered; outputs finite ---
    trades_bad = mk_trades([("buy", inf), ("sell", nan), ("buy", 1.0), ("sell", 1.0)])
    res_bad = orderflow_imbalance_multi_horizon(trades_bad, horizons=[1, 2])
    for v in res_bad.values():
        if isinstance(v, float):
            assert isfinite(v) and -1.0 <= v <= 1.0

    # --- horizon larger than number of trades ---
    res_big = orderflow_imbalance_multi_horizon(trades[:3], horizons=[1000])
    assert isfinite(res_big["imb_1000"]) and -1.0 <= res_big["imb_1000"] <= 1.0

    # --- single horizon ---
    res_one = orderflow_imbalance_multi_horizon(trades, horizons=[7])
    assert "imb_7" in res_one and isfinite(res_one["imb_decay_weighted"])

    # --- invalid decay clamped (nan / negative / huge) ---
    res_nd = orderflow_imbalance_multi_horizon(trades, horizons=[1, 2], decay=nan)
    assert isfinite(res_nd["imb_decay_weighted"])
    res_neg = orderflow_imbalance_multi_horizon(trades, horizons=[1, 2], decay=-5.0)
    assert isfinite(res_neg["imb_decay_weighted"])
    res_huge = orderflow_imbalance_multi_horizon(trades, horizons=[1, 2], decay=1e6)
    assert isfinite(res_huge["imb_decay_weighted"])
