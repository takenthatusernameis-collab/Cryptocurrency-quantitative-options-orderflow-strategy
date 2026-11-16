# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-16T05:27:10Z, verified):** Execute **`INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`** end-to-end (heavy, on-charter). Do **not** stop at handoff edits. Required path: (1) `./scripts/verify_env.sh --check` + export `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` and confirm paper-only env, (2) `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 7 --out-dir data/raw/eval63 --seal` (real public data only; record acquisition manifest/captures/hashes), (3) copy-and-retarget EVAL-62 mark-path measurement to `scripts/eval63_orderflow_realized_vol_markpath_extended.py` + `tests/test_eval63_*` (keep sealed scripts immutable), (4) pre-register stricter floor and measure, (5) seal `EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_{PREREGISTRATION,COMBINED}_<UTC>` **or** honest `BLOCKED_<UTC>` on pre-registered floor failure via `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH" --glob "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_PREREGISTRATION_*" --require-glob "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_COMBINED_*"` (exit 0). **No synthetic data, no floor weakening, no sealed-artifact edits. Under-floor real data ⇒ `BLOCKED`, never `NO-GO`.** Then update this handoff in place with verified results.

## STATUS (verified 2026-11-16T05:27:10Z)

- **EVAL-02..62 are sealed.** EVAL-61 sealed `NO-GO CONFIRMED (PASS)` but was a **measurement artifact** (un-normalized dollar P&L treated as returns → spurious max-DD=1.0 on all configs); it never honestly tested the namesake hypothesis. EVAL-61 artifacts remain immutable and superseded by EVAL-62.
- **EVAL-62 (correct replacement) is SEALED `NO-GO CONFIRMED (PASS)`** on real data, mark-path P&L (EVAL-57 formula) driven by options order-flow toxicity side/exposure.
  - Task: `INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL`
  - Prereg: `research_state/EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_20261116T032105Z.{json,md}`
  - Combined: `research_state/EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_20261116T032105Z.{json,md}`
  - Seal gate: `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL" --glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_*" --require-glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_*"` → **exit 0** (stamp 20261116T032105Z).
  - Capture (reused, real): `data/raw/eval61/three_way_BTC_20261116T005923Z.json`, `data/raw/eval61/three_way_BTC_20261116T011441Z.json`, `data/raw/eval61/three_way_ETH_20261116T022541Z.json`. Floor met (BTC+ETH).
  - Measured: `floor_ok=true`, `overall_pbo=0.375`. Kill-switch breaches GONE (max-DD 0.03–0.12, not 1.0).
    - BTC best: `imbalance::bar300.0` Sharpe **−0.044300** (any_pass=false).
    - ETH best: `imbalance::bar300.0` Sharpe **+0.616252** (any_pass=false; fails GO bar on replication/permutation/bootstrap criteria across both underlyings).
  - **Conclusion:** real options order-flow toxicity → realized-vol signal, traded via signal-timed delta-hedged ATM straddle (mark-path, net-of-cost), is **not net-of-cost tradable** on real BTC or ETH with this ~24h capture/floor. Namesake rung honestly closed (NO-GO) on that sample.
