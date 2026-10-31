"""Build and materialize features pipeline."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from ..data.loader import DataLoader
from ..features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance
from ..features.volatility import calculate_put_call_ratio, calculate_iv_skew, calculate_max_pain
from ..features.liquidity import calculate_bid_ask_spread, calculate_liquidity_score


def build_features(
    orderflow_path: str,
    options_path: str,
    spot: float = 65000.0,
    venue: str = "synthetic",
    output_dir: str = "data/processed",
) -> Dict[str, Any]:
    """Build features from raw data and materialize to disk."""
    loader = DataLoader(cache=False)
    of = loader.load_orderflow(orderflow_path, venue=venue, symbol="BTCUSDT")
    oc = loader.load_options_chain(options_path, venue=venue, underlying="BTC")

    features = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "spot": spot,
        "orderflow": {
            "num_trades": len(of.trades),
            "num_liquidations": len(of.liquidations),
            "num_funding_rates": len(of.funding_rates),
            "cumulative_delta": calculate_cumulative_delta(of.trades),
            "orderflow_imbalance": calculate_orderflow_imbalance(of.trades),
        },
        "options": {
            "num_quotes": len(oc.quotes),
            "put_call_ratio": calculate_put_call_ratio(oc.quotes),
            "iv_skew": calculate_iv_skew(oc.quotes, spot),
            "max_pain": calculate_max_pain(oc),
        },
    }

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    manifest_path = Path(output_dir) / f"features_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(manifest_path, "w") as f:
        json.dump(features, f, indent=2)

    # Also write latest
    latest_path = Path(output_dir) / "features_latest.json"
    with open(latest_path, "w") as f:
        json.dump(features, f, indent=2)

    features["manifest_path"] = str(manifest_path)
    return features


if __name__ == "__main__":
    res = build_features(
        "data/raw/orderflow_btcusdt_synthetic.json",
        "data/raw/options_btc_synthetic.json",
    )
    print(json.dumps(res["orderflow"], indent=2))
