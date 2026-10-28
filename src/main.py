"""CLI entrypoint wiring ingestion -> features -> signals -> backtest."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import yaml

from .backtest.engine import BacktestEngine
from .ingestion.binance import BinanceOptionsIngestion, BinanceOrderflowIngestion
from .ingestion.deribit import DeribitOptionsIngestion, DeribitOrderflowIngestion
from .ingestion.okx import OKXOptionsIngestion, OKXOrderflowIngestion
from .signals.composite import CompositeSignalGenerator


def load_config(config_path: str = "config/settings.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    with path.open() as f:
        return yaml.safe_load(f) or {}


def run_pipeline(config: Dict[str, Any], symbols: list[str] | None = None) -> Dict[str, Any]:
    venues = config.get("venues", ["deribit"])
    symbols = symbols or config.get("data", {}).get("symbols", ["BTC"])
    results: Dict[str, Any] = {"venues": venues, "symbols": symbols, "timestamp": datetime.now(timezone.utc).isoformat()}

    # Ingestion
    for sym in symbols:
        for v in venues:
            v_lower = str(v).lower()
            try:
                if v_lower == "deribit":
                    opt_ing = DeribitOptionsIngestion()
                    of_ing = DeribitOrderflowIngestion()
                    chain = opt_ing.fetch_options_chain(sym)
                    results.setdefault("options_chains", {})[f"{v_lower}:{sym}"] = {"quotes": len(chain.quotes)}
                    # Try perpetual style for orderflow
                    try:
                        trades = of_ing.fetch_trades(f"{sym}-PERPETUAL")
                        results.setdefault("orderflow", {})[f"{v_lower}:{sym}"] = {"trades": len(trades.trades)}
                    except Exception as e:
                        results.setdefault("errors", []).append(f"deribit_trades_{sym}: {e}")
                elif v_lower == "okx":
                    opt_ing = OKXOptionsIngestion()
                    of_ing = OKXOrderflowIngestion()
                    chain = opt_ing.fetch_options_chain(sym)
                    results.setdefault("options_chains", {})[f"{v_lower}:{sym}"] = {"quotes": len(chain.quotes)}
                    try:
                        trades = of_ing.fetch_trades(f"{sym}-USDT-SWAP")
                        results.setdefault("orderflow", {})[f"{v_lower}:{sym}"] = {"trades": len(trades.trades)}
                    except Exception as e:
                        results.setdefault("errors", []).append(f"okx_trades_{sym}: {e}")
                elif v_lower == "binance":
                    opt_ing = BinanceOptionsIngestion()
                    of_ing = BinanceOrderflowIngestion()
                    chain = opt_ing.fetch_options_chain(sym)
                    results.setdefault("options_chains", {})[f"{v_lower}:{sym}"] = {"quotes": len(chain.quotes)}
                    try:
                        # Try common perpetual symbol
                        trades = of_ing.fetch_trades(f"{sym}USDT")
                        results.setdefault("orderflow", {})[f"{v_lower}:{sym}"] = {"trades": len(trades.trades)}
                    except Exception as e:
                        results.setdefault("errors", []).append(f"binance_trades_{sym}: {e}")
                else:
                    results.setdefault("errors", []).append(f"unknown_venue_{v}")
            except Exception as e:
                results.setdefault("errors", []).append(f"{v_lower}_options_{sym}: {e}")

    # Signals + backtest (basic wiring)
    signal_gen = CompositeSignalGenerator()
    engine = BacktestEngine(initial_capital=float(config.get("backtest", {}).get("initial_capital", 100000.0)))
    results["signal_generator"] = signal_gen.__class__.__name__
    results["backtest_engine"] = engine.__class__.__name__
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Crypto options orderflow strategy runner")
    parser.add_argument("--config", default="config/settings.yaml")
    parser.add_argument("--symbols", nargs="*")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    res = run_pipeline(config, args.symbols)
    if args.json:
        print(json.dumps(res, indent=2, default=str))
    else:
        print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
