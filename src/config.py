"""Configuration management for crypto options orderflow strategy."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class VenueConfig:
    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    enabled: bool = True


@dataclass
class DataConfig:
    symbols: List[str] = field(default_factory=lambda: ["BTC", "ETH"])
    include_liquidations: bool = True
    include_trades: bool = True
    options_interval: int = 60


@dataclass
class BacktestConfig:
    initial_capital: float = 100000.0
    fee_rate: float = 0.0005
    slippage_bps: float = 1.0
    risk_free_rate: float = 0.0
    partial_fill_rate: float = 0.0  # 0 = fills fully; 0 < r <= 1 = random fill fraction (deterministic seed)
    round_lot_size: float = 0.0  # 0 = no rounding; > 0 = round quantity down to lot
    max_slippage_bps: float = 0.0  # 0 = no cap; > 0 = cap slippage to this many bps
    slippage_seed: int = 42  # seed for deterministic partial fills


@dataclass
class RiskConfig:
    max_position_pct: float = 0.1
    max_drawdown_limit: float = 0.2
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    max_position_qty: float = 0.0  # 0 = no cap; > 0 = hard quantity cap
    allow_shorting: bool = True


@dataclass
class StrategyConfig:
    venues: List[VenueConfig] = field(default_factory=list)
    data: DataConfig = field(default_factory=DataConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)


def validate_config(cfg: "StrategyConfig") -> None:
    """Validate required config fields; raise ValueError with field names if missing/invalid."""
    errors = []
    # Symbols non-empty
    if not cfg.data.symbols:
        errors.append("data.symbols must be non-empty")
    # Backtest fields
    if not (0.0 <= cfg.backtest.fee_rate <= 1.0):
        errors.append("backtest.fee_rate must be in [0, 1]")
    if cfg.backtest.initial_capital <= 0:
        errors.append("backtest.initial_capital must be > 0")
    if cfg.backtest.slippage_bps < 0:
        errors.append("backtest.slippage_bps must be >= 0")
    if cfg.backtest.max_slippage_bps < 0:
        errors.append("backtest.max_slippage_bps must be >= 0")
    if not (0.0 <= cfg.backtest.partial_fill_rate <= 1.0):
        errors.append("backtest.partial_fill_rate must be in [0, 1]")
    if cfg.backtest.round_lot_size < 0:
        errors.append("backtest.round_lot_size must be >= 0")
    # Risk limits in (0, 1]
    for field_name in ("max_position_pct", "max_drawdown_limit", "stop_loss_pct", "take_profit_pct"):
        val = getattr(cfg.risk, field_name)
        if not (0.0 < val <= 1.0):
            errors.append(f"risk.{field_name} must be in (0, 1], got {val}")
    if cfg.risk.max_position_qty < 0:
        errors.append("risk.max_position_qty must be >= 0")
    if not isinstance(cfg.risk.allow_shorting, bool):
        errors.append("risk.allow_shorting must be bool")
    if errors:
        raise ValueError("Invalid config: " + "; ".join(errors))


def load_config(config_path: Optional[Path] = None) -> StrategyConfig:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "settings.yaml"

    config_path = Path(config_path)
    if not config_path.exists():
        return StrategyConfig()

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f) or {}

    venues = []
    for v in raw.get("venues", []):
        if isinstance(v, str):
            venues.append(VenueConfig(name=v))
        elif isinstance(v, dict):
            venues.append(VenueConfig(**v))

    data_raw = raw.get("data", {})
    data_cfg = DataConfig(
        symbols=data_raw.get("symbols", ["BTC", "ETH"]),
        include_liquidations=data_raw.get("orderflow", {}).get("include_liquidations", True),
        include_trades=data_raw.get("orderflow", {}).get("include_trades", True),
        options_interval=data_raw.get("options", {}).get("interval", 60),
    )

    bt_raw = raw.get("backtest", {})
    bt_cfg = BacktestConfig(**bt_raw)

    risk_raw = raw.get("risk", {})
    risk_cfg = RiskConfig(**risk_raw)

    cfg = StrategyConfig(venues=venues, data=data_cfg, backtest=bt_cfg, risk=risk_cfg)
    validate_config(cfg)
    return cfg
