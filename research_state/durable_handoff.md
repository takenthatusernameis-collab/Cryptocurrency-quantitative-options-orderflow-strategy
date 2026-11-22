# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T04:08:19Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The predictiveness rungs EVAL-02..183 are all sealed. The order-flow × surface interaction cells are uniformly NO-GO CONFIRMED (PASS). The single-asset and cross-asset surface/term distributional grids are complete. The only surviving directional/tail alpha is on the **surface** line (EVAL-177 skew → variance GO; EVAL-168/169 atm_iv/term_slope → CVaR GO).
>
> **BOTTLENECK REMOVED — the prior "wait ~3.7 days" framing was WRONG and is RETIRED.** EVAL-67/68/69 (forward disjoint-window OOS, including the traded-form monetization EVAL-69) are sealed **`BLOCKED` (measured)** — NOT "threshold PASSED." Verified from the artifacts (`research_state/EVAL_67_..._BLOCKED_20261120T005220Z.json`, `EVAL_68_..._BLOCKED_20261120T014819Z.json`, `EVAL_69_..._BLOCKED_20261120T015619Z.json`): `disjointness_ok=true` (window 2026-11-16T08:04:50Z..2026-11-20T00:52:50Z, 0 s overlap with the sealed 2026-11-09..16 window) but `floor_ok=false` on `of_instruments_ok` (BTC 101, ETH 93 traded instruments; floor=150) and ETH `trades_ok` (1895 < 2000). **The blocker was the acquisition default `--max-per-expiry 12`, not Deribit retention and not elapsed time.** Live Deribit probe (2026-11-22T04:06Z): BTC 514 option strikes / ETH 448 strikes across 7 expiries within 45 d; default 12 strikes/expiry selects ~84 instruments ⇒ only ~96–101 ever trade in a 24 h window ⇒ permanently below the 150 floor. Waiting adds no distinct traded instruments (Deribit tick-trade retention is ~24 h regardless). **Fix = re-capture with elevated `--max-per-expiry` (e.g. 30 ⇒ ~210 selected instruments) so the floor is MET without weakening it, then run the forward OOS verdicts.**
>
> **CURRENT MANDATED QUEUE (the only remaining on-charter work — real in-session heavy work, NOT data-blocked):**
> 1. Fresh **floor-compliant disjoint** three-way capture with elevated strike selection:
>    `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --max-per-expiry 30 --out-dir data/raw/eval84cap`
>    (keep `data/raw/eval84cap` LOCAL, never commit; `--days 3.7` with `--end` ≥ now is auto-disjoint from the sealed 2026-11-09..16 window).
> 2. **Floor gate before any verdict:** run the EVAL-64 strict probe on the new dir; require `ok=True` for BOTH BTC and ETH (`of_instruments ≥ 150`, `trades ≥ 2000`, `snapshots ≥ 1000`, `surface_bars ≥ 1000`, `common ≥ 240`). If still under floor, raise `--max-per-expiry` further (40/50) and re-capture — do NOT weaken the floor, do NOT emit NO-GO on under-floor data.
> 3. **Forward OOS verdicts (the terminal deliverable):** run EVAL-67 (BTC), EVAL-68 (pooled BTC+ETH), EVAL-69 (pooled traded-form net-of-cost monetization) against `data/raw/eval84cap` via their `--capture-dir`/`--capture-dir` runners. EVAL-69 is the actual repo deliverable (tradeable, net-of-cost). Each emits GO / NO-GO CONFIRMED (PASS) / BLOCKED per its sealed prereg GO bar. Seal with the driver (`SEAL_SPECS`/`GATE_SPECS`), reconcile `EXPECTED_TARGETED_TESTS`.
> 4. Do **not** re-run / re-litigate the sealed BLOCKED EVAL-67/68/69 artifacts — they stay as historical BLOCKED seals; the new runs produce NEW artifacts against the floor-compliant capture.
>
> **NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute):** green driver every session is the per-session gate; `green driver + all-sealed through EVAL-183 is NOT completion`. The mandated heavy work is the floor-compliant capture → EVAL-67/68/69 forward OOS verdicts above. This is runnable in-session (capture ~minutes, verdicts ~minutes) and is NOT data-blocked. Do not invent a substitute predictiveness rung (none remains unsealed); do not declare completion on green-driver + all-sealed alone.

