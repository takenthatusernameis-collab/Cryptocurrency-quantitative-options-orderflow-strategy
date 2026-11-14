# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T17:39:12Z UTC — TASK ID `INIT-2026-11-14T17:39:12Z-EVAL-41-DECISIVE-FALSIFICATION`** (authoritative; supersedes all prior task IDs/messages, including the now-completed `INIT-2026-11-14T17:33:33Z-EVAL-40-EXECUTE-SEAL`). Inferred from the repo charter: *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement*. **EVAL-40 is DONE and sealed: `EVAL_40_MEASUREMENT_20261114T173912Z` — NO-GO 8/11, REPLICATION.** The campaign remains **TERMINATED (EVAL-36 `TERMINATE_NO_GO`)**, but two pillars' open scientific questions are not yet closed on real data: (A) the **options leg is structurally degenerate** only because every net-of-cost run so far used a *single* options cross-section (EVAL-29/40) or only 3 sparse snapshots (EVAL-27/30/33); (B) the **orderflow pillar's sign flips across windows** (EVAL-33 held-out Sharpe +4.81 vs EVAL-39 orderflow IC +0.0419 vs EVAL-40 orderflow Sharpe -5.35). **This session MUST execute heavy work and seal at least one EVAL-41 artifact. Handoff-only, discovery-only, re-read, or re-acquisition-without-evaluation sessions are NOT progress.**

## MANDATORY HEAVY-WORK CAMPAIGN — EVAL-41 (cannot be avoided)
Two tracks. **Seal at least one track per session** (or seal `EVAL_41_BLOCKED_<UTC>` with exact command + stderr). Both are paper-only, real-data only, no synthetic fallback.

### Track A — Orderflow cross-window robustness (IMMEDIATE, no waiting; do this first)
Tests whether the orderflow pillar has any *persistent* net-of-cost edge across disjoint real windows, or whether the EVAL-33 +4.81 was a lucky window.

