# HANDOFF_NEXT_AGENT — POINTER (RETIRED)

**Refreshed:** 2026-11-12T15:19:24Z (UTC)
**Status:** RETIRED. This file is a pointer, not a task source.

**Single durable handoff (READ FIRST):** `research_state/durable_handoff.md`

- **Active task:** `INIT-2026-11-12T15:19:24Z-STRATEGY-EVAL-06-NET-OF-COST-FALSIFICATION`
- **Root cause fixes landed this session:** deterministic `_stable_seed()` (SHA-256) and time-varying `_time_varying_signal_series()` in `src/campaign/integrated.py`. The all-zero-signal / 0.0 OOS defect is fixed; a real run now produces 10 windows, nonzero portfolio OOS return/Sharpe, and 72/59/185 trades for BTC/ETH/SOL.
- **Do not** re-run environment verification, re-write EVAL-02/03, or advance the archived Phase 272–291 clone loop.
- **Guards:** NO live trading, no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`.