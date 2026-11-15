# EVAL_45_OPTIONS_ETH_BLOCKED — ETH options net-of-cost BLOCKED (EVAL-45 Leg B)

- **Generated:** 2026-11-15T01:29:06.892991Z
- **Task ID:** `INIT-2026-11-15T01:29:06.892991Z-EVAL-45-OPTIONS-ETH-BLOCKED`
- **Status:** `BLOCKED` — 0 real ETH option snapshots on disk < required 30 dense snapshots (BTC reference: 101); a single cross-section cannot support a net-of-cost walk-forward
- **Trading mode:** paper (live_trading_enabled=False)

## Readiness (measured)

- Real ETH option snapshots on disk: 0 (required min 30; BTC reference 101)
- Dense series available: False
- Disk scan error: None

## Venue reachability (measured, not the blocker)

- OKX ETH-USD option venue reachable: 716 quotes, 13 distinct expiries (sample ts 2026-11-15T01:29:06.095000Z)

## Why BLOCKED (not NO-GO)

A net-of-cost walk-forward requires a dense real snapshot time-series; a single cross-section cannot support the pre-declared IC/quintile/sign-flip/z-score falsification statistics. This is an acquisition-horizon blocker, not a measured NO-GO — the ETH options pillar remains OPEN.

## Attempts
- Counted real ETH option snapshots on disk via scripts/eval45_options_eth_blocked.py (no BTC relabel, no synthesis).
- Probed the public OKX ETH-USD option venue to confirm reachability is not the blocker (single cross-section is not a time-series).
- No substitution attempted: BTC snapshots are never relabelled as ETH; a single cross-section is never reported as a net-of-cost result.

## Remediation (EVAL-46)
- EVAL-46: collect a dense real ETH-USD option snapshot time-series (public read-only polling over the required horizon, >= 30 snapshots) into data/raw/options_candles/.
- Then run the sealed EVAL-42 independent options audit on the ETH series (IC, quintile long-short, sign-flip, continuous z-score; 1000-perm, 1000-bootstrap, CSCV PBO k=4, BH-FDR alpha 0.1, seed 42) and seal EVAL_46.

## Command
```bash
python3 scripts/eval45_options_eth_blocked.py
```

## Code paths
- `scripts/eval45_options_eth_blocked.py`
- `scripts/eval42_options_timeseries_independent_audit.py`
- `src/data/public_export_acquisition.py`
- `tests/test_eval45_options_eth_blocked.py`
