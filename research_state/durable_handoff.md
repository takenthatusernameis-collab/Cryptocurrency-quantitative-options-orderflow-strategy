# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T20:57:00Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** `...options...orderflow...strategy` ⇒ two load-bearing signal halves (options **surface** + options **order-flow**) feeding one deliverable (a **tradeable, net-of-cost strategy**). The order-flow half's distributional-moment sweep is COMPLETE and uniformly NO-GO CONFIRMED (PASS). The surviving directional alpha is on the **surface** line. The single-asset surface distributional grids are complete for signed-return-mean / skewness / kurtosis / CVaR / downside-semivariance share. The cross-asset order-flow distributional sweep is complete. The cross-asset surface/term → forward-CVaR grid is COMPLETE: atm_iv (EVAL-168, sealed GO CONFIRMED), term_slope (EVAL-169, sealed), term_ratio (EVAL-170, sealed), skew (EVAL-171, sealed). **The next mandated heavy work: EVAL-172 (single-asset `atm_iv` → forward realized return variance) is BUILT + WIRED + DUE (unsealed) — the driver is RED (exit 20, `needs_execute: ["EVAL-172"]`).**
>
> **DECISIVE BOTTLENOCk REMOVED — there is ALWAYS runnable-now heavy work.** The prior handoff (15:28:31Z) was STALE: it claimed EVAL-165 was DUE, but EVAL-165/166/167/168 were already sealed, and a half-built EVAL-169 `term_slope` runner existed with no gate/tests/driver wiring. That half-built runner is now COMPLETED (gate + 2 tests + driver wiring) and SEALED. EVAL-170/171 are now SEALED; the driver is intentionally left **RED** on `needs_execute: ["EVAL-172"]` (exit 20) so a future agent cannot produce a green driver without doing the heavy measurement. **This is the anti-avoidance guarantee.**
>
> **THE CORRECT NEXT CAMPAIGN (do these in order, every session):**
> - **FIRST ACTION, non-negotiable, every session:** run the full heavy-work driver and require exit 0:
>   ```bash
>   python3 scripts/eval67_prethreshold_progress.py --execute
>   ```
>   This will SEAL EVAL-172 on this first run (EVAL-170/171 already sealed), then be an idempotent no-op forever after. Require after the seal: `targeted_tests: 2233/2233`, `diagnostic_tests: 27/27`, all `EVAL-70..172` gates classified `ok`/phase `SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. (If EVAL-172 is still DUE after `--execute`, the run FAILED — investigate; do not hand-wave.)
> - **THEN build the next runnable-now rung in the SAME session (never stop at "driver green"):** identify the next genuine gap from the sealed space (never duplicate a sealed cell) and build it as a DUE gate (runner + gate + 2 test files + driver TARGETED_TEST_FILES/GATE_SPECS/SEAL_SPECS + bump `EXPECTED_TARGETED_TESTS` by the `pytest --collect-only` delta), run the driver `--execute` to seal, require exit 0. Natural next cells: remaining single-asset surface (`term_ratio`/`term_slope`/`skew`/`atm_iv`) → forward variance/skewness/kurtosis cells, or cross-asset surface/term → forward variance — all unsealed gaps.
> - **TRACK A (NON-BLOCKING background, NOT a per-session gate):** a fresh ~3.7-day three-way capture (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, under `background_process`/`start` if available, else operator-deferred) → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).
> - **Anti-avoidance:** a green driver plus all-sealed is NOT completion. If EVAL-172 is sealed AND TRACK A has not produced a floor-passing capture, identify the next gap from the sealed space and build it as the next DUE rung before going green. There is ALWAYS a next heavy rung.

## DECISIVE BOTTLENOCk (resolved this session — load-bearing)

The charter's terminal deliverable is a *tradeable, net-of-cost* strategy. Every such rung requires the sealed **EVAL-64 feasible floor** (`scripts/eval64_orderflow_realized_vol_markpath_feasible.py`: `MIN_SNAPSHOTS=1000`, `MIN_SURFACE_BARS_5M=1000`, `MIN_PERP_BARS_5M=1000`, `MIN_PERP_SPAN_SECONDS=300000`, `MIN_OPTION_TRADES=2000`, `MIN_OF_INSTRUMENTS=150`, `MIN_SURFACE_INSTRUMENTS=100`, `MIN_COMMON_BARS=240`, `MIN_UNDERLYINGS=2`). The floor is **not weakened**. Measured floor probe (2026-11-21): eval61/eval67/eval68 all fail (short captures lack duration; long captures' trailing-24h option window is quiet: `of_instruments` < 150). Root cause: Deribit option-trade retention ~24h, so a multi-day capture's duration legs scale but its option-flow leg stays 24h-capped. **Unblock condition = a fresh 3.7-day capture whose trailing 24h option window is liquidity-rich.** Until then, the honest traded-form verdict is `BLOCKED`, never NO-GO (confirmed by EVAL-69/EVAL-124 `BLOCKED`).

**Half-built runner bottleneck removed:** a pre-existing `scripts/eval169_cross_asset_term_slope_spillover_forward_cvar.py` runner had no gate, no tests, and no driver wiring (half-wired trap, Bottleneck 9). Completed as EVAL-169: `scripts/eval169_phaseb_gate.py` + `tests/test_eval169_*.py` (2 files, 18 tests) + wired into driver (TARGETED_TEST_FILES, GATE_SPECS DUE, SEAL_SPECS, `EXPECTED_TARGETED_TESTS` reconciled) + sealed via `driver --execute`. Fixed a TASK_ID/TASK_LABEL (`ATM-IV`→`TERM-SLOPE`) inconsistency in the gate.

## VERIFIED STATE (2026-11-21T20:57:00Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2233`, `EXPECTED_DIAGNOSTIC_TESTS=27`. All `EVAL-66..171` sealed (109 seal gates ok); **EVAL-172 is `DUE` (unsealed) — status-mode driver exits 20 with `needs_execute: ["EVAL-172"]`.** `EVAL-67/68/69` SEALED (forward disjoint-window ladder complete; threshold `2026-11-20T00:00:00Z` PASSED).

