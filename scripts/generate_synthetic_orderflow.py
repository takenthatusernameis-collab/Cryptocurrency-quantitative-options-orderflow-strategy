#!/usr/bin/env python3
"""Generate realistic synthetic orderflow fixtures."""

import json
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate_trades(symbol="BTCUSDT", venue="synthetic", n=1000, seed=42):
    rng = random.Random(seed)
    base = 65000.0
    trades = []
    now = datetime.now(timezone.utc)
    for i in range(n):
        ts = now - timedelta(seconds=rng.randint(0, 3600))
        # random walk
        base = base * (1.0 + rng.gauss(0, 0.0002))
        price = round(base * (1.0 + rng.uniform(-0.001, 0.001)), 2)
        size = round(rng.lognormvariate(-2, 0.8), 6)
        side = rng.choice(["buy", "sell"])
        trades.append(
            {
                "trade_id": f"t{i:06d}",
                "symbol": symbol,
                "venue": venue,
                "price": price,
                "size": size,
                "side": side,
                "timestamp": ts.isoformat().replace("+00:00", "Z"),
            }
        )
    return trades


def generate_liquidations(symbol="BTCUSDT", venue="synthetic", n=20, seed=123):
    rng = random.Random(seed)
    base = 65000.0
    liqs = []
    now = datetime.now(timezone.utc)
    for i in range(n):
        ts = now - timedelta(seconds=rng.randint(0, 7200))
        base = base * (1.0 + rng.gauss(0, 0.0003))
        price = round(base, 2)
        size = round(rng.lognormvariate(-1.5, 0.7), 6)
        side = rng.choice(["long", "short"])
        liqs.append(
            {
                "liquidation_id": f"l{i:06d}",
                "symbol": symbol,
                "venue": venue,
                "price": price,
                "size": size,
                "side": side,
                "timestamp": ts.isoformat().replace("+00:00", "Z"),
            }
        )
    return liqs


def generate_funding(symbol="BTCUSDT", venue="synthetic", n=8, seed=456):
    rng = random.Random(seed)
    frs = []
    now = datetime.now(timezone.utc)
    for i in range(n):
        t = now - timedelta(hours=rng.randint(0, 24))
        rate = round(rng.gauss(0.0001, 0.00005), 8)
        frs.append(
            {
                "symbol": symbol,
                "venue": venue,
                "funding_rate": rate,
                "funding_time": t.isoformat().replace("+00:00", "Z"),
                "timestamp": t.isoformat().replace("+00:00", "Z"),
            }
        )
    return frs


def generate_options_chain(symbol="BTC", venue="synthetic", spot=65000.0, seed=789):
    rng = random.Random(seed)
    quotes = []
    now = datetime.now(timezone.utc)
    # generate a few expiries and strikes
    for exp_offset_days in [1, 7, 30]:
        exp = now + timedelta(days=exp_offset_days)
        for moneyness in [0.9, 0.95, 1.0, 1.05, 1.1]:
            strike = round(spot * moneyness, 0)
            for opt_type in ["call", "put"]:
                bid = max(0.01, rng.gauss(500 if opt_type == "call" else 400, 50))
                ask = bid * (1.0 + rng.uniform(0.001, 0.01))
                quotes.append(
                    {
                        "symbol": f"{symbol}-{int(exp.timestamp())}-{strike}-{opt_type[0].upper()}",
                        "underlying": symbol,
                        "strike": strike,
                        "expiry": exp.isoformat().replace("+00:00", "Z"),
                        "option_type": opt_type,
                        "venue": venue,
                        "contract_size": 1.0,
                        "bid": round(bid, 4),
                        "ask": round(ask, 4),
                        "last": round((bid + ask) / 2.0 * rng.uniform(0.99, 1.01), 4),
                        "mark": round((bid + ask) / 2.0, 4),
                        "bid_iv": round(rng.uniform(0.4, 0.8), 4),
                        "ask_iv": round(rng.uniform(0.4, 0.8), 4),
                        "mark_iv": round(rng.uniform(0.4, 0.8), 4),
                        "delta": round(rng.uniform(0.1, 0.9) if opt_type == "call" else rng.uniform(-0.9, -0.1), 6),
                        "gamma": round(rng.uniform(0.0001, 0.001), 8),
                        "theta": round(rng.uniform(-50, -10), 4),
                        "vega": round(rng.uniform(10, 100), 4),
                        "open_interest": int(rng.uniform(100, 10000)),
                        "volume": int(rng.uniform(10, 1000)),
                        "timestamp": now.isoformat().replace("+00:00", "Z"),
                    }
                )
    return {"quotes": quotes, "underlying": symbol, "venue": venue, "timestamp": now.isoformat().replace("+00:00", "Z")}


def main():
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    # orderflow
    of = {
        "trades": generate_trades(),
        "liquidations": generate_liquidations(),
        "funding_rates": generate_funding(),
        "symbol": "BTCUSDT",
        "venue": "synthetic",
    }
    with open(raw_dir / "orderflow_btcusdt_synthetic.json", "w") as f:
        json.dump(of, f, indent=2)
    # options
    oc = generate_options_chain()
    with open(raw_dir / "options_btc_synthetic.json", "w") as f:
        json.dump(oc, f, indent=2)
    print("Generated synthetic fixtures in data/raw/")


if __name__ == "__main__":
    main()
