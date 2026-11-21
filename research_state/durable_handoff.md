# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T08:44:13Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** `...options...orderflow...strategy` ⇒ two load-bearing signal halves (options **surface** + options **order-flow**) feeding one deliverable (a **tradeable, net-of-cost strategy**). The order-flow half is the highest charter-relevance rung; its distributional-moment sweep is **COMPLETE** (signed-return mean EVAL-149/150/151/152, skewness 153/154, downside-semivariance share 155/156, kurtosis 157/158, forward realized return variance 159/160). **Every order-flow cell is NO-GO CONFIRMED (PASS)** — the order-flow line is uniformly NO-GO as a standalone predictor across every moment. The surviving directional alpha is entirely on the **surface** line (EVAL-101/102/104 GO CONFIRMED, IC 0.26–0.41).
>
> **DECISIVE CONFIRMED FACT — the "strategy" (traded-form, net-of-cost) deliverable is DATA-BLOCKED, not merely unbuilt.** A fresh EVAL-64 feasible-floor probe across every on-disk capture (`data/raw/eval61`, `eval67`, `eval68`) shows **no single capture meets the floor**: the short 24h captures (eval61, 2026-11-15/16) have rich option flow (`of_instruments` 227–248 ≥ 150, `option_trades` ≥ 2748 ≥ 2000) but far too little duration (289 surface snaps / 288 5m bars < 1000; perp span 86400s < 300000s); the long 3.7-day captures (eval67/68, 2026-11-16→20) have sufficient duration (1066–1067 snaps, 1001 5m bars, 319680s span) but a quiet trailing 24h Deribit option-trade window (`of_instruments` 93–101 < 150; ETH `option_trades` 1895 < 2000). **EVAL-69 (the traded-form net-of-cost capstone on eval68) already sealed `BLOCKED` ("Floor met: False", `20261120T015619Z`), and EVAL-124 sealed `BLOCKED` (`20261119T125055Z`).** Any single-asset traded-form net-of-cost rung on existing captures would re-seal **BLOCKED** on the same data ceiling — that is the bottleneck removed here.
>
> **THE CORRECT NEXT CAMPAIGN (two tracks, in priority order — do NOT substitute re-running any sealed rung):**
> - **TRACK A (primary — unblock the charter's actual deliverable):** acquire a FRESH ~3.7-day three-way capture via `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval70cap`, timed to a **liquidity-rich trailing 24h** so the single capture simultaneously satisfies `snapshots ≥ 1000`, `surface_bars_5m ≥ 1000`, `perp_bars_5m ≥ 1000`, `perp_span ≥ 300000s` **and** `option_trades ≥ 2000`, `of_instruments ≥ 150`. Verify with the EVAL-64 floor probe (see REPRO). **If and only if the floor is met**, build the next unsealed traded-form rung **EVAL-161**: single-asset `term_slope` (EVAL-104 anchor, BTC IC 0.4058 / ETH IC 0.2600) monetized **net-of-cost** as a *directional* (sign-of-term_slope) delta-hedged traded form, genuinely distinct from sealed EVAL-72/75 (straddle on skew/term-structure RV), EVAL-76 (surface-skew risk reversal), EVAL-124/135/142 (cross-asset risk reversal), EVAL-137 (term_ratio basis straddle spread), EVAL-69 (order-flow→straddle). **If the floor is NOT met, seal `BLOCKED` (never NO-GO) and fall through to TRACK B in the same session — do NOT stop.**
> - **TRACK B (runnable NOW, no network — the anti-avoidance heavy-work backstop):** build + wire + seal **EVAL-161 (predictiveness variant)** on the existing eval61 captures: single-asset `term_slope` (fallback `term_ratio`) → forward **expected shortfall / CVaR** of the signed return — a genuinely-new tail-risk target verified absent from the sealed space (no `expected_shortfall`/`cvar` predictiveness rung exists; it is distinct from the tail-asymmetry-*index* rungs EVAL-85/87/99/100 and from the variance rungs EVAL-159/160). Reuses EVAL-74 `_term_bars`, EVAL-71 `_forward_fill`, EVAL-61/62 `expanding_zscore`, EVAL-65 `_perm_p_ic`/`_boot_ci_ic`, and the EVAL-71 surface floor / EVAL-74 term floor **verbatim**. This is runnable on-disk today.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver and require exit 0 (idempotent no-op on every sealed rung):
>   ```bash
>   python3 scripts/eval67_prethreshold_progress.py --execute
>   ```
>   Require: `targeted_tests: 2015/2015`, `diagnostic_tests: 27/27`, all `EVAL-70..160` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED` (forward disjoint-window threshold `2026-11-20T00:00:00Z` PASSED), every `GATE_SPEC` classified ok + every `SEAL_SPEC` ok, `failures: []`, `gate_phase: SEALED`, `gate_exit=0`. This was verified green this session at `08:06:57Z` and re-confirmed at `08:44:13Z` (`failures: []`, `2015/2015`, `27/27`, `gate_phase=SEALED`, `gate_exit=0`). Then execute TRACK A (fall to TRACK B if floor unmet) — do not merely re-stamp this file.

## DECISIVE BOTTLENECK (new this session — load-bearing)

The charter's terminal deliverable is a *tradeable, net-of-cost* strategy. Every such rung requires the sealed **EVAL-64 feasible floor** (`scripts/eval64_orderflow_realized_vol_markpath_feasible.py`: `MIN_SNAPSHOTS=1000`, `MIN_SURFACE_BARS_5M=1000`, `MIN_PERP_BARS_5M=1000`, `MIN_PERP_SPAN_SECONDS=300000`, `MIN_OPTION_TRADES=2000`, `MIN_OF_INSTRUMENTS=150`, `MIN_SURFACE_INSTRUMENTS=100`, `MIN_COMMON_BARS=240`, `MIN_UNDERLYINGS=2`). The floor is **not weakened**. Measured floor probe (2026-11-21):

| capture | snaps | 5m bars | option_trades | of_instruments | verdict |
|---|---|---|---|---|---|
| eval61 BTC/ETH (24h, 11-15/16) | 289 | 289 | 2748–6872 | 227–248 | fail: snapshots, surface_bars, perp_bars, perp_span |
| eval67 BTC (3.7d) | 1066 | 1001 | 3443 | 101 | fail: of_instruments (101<150) |
| eval68 BTC (3.7d) | 1067 | 1001 | 3469 | 96 | fail: surface_instruments (99<100), of_instruments (96<150) |
| eval68 ETH (3.7d) | 1067 | 1001 | 1895 | 93 | fail: option_trades (1895<2000), of_instruments (93<150) |

**Root cause:** Deribit option-trade retention is ~24h, so a multi-day capture's *duration* legs (surface/perp) scale up while its *option-flow* leg stays 24h-capped. A single capture passes only when its trailing 24h option window is liquidity-rich (`of_instruments ≥ 150`, `trades ≥ 2000`) **and** its surface/perp legs span ≥ ~3.5 days. This is a liquidity-timing condition, not a duration one. **Unblock condition = a fresh 3.7-day capture whose trailing 24h option window is rich.** Until then, the honest traded-form verdict is `BLOCKED`, never NO-GO. Confirmed by EVAL-69 `BLOCKED` and EVAL-124 `BLOCKED`.

## VERIFIED STATE (2026-11-21T08:44:13Z, this session — driver re-run exit 0)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2015`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`). All `EVAL-70..160` `SEALED`/`ok`; `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (`updated_at: 2026-11-21T08:06:57Z`; `tests_passed=2015`, `diagnostics_passed=27`, `total_tests_passed=2042`, `gate_exit=0`, `gate_phase=SEALED`).

- **NEW VERIFIED FACTS (this session):** (a) full driver re-run `--execute` **green, exit 0** at `08:06:57Z` and re-confirmed at `08:44:13Z` (`targeted_tests 2015/2015`, `diagnostic_tests 27/27`, `failures: []`, `gate_phase=SEALED`, `gate_exit=0`); (b) **EVAL-64 floor probe across ALL on-disk captures → NO capture meets the floor** (see table above; binding constraints `of_instruments` 93–101<150 on the 3.7-day captures and duration on the 24h captures); (c) EVAL-69 (traded-form capstone) confirmed `BLOCKED` "Floor met: False" (`20261120T015619Z`) and EVAL-124 `BLOCKED` (`20261119T125055Z`) — the traded-form net-of-cost line is data-blocked; (d) verified **no expected-shortfall/CVaR predictiveness rung exists** (Track B cell is genuinely new). **No sealed artifact or `src/` was modified; the driver was only re-run (idempotent no-op) to refresh verified facts.**

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..147 | 78 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-64/69/72/75, 76, 80, 82, 124/135, 137, 142 | all `NO-GO`/`BLOCKED` (EVAL-64/69/124 `BLOCKED` = floor) |
| Cross-asset surface/term spillover → forward signed return mean | EVAL-148 (atm_iv/skew/term_slope/term_ratio) | **SEALED COMPLETE** (4 cells, `010725Z`..`010827Z`) |
| Cross-asset options order-flow → forward signed return mean | EVAL-149 (imbalance), 150 (imbalance×atm_iv), 151 (toxicity×atm_iv), 152 (toxicity alone) | **SEALED COMPLETE** (`010848Z`..`025341Z`) |
| Cross-asset options order-flow → forward skewness | EVAL-153 (toxicity), 154 (imbalance) | **SEALED COMPLETE** (`025645Z`, `031533Z`) |
| Cross-asset options order-flow → forward downside-semivariance share | EVAL-155 (toxicity), 156 (imbalance) | **SEALED COMPLETE** (`042021Z`, `044145Z`) |
| Cross-asset options order-flow → forward realized return kurtosis | EVAL-157 (toxicity), 158 (imbalance) | **SEALED COMPLETE** (`054648Z`, `060009Z`) |
| Cross-asset options order-flow → forward realized return variance | EVAL-159 (toxicity), 160 (imbalance) | **SEALED COMPLETE** (`065641Z`, `075913Z`); order-flow moment sweep DONE |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: EVAL-161 (TRACK A traded-form on a floor-passing capture; TRACK B runnable CVaR fallback)

The order-flow distributional sweep is complete and uniformly NO-GO; the surface-line directional GOs (EVAL-104 `term_slope` IC 0.4058, EVAL-102 `term_ratio` IC 0.3926, EVAL-101 `atm_iv` IC 0.3442) are the only surviving alpha. The terminal deliverable (traded-form net-of-cost) is blocked on the EVAL-64 floor (see DECISIVE BOTTLENECK). Build the next unsealed rung as:

1. **TRACK A (preferred):** fresh 3.7-day acquisition → floor probe → **if floor met**, EVAL-161 = single-asset `term_slope` → *directional* delta-hedged traded-form net-of-cost (distinct from sealed cells; EVAL-104 directional IC is the monetization target). Reuse EVAL-64 floor + EVAL-62 mark-path + EVAL-74 `_term_bars` verbatim.
2. **TRACK B (fallback, runnable now on eval61):** EVAL-161 = single-asset `term_slope` (fallback `term_ratio`) → forward **expected shortfall / CVaR** predictiveness, reusing EVAL-74/EVAL-71/EVAL-61/EVAL-62/EVAL-65 primitives and the EVAL-71 surface / EVAL-74 term floor verbatim.

**Already covered — do NOT rebuild/re-litigate:** EVAL-77, 88..160; all sealed traded-form cells EVAL-64/69/72/75/76/80/82/124/135/137/142; do NOT re-test `atm_iv`→VRP or `term_ratio`→VRP (mechanical overlap); do NOT rebuild the collar (EVAL-76); do NOT re-run EVAL-144..160 as a substitute; do NOT weaken EVAL-64; do NOT touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) complete. EVAL-70..160 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137/142: `SEALED`(0) complete (BLOCKED). EVAL-138/139: `SEALED`(0) complete (GO CONFIRMED). EVAL-140/141/144/145/146/147/148/149/150/151/152/153/154/155/156/157/158/159/160: `SEALED`(0) complete (NO-GO). EVAL-143: `SEALED`(0) complete (verdict per run). Idempotent no-ops; do not re-run.
- Green driver = env OK, `2015/2015` targeted, `27/27` diagnostics, all `EVAL-70..160` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED`, every `GATE_SPEC` ok + every `SEAL_SPEC` ok, `failures: []`, `gate_phase: SEALED`, `gate_exit=0`.
- After EVAL-161 is built+sealed: add its test files to `TARGETED_TEST_FILES`, add its gate to `GATE_SPECS` and its seal to `SEAL_SPECS`, and bump `EXPECTED_TARGETED_TESTS` to the new `pytest --collect-only` total (reconcile all three tables AND the count in the SAME session — see Bottleneck 9). Flip any `expected_exit` 1→0 for the newly-sealed gate.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung (order-flow sweep → surface strategy pivot → EVAL-161 two-track).
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
6. Stale-handoff / timestamp-refresh treadmill — fixed this session: the handoff now reflects the TRUE state (EVAL-160 sealed; traded-form DATA-BLOCKED, not merely unbuilt) and points at the genuinely-next runnable work (TRACK A unblock / TRACK B CVaR). Do not refresh the timestamp without new verified facts (green driver + green tests + green gates + a real measurement).
7. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
8. Degenerate skew/kurtosis/variance fixture trap — alternating ±drift yields an all-zero third/fourth/second moment; skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
9. Half-wired driver: a new rung's test files added to `TARGETED_TEST_FILES` without adding the rung to `GATE_SPECS`/`SEAL_SPECS` and without bumping `EXPECTED_TARGETED_TESTS`, so the driver fails the count check. Always reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
10. Signal/target (and hyphenated `TERM-RATIO`) copy-paste bugs in a cloned runner/gate/tests — always grep the new files for stale ids, hyphenated task labels, signal/target names AND stale helper references before sealing.
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to have ≥1 BH-FDR-rejected passing config; a single-asset pass is a legitimate `NO-GO CONFIRMED (PASS)`; do not relax the bar.
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_slope`/`term_ratio` via EVAL-74 `_term_bars`; order-flow imbalance/toxicity via EVAL-62 `build_states`. Do not cross them.
13. No-hyphen / underscore / hyphenated `EVAL161` / `EVAL_161` / `EVAL-161` task-label traps when cloning — a single bulk replace of one form does NOT catch the others; grep for ALL THREE forms before sealing.
14. **NEW — Traded-form "data-blocked" misread as "unbuilt".** A traded-form rung is NOT productively buildable on eval61/67/68: it will seal `BLOCKED` (EVAL-64 floor unmet) — this is the honest ceiling, not a bug. Do NOT re-attempt single-asset traded-form on the existing captures expecting a verdict; either (a) acquire a floor-passing capture (TRACK A) or (b) run the runnable CVaR predictiveness fallback (TRACK B). Never weaken EVAL-64 to force a verdict.
15. **NEW — Duplicate-artifact churn on already-sealed rungs (EVAL-126).** A background poller keeps re-running EVAL-126 and appending `..._BLOCKED_<stamp>` files (hundreds already committed; a new one appears every few minutes). These are NOT new work and do NOT change EVAL-126's sealed `GO CONFIRMED` verdict. Do not re-run EVAL-126, do not commit the churn files, and do not mistake them for a live campaign. `research_state/` holds 100k+ tracked files for this reason — never enumerate it; read only the specific `EVAL_<n>_*.md` you need.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..160 artifacts or `src/`. Append-only for new authorized work (EVAL-161).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-68 acquires BTC+ETH in ONE process; EVAL-69/143/145/146/147/149/150/151/152/153/154/155/156/157/158/159/160 acquire nothing (consume on-disk `data/raw/eval61`).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint past window.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs (do not edit). A NEW large capture dir (e.g. `data/raw/eval70cap`, ~100MB+, like the gitignored `data/raw/eval63/`/`eval66/`) must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement, e.g. a floor probe or a sealed rung).

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session (idempotent). EVAL-70..160 SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval160_phaseb_gate.py

