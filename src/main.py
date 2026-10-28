"""CLI entrypoint wiring ingestion -> features -> signals -> backtest."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import yaml

from .backtest.engine import BacktestEngine
from .data.normalization import normalize_options_chain, normalize_orderflow
from .features.gamma_exposure import (
    calculate_total_gex,
    calculate_total_delta_weighted_gex,
    calculate_total_oi_volume_weighted_gex,
    gamma_flip_level,
    gamma_flip_level_weighted,
)
from .features.liquidity import calculate_chain_liquidity_metrics


def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    with path.open() as f:
        return yaml.safe_load(f) or {}


def validate_config_dict(config: Dict[str, Any]) -> None:
    """Validate required config fields; raise ValueError with field names if missing/invalid."""
    from .config import validate_config, StrategyConfig
    # Build StrategyConfig from dict
    venues_raw = config.get("venues", [])
    venues = []
    for v in venues_raw:
        if isinstance(v, str):
            from .config import VenueConfig
            venues.append(VenueConfig(name=v))
        elif isinstance(v, dict):
            from .config import VenueConfig
            venues.append(VenueConfig(**v))
    data_raw = config.get("data", {})
    from .config import DataConfig, BacktestConfig, RiskConfig
    data_cfg = DataConfig(
        symbols=data_raw.get("symbols", ["BTC", "ETH"]),
        include_liquidations=data_raw.get("orderflow", {}).get("include_liquidations", True),
        include_trades=data_raw.get("orderflow", {}).get("include_trades", True),
        options_interval=data_raw.get("options", {}).get("interval", 60),
    )
    bt_raw = config.get("backtest", {})
    bt_cfg = BacktestConfig(**bt_raw)
    risk_raw = config.get("risk", {})
    risk_cfg = RiskConfig(**risk_raw)
    cfg = StrategyConfig(venues=venues, data=data_cfg, backtest=bt_cfg, risk=risk_cfg)
    validate_config(cfg)


def run_pipeline(config: Dict[str, Any], symbols: list[str] | None = None) -> Dict[str, Any]:
    try:
        validate_config_dict(config)
    except ValueError as e:
        return {
            "venues": config.get("venues", []),
            "symbols": symbols or config.get("data", {}).get("symbols", ["BTC", "ETH"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "errors": [f"config_validation: {e}"],
        }
    venues = config.get("venues", ["deribit", "okx", "binance"])
    symbols = symbols or config.get("data", {}).get("symbols", ["BTC", "ETH"])
    spot_price_default = float(config.get("data", {}).get("spot_price", 50000.0))
    if not math.isfinite(spot_price_default) or spot_price_default <= 0:
        spot_price_default = 50000.0
    results: Dict[str, Any] = {
        "venues": venues,
        "symbols": symbols,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errors": [],
    }

    ingested_chains = {}
    ingested_orderflows = {}

    for sym in symbols:
        for v in venues:
            v_lower = str(v).lower()
            try:
                if v_lower == "deribit":
                    opt_ing = DeribitOptionsIngestion()
                    of_ing = DeribitOrderflowIngestion()
                    chain = opt_ing.fetch_options_chain(sym)
                    chain = normalize_options_chain(chain)
                    ingested_chains[f"{v_lower}:{sym}"] = chain
                    results.setdefault("options_chains", {})[f"{v_lower}:{sym}"] = {"quotes": len(chain.quotes)}
                    try:
                        trades = of_ing.fetch_trades(f"{sym}-PERPETUAL")
                        of_snapshot = normalize_orderflow(trades)
                        ingested_orderflows[f"{v_lower}:{sym}"] = of_snapshot
                        results.setdefault("orderflow", {})[f"{v_lower}:{sym}"] = {"trades": len(of_snapshot.trades)}
                    except Exception as e:
                        results.setdefault("errors", []).append(f"deribit_trades_{sym}: {e}")
                elif v_lower == "okx":
                    opt_ing = OKXOptionsIngestion()
                    of_ing = OKXOrderflowIngestion()
                    chain = opt_ing.fetch_options_chain(sym)
                    chain = normalize_options_chain(chain)
                    ingested_chains[f"{v_lower}:{sym}"] = chain
                    results.setdefault("options_chains", {})[f"{v_lower}:{sym}"] = {"quotes": len(chain.quotes)}
                    try:
                        trades = of_ing.fetch_trades(f"{sym}-USDT-SWAP")
                        of_snapshot = normalize_orderflow(trades)
                        ingested_orderflows[f"{v_lower}:{sym}"] = of_snapshot
                        results.setdefault("orderflow", {})[f"{v_lower}:{sym}"] = {"trades": len(of_snapshot.trades)}
                    except Exception as e:
                        results.setdefault("errors", []).append(f"okx_trades_{sym}: {e}")
                elif v_lower == "binance":
                    opt_ing = BinanceOptionsIngestion()
                    of_ing = BinanceOrderflowIngestion()
                    chain = opt_ing.fetch_options_chain(sym)
                    chain = normalize_options_chain(chain)
                    ingested_chains[f"{v_lower}:{sym}"] = chain
                    results.setdefault("options_chains", {})[f"{v_lower}:{sym}"] = {"quotes": len(chain.quotes)}
                    try:
                        trades = of_ing.fetch_trades(f"{sym}USDT")
                        of_snapshot = normalize_orderflow(trades)
                        ingested_orderflows[f"{v_lower}:{sym}"] = of_snapshot
                        results.setdefault("orderflow", {})[f"{v_lower}:{sym}"] = {"trades": len(of_snapshot.trades)}
                    except Exception as e:
                        results.setdefault("errors", []).append(f"binance_trades_{sym}: {e}")
                else:
                    results.setdefault("errors", []).append(f"unknown_venue_{v}")
            except Exception as e:
                results.setdefault("errors", []).append(f"{v_lower}_options_{sym}: {e}")

    signal_gen = CompositeSignalGenerator()
    signals = {}
    for key, chain in ingested_chains.items():
        try:
            v, sym = key.split(":", 1)
            spot_price = spot_price_default
            total_gex = calculate_total_gex(chain, spot_price)
            cum_delta = 0.0
            of_imbalance = 0.0
            if key in ingested_orderflows:
                trades = ingested_orderflows[key].trades
                cum_delta = calculate_cumulative_delta(trades)
                of_imbalance = calculate_orderflow_imbalance(trades)
            pcr = calculate_put_call_ratio(chain.quotes)
            iv_skew = calculate_iv_skew(chain.quotes, spot_price)
            max_pain = calculate_max_pain(chain)
            signal = signal_gen.generate_signal(
                symbol=sym,
                spot_price=spot_price,
                total_gex=total_gex,
                cum_delta=cum_delta,
                of_imbalance=of_imbalance,
                iv_skew=iv_skew,
                put_call_ratio=pcr,
            )
            signals[key] = {
                "symbol": signal.symbol,
                "direction": signal.direction,
                "strength": signal.strength,
                "confidence": signal.confidence,
                "components": signal.components,
                "regime": getattr(signal, "regime", "unknown"),
                "spot_price": spot_price,
                "total_gex": total_gex,
                "cumulative_delta": cum_delta,
                "orderflow_imbalance": of_imbalance,
                "iv_skew": iv_skew,
                "put_call_ratio": pcr,
                "max_pain": max_pain,
                "gamma_flip": gamma_flip_level(chain, spot_price),
            }
        except Exception as e:
            results.setdefault("errors", []).append(f"signal_generation_{key}: {e}")
    results["signals"] = signals

    try:
        from .config import BacktestConfig, RiskConfig

        bt_config = config.get("backtest", {})
        risk_config = config.get("risk", {}) or {}
        engine = BacktestEngine(
            config=BacktestConfig(
                initial_capital=float(bt_config.get("initial_capital", 100000.0)),
                fee_rate=float(bt_config.get("fee_rate", 0.0005)),
                slippage_bps=float(bt_config.get("slippage_bps", 1.0)),
                risk_free_rate=float(bt_config.get("risk_free_rate", 0.0)),
            ),
            risk_config=RiskConfig(**risk_config) if risk_config else RiskConfig(),
        )
        if signals:
            for key, sig in signals.items():
                spot = sig.get("spot_price", 50000.0)
                if sig["direction"] == "long" and sig["confidence"] > 0.1:
                    qty = engine.calculate_position_size(spot) * sig["confidence"]
                    if qty > 0 and engine.cash > spot * qty * 1.05:
                        try:
                            engine.execute_trade(key, qty, spot, "buy", datetime.now(timezone.utc))
                        except Exception as e:
                            results.setdefault("errors", []).append(f"execute_trade_long_{key}: {e}")
                elif sig["direction"] == "short" and sig["confidence"] > 0.1:
                    qty = engine.calculate_position_size(spot) * sig["confidence"]
                    if qty > 0:
                        try:
                            engine.execute_trade(key, qty, spot, "sell", datetime.now(timezone.utc))
                        except Exception as e:
                            results.setdefault("errors", []).append(f"execute_trade_short_{key}: {e}")
            prices = {k: s["spot_price"] for k, s in signals.items()}
            engine.update_equity_curve(prices)
        bt_results = engine.calculate_metrics()
        results["backtest"] = {
            "total_return": bt_results.total_return,
            "sharpe_ratio": bt_results.sharpe_ratio,
            "sortino_ratio": bt_results.sortino_ratio,
            "max_drawdown": bt_results.max_drawdown,
            "win_rate": bt_results.win_rate,
            "profit_factor": bt_results.profit_factor,
            "calmar_ratio": bt_results.calmar_ratio,
            "total_trades": bt_results.total_trades,
            "winning_trades": bt_results.winning_trades,
            "losing_trades": bt_results.losing_trades,
            "equity_final": bt_results.equity_curve[-1] if bt_results.equity_curve else engine.initial_capital,
        }
        results["backtest_engine"] = engine.__class__.__name__
    except Exception as e:
        results.setdefault("errors", []).append(f"backtest: {e}")
        from .config import BacktestConfig, RiskConfig

        bt_config = config.get("backtest", {})
        risk_config = config.get("risk", {}) or {}
        engine = BacktestEngine(
            config=BacktestConfig(initial_capital=float(bt_config.get("initial_capital", 100000.0))),
            risk_config=RiskConfig(**risk_config) if risk_config else RiskConfig(),
        )
        results["backtest_engine"] = engine.__class__.__name__

    results["signal_generator"] = signal_gen.__class__.__name__
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Crypto options orderflow strategy runner")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--symbols", nargs="*")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    res = run_pipeline(config, args.symbols)
    # Ensure JSON output is valid with allow_nan=False (no inf/nan)
    try:
        json_str = json.dumps(res, indent=2, default=str, allow_nan=False)
    except ValueError:
        # Fallback: sanitize non-finite values
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize(v) for v in obj]
            elif isinstance(obj, float) and not math.isfinite(obj):
                return None
            return obj
        res = sanitize(res)
        json_str = json.dumps(res, indent=2, default=str, allow_nan=False)
    print(json_str)


if __name__ == "__main__":
    main()
