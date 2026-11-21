# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T14:55:43Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** `...options...orderflow...strategy` ⇒ two load-bearing signal halves (options **surface** + options **order-flow**) feeding one deliverable (a **tradeable, net-of-cost strategy**). The order-flow half is the highest charter-relevance rung; its distributional-moment sweep is **COMPLETE** (signed-return mean EVAL-149/150/151/152, skewness 153/154, downside-semivariance share 155/156, kurtosis 157/158, forward realized return variance 159/160) — **every order-flow cell is NO-GO CONFIRMED (PASS)**, the order-flow line is uniformly NO-GO as a standalone predictor. The surviving directional alpha is entirely on the **surface** line (EVAL-101/102/104 GO CONFIRMED, IC 0.26–0.41). **The surface-signal → forward-CVaR tail-risk sweep is now COMPLETE:** EVAL-161 (`term_slope`→CVaR) sealed `NO-GO CONFIRMED (PASS)`, EVAL-162 (`term_ratio`→CVaR) sealed `NO-GO CONFIRMED (PASS)`, EVAL-163 (`atm_iv`→CVaR) sealed `GO CONFIRMED` (`20261121T111517Z`; floor OK, BTC best IC 0.2068 / ETH best IC 0.2481, both assets pass, 8 BH-FDR-rejected configs), and EVAL-164 (`skew`→CVaR) sealed `NO-GO CONFIRMED (PASS)` (`20261121T150532Z`; floor OK BTC/ETH; BTC best IC -0.0092/0 pass, ETH best IC 0.1908/4 pass, both-asset GO bar failed). `atm_iv`→CVaR (EVAL-163) is the only surviving surface-tail-risk GO.
>
> **DECISIVE CONFIRMED FACT — the "strategy" (traded-form, net-of-cost) deliverable is DATA-BLOCKED, not merely unbuilt.** A fresh EVAL-64 feasible-floor probe across every on-disk capture (`data/raw/eval61`, `eval67`, `eval68`) shows **no single capture meets the floor**: the short 24h captures (eval61, 2026-11-15/16) have rich option flow (`of_instruments` 227–248 ≥ 150, `option_trades` ≥ 2748 ≥ 2000) but far too little duration (289 surface snaps / 288 5m bars < 1000; perp span 86400s < 300000s); the long 3.7-day captures (eval67/68, 2026-11-16→20) have sufficient duration (1066–1067 snaps, 1001 5m bars, 319680s span) but a quiet trailing 24h Deribit option-trade window (`of_instruments` 93–101 < 150; ETH `option_trades` 1895 < 2000). **EVAL-69 (traded-form capstone on eval68) sealed `BLOCKED` ("Floor met: False", `20261120T015619Z`), EVAL-124 sealed `BLOCKED` (`20261119T125055Z`), and EVAL-161/162/163/164's dry-runs confirm the composed EVAL-74/EVAL-71 term/surface floor is met on eval61 while the EVAL-64 ladder floor is not — the two floors are distinct and neither is weakened.** Any single-asset traded-form net-of-cost rung on existing captures would re-seal `BLOCKED` on the same data ceiling — that is the bottleneck.
>
> **BOTTLENECK REMOVED THIS SESSION — the traded-form acquisition can no longer BLOCK a session.** TRACK A (a fresh ~3.7-day three-way capture) inherently needs ~3.7 days of wall-clock collection, so it can NEVER complete inside one agentic session; treating it as "mandatory-first every session" was the inefficiency that let a session stall waiting on an impossible in-session acquisition. **TRACK A is RE-CLASSIFIED to a non-blocking background option** (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, run under `background_process`/`start` if a persistent process is available, else deferred to the operator). It is NOT a per-session gate. The per-session heavy work is always the runnable-now rung below, which always advances.
>
> **HALF-WIRE BOTTLENECK FIXED THIS SESSION:** `scripts/eval67_prethreshold_progress.py` had EVAL-164's test files + gate + seal-spec wired but `EXPECTED_TARGETED_TESTS` left at `2063` while `pytest --collect-only` returns **2079** (2015 + 4×16 for EVAL-161/162/163/164). Reconciled `EXPECTED_TARGETED_TESTS` → **2079** before `--execute`. Always reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (see Bottleneck 9).
>
> **THE CORRECT NEXT CAMPAIGN:**
> - **FIRST ACTION, non-negotiable, every session:** run the full heavy-work driver and require exit 0 (idempotent no-op on every sealed rung, now including EVAL-164):
>   ```bash
>   python3 scripts/eval67_prethreshold_progress.py --execute
>   ```
>   Require: `targeted_tests: 2079/2079`, `diagnostic_tests: 27/27`, all `EVAL-70..164` gates `SEALED`/`ok` (100 gates), all `seal_gates` ok (100/100), `EVAL-67/68/69` `SEALED` (forward disjoint-window threshold `2026-11-20T00:00:00Z` PASSED), `failures: []`, `gate_exit=0`. This was verified green THIS SESSION at `15:06:10Z` (`ok: true`, `exit_code: 0`, `failures: []`, `2079/2079`, `27/27`, 100/100 gates classified ok, 100/100 seal_gates ok).
> - **EVAL-164 is DONE (`NO-GO CONFIRMED (PASS)`, sealed `20261121T150532Z`) — the surface→CVaR sweep is complete.** Do not re-run/re-seal EVAL-161/162/163/164.
> - **TRACK A (non-blocking background, NOT a per-session gate):** fresh 3.7-day acquisition → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung EVAL-165 (single-asset `atm_iv` or `term_slope` → *directional* delta-hedged traded-form net-of-cost, distinct from all sealed traded-form cells; reuse EVAL-64 floor + EVAL-62 mark-path verbatim). Build + wire + seal in the SAME session, then re-run the driver (require exit 0). If the floor is NOT met, seal `BLOCKED` (never NO-GO). Do NOT block the session on this; the driver (EVAL-164 sealed, idempotent) always runs first.

