#!/usr/bin/env python3
from __future__ import annotations

from src.integration.phase37_orderflow_routing_loop import Loop37Config, Phase37OrderflowRoutingLoop


def main() -> None:
    cfg = Loop37Config(symbols=["BTC-USD"], venues=["deribit", "okx", "bybit"], underlyings=["BTC"], expiries=["20261107"], modes="paper", cycles=20, seed=737373, outdir="research_state")
    loop = Phase37OrderflowRoutingLoop(cfg)
    res = loop.run()
    print("PHASE37_OK", res["aggregate"]["n_cycles"], res["aggregate"]["delta_neutral_ok_cycles"])


if __name__ == "__main__":
    main()
