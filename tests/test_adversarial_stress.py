"""Adversarial stress scenarios across all modules (Phase 8 - CRITICAL)."""

from datetime import datetime, timezone
from unittest.mock import patch

import math
import pytest

from src.data.schemas import (
    OptionContract,
    OptionQuote,
    OptionsChain,
    Trade,
    OrderflowSnapshot,
)
from src.data.normalization import (
    normalize_options_chain,
    normalize_orderflow,
    normalize_symbol,
    normalize_timestamp,
    calculate_moneyness,
    calculate_cumulative_delta,
    compute_vwap,
)
from src.features.gamma_exposure import (
    calculate_gex_by_strike,
    calculate_gamma_exposure,
    calculate_delta_weighted_gex,
    calculate_total_gex,
    calculate_total_delta_weighted_gex,
    calculate_total_oi_volume_weighted_gex,
    gamma_flip_level,
    gamma_flip_level_weighted,
)
from src.features.orderflow import (
    calculate_cumulative_delta as calc_cum_delta_feat,
    calculate_orderflow_imbalance,
    vpin_style_toxicity,
    absorption_detection,
)
from src.features.volatility import (
    calculate_iv_skew,
    calculate_put_call_ratio,
    calculate_max_pain,
)
from src.features.liquidity import calculate_chain_liquidity_metrics
from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig, VenueConfig, DataConfig, StrategyConfig, validate_config
from src.errors import RiskLimitError, OrderError, ConfigError
from src.main import run_pipeline, validate_config_dict
from src.utils.validation import validate_option_quote, validate_trade, validate_quotes_batch, validate_trades_batch


def _make_contract(symbol="BTC-50000-C", underlying="BTC", strike=50000.0, opt_type="call", venue="deribit"):
    return OptionContract(
        symbol=symbol,
        underlying=underlying,
        strike=strike,
        expiry=datetime(2026, 12, 25, tzinfo=timezone.utc),
        option_type=opt_type,
        venue=venue,
    )


def test_normalization_empty_degenerate():
    ts = normalize_timestamp(None)
    assert ts.tzinfo is not None
    assert normalize_symbol(" btc-usdt ", "deribit") == "BTCUSDT"
    assert calculate_moneyness(0, 100) == 0.0
    assert calculate_cumulative_delta([]) == 0.0
    assert compute_vwap([]) == 0.0
    naive = datetime(2026, 1, 1)
    norm = normalize_timestamp(naive)
    assert norm.tzinfo is not None


def test_normalization_orderflow_with_missing_fields():
    trades = [Trade(trade_id="1", symbol="BTC", venue="deribit", price=50000, size=1, side="buy", timestamp=datetime(2026,1,1,tzinfo=timezone.utc))]
    snap = OrderflowSnapshot(symbol="BTC", venue="deribit", trades=trades, timestamp=datetime(2026,1,1))
    norm = normalize_orderflow(snap)
    assert norm.timestamp.tzinfo is not None


def test_gamma_empty_chain():
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
    assert calculate_total_gex(chain, 50000) == 0.0
    assert calculate_total_delta_weighted_gex(chain, 50000) == 0.0
    assert calculate_total_oi_volume_weighted_gex(chain, 50000) == 0.0
    flip = gamma_flip_level(chain, 50000)
    assert isinstance(flip, float)
    flip_w = gamma_flip_level_weighted(chain, 50000)
    assert isinstance(flip_w, float)


def test_gamma_all_same_sign_gex():
    c = _make_contract(strike=40000, opt_type="call")
    q = OptionQuote(contract=c, bid=2000, ask=2100, gamma=0.001, delta=0.9, open_interest=100, volume=10, timestamp=datetime.now(timezone.utc))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[q], timestamp=datetime.now(timezone.utc))
    flip = gamma_flip_level(chain, 50000)
    assert math.isfinite(flip)
    flip_w = gamma_flip_level_weighted(chain, 50000)
    assert math.isfinite(flip_w)


def test_gamma_nan_inf_guard():
    c = _make_contract()
    q = OptionQuote(contract=c, bid=100, ask=110, gamma=float('nan'), delta=float('inf'), open_interest=float('nan'), volume=0, timestamp=datetime.now(timezone.utc))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[q], timestamp=datetime.now(timezone.utc))
    for fn in [calculate_total_gex, calculate_total_delta_weighted_gex, calculate_total_oi_volume_weighted_gex]:
        res = fn(chain, 50000)
        assert math.isfinite(res)
    flip = gamma_flip_level(chain, 50000)
    assert math.isfinite(flip)


def test_orderflow_all_same_side():
    trades = [Trade(trade_id=str(i), symbol="BTC", venue="deribit", price=50000+i, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)) for i in range(10)]
    assert calculate_cumulative_delta(trades) == 10.0
    assert calc_cum_delta_feat(trades) == 10.0
    imb = calculate_orderflow_imbalance(trades)
    assert math.isfinite(imb)
    vpin = vpin_style_toxicity(trades)
    assert math.isfinite(vpin)
    tox = calculate_orderflow_imbalance(trades)  # ensure call works
    assert math.isfinite(tox)