## DECISIVE BOTTLENECK (resolved this session — load-bearing)

The charter's terminal deliverable is a *tradeable, net-of-cost* strategy. Every such rung requires the sealed **EVAL-64 feasible floor** (`scripts/eval64_orderflow_realized_vol_markpath_feasible.py`: `MIN_SNAPSHOTS=1000`, `MIN_SURFACE_BARS_5M=1000`, `MIN_PERP_BARS_5M=1000`, `MIN_PERP_SPAN_SECONDS=300000`, `MIN_OPTION_TRADES=2000`, `MIN_OF_INSTRUMENTS=150`, `MIN_SURFACE_INSTRUMENTS=100`, `MIN_COMMON_BARS=240`, `MIN_UNDERLYINGS=2`). The floor is **not weakened**. Measured floor probe (2026-11-21):

| capture | snaps | 5m bars | option_trades | of_instruments | verdict |
|---|---|---|---|---|---|
| eval61 BTC/ETH (24h, 11-15/16) | 289 | 289 | 2748–6872 | 227–248 | fail: snapshots, surface_bars, perp_bars, perp_span |
| eval67 BTC (3.7d) | 1066 | 1001 | 3443 | 101 | fail: of_instruments (101<150) |
| eval68 BTC (3.7d) | 1067 | 1001 | 3469 | 96 | fail: surface_instruments (99<100), of_instruments (96<150) |
| eval68 ETH (3.7d) | 1067 | 1001 | 1895 | 93 | fail: option_trades (1895<2000), of_instruments (93<150) |

**Root cause:** Deribit option-trade retention is ~24h, so a multi-day capture's *duration* legs (surface/perp) scale up while its *option-flow* leg stays 24h-capped. A single capture passes only when its trailing 24h option window is liquidity-rich (`of_instruments ≥ 150`, `trades ≥ 2000`) **and** its surface/perp legs span ≥ ~3.5 days. This is a liquidity-timing condition, not a duration one. **Unblock condition = a fresh 3.7-day capture whose trailing 24h option window is rich.** Until then, the honest traded-form verdict is `BLOCKED`, never NO-GO. Confirmed by EVAL-69 `BLOCKED` and EVAL-124 `BLOCKED`.

