# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T18:28:02Z UTC — TASK ID `INIT-2026-11-14T18:28:02Z-EVAL-41-EXECUTE-AND-SEAL`** (authoritative; supersedes all prior task IDs/messages, including `INIT-2026-11-14T18:21:06Z-EVAL-41-EXECUTE-AND-SEAL`, `INIT-2026-11-14T17:39:12Z-EVAL-41-DECISIVE-FALSIFICATION`, and `INIT-2026-11-14T17:33:33Z-EVAL-40-EXECUTE-SEAL`). Inferred from the repository charter (`Cryptocurrency-quantitative-options-orderflow-strategy`): *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement*. **EVAL-40 is DONE/sealed** (`EVAL_40_MEASUREMENT_20261114T173912Z` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z`, NO-GO 8/11, REPLICATION). Campaign remains **TERMINATED (EVAL-36 `TERMINATE_NO_GO`)**, but two decisive open questions remain: (A) options-leg degeneracy — every net-of-cost run used 1 options cross-section (EVAL-29/40) or 3 sparse snapshots (EVAL-27/30/33); (B) orderflow sign flips across windows — EVAL-33 held-out Sharpe +4.81 vs EVAL-39 IC +0.0419 vs EVAL-40 orderflow-only Sharpe -5.35. **The next session MUST execute the EVAL-41 campaign below and seal at least one EVAL-41 artifact. Handoff-only, discovery-only, re-read, re-acquisition-without-evaluation, and full-suite runs are NOT progress.**

## MANDATORY HEAVY-WORK CAMPAIGN — EVAL-41 (cannot be avoided)
**Do Track A first (immediate, no waiting).** Seal at least one per session: `ORDERFLOW_ROBUSTNESS_41_<UTC>`, `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>`, or `EVAL_41_BLOCKED_<UTC>` (with exact command/exit/stderr/attempts). Paper-only, real-data only, no synthetic fallback, no `phaseNN_*` wrappers.

### Track A — Orderflow cross-window robustness (IMMEDIATE, highest priority)
Question: does orderflow have persistent net-of-cost edge, or was EVAL-33's +4.81 window-lucky?

1. **Acquire 3 NEW disjoint real tapes** (historical pagination, no waiting). OKX `after` returns trades **older than** the cursor (verified: `after=485439506` → `485439505, 485439504, ...`). Start at the EVAL-40 tape's oldest id `485439506` and walk downward, reading each new tape's oldest id before the next call. Use a unique `--orderflow-symbol` and `--timestamp` per call; `--request-delay-seconds 0.15` stays polite (OKX public limit ≈20 req/2s):
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.data.public_export_acquisition --underlying BTC --skip-options \
     --orderflow-instrument BTC-USD-SWAP --orderflow-symbol 41a \
     --after-cursor 485439506 --request-delay-seconds 0.15 \
     --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     --data-dir data/raw --out research_state
   python3 -c "import json;d=json.load(open('data/raw/orderflow_okx_41a.json'));ids=[int(t['trade_id']) for t in d['trades']];print(len(ids),min(ids),max(ids))"
   # use min(ids) as the next --after-cursor for 41b, then 41c
   ```
   Each tape must span ≥6.46 h (1550 bars × 15 s). Record empty/overlap/exhaustion explicitly per window; never reuse overlapping cursors or invent data.
2. **Evaluate each tape pinned** (do not let recency-based discovery mix tapes):
   ```bash
   python3 -m src.analytics.real_net_of_cost_evaluation \
     --data-dir data/raw --out research_state --symbol BTC --bar-duration-seconds 15 \
     --orderflow-path data/raw/orderflow_okx_41a.json
   # repeat for 41b, 41c; verified runtime ≈84 s per tape
   ```
   Record each `REAL_NET_OF_COST_EVAL_23_<stamp>` path + sha256, plus `orderflow_only_wf.oos_sharpe`, `oos_max_drawdown`, `num_trades`, `total_cost_usd`.
3. **Seal `ORDERFLOW_ROBUSTNESS_41_<UTC>.{json,md}`**: per-tape verdict, orderflow-only net-of-cost Sharpe, trades, cost, max-DD, kill-switch, orderflow IC, inputs/provenance. Pre-declared bar: **GO only if orderflow-only net-of-cost Sharpe > 0 on ≥2/3 new tapes AND no kill-switch breach (max-DD ≤ 0.20)**; else REPLICATION/NO-GO. Report every tape; no cherry-picking.

### Track B — Dense real options time-series decisive test (NON-BLOCKING; poll, do not block)
Question: can a genuinely time-varying options signal carry net-of-cost alpha? (Prior: 1 snapshot degenerate; 3 sparse snapshots produced 0 net-of-cost trades.)

1. **Acquire dense real series**: ≥12 real options snapshots at ≤10-min spacing over ≥2 h. OKX tickers are current-only, so poll with `schedule_wakeup`/`cron_create` (never block the session). Unique `--timestamp` per poll:
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.data.public_export_acquisition --underlying BTC --skip-orderflow \
     --request-delay-seconds 0.15 \
     --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --data-dir data/raw --out research_state
   ```
   Seed with existing `options_okx_BTC_20261114T153357Z.json`, `options_okx_BTC_20261114T171725Z.json`, plus new polls. List every snapshot path + sha256 in the final artifact.
