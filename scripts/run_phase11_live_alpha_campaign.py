#!/usr/bin/env python3
"""Run Phase 11 Live Alpha Campaign."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.execution.phase11_campaign import Phase11Campaign


def main() -> int:
    camp = Phase11Campaign(symbols=("BTC", "ETH"), seed=42)
    res = camp.run()
    print(f"Phase11 artifacts: {len(res['artifacts'])}")
    for a in res['artifacts']:
        print(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