**NEW BOTTLENECK REMOVED THIS SESSION (was blocking the driver):** the prior (interrupted, 08:25) session had left EVAL-161 TRACK B half-built and the driver RED. Three concrete defects, all fixed this session: (1) `run_eval161` iterated `for c in captures:` / `for cap in captures:` over a **dict** (yielding string keys) → `AttributeError: 'str' object has no attribute 'get'` in 4 tests; (2) `run_eval161` never called the `_campaign_floor` helper the tests monkeypatch (inline floor check instead); (3) `EXPECTED_TARGETED_TESTS` was set to the *passed* count instead of the authoritative `--collect-only` total. All fixed; EVAL-161/162/163/164 wired into `GATE_SPECS`+`SEAL_SPECS` and sealed. **Do not re-attempt single-asset traded-form on eval61/67/68 expecting a verdict — it will seal `BLOCKED`; acquire (TRACK A) or rely on the sealed surface→CVaR predictiveness cells.**

## VERIFIED STATE (2026-11-21T15:06:10Z, this session — driver green exit 0, EVAL-164 sealed NO-GO CONFIRMED (PASS))

Driver source of truth: `EXPECTED_TARGETED_TESTS=2079`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`; reconcile with `pytest --collect-only` if you add a rung). All `EVAL-70..164` `SEALED`/`ok` (100 gates classified ok; 100/100 `seal_gates` ok); `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (`generated_at: 2026-11-21T15:06:10Z`; `targeted_tests.passed=2079`, `diagnostic_tests.passed=27`, `gate_exit=0`, all gates classified ok).

- **NEW VERIFIED FACTS (this session):** (a) full driver re-run `--execute` **green, exit 0** (`targeted_tests 2079/2079`, `diagnostic_tests 27/27`, `failures: []`, `gate_exit=0`, 100/100 gates classified ok / SEALED, 100/100 `seal_gates` ok, EVAL-164 gate SEALED + seal ok); (b) **EVAL-164 BUILT + WIRED + SEALED `NO-GO CONFIRMED (PASS)`** (`EVAL_164_SINGLE_ASSET_SKEW_FORWARD_CVAR_COMBINED_20261121T150532Z.json/.md`; `floor_ok=True`, BTC best IC -0.0092 / 0 pass, ETH best IC 0.1908 / 4 pass, both-asset GO bar failed → NO-GO CONFIRMED (PASS)) — the surface→CVaR sweep is now COMPLETE (term_slope EVAL-161 NO-GO, term_ratio EVAL-162 NO-GO, atm_iv EVAL-163 GO CONFIRMED, skew EVAL-164 NO-GO CONFIRMED (PASS)); (c) `EXPECTED_TARGETED_TESTS` reconciled 2063→2079 via `pytest --collect-only` (2015+16+16+16+16). **No sealed artifact (EVAL-02..163) or `src/` was modified; only EVAL-164 was added and sealed, and the driver count table was reconciled.**

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..147 | 78 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-64/69/72/75, 76, 80, 82, 124/135, 137, 142 | all `NO-GO`/`BLOCKED` (EVAL-64/69/124 `BLOCKED` = floor) |
| Cross-asset surface/term spillover → forward signed return mean | EVAL-148 (atm_iv/skew/term_slope/term_ratio) | **SEALED COMPLETE** (`010725Z`..`010827Z`) |
| Cross-asset options order-flow → forward signed return mean | EVAL-149 (imbalance), 150 (imbalance×atm_iv), 151 (toxicity×atm_iv), 152 (toxicity alone) | **SEALED COMPLETE** (`010848Z`..`025341Z`) |
| Cross-asset options order-flow → forward skewness | EVAL-153 (toxicity), 154 (imbalance) | **SEALED COMPLETE** (`025645Z`, `031533Z`) |
| Cross-asset options order-flow → forward downside-semivariance share | EVAL-155 (toxicity), 156 (imbalance) | **SEALED COMPLETE** (`042021Z`, `044145Z`) |
| Cross-asset options order-flow → forward realized return kurtosis | EVAL-157 (toxicity), 158 (imbalance) | **SEALED COMPLETE** (`054648Z`, `060009Z`) |
| Cross-asset options order-flow → forward realized return variance | EVAL-159 (toxicity), 160 (imbalance) | **SEALED COMPLETE** (`065641Z`, `075913Z`); order-flow moment sweep DONE |
| Single-asset surface term slope → forward expected shortfall / CVaR | EVAL-161 (term_slope) | **SEALED** `NO-GO CONFIRMED (PASS)` (`20261121T094413Z`); first CVaR rung; BTC 4 pass / ETH 0 |
| Single-asset surface term ratio → forward expected shortfall / CVaR | EVAL-162 (term_ratio) | **SEALED** `NO-GO CONFIRMED (PASS)` (`20261121T103105Z`); BTC 4 pass / ETH 0, best IC 0.3605 |
| Single-asset surface atm_iv → forward expected shortfall / CVaR | EVAL-163 (atm_iv) | **SEALED** `GO CONFIRMED` (`20261121T111517Z`); floor OK, BTC best IC 0.2068 / ETH best IC 0.2481, both assets pass, 8 BH-FDR-rejected configs |
| Single-asset surface skew → forward expected shortfall / CVaR | EVAL-164 (skew) | **SEALED** `NO-GO CONFIRMED (PASS)` (`20261121T150532Z`); floor OK BTC/ETH; both-asset GO bar failed; surface→CVaR sweep COMPLETE |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: EVAL-165 via TRACK A only if the EVAL-64 floor is met; EVAL-164 complete