- EVAL-170/171 sealed via `driver --execute` (cross-asset `term_ratio`/`skew` → forward CVaR; cross-asset surface/term → forward CVaR grid now COMPLETE: 168 atm_iv + 169 term_slope + 170 term_ratio + 171 skew; runner validated on real `data/raw/eval61`, seal-gate exit 0).
- EVAL-172 built + wired + DUE: `scripts/eval172_single_asset_atm_iv_forward_variance.py` + `scripts/eval172_phaseb_gate.py` + `tests/test_eval172_*.py` (2 files, 17 tests) + wired into driver (TARGETED_TEST_FILES, GATE_SPECS DUE, SEAL_SPECS, `EXPECTED_TARGETED_TESTS=2233` reconciled via `pytest --collect-only`). Runner validated `--no-write` on real `data/raw/eval61` (no crash, computes 12 configs); left **DUE/unsealed** so the driver stays RED (`needs_execute: ["EVAL-172"]`) — the anti-avoidance guarantee.
- No sealed artifact (EVAL-02..171) or `src/` modified; only EVAL-172 added (intentionally DUE) and the driver count table reconciled.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67/68/69 | SEALED (`20261120T...`) |
| Physics-independent predictiveness EVAL-70..160 | 91 rungs | SEALED |
| Single-asset surface → forward CVaR | EVAL-161/162/163/164 | SEALED (163 GO CONFIRMED; others NO-GO CONFIRMED (PASS)) |
| Single-asset surface → forward downside-semivariance share | EVAL-115 (atm_iv), 165 (skew), 166 (term_ratio), 167 (term_slope) | SEALED |
| Cross-asset surface/term → forward signed return mean | EVAL-148 (4 cells) | SEALED COMPLETE |
| Cross-asset options order-flow → forward signed return mean / skewness / downside / kurtosis / variance | EVAL-149..160 | SEALED COMPLETE |
| Cross-asset surface/term → forward CVaR | EVAL-168 (atm_iv), 169 (term_slope), 170 (term_ratio), 171 (skew) | SEALED |
| Single-asset surface → forward variance | EVAL-172 (atm_iv) | **BUILT + WIRED + DUE (unsealed)** |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: `driver --execute` seals EVAL-172 → build next DUE gap → TRACK A background

The order-flow sweep is complete and uniformly NO-GO; the surface-line directional GOs are the only surviving alpha. The single-asset surface distributional grids are complete. The cross-asset → forward-CVaR grid is COMPLETE (atm_iv 168 + term_slope 169 + term_ratio 170 + skew 171, all sealed). **EVAL-172 (single-asset `atm_iv` → forward variance) is BUILT + WIRED + DUE.** The terminal deliverable (traded-form net-of-cost) remains data-blocked on the EVAL-64 floor — NOT the per-session heavy work.