## VERIFIED STATE (2026-11-22T04:06:51Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2430`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..183 are sealed (EVAL-63 never sealed). **All gates `ok`/phase `SEALED`; driver exit 0; idempotent no-op; verified this session (2430/2430 targeted, 27/27 diagnostics, `failures: []`).** **CORRECTION:** EVAL-67/68/69 are sealed **`BLOCKED` (measured)** — NOT "threshold PASSED." Verified artifacts: `disjointness_ok=true`, `floor_ok=false` on `of_instruments_ok` (BTC 101, ETH 93 traded instruments vs floor 150) and ETH `trades_ok` (1895 < 2000). Root cause = acquisition default `--max-per-expiry 12` (not Deribit retention, not elapsed time). Live Deribit probe 2026-11-22T04:06Z: BTC 514 / ETH 448 strikes across 7 expiries ≤45 d ⇒ `--max-per-expiry 30` clears the floor without weakening it.

- EVAL-180 sealed successfully: `research_state/EVAL_180_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261122T011312Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars). Best IC: BTC 0.1331 (`ETH->BTC::oflow_atm_iv_interaction::bar60.0::h6`), ETH 0.1326 (`BTC->ETH::oflow_atm_iv_interaction::bar300.0::h24`); 0 pass configs; 12 configs; no BH-FDR rejections. Cross-asset order-flow × surface interaction → forward variance cell complete.
- EVAL-181 sealed successfully: `research_state/EVAL_181_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR_COMBINED_20261122T012720Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars). Best IC: BTC -0.0163 (`ETH->BTC::oflow_atm_iv_interaction::bar300.0::h6`), ETH 0.0051 (`BTC->ETH::oflow_atm_iv_interaction::bar300.0::h6`); 0 pass configs; 12 configs; no BH-FDR rejections. Cross-asset order-flow imbalance × atm_iv interaction → forward CVaR cell complete.
- EVAL-182 sealed successfully: `research_state/EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261122T020547Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH; 12 configs; no BH-FDR rejections. Cross-asset order-flow **toxicity** × atm_iv interaction → forward variance cell complete. Signal path: `e62.build_states(tox_signal="tox")` × `e71.build_surface_bars().atm_iv`.
- EVAL-183 sealed successfully: `research_state/EVAL_183_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR_COMBINED_20261122T025328Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 toxicity states and 289 surface bars each; 274 aligned common bars); 12 configs; no BH-FDR rejections. Cross-asset order-flow **toxicity** × atm_iv interaction → forward CVaR cell complete. Signal path: `e62.build_states(tox_signal="tox")` × `e71.build_surface_bars().atm_iv`; target `_forward_cvar` via EVAL-168 (`CVAR_ALPHA` verbatim from EVAL-163/EVAL-168).
- EVAL-180/181/182/183 scripts/tests are new untracked files. Driver tables updated: `TARGETED_TEST_FILES` (+8 files vs EVAL-181 baseline, +72 tests → 2430), `GATE_SPECS` (+EVAL-182, +EVAL-183), `SEAL_SPECS` (+EVAL-182, +EVAL-183), `EXPECTED_TARGETED_TESTS=2430` reconciled via the full driver run. Duplicate EVAL-126 test-artifact churn remains untracked; do not commit it.
- No sealed EVAL artifact or `src/` modified. Only `scripts/eval67_prethreshold_progress.py` is modified (EVAL-182/183 wiring); EVAL-180/181/182/183 scripts/tests/artifacts are new.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder (incl. traded-form EVAL-69) | EVAL-67/68/69 | **SEALED `BLOCKED` (measured)** — floor-deficient (`of_instruments` 96–101 < 150; ETH trades 1895 < 2000), disjointness OK. Bottleneck removed: re-capture with `--max-per-expiry 30` → forward OOS verdicts pending (`20261120T...`) |
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