2. **TAPE-ALIGNMENT GOTCHA (verified — do not repeat the false negative):** the two existing snapshots are at `15:39:08Z` and `17:21:33Z`, both **after** the newest existing orderflow tape ends (`15:33:56Z`). Aligning Track B to the EVAL-40 tape (ends `09:05:22Z`) or to `orderflow_okx_BTC-USD-SWAP.json` (ends `15:33:56Z`) yields **zero usable snapshots → false flat/degenerate**. Acquire a fresh orderflow tape with **no** `--after-cursor` (it fetches newest-first and spans the latest ~6.46 h), then align snapshots to that tape's bars.
3. **Load snapshots with the correct call**: `load_snapshot_signals('BTC', 'data/raw')` — the first positional argument is `symbol`, **not** a path. Verified: 2 snapshots load with distinct levels `-0.40919 @15:39:08Z` and `-0.386624 @17:21:33Z`.
4. **Time-varying net-of-cost falsification** reusing existing primitives (no `phaseNN_*`). Template: `scripts/eval33_options_leg_falsification.py`; modules: `src/analytics/options_time_varying_signal.py`, `src/data/options_timeseries.py`. Build thin `scripts/eval41_options_timeseries_net_of_cost.py` that loads all real snapshots, aligns them to the fresh tape's bars, sweeps the pre-declared options-only grid including lower thresholds `{0.01,0.02,0.05,0.1,0.2,0.5}`, and reports IC/permutation vs orderflow-only + flat, block-bootstrap CI, PBO, BH-FDR.
5. **Seal `EVAL_41_TIMESERIES_NET_OF_COST_<UTC>.{json,md}`** with the full grid, per-snapshot signal levels (must show ≥2 distinct time-varying levels), IC, permutation, CI, verdict. Pre-declared bar: **GO only if any options-only variant has (a) OOS Sharpe > max(orderflow-only, flat), (b) permutation p<0.05 vs that control, (c) 95% CI excludes 0, (d) ≥2 distinct time-varying levels with |IC|>1e-9**; else REPLICATION/NO-GO (options pillar definitively closed as untestable with available real data).
6. **Pilot now**: run the new script immediately on the 2 existing snapshots + the fresh tape to validate the pipeline; label it PILOT (insufficient for GO), then replace it with the ≥12-snapshot decisive run once polling completes.

### Per-session contract
Append the measured verdict to this handoff. REPLICATION/NO-GO keeps the campaign terminated; GO requires a sealed verifying artifact on new real data plus a pre-registered replication campaign. No GO without sealed evidence.

