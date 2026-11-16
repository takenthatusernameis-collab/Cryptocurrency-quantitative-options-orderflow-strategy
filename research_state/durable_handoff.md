# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T15:48:49Z — verified this session):**
> **Repo-priority reading of `Cryptocurrency-quantitative-options-orderflow-strategy`:** the thesis is *crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. **On-charter ladder EVAL-02..66 is CLOSED** (EVAL-66 sealed `BLOCKED`, seal-gate exit 0; the namesake options order-flow → realized-vol hypothesis is not supported on real BTC/ETH in the tested windows). Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Never synthetic data, never weaken the EVAL-64 floor, paper-only.
>
> **NEXT FOCUS CAMPAIGN — EVAL-67 (heavy, real-data, off-charter but core-thesis-aligned):** BTC options order-flow toxicity/imbalance → forward realized-vol OOS replication on a fresh, DISJOINT, floor-compliant real BTC capture. Task ID `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`; prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`.
>
> **DETERMINISTIC COMPLETION CONTRACT — run ONE command, it tells you the truth:**
> `python3 scripts/eval67_phaseb_gate.py` (status) → prints `phase` + `exit_code`:
> - **`SEALED` (exit 0)** — a `COMBINED_*`/`BLOCKED_*` EVAL-67 artifact exists and the seal-gate passes. Campaign COMPLETE. Idempotent no-op; do nothing else.
> - **`NOT_DUE` (exit 10)** — now < `2026-11-20T00:00:00Z`, nothing sealed yet. This is the CORRECT CARRY state, **not** a completion and **not** a timestamp-only stop. It prints the verified disjointness math (a capture now overlaps the sealed BTC window ⇒ BLOCKED) and readiness evidence. **Durably carry** via this git-committed handoff + the external `*/5` cron (`.github/workflows/main.yml`). Do **not** bump this timestamp without new verified facts; do **not** spawn a bridge (bridges die with the ≤6 h job and were removed — see bottlenecks).
> - **`DUE` (exit 20)** — now ≥ threshold and nothing sealed. **HEAVY WORK IS REQUIRED NOW.** Re-run: `python3 scripts/eval67_phaseb_gate.py --execute`.
> - **`FAILED` (exit 1)** — `--execute` ran but the acquire→dry-run→seal→seal-gate pipeline did not reach seal-gate exit 0. Fix the reported step and re-run `--execute`.
>
> **UNSKIPPABLE HEAVY WORK (`--execute`, valid only at/after the threshold):** acquires a disjoint forward BTC three-way capture (real, paper-only, public read-only) → dry-runs the EVAL-67 statistic → seals prereg + COMBINED/BLOCKED → runs the authoritative seal-gate, and **refuses to exit 0 unless the seal-gate exits 0**. This is the single path to a sealed EVAL-67 artifact. A session that fires at/after the threshold and only bumps this timestamp has FAILED the contract.

## ENVIRONMENT & DURABILITY REALITY (verified 2026-11-16T15:48Z)
- Ephemeral GitHub Actions runner (`ubuntu-24.04`, host `runnervm8axu0`); repo `takenthatusernameis-collab/Cryptocurrency-quantitative-options-orderflow-strategy` @ `main`. Workflow = "Kilo General Agent Loop", `on: schedule */5 * * * *` + `workflow_dispatch`, `timeout-minutes: 360`. Each activation = fresh VM; **only git-committed state survives**. The workflow auto-persists ordinary working-tree changes (`persist_checkpoint` → `git push origin main`), so **editing this file is sufficient for durability — do not rely on a manual commit, and do not rewrite `.github/workflows/main.yml`.**
- **No persistent bridge.** The old self-completing capture bridge and its launcher were **removed this session** because a bridge cannot reach the `2026-11-20` threshold inside a ≤6 h job and only created liveness-file churn (5 zombie/stale bridge heartbeats were cleaned up). The durable layer is: **git-committed handoff + external `*/5` cron + `scripts/eval67_phaseb_gate.py`.**

## BOTTLENECKS REMOVED (do not rediscover)
1. **Zombie bridge + liveness churn — REMOVED.** Killed the live bridge (pid 73716) and deleted `scripts/eval67_capture_bridge.py`, `scripts/eval67_launch_capture.sh`, and all `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_*.json`. The Phase-B gate (`eval67_phaseb_gate.py`) is the deterministic, idempotent replacement. **Do not recreate any bridge/waiter process.**
2. **Forward wait is a HARD physics constraint — not a fixable inefficiency.** Free Deribit **perp 1m** returns ≤5001 candles (300000 s); **options 5m candles return 0 at ~6–8 days back** (verified: recent 12 h = 145 candles, ~6 d = 0, ~8 d = 0) and a bounded past-window acquisition yields **surface snapshots = 0, option trades = 0** (fails EVAL-64 floor). All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is **forward**: earliest capture end `2026-11-19T18:08:16Z`, prereg threshold `2026-11-20T00:00:00Z`. Do not switch to a past window (seals BLOCKED); do not run a naive trailing `--days 7` capture before the threshold (overlaps sealed window ⇒ BLOCKED).
3. **Power / sample-adequacy (recorded pre-run; do not rationalize post-hoc).** The EVAL-65 BTC slice EVAL-67 targets is `imbalance::bar60::h72`, **IC = 0.0883, perm p = 0.017, n_pairs = 596 — but BTC `n_pass = 0`, `any_pass = False`** (only ETH `imbalance::bar60::h72`, IC = 0.1176, p = 0.001, cleared the full GO bar). Analytical Fisher-z power at ρ=0.088, n=596: **one-sided ≈ 0.70, two-sided ≈ 0.58; ≈ 790 pairs needed for 80% power**; Monte-Carlo conjunction (IC>0 & perm_p<0.05 & block-bootstrap CI_lo>0, 60 sims) **≈ 0.53**. Expectation: **EVAL-67 is underpowered for this weak BTC effect — a NO-GO/inconclusive outcome is likely even if the effect is real.** Record this BEFORE the Phase-B run.
4. **Runner + tests green (verified 2026-11-16T15:48Z).** `scripts/eval67_btc_oflow_tox_rv_oos.py` (BTC-only, EVAL-64 floor, runtime disjointness check) + `tests/test_eval67_btc_oflow_tox_rv_oos.py` **12/12**; new `scripts/eval67_phaseb_gate.py` + `tests/test_eval67_phaseb_gate.py` **22/22**; EVAL-66 baseline `tests/test_eval66_eth_oflow_tox_rv_oos.py` **9/9**; EVAL-65 `tests/test_eval65_orderflow_tox_rv_predictiveness.py` **8/8**; `verify_env.sh --check` **OK**. Re-run if the environment changed.

## PROHIBITED / INVARIANTS (non-negotiable)
- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting, single acquisition process.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use retired compact task ID `INIT-2026-11-16T122919Z-...`; use `INIT-2026-11-16T13:25:40Z-...`.
- Do **not** switch EVAL-67 to a disjoint *past* window (options retention wall ⇒ surface/trades = 0 ⇒ BLOCKED).
- Do **not** spawn/recreate capture bridges or waiter processes; they die with the ≤6 h job. Use `eval67_phaseb_gate.py`.
- Reuse existing `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and `scripts/eval60_*`/`eval66_*`/`eval67_*` patterns; no `phaseNN_*` wrappers.
- `data/raw/eval66/`, `data/raw/eval67/` gitignored — do not commit/push.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only. **No timestamp-only bumps without new verified facts.**

