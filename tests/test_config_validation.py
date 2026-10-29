"""Tests for config validation edge cases (src/config.py).

Covers cross-field validation, invalid-combo rejection, and safe-default
behavior. Invalid configurations must raise ConfigError with field-level
context.
"""

import pytest

from src.config import BacktestConfig, RiskConfig, StrategyConfig, VenueConfig, validate_config
from src.errors import ConfigError


def _make_cfg(**overrides) -> StrategyConfig:
    venues = [VenueConfig(name="deribit")]
    backtest = BacktestConfig()
    risk = RiskConfig()
    for k, v in overrides.get("backtest", {}).items():
        setattr(backtest, k, v)
    for k, v in overrides.get("risk", {}).items():
        setattr(risk, k, v)
    return StrategyConfig(venues=venues, backtest=backtest, risk=risk)


def test_valid_config_passes():
    cfg = _make_cfg()
    validate_config(cfg)  # must not raise


def test_slippage_exceeds_cap_rejected():
    cfg = _make_cfg(backtest={"slippage_bps": 10.0, "max_slippage_bps": 5.0})
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_slippage_at_cap_allowed():
    cfg = _make_cfg(backtest={"slippage_bps": 5.0, "max_slippage_bps": 5.0})
    validate_config(cfg)  # equal is allowed


def test_no_slippage_cap_allowed():
    cfg = _make_cfg(backtest={"slippage_bps": 100.0, "max_slippage_bps": 0.0})
    validate_config(cfg)  # 0 = no cap


def test_fee_rate_too_high_rejected():
    cfg = _make_cfg(backtest={"fee_rate": 0.2})
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_fee_rate_boundary_allowed():
    cfg = _make_cfg(backtest={"fee_rate": 0.1})
    validate_config(cfg)


def test_stop_loss_not_below_take_profit_rejected():
    cfg = _make_cfg(risk={"stop_loss_pct": 0.05, "take_profit_pct": 0.04})
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_stop_loss_equals_take_profit_rejected():
    cfg = _make_cfg(risk={"stop_loss_pct": 0.03, "take_profit_pct": 0.03})
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_stop_loss_below_take_profit_allowed():
    cfg = _make_cfg(risk={"stop_loss_pct": 0.02, "take_profit_pct": 0.04})
    validate_config(cfg)


def test_options_interval_non_positive_rejected():
    cfg = _make_cfg()
    cfg.data.options_interval = 0
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_options_interval_negative_rejected():
    cfg = _make_cfg()
    cfg.data.options_interval = -5
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_options_interval_positive_allowed():
    cfg = _make_cfg()
    cfg.data.options_interval = 60
    validate_config(cfg)


def test_max_position_qty_below_round_lot_rejected():
    cfg = _make_cfg(backtest={"round_lot_size": 1.0}, risk={"max_position_qty": 0.5})
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_max_position_qty_at_round_lot_allowed():
    cfg = _make_cfg(backtest={"round_lot_size": 1.0}, risk={"max_position_qty": 1.0})
    validate_config(cfg)


def test_no_round_lot_with_qty_cap_allowed():
    cfg = _make_cfg(backtest={"round_lot_size": 0.0}, risk={"max_position_qty": 1.0})
    validate_config(cfg)


def test_validation_error_mentions_fields():
    cfg = _make_cfg(backtest={"slippage_bps": 10.0, "max_slippage_bps": 5.0})
    try:
        validate_config(cfg)
    except ConfigError as e:
        assert "slippage_bps" in str(e) or "max_slippage_bps" in str(e)
        assert e.context is not None and "errors" in e.context
    else:
        raise AssertionError("expected ConfigError")