The order-flow distributional sweep is complete and uniformly NO-GO; the surface-line directional GOs (EVAL-104 `term_slope` IC 0.4058, EVAL-102 `term_ratio` IC 0.3926, EVAL-101 `atm_iv` IC 0.3442) are the only surviving alpha. EVAL-161 (term_slope→CVaR), EVAL-162 (term_ratio→CVaR) and EVAL-164 (skew→CVaR) are sealed NO-GO; **EVAL-163 (atm_iv→CVaR) is sealed GO CONFIRMED** — the surface→CVaR sweep is complete and there is no further runnable-now predictiveness rung. The terminal deliverable (traded-form net-of-cost) remains blocked on the EVAL-64 floor (see DECISIVE BOTTLENECK).

1. **EVAL-165 (only if TRACK A floor is met):** single-asset `atm_iv`/`term_slope` → *directional* delta-hedged traded-form net-of-cost (distinct from all sealed traded-form cells). Prerequisite: a fresh 3.7-day capture whose trailing 24h option window passes the EVAL-64 floor (`of_instruments ≥ 150`, `option_trades ≥ 2000`, surface/perp ≥ ~3.5 days). Reuse EVAL-64 floor + EVAL-62 mark-path verbatim. Build + wire + seal in the SAME session, then re-run the driver (require exit 0).
2. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day acquisition → EVAL-64 floor probe → **if floor met**, build EVAL-165. If floor unmet, seal `BLOCKED` (never NO-GO). Run `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap` under `background_process`/`start` if a persistent process is available, else defer to the operator. It is NOT a per-session gate; the driver (EVAL-164 sealed, idempotent) always runs first.

