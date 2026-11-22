# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T07:30:10Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **STATUS THIS SESSION (2026-11-22T07:30Z):** green driver (`eval67_prethreshold_progress.py --execute` exit 0; 2430/2430 targeted, 27/27 diagnostics, `failures: []`, all EVAL-70..183 + EVAL-67/68/69 gates SEALED, 120/120 seal_gates ok). EVAL-184 anti-avoidance gate `scripts/eval184_phaseb_gate.py` reports `WAIT_CAPTURE` (exit 10) with **`runner_green: true`** and **`prereg_present: true`** — runner `scripts/eval184_surface_traded_netofcost_oos.py` (+ prereg + 13 tests) built/green; `--no-write` dry-run green. `data/raw/eval84cap/three_way_BTC_20261122T064658Z.json` (154 MB) landed; **ETH capture MISSING**. ETH three-way acquisition started in background (`bgp_2022d5e33002YpMR2UPctz4LNW`, pid 7352, `--underlying ETH --days 3.7 --end 2026-11-22T06:46:43Z --max-per-expiry 30 --out-dir data/raw/eval84cap --seal`, ~55 min wall) to complete the disjoint floor-compliant capture. Task floor threshold `2026-11-20T00:00:00Z` already passed; disjointness OK once ETH lands. Once ETH lands → verify EVAL-64 floor on both underlyings → `python3 scripts/eval184_phaseb_gate.py --execute` → require `SEALED` (exit 0) + passing `check_session_sealed.py`. Do NOT declare completion on green driver alone; the mandated heavy work is the surface-line traded-form net-of-cost OOS verdict (EVAL-184), enforced by the gate.
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The predictiveness rungs EVAL-02..183 are all sealed. The order-flow × surface interaction cells are uniformly NO-GO CONFIRMED (PASS). The single-asset and cross-asset surface/term distributional grids are complete. The only surviving directional/tail alpha is on the **surface** line (EVAL-177 skew → variance GO; EVAL-168/169 atm_iv/term_slope → CVaR GO).
>
> **DELIVERABLE STATUS (2026-11-22T06:35Z):** the order-flow line is fully resolved and sealed — predictive (EVAL-67/68 GO CONFIRMED) but **NOT tradeable net-of-cost** (EVAL-69 `NO-GO CONFIRMED (PASS)`: predictive but 0 BH-FDR rejections, pooled Sharpe 0.19–0.20, perm_p 0.59–0.60, CI95 spans 0). The surviving tradeable alpha is **exclusively on the surface line**: EVAL-177 (skew → forward variance, GO CONFIRMED) and EVAL-168/169 (atm_iv / term_slope → forward CVaR, GO CONFIRMED). **The single remaining on-charter heavy work is the surface-line traded-form net-of-cost OOS verdict — the EVAL-69 analogue for EVAL-177/168/169 (EVAL-184).** Do NOT re-run or re-litigate sealed EVAL-67/68/69. Do NOT declare completion on green-driver alone.
>
> **⚠ CORRECTION TO THE PRIOR HANDOFF (load-bearing — do not repeat the stale claim):** the previous handoff stated "`data/raw/eval84cap` is already on disk and floor-compliant." **That is now FALSE — `data/raw/eval84cap` is NOT on disk in this checkout** (it was gitignored, ~300 MB, and is gone; only the git-tracked `data/raw/eval61|eval67|eval68` captures persist). The surface-line heavy work is therefore **NOT** data-blocked in the "wait days" sense, but it **does require a fresh ~1 h acquisition** (~3.7 days, both underlyings, Deribit+OKX pagination, network-bound). Budget ~1 h; do not reduce `--days` below 3.7 (the EVAL-64 floor needs the span). Also `.venv-deps` is absent on a fresh checkout — bootstrap once with `./scripts/verify_env.sh` before any run.
>
> **NEW ANTI-AVOIDANCE ARBITER (this session built it — future agents CANNOT skip the heavy work):** `scripts/eval184_phaseb_gate.py` is now the deterministic, idempotent arbiter of the EVAL-184 completion contract. Run it every session BEFORE declaring anything:
>   `python3 scripts/eval184_phaseb_gate.py`  (and `--execute` only when it reports `DUE`).
> Its exit codes encode the exact required work and refuse to let you seal without doing it:
>   - `WAIT_CAPTURE` (exit 10) — no floor-compliant disjoint surface capture at the capture dir. **HEAVY WORK REQUIRED:** acquire it (see the exact command the gate prints). You may NOT substitute a sealed capture or skip to sealing.
>   - `WAIT_RUNNER` (exit 20) — capture present but the EVAL-184 surface-line runner is missing/not green. **HEAVY WORK REQUIRED:** build/fix `scripts/eval184_surface_traded_netofcost_oos.py` + prereg + tests until `--no-write` is green.
>   - `DUE` (exit 30) — capture + runner green, nothing sealed. **HEAVY WORK REQUIRED NOW:** re-run with `--execute` (runs the surface-line traded-form → seals → seal-gate, requires seal-gate exit 0).
>   - `SEALED` (exit 0) — a COMBINED/BLOCKED EVAL-184 artifact exists with stamp ≥ task floor; idempotent no-op. Only now is the surface-line traded-form line complete.
>
> **CURRENT MANDATED QUEUE (the only remaining on-charter work — real in-session heavy work, NOT "wait days" data-blocked):**
> 1. **Env + driver green check (every session):** `./scripts/verify_env.sh` then `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2430/2430 targeted, 27/27 diagnostics, `failures: []`, all EVAL-70..183 + EVAL-67/68/69 gates SEALED, all 120 seal_gates ok). Verified green this session at 2430/2430, 27/27, 120/120.
> 2. **Run the EVAL-184 gate:** `python3 scripts/eval184_phaseb_gate.py`. Read the phase. It will be `WAIT_CAPTURE` right now (no `eval84cap`). Do NOT treat that as "blocked forever" — the contract in its output tells you to acquire the capture. **This is the mandated heavy work.**
> 3. **Acquire the disjoint floor-compliant capture (~1 h, in-session):** `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --end <at/after 2026-11-19T18:08:16Z> --max-per-expiry 30 --out-dir data/raw/eval84cap --seal`. Then verify the EVAL-64 floor on both underlyings (see REPRO step 3) — never weaken it; under-floor ⇒ `BLOCKED`, never NO-GO. Keep `data/raw/eval84cap` LOCAL (gitignored, never commit).
> 4. **Build the surface-line traded-form runner (the heavy computation, in-session):** implement `scripts/eval184_surface_traded_netofcost_oos.py` — the EVAL-69 analogue for the surface line. Signals `skew` (EVAL-177, e71.build_surface_bars) → forward variance; `atm_iv` (EVAL-168, e71.build_surface_bars) and `term_slope` (EVAL-169, e74._term_bars) → forward CVaR — at the bar horizons that produced the GOs. Pre-register a traded-form monetization (mark-path net-of-cost P&L, Sharpe / max-DD / permutation / block-bootstrap, pooled BH-FDR, both-asset GO bar, EVAL-64 floor verbatim, disjointness verbatim). **Reuse the sealed EVAL-69 mark-path/cost helpers (`e62.markpath_returns`, `e62.build_states`) and EVAL-64 feasible floor verbatim** — do not weaken the floor, do not relax the GO bar (single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`). Add its prereg + tests (append-only; grep for hyphen/underscore/hyphenated task-label traps).
> 5. **Seal:** re-run `python3 scripts/eval184_phaseb_gate.py --execute`. Require `SEALED` (exit 0) and a passing `check_session_sealed.py` seal-gate. Then, and only then, reconcile `GATE_SPECS`/`SEAL_SPECS`/`EXPECTED_TARGETED_TESTS` in the driver if you wire it in (append-only; new files only; do not edit sealed artifacts or `src/`).
> 6. **Do NOT re-run / re-litigate the sealed EVAL-67/68/69 or EVAL-70..183 artifacts** — they are historical append-only seals. EVAL-184 produces NEW artifacts.
>
> **NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute):** green driver + all-sealed through EVAL-183 (and EVAL-67/68/69) is **NOT** session completion. The mandated heavy work is the **surface-line traded-form net-of-cost OOS verdict (EVAL-184)**, enforced by `scripts/eval184_phaseb_gate.py`. The capture must be freshly acquired (~1 h); the runner must be built and green; the gate must reach `SEALED`. Do not invent a substitute predictiveness rung (none remains unsealed). Do not declare completion on green-driver + all-sealed alone. Do not refresh this timestamp without new verified facts (a sealed EVAL-184 artifact).

