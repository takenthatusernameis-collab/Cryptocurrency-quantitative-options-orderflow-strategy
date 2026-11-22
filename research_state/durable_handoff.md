# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T05:50:00Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The predictiveness rungs EVAL-02..183 are all sealed. The order-flow × surface interaction cells are uniformly NO-GO CONFIRMED (PASS). The single-asset and cross-asset surface/term distributional grids are complete. The only surviving directional/tail alpha is on the **surface** line (EVAL-177 skew → variance GO; EVAL-168/169 atm_iv/term_slope → CVaR GO).
>
> **DELIVERABLE STATUS (2026-11-22T05:50Z — EVAL-67/68/69 forward OOS ladder is NOW SEALED with real verdicts, NOT BLOCKED):** this session completed the previously-pending heavy work. A fresh floor-compliant disjoint 3.7-day three-way capture was acquired (`data/raw/eval84cap`, window `2026-11-18T11:35:59Z..2026-11-22T04:23:59Z`, 0 s overlap with the sealed 2026-11-09..16 window) with `--max-per-expiry 30`, clearing the EVAL-64 floor for BOTH BTC and ETH without weakening it (BTC: 8489 option trades, 227 traded OF instruments, 1066 snapshots; ETH: 6055 trades, 199 instruments, 1066 snapshots; both `ok=True` on every floor check). The three forward OOS verdicts are sealed:
> - **EVAL-67 (BTC predictiveness): `GO CONFIRMED`** (`EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_20261122T053156Z`). Best IC 0.0962 (`imbalance::bar60.0::h72`), 1 pass config, BH-FDR rejected. Floor OK, disjointness OK.
> - **EVAL-68 (pooled BTC+ETH predictiveness): `GO CONFIRMED`** (`EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_20261122T053327Z`). Max pooled pairs 1856 (≥790; power adequate), BH-FDR rejected `imbalance::bar60.0::h72`. Floor OK, disjointness OK.
> - **EVAL-69 (pooled traded-form net-of-cost monetization — THE REPO DELIVERABLE): `NO-GO CONFIRMED (PASS)`** (`EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_20261122T053616Z`). Floor OK, disjointness OK, power adequate (1998 pooled returns), but **0 BH-FDR rejections** — pooled Sharpe 0.19–0.20 (tox/imbalance bar60), perm_p 0.59–0.60, CI95 spans 0. The order-flow toxicity→realized-vol slice is **predictive but does NOT survive traded-form net-of-cost**. This is the legitimate terminal verdict for the options-order-flow line.
>
> **WHAT THIS MEANS (anti-substitution, load-bearing):** the options **order-flow** half is now fully resolved: predictive (EVAL-67/68 GO) but not tradeable net-of-cost (EVAL-69 NO-GO CONFIRMED (PASS)). The surviving tradeable alpha is exclusively on the **surface** line (EVAL-177 skew→variance GO; EVAL-168/169 atm_iv/term_slope→CVaR GO). **The next on-charter heavy work is therefore the traded-form net-of-cost OOS test of the surface-line GOs — the EVAL-69 analogue for the surface alpha.** Do NOT re-run or re-litigate EVAL-67/68/69 (all sealed, append-only). Do NOT declare completion on green-driver alone.
>
> **CURRENT MANDATED QUEUE (the only remaining on-charter work — real in-session heavy work, NOT data-blocked):**
> 1. **Driver green check (every session):** `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2430/2430 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`, all EVAL-70..183 + EVAL-67/68/69 gates SEALED, all 120 seal_gates ok). Verified green this session at 2430/2430, 27/27, 120/120 seal gates ok.
> 2. **Traded-form net-of-cost OOS test of the surface-line GOs (the heavy work):** build a new forward OOS runner analogous to EVAL-69 but for the surface-line surviving alpha — EVAL-177 (skew → forward variance, GO) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO). The capture `data/raw/eval84cap` is already on disk and floor-compliant (BTC+ETH, disjoint, 3.7d). Pre-register a traded-form monetization (mark-path net-of-cost P&L, Sharpe / max-DD / permutation / bootstrap, pooled BH-FDR) for the surface signals (`skew`, `atm_iv`, `term_slope`) at the bar horizons that produced the GOs, on the SAME disjoint forward capture. This is the EVAL-69 analogue for the surface line and the genuinely-next runnable heavy work. Keep `data/raw/eval84cap` LOCAL (never commit).
> 3. **Seal via the driver** (`GATE_SPECS`/`SEAL_SPECS`), reconcile `EXPECTED_TARGETED_TESTS`. The new runner/gate/tests are NEW files; append-only. Do not edit sealed artifacts or `src/`.
> 4. **Do NOT re-run / re-litigate the sealed EVAL-67/68/69 artifacts** — they stay as historical seals (EVAL-67/68 COMBINED GO + old BLOCKED; EVAL-69 COMBINED NO-GO + old BLOCKED). The new surface-line traded-form runner produces NEW artifacts (e.g. EVAL-184+).
>
> **NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute):** green driver every session is the per-session gate; `green driver + all-sealed through EVAL-183 (and EVAL-67/68/69) is NOT completion`. The mandated heavy work is the **surface-line traded-form net-of-cost OOS verdict** (the EVAL-69 analogue for EVAL-177/168/169). This is runnable in-session on the already-on-disk `data/raw/eval84cap` and is NOT data-blocked. Do not invent a substitute predictiveness rung (none remains unsealed); do not declare completion on green-driver + all-sealed alone.