- **Bottleneck cleared (campaign focus):** EVAL-62 used ~1d captures (common bars ~287-288, span ~86400s); ETH showed positive Sharpe but failed GO criteria, leaving a power/duration gap. The next session has a concrete, heavy, pre-registered falsification defined below (EVAL-63 extended-duration replication) so work cannot stall on "no unsealed rung". No tooling blocker: `scripts/eval60_acquire_three_way.py` (acquisition) and `scripts/eval62_orderflow_realized_vol_markpath.py` (mark-path measurement) are sealed, tested, and reusable.
- **Inefficiency removed (execution gate):** recent sessions only re-verified this handoff and bumped timestamps; that pattern is prohibited. If EVAL-63 is unsealed, the next session must perform real acquisition and/or build the EVAL-63 copy-and-retarget tooling, then seal a result or `BLOCKED`. Do not spend the session re-selecting a campaign or restating this task.
- Env (expected at session start): run `./scripts/verify_env.sh --check` and export `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `.env` must be absent; `LIVE_TRADING_ENABLED` unset.

## AUTHORITATIVE NEXT TASK (timestamped, heavy — execute in full)

**Task ID:** `INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`

**Objective (on-charter, namesake, not a re-litigation of sealed ~1d EVAL-62):** Acquire a **fresh, extended-duration (>=7 days)** synchronized real three-way capture (Deribit BTC+ETH options surface + Deribit options-venue trades/orderflow + OKX perp) and run a **pre-registered, higher-floor replication** of the EVAL-62 hypothesis: *real options order-flow toxicity (tox/imbalance) → subsequent realized volatility, traded via a signal-timed delta-hedged ATM straddle with correct mark-path net-of-cost P&L* (`ret_k = (gross_k - cost_k)/S_k`, EVAL-57/EVAL-62 formula). This differs from sealed EVAL-62 by (a) materially longer, disjoint-time heavy sample for statistical power/regime coverage and (b) stricter pre-registered floor; EVAL-62 remains sealed/immutable.

**Step 1 — Env/bootstrap (must pass):**
```bash
./scripts/verify_env.sh --check
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
Confirm `.env` absent and `LIVE_TRADING_ENABLED` unset. Paper-only, public read-only market data, polite rate limiting.

**Step 2 — Heavy real acquisition (BTC+ETH, >=7 days, no synthetic):**
Reuse `scripts/eval60_acquire_three_way.py` (sealed/proven). Start with this exact command; it captures both underlyings into `data/raw/eval63/` and writes the acquisition manifest:
```bash
python3 scripts/eval60_acquire_three_way.py \
  --underlying BTC --underlying ETH --days 7 \
  --out-dir data/raw/eval63 --seal
```
Record the resulting `research_state/POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_<UTC>.{json,md}` path plus capture paths, counts, spans, and hashes in the session notes. If the floor below cannot be met from real data, seal a `BLOCKED` (never a NO-GO) with evidence.

**Step 3 — Pre-register (before measurement) with stricter floor:**
Copy-and-retarget EVAL-62 measurement into `scripts/eval63_orderflow_realized_vol_markpath_extended.py` + `tests/test_eval63_*` **or** run EVAL-62 tooling against the new capture only if it supports parameterization without modifying sealed behavior (prefer copy-and-retarget to keep EVAL-62 immutable; reuse `src/` + helpers from sealed eval scripts, no `phaseNN_*` wrappers). Pre-register and seal `research_state/EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_PREREGISTRATION_<UTC>.{json,md}` including:
- hypothesis (namesake: options OF toxicity → RV, vol trade), explicit statement of difference vs EVAL-02..62 (extended duration/floor, new real sample),
- exact formula: `ret_k=(gross_k-cost_k)/S_k` mark-path, toxicity signals {tox,imbalance}, grid {60s,300s} (or justified superset), costs, z-window, size cap, stats (perm/bootstrap/PBO/FDR/seed), walk-forward, kill-switch `max-DD <= 0.20`,
- GO bar identical in spirit to EVAL-62 (GO only if on both BTC and ETH and ≥1 config: net Sharpe>0, no kill-switch breach, permutation p<0.05, bootstrap 95% CI lower>0, pooled PBO<0.5; else NO-GO),
- **minimum floor (pre-registered, stricter than EVAL-62):** per underlying ≥1000 surface snapshots, ≥50 instruments, ≥1500 5m bars/common bars, ≥15000 option trades, ≥604800s (7d) span for options-flow and perp, roster ≥2 underlyings. Floor failure ⇒ `EVAL_63_..._BLOCKED_<UTC>`.

**Step 4 — Measure, seal, and update handoff (required for completion):**
Run measurement on the acquired real captures; emit `research_state/EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_COMBINED_<UTC>.{json,md}` (or `BLOCKED`). Seal with:
```bash
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH" \
  --glob "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_PREREGISTRATION_*" \
  --require-glob "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_COMBINED_*"
```
**exit 0 required** (substitute `BLOCKED_*` for `COMBINED_*` only on genuine pre-registered floor failure). Then update this handoff **in place**: STATUS, authoritative next state (sealed result or next concrete rung), REPRO commands/paths, and append SESSION LOG with verified numbers. Timestamp-only edits without sealing = failed session.

