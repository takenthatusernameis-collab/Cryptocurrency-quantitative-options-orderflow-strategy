# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T16:53:42Z UTC — TASK ID `INIT-2026-11-14T16:53:42Z-EVAL-40-ACQUIRE-PREREG-EVAL`** (authoritative; supersedes all prior task IDs/messages). Inferred from repo charter: *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement*. Campaign **TERMINATED (EVAL-36 `TERMINATE_NO_GO`)** and durability-closed for available real data (EVAL-39 REPLICATION, ledger `DURABILITY_LEDGER_39_20261114T163011Z`). **No handoff-only, discovery-only, or re-read session is progress. This session MUST execute the heavy-work campaign below; no other outcome advances the repository. Bottlenecks removed: .env absent, deps in .venv-deps/, public_export_acquisition module verified runnable — IMMEDIATE ACTION POSSIBLE on Step 1.**

## MANDATORY HEAVY-WORK CAMPAIGN (cannot be avoided)
Complete the next sealed artifact in this chain every session (or seal BLOCKED with exact failing command + stderr). All steps are paper-only, real-data only.

1. **ACQUIRE NEW REAL DATA (EVAL-40 prerequisite).** Fetch a public OKX tape **not overlapping** existing real orderflow `data/raw/orderflow_okx_BTC-USD-SWAP.json` (77,700 trades, 2026-11-14T09:05:22.330Z→15:33:56.432Z). Preferred: a **post-15:33:56Z** (or pre-09:05:22Z) window with enough span for ≥1550 bars @15s. Example (adjust timestamps as needed):
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.data.public_export_acquisition \
     --underlying BTC --orderflow-instrument BTC-USD-SWAP \
     --min-bars 1550 --bar-duration-seconds 15 \
     --data-dir data/raw --out research_state
   ```
   Verify outputs are non-synthetic, record SHA-256 + full provenance/command/stdout, and seal `PUBLIC_EXPORT_ACQUISITION_40_<UTC>.{json,md}`. `authenticity_verified` must remain `false` unless independently verifiable; `data_provenance="real"`. **Do not** overwrite existing raw files; use timestamped/unique names if the tool would collide.
2. **PRE-REGISTER EVAL-40 (before evaluation).** Seal `EVAL_40_PREREGISTRATION_<UTC>.{json,md}` specifying: new dataset paths+SHAs, evaluation module/CLI (`python3 -m src.analytics.real_net_of_cost_evaluation --data-dir data/raw --out research_state` or explicit inputs as supported), exact command, GO/NO-GO criteria, and sealing intent (REPLICATION/REFUTED/BLOCKED). No evaluation before this is sealed.
3. **EXECUTE & SEAL EVAL-40.** Run the pre-registered command on the new real dataset only and seal measured artifact with verdict `REPLICATION`/`REFUTED`/`BLOCKED` and full numbers. A GO claim requires a verifying sealed artifact on new real data.

**BLOCKED protocol:** if acquisition/eval cannot run (network, missing data window, tool failure), seal `EVAL_40_BLOCKED_<UTC>.{json,md}` with exact command, exit code, stderr, environment facts, and what was attempted. That is the only acceptable non-advancing outcome.

## BOTTLENECKS REMOVED / SESSION READINESS (verified 2026-11-14T16:50Z — **IMMEDIATE ACTION POSSIBLE**)
- `.env` **absent** (paper-only; must stay absent). No stale `*.lock`/`*.pid` in `research_state/`.
- Runtime deps bootstrapped in `.venv-deps/` (git-ignored). **Always** `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` before python/pytest; bare `python3 -m src.data.public_export_acquisition` fails with missing deps outside that PYTHONPATH.
- `scripts/verify_env.sh` available for env bootstrap/check. `data/raw/` contains real `orderflow_okx_BTC-USD-SWAP.json` (09:05:22Z→15:33:56Z) and `options_okx_BTC_20261114T153357Z.json` plus synthetic fixtures (do not use synthetic).
- Acquisition module: `src/data/public_export_acquisition.py` (public OKX, read-only, no credentials/.env). Prior sessions confirmed public endpoints reachable. **No remaining technical blocker to attempt step 1 now. The command in Step 1 is copy-paste runnable.**

## CURRENT MEASURED STATE (ground truth)
- **EVAL-02..38 sealed** (immutable). **EVAL-36:** `FINAL_TERMINATION_MEMO_36_20261114T145419Z` — `TERMINATE_NO_GO`.
- **EVAL-37:** `FINAL_TERMINATION_AUDIT_37_20261114T152849Z` — **PASS 9/9** (earlier 151805Z FAIL kept as history).
- **EVAL-38:** `EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z` — **REPLICATION** of EVAL-35 NO-GO on re-acquired real tape (Sharpe -7.9539, 1221 trades, $179.28 cost, max-DD 0.8679, kill-switch breach).
- **EVAL-39:** `DURABILITY_LEDGER_39_20261114T163011Z` (**REPLICATION**) + rerun `REAL_NET_OF_COST_EVAL_23_20261114T162521Z` (NO-GO 8/11; failed `options_signal_exists, combined_net_of_cost_superior, options_signal_tradable`; `options_leg_degenerate=true`; `combined_alpha.ic_mean=-0.000258`, `options_alpha` 0.0 all horizons, `orderflow_alpha.ic_mean=0.041876`, permutation p=0.000999 combined worse than best single pillar). Qualitative replication on different window, not bit-level reproduction.
- **Key facts (do not re-litigate):** options leg static broadcast → zero time-variation (sealed root cause; do not modify `integrated_options_orderflow_evaluation.py::_causal_options_signal_series`). Synthetic-preferring loaders in `src/campaign/integrated.py` and `src/analytics/integrated_options_orderflow_evaluation.py::main` must not be used for real evaluation; use `src.analytics.real_net_of_cost_evaluation` / `load_real_*`.

## HARD CONSTRAINTS / INVARIANTS
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Sealed artifacts EVAL-02..39 immutable; append new timestamped artifacts only. Do not modify sealed artifacts to make checks pass.
- Network: public read-only market data only, polite rate limiting, only if required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`; no `phaseNN_*` orchestrator wrappers.
- Prohibited: discovery runs, re-litigating sealed EVALs, broad `research_state/` enumeration, full test-suite runs, workflow edits, handoff-only sessions.

## HANDOFF DISCIPLINE
- This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands only; no timestamped handoff copies. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with no task IDs.
- Record measured numbers, not intentions. No GO without a verifying sealed artifact.
- Final responses must not ask follow-up questions.