## VERIFIED STATE (2026-11-22T06:59:10Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2430`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..183 are sealed (EVAL-63 never sealed). EVAL-67/68/69 are sealed **COMBINED** (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`). **All gates `ok`/phase `SEALED`; driver exit 0; idempotent no-op; verified this session (2430/2430 targeted, 27/27 diagnostics, `failures: []`, all EVAL-70..183 + EVAL-67/68/69 gates SEALED, 120/120 seal gates ok).**

- **EVAL-67 sealed COMBINED `GO CONFIRMED`** (`EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_20261122T053156Z.json/.md` + preregistration). Best IC 0.0962 (`imbalance::bar60.0::h72`), BH-FDR rejected. Capture dir (at acquisition) `data/raw/eval84cap` — **now absent from this checkout; must be re-acquired for EVAL-184.**
- **EVAL-68 sealed COMBINED `GO CONFIRMED`** (`EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_20261122T053327Z.json/.md` + prereg). Max pooled pairs 1856, BH-FDR rejected `imbalance::bar60.0::h72`.
- **EVAL-69 sealed COMBINED `NO-GO CONFIRMED (PASS)`** (`EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_20261122T053616Z.json/.md` + prereg). Floor OK, disjointness OK, power adequate (1998 pooled returns), but **0 BH-FDR rejections** (pooled Sharpe 0.19–0.20 for tox/imbalance bar60, perm_p 0.59–0.60, CI95 spans 0). The order-flow toxicity→realized-vol slice is **predictive but not tradeable net-of-cost**.
- `data/raw/eval84cap` (when present) is gitignored and must stay LOCAL — never commit/push. `data/raw/eval61|eval67|eval68` are git-tracked read-only inputs.
- EVAL-180/181/182/183 sealed (cross-asset order-flow × atm_iv interaction cells, all `NO-GO CONFIRMED (PASS)`). EVAL-177 (skew → forward variance, GO) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO) remain the surviving surface-line GOs.
- **NEW this session:** `scripts/eval184_phaseb_gate.py` added (append-only, touches no sealed artifact/src) and **`scripts/eval184_surface_traded_netofcost_oos.py` built + prereg + 13 tests (all pass)**. The gate reports `WAIT_CAPTURE` (exit 10) because `data/raw/eval84cap` is absent — correct pre-acquisition state, not a failure — but **`runner_green: true`** and **`prereg_present: true`**, so once the capture lands the gate proceeds `WAIT_CAPTURE → DUE → SEALED` via `--execute`. Prereg: `EVAL_184_SURFACE_TRADED_NETFCOST_OOS_PREREGISTRATION_20261122T065050Z.{json,md}`. No sealed EVAL artifact or `src/` modified.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder (incl. traded-form EVAL-69) | EVAL-67/68/69 | **SEALED COMBINED** — EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)` (predictive but not tradeable net-of-cost); floor OK both underlyings, disjointness OK (`20261122T...`) |
| Physics-independent predictiveness EVAL-70..160 | 91 rungs | SEALED |
| Single-asset surface → forward CVaR | EVAL-161/162/163/164 | SEALED (163 GO CONFIRMED; others NO-GO CONFIRMED (PASS)) |
| Single-asset surface → forward downside-semivariance share | EVAL-115 (atm_iv), 165 (skew), 166 (term_ratio), 167 (term_slope) | SEALED |
| Cross-asset surface/term → forward signed return mean | EVAL-148 (4 cells) | SEALED COMPLETE |
| Cross-asset options order-flow → forward signed return mean / skewness / downside / kurtosis / variance | EVAL-149..160 | SEALED COMPLETE |
| Cross-asset surface/term → forward CVaR | EVAL-168 (atm_iv), 169 (term_slope), 170 (term_ratio), 171 (skew) | SEALED |
| Single-asset surface → forward variance | EVAL-172 (atm_iv), 173 (skew), 174 (term_slope), 175 (term_ratio) | SEALED (grid COMPLETE) |
| Cross-asset surface → forward variance | EVAL-176 (atm_iv), 177 (skew), 178 (term_slope), 179 (term_ratio) | SEALED COMPLETE (176 NO-GO; 177 GO; 178/179 NO-GO) |
| Cross-asset order-flow × surface interaction → forward variance | EVAL-180 (imbalance × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T011312Z`) |
| Cross-asset order-flow × surface interaction → forward CVaR | EVAL-181 (imbalance × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T012720Z`) |
| Cross-asset order-flow **toxicity** × atm_iv interaction → forward variance | EVAL-182 (tox × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T020547Z`) |
| Cross-asset order-flow **toxicity** × atm_iv interaction → forward CVaR | EVAL-183 (tox × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T025328Z`) |
| **Surface-line traded-form net-of-cost OOS (EVAL-184)** | **skew/atm_iv/term_slope** | **NEXT — gate built (`eval184_phaseb_gate.py`), currently `WAIT_CAPTURE`; heavy work = acquire + build runner + seal** |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — surface-line traded-form net-of-cost OOS (EVAL-184, the next heavy work)

All predictiveness rungs EVAL-02..183 are sealed. EVAL-67/68 are GO (order-flow toxicity→RV is predictive OOS), but EVAL-69 (traded-form net-of-cost monetization of that same order-flow slice) is `NO-GO CONFIRMED (PASS)`. The surviving tradeable alpha is exclusively on the **surface** line (EVAL-177 skew→variance GO; EVAL-168/169 atm_iv/term_slope→CVaR GO). The next on-charter heavy work is the **surface-line traded-form net-of-cost OOS test (EVAL-184)** — the EVAL-69 analogue for the surface alpha — enforced by `scripts/eval184_phaseb_gate.py`.

1. **Env + driver green check (every session):** `./scripts/verify_env.sh` then `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2430/2430 targeted, 27/27 diagnostics, `failures: []`, all EVAL-70..183 + EVAL-67/68/69 gates SEALED, all 120 seal_gates ok).
2. **EVAL-184 gate:** `python3 scripts/eval184_phaseb_gate.py`. Read the phase. Currently `WAIT_CAPTURE` (no `eval84cap` on disk). The phase output contains the exact next action; do NOT skip to sealing.
3. **Acquire the disjoint floor-compliant capture (~1 h, in-session):** BTC landed at `data/raw/eval84cap/three_way_BTC_20261122T064658Z.json` (154 MB); ETH capture in flight (`bgp_2022d5e33002YpMR2UPctz4LNW`, pid 7352, `--underlying ETH --days 3.7 --end 2026-11-22T06:46:43Z --max-per-expiry 30 --out-dir data/raw/eval84cap --seal`, ~55 min wall). Do NOT re-start BTC. Once ETH lands, verify the EVAL-64 floor on both underlyings (REPRO step 3). Never weaken the floor; under-floor ⇒ `BLOCKED`, never NO-GO. Keep `eval84cap` LOCAL (gitignored).
4. **Build the surface-line traded-form runner (the heavy computation, in-session, NOT data-blocked):** implement `scripts/eval184_surface_traded_netofcost_oos.py` — the EVAL-69 analogue for the surface signals `skew` (EVAL-177, e71 surface bar) → forward variance; `atm_iv` (EVAL-168, e71 surface bar) and `term_slope` (EVAL-169, e74 term bar) → forward CVaR — at the GO-producing bar horizons. Reuse the sealed EVAL-69 mark-path/cost helpers (`e62.markpath_returns`, `e62.build_states`) and EVAL-64 feasible floor verbatim; pre-register mark-path net-of-cost P&L + Sharpe / max-DD / permutation / block-bootstrap / pooled BH-FDR; both-asset GO bar; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`. Add prereg + tests (append-only; grep for hyphen/underscore/hyphenated task-label traps; grep for stale signal/target ids).
5. **Seal:** `python3 scripts/eval184_phaseb_gate.py --execute`. Require `SEALED` (exit 0) and a passing `check_session_sealed.py` seal-gate. Then (optionally, append-only) reconcile `GATE_SPECS`/`SEAL_SPECS`/`EXPECTED_TARGETED_TESTS` in the driver. Do not edit sealed artifacts or `src/`.
6. **Do NOT re-run / re-litigate the sealed EVAL-67/68/69 or EVAL-70..183 artifacts.** EVAL-184 produces NEW artifacts.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) as **COMBINED** (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`) — floor OK both underlyings, disjointness OK. EVAL-70..183 gates: `SEALED`(0) idempotent no-op. `FAILED`(1) fix and rerun.
- Green driver = env OK, `2430/2430` targeted, `27/27` diagnostics, all `EVAL-70..183` + `EVAL-67/68/69` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-183 (and EVAL-67/68/69) is completion ONLY for the **predictiveness + order-flow-traded-form lines**; it is **NOT** session completion — the remaining on-charter work is the **surface-line traded-form net-of-cost OOS verdict (EVAL-184)**, enforced by `scripts/eval184_phaseb_gate.py`.
- EVAL-184 completion = `python3 scripts/eval184_phaseb_gate.py` exits `SEALED`(0) with a COMBINED/BLOCKED artifact stamp ≥ `20261122T063000Z` and a passing `check_session_sealed.py` seal-gate. The gate will not seal without: (a) a floor-compliant disjoint capture at `data/raw/eval84cap`, (b) a green `scripts/eval184_surface_traded_netofcost_oos.py --no-write`, (c) a successful `--seal` run. Under-floor/non-disjoint ⇒ `BLOCKED`, never NO-GO.
- The terminal deliverable (tradeable net-of-cost strategy) is currently `NO-GO CONFIRMED (PASS)` for the order-flow line (EVAL-69). The surface-line traded-form verdict (EVAL-184) is the next candidate deliverable.
- Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow toxicity via `e62.build_states(tox_signal="tox")`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- Multi-day acquisition timing (measured) — the 3.7-day floor-compliant capture with `--max-per-expiry 30` takes ~55 min wall-clock (network-bound, ~8–9 KB/s Deribit pagination across ~200 instruments/underlying × 2 legs + OKX history-trades). It IS runnable in-session and is NOT "wait days" data-blocked. Do not reduce `--days` below 3.7 (the floor needs the span).
- **"Capture is already on disk" is FALSE in a fresh checkout** — `data/raw/eval84cap` is gitignored and absent; the heavy work requires a fresh ~1 h acquisition first. Do not claim the capture exists without `ls data/raw/eval84cap/three_way_*.json`. Do not wait days; acquire in-session.
- **"No runnable-now predictiveness rung" avoidance** — all predictiveness rungs through EVAL-183 are sealed, and the order-flow traded-form verdict (EVAL-69) is sealed NO-GO CONFIRMED (PASS). The genuinely-next heavy work is the **surface-line traded-form net-of-cost OOS verdict (EVAL-184)**, enforced by `scripts/eval184_phaseb_gate.py`. This is the mandated heavy work. Do not invent a substitute rung.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..183 artifacts or `src/`. Append-only for new authorized work. The sealed EVAL-67/68/69 artifacts (both the old **BLOCKED** `20261120T...` and the new **COMBINED** `20261122T...`) are historical seals — do not edit them; EVAL-184 produces NEW artifacts (append-only).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-184 consumes the freshly-acquired disjoint capture (acquire nothing during the compute phase).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs (`INIT-2026-11-22T06:30:00Z-EVAL184-SURFACE-TRADED-NETOFCOST-OOS`); do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. `data/raw/eval84cap` (~300 MB) is gitignored and must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement, e.g. a sealed EVAL-184 artifact). Do not refresh this timestamp without a sealed EVAL-184.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. All EVAL-183 + EVAL-67/68/69 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2430/2430, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 + EVAL-67/68/69 gates SEALED/ok, all 120 seal_gates ok. EXPECTED_TARGETED_TESTS=2430.

