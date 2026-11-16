# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T08:25:00Z, verified):** Execute **`INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`** end-to-end now. The repo's namesake rung (real options order-flow toxicity → subsequent realized volatility) has now been **closed in traded form** (EVAL-62 and EVAL-64 both sealed `NO-GO CONFIRMED (PASS)` on real data). The one remaining decisive question is *informational*, not traded: **does the options order-flow toxicity signal predict subsequent realized volatility at all, independent of any wrapper?** EVAL-65 answers it (wrapper-free Spearman rank-IC). **Its tooling is already built, tested (8/8 pass), and dry-run-verified on the real 7d captures — the ONLY remaining step is to seal it.** Do NOT stop at handoff edits, env checks, or re-deriving the campaign. Do NOT produce a timestamp-only checkpoint. This session must produce a sealed EVAL-65 `COMBINED` (or honest `BLOCKED`) via the gate below (**exit 0 required**). Required path: (1) `./scripts/verify_env.sh --check` + `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`, confirm `.env` absent / `LIVE_TRADING_ENABLED` unset (paper-only); (2) optionally re-verify the sealed EVAL-64 gate (exit 0); (3) run `python3 scripts/eval65_orderflow_tox_rv_predictiveness.py --capture-dir data/raw/eval63 --seal --task-label EVAL65-OFLOW-TOX-RV-PREDICTIVENESS` (real 7d captures already on disk; **no acquisition, no network, no synthetic data**); (4) seal gate: `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL" --glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" --require-glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*"` (**exit 0 required**); (5) update this handoff in place with verified paths/numbers and the next concrete rung. **Verified dry-run expectation (deterministic, seed 42): floor_ok=true; verdict `NO-GO CONFIRMED (PASS)` — BTC 0 passing configs (best IC 0.0883), ETH 2 passing configs (tox & imbalance ::bar60::h72, best IC 0.1176; BH-FDR rejects those 2 ETH configs); the signal does NOT predict vol on both assets.** Report exactly what the seal emits; do not fabricate. **No synthetic data, no floor weakening, no sealed-artifact edits. A handoff-only session that does not seal EVAL-65 is a FAILURE — the data (`data/raw/eval63`, ~360 MB) and tested tooling are present, so there is no acquisition/tooling excuse.**

## STATUS (verified 2026-11-16T08:25:00Z)

- **EVAL-64 (feasible-floor traded form) is SEALED `NO-GO CONFIRMED (PASS)`** on the real 7d BTC+ETH captures (this session).
  - Task: `INIT-2026-11-16T07:59:00Z-EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH`
  - Prereg: `research_state/EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_PREREGISTRATION_20261116T082210Z.{json,md}`
  - Combined: `research_state/EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_COMBINED_20261116T082210Z.{json,md}`
  - Seal gate exit 0. Captures (real, 7d): `data/raw/eval63/three_way_BTC_20261116T064816Z.json`, `data/raw/eval63/three_way_ETH_20261116T064816Z.json`.
  - Measured (floor_ok=true, all checks true for both underlyings): BTC best `imbalance::bar60.0` Sharpe **−0.5837** (any_pass=false); ETH best `imbalance::bar300.0` Sharpe **−0.0954** (any_pass=false); pooled PBO **0.375**; BH-FDR rejected `BTC::imbalance::bar300.0`.
  - **Conclusion (traded form closed):** real options order-flow toxicity → signal-timed delta-hedged ATM straddle (correct mark-path net-of-cost P&L) is **not net-of-cost tradable** on the heaviest achievable real 7d sample. The namesake traded rung is honestly closed.