## REPRO / KEY COMMANDS
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check
python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py    # 12/12
python3 -m pytest -q tests/test_eval67_phaseb_gate.py             # 22/22
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py    # 9/9 baseline

# THE completion arbiter — run this first, every session:
python3 scripts/eval67_phaseb_gate.py            # status: SEALED(0)/NOT_DUE(10)/DUE(20)

# immutable sealed EVAL-66 check (should be exit 0)
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

# ---- PHASE B ONLY, at/after 2026-11-20T00:00:00Z — the gate does all of this for you ----
python3 scripts/eval67_phaseb_gate.py --execute    # acquire->dry-run->seal->seal-gate; exit 0 only if sealed
```

## STATUS (verified 2026-11-16T15:48:49Z)
- **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (seal-gate exit 0) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (`INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`).
- **EVAL-67 phase:** `NOT_DUE` (gate exit 10) at 15:48:49Z. Prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` present; no `COMBINED_*`/`BLOCKED_*` yet; `data/raw/eval67/` absent; EVAL-67 seal gate **exit 1** (expected). Gate/tooling re-verified this session.
- **Data-availability constraint (hard):** earliest disjoint floor-compliant forward capture end = **2026-11-19T18:08:16Z** (prereg threshold **2026-11-20T00:00:00Z**). Past windows non-viable (options retention < 6 d). The gate's `disjointness` block shows overlap > 0 until then.
- **Power expectation (recorded pre-run):** EVAL-67 underpowered for the EVAL-65 BTC effect (IC 0.088, n 596): one-sided power ≈ 0.70, conjunction ≈ 0.53, ~790 pairs for 80%.
- **Durable mechanism:** git-committed handoff + external `*/5` cron + `eval67_phaseb_gate.py`. No bridges.
- **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
- **Tests (verified 2026-11-16T15:48Z):** eval67 **12/12**, phaseb gate **22/22**, eval66 **9/9**, eval65 **8/8**, `verify_env` **OK**.

## SESSION LOG (append-only, recent)
- 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH; gate exit 0). `CAMPAIGN_CLOSED`.
- 2026-11-16T13:39:12Z: De-risked EVAL-67 path (real smoke OK, dry-run BLOCKED with disjointness_ok=true, math proven).
- 2026-11-16T15:28:47Z: Verified gates; proved ephemeral-runner durability model; proved past-window non-viability; produced power/sample-adequacy analysis.
- **2026-11-16T15:48:49Z (this session — bottleneck removal + deterministic gate):** Re-verified gates (EVAL-66 exit 0; EVAL-67 exit 1 expected), tests (eval67 12/12 after bridge removal, phaseb gate 22/22, eval66 9/9, eval65 8/8), env OK. **Removed the churn vector:** killed the live zombie bridge (pid 73716), deleted `scripts/eval67_capture_bridge.py` + `scripts/eval67_launch_capture.sh`, deleted all `EVAL_67_CAPTURE_BRIDGE_LIVENESS_*.json` (5 stale/live heartbeats), and removed the bridge unit tests. **Added `scripts/eval67_phaseb_gate.py` + `tests/test_eval67_phaseb_gate.py`:** a deterministic, idempotent completion arbiter (SEALED 0 / NOT_DUE 10 / DUE 20 / FAILED 1) whose `--execute` performs acquire→dry-run→seal→seal-gate and refuses to exit 0 unless the seal-gate passes — so heavy work is unskippable and no session can stop on a timestamp-only bump. Rewrote this handoff with a timestamped, repo-prioritized initial task message and the gate as the single completion contract. No sealed artifacts or `src/` modified; no synthetic data; paper-only.

## SEALED STATE (immutable; append only)
EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. On-charter closed; EVAL-67 is the next authorized heavy falsification campaign, gated by `scripts/eval67_phaseb_gate.py`.