1. **Acquire 3 NEW disjoint real tapes** (historical pagination, no waiting). OKX `after` returns trades **older than** the cursor, so start at the oldest id of the EVAL-40 tape (`485439506`) and walk **downward**, reading each new tape's oldest id before the next call. Each call must use a **unique `--orderflow-symbol`** (never the default, which would overwrite the base tape) and a **unique `--timestamp`**:
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   # window 41a: older than EVAL-40's oldest trade id 485439506
   python3 -m src.data.public_export_acquisition --underlying BTC --skip-options \
     --orderflow-instrument BTC-USD-SWAP --orderflow-symbol 41a \
     --after-cursor 485439506 --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     --data-dir data/raw --out research_state
   # oldest id of the tape just written:
   python3 -c "import json;print(min(int(t['trade_id']) for t in json.load(open('data/raw/orderflow_okx_41a.json'))['trades']))"
   # use that value as the next --after-cursor for 41b, then repeat for 41c
   ```
   If the venue returns no older data (empty tape), record that window as exhausted and continue. Do not reuse a cursor that would overlap an already-sealed window.
2. **Evaluate each tape with the pinned path** (discovery is recency-based and would mix tapes):
   ```bash
   python3 -m src.analytics.real_net_of_cost_evaluation \
     --data-dir data/raw --out research_state --symbol BTC --bar-duration-seconds 15 \
     --orderflow-path data/raw/orderflow_okx_41a.json
   # repeat for orderflow_okx_41b.json and orderflow_okx_41c.json
   ```
   Record each `REAL_NET_OF_COST_EVAL_23_<stamp>` artifact path + sha256.
3. **Seal `ORDERFLOW_ROBUSTNESS_41_<UTC>.{json,md}`**: per-tape verdict, orderflow-only net-of-cost Sharpe, trades, cost, max-DD, kill-switch status, orderflow IC, plus a pre-declared persistence bar: **GO only if the orderflow-only net-of-cost Sharpe is > 0 on a majority (≥2/3) of the new tapes AND no tape breaches the kill-switch.** Otherwise REPLICATION/NO-GO. Do not cherry-pick; report every tape.

### Track B — Dense real options time-series decisive test (TIME-BASED; use `cron_create`/`schedule_wakeup` to poll, do not block the session)
The single open question that could overturn termination for the options pillar: does a *genuinely time-varying* options signal carry net-of-cost alpha? Prior tests used 1 snapshot (degenerate) or 3 sparse snapshots (0 net-of-cost trades).

1. **Acquire a dense real snapshot series**: ≥12 real options snapshots at ≤10-minute spacing over ≥2 hours (OKX public tickers are current-only, so poll). Use a unique `--timestamp` per call so filenames never collide:
   ```bash
   python3 -m src.data.public_export_acquisition \
     --underlying BTC --skip-orderflow --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     --data-dir data/raw --out research_state
   ```
   Seed the series with the two existing real snapshots (`data/raw/options_okx_BTC_20261114T153357Z.json`, `data/raw/options_okx_BTC_20261114T171725Z.json`) plus the new polls. Each poll seals its own `PUBLIC_EXPORT_ACQUISITION_<stamp>`; list every snapshot path + sha256 in the final `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>` artifact (no separate manifest needed).
2. **Run the time-varying net-of-cost falsification** by reusing existing primitives — do **not** invent a new orchestrator (`phaseNN_*` prohibited). Template: `scripts/eval33_options_leg_falsification.py` (already wires `src.analytics.options_time_varying_signal.load_snapshot_signals` → `align_options_signal_to_bars` → `src.analytics.integrated_options_orderflow_evaluation._run_walkforward`). Build a thin `scripts/eval41_options_timeseries_net_of_cost.py` that (i) loads **all** real snapshots via `discover_all_real_options_exports`/`load_snapshot_signals`, (ii) aligns the signal to bars built from the EVAL-40 tape (`data/raw/orderflow_okx_BTC-USD-SWAP-40.json`), (iii) sweeps a **pre-declared** options-only grid including **lower thresholds** than EVAL-33 (add `{0.01, 0.02, 0.05}` alongside `{0.1,0.2,0.5}`) so a real signal is not silently zeroed, and (iv) reports IC, permutation vs orderflow-only/flat, block-bootstrap CI, PBO, BH-FDR.
3. **Seal `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>.{json,md}`** with the full grid, per-snapshot signal values (must show ≥2 distinct time-varying levels), IC, permutation, CI, and verdict. Pre-declared bar: **GO only if some options-only variant achieves (a) OOS Sharpe > max(orderflow-only, flat), (b) permutation p < 0.05 vs that control, (c) 95% bootstrap CI excludes 0, and (d) the options signal has ≥2 distinct time-varying levels with |IC| > 1e-9.** Otherwise REPLICATION/NO-GO and the options pillar is definitively closed as untestable with available real data.

### Per-session contract
Seal exactly one of: `ORDERFLOW_ROBUSTNESS_41_<UTC>`, `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>`, or `EVAL_41_BLOCKED_<UTC>`. Append the measured verdict to this handoff. `REPLICATION`/NO-GO keeps the campaign terminated; a GO requires the verifying sealed artifact on new real data and a new pre-registered replication campaign.

**BLOCKED protocol:** if a track cannot run (missing input, tool failure, environment, no network), seal `EVAL_41_BLOCKED_<UTC>.{json,md}` with exact command, exit code, stderr, environment facts, and what was attempted. That is the only acceptable non-advancing outcome.

## BOTTLENECKS REMOVED / SESSION READINESS (verified 2026-11-14T17:39:12Z — **IMMEDIATE ACTION POSSIBLE**)
- **EVAL-40 measured artifact is no longer missing.** Sealed this session: `research_state/EVAL_40_MEASUREMENT_20261114T173912Z.{json,md}` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z` (sha256 json `dd6c133ce2a8794a70aaf398125aa62fff1e6852b605c10b5c3d2eef97b9cd9e`).
- `.env` **absent** (paper-only; must stay absent). No stale `*.lock`/`*.pid` in `research_state/`.
- Runtime deps bootstrapped in `.venv-deps/` (git-ignored). **Always** `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` before python/pytest.
- **Loader gotcha:** `load_real_orderflow` / `load_real_options_chain` pick the alphabetically-last / most-recent real export. For any specific tape use `--orderflow-path`; for a specific options snapshot use the explicit file, never bare discovery.
- **Existing real inputs (do not delete):** `data/raw/orderflow_okx_BTC-USD-SWAP-40.json` (84,800 trades, `485439506..485524305`), `data/raw/orderflow_okx_BTC-USD-SWAP.json` (base tape), `data/raw/options_okx_BTC_20261114T153357Z.json`, `data/raw/options_okx_BTC_20261114T171725Z.json`. Synthetic fixtures (`*_synthetic.json`) must never be used for real evaluation.
- **Network probe (2026-11-14T17:39:12Z):** OKX public read-only endpoints reachable — `public/instruments?instType=OPTION&uly=BTC-USD` HTTP 200 (1,636 contracts); `market/history-trades?instId=BTC-USD-SWAP` HTTP 200 (latest tradeId ~`485644988`). Track A (older-than-`485439506` tapes) and Track B (options polling) are both viable now.
- `scripts/verify_env.sh` bootstraps/checks env. Reusable modules: `src/data/public_export_acquisition.py`, `src/data/options_timeseries.py`, `src/analytics/options_time_varying_signal.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/analytics/integrated_options_orderflow_evaluation.py`.