## PRE-REGISTERED BUILD QUEUE — EVAL-67/68/69 BLOCKED on floor → floor-compliant re-capture → forward OOS verdicts

All predictiveness rungs EVAL-02..183 are sealed; the order-flow × surface interaction cells are uniformly NO-GO and the surface-line GOs (EVAL-177 skew → variance; EVAL-168/169 atm_iv/term_slope → CVaR) are the surviving alpha. EVAL-67/68/69 are sealed **`BLOCKED` (measured)** on floor (not disjointness) — `disjointness_ok=true` but `floor_ok=false` (`of_instruments` ≈96–101 < 150; ETH trades 1895 < 2000). The blocker was the acquisition default `--max-per-expiry 12`, NOT a data wait and NOT Deribit retention. The terminal deliverable (EVAL-69 traded-form net-of-cost) is therefore **runnable now** with a floor-compliant re-capture — not data-blocked.

1. **Driver green check (every session):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2430/2430 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`). All EVAL-70..183 gates SEALED. (Verified green this session.)
2. **Floor-compliant re-capture (the heavy work, in-session, NOT data-blocked):** `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --max-per-expiry 30 --out-dir data/raw/eval84cap`. Keep `data/raw/eval84cap` LOCAL (never commit). Verify the EVAL-64 strict floor (`of_instruments ≥ 150`, `trades ≥ 2000`, `snapshots ≥ 1000`, `surface_bars ≥ 1000`, `common ≥ 240`) for BOTH BTC and ETH. If still under floor, raise `--max-per-expiry` (40/50) and re-capture — never weaken the floor.
3. **Forward OOS verdicts (the terminal deliverable):** EVAL-67 (BTC), EVAL-68 (pooled BTC+ETH), EVAL-69 (pooled traded-form net-of-cost monetization) against `data/raw/eval84cap` via their `--capture-dir` runners. EVAL-69 is the actual repo deliverable. Seal via the driver (`SEAL_SPECS`/`GATE_SPECS`), reconcile `EXPECTED_TARGETED_TESTS`. Do NOT re-run / re-litigate the sealed BLOCKED EVAL-67/68/69 artifacts — they stay as historical BLOCKED seals; the new runs produce NEW artifacts.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) as **`BLOCKED` (measured)** — floor-deficient, disjointness OK. EVAL-70..183 gates: `SEALED`(0) idempotent no-op. `FAILED`(1) fix and rerun.
- Green driver = env OK, `2430/2430` targeted, `27/27` diagnostics, all `EVAL-70..183` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-183 is completion for the **predictiveness ladder**; it is **NOT** session completion — the remaining on-charter work is the floor-compliant re-capture → EVAL-67/68/69 forward OOS verdicts (in-session heavy work, NOT data-blocked).
- The terminal deliverable is **EVAL-69 traded-form net-of-cost** (the repo's tradeable strategy). It is runnable now with a floor-compliant capture (`--max-per-expiry 30`), not data-blocked.
- Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
- Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-180/181/182/183 sealed; EVAL-67/68/69 sealed **BLOCKED** on floor; driver green at 2430/2430; bottleneck removed = `--max-per-expiry` was too low, NOT a data wait) and points at genuinely-next runnable work (floor-compliant re-capture → forward OOS verdicts). Do not refresh the timestamp without new verified facts.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (EVAL-183: 2412→2430).
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow toxicity via `e62.build_states(tox_signal="tox")`; EVAL-183 composes `e62.build_states(tox_signal="tox")` × `e71.build_surface_bars`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- **"Data-blocked" avoidance (corrected)** — EVAL-67/68/69 were sealed BLOCKED on `floor_ok=false` (under-provisioned `--max-per-expiry 12`), NOT on an unreachable data wait. The floor IS reachable now: live Deribit probe 2026-11-22T04:06Z shows 514 BTC / 448 ETH strikes across 7 expiries ≤45 d, so `--max-per-expiry 30` clears the 150-instrument floor. Do NOT declare completion on green-driver + all-sealed alone; the heavy work is the floor-compliant re-capture → EVAL-67/68/69 verdicts.
- Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`. The EVAL-126 gate unit test now monkeypatches `execute_phaseb`; do not reintroduce a real `main --execute` call with fake captures.
- Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor`/`campaign_floor` is actually CALLED.
- Multi-day acquisition is NOT the gate — the floor-compliant capture completes in-session (minutes); `--days 3.7` is a trailing window with `--end` ≥ now, auto-disjoint from the sealed window. Do not wait days.
- **"No runnable-now predictiveness rung" avoidance** — all predictiveness rungs through EVAL-183 are sealed, but the forward OOS traded-form verdict (EVAL-69) is NOT yet produced and IS runnable now with a floor-compliant capture. This is the mandated heavy work.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..183 artifacts or `src/`. Append-only for new authorized work. The sealed **BLOCKED** EVAL-67/68/69 artifacts are historical seals — do not edit them; the new floor-compliant runs against `data/raw/eval84cap` produce NEW artifacts (append-only).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..183 acquire nothing (consume on-disk `data/raw/eval61`).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint **past** window. The forward capture (`--end` ≥ now, auto-disjoint from the sealed 2026-11-09..16 window) is the correct path; a trailing capture ending before the sealed window clears would overlap and must seal BLOCKED.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. A NEW large capture dir (e.g. `data/raw/eval84cap`, ~100MB+) must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement).

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. All EVAL-183 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2430/2430, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2430.

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

# 3) EVAL-64 feasible-floor probe across all on-disk captures (slow: large JSON):
PYTHONPATH=$PWD/.venv-deps python3 - <<'PY'
import json, glob, os, sys; sys.path.insert(0, ".")
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
for f in sorted(glob.glob("data/raw/eval*/three_way_*.json")):
    r = e64._underlying_floor_strict(json.load(open(f)))
    failed = [k for k,v in r["checks"].items() if not v]
    print(os.path.basename(f), "ok=", r["ok"], "FAILED=", failed)
PY

# 4) MANDATED HEAVY WORK — floor-compliant re-capture (in-session, NOT data-blocked):
#    EVAL-67/68/69 sealed BLOCKED on floor (of_instruments 96-101 < 150; ETH trades 1895<2000).
#    Root cause = default --max-per-expiry 12. Live Deribit: BTC 514 / ETH 448 strikes <=45d.
#    Keep data/raw/eval84cap LOCAL (never commit). Then run EVAL-67/68/69 vs this dir.
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --max-per-expiry 30 --out-dir data/raw/eval84cap
#    floor gate (require ok=True for BOTH; if under floor raise --max-per-expiry 40/50 and re-capture):
#    (reuse the EVAL-64 strict probe below on data/raw/eval84cap)
python3 scripts/eval67_btc_oflow_tox_rv_oos.py --capture-dir data/raw/eval84cap --seal --task-label EVAL67-BTC-OFLOW-TOX-RV-OOS
python3 scripts/eval68_pooled_btc_eth_oflow_tox_rv_oos.py --capture-dir data/raw/eval84cap --seal --task-label EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS
python3 scripts/eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py --capture-dir data/raw/eval84cap --seal --task-label EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS
#    EVAL-69 is the repo deliverable (tradeable, net-of-cost). Seal via the driver, reconcile EXPECTED_TARGETED_TESTS.

# 5) Anti-avoidance: green driver + all-sealed through EVAL-183 is completion ONLY for the predictiveness ladder. Remaining on-charter work = floor-compliant re-capture -> EVAL-67/68/69 forward OOS verdicts (incl. EVAL-69 traded-form), runnable in-session.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..183 sealed. **EVAL-63 never sealed.** EVAL-67/68/69 are sealed **`BLOCKED` (measured)** on floor (not disjointness) — bottleneck removed, floor-compliant re-capture → forward OOS verdicts (incl. EVAL-69 traded-form, the repo deliverable) is the pending heavy work. EVAL-183 (cross-asset order-flow toxicity × atm_iv interaction → forward CVaR, `NO-GO CONFIRMED (PASS)`, `20261122T025328Z`) is the latest sealed predictiveness rung; EVAL-177 (skew → forward variance, GO CONFIRMED) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO CONFIRMED) remain the surviving surface-line GOs.
