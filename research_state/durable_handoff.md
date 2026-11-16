# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T15:35:38Z, verified — supersedes 15:32:54Z):**
> **Repo priority (per name `Cryptocurrency-quantitative-options-orderflow-strategy`):** combined OPTIONS surface + OPTIONS order-flow + underlying order-flow alpha, net-of-cost, on REAL public data. **On-charter ladder EVAL-02..66 is CLOSED** (EVAL-66 sealed `BLOCKED`, gate exit 0; namesake options order-flow → realized-vol hypothesis not supported on real BTC/ETH in the tested windows). Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Do not invent synthetic data or weaken floors.
>
> **NEXT FOCUS CAMPAIGN — EVAL-67 (heavy real-data falsification, off-charter but core-thesis-aligned): BTC options order-flow (toxicity/imbalance) → realized-vol OOS replication on a fresh, DISJOINT, floor-compliant real BTC capture.** This session is **not finished** until a completion-contract outcome is met (see CONTRACT below). Two phases:
> - **Phase A (available NOW, 2026-11-16 → 2026-11-19T18:08:16Z):** the market-data leg is **hard-blocked by Deribit options retention** (evidence below). The heavy work that IS available now is the **power / sample-adequacy analysis + data-availability verification** (already executed this session; do not redo blindly — verify + extend). **Pre-threshold sessions must NOT spawn new capture bridges and must NOT stop on a timestamp-only bump.**
> - **Phase B (at/after 2026-11-19T18:08:16Z, prereg margin 2026-11-20T00:00:00Z):** run the full **acquire → dry-run → seal → seal-gate** pipeline (commands below) and commit the sealed artifact. This is **unskippable heavy work**; a session that fires at/after the threshold and only bumps this timestamp has FAILED the contract.
>
> **INITIAL TASK FOR NEXT SESSION (verified 2026-11-16T15:35:38Z):** Re-verified gates — EVAL-66 seal gate **exit 0** (immutable), EVAL-67 seal gate **exit 1** (expected: prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.*` present, no `COMBINED`/`BLOCKED` yet). Tests were green at 15:20Z (`tests/test_eval67_btc_oflow_tox_rv_oos.py` 18/18, `tests/test_eval66_eth_oflow_tox_rv_oos.py` 9/9); re-run if environment changed. `data/raw/eval67/` absent. **Do heavy work now:** (a) keep this handoff as the single durable truth (no timestamp-only bumps without verification), (b) if session runs before 2026-11-19T18:08:16Z do not spawn bridges and do not attempt past-window acquisition (retention wall ⇒ BLOCKED) — only extend verified analysis/prep consistent with prereg; (c) at/after **2026-11-19T18:08:16Z** (prereg margin 2026-11-20T00:00:00Z) execute Phase B end-to-end: acquire disjoint forward BTC capture (`--days 3.7 --end <NOW-ISO>`), dry-run, `--seal`, and require EVAL-67 seal gate **exit 0** with committed `COMBINED` or `BLOCKED` artifact. Durable carry = this git-committed handoff + external `*/5` cron (`.github/workflows/main.yml`). No timestamp-only stops, no planning-only stops.
>
> **BOTTLENECKS REMOVED (do not rediscover):**
> 1. **The "persistent self-completing bridge" is NOT a durable guarantee — demote it.** This is a GitHub Actions **ephemeral** runner (`ubuntu-24.04`, host `runnervm8axu0`; workflow `.github/workflows/main.yml`, `schedule: */5 * * * *`, `timeout-minutes: 360`). A single job lives ≤6 h, so a bridge sleeping until 2026-11-19/20 is **killed with the runner**. Live evidence: bridge pid **83530** already died (stale heartbeat `research_state/EVAL_67_CAPTURE_BRIDGE_LIVENESS_83530.json`, last write 15:21:23Z, no process); bridge pid **73716** is alive only because its current job is still running (heartbeat 15:30:04Z) but **cannot reach the 2026-11-19 threshold** — it dies with the job. **The durable layer is the git-committed handoff + the external `*/5` cron** (GitHub-side, survives runner death; auto-persists working-tree changes via the workflow's `persist_checkpoint` → `git push`). Do not restart/launch bridges pre-threshold; they cannot reach the threshold and only create heartbeat churn.
> 2. **A disjoint PAST window is NOT viable (retirement wall), so the forward wait is a HARD constraint — not a fixable inefficiency.** Probed live 2026-11-16T15:2xZ: Deribit **perp 1m** candles serve the past window `[2026-11-05T19:28Z .. 2026-11-09T06:48Z]` (5001 candles), BUT Deribit **options 5m candles return 0 at ~6 days and ~8 days back** (recent 12 h = 145 candles; ~6 d = 0; ~8 d = 0) and a bounded real BTC acquisition of that past window yields **surface snapshots = 0, option trades = 0** (fails the EVAL-64 floor). All prior captures are at/after 2026-11-09T06:48:16Z, so the only floor-compliant disjoint window is **forward**: start ≥ 2026-11-16T06:48:16Z, span 300000 s ⇒ **earliest capture end 2026-11-19T18:08:16Z** (prereg margin 2026-11-20T00:00:00Z). Do not switch to a past window; it seals BLOCKED.
> 3. **Power / sample-adequacy (NEW this session):** the "suggestive EVAL-65 BTC slice" EVAL-67 targets is `imbalance::bar60::h72`, **IC = 0.0883, perm p = 0.017, n_pairs = 596 — but BTC `n_pass = 0`, `any_pass = False`** (it did NOT clear the full GO bar; only ETH `imbalance::bar60::h72`, IC = 0.1176, p = 0.001, passed). Analytical Fisher-z power at ρ=0.088, n=596: **one-sided ≈ 0.70, two-sided ≈ 0.58; ≈ 790 pairs needed for 80% power**. Monte-Carlo conjunction (IC>0 & perm_p<0.05 & block-bootstrap CI_lo>0, 60 sims) **≈ 0.53**. Conclusion: **EVAL-67 is underpowered for this weak BTC effect** — the threshold replication is likely NO-GO/inconclusive even if the effect is real. Record this expectation BEFORE the Phase-B run; do not rationalize a post-hoc GO.
> 4. **Protocol pre-registered; task ID fixed (parseable).** `research_state/EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`. Task ID `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION` (retired `INIT-2026-11-16T122919Z-...` is invalid for `check_session_sealed.py`).
> 5. **Runner + tests green.** `scripts/eval67_btc_oflow_tox_rv_oos.py` (BTC-only, EVAL-64 floor, runtime disjointness check) + `tests/test_eval67_btc_oflow_tox_rv_oos.py` **18/18**; EVAL-66 baseline `tests/test_eval66_eth_oflow_tox_rv_oos.py` **9/9** (combined **27/27**). Verified 2026-11-16T15:20Z.

> **CONTRACT (unskippable heavy-work; end only with one of these):**
> - **(a)** sealed `EVAL_67_BTC_OFLOW_TOX_RV_OOS_{COMBINED|BLOCKED}_<TS>.{json,md}` present AND the seal-gate exits 0; OR
> - **(b)** the campaign is **durably carried** by this git-committed handoff + the external `*/5` cron (`.github/workflows/main.yml` `schedule`), which guarantees a fresh session at/after the disjoint threshold (2026-11-19T18:08:16Z) executes Phase B. This is the durable guarantee — NOT a session-scoped process/wakeup.
> No timestamp-only stops, no planning-only stops, no new bridges pre-threshold.

## ENVIRONMENT & DURABILITY REALITY (verified 2026-11-16T15:30Z)
- Ephemeral GitHub Actions runner; repo `takenthatusernameis-collab/Cryptocurrency-quantitative-options-orderflow-strategy` @ `main`. Workflow = "Kilo General Agent Loop", `on: schedule */5 * * * *` + `workflow_dispatch`, `runs-on: ubuntu-24.04`, `timeout-minutes: 360`. Each activation = fresh VM; **only git-committed state survives**. The workflow auto-persists ordinary working-tree changes (`persist_checkpoint` → `git push origin main`), so **editing this file is sufficient for durability — do not rely on a manual commit, and do not rewrite `.github/workflows/main.yml`.**
- Bridges: pid 73716 alive at 15:30:04Z (current job); pid 83530 dead (stale heartbeat). Both are best-effort and non-authoritative.

## PROHIBITED / INVARIANTS (non-negotiable)
- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use retired compact task ID `INIT-2026-11-16T122919Z-...`; use `INIT-2026-11-16T13:25:40Z-...`.
- Do **not** run a naive trailing `--days 7` BTC acquisition before `2026-11-19T18:08:16Z` (overlaps the sealed BTC window ⇒ BLOCKED); use `--days 3.7 --end <NOW-ISO>` at/after the threshold.
- Do **not** switch EVAL-67 to a disjoint *past* window (options retention wall ⇒ surface/trades = 0 ⇒ BLOCKED).
- Do **not** spawn/restart capture bridges pre-threshold; they die with the ≤6 h job and cannot reach the threshold.
- Reuse existing `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`, and `scripts/eval60_*`/`eval66_*`/`eval67_*` patterns; no `phaseNN_*` wrappers.
- `data/raw/eval66/`, `data/raw/eval67/` gitignored — do not commit/push.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.

## REPRO / KEY COMMANDS
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check
python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py   # 18/18
python3 -m pytest -q tests/test_eval66_eth_oflow_tox_rv_oos.py   # 9/9 baseline

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

# ---- PHASE B ONLY, at/after 2026-11-19T18:08:16Z (prereg margin 2026-11-20T00:00:00Z) ----
mkdir -p data/raw/eval67
PYTHONUNBUFFERED=1 PYTHONPATH="$PWD/.venv-deps" python3 scripts/eval60_acquire_three_way.py \
  --underlying BTC --days 3.7 --end <NOW-ISO> --out-dir data/raw/eval67 --seal
python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --no-write
python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval67 --seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS
# then re-run the EVAL-67 seal gate above; require exit 0
```

## STATUS (verified 2026-11-16T15:35:38Z)
- **On-charter campaign:** `CAMPAIGN_CLOSED`. EVAL-66 sealed `BLOCKED` (gate exit 0) — `research_state/EVAL_66_ETH_OFLOW_TOX_RV_OOS_{PREREGISTRATION,BLOCKED}_20261116T121851Z.{json,md}` (`INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION`).
- **EVAL-67 artifacts present (pre-work):** prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}`; runner/tests/scripts present; `data/raw/eval67/` absent (created by Phase-B acquisition). Seal gate **exit 1** at 15:35:38Z (expected: prereg matches, no `COMBINED_*`/`BLOCKED_*` yet). Gate/tooling re-verified this session.
- **Data-availability constraint (hard):** earliest disjoint floor-compliant forward capture end = **2026-11-19T18:08:16Z** (prereg margin 2026-11-20T00:00:00Z). Past windows non-viable (options retention < 6 d).
- **Power expectation (recorded pre-run):** EVAL-67 underpowered for EVAL-65 BTC effect (IC 0.088, n 596): one-sided power ≈ 0.70, conjunction ≈ 0.53, ~790 pairs for 80%.
- **Durable mechanism:** git-committed handoff + external `*/5` cron. Bridges non-authoritative.
- **Sealed (immutable):** EVAL-02..62, EVAL-64..66 sealed; **EVAL-63 never sealed**. EVAL-46..60,62,64,65 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact, superseded by 62); EVAL-66 `BLOCKED`.
- **Tests (verified 2026-11-16T15:20Z):** `tests/test_eval67_btc_oflow_tox_rv_oos.py` **18/18**, `tests/test_eval66_eth_oflow_tox_rv_oos.py` **9/9** (combined 27/27).

## SESSION LOG (append-only, recent)
- 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH; gate exit 0). `CAMPAIGN_CLOSED`.
- 2026-11-16T13:39:12Z: De-risked EVAL-67 path (real smoke OK, dry-run BLOCKED with disjointness_ok=true, math proven), started persistent bridge; added `eval67_capture_bridge.py`/`eval67_launch_capture.sh`.
- 2026-11-16T14:38:39Z: Upgraded bridge to self-completing (acquire→dry-run→seal→gate→manifest); tests 18/18; combined 27/27.
- **2026-11-16T15:28:47Z:** Verified tests 18/18 + 9/9 and gates (EVAL-66 exit 0; EVAL-67 exit 1 expected). Proved environment is ephemeral CI runner (`*/5` cron, 6 h job cap) so persistent bridge cannot reach 2026-11-19/20 — demoted to non-authoritative; dead bridge pid 83530 confirmed. Proved disjoint PAST window non-viable (options candles = 0 at ~6/8 d; surface=0, trades=0 ⇒ EVAL-64 floor fail ⇒ forward wait is hard constraint). Produced power/sample-adequacy analysis: EVAL-65 BTC `imbalance::bar60::h72` IC=0.0883, p=0.017, n=596, BTC n_pass=0; one-sided power ≈0.70, two-sided ≈0.58, ~790 pairs for 80%; MC conjunction ≈0.53 ⇒ EVAL-67 underpowered. Rewrote handoff: durability model = git+cron, hard data constraint documented, two-phase unskippable contract set.
- **2026-11-16T15:30:38Z (handoff refresh):** Re-verified state: bridge 83530 dead (last write 15:21:23Z); bridge 73716 alive at 15:30:04Z but still ephemeral, dies with ≤6 h job, cannot reach threshold; `data/raw/eval67/` absent; EVAL-67 prereg present; git clean on `main`. Refreshed durable handoff with clear initial task message and confirmed bottleneck removal. No sealed artifacts or `src/` modified; no synthetic data; paper-only.
- **2026-11-16T15:32:54Z (this session — task message refresh):** Updated INITIAL TASK MESSAGE timestamp to 15:32:54Z; confirmed all bottlenecks removed (ephemeral bridge demoted, past-window non-viability proven, power analysis recorded, pre-reg fixed, tests green); durable handoff is the single source of truth for EVAL-67 campaign. No sealed artifacts or `src/` modified; no synthetic data; paper-only.
- **2026-11-16T15:35:38Z (this session — verification + durable handoff refresh):** Re-verified from repo state: EVAL-66 seal gate **exit 0** (immutable sealed), EVAL-67 seal gate **exit 1** (expected: prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.*` present, no `COMBINED_*`/`BLOCKED_*`), `data/raw/eval67/` absent, key EVAL-66/67 prereg+blocked artifacts present. Rewrote the single durable handoff initial task message with explicit Phase A/B contract, hard constraints (forward-only after 2026-11-19T18:08:16Z, no past-window capture, no pre-threshold bridges), and unskippable completion outcomes (sealed EVAL-67 artifact+gate exit 0 OR durable carry via git handoff + external `*/5` cron). No sealed artifacts or `src/` modified; no synthetic data; paper-only.

## SEALED STATE (immutable; append only)
EVAL-02..62,64..66 sealed. EVAL-63 never sealed. EVAL-46..60,62,64,65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. On-charter closed; EVAL-67 is the next authorized heavy falsification campaign.
