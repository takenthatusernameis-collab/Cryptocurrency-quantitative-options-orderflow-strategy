# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T17:33:33Z UTC — TASK ID `INIT-2026-11-14T17:33:33Z-EVAL-40-EXECUTE-SEAL`** (authoritative; supersedes all prior task IDs/messages). Inferred from repo charter: *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement*. Campaign **TERMINATED (EVAL-36 `TERMINATE_NO_GO`)** and durability-closed for available real data (EVAL-39 REPLICATION, ledger `DURABILITY_LEDGER_39_20261114T163011Z`). **EVAL-40 acquisition and pre-registration are already sealed; this session MUST execute the heavy evaluation and seal the measured artifact. No handoff-only, discovery-only, re-read, or re-acquisition session is progress. Bottleneck removed: the pre-registration's unpinned loader command would select the older base tape, so the pinned command below is authoritative.**

## MANDATORY HEAVY-WORK CAMPAIGN (cannot be avoided)
Complete the EVAL-40 execution every session (or seal BLOCKED with exact failing command + stderr). All steps are paper-only, real-data only.

1. **PRE-FLIGHT THE SEALED PREREG (fast; do not reacquire).** Confirm `research_state/EVAL_40_PREREGISTRATION_20261114T172130Z.{json,md}` exists and these hashes still match:
   ```bash
   sha256sum data/raw/orderflow_okx_BTC-USD-SWAP-40.json data/raw/options_okx_BTC_20261114T171725Z.json
   # expected: a105db1c323c9c64db75882c367f84a81f2ac87374ed62ad490d334af484bc4b
   #           159bc3b8f27a605f2ac3d2430a51485a16c0781aee04c7f3ec79e295934f2eca
   ```
   If either hash differs or the pinned loader cannot load 84,800 trades, seal `EVAL_40_BLOCKED_<UTC>.{json,md}` with exact command/exit/stderr; do **not** overwrite raw files.
2. **EXECUTE & SEAL EVAL-40 (the heavy work).** Run the corrected pre-registered command:
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.analytics.real_net_of_cost_evaluation \
     --data-dir data/raw --out research_state \
     --symbol BTC --bar-duration-seconds 15 \
     --orderflow-path data/raw/orderflow_okx_BTC-USD-SWAP-40.json
   ```
   The `--orderflow-path` pin is required: discovery is recency-based and would otherwise select the base 09:05→15:33 tape. The dataset and GO/NO-GO criteria in the pre-registration are unchanged. Verify the generated `REAL_NET_OF_COST_EVAL_23_<stamp>` artifact reports the EVAL-40 window (84,800 trades, 02:25:00.798Z→09:05:22.330Z), then seal `EVAL_40_MEASUREMENT_<UTC>.{json,md}` referencing that artifact's path + SHA-256, verdict, checks, and measured numbers. If execution fails, seal `EVAL_40_BLOCKED_<UTC>.{json,md}` with exact command/exit/stderr.
3. **RECORD THE OUTCOME HERE.** Append the measured verdict to this handoff. `REPLICATION`/NO-GO keeps the campaign terminated; `REFUTED` requires sealing the exact contradicting evidence and a new pre-registered replication campaign. Never claim GO without a verifying sealed artifact on the new real data.

**BLOCKED protocol:** if the evaluation cannot run (missing input, tool failure, environment), seal `EVAL_40_BLOCKED_<UTC>.{json,md}` with exact command, exit code, stderr, environment facts, and what was attempted. That is the only acceptable non-advancing outcome.

## BOTTLENECKS REMOVED / SESSION READINESS (verified 2026-11-14T17:33:33Z — **IMMEDIATE ACTION POSSIBLE**)
- `.env` **absent** (paper-only; must stay absent). No stale `*.lock`/`*.pid` in `research_state/`.
- Runtime deps bootstrapped in `.venv-deps/` (git-ignored). **Always** `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` before python/pytest.
- EVAL-40 real inputs already acquired: `data/raw/orderflow_okx_BTC-USD-SWAP-40.json` (84,800 trades, 1,602 bars, disjoint trade-id range `485439506..485524305`) and `data/raw/options_okx_BTC_20261114T171725Z.json` (827 quotes / 14 expiries). Pinned loader verified to load 84,800 trades; options loader selected 827 quotes. **No technical blocker to Step 2.**
- Do **not** rerun acquisition. If a future tape is required, use a unique `--orderflow-symbol` and `--after-cursor <oldest trade id>`; the default symbol would overwrite the existing base tape.
- `scripts/verify_env.sh` available for env bootstrap/check. Synthetic fixtures in `data/raw/` must never be used for real evaluation.

## CURRENT MEASURED STATE (ground truth)
- **EVAL-02..39 sealed** (immutable). **EVAL-36:** `FINAL_TERMINATION_MEMO_36_20261114T145419Z` — `TERMINATE_NO_GO`.
- **EVAL-37:** `FINAL_TERMINATION_AUDIT_37_20261114T152849Z` — **PASS 9/9** (earlier 151805Z FAIL kept as history).
- **EVAL-38:** `EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z` — **REPLICATION** of EVAL-35 NO-GO on re-acquired real tape (Sharpe -7.9539, 1221 trades, $179.28 cost, max-DD 0.8679, kill-switch breach).
- **EVAL-39:** `DURABILITY_LEDGER_39_20261114T163011Z` (**REPLICATION**) + rerun `REAL_NET_OF_COST_EVAL_23_20261114T162521Z` (NO-GO 8/11; failed `options_signal_exists, combined_net_of_cost_superior, options_signal_tradable`; `options_leg_degenerate=true`; `combined_alpha.ic_mean=-0.000258`, `options_alpha` 0.0 all horizons, `orderflow_alpha.ic_mean=0.041876`, permutation p=0.000999 combined worse than best single pillar). Qualitative replication on different window, not bit-level reproduction.
- **EVAL-40:** acquisition `PUBLIC_EXPORT_ACQUISITION_20261114T171725Z` + pre-registration `EVAL_40_PREREGISTRATION_20261114T172130Z` are sealed; **measured EVAL-40 artifact is still missing and is this session's required output.**
- **Key facts (do not re-litigate):** options leg static broadcast → zero time-variation (sealed root cause; do not modify `integrated_options_orderflow_evaluation.py::_causal_options_signal_series`). Synthetic-preferring loaders in `src/campaign/integrated.py` and `src/analytics/integrated_options_orderflow_evaluation.py::main` must not be used for real evaluation; use `src.analytics.real_net_of_cost_evaluation` / `load_real_*` with the explicit EVAL-40 path.

## HARD CONSTRAINTS / INVARIANTS
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Sealed artifacts EVAL-02..39 and the EVAL-40 acquisition/pre-registration artifacts are immutable; append new timestamped artifacts only. Do not modify sealed artifacts to make checks pass.
- Network: public read-only market data only, polite rate limiting, only if required.
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`; no `phaseNN_*` orchestrator wrappers.
- Prohibited: discovery runs, re-litigating sealed EVALs, broad `research_state/` enumeration, full test-suite runs, workflow edits, handoff-only sessions.

## HANDOFF DISCIPLINE
- This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands only; no timestamped handoff copies. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with no task IDs.
- Record measured numbers, not intentions. No GO without a verifying sealed artifact.
- Final responses must not ask follow-up questions.