# 1b) EVAL-184 anti-avoidance gate (the next heavy work arbiter):
python3 scripts/eval184_phaseb_gate.py
#    Currently WAIT_CAPTURE (exit 10) because data/raw/eval84cap is absent. The phase output
#    contains the exact next action. Do NOT skip to sealing. Re-run with --execute ONLY when DUE.

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 SEALED, exit 0
python3 scripts/eval176_phaseb_gate.py   # EVAL-176 SEALED, exit 0
python3 scripts/eval177_phaseb_gate.py   # EVAL-177 SEALED, exit 0
python3 scripts/eval178_phaseb_gate.py   # EVAL-178 SEALED, exit 0
python3 scripts/eval179_phaseb_gate.py   # EVAL-179 SEALED, exit 0
python3 scripts/eval180_phaseb_gate.py   # EVAL-180 SEALED, exit 0
python3 scripts/eval181_phaseb_gate.py   # EVAL-181 SEALED, exit 0
python3 scripts/eval182_phaseb_gate.py   # EVAL-182 SEALED, exit 0
python3 scripts/eval183_phaseb_gate.py   # EVAL-183 SEALED, exit 0
python3 scripts/eval67_phaseb_gate.py    # EVAL-67 SEALED (COMBINED GO), exit 0
python3 scripts/eval68_phaseb_gate.py    # EVAL-68 SEALED (COMBINED GO), exit 0
python3 scripts/eval69_phaseb_gate.py    # EVAL-69 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0

