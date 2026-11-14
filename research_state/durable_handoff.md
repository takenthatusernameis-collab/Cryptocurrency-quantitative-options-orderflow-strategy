# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T18:21:06Z UTC — TASK ID `INIT-2026-11-14T18:21:06Z-EVAL-41-EXECUTE-AND-SEAL`** (authoritative; supersedes all prior task IDs/messages, including completed `INIT-2026-11-14T17:39:12Z-EVAL-41-DECISIVE-FALSIFICATION` and `INIT-2026-11-14T17:33:33Z-EVAL-40-EXECUTE-SEAL`). Inferred from repo charter: *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement*. **EVAL-40 is DONE/sealed** (`EVAL_40_MEASUREMENT_20261114T173912Z` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z`, NO-GO 8/11, REPLICATION). Campaign remains **TERMINATED (EVAL-36 `TERMINATE_NO_GO`)** but two decisive open questions remain: (A) options leg appears degenerate because all net-of-cost runs used 1 options cross-section (EVAL-29/40) or 3 sparse snapshots (EVAL-27/30/33); (B) orderflow sign flips across windows (EVAL-33 held-out Sharpe +4.81 vs EVAL-39 IC +0.0419 vs EVAL-40 orderflow Sharpe -5.35). **Next session MUST do heavy measured work and seal at least one EVAL-41 artifact. Handoff-only, discovery-only, re-read, re-acquisition-without-evaluation, or full-suite runs are NOT progress.**

## MANDATORY HEAVY-WORK CAMPAIGN — EVAL-41 (cannot be avoided)
**Do Track A first (immediate, no waiting).** Seal at least one per session: `ORDERFLOW_ROBUSTNESS_41_<UTC>`, `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>`, or `EVAL_41_BLOCKED_<UTC>` (exact command/exit/stderr/attempted). Paper-only, real-data only, no synthetic fallback. No `phaseNN_*` wrappers.

### Track A — Orderflow cross-window robustness (IMMEDIATE, highest priority)
Test whether orderflow has persistent net-of-cost edge or EVAL-33 +4.81 was window-lucky.

1. **Acquire 3 NEW disjoint real tapes** (historical pagination, no waiting). OKX `after` returns trades **older than** cursor; start at EVAL-40 oldest `485439506` and walk downward, reading each new tape's oldest id before next call. Each call: unique `--orderflow-symbol` (never default/base) + unique `--timestamp`:
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.data.public_export_acquisition --underlying BTC --skip-options \
     --orderflow-instrument BTC-USD-SWAP --orderflow-symbol 41a \
     --after-cursor 485439506 --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     --data-dir data/raw --out research_state
   python3 -c "import json;print(min(int(t['trade_id']) for t in json.load(open('data/raw/orderflow_okx_41a.json'))['trades']))"
   # use that min as next --after-cursor for 41b, then 41c
   ```
   Empty/overlap/exhaustion: record explicitly per window (no reuse of overlapping cursors); do not invent data.
2. **Evaluate each tape pinned** (discovery recency-based would mix tapes):
   ```bash
   python3 -m src.analytics.real_net_of_cost_evaluation \
     --data-dir data/raw --out research_state --symbol BTC --bar-duration-seconds 15 \
     --orderflow-path data/raw/orderflow_okx_41a.json
   # repeat for 41b, 41c
   ```
   Record each `REAL_NET_OF_COST_EVAL_23_<stamp>` path + sha256.
3. **Seal `ORDERFLOW_ROBUSTNESS_41_<UTC>.{json,md}`**: per-tape verdict, orderflow-only net-of-cost Sharpe, trades, cost, max-DD, kill-switch, orderflow IC, inputs/provenance. Pre-declared bar: **GO only if orderflow-only net-of-cost Sharpe > 0 on ≥2/3 new tapes AND no kill-switch breach**; else REPLICATION/NO-GO. Report every tape, no cherry-pick.

### Track B — Dense real options time-series decisive test (TIME-BASED; poll, do not block)
Can a genuinely time-varying options signal carry net-of-cost alpha? (prior: 1 snapshot degenerate; 3 sparse snapshots 0 net-of-cost trades.)

1. **Acquire dense real series**: ≥12 real options snapshots at ≤10-min spacing over ≥2h (OKX tickers current-only, poll via `schedule_wakeup`/`cron_create`; do not block). Unique `--timestamp` per poll:
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.data.public_export_acquisition --underlying BTC --skip-orderflow \
     --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --data-dir data/raw --out research_state
   ```
   Seed with existing `options_okx_BTC_20261114T153357Z.json`, `options_okx_BTC_20261114T171725Z.json` + new polls. List every snapshot path + sha256 in final artifact.