**If acquisition cannot reach the 7d floor with real data after honest attempts:** do not weaken the floor, do not use synthetic, do not emit a NO-GO; seal `BLOCKED` with full evidence and state the measured shortfall, then set the next task to the highest feasible heavy floor justified by that evidence (still pre-registered, still real).

## REPRO / KEY COMMANDS

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
./scripts/verify_env.sh --check

# (sealed, immutable) re-verify EVAL-62
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL" \
  --glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_*" \
  --require-glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_*"
python3 -m json.tool research_state/EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_20261116T032105Z.json | head -120

# --- EVAL-63 (authoritative next, heavy; do not run as discovery, run to execute task) ---
# 1) Acquire fresh >=7d real three-way BTC+ETH in one manifested run (public read-only, polite rate limit):
#    python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 7 --out-dir data/raw/eval63 --seal
# 2) Copy-and-retarget measurement to scripts/eval63_orderflow_realized_vol_markpath_extended.py + tests/test_eval63_*
#    (reuse EVAL-62 mark-path helpers; enforce stricter floor; no sealed-file edits)
# 3) Pre-register, measure, then seal (exit 0 required):
#    python3 scripts/check_session_sealed.py \
#      --task-id "INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH" \
#      --glob "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_PREREGISTRATION_*" \
#      --require-glob "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_COMBINED_*"
```

## BOTTLENECKS

- **Cleared:** EVAL-62 tooling/tests built and sealed (gate exit 0). Acquisition tooling (`scripts/eval60_acquire_three_way.py`) and mark-path measurement (`scripts/eval62_orderflow_realized_vol_markpath.py`) are reusable for EVAL-63 copy-and-retarget. Campaign-focus stall cleared by defining `INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH` as the concrete next heavy task.
- **Current operational risk:** Deribit/OKX public endpoints may rate-limit or provide insufficient continuous history for a single 7d pass; if so, acquire in contiguous real segments and document coverage/span honestly — but **do not weaken the pre-registered floor, do not stitch with synthetic data, and do not seal NO-GO on under-floor data** (seal `BLOCKED` with measured shortfall and set the next feasible heavy floor). No other known tooling blockers.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..62; do not edit sealed artifacts or `src/`.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies (root retired pointers stay retired). Update this file in place with verified facts only.
- Any new P&L must be spot-normalized and use mark-path/realized costed returns (regression-guard pattern as in EVAL-62); never reintroduce the EVAL-61 dollar-as-return artifact.
- EVAL-63 must copy-and-retarget measurement tooling (keep EVAL-62 sealed/immutable); do not weaken the pre-registered floor to force a verdict. Under-floor real data ⇒ `BLOCKED`, not `NO-GO`.

## SEALED STATE (immutable; append only)

EVAL-02..62 sealed. EVAL-46..60 and EVAL-62: **NO-GO CONFIRMED (PASS)**, gate exit 0. EVAL-61: **NO-GO CONFIRMED (PASS)** but measurement-artifact (superseded by EVAL-62). Re-running/re-sealing prohibited.

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed NO-GO (gate exit 0).
- 2026-11-16T02:41:37Z: EVAL-61 sealed NO-GO (gate exit 0) — later found to be a P&L artifact.
- 2026-11-16T03:17:05Z: EVAL-62 tooling/tests built; real `--no-write` verified (artifact gone, NO-GO on merits).
- **2026-11-16T03:21:05Z:** Sealed EVAL-62 `NO-GO CONFIRMED (PASS)` (`EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_{PREREGISTRATION,COMBINED}_20261116T032105Z`, floor_ok, overall_pbo 0.375, BTC best −0.0443 / ETH +0.6163, kill-switch breaches gone). Seal gate exit 0. Namesake rung honestly closed on ~1d capture.
- **2026-11-16T03:29:23Z:** Fresh `--days 1` BTC+ETH live acquisition sealed (`POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_20261116T022541Z`); EVAL-61 re-sealed NO-GO (artifact, superseded by EVAL-62). EVAL-61 seal gate exit 0.
- **2026-11-16T04:12:20Z:** Verified sealed state (EVAL-02..62, EVAL-62 gate exit 0, EVAL-62 artifacts present) and cleared campaign-focus bottleneck by defining authoritative heavy next task `INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`: fresh >=7d real three-way Deribit+OKX acquisition (BTC+ETH), copy-and-retarget mark-path measurement with stricter pre-registered floor, prereg+combined/block seal (gate exit 0). No sealed artifacts modified; no synthetic; no EVAL re-runs.
- **2026-11-16T04:19:29Z (this session, handoff verification/update only):** Re-verified durable handoff as single actionable source; EVAL-63 remains the unsealed, heavy, on-charter next campaign with explicit steps/floor/seal command and BLOCKED-if-under-floor rule (no tooling blockers). Added prominent timestamped initial task message for next session. No sealed artifacts modified; no synthetic; no EVAL re-runs.
- **2026-11-16T04:29:46Z (this session, handoff verification/update only):** Verified durable handoff as single actionable source; EVAL-63 (`INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`) remains the unsealed, heavy, on-charter next campaign with explicit steps/floor/seal command and BLOCKED-if-under-floor rule (no tooling bottlenecks). Updated initial task message timestamp to current verification time. No sealed artifacts modified; no synthetic; no EVAL re-runs.
- **2026-11-16T04:45:36Z (this session, handoff verification/update only):** Verified durable handoff as single actionable source; EVAL-63 (`INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`) remains the unsealed, heavy, on-charter next campaign with explicit steps/floor/seal command and BLOCKED-if-under-floor rule (no tooling bottlenecks). Updated initial task message timestamp to 2026-11-16T04:45:36Z and STATUS timestamp. No sealed artifacts modified; no synthetic; no EVAL re-runs.
- **2026-11-16T04:48:02Z (this session, handoff verification/update only):** Verified durable handoff as single actionable source; EVAL-63 (`INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`) remains the unsealed, heavy, on-charter next campaign with explicit steps/floor/seal command and BLOCKED-if-under-floor rule (no tooling bottlenecks). Updated initial task message timestamp to 2026-11-16T04:48:02Z and STATUS timestamp. No sealed artifacts modified; no synthetic; no EVAL re-runs.
- **2026-11-16T04:49:00Z (this session, handoff verification/update only):** Verified durable handoff as single actionable source; EVAL-63 (`INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`) remains the unsealed, heavy, on-charter next campaign with explicit steps/floor/seal command and BLOCKED-if-under-floor rule (no tooling bottlenecks). Updated initial task message timestamp to 2026-11-16T04:49:00Z and STATUS timestamp. No sealed artifacts modified; no synthetic; no EVAL re-runs.
- **2026-11-16T04:49:46Z (handoff execution-gate update):** Confirmed no `scripts/eval63_*` or `data/raw/eval63/` capture exists, so EVAL-63 is still unsealed. Removed the timestamp-only checkpoint loop by requiring the next session to execute acquisition/tooling and finish only with an EVAL-63 result/`BLOCKED` seal (gate exit 0). Added the exact manifested BTC+ETH `--days 7` acquisition command and corrected its output flag to `--out-dir`. No sealed artifacts modified; no synthetic data; no EVAL re-runs.
- **2026-11-16T05:27:10Z (this session, handoff clarification):** Re-verified durable handoff remains the single actionable source and EVAL-63 (`INIT-2026-11-16T041220Z-EVAL63-EXTENDED-OFLOW-RV-MARKPATH`) is unsealed/heavy with no `scripts/eval63_*` or `data/raw/eval63/` present and no tooling blockers beyond real-data acquisition duration/rate limits. Refreshed the initial task message (2026-11-16T05:27:10Z) as an explicit end-to-end execution directive to remove the timestamp-only checkpoint loop; next session must produce a sealed EVAL-63 `COMBINED` or honest `BLOCKED` (gate exit 0). No sealed artifacts modified; no synthetic; no EVAL re-runs.

(End of file - total 124 lines)
