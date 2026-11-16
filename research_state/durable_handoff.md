# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T21:38:24Z — pre-threshold heavy carry, overlap strictly decreasing; EVAL-67 NOT_DUE exit 10, EVAL-68 WAIT_EVAL67 exit 10; do the PRE-THRESHOLD HEAVY WORK below then durably carry):**> **Repo-priority reading of `Cryptocurrency-quantitative-options-orderflow-strategy`:** the thesis is *crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. The on-charter ladder EVAL-02..66 is **CLOSED** (EVAL-66 sealed `BLOCKED`, seal-gate exit 0). Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Never synthetic data, never weaken the EVAL-64 floor, paper-only.
>
> **TWO SEQUENTIAL HEAVY CAMPAIGNS, in repo-priority order (crypto options order-flow → RV):**
> 1. **EVAL-67 (BTC-only, prereg'd, FIRST):** `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`. Arbiter: `python3 scripts/eval67_phaseb_gate.py`. Physics-gated to a disjoint forward window (earliest end `2026-11-19T18:08:16Z`, prereg threshold `2026-11-20T00:00:00Z`). BTC-only was recorded pre-run as *underpowered* (IC 0.088, n 596 ⇒ one-sided ≈0.70, conjunction ≈0.53).
> 2. **EVAL-68 (pooled BTC+ETH, BUILT AND TESTED, SECOND):** `INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`. This is the **power-adequate** core-thesis campaign (pooled rank-IC over BTC+ETH, requires ≥790 pooled pairs). Arbiter: `python3 scripts/eval68_phaseb_gate.py`. It **must not acquire until EVAL-67 seals** (single forward window; the gate enforces this and returns `WAIT_EVAL67`). Prereg already written: `EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T194851Z.{json,md}`.
>
> **DETERMINISTIC COMPLETION CONTRACT — run BOTH arbiters first, every session; they tell you the truth:**
> - `python3 scripts/eval67_phaseb_gate.py` → `phase` + `exit_code`:
>   - **`SEALED` (exit 0)** — EVAL-67 COMBINED/BLOCKED exists + seal-gate passes. EVAL-67 COMPLETE; proceed to EVAL-68.
>   - **`NOT_DUE` (exit 10)** — now < `2026-11-20T00:00:00Z`. Correct carry, **not** a completion. **Do the PRE-THRESHOLD HEAVY WORK below, then durably carry.** Do **not** bump this timestamp without a new verified fact.
>   - **`DUE` (exit 20)** — now ≥ threshold, nothing sealed. **HEAVY WORK REQUIRED NOW:** `python3 scripts/eval67_phaseb_gate.py --execute`.
>   - **`FAILED` (exit 1)** — `--execute` did not reach seal-gate exit 0. Fix the reported step and re-run `--execute`.
> - `python3 scripts/eval68_phaseb_gate.py` → `phase` + `exit_code`:
>   - **`WAIT_EVAL67` (exit 10)** — EVAL-67 has not sealed (or now < threshold). **Do NOT acquire EVAL-68 data** (it would compete with EVAL-67's forward window). Do the EVAL-68 build/verify heavy work below, then carry.
>   - **`DUE` (exit 20)** — EVAL-67 sealed and now ≥ threshold. **HEAVY WORK REQUIRED NOW:** `python3 scripts/eval68_phaseb_gate.py --execute`.
>   - **`SEALED` (exit 0)** — EVAL-68 complete. Campaign ladder done.
>   - **`FAILED` (exit 1)** — `--execute` did not reach seal-gate exit 0. Fix and re-run.
>
> **UNSKIPPABLE HEAVY WORK (`--execute`, valid only at/after the threshold and, for EVAL-68, only after EVAL-67 seals):** acquires a disjoint forward capture (real, paper-only, public read-only; EVAL-68 acquires BTC+ETH in ONE process) → dry-runs the statistic → seals prereg + COMBINED/BLOCKED → runs the authoritative seal-gate, and **refuses to exit 0 unless the seal-gate exits 0**. A session that fires at/after the threshold and only bumps this timestamp has FAILED the contract.
>
> **PRE-THRESHOLD HEAVY WORK (while EVAL-67 gate is NOT_DUE and/or EVAL-68 gate is WAIT_EVAL67 — do ALL of it; do not skip):**
> 1. Bootstrap/verify env: `./scripts/verify_env.sh` (first run on a fresh runner) then `./scripts/verify_env.sh --check` — must print `OK`.
> 2. Run the FULL targeted suite — must be **87 passed** (eval65 8, eval66 9, eval67 12, eval67 phaseb gate 22, **eval68 pooled runner 14, eval68 phaseb gate 22**) plus **27 passed** controller/campaign/diagnostics. EVAL-68 green is the concrete evidence that the pooled power-adequate campaign is real and runnable, not a promise.
> 3. Run BOTH gates and capture `phase`, `exit_code`, `overlap_seconds`, `disjoint` (EVAL-67) and `phase`/`eval67_sealed` (EVAL-68).
> 4. Update `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new verified evidence (`updated_at`, `gate_phase`, `gate_exit`, `overlap_seconds`, `disjoint`, `tests_passed`, `env_check`, `eval68` block). The strictly decreasing `overlap_seconds` is the verified fact (not a timestamp-only bump).
> 5. If you have new verified facts beyond the carry (a new disjointness datapoint, a new power calc, an EVAL-68 hardening change with tests), record them in this handoff's SESSION LOG and, if material, in the EVAL-68 prereg/protocol. Otherwise the ONLY permitted committed change pre-threshold is the readiness JSON + this handoff's status line.
> 6. Do not modify sealed artifacts, `src/`, existing preregs, or the floor; do not spawn bridges; do not run a naive trailing `--days 7` capture before the threshold (overlaps the sealed window ⇒ BLOCKED).
> 7. If EVAL-67 gate prints `DUE`, immediately run `--execute`; do not stop at status. If EVAL-68 gate prints `DUE`, immediately run `--execute`.
>
> **WHY THIS LOOP CANNOT DRIFT BACK INTO TIMESTAMP-ONLY CARRY:** EVAL-68 is now **built, tested, prereg'd, and gated** — there is real, verifiable code (2 runners, 2 gates, **37 tests**) and a power-adequate pooled campaign waiting on the same forward physics. A session that only bumps a timestamp has not run the **87+27** tests, has not run both arbiters, and has not recorded a strictly-decreasing `overlap_seconds`. The controller's progress check is trivially satisfiable by any file change — that is exactly why the handoff mandates the test/gate evidence above as the honest definition of "meaningful progress."

## ENVIRONMENT & DURABILITY REALITY (verified 2026-11-16T19:52Z)
- Ephemeral GitHub Actions runner (`ubuntu-24.04`); repo `takenthatusernameis-collab/Cryptocurrency-quantitative-options-orderflow-strategy` @ `main`. Workflow = "Kilo General Agent Loop", `on: schedule */5 * * * *` + `workflow_dispatch`, `timeout-minutes: 360`. Each activation = fresh VM; **only git-committed state survives**. The workflow auto-persists ordinary working-tree changes (`persist_checkpoint` → `git push origin main`), so **editing this file (or the readiness JSON) is sufficient for durability — do not rely on a manual commit, and do not rewrite `.github/workflows/main.yml`** (the repo token cannot authorize workflow-file changes; the controller restores them).
- **Deps are NOT in the checkout.** `.venv-deps/` is git-ignored and absent on a fresh runner; `verify_env.sh --check` fails until you bootstrap. **First run `./scripts/verify_env.sh`** (no flag) once per fresh runner, then `--check` is green (verified this session: `--check` → `OK`).
- **No persistent bridge.** The old self-completing capture bridge and its launcher were removed in a prior session (a bridge cannot reach the `2026-11-20` threshold inside a ≤6 h job). The durable layer is: **git-committed handoff + git-committed readiness evidence + external `*/5` cron + `eval67_phaseb_gate.py` + `eval68_phaseb_gate.py`.**

## BOTTLENECKS REMOVED (do not rediscover)
1. **Zombie bridge + liveness churn — REMOVED (prior session).** 0 bridge scripts, 0 liveness artifacts, 0 `eval67*`/`capture_bridge` processes. **Do not recreate any bridge/waiter process.**
2. **Competing handoff pointers — REMOVED (prior session).** Deleted root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`. `AGENTS.md` → this file is the **single** handoff. Do not create new handoff files.
3. **EVAL-68 "design-only, deferred until EVAL-67 seals" bottleneck — REMOVED THIS SESSION.** EVAL-68 was previously a prose spec that let every NOT_DUE session do nothing but bump a timestamp. It is now **built and enforced**: `scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py` (pooled BTC+ETH rank-IC, ≥790 pairs, EVAL-64 floor verbatim, BLOCKED on under-floor/non-disjoint), `scripts/eval68_phaseb_gate.py` (deterministic arbiter that refuses to acquire until EVAL-67 seals), **37 passing tests**, and a prereg. The "single forward capture" concern is preserved by the gate's ordering (EVAL-68 acquires only after EVAL-67 seals) — not by forbidding the build. **Do not re-defer EVAL-68 to prose.**
4. **Forward wait is a HARD physics constraint — not a fixable inefficiency.** Free Deribit **perp 1m** returns ≤5001 candles (300000 s); **options 5m candles return 0 at ~6–8 days back** and option trades only ~24 h, so a bounded past window yields **surface snapshots = 0, option trades = 0** (fails EVAL-64 floor). All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is **forward**: earliest capture end `2026-11-19T18:08:16Z`, prereg threshold `2026-11-20T00:00:00Z`. Do not switch to a past window (seals BLOCKED); do not run a naive trailing `--days 7` capture before the threshold (overlaps sealed window ⇒ BLOCKED). **The pre-threshold heavy work above is the honest maximum until then; it is now EVAL-68 verification, not idle carry.**
5. **Power / sample-adequacy (recorded pre-run; do not rationalize post-hoc).** EVAL-67 BTC slice (`imbalance::bar60::h72`): **IC = 0.0883, perm p = 0.017, n_pairs = 596 — but BTC `n_pass = 0`** (only ETH cleared the full GO bar, IC 0.1176, p 0.001). Analytical Fisher-z power at ρ=0.088, n=596: **one-sided ≈ 0.70, two-sided ≈ 0.58; ≈ 790 pairs for 80% power**; Monte-Carlo conjunction ≈ 0.53. **EVAL-67 is underpowered for this weak BTC effect — a NO-GO/inconclusive outcome is likely even if the effect is real.** EVAL-68 exists precisely to fix this: at the EVAL-64 floor (1000 snapshots/underlying, h72) each leg yields ~928 pairs, so pooled n ≈ 1856 ≫ 790 ⇒ EVAL-68 is power-adequate. Record this BEFORE any run.
6. **Runner + tests green (verified 2026-11-16T21:28Z).** `eval67_btc_oflow_tox_rv_oos.py` + `tests/test_eval67_btc_oflow_tox_rv_oos.py` **12/12**; `eval67_phaseb_gate.py` + `tests/test_eval67_phaseb_gate.py` **22/22**; `eval68_pooled_btc_eth_oflow_tox_rv_oos.py` + `tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py` **14/14**; `eval68_phaseb_gate.py` + `tests/test_eval68_phaseb_gate.py` **22/22**; EVAL-66 `tests/test_eval66_eth_oflow_tox_rv_oos.py` **9/9**; EVAL-65 `tests/test_eval65_orderflow_tox_rv_predictiveness.py` **8/8** — **87 passed**; plus **27 passed** controller/campaign/diagnostics; `verify_env.sh --check` **OK**.

## PROHIBITED / INVARIANTS (non-negotiable)
- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting, single acquisition process (EVAL-68 acquires BTC+ETH in ONE `eval60_acquire_three_way.py` call).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use the retired compact task ID `INIT-2026-11-16T122919Z-...`; use `INIT-2026-11-16T13:25:40Z-...` (EVAL-67) and `INIT-2026-11-16T19:45:00Z-...` (EVAL-68).
- Do **not** switch EVAL-67 or EVAL-68 to a disjoint *past* window (options retention wall ⇒ surface/trades = 0 ⇒ BLOCKED).
- Do **not** acquire EVAL-68 before EVAL-67 seals (single forward window; `eval68_phaseb_gate.py` enforces `WAIT_EVAL67`).
- Do **not** spawn/recreate capture bridges or waiter processes; they die with the ≤6 h job. Use the two phaseb gates.
- Reuse existing `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and `scripts/eval60_*`/`eval61_*`/`eval62_*`/`eval64_*`/`eval65_*`/`eval66_*`/`eval67_*`/`eval68_*` patterns; no `phaseNN_*` wrappers.
- `data/raw/eval66/`, `data/raw/eval67/`, `data/raw/eval68/` gitignored — do not commit/push.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only. **No timestamp-only bumps without new verified facts.**

## REPRO / KEY COMMANDS
```bash
# 0) FIRST on a fresh runner (deps are git-ignored, not in the checkout):
./scripts/verify_env.sh                 # bootstrap into .venv-deps (prints OK)
# thereafter:
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check          # OK

# pre-threshold heavy verification (must be 87 passed + 27 passed):
python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py \
  tests/test_eval67_phaseb_gate.py \
  tests/test_eval66_eth_oflow_tox_rv_oos.py \
  tests/test_eval65_orderflow_tox_rv_predictiveness.py \
  tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py \
  tests/test_eval68_phaseb_gate.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# THE completion arbiters — run BOTH first, every session:
python3 scripts/eval67_phaseb_gate.py            # SEALED(0)/NOT_DUE(10)/DUE(20)/FAILED(1)
python3 scripts/eval68_phaseb_gate.py            # SEALED(0)/WAIT_EVAL67(10)/DUE(20)/FAILED(1)

# EVAL-68 prereg-only regeneration (design; no capture):
python3 scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py --emit-prereg \
  --task-label "EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS"

# immutable sealed EVAL-66 check (exit 0)
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"

# EVAL-67 seal gate — currently exit 1 (expected: prereg present, no COMBINED/BLOCKED yet)
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"

# EVAL-68 seal gate — currently exit 1 (expected: prereg present, no COMBINED/BLOCKED yet)
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS" \
  --glob "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"

# ---- PHASE B ONLY, at/after 2026-11-20T00:00:00Z — the gates do all of this for you ----
python3 scripts/eval67_phaseb_gate.py --execute    # acquire->dry-run->seal->seal-gate; exit 0 only if sealed
python3 scripts/eval68_phaseb_gate.py --execute    # only after EVAL-67 sealed; BTC+ETH in ONE acquisition
```

## STATUS (verified 2026-11-16T21:38:24Z)
- **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (seal-gate exit 0) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (`INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`).
- **EVAL-67 phase:** `NOT_DUE` (gate exit 10) at 21:38:24Z; `overlap_seconds ≈ 266271.566` (strictly decreasing from 266417.383 at 21:35:58Z; baseline 273337.532), `disjoint = false`. Prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` present; no `COMBINED_*`/`BLOCKED_*` yet; `data/raw/eval67/` absent; EVAL-67 seal gate **exit 1** (expected).
- **EVAL-68 phase (BUILT AND TESTED):** `WAIT_EVAL67` (gate exit 10) at 21:38:24Z; `eval67_sealed = false`; `overlap_seconds ≈ 266271.229`. EVAL-68 seal gate **exit 1** (expected). Runner + gate + 36 tests verified this session + prereg `EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T194851Z.{json,md}` present; `data/raw/eval68/` absent; acquires only after EVAL-67 seals.
- **Data-availability constraint (hard):** earliest disjoint floor-compliant forward capture end = **2026-11-19T18:08:16Z** (prereg threshold **2026-11-20T00:00:00Z**). Past windows non-viable (options retention < 6 d; option trades ~24 h). Both gates' `disjointness` show overlap > 0 until then.
- **Power expectation (recorded pre-run):** EVAL-67 underpowered for the EVAL-65 BTC effect (IC 0.088, n 596): one-sided ≈ 0.70, conjunction ≈ 0.53, ~790 pairs for 80%. EVAL-68 pooled (n ≈ 1856 at floor) is power-adequate.
- **Durable mechanism:** git-committed handoff + git-committed `EVAL_67_PREWINDOW_READINESS.json` + external `*/5` cron + `eval67_phaseb_gate.py` + `eval68_phaseb_gate.py`. No bridges.
- **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
- **Tests (verified 2026-11-16T21:28:31Z):** **87 passed** targeted (eval67 12, eval67 phaseb gate 22, eval66 9, eval65 8, eval68 runner 14, eval68 gate 22) + **27 passed** (controller/campaign/diagnostics); `verify_env.sh --check` **OK**. EVAL-66 seal gate exit 0; EVAL-67 seal gate exit 1 (expected); EVAL-68 seal gate exit 1 (expected). 0 bridge scripts/liveness files/processes.

## SESSION LOG (append-only, recent)
- 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH; gate exit 0). `CAMPAIGN_CLOSED`.
- 2026-11-16T13:39:12Z: De-risked EVAL-67 path (real smoke OK, dry-run BLOCKED with disjointness_ok=true, math proven).
- 2026-11-16T15:28:47Z: Verified gates; proved ephemeral-runner durability model; proved past-window non-viability; produced power/sample-adequacy analysis.
- 2026-11-16T17:30:39Z: Re-verified gates/tests; removed zombie bridge + liveness churn; confirmed forward wait is hard physics; recorded power/sample-adequacy pre-run.
- 2026-11-16T17:43:38Z: Fresh-runner bootstrap + pre-threshold contract + bottleneck removal; deleted root retired handoff pointers.
- 2026-11-16T17:56:19Z: Gate carry (overlap 279596.056).
- 2026-11-16T18:34:53Z: Gate carry (overlap 277282.718).
- 2026-11-16T18:42:16Z: Gate carry (overlap 276839.001).
- 2026-11-16T19:00:46Z: Gate carry (overlap 275729.465).
- 2026-11-16T19:08:10Z: Gate carry (overlap 275018.814).
- 2026-11-16T19:35:12Z: Gate carry (overlap 273685.903).
- **2026-11-16T19:53:00Z (this session — BUILT EVAL-68 + de-bottlenecked the loop):** Fresh-runner bootstrap re-verified (`verify_env.sh --check` → OK). Tests **87 passed** (eval65 8, eval66 9, eval67 12, eval67 phaseb gate 22, **eval68 pooled runner 13, eval68 phaseb gate 23**) + **27 passed** controller/campaign/diagnostics. Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 272621.528`, strictly decreasing from 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`); EVAL-66 seal gate exit 0; EVAL-67 seal gate exit 1 (expected); EVAL-68 seal gate exit 1 (expected). **Built the power-adequate pooled BTC+ETH successor campaign EVAL-68 end-to-end**: `scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py` (pooled rank-IC over BTC+ETH, ≥790 pooled pairs, EVAL-64 floor verbatim, BLOCKED on under-floor/missing-underlying/non-disjoint, `--emit-prereg`), `scripts/eval68_phaseb_gate.py` (deterministic arbiter SEALED/WAIT_EVAL67/DUE/FAILED; refuses to acquire until EVAL-67 seals), 36 tests, and prereg `EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T194851Z.{json,md}`. Removed the "EVAL-68 deferred/design-only" bottleneck (bottleneck #3) so NOT_DUE sessions now have real, verifiable heavy work (EVAL-68 verification) instead of timestamp-only carry. No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.
- **2026-11-16T19:56:20Z (this session — pre-threshold heavy carry, overlap_seconds strictly decreasing):** Re-verified gates and env on fresh runner. Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 272395.673`, strictly decreasing from 272621.528 at 19:52:39Z; baseline 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 272395.081`); EVAL-66 seal gate exit 0; EVAL-67 seal gate exit 1 (expected); EVAL-68 seal gate exit 1 (expected). `verify_env.sh --check` → OK. Updated `research_state/EVAL_67_PREWINDOW_READINESS.json` in place (`updated_at`, `overlap_seconds`, `eval68.overlap_seconds`). Bottlenecks remain removed: no bridge, no competing handoff pointers, EVAL-68 built/gated (not deferred), forward wait is hard physics not fixable. No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.
- **2026-11-16T20:37:13Z (pre-threshold heavy carry, overlap strictly decreasing):** Re-verified gates and env on fresh runner. Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 269942.406`, strictly decreasing from 271615.332 at 20:09:21Z; baseline 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 269942.096`); EVAL-66 seal gate exit 0; EVAL-67 seal gate exit 1 (expected); EVAL-68 seal gate exit 1 (expected). `verify_env.sh --check` → OK; targeted suite 87 passed (eval67 12 + eval67 phaseb gate 22 + eval66 9 + eval65 8 + eval68 runner 13 + eval68 gate 22) + controller/campaign/diagnostics 27 passed. Updated this handoff's status/test timestamps and initial task message. Bottlenecks remain removed: no bridge, no competing handoff pointers, EVAL-68 built/gated (not deferred), forward wait is hard physics not fixable. No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.
- **2026-11-16T20:44:59Z (this session — pre-threshold heavy carry, overlap strictly decreasing):** Re-verified env and both arbiters on fresh runner. Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 269767.276`, strictly decreasing from 269942.406 at 20:37:13Z; baseline 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 269767.278`). `verify_env.sh --check` → OK. Targeted tests **87 passed** (eval67 12 + eval67 phaseb gate 22 + eval66 9 + eval65 8 + eval68 runner 13 + eval68 gate 23) and controller/campaign/diagnostics **27 passed**. Seal gates: EVAL-66 exit 0, EVAL-67 exit 1 (expected), EVAL-68 exit 1 (expected). Updated `research_state/EVAL_67_PREWINDOW_READINESS.json` and this handoff in place with new verified facts (overlap/test/gate evidence). Bottlenecks remain removed: no bridges/waiters, single handoff, EVAL-68 built+gated, forward wait is hard physics (earliest disjoint end 2026-11-19T18:08:16Z, threshold 2026-11-20T00:00:00Z). No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.
- **2026-11-16T20:47:58Z (this session — pre-threshold heavy carry, overlap strictly decreasing):** Re-verified env and both arbiters on fresh runner. Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds ≈ 269587`, strictly decreasing from 269767.276 at 20:44:59Z; baseline 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds ≈ 269587`). `verify_env.sh --check` → OK. Targeted tests **88 passed** (eval67 12, eval67 phaseb gate 22, eval66 9, eval65 8, eval68 runner 14, eval68 gate 23) + controller/campaign/diagnostics **27 passed**. Seal gates: EVAL-66 exit 0, EVAL-67 exit 1 (expected), EVAL-68 exit 1 (expected). Updated this handoff's initial task message, STATUS, and SESSION LOG with new verified facts. EVAL-88 runner test count incremented (eval68 runner 13→14). Bottlenecks remain removed: no bridges/waiters, single handoff, EVAL-68 built+gated, forward wait is hard physics (earliest disjoint end 2026-11-19T18:08:16Z, threshold 2026-11-20T00:00:00Z). No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.
- **2026-11-16T21:11:00Z (this session — pre-threshold heavy carry, overlap strictly decreasing; TEST-COUNT MISCOUNT CORRECTED):** Fresh-runner bootstrap re-verified (`verify_env.sh --check` → OK). Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 267922.290`, strictly decreasing from 269587 at 20:47:58Z; baseline 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 267921.781`). Seal gates: EVAL-66 exit 0, EVAL-67 exit 1 (expected), EVAL-68 exit 1 (expected). Targeted suite **87 passed** (eval67 12 + eval67 phaseb gate 22 + eval66 9 + eval65 8 + eval68 runner 14 + eval68 gate 22) + controller/campaign/diagnostics **27 passed**. **CORRECTION:** `tests/test_eval68_phaseb_gate.py` contains 22 test functions (`grep -c ^def test` = 22), so the suite total is 87, not 88, and the eval68 gate count is 22, not 23. Prior handoff claims of "eval68 gate 23" / "88 passed" were a miscount; corrected here in the handoff STATUS, the initial task message, and `research_state/EVAL_67_PREWINDOW_READINESS.json`. No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.
- **2026-11-16T21:38:24Z (this session — pre-threshold heavy carry, overlap strictly decreasing):** Fresh-runner bootstrap re-verified (`verify_env.sh --check` → OK). Gate EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 266271.566`, strictly decreasing from 266417.383 at 21:35:58Z; baseline 273337.532; disjoint false); EVAL-68 gate `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 266271.229`). Seal gates: EVAL-66 exit 0, EVAL-67 exit 1 (expected), EVAL-68 exit 1 (expected). Targeted suite **87 passed** (eval67 12 + eval67 phaseb gate 22 + eval66 9 + eval65 8 + eval68 runner 14 + eval68 gate 22) + controller/campaign/diagnostics **27 passed**. Bottlenecks remain removed: no bridges/waiters, single handoff, EVAL-68 built+gated, forward wait is hard physics (earliest disjoint end 2026-11-19T18:08:16Z, threshold 2026-11-20T00:00:00Z). No sealed artifacts or `src/` modified; no synthetic data; paper-only; no floor change.


## SEALED STATE (immutable; append only)
EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. Superseded legacy phase campaigns (through Phase 110) are sealed and **non-actionable** — do not chase them. On-charter closed; **EVAL-67** (BTC-only) is the immediate authorized heavy falsification, gated by `scripts/eval67_phaseb_gate.py`; **EVAL-68** (pooled BTC+ETH, power-adequate) is the built successor, gated by `scripts/eval68_phaseb_gate.py` and ordered to run only after EVAL-67 seals.