2. **Time-varying net-of-cost falsification** reusing existing primitives (no `phaseNN_*`). Template `scripts/eval33_options_leg_falsification.py`; build thin `scripts/eval41_options_timeseries_net_of_cost.py` that: loads all real snapshots (`discover_all_real_options_exports`/`load_snapshot_signals`), aligns to bars from `data/raw/orderflow_okx_BTC-USD-SWAP-40.json`, sweeps pre-declared options-only grid including lower thresholds `{0.01,0.02,0.05,0.1,0.2,0.5}`, reports IC/permutation vs orderflow-only+flat/block-bootstrap CI/PBO/BH-FDR.
3. **Seal `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>.{json,md}`** with full grid, per-snapshot signal levels (must show ≥2 distinct time-varying levels), IC, permutation, CI, verdict. Pre-declared bar: **GO only if any options-only variant has (a) OOS Sharpe > max(orderflow-only,flat), (b) permutation p<0.05 vs that control, (c) 95% CI excludes 0, (d) ≥2 distinct time-varying levels with |IC|>1e-9**; else REPLICATION/NO-GO (options pillar definitively closed as untestable with available real data).

### Per-session contract
Append measured verdict to this handoff. REPLICATION/NO-GO keeps campaign terminated; GO requires verifying sealed artifact on new real data + pre-registered replication campaign. No GO without sealed evidence.

## BOTTLENECKS REMOVED / SESSION READINESS (verified 2026-11-14T18:21:06Z — **IMMEDIATE ACTION POSSIBLE**)
- **EVAL-40 sealed:** `research_state/EVAL_40_MEASUREMENT_20261114T173912Z.{json,md}` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z` (sha256 json `dd6c133ce2a8794a70aaf398125aa62fff1e6852b605c10b5c3d2eef97b9cd9e`). No EVAL-41 artifacts/tapes/scripts exist yet.
- **Env verified:** `./scripts/verify_env.sh --check` → OK (EVAL-37 6/6, EVAL-36 7/7). Deps in `.venv-deps/` (git-ignored). **Always** `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` before python/pytest (bare `python3 -m ...` fails with missing numpy). `.env` **absent**; no stale `*.lock`/`*.pid` in `research_state/`.
- **Real inputs (do not delete):** `data/raw/orderflow_okx_BTC-USD-SWAP-40.json` (84,800 trades, ids `485439506..485524305`), `data/raw/orderflow_okx_BTC-USD-SWAP.json`, `data/raw/options_okx_BTC_20261114T153357Z.json`, `data/raw/options_okx_BTC_20261114T171725Z.json`. Synthetic `*_synthetic.json` never for real eval.
- **Loader gotchas:** `load_real_orderflow`/`load_real_options_chain` pick latest/alpha-last export — always use `--orderflow-path` for a specific tape and explicit file for specific options snapshot. Acquisition: `--orderflow-symbol` + `--timestamp` unique to avoid overwrites; `--after-cursor` walks older-than.
- **Network probe (2026-11-14T18:21:06Z):** OKX public read-only reachable — options instruments HTTP 200; history-trades HTTP 200. Track A viable immediately; Track B polling viable.
- **Reusable modules (no new orchestrators):** `src/data/public_export_acquisition.py`, `src/data/options_timeseries.py`, `src/analytics/options_time_varying_signal.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/analytics/integrated_options_orderflow_evaluation.py`; template `scripts/eval33_options_leg_falsification.py`.

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

## EVAL-41 SESSION LOG (append-only)
- 2026-11-14T18:21:06Z: Handoff refreshed for next session (`INIT-2026-11-14T18:21:06Z-EVAL-41-EXECUTE-AND-SEAL`). Readiness verified (env/checks OK, .env absent, no locks, no EVAL-41 artifacts, OKX public endpoints reachable). **No EVAL-41 sealed this session** — next agent must execute Track A immediately and seal `ORDERFLOW_ROBUSTNESS_41_<UTC>` or `EVAL_41_BLOCKED_<UTC>`.