- **EVAL-63 was NEVER actually sealed — correction.** The prior handoff claimed `EVAL_63_..._BLOCKED_20261116T075900Z`, but **no `EVAL_63_*` artifact exists** anywhere (working tree or git). The strict EVAL-63 ≥7d perp floor (perp span ≥600000 s, ≥1500 surface 5m bars, ≥4000 option trades) is **physically unreachable** from the free public API (measured: Deribit `{BTC,ETH}-PERPETUAL` 1m candles cap at 300000 s / 5001 candles / 1000 5m bars; surface 5m candles DO scale to 7d; Deribit tick-trade retention ≈24h). EVAL-64 supersedes EVAL-63 on the feasible floor. **Do not claim EVAL-63 sealed; it is not.**
- **EVAL-65 tooling is BUILT, TESTED (8/8), and DRY-RUN-VERIFIED but NOT sealed** (next session's heavy task).
  - Script: `scripts/eval65_orderflow_tox_rv_predictiveness.py`; tests: `tests/test_eval65_orderflow_tox_rv_predictiveness.py` (8 passed).
  - Reuses sealed `e62.build_states` (identical causal toxicity signal + spot series) and sealed `e64` feasible floor verbatim; adds a wrapper-free Spearman rank-IC between signal at bar k and forward realized vol over the next H bars.
  - Verified `--no-write` on real 7d captures: floor_ok=true, verdict `NO-GO CONFIRMED (PASS)` (BTC 0 pass; ETH 2 pass at bar60/h72; PBO-style BH-FDR rejects 2 ETH configs). Deterministic (seed 42).
- **Persistence recovered (this session):** session 58's checkpoint commit `d98a38942` could not push — GitHub's pre-receive hook rejected two real 7d captures (`data/raw/eval63/three_way_{BTC,ETH}_20261116T064816Z.json`, ~170 MB each) exceeding the 100 MB per-file limit. Root cause confirmed (oversized real captures, not transient network). Remedy: preserved `d98a38942` in backup branch `recovery/session-58-checkpoint-d98a38942` (recovery bundle; reflog retained; `gc.auto=0`), rewound `main` to `origin/main` without touching the working tree, committed the pushable subset (EVAL-64 seal artifacts, EVAL-65 tooling/tests, handoff, `.gitignore` ignoring `data/raw/eval63/`), and pushed. Remote-tracking `origin/main` now == local `main` == `4f26fb5859dacbde5632a761ac8537044805cc75` — persistence claimed. The two captures remain on local disk for EVAL-65; gitignored, must not be re-committed. Rollback plan: `git reset --hard recovery/session-58-checkpoint-d98a38942` restores the exact session-58 checkpoint.
- **Bottleneck removed (data ceiling + tooling bugs + process loop):**
  - Data ceiling documented: the strict ≥7d perp floor is unachievable; the feasible floor (EVAL-64) is the honest ceiling and is met on existing captures.
  - Copy-and-retarget bugs fixed in the UNSEALED EVAL-64 (EVAL-62/63 untouched): (a) `e62.build_prereg_md` raised `KeyError: 'min_bars_per_underlying'` on the EVAL-64 split floor schema → added a local `build_prereg_md` rendering the EVAL-64 floor; (b) the EVAL-64 test file was a stale copy of the EVAL-63 test (imported `eval63`, asserted `EVAL_63_*`) → retargeted to `eval64` / `EVAL_64_*`. Spurious partial artifacts from the first failed seal attempt (`..._BLOCKED_20261116T082044Z`, incomplete prereg `.json`) were removed; the sealed EVAL-64 verdict is the single `COMBINED` NO-GO.
  - Process loop removed: ~12 prior sessions only bumped handoff timestamps. This session performed real heavy work (sealed EVAL-64, built+tested EVAL-65) instead of re-verifying the handoff. That anti-pattern is prohibited going forward.
- Env (expected at session start): run `./scripts/verify_env.sh --check` and export `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `.env` must be absent; `LIVE_TRADING_ENABLED` unset.

## AUTHORITATIVE NEXT TASK (timestamped, heavy — execute in full)

**Task ID:** `INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`

**Objective (on-charter, namesake information-content, NOT a re-litigation of sealed EVAL-62/64):** Determine whether the real options order-flow toxicity signal has *any* monotone predictive relationship with subsequent realized volatility on the BTC/ETH perpetual, **decoupled from any trading wrapper** (the decisive follow-up to the traded-form NO-GO). This is a Spearman rank-IC falsification on the **already-acquired real 7d captures**; tooling is built/tested/dry-run-verified; the only remaining work is to **seal** it.

**Step 1 — Env/bootstrap (must pass):**
```bash
./scripts/verify_env.sh --check
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
Confirm `.env` absent and `LIVE_TRADING_ENABLED` unset. Paper-only.

**Step 2 — (optional) re-verify the sealed EVAL-64 gate (immutable):**
```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T07:59:00Z-EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH" \
  --glob "EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_PREREGISTRATION_*" \
  --require-glob "EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_COMBINED_*"
```

**Step 3 — Seal EVAL-65 (heavy: full 7d capture load + 24-config rank-IC + permutation + block bootstrap + BH-FDR; real captures already on disk; no acquisition):**
```bash
python3 scripts/eval65_orderflow_tox_rv_predictiveness.py \
  --capture-dir data/raw/eval63 --seal \
  --task-label EVAL65-OFLOW-TOX-RV-PREDICTIVENESS
```

**Step 4 — Seal gate (exit 0 required):**
```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL" \
  --glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*"
```
GO bar (pre-registered, identical in spirit to EVAL-62/64): GO only if on **both** BTC and ETH and ≥1 config the Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else `NO-GO CONFIRMED (PASS)`. **Under-floor real data ⇒ `BLOCKED`, never `NO-GO`.** No synthetic data, no floor weakening, no sealed-artifact edits, no EVAL-62/64 re-runs.

**Expected (verified deterministic dry-run, seed 42):** floor_ok=true; `NO-GO CONFIRMED (PASS)` — BTC 0 passing configs (best IC 0.0883), ETH 2 passing configs (tox & imbalance ::bar60::h72, best IC 0.1176; BH-FDR rejects those 2 ETH configs). The signal does **not** predict vol on both assets. Report exactly what the seal emits.

**Step 5 — After sealing:** update this handoff in place with verified paths/numbers and define the next rung. **Recommended next rung (EVAL-66), only after EVAL-65 is sealed:** since the namesake signal is non-predictive on real BTC+ETH, the honest closure is to (a) attempt the *single* remaining predictive slice that showed signal (ETH 1m/6h horizon) as a **pre-registered, isolated out-of-sample replication on a disjoint real window** (fresh acquisition, `scripts/eval60_acquire_three_way.py --underlying ETH --days 7 --out-dir data/raw/eval66 --seal`, then copy-and-retarget EVAL-65 with the ETH-only `tox`/`imbalance` bar60 h72 config and the EVAL-64 feasible floor) — if it fails to replicate, the namesake is definitively closed; or (b) formally close the campaign (`CAMPAIGN_CLOSED`) if no further on-charter rung is justified. Do not invent synthetic or off-charter rungs.

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check

# (sealed, immutable) re-verify EVAL-64
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T07:59:00Z-EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH" \
  --glob "EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_PREREGISTRATION_*" \
  --require-glob "EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_COMBINED_*"
python3 -m json.tool research_state/EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_COMBINED_20261116T082210Z.json | head -120

# --- EVAL-65 (authoritative next, heavy; do NOT run as discovery, run to seal) ---
# tooling already built/tested; real 7d captures already on disk (data/raw/eval63)
python3 -m pytest -q tests/test_eval65_orderflow_tox_rv_predictiveness.py   # 8 passed
python3 scripts/eval65_orderflow_tox_rv_predictiveness.py --capture-dir data/raw/eval63 --no-write   # dry-run (no seal)
python3 scripts/eval65_orderflow_tox_rv_predictiveness.py --capture-dir data/raw/eval63 --seal \
  --task-label EVAL65-OFLOW-TOX-RV-PREDICTIVENESS
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL" \
  --glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-glob "EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*"
```

## BOTTLENECKS

- **Cleared:** EVAL-64 sealed (gate exit 0) on real 7d data → the namesake traded rung is honestly closed. The strict ≥7d perp floor is documented as physically unreachable; the feasible floor (EVAL-64) is met on the existing captures. EVAL-65 tooling built + tested + dry-run-verified; **no acquisition or tooling blocker remains** for EVAL-65 — only the seal + gate.
- **Cleared (process):** the timestamp-only handoff-edit loop (~12 sessions) is prohibited. A session that does not produce a sealed artifact for its task-id is a failure.
- **Current operational risk:** none for EVAL-65 (data + tooling present, deterministic). For any *future* fresh acquisition (e.g. EVAL-66 ETH-only), Deribit public endpoints may rate-limit; acquire exactly ONE process, dedupe captures, and record span/hashes honestly. Do **not** weaken a pre-registered floor, do **not** stitch synthetic data, and do **not** seal NO-GO on under-floor data (seal `BLOCKED`).

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..62 or EVAL-64; do not edit sealed artifacts or `src/`. EVAL-65 must be sealed once (append-only); do not edit its artifacts after sealing.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies (root retired pointers stay retired). Update this file in place with verified facts only.
- Any P&L must be spot-normalized and use mark-path/realized costed returns (regression-guard pattern as in EVAL-62); never reintroduce the EVAL-61 dollar-as-return artifact.
- Do not weaken a pre-registered floor to force a verdict. Under-floor real data ⇒ `BLOCKED`, not `NO-GO`.

## SEALED STATE (immutable; append only)

EVAL-02..62 sealed. EVAL-46..60, EVAL-62, **EVAL-64**: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). **EVAL-63: NEVER sealed (no artifact exists); superseded by EVAL-64.** Re-running/re-sealing prohibited.

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed NO-GO (gate exit 0).
- 2026-11-16T02:41:37Z: EVAL-61 sealed NO-GO (gate exit 0) — later found to be a P&L artifact.
- 2026-11-16T03:17:05Z: EVAL-62 tooling/tests built; real `--no-write` verified (artifact gone, NO-GO on merits).
- 2026-11-16T03:21:05Z: Sealed EVAL-62 `NO-GO CONFIRMED (PASS)` (floor_ok, overall_pbo 0.375, BTC −0.0443 / ETH +0.6163). Seal gate exit 0. Namesake rung honestly closed on ~1d capture.
- 2026-11-16T03:29:23Z: Fresh `--days 1` BTC+ETH acquisition sealed; EVAL-61 re-sealed NO-GO (artifact, superseded by EVAL-62). EVAL-61 gate exit 0.
- 2026-11-16T04:12→06:28: ~12 handoff-verification/timestamp-bump sessions (no heavy artifacts); EVAL-63 task defined but never actually sealed.
- **2026-11-16T08:1x–08:25Z (this session, real heavy work):** (1) Fixed two copy-and-retarget bugs in the UNSEALED EVAL-64: `e62.build_prereg_md` `KeyError` on the EVAL-64 split floor schema (added local `build_prereg_md`), and the stale EVAL-63 test file (retargeted to `eval64`/`EVAL_64_*`). EVAL-64 tests 8/8 pass. (2) Sealed **EVAL-64 `NO-GO CONFIRMED (PASS)`** on the real 7d captures (`EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_{PREREGISTRATION,COMBINED}_20261116T082210Z`; floor_ok=true; BTC best −0.5837, ETH best −0.0954; pooled PBO 0.375; gate exit 0); removed spurious partial artifacts from the first failed seal attempt. (3) Corrected the handoff: **EVAL-63 was never actually sealed** (no `EVAL_63_*` artifact in tree or git); EVAL-64 supersedes it. (4) Built + tested **EVAL-65** (`scripts/eval65_orderflow_tox_rv_predictiveness.py`, `tests/test_eval65_...`, 8/8 pass) — wrapper-free Spearman rank-IC predictiveness reusing sealed EVAL-62 `build_states` + sealed EVAL-64 floor; verified `--no-write` on the real 7d captures (floor_ok=true, NO-GO: BTC 0 pass / ETH 2 pass at bar60 h72). EVAL-65 left **UNSEALED** for the next session (heavy: seal + gate). No synthetic data; no sealed EVAL-02..62/64 edits; no EVAL re-runs.
- **2026-11-16T08:39Z (this recovery session, same GitHub Actions run as session 58):** Diagnosed push failure — GitHub pre-receive hook rejects `data/raw/eval63/three_way_{BTC,ETH}_20261116T064816Z.json` (~170 MB each) over the 100 MB per-file limit (root cause: oversized real captures). Preserved session-58 commit `d98a38942` in backup branch `recovery/session-58-checkpoint-d98a38942` (recovery bundle) + reflog. Rewound `main` to `origin/main` without touching the working tree; committed the pushable subset (EVAL-64 seal, EVAL-65 tooling/tests, handoff, `.gitignore` ignoring `data/raw/eval63/`); pushed successfully. Remote-tracking `origin/main` == local `main` == `4f26fb5859dacbde5632a761ac8537044805cc75` — persistence claimed. Captures remain on local disk for EVAL-65 (gitignored, not re-committed). Rollback: `git reset --hard recovery/session-58-checkpoint-d98a38942`. Next task unchanged: seal EVAL-65 (`INIT-2026-11-16T08:25:00Z-EVAL65-OFLOW-TOX-RV-PREDICTIVENESS-SEAL`).

(End of file)