# 3) EVAL-64 feasible-floor probe across all on-disk captures (slow: large JSON):
PYTHONPATH=$PWD/.venv-deps python3 - <<'PY'
import json, glob, os, sys; sys.path.insert(0, ".")
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
for f in sorted(glob.glob("data/raw/eval*/three_way_*.json")):
    r = e64._underlying_floor_strict(json.load(open(f)))
    failed = [k for k,v in r["checks"].items() if not v]
    print(os.path.basename(f), "ok=", r["ok"], "FAILED=", failed)
PY

# 4) MANDATED HEAVY WORK — EVAL-184 surface-line traded-form net-of-cost OOS (enforced by the gate):
#    (a) Acquire the floor-compliant disjoint capture (~1 h, in-session, gitignored, keep LOCAL):
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 \
  --end <at/after 2026-11-19T18:08:16Z> --max-per-expiry 30 --out-dir data/raw/eval84cap --seal
#    (b) Verify the EVAL-64 floor on both underlyings (step 3). Under-floor => BLOCKED, never NO-GO.
#    (c) Build scripts/eval184_surface_traded_netofcost_oos.py (EVAL-69 analogue for skew/atm_iv/
#        term_slope at EVAL-177/168/169 GO horizons; reuse EVAL-69 mark-path/cost helpers verbatim;
#        pooled BH-FDR; both-asset GO bar) + prereg + tests. Make --no-write green.
#    (d) Seal: python3 scripts/eval184_phaseb_gate.py --execute  => require SEALED (exit 0).
#    Then (optionally, append-only) reconcile GATE_SPECS/SEAL_SPECS/EXPECTED_TARGETED_TESTS in the driver.