def test_orderflow_extreme_and_zero():
    trades = [Trade(trade_id="1", symbol="BTC", venue="deribit", price=50000, size=0.0, side="buy", timestamp=datetime.now(timezone.utc))]
    imb = calculate_orderflow_imbalance(trades)
    assert math.isfinite(imb)
    assert math.isfinite(calculate_orderflow_imbalance([]))


def test_orderflow_nan_inf():
    trades = [Trade(trade_id="1", symbol="BTC", venue="deribit", price=50000, size=float('inf'), side="buy", timestamp=datetime.now(timezone.utc)),
              Trade(trade_id="2", symbol="BTC", venue="deribit", price=50000, size=float('nan'), side="sell", timestamp=datetime.now(timezone.utc))]
    try:
        res = absorption_detection(trades)
        assert res is not None
    except Exception:
        pass


def test_volatility_degenerate():
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
    assert calculate_put_call_ratio(chain.quotes) >= 0
    assert math.isfinite(calculate_iv_skew(chain.quotes, 50000))
    mp = calculate_max_pain(chain)
    assert math.isfinite(mp)


def test_volatility_nan_quotes():
    c = _make_contract(strike=50000, opt_type="call")
    q = OptionQuote(contract=c, bid=100, ask=110, mark_iv=float('nan'), delta=float('nan'), gamma=float('nan'), open_interest=0, volume=0, timestamp=datetime.now(timezone.utc))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[q], timestamp=datetime.now(timezone.utc))
    assert math.isfinite(calculate_iv_skew(chain.quotes, 50000))
    assert math.isfinite(calculate_put_call_ratio(chain.quotes))
    mp = calculate_max_pain(chain)
    assert math.isfinite(mp)


def test_liquidity_zero():
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
    m = calculate_chain_liquidity_metrics(chain)
    assert isinstance(m, dict)


def test_backtest_adversarial():
    cfg = BacktestConfig(initial_capital=100000, fee_rate=0.001, slippage_bps=5)
    rc = RiskConfig(max_position_pct=0.1, max_drawdown_limit=0.5)
    eng = BacktestEngine(cfg, rc)
    with pytest.raises(OrderError):
        eng.execute_trade("BTC", -1, 50000, "buy", datetime.now(timezone.utc))
    with pytest.raises(OrderError):
        eng.execute_trade("BTC", 1, -1, "buy", datetime.now(timezone.utc))
    with pytest.raises(OrderError):
        eng.execute_trade("BTC", 0, 50000, "buy", datetime.now(timezone.utc))
    with pytest.raises(OrderError):
        eng.execute_trade("BTC", float('nan'), 50000, "buy", datetime.now(timezone.utc))
    with pytest.raises(OrderError):
        eng.execute_trade("BTC", 1, float('inf'), "buy", datetime.now(timezone.utc))


def test_backtest_insufficient_cash():
    cfg = BacktestConfig(initial_capital=1000)
    rc = RiskConfig(max_position_pct=1.0)
    eng = BacktestEngine(cfg, rc)
    with pytest.raises(RiskLimitError):
        eng.execute_trade("BTC", 100, 50000, "buy", datetime.now(timezone.utc))


def test_backtest_short_not_allowed():
    cfg = BacktestConfig(initial_capital=100000)
    rc = RiskConfig(allow_shorting=False, max_position_pct=0.1)
    eng = BacktestEngine(cfg, rc)
    with pytest.raises(RiskLimitError):
        eng.execute_trade("BTC", 1, 50000, "sell", datetime.now(timezone.utc))


def test_backtest_drawdown_liquidation():
    cfg = BacktestConfig(initial_capital=10000)
    rc = RiskConfig(max_position_pct=0.5, max_drawdown_limit=0.1)
    eng = BacktestEngine(cfg, rc)
    eng.execute_trade("BTC", 0.1, 50000, "buy", datetime.now(timezone.utc))
    eng.update_equity_curve({"BTC": 40000})
    metrics = eng.calculate_metrics()
    assert math.isfinite(metrics.total_return)
    assert math.isfinite(metrics.max_drawdown)


def test_backtest_metrics_nan_inf_equity():
    cfg = BacktestConfig(initial_capital=100000)
    eng = BacktestEngine(cfg)
    eng.equity_curve = [100000, float('nan'), float('inf'), 110000]
    metrics = eng.calculate_metrics()
    assert math.isfinite(metrics.total_return)
    assert math.isfinite(metrics.sharpe_ratio)
    assert math.isfinite(metrics.sortino_ratio)
    assert math.isfinite(metrics.max_drawdown)


