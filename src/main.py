"""CLI entrypoint wiring ingestion -> features -> signals -> backtest."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import yaml

from .backtest.engine import BacktestEngine
from .data.schemas import OptionsChain, OrderflowSnapshot
from .ingestion.deribit import DeribitOptionsIngestion, DeribitOrderflowIngestion
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
            if v == "deribit":
                opt_ing = DeribitOptionsIngestion()
                of_ing = DeribitOrderflowIngestion()
                try:
                    chain = opt_ing.fetch_options_chain(sym)
                    results.setdefault("options_chains", {})[f"{v}:{sym}"] = {"quotes": len(chain.quotes)}
                except Exception as e:
                    results.setdefault("errors", []).append(f"deribit_options_{sym}: {e}")
                try:
                    trades = of_ing.fetch_trades(f"{sym}-PERPETUAL" if v == "deribit" else sym)
                    results.setdefault("orderflow", {})[f"{v}:{sym}"] = {"trades": len(trades.trades)}
                except Exception as e:
                    results.setdefault("errors", []).append(f"deribit_trades_{sym}: {e}")

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
