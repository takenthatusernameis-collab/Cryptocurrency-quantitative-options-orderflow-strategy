#!/usr/bin/env python3
"""Run Phase 10 Alpha Campaign."""
from __future__ import annotations

import sys
from pathlib import Path

# ensure cwd
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.alpha.phase10_campaign import Phase10Campaign


def main() -> int:
    camp = Phase10Campaign(symbols=("BTC", "ETH"), seed=42)
    res = camp.run()
    print(f"Phase10 artifacts: {len(res['artifacts'])}")
    for a in res['artifacts']:
        print(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