# 3) EVAL-64 feasible-floor probe across all on-disk captures (decides TRACK A vs TRACK B):
PYTHONPATH=$PWD/.venv-deps python3 - <<'PY'
import json, glob, os, sys; sys.path.insert(0, ".")
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
for f in sorted(glob.glob("data/raw/eval*/three_way_*.json")):
    r = e64._underlying_floor_strict(json.load(open(f)))
    failed = [k for k,v in r["checks"].items() if not v]
    print(os.path.basename(f), "ok=", r["ok"], "snaps=", r["n_surface_snapshots"],
          "5m=", r["n_surface_bars_5m"], "trades=", r["n_option_trades"],
          "of_inst=", r["n_of_instruments"], "FAILED=", failed)
PY

# 4) TRACK A (primary): acquire a fresh 3.7-day capture timed to a liquidity-rich 24h, then floor-probe it:
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval70cap
#    if floor met -> build EVAL-161 traded-form; else seal BLOCKED and fall to TRACK B.

# 5) TRACK B (fallback, runnable now): build EVAL-161 single-asset term_slope -> forward expected shortfall (CVaR).
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..69, 70..160 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125, 138, 139 (`GO CONFIRMED`). NO-GO CONFIRMED (PASS): EVAL-70, 72, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 127, 128, 129, 130, 131, 133, 134, 136, 140, 141, 144, 145, 146, 147, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160. BLOCKED (curated): EVAL-64, EVAL-69, EVAL-124, EVAL-135, EVAL-137, EVAL-142. EVAL-67/68/69 SEALED (forward ladder complete). EVAL-148 (4 cells) SEALED. EVAL-149 SEALED. Strongest surviving GO IC anchors unchanged: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643); EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128); EVAL-138 `term_ratio` spillover→return kurtosis (BTC 0.2931 / ETH 0.4679); EVAL-139 `term_ratio` spillover→return skewness (BTC 0.2613 / ETH 0.4878, 7 BH-FDR). Order-flow NO-GO anchors (all fail the both-asset GO bar): EVAL-152 toxicity→signed-return (BTC 0.1878, 1 pass; ETH 0.0969, 0); EVAL-153 toxicity→skewness (BTC 0.2180, 2; ETH 0.0598, 0); EVAL-154 imbalance→skewness (BTC 0.0573, 0; ETH 0.0887, 0); EVAL-157 toxicity→kurtosis (ETH→BTC 0.1004, 0; BTC→ETH 0.0927, 0); EVAL-158 imbalance→kurtosis (ETH→BTC 0.1774, 1; BTC→ETH 0.0784, 0); EVAL-159 toxicity→variance (ETH→BTC 0.1412, 0; BTC→ETH 0.1019, 0); EVAL-160 imbalance→variance (NO-GO CONFIRMED).