## BOTTLENECKS REMOVED / SESSION READINESS (verified 2026-11-14T18:28:02Z — IMMEDIATE ACTION POSSIBLE)
- **EVAL-40 sealed:** `research_state/EVAL_40_MEASUREMENT_20261114T173912Z.{json,md}` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z` (sha256 json `dd6c133ce2a8794a70aaf398125aa62fff1e6852b605c10b5c3d2eef97b9cd9e`). **No EVAL-41 artifacts/scripts exist yet** (checked).
- **Env verified:** `./scripts/verify_env.sh --check` → OK (EVAL-37 6/6, EVAL-36 7/7). Deps in `.venv-deps/` (git-ignored). **Always** `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` before python/pytest (bare `python3 -m ...` fails on missing numpy). `.env` **absent**; no stale `*.lock`/`*.pid` in `research_state/`.
- **Network verified:** OKX public read-only endpoints work through the acquisition module's `requests` session (default UA → HTTP 200). **Do not probe with bare `urllib` (no User-Agent): OKX returns HTTP 403 — that is a probe artifact, not a block.** Use `src.data.public_export_acquisition` or set a normal UA.
- **Real inputs (do not delete):** `data/raw/orderflow_okx_BTC-USD-SWAP-40.json` (84,800 trades, ids `485439506..485524305`, `02:25:00.798Z..09:05:22.330Z`), `data/raw/orderflow_okx_BTC-USD-SWAP.json` (77,700 trades, ids `485524306..485602005`, `09:05:22.330Z..15:33:56.432Z`), `data/raw/options_okx_BTC_20261114T153357Z.json`, `data/raw/options_okx_BTC_20261114T171725Z.json`. Synthetic `*_synthetic.json` never for real eval.
- **Track A executable now:** the pinned eval was run end-to-end on `-40` → `NO-GO`, 8/11, `options_leg_degenerate=true`, ≈84 s. Cursors are disjoint; `after` returns older trades.
- **Track B executable after a fresh tape:** both existing snapshots load and are distinct; the only missing piece is a tape covering `15:39Z..now` (see gotcha above).
- **Loader gotchas:** `load_real_orderflow`/`load_real_options_chain` pick latest/alpha-last export — always use `--orderflow-path` for a specific tape and an explicit file for a specific options snapshot. Acquisition needs unique `--orderflow-symbol` + `--timestamp` to avoid overwrites; `--after-cursor` walks older-than.
- **Reusable modules (no new orchestrators):** `src/data/public_export_acquisition.py`, `src/data/options_timeseries.py`, `src/analytics/options_time_varying_signal.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/analytics/integrated_options_orderflow_evaluation.py`; template `scripts/eval33_options_leg_falsification.py`.

## CURRENT MEASURED STATE (ground truth)
- **EVAL-02..40 sealed** (immutable). **EVAL-36:** `FINAL_TERMINATION_MEMO_36_20261114T145419Z` — `TERMINATE_NO_GO`.
- **EVAL-37:** `FINAL_TERMINATION_AUDIT_37_20261114T152849Z` — **PASS 9/9**.
- **EVAL-38:** `EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z` — REPLICATION (Sharpe -7.9539, 1221 trades, $179.28 cost, max-DD 0.8679, kill-switch breach).
- **EVAL-39:** `DURABILITY_LEDGER_39_20261114T163011Z` (REPLICATION) + `REAL_NET_OF_COST_EVAL_23_20261114T162521Z` (NO-GO 8/11; `options_leg_degenerate=true`; `combined_alpha.ic_mean=-0.000258`, `options_alpha` 0.0, `orderflow_alpha.ic_mean=0.041876`; permutation p=0.000999 combined worse than best single pillar).
- **EVAL-40:** `EVAL_40_MEASUREMENT_20261114T173912Z` → `REAL_NET_OF_COST_EVAL_23_20261114T173647Z`. **NO-GO 8/11, REPLICATION.** Disjoint window `02:25:00.798Z→09:05:22.330Z`, 84,800 trades / 1,602 bars. Failed `options_signal_exists, combined_net_of_cost_superior, options_signal_tradable`; `options_leg_degenerate=true` (signal stdev 0.0, abs IC 3.97e-18). combined_alpha `ic_mean=-0.029023` (t=-1.807); orderflow_alpha `ic_mean=-0.010087`; permutation observed diff `-0.093161`, p=0.000999. WF: combined Sharpe 1.858414 (232 trades, $415.64); options-only 4.246051 (688 trades); orderflow-only **-5.349272** (614 trades, $646.34); flat 0.0.
- **EVAL-41 readiness re-verified 2026-11-14T18:28:02Z:** Track A command executed with `--no-write` on `-40` (NO-GO 8/11, degenerate, ≈84 s); `load_snapshot_signals('BTC','data/raw')` returns 2 distinct signals; OKX `after=485439506` returns older ids.
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
- 2026-11-14T18:21:06Z: Handoff refreshed for next session (`INIT-2026-11-14T18:21:06Z-EVAL-41-EXECUTE-AND-SEAL`). Readiness verified (env/checks OK, .env absent, no locks, no EVAL-41 artifacts, OKX public endpoints reachable). **No EVAL-41 sealed this session.**
- 2026-11-14T18:28:02Z: Handoff refreshed (`INIT-2026-11-14T18:28:02Z-EVAL-41-EXECUTE-AND-SEAL`). Re-verified env (`verify_env.sh --check` OK), `.env` absent, no locks, no EVAL-41 artifacts/scripts. Ran the Track A pinned eval with `--no-write` on `-40` (NO-GO 8/11, degenerate, ≈84 s). Confirmed OKX `after=485439506` returns older ids; confirmed 2 existing options snapshots load via `load_snapshot_signals('BTC','data/raw')` with distinct levels. **Removed two bottlenecks:** (1) documented that bare-`urllib` OKX probes return 403 while the module's `requests` session returns 200; (2) documented that Track B must not align to either existing tape (both end before the snapshots) and must acquire a fresh no-cursor tape. **No EVAL-41 artifact sealed this session** — the next agent must execute Track A and seal `ORDERFLOW_ROBUSTNESS_41_<UTC>` or `EVAL_41_BLOCKED_<UTC>`.