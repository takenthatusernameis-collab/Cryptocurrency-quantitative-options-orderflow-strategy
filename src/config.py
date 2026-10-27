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


@dataclass
class RiskConfig:
    max_position_pct: float = 0.1
    max_drawdown_limit: float = 0.2
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04


@dataclass
class StrategyConfig:
    venues: List[VenueConfig] = field(default_factory=list)
    data: DataConfig = field(default_factory=DataConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)


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
    
    return StrategyConfig(venues=venues, data=data_cfg, backtest=bt_cfg, risk=risk_cfg)