1. **EVAL-172 (DUE — mandated next heavy work; `driver --execute` seals it automatically):** run `python3 scripts/eval67_prethreshold_progress.py --execute` (seals EVAL-172, then idempotent no-op). Require exit 0 (2233/2233, 27/27, failures: [], gate_exit=0).
2. **Next gap (same session after seal, never stop at green):** identify the next genuine unsealed cell from the sealed space (do not duplicate a sealed cell), build it as a DUE gate, run `driver --execute`, require exit 0. Natural next cells: remaining single-asset surface → forward variance/skewness/kurtosis, or cross-asset surface/term → forward variance.
3. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day capture → EVAL-64 floor probe → traded-form rung only if floor met, else `BLOCKED` (never NO-GO). Never block the session on TRACK A.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0). EVAL-70..171 gates: `SEALED`(0) idempotent no-op. **EVAL-172: `DUE`(20) until `driver --execute` seals it; after that `SEALED`(0) idempotent no-op.** `FAILED`(1) fix and rerun.
- Green driver = env OK, `2233/2233` targeted, `27/27` diagnostics, all `EVAL-70..172` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. (Before EVAL-172 is sealed the status-mode driver exits 20 with `needs_execute:["EVAL-172"]` — that is the expected DUE state, not a failure.)
- EVAL-172 built+wired (DUE, unsealed): test files in `TARGETED_TEST_FILES`, gates in `GATE_SPECS`, seals in `SEAL_SPECS` (`expected_exit:0`), `EXPECTED_TARGETED_TESTS=2233` (reconciled: 2216 + 17 via `pytest --collect-only`). Do not re-run EVAL-161/162/163/164/165/166/167/168/169/170/171 as a substitute for new work; do not hand-run a runner — let the driver seal it.

## BOTTLENOCks REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. "No heavy work left" avoidance — removed; EVAL-172 is wired as DUE, forcing the driver red until executed. When sealed, build the next gap as DUE.
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
6. Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-165/166/167/168 already sealed; EVAL-169/170/171 completed+sealed; EVAL-172 DUE) and points at genuinely-next runnable work. Do not refresh the timestamp without new verified facts.
7. Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
8. Degenerate moment fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
9. Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (CONFIRMED for EVAL-172: 2216→2233).
10. Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing (applied to EVAL-169 gate TASK_ID/LABEL fix).
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow via `e62.build_states`. Do not cross them.
13. No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
14. Traded-form "data-blocked" misread as "unbuilt" — the per-session heavy work is ALWAYS a runnable predictiveness rung, never the data-blocked traded-form.
15. Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`.
16. Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor` is actually CALLED.
17. Multi-day acquisition not a per-session gate — TRACK A (~3.7 days) cannot finish in one session; non-blocking background only.
18. **"No runnable-now predictiveness rung" avoidance** — the driver is left RED (EVAL-172 DUE) so the next session is forced to execute heavy work.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..171 artifacts or `src/`. Append-only for new authorized work (EVAL-172 DUE — seal via driver).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168/169/170/171/172 acquire nothing (consume on-disk `data/raw/eval61`).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint past window.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. A NEW large capture dir (e.g. `data/raw/eval162cap`, ~100MB+) must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement).

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. Seals EVAL-172 (DUE), then no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2233/2233, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..172 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2233.
#    (Status-mode without --execute exits 20 with needs_execute:["EVAL-172"].)

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval169_phaseb_gate.py   # EVAL-169 SEALED, exit 0
python3 scripts/eval170_phaseb_gate.py   # EVAL-170 DUE until --execute seals it (exit 20)
python3 scripts/eval171_phaseb_gate.py   # EVAL-171 DUE until --execute seals it (exit 20)

# 3) EVAL-64 feasible-floor probe across all on-disk captures:
PYTHONPATH=$PWD/.venv-deps python3 - <<'PY'
import json, glob, os, sys; sys.path.insert(0, ".")
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
for f in sorted(glob.glob("data/raw/eval*/three_way_*.json")):
    r = e64._underlying_floor_strict(json.load(open(f)))
    failed = [k for k,v in r["checks"].items() if not v]
    print(os.path.basename(f), "ok=", r["ok"], "FAILED=", failed)
PY

# 4) TRACK A (NON-BLOCKING background; ~3.7 days wall-clock; do NOT block the session):
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap
#    if floor met -> build traded-form rung; else seal BLOCKED.

# 5) Anti-avoidance: green driver + all-sealed is NOT completion. Build the next DUE rung.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..171 sealed. **EVAL-172 is BUILT + WIRED + DUE (intentionally UNSEALED — the next `driver --execute` seals it).** EVAL-63 never sealed.