**Already covered — do NOT rebuild/re-litigate:** EVAL-77, 88..164; all sealed traded-form cells EVAL-64/69/72/75/76/80/82/124/135/137/142; do NOT re-test `atm_iv`→VRP or `term_ratio`→VRP (mechanical overlap); do NOT rebuild the collar (EVAL-76); do NOT re-run EVAL-144..164 as a substitute; do NOT weaken EVAL-64; do NOT touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) complete. EVAL-70..164 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137/142: `SEALED`(0) complete (BLOCKED). EVAL-138/139: `SEALED`(0) complete (GO CONFIRMED). EVAL-140/141/144..164: `SEALED`(0) complete (NO-GO; EVAL-143 per run; EVAL-163 GO CONFIRMED; EVAL-164 NO-GO CONFIRMED (PASS)). Idempotent no-ops; do not re-run.
- Green driver = env OK, `2079/2079` targeted, `27/27` diagnostics, all `EVAL-70..164` gates classified `ok`/phase `SEALED` (100 gates), all `seal_gates` ok (100/100), `failures: []`, `gate_exit=0`.
- EVAL-164 is built+sealed (NO-GO CONFIRMED (PASS)): its test files are in `TARGETED_TEST_FILES`, its gate in `GATE_SPECS`, its seal in `SEAL_SPECS`, and `EXPECTED_TARGETED_TESTS` bumped to `2079` (reconciled with `pytest --collect-only`). No `expected_exit` flip needed (EVAL-164 is `expected_exit: 0`). Do not re-run EVAL-161/162/163/164 as a substitute for new work.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung (order-flow sweep → surface strategy pivot → EVAL-161 term_slope→CVaR → EVAL-162 term_ratio→CVaR → EVAL-163 atm_iv→CVaR → EVAL-164 skew→CVaR → traded-form when floor met).
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
6. Stale-handoff / timestamp-refresh treadmill — fixed this session: the handoff reflects the TRUE state (EVAL-164 sealed NO-GO CONFIRMED (PASS); surface→CVaR sweep complete; traded-form DATA-BLOCKED, not merely unbuilt) and points at the genuinely-next runnable work (driver idempotent no-op + TRACK A background acquisition → floor probe → EVAL-165 only if floor met). Do not refresh the timestamp without new verified facts (green driver + green tests + green gates + a real measurement).
7. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
8. Degenerate skew/kurtosis/variance fixture trap — alternating ±drift yields an all-zero third/fourth/second moment; skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift. EVAL-161's `_forward_cvar` fixtures already follow this.
9. Half-wired driver: a new rung's test files added to `TARGETED_TEST_FILES` without adding the rung to `GATE_SPECS`/`SEAL_SPECS` and without bumping `EXPECTED_TARGETED_TESTS`, so the driver fails the count check. **CONFIRMED AND FIXED this session (EVAL-164): `EXPECTED_TARGETED_TESTS` reconciled 2063→2079 via `pytest --collect-only` (2015+16+16+16+16) before `--execute`.** Always reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
10. Signal/target (and hyphenated `TERM-RATIO`) copy-paste bugs in a cloned runner/gate/tests — always grep the new files for stale ids, hyphenated task labels, signal/target names AND stale helper references before sealing.
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to have ≥1 BH-FDR-rejected passing config; a single-asset pass is a legitimate `NO-GO CONFIRMED (PASS)`; do not relax the bar. (EVAL-164 is exactly this: BTC 0 pass, ETH 4 pass → NO-GO.)
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_slope`/`term_ratio` via EVAL-74 `_term_bars`; order-flow imbalance/toxicity via EVAL-62 `build_states`. Do not cross them.
13. No-hyphen / underscore / hyphenated `EVAL161` / `EVAL_161` / `EVAL-161` task-label traps when cloning — a single bulk replace of one form does NOT catch the others; grep for ALL THREE forms before sealing. (Same for EVAL-164.)
14. Traded-form "data-blocked" misread as "unbuilt". A traded-form rung is NOT productively buildable on eval61/67/68: it will seal `BLOCKED` (EVAL-64 floor unmet) — this is the honest ceiling, not a bug. Do NOT re-attempt single-asset traded-form on the existing captures expecting a verdict; either (a) acquire a floor-passing capture (TRACK A — a NON-BLOCKING background option, NOT a per-session gate) or (b) run the runnable predictiveness rung (none remain; surface→CVaR sweep complete). Never weaken EVAL-64 to force a verdict, and never stall a session waiting on the multi-day acquisition.
15. Duplicate-artifact churn on already-sealed rungs (EVAL-126). A background poller keeps re-running EVAL-126 and appends `..._BLOCKED_<stamp>` / `..._PREREGISTRATION_<stamp>` files (hundreds already committed; a new pair appears every ~5 min — confirmed again this session at `092922Z/093429Z/093940Z/094801Z/095257Z`). These are NOT new work and do NOT change EVAL-126's sealed `GO CONFIRMED` verdict. Do not re-run EVAL-126, do not commit the churn files, and do not mistake them for a live campaign. `research_state/` holds 100k+ tracked files for this reason — never enumerate it; read only the specific `EVAL_<n>_*.md` you need.
16. **Dict-vs-list iteration in a cloned runner (EVAL-161 root cause).** `for c in some_dict:` yields **keys** (strings), not capture dicts → `AttributeError: 'str' object has no attribute 'get'`. When cloning any runner that builds a `{underlying: capture}` dict, iterate `.values()`. Also ensure the campaign-floor helper the tests monkeypatch (`_campaign_floor`) is actually CALLED by the runner.
17. **Multi-day acquisition treated as a per-session gate (removed this session).** TRACK A's fresh ~3.7-day capture needs ~3.7 days of wall-clock collection, so it can NEVER complete inside one agentic session; requiring it "mandatory-first every session" let sessions stall or re-stamp without real progress. It is now a non-blocking background option (`background_process`/`start` if available, else operator-deferred). The per-session heavy work is the driver (idempotent) which always advances. If a future floor-passing capture appears on disk, run the EVAL-64 floor probe; only then attempt the traded-form rung (EVAL-165).

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..164 artifacts or `src/`. Append-only for new authorized work (EVAL-164 sealed; EVAL-165 next via TRACK A).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-68 acquires BTC+ETH in ONE process; EVAL-69/143/145/146/147/149/150/151/152/153/154/155/156/157/158/159/160/161/162/163/164 acquire nothing (consume on-disk `data/raw/eval61`).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint past window.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs (do not edit). A NEW large capture dir (e.g. `data/raw/eval162cap`, ~100MB+, like the gitignored `data/raw/eval63/`/`eval66/`) must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement, e.g. a floor probe or a sealed rung).

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session (idempotent). EVAL-70..164 SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2079/2079, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..164 gates SEALED/ok, all seal_gates ok (100/100). EXPECTED_TARGETED_TESTS=2079
#    (reconciled via pytest --collect-only; was 2063 before EVAL-164 was wired).

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval164_phaseb_gate.py   # EVAL-164 already SEALED NO-GO CONFIRMED (PASS); exit 0 no-op

# 3) EVAL-64 feasible-floor probe across all on-disk captures (decides whether TRACK A can build traded-form EVAL-165):
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

# 4) TRACK A (NON-BLOCKING background; ~3.7 days wall-clock, cannot finish in one session):
#    run under background_process/start if available, else defer to the operator. Do NOT block the session on it.
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap
#    if the capture completes and the EVAL-64 floor is met -> build EVAL-165 traded-form; else seal BLOCKED.

# 5) Anti-avoidance: a green driver plus all-sealed is NOT completion. EVAL-164 is sealed; there is no
#    further runnable-now predictiveness rung. The only path to the terminal traded-form deliverable is
#    TRACK A → EVAL-64 floor probe → EVAL-165 (only if floor met). Never stall on TRACK A (~3.7 days,
#    never in-session).
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..164 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125, 138, 139, 163 (`GO CONFIRMED`). NO-GO CONFIRMED (PASS): EVAL-70, 72, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 127, 128, 129, 130, 131, 133, 134, 136, 140, 141, 144, 145, 146, 147, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 164. BLOCKED (curated): EVAL-64, EVAL-69, EVAL-124, EVAL-135, EVAL-137, EVAL-142. EVAL-67/68/69 SEALED (forward ladder complete). EVAL-148 (4 cells) SEALED. EVAL-149 SEALED. Strongest surviving GO IC anchors unchanged: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643); EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128); EVAL-138 `term_ratio` spillover→return kurtosis (BTC 0.2931 / ETH 0.4679); EVAL-139 `term_ratio` spillover→return skewness (BTC 0.2613 / ETH 0.4878, 7 BH-FDR); **EVAL-163 `atm_iv`→forward CVaR (BTC best IC 0.2068 / ETH best IC 0.2481, both assets pass, 8 BH-FDR-rejected configs — GO CONFIRMED)**. **CVaR tail-risk anchors:** EVAL-161 `term_slope`→forward CVaR (BTC 0.3073, 4 pass; ETH 0.0756, 0, NO-GO); EVAL-162 `term_ratio`→forward CVaR (BTC 0.3605, 4 pass; ETH 0.0424, 0, NO-GO); **EVAL-163 `atm_iv`→forward CVaR (GO CONFIRMED)**; **EVAL-164 `skew`→forward CVaR (NO-GO CONFIRMED (PASS))**. Order-flow NO-GO anchors (all fail the both-asset GO bar): EVAL-152 toxicity→signed-return (BTC 0.1878, 1 pass; ETH 0.0969, 0); EVAL-153 toxicity→skewness (BTC 0.2180, 2; ETH 0.0598, 0); EVAL-154 imbalance→skewness (BTC 0.0573, 0; ETH 0.0887, 0); EVAL-157 toxicity→kurtosis (ETH→BTC 0.1004, 0; BTC→ETH 0.0927, 0); EVAL-1... (line truncated at handoff length; per-rung `.md` files remain authoritative).

> **EVAL-126 correction:** EVAL-126 is sealed **GO CONFIRMED** per its COMBINED artifact (`EVAL_126_..._COMBINED_20261119T144715Z.json`, `verdict=GO CONFIRMED`), NOT NO-GO — it is removed from the NO-GO list above. A background poller repeatedly re-runs EVAL-126 and appends duplicate `..._BLOCKED_<stamp>` / `..._PREREGISTRATION_<stamp>` artifacts (hundreds exist, 2026-11-19→21); these re-run files do NOT change the sealed GO verdict (the driver treats EVAL-126 as SEALED no-op). Do NOT re-run EVAL-126 and do NOT treat the churn files as new work (see Bottleneck 15). Per-rung `.md` files remain authoritative.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-21T11:15:17Z:** EVAL-163 BUILT + WIRED + SEALED `GO CONFIRMED` (surface→CVaR sweep: term_slope/term_ratio NO-GO, atm_iv GO); driver green `2063/2063`+27/27 exit 0.
- **2026-11-21T15:05:32Z / 15:06:10Z:** **EVAL-164 BUILT + WIRED + SEALED `NO-GO CONFIRMED (PASS)` (surface→CVaR sweep COMPLETE) + half-wire bottleneck fixed + driver green.** (a) Reconciled `EXPECTED_TARGETED_TESTS` 2063→2079 via `pytest --collect-only` (2015+16+16+16+16) — EVAL-164's tests/gate/seal-spec were wired but the count was stale (Bottleneck 9). (b) Ran the full driver `--execute` → **green, exit 0** (`2079/2079`, `27/27`, `failures: []`, `gate_exit=0`, 100/100 gates ok/SEALED, 100/100 seal_gates ok, EVAL-164 seal ok). (c) EVAL-164 verdict: floor OK (BTC/ETH), BTC best IC -0.0092/0 pass, ETH best IC 0.1908/4 pass, both-asset GO bar failed → `NO-GO CONFIRMED (PASS)`. (d) Surface→CVaR sweep COMPLETE (EVAL-161/162/164 NO-GO CONFIRMED (PASS); EVAL-163 GO CONFIRMED). No sealed artifact (EVAL-02..163) or `src/` modified; only EVAL-164 added and sealed + driver count reconciled. **Next session: run driver (exit 0, idempotent no-op), then pursue TRACK A (background 3.7-day acquisition → EVAL-64 floor probe → EVAL-165 traded-form only if floor met, else seal BLOCKED).**