## CURRENT MEASURED STATE (ground truth)
- **EVAL-02..40 sealed** (immutable). **EVAL-36:** `FINAL_TERMINATION_MEMO_36_20261114T145419Z` — `TERMINATE_NO_GO`.
- **EVAL-37:** `FINAL_TERMINATION_AUDIT_37_20261114T152849Z` — **PASS 9/9**.
- **EVAL-38:** `EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z` — REPLICATION (Sharpe -7.9539, 1221 trades, $179.28 cost, max-DD 0.8679, kill-switch breach).
- **EVAL-39:** `DURABILITY_LEDGER_39_20261114T163011Z` (REPLICATION) + `REAL_NET_OF_COST_EVAL_23_20261114T162521Z` (NO-GO 8/11; `options_leg_degenerate=true`; `combined_alpha.ic_mean=-0.000258`, `options_alpha` 0.0, `orderflow_alpha.ic_mean=0.041876`; permutation p=0.000999 combined worse than best single pillar).
- **EVAL-40 (NEW, this session):** `EVAL_40_MEASUREMENT_20261114T173912Z` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z`. **NO-GO 8/11, REPLICATION.** Disjoint window `02:25:00.798Z→09:05:22.330Z`, 84,800 trades / 1,602 bars. Failed `options_signal_exists, combined_net_of_cost_superior, options_signal_tradable`; `options_leg_degenerate=true` (signal stdev 0.0, abs IC 3.97e-18). combined_alpha `ic_mean=-0.029023` (t=-1.807); orderflow_alpha `ic_mean=-0.010087`; permutation observed diff `-0.093161`, p=0.000999. WF: combined Sharpe 1.858414 (232 trades, $415.64); options-only 4.246051 (688 trades); orderflow-only **-5.349272** (614 trades, $646.34); flat 0.0.
- **Key facts (do not re-litigate):** options leg is static-broadcast in the single-snapshot path (`src/analytics/integrated_options_orderflow_evaluation.py::_causal_options_signal_series`); synthetic-preferring loaders in `src/campaign/integrated.py` and `src/analytics/integrated_options_orderflow_evaluation.py::main` must not be used for real evaluation; use `src.analytics.real_net_of_cost_evaluation` / `load_real_*` with the explicit path. Options parity residuals are large on the raw inverse-quanto exports (EVAL-27: ~1017 parity violations) — record, do not "fix", the raw data.

## HARD CONSTRAINTS / INVARIANTS
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Sealed artifacts EVAL-02..40 are immutable; append new timestamped artifacts only. Do not modify sealed artifacts to make checks pass.
- Network: public read-only market data only, polite rate limiting, only if required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`; no `phaseNN_*` orchestrator wrappers.
- Prohibited: discovery runs, re-litigating sealed EVALs, broad `research_state/` enumeration, full test-suite runs, workflow edits, handoff-only sessions.

## HANDOFF DISCIPLINE
- This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands only; no timestamped handoff copies. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with no task IDs.
- Record measured numbers, not intentions. No GO without a verifying sealed artifact.
- Final responses must not ask follow-up questions.