# 5) Anti-avoidance: green driver + all-sealed through EVAL-183 (and EVAL-67/68/69) is completion ONLY
#    for the predictiveness + order-flow-traded-form lines. Remaining on-charter work = EVAL-184
#    surface-line traded-form net-of-cost OOS verdict, enforced by scripts/eval184_phaseb_gate.py.
#    The gate will not seal without a real capture + a green runner. Do not fake it.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..183 sealed. **EVAL-63 never sealed.** EVAL-67/68/69 are sealed **COMBINED**: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK, on the floor-compliant disjoint capture acquired at `data/raw/eval84cap` (window 2026-11-18T11:35:59Z..2026-11-22T04:23:59Z; **capture now absent from this checkout and must be re-acquired for EVAL-184**). The order-flow toxicity→realized-vol slice is **predictive but not tradeable net-of-cost**. The surviving tradeable alpha is exclusively on the **surface** line: EVAL-177 (skew → forward variance, GO CONFIRMED) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO CONFIRMED). EVAL-183 (cross-asset order-flow toxicity × atm_iv interaction → forward CVaR, `NO-GO CONFIRMED (PASS)`, `20261122T025328Z`) is the latest sealed cross-asset interaction rung. **The next on-charter heavy work is the surface-line traded-form net-of-cost OOS verdict (EVAL-184), enforced by `scripts/eval184_phaseb_gate.py`.**