> **EVAL-126 correction (this session):** EVAL-126 is sealed **GO CONFIRMED** per its COMBINED artifact (`EVAL_126_..._COMBINED_20261119T144715Z.json`, `verdict=GO CONFIRMED`), NOT NO-GO as the prior handoff stated — it is removed from the NO-GO list above. However, a background poller repeatedly re-runs EVAL-126 and appends duplicate `..._BLOCKED_<stamp>` artifacts (hundreds exist, 2026-11-19→21); these re-run BLOCKED files do NOT change the sealed GO verdict (the driver treats EVAL-126 as SEALED no-op). Do NOT re-run EVAL-126 and do NOT treat the churn BLOCKED files as new work (see Bottleneck 15). Per-rung `.md` files remain authoritative.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-21T01:22:25Z:** EVAL-148 (4 cells) + EVAL-149 sealed; driver green 1809/1809+27/27. (Prior session.)
- **2026-11-21T02:18:18Z:** Prior (interrupted) session built EVAL-150/151/152 runners+gates+tests and sealed EVAL-150 (`015450Z`) + EVAL-151 (`020925Z`), wired 150/151 into the driver, but left EVAL-152 unsealed/unwired and set `EXPECTED_TARGETED_TESTS=1845` (actual 1863) — driver left broken; handoff not updated.
- **2026-11-21T03:03:13Z:** Sealed EVAL-152 (`NO-GO`, `025341Z`); wired 152; corrected count 1845→1863; built+wired+sealed EVAL-153 (`NO-GO`, `025645Z`); corrected 1863→1882; driver green 1882/1882+27/27.
- **2026-11-21T03:21:16Z:** Built+wired+sealed EVAL-154 (imbalance→skewness, `NO-GO`, `031533Z`); corrected 1882→1901; driver green 1901/1901+27/27.
- **2026-11-21T04:20:21Z:** Built+wired+sealed EVAL-155 (toxicity→downside-semivariance share, `NO-GO`, `042021Z`); corrected 1901→1920; driver green 1920/1920+27/27.
- **2026-11-21T04:42:15Z:** Built+wired+sealed EVAL-156 (imbalance→downside-semivariance share, `NO-GO`, `044145Z`); corrected 1920→1939; driver green 1939/1939+27/27.
- **2026-11-21T04:55:37Z / 05:37:36Z:** Handoff refreshed (timestamp only); next builds EVAL-157→158.
- **2026-11-21T05:46:48Z:** EVAL-157 (toxicity→forward return kurtosis) sealed `NO-GO CONFIRMED (PASS)` (ETH→BTC 0.1004/0; BTC→ETH 0.0927/0).
- **2026-11-21T06:00:09Z:** EVAL-158 (imbalance→forward return kurtosis) sealed `NO-GO CONFIRMED (PASS)` (ETH→BTC 0.1774, 1 pass; BTC→ETH 0.0784, 0).
- **2026-11-21T06:57:54Z:** Built + wired + sealed EVAL-159 (cross-asset toxicity → forward realized return variance, `NO-GO CONFIRMED (PASS)`, `20261121T065641Z`). Driver green 1996/1996+27/27, exit 0.
- **2026-11-21T07:59:49Z:** EVAL-160 built + wired + sealed `NO-GO CONFIRMED (PASS)` (`20261121T075913Z`). Order-flow moment sweep COMPLETE (mean, variance, skewness, kurtosis, downside-semivariance share — both signals, all NO-GO). Driver green **2015/2015 targeted + 27/27 diagnostics, exit 0**. `EXPECTED_TARGETED_TESTS` 1996→2015.
- **2026-11-21T08:12:00Z:** **Handoff corrected + bottleneck removed (heavy-work continuity restored).** (a) Driver re-run `--execute` green, exit 0 (`2015/2015`, `27/27`, `failures: []`, `gate_phase=SEALED`, `gate_exit=0`) at `08:06:57Z`. (b) **Decisive new measurement:** EVAL-64 floor probe across all on-disk captures → **no capture meets the floor** (24h captures: rich option flow but too-short duration; 3.7-day captures: sufficient duration but `of_instruments` 93–101<150 and ETH `option_trades` 1895<2000). Confirmed EVAL-69 `BLOCKED` + EVAL-124 `BLOCKED`. (c) The previous handoff's "single-asset traded-form net-of-cost" next campaign would have re-sealed **BLOCKED** — re-pointed to a runnable **two-track EVAL-161** plan: TRACK A = fresh 3.7-day liquidity-rich acquisition to unblock the charter's traded-form deliverable (primary); TRACK B = runnable-now `term_slope`→forward expected-shortfall/CVaR predictiveness (verified genuinely new) as the anti-avoidance fallback. No sealed artifact or `src/` modified; only the driver re-run + a read-only floor probe were executed. **Next session: run the driver (exit 0), then execute TRACK A (fall to TRACK B if floor unmet) — build + wire + seal EVAL-161.**

- **2026-11-21T08:44:13Z:** **Driver re-verified green at session boundary** (`targeted_tests 2015/2015`, `diagnostic_tests 27/27`, `failures: []`, `gate_phase=SEALED`, `gate_exit=0`). Handoff initial task message updated to `2026-11-21T08:44:13Z` with confirmed state: all EVAL-70..160 SEALED, order-flow moment sweep COMPLETE (all NO-GO), traded-form line DATA-BLOCKED on EVAL-64 floor (no capture passes), EVAL-161 two-track queue locked in (TRACK A primary: fresh 3.7-day liquidity-rich capture → floor probe → if met, directional delta-hedged `term_slope` traded-form; TRACK B fallback: `term_slope`→forward CVaR predictiveness on eval61). Next agent MUST run driver (exit 0) then execute TRACK A (fall to TRACK B if floor unmet) — build + wire + seal EVAL-161 in same session.