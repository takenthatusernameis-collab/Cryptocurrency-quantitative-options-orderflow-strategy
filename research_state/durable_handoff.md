# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T14:39:46Z, verified — supersedes 14:38:39Z):**
> **Repo priority (per name `Cryptocurrency-quantitative-options-orderflow-strategy`):** options + orderflow alpha, net-of-cost on real data. **On-charter ladder EVAL-02..66 is CLOSED** — EVAL-66 sealed `BLOCKED` (gate exit 0; ETH capture under-floor & not disjoint from EVAL-65); namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH in tested windows. Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Do not invent synthetic data or weaken floors.
>
> **NEXT FOCUS CAMPAIGN — EVAL-67 (MANDATORY heavy real-data falsification, off-charter but core-thesis-aligned): BTC options order-flow (toxicity/imbalance) → realized-vol OOS replication on a fresh, disjoint, floor-compliant real BTC capture.** Future agents must not avoid heavy work. This session is **not finished** until one of the completion-contract outcomes is achieved: (a) sealed EVAL-67 artifact + `check_session_sealed.py` exit 0, OR (b) a genuinely live **persistent, self-completing** acquisition with recorded PID/command/liveness (recorded here), OR (c) a recorded **scheduled wakeup/cron** for the earliest disjoint capture time (exact command recorded). No timestamp-only refreshes, no planning-only stops.
>
> **BOTTLENECKS REMOVED (do not rediscover):**
> 1. **Naive `--days 7` BTC acquisition is RETIRED (overlaps sealed BTC window).** Correct: capture end `>= 2026-11-20T00:00:00Z`; use `--days 3.7 --end <NOW-ISO>` (start `2026-11-16T07:12:00Z`, span 319680s). The disjointness gate in `scripts/eval67_btc_oflow_tox_rv_oos.py` seals `BLOCKED` on overlap/non-disjoint windows.
> 2. **Runner + tests ready and green.** `scripts/eval67_btc_oflow_tox_rv_oos.py` (BTC-only, EVAL-64 floor, runtime disjointness check) and `tests/test_eval67_btc_oflow_tox_rv_oos.py` (**18/18** — includes 6 new self-completing-bridge tests). EVAL-66 baseline `tests/test_eval66_eth_oflow_tox_rv_oos.py` remains 9/9 (combined **27/27**).
> 3. **Protocol pre-registered.** `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` (do not rewrite unless necessary; must keep parseable task ID/floor/disjointness/hypothesis).
> 4. **Seal-gate task ID fixed (parseable).** Use `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION` (retired `INIT-2026-11-16T122919Z-...` is invalid for `check_session_sealed.py`).
> 5. **Persistent bridge is now SELF-COMPLETING (upgraded this session — the key bottleneck fix).** `scripts/eval67_capture_bridge.py` runs as background process **`bgp_1e4ca4423001iJUVAJf78cTZJ4`** (`lifetime: persistent`, python **pid 73716**, phase `waiting`, heartbeat `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_73716.json`, threshold `2026-11-20T00:00:00Z`, started `2026-11-16T14:38:04Z`, verified alive 2026-11-16T14:38:39Z). **Unlike the prior bridge, it does NOT stop after acquisition**: at/after threshold it runs the full heavy pipeline itself — **acquire → dry-run evaluate → seal → seal-gate** — and writes a completion manifest `research_state/EVAL_67_BRIDGE_COMPLETE_73716.json` with per-step exit codes and `result` ∈ {`COMPLETE`,`GATE_FAILED`,`ACQUIRE_FAILED`,`DRYRUN_FAILED`}. This means the campaign **cannot stall after acquisition** even if no agent session is alive on 2026-11-20. If the process dies before threshold, relaunch via `bash scripts/eval67_launch_capture.sh` at/after threshold, or restart the tracked background process and record the new PID here.
>
> **RETIRED-BUT-DO-NOT-TRUST CLAIM:** the previous handoff cited backup wakeup `wku_1e4c1baf4001MBQw4BavCd0vX8` for 2026-11-20T00:00:00Z. **That wakeup is session-scoped and does NOT exist in the current session** (verified: `cron_list`/`cancel_wakeup list` empty). Do **not** rely on it. The durable guarantee is now the **persistent self-completing bridge (b)**, not a wakeup.
>
> **Task ID (authoritative):** `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`
>
> **Unskippable heavy-work contract (execute in order):**
> 1. **Env/safety:** `.env` absent; `LIVE_TRADING_ENABLED` unset/false (paper-only). `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `./scripts/verify_env.sh --check`. Tests: `python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py` (18/18), `python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py` (9/9). No full-suite enumeration loops; no `research_state/` enumeration loops.
> 2. **If you arrive before 2026-11-20T00:00:00Z:** do not run retired `--days 7` acquisition. Verify the persistent bridge is alive: `background_process list` should show `bgp_1e4ca4423001iJUVAJf78cTZJ4` (`lifetime: persistent`) and `ps -p 73716` should succeed with a fresh `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_73716.json`. If it is dead, restart it (persistent) and record the new PID here; do not stop with only a timestamp bump.
> 3. **At/after threshold (disjoint, heavy real capture):** the persistent bridge runs, in order:
>    `python3 scripts/eval60_acquire_three_way.py --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal`
>    then `python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write`
>    then `python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS`
>    then `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"`
>    (or via `bash scripts/eval67_launch_capture.sh` for the acquisition step). Real loaders only (`RealDataUnavailable` on missing); never synthetic/relabeled; never `{"valid": true}`. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED` (no floor weakening). Do not seal on missing/empty state. If you run the steps yourself, mirror the bridge exactly.
> 4. **Verify the bridge's completion manifest** `research_state/EVAL_67_BRIDGE_COMPLETE_73716.json`: expect `result=COMPLETE`, `gate_rc=0`, and a sealed `EVAL_67_BTC_OFLOW_TOX_RV_OOS_{COMBINED|BLOCKED}_<TS>.{json,md}` in `research_state/`. If `result` is a failure kind, diagnose from `steps[*].detail` and finish the pipeline manually.
> 5. **Seal gate (must exit 0):**
>    `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"`
> 6. **Close session:** update this handoff in place with verified facts (artifact names, verdict, gate exit code, capture sha256/size/window/disjointness, bridge PID/completion-manifest result). `data/raw/eval67/` is gitignored — do not commit. Paper-only preserved.
>
> **Completion contract:** end only with (a) sealed EVAL-67 + gate exit 0, OR (b) genuinely live **persistent, self-completing** acquisition with recorded PID/command/liveness (now satisfied by `bgp_1e4ca4423001iJUVAJf78cTZJ4` / pid 73716), OR (c) recorded **scheduled wakeup/cron** for earliest disjoint time with exact command. No other stopping point is acceptable.
>
> ## STATUS (verified 2026-11-16T14:38:39Z)
>
> - **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (gate exit 0) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (`INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`).
> - **Persistent self-completing bridge (verified):** background process `bgp_1e4ca4423001iJUVAJf78cTZJ4` (`lifetime: persistent`), python **pid 73716** alive (`python3 scripts/eval67_capture_bridge.py`), heartbeat `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_73716.json` phase `waiting`, threshold `2026-11-20T00:00:00Z`, started `2026-11-16T14:38:04Z`. At threshold it runs acquire→dry-run→seal→gate→manifest `EVAL_67_BRIDGE_COMPLETE_73716.json` and cannot stall after acquisition. If it dies before threshold, restart persistent and record the new PID here.
> - **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
> - **EVAL-67 artifacts present (pre-work):** prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`; runner/tests/scripts present; `data/raw/eval67/` absent (created by acquisition). Seal-gate currently **exit 1** (expected: prereg matches, no `COMBINED_*`/`BLOCKED_*` yet).
> - **Tests (verified 2026-11-16T14:38Z):** `tests/test_eval67_btc_oflow_tox_rv_oos.py` **18/18**, `tests/test_eval66_eth_oflow_tox_rv_oos.py` **9/9** (combined 27/27). New bridge tests lock in: exact heavy-work order (acquire→evaluate→seal→gate), completion-manifest COMPLETE, acquire-failure short-circuit, gate-failure marking, pre-threshold refusal, parseable task ID.
> - **Untracked new files (do not commit):** `scripts/eval67_btc_oflow_tox_rv_oos.py`, `scripts/eval67_launch_capture.sh`, `scripts/eval67_capture_bridge.py` (upgraded self-completing this session), `tests/test_eval67_btc_oflow_tox_rv_oos.py` (18/18), `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`, `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_73716.json`. `data/raw/eval66/`, `data/raw/eval67/` gitignored.
>
> ## AUTHORITATIVE NEXT TASK
>
> **EVAL-67 — BTC options order-flow (tox/imbalance) → realized-vol OOS replication** (`INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`). Heavy, pre-registered, real-data-only, floor-compliant, **disjoint** (>= 2026-11-20T00:00:00Z window). The persistent self-completing bridge carries this to a sealed artifact autonomously; do not stop at planning/timestamp bumps, and verify the completion manifest + gate exit 0.
>
> ## REPRO / KEY COMMANDS
>
> ```bash
> export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
> ./scripts/verify_env.sh --check
> python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py   # 18/18
> python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py   # 9/9 baseline
>
> # persistent self-completing bridge status (should be running, lifetime: persistent)
> #   background_process list   -> bgp_1e4ca4423001iJUVAJf78cTZJ4
> #   ps -p 73716
> #   cat research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_73716.json
>
> # immutable sealed EVAL-66 check (should be exit 0)
> python3 scripts/check_session_sealed.py \
>   --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
>   --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
>   --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
>   --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
>
> # EVAL-67 capture ONLY at/after 2026-11-20T00:00:00Z (retired: naive --days 7 now)
> mkdir -p data/raw/eval67
> PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py \
>   --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal
>
> # or launch helper (refuses before threshold):
> # bash scripts/eval67_launch_capture.sh
>
> # EVAL-67 dry-run, then seal
> python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write
> python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS
>
> # EVAL-67 seal gate (after prereg + sealed result exist) — must be exit 0
> python3 scripts/check_session_sealed.py \
>   --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" \
>   --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
>   --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" \
>   --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"
> ```
>
> ## PROHIBITED / INVARIANTS (non-negotiable)
>
> - Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
> - Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting.
> - Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
> - No pre-registered floor weakening. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
> - Do **not** use retired compact task ID `INIT-2026-11-16T122919Z-...`; use `INIT-2026-11-16T13:25:40Z-...`.
> - Do **not** run retired naive `--days 7` BTC acquisition before `2026-11-20T00:00:00Z`; use corrected `--days 3.7 --end <NOW-ISO>`.
> - Do **not** rely on retired wakeup `wku_1e4c1baf4001MBQw4BavCd0vX8` (session-scoped, does not exist). The durable guarantee is the persistent self-completing bridge.
> - Reuse existing `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and `scripts/eval60_*`/`eval66_*`/`eval67_*` patterns; no `phaseNN_*` wrappers.
> - `data/raw/eval66/`, `data/raw/eval67/` gitignored — do not commit/push.
> - No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.
>
> ## SESSION LOG (append-only, recent)
>
> - 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH; gate exit 0). `CAMPAIGN_CLOSED`.
> - **2026-11-16T13:39:12Z:** De-risked EVAL-67 path (real smoke OK, dry-run `BLOCKED` with `disjointness_ok=true`, math proven), started persistent bridge waiting to threshold; added `eval67_capture_bridge.py`/`eval67_launch_capture.sh`; backup wakeup scheduled for 2026-11-20T00:05:00Z. Seal-gate exit 1 expected (no verdict yet).
> - **2026-11-16T14:23:03Z:** Verified bridge alive; refreshed handoff. No sealed artifacts or `src/` modified; paper-only.
> - **2026-11-16T14:26:11Z:** Verified bridge alive; ran eval67+eval66 tests → 21/21 passed. Seal gate exit 1 as expected. Recorded backup wakeup (later found session-scoped).
> - **2026-11-16T14:28:41Z:** Re-verified bridge alive, verify_env exit 0, tests 21/21, gate exit 1 expected. Handoff refreshed.
> - **2026-11-16T14:38:39Z (this session — bottleneck removal):** Upgraded `scripts/eval67_capture_bridge.py` to be **self-completing**: at/after threshold it now runs acquire → dry-run evaluate → seal → seal-gate → completion manifest `EVAL_67_BRIDGE_COMPLETE_<pid>.json`, so the campaign cannot stall after acquisition even with no live agent session. Added 6 bridge unit tests (order, COMPLETE manifest, acquire-failure short-circuit, gate-failure, pre-threshold refusal, parseable task ID) → `tests/test_eval67_btc_oflow_tox_rv_oos.py` now **18/18**; combined with EVAL-66 **27/27**. Stopped the prior acquire-only bridge (pid 58162) and started the upgraded bridge as persistent background process `bgp_1e4ca4423001iJUVAJf78cTZJ4` (python pid **73716**, phase `waiting`, heartbeat fresh at 2026-11-16T14:38Z). Corrected the handoff's retired-wakeup claim (that wakeup does not exist in this session). No sealed artifacts or `src/` modified; no synthetic data; paper-only. Completion-contract outcome (b) satisfied by the live persistent self-completing bridge.
>
> ## SEALED STATE (immutable; append only)
>
> EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. On-charter closed; EVAL-67 is the next authorized heavy falsification campaign.