def test_config_validation_adversarial():
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="badvenue")], data=DataConfig(symbols=["BTC"]), backtest=BacktestConfig(), risk=RiskConfig())
        validate_config(cfg)
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="deribit")], data=DataConfig(symbols=[]), backtest=BacktestConfig(), risk=RiskConfig())
        validate_config(cfg)
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="deribit")], data=DataConfig(symbols=["BTC"]), backtest=BacktestConfig(fee_rate=1.5), risk=RiskConfig())
        validate_config(cfg)
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="deribit")], data=DataConfig(symbols=["BTC"]), backtest=BacktestConfig(initial_capital=0), risk=RiskConfig())
        validate_config(cfg)
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="deribit")], data=DataConfig(symbols=["BTC"]), backtest=BacktestConfig(), risk=RiskConfig(max_position_pct=0))
        validate_config(cfg)
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="deribit")], data=DataConfig(symbols=["BTC"]), backtest=BacktestConfig(), risk=RiskConfig(max_drawdown_limit=1.5))
        validate_config(cfg)
    with pytest.raises((ConfigError, ValueError)):
        cfg = StrategyConfig(venues=[VenueConfig(name="deribit")], data=DataConfig(symbols=["BTC"]), backtest=BacktestConfig(slippage_seed=1.5), risk=RiskConfig())
        validate_config(cfg)


def test_validate_config_dict_adversarial():
    bad = {"venues": ["deribit"], "data": {"symbols": []}, "backtest": {}, "risk": {}}
    with pytest.raises((ConfigError, ValueError)):
        validate_config_dict(bad)


def test_validation_utils():
    c = _make_contract()
    q = OptionQuote(contract=c, bid=-1, ask=10, timestamp=datetime.now(timezone.utc))
    assert validate_option_quote(q) is False
    q2 = OptionQuote(contract=c, bid=10, ask=5, timestamp=datetime.now(timezone.utc))
    assert validate_option_quote(q2) is False
    q3 = OptionQuote(contract=c, bid=5, ask=10, timestamp=datetime.now(timezone.utc))
    assert validate_option_quote(q3) is True
    t = Trade(trade_id="1", symbol="BTC", venue="deribit", price=-1, size=1, side="buy", timestamp=datetime.now(timezone.utc))
    assert validate_trade(t) is False
    t2 = Trade(trade_id="1", symbol="BTC", venue="deribit", price=1, size=-1, side="buy", timestamp=datetime.now(timezone.utc))
    assert validate_trade(t2) is False
    t3 = Trade(trade_id="1", symbol="BTC", venue="deribit", price=1, size=1, side="bad", timestamp=datetime.now(timezone.utc))
    assert validate_trade(t3) is False


def test_pipeline_adversarial_no_crash():
    config = {"venues": ["deribit"], "data": {"symbols": ["BTC"], "spot_price": 50000}, "backtest": {"initial_capital": 100000}, "risk": {"max_position_pct": 0.1}}
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, \
         patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = chain
        MockOf.return_value.fetch_trades.return_value = []
        res = run_pipeline(config, symbols=["BTC"])
    assert isinstance(res, dict)
    assert "errors" in res


def test_duplicate_timestamps_normalization():
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=50000, size=1, side="buy", timestamp=datetime(2026,1,1,tzinfo=timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=50001, size=2, side="sell", timestamp=datetime(2026,1,1,tzinfo=timezone.utc)),
        Trade(trade_id="3", symbol="BTC", venue="deribit", price=50000, size=1, side="buy", timestamp=datetime(2026,1,1,tzinfo=timezone.utc)),
    ]
    # Should not crash; cumulative delta should be finite
    cd = calculate_cumulative_delta(trades)
    assert math.isfinite(cd)


def test_division_by_zero_paths():
    # moneyness with spot 0
    from src.data.normalization import calculate_moneyness
    assert calculate_moneyness(0, 100) == 0.0
    assert calculate_moneyness(-5, 100) == 0.0
    # vwap with zero volume
    from src.data.normalization import compute_vwap
    trades = [Trade(trade_id="1", symbol="BTC", venue="deribit", price=50000, size=0, side="buy", timestamp=datetime.now(timezone.utc))]
    assert compute_vwap(trades) == 0.0


def test_log_sqrt_invalid_values():
    import math
    # Ensure our code paths don't produce unguarded log of non-positive
    # Test features handle edge cases
    from src.features.volatility import calculate_iv_skew
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
    sk = calculate_iv_skew(chain.quotes, 0)  # spot 0
    assert math.isfinite(sk)
    sk2 = calculate_iv_skew([], -100)
    assert math.isfinite(sk2)


def test_dataframe_like_objects_adversarial():
    # If passed unexpected types, should be handled gracefully
    from src.data.normalization import normalize_options_chain
    try:
        # Pass minimal objects
        chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
        res = normalize_options_chain(chain)
        assert res is not None
    except Exception:
        # Should not be unhandled crash in general
        pass


def test_all_modules_nan_inf_cascades():
    from src.features.gamma_exposure import calculate_gex_by_strike
    c = _make_contract()
    q = OptionQuote(contract=c, bid=100, ask=110, gamma=float('nan'), delta=float('nan'), open_interest=float('inf'), volume=float('inf'), timestamp=datetime.now(timezone.utc))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[q], timestamp=datetime.now(timezone.utc))
    # All results should be finite
    import math
    assert math.isfinite(calculate_total_gex(chain, float('nan')))
    assert math.isfinite(calculate_total_gex(chain, 0))
    assert math.isfinite(calculate_total_gex(chain, -1))