## VERIFIED STATE (2026-11-22T05:49:08Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2430`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..183 are sealed (EVAL-63 never sealed). EVAL-67/68/69 are now sealed **COMBINED** (real verdicts, not BLOCKED). **All gates `ok`/phase `SEALED`; driver exit 0; idempotent no-op; verified this session (2430/2430 targeted, 27/27 diagnostics, 120/120 seal gates ok, `failures: []`, `gate_exit=0`, EVAL-67/68/69 phase SEALED exit 0).**

- **EVAL-67 sealed COMBINED `GO CONFIRMED`** (`EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_20261122T053156Z.json/.md` + preregistration). Floor OK, disjointness OK (window 2026-11-18T11:35:59Z..2026-11-22T04:23:59Z, 0 s overlap). Best IC 0.0962 (`imbalance::bar60.0::h72`), 1 pass config, BH-FDR rejected. Capture dir `data/raw/eval84cap`.
- **EVAL-68 sealed COMBINED `GO CONFIRMED`** (`EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_20261122T053327Z.json/.md` + preregistration). Floor OK, disjointness OK, max pooled pairs 1856 (≥790; power adequate), BH-FDR rejected `imbalance::bar60.0::h72`. Capture dir `data/raw/eval84cap`.
- **EVAL-69 sealed COMBINED `NO-GO CONFIRMED (PASS)`** (`EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_20261122T053616Z.json/.md` + preregistration). Floor OK, disjointness OK, power adequate (1998 pooled returns, min 790), but **0 BH-FDR rejections** (pooled Sharpe 0.19–0.20 for tox/imbalance bar60, perm_p 0.59–0.60, CI95 spans 0). The repo deliverable (traded-form net-of-cost monetization of the options order-flow toxicity→realized-vol slice) is **NO-GO CONFIRMED (PASS)** — predictive but not tradeable net-of-cost. Capture dir `data/raw/eval84cap`.
- `data/raw/eval84cap` is gitignored (added to `.gitignore`) and must stay LOCAL — never commit/push (~300 MB, both underlyings).
- The sealed **BLOCKED** EVAL-67/68/69 artifacts (`20261120T...`) remain as historical seals (append-only); the new COMBINED artifacts are the live verdicts.
- EVAL-180/181/182/183 sealed (cross-asset order-flow × atm_iv interaction cells, all `NO-GO CONFIRMED (PASS)`). EVAL-177 (skew → forward variance, GO) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO) remain the surviving surface-line GOs.
- No sealed EVAL artifact or `src/` modified. Only `.gitignore` modified (eval84cap ignore rule) and new EVAL-67/68/69 COMBINED/preregistration artifacts added.

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

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — surface-line traded-form net-of-cost OOS (the next heavy work)

All predictiveness rungs EVAL-02..183 are sealed. EVAL-67/68 are GO (order-flow toxicity→RV is predictive OOS), but EVAL-69 (traded-form net-of-cost monetization of that same order-flow slice) is `NO-GO CONFIRMED (PASS)` — predictive but not tradeable net-of-cost. The surviving tradeable alpha is exclusively on the **surface** line (EVAL-177 skew→variance GO; EVAL-168/169 atm_iv/term_slope→CVaR GO). The next on-charter heavy work is the **traded-form net-of-cost OOS test of the surface-line GOs** — the EVAL-69 analogue for the surface alpha — on the already-on-disk floor-compliant disjoint capture `data/raw/eval84cap`.

1. **Driver green check (every session):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2430/2430 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`, all EVAL-70..183 + EVAL-67/68/69 gates SEALED, all 120 seal_gates ok). (Verified green this session.)
2. **Surface-line traded-form OOS runner (the heavy work, in-session, NOT data-blocked):** build a new forward OOS runner analogous to EVAL-69 (`scripts/eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py`) but for the surface signals — `skew` (EVAL-177), `atm_iv`/`term_slope` (EVAL-168/169) — at the bar horizons that produced the GOs. Pre-register the traded-form monetization (mark-path net-of-cost P&L, Sharpe / max-DD / permutation / bootstrap, pooled BH-FDR) and run it against `data/raw/eval84cap` (already floor-compliant, disjoint, 3.7d). Reuse the sealed EVAL-69 mark-path/cost helpers verbatim; do not weaken the floor; do not relax the GO bar (both BTC and ETH must pass for GO; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`).
3. **Seal via the driver** (`GATE_SPECS`/`SEAL_SPECS`), reconcile `EXPECTED_TARGETED_TESTS` with `pytest --collect-only`. The new runner/gate/tests are NEW files (e.g. EVAL-184+); append-only. Do not edit sealed artifacts or `src/`.
4. **Do NOT re-run / re-litigate the sealed EVAL-67/68/69 artifacts** — they stay as historical seals (COMBINED GO + old BLOCKED; EVAL-69 COMBINED NO-GO + old BLOCKED). The new surface-line traded-form runner produces NEW artifacts.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) as **COMBINED** (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`) — floor OK both underlyings, disjointness OK. EVAL-70..183 gates: `SEALED`(0) idempotent no-op. `FAILED`(1) fix and rerun.
- Green driver = env OK, `2430/2430` targeted, `27/27` diagnostics, all `EVAL-70..183` + `EVAL-67/68/69` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-183 (and EVAL-67/68/69) is completion for the **predictiveness + order-flow-traded-form lines**; it is **NOT** session completion — the remaining on-charter work is the **surface-line traded-form net-of-cost OOS verdict** (the EVAL-69 analogue for EVAL-177/168/169), runnable in-session on `data/raw/eval84cap`.
- The terminal deliverable (tradeable net-of-cost strategy) is currently `NO-GO CONFIRMED (PASS)` for the order-flow line (EVAL-69). The surface-line traded-form verdict (EVAL-177/168/169 analogue) is the next candidate deliverable.
- Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
- Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-67/68 COMBINED GO; EVAL-69 COMBINED NO-GO CONFIRMED (PASS); driver green at 2430/2430, 120/120 seal gates; capture `data/raw/eval84cap` floor-compliant and gitignored) and points at genuinely-next runnable work (surface-line traded-form net-of-cost OOS verdict). Do not refresh the timestamp without new verified facts.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow toxicity via `e62.build_states(tox_signal="tox")`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- **Multi-day acquisition timing (measured, corrected)** — the 3.7-day floor-compliant capture with `--max-per-expiry 30` took ~55 min wall-clock (network-bound, ~8–9 KB/s Deribit pagination across ~200 instruments/underlying × 2 legs + OKX history-trades). It is NOT "minutes" — budget ~1 h for the capture. But it IS runnable in-session and is NOT data-blocked. Do not wait days; do not reduce `--days` below 3.7 (the floor needs the span).
- **"No runnable-now predictiveness rung" avoidance** — all predictiveness rungs through EVAL-183 are sealed, and the order-flow traded-form verdict (EVAL-69) is now sealed NO-GO CONFIRMED (PASS). The genuinely-next heavy work is the **surface-line traded-form net-of-cost OOS verdict** (EVAL-177/168/169 analogue), runnable in-session on `data/raw/eval84cap`. This is the mandated heavy work.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..183 artifacts or `src/`. Append-only for new authorized work. The sealed EVAL-67/68/69 artifacts (both the old **BLOCKED** `20261120T...` and the new **COMBINED** `20261122T...`) are historical seals — do not edit them; new surface-line runs produce NEW artifacts (append-only).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..183 acquire nothing (consume on-disk `data/raw/eval61`).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. `data/raw/eval84cap` (~300 MB) is gitignored and must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement).

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. All EVAL-183 + EVAL-67/68/69 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2430/2430, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 + EVAL-67/68/69 gates SEALED/ok, all 120 seal_gates ok. EXPECTED_TARGETED_TESTS=2430.

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

# 4) MANDATED HEAVY WORK — surface-line traded-form net-of-cost OOS (the next heavy work):
#    EVAL-67/68 GO (predictive) but EVAL-69 NO-GO (not tradeable net-of-cost) for the order-flow line.
#    Surviving tradeable alpha = surface line (EVAL-177 skew->variance GO; EVAL-168/169 atm_iv/term_slope->CVaR GO).
#    Build a new forward OOS runner (EVAL-69 analogue) for the surface signals on data/raw/eval84cap
#    (already floor-compliant, disjoint, 3.7d; gitignored, keep LOCAL). Pre-register mark-path net-of-cost
#    monetization (Sharpe / max-DD / permutation / bootstrap, pooled BH-FDR). Seal via the driver.
#    Reuse EVAL-69 mark-path/cost helpers verbatim; do not weaken the floor or relax the GO bar.

# 5) Anti-avoidance: green driver + all-sealed through EVAL-183 (and EVAL-67/68/69) is completion ONLY
#    for the predictiveness + order-flow-traded-form lines. Remaining on-charter work = surface-line
#    traded-form net-of-cost OOS verdict (EVAL-177/168/169 analogue), runnable in-session on eval84cap.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..183 sealed. **EVAL-63 never sealed.** EVAL-67/68/69 are sealed **COMBINED**: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK, on the fresh floor-compliant disjoint capture `data/raw/eval84cap` (window 2026-11-18T11:35:59Z..2026-11-22T04:23:59Z). The order-flow toxicity→realized-vol slice is **predictive but not tradeable net-of-cost**. The surviving tradeable alpha is exclusively on the **surface** line: EVAL-177 (skew → forward variance, GO CONFIRMED) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO CONFIRMED). EVAL-183 (cross-asset order-flow toxicity × atm_iv interaction → forward CVaR, `NO-GO CONFIRMED (PASS)`, `20261122T025328Z`) is the latest sealed cross-asset interaction rung. The next on-charter heavy work is the surface-line traded-form net-of-cost OOS verdict (the EVAL-69 analogue for EVAL-177/168/169).