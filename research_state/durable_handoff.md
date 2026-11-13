# SINGLE DURABLE HANDOFF — READ FIRST

**Handoff refreshed:** 2026-11-13T21:40:24Z (UTC). Verified at HEAD `34a586130c392554eedb46c1d86942d0853d1381`, clean tree.
`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

**State (measured 2026-11-13T21:40Z):** EVAL-02..EVAL-21 **SEALED**. **EVAL-22 ACTIVE and UNSTARTED** — `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py`, `research_state/REAL_TAPE_INGESTION_*` all **absent** (verified by glob). `.env` **ABSENT** (paper-only) — verified. `data/raw/` contains **only synthetic**: `orderflow_btcusdt_synthetic.json` (SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`; 1000 trades / 20 liq / 8 funding; 2026-10-31T06:16:23.656379Z→07:16:21.656379Z; venue `synthetic`, symbol `BTCUSDT`; 240 bars / 239 returns / **3 windows**) and `options_btc_synthetic.json` (30 quotes; internally inconsistent, EVAL-16). No real tape. Regression baseline: `tests/test_sample_adequacy_acquisition.py` + `tests/test_measurement_validity_evaluation.py` = **45 passed in 134.07s** (re-measured 2026-11-13T21:38Z; the previous 84.56s claim is stale — budget **~150s**, 90s is too tight). Working tree clean.

**NEXT FOCUS CAMPAIGN:** **EVAL-22 → EVAL-23B → EVAL-23 → EVAL-24 → EVAL-25.** Never idle; each session ships a module + tests + artifact.

---

## INITIAL TASK MESSAGE — 2026-11-13T21:40:24Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-13T21:40:24Z-EVAL-22-REAL-TAPE-GATE`
**STATUS:** **ACTIVE, not started.** Start here — zero discovery needed.

> **Hard floor:** a session ending without new EVAL-22 artifacts (`src/analytics/real_tape_ingestion.py` + `tests/test_real_tape_ingestion.py` + `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}` + recorded verification evidence) is **FAILED**. Handoff-only work is FAILED. If no adequate real tape exists (it does not today), ship module+tests and seal an explicit **`NO-GO (no adequate real tape)`** artifact with measured shortfall + exact data contract (a legitimate seal), then set next active task to **EVAL-23B**.

### Environment setup (verified — do this first, ~60s)
Deps are **not preinstalled** in the runner image. `pip install` works:
```
python3 -m pip install --quiet numpy pandas scipy pytest pyyaml pydantic requests websocket-client python-dateutil
```
Verified working set (2026-11-13T21:40Z): Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3. `python3 -m py_compile` + targeted `pytest` are the only verification (no mypy/ruff/flake8 installed). **Never run the full suite (5297 tests).** Never enumerate `research_state/`.

### Do now (heavy work required)
1. **Implement `src/analytics/real_tape_ingestion.py`** — deterministic, offline, paper-only, **no exchange/network calls**.
   - `discover_real_orderflow_tapes(data_raw_dir=Path("data/raw")) -> List[Path]`: glob `orderflow_*.json`; **exclude** any name containing `synthetic`; deterministic `sorted()`. (Measured today: returns `['data/raw/orderflow_btcusdt_synthetic.json']` unfiltered, `[]` after excluding synthetic — so the filter is the whole point.)
   - `load_real_tape(path) -> dict`: `DataLoader(cache=False).load_orderflow(path, venue=<from filename>, symbol=<from filename>)` (`src/data/loader.py:103`); **reject** if venue/symbol empty, venue is synthetic, or content SHA-256 matches the canonical synthetic tape. Record path, venue, symbol, content SHA-256, span, n_trades, n_bars, n_returns, n_windows.
     - **Use `cache=False`** — `DataLoader.cache` defaults to `True` and would return a stale snapshot when a test rewrites the same path.
   - `validate_real_tape(...)`: adequacy (`n_returns >= 1000` **and** `n_windows >= 20`), causal no-lookahead, microstructure sanity (price > 0, size > 0, side ∈ {buy,sell}, timestamps monotone non-decreasing), symbol/venue consistency.
   - If adequate real tape found: drive the **same sealed EVAL-20 primitives** on the real snapshot following `sample_adequacy_acquisition.py:428` `evaluate_sample_adequacy` as the template — `build_pillar_signals` → `simulate_pillar` → `adequacy_report` → `ic_report` → `compute_verdict` → `pillar_metrics`. **Do NOT call `evaluate_measurement_validity()`** (no snapshot param; hardcodes synthetic). If none: emit `NO-GO (no adequate real tape)` with per-candidate counts and exact shortfall.
   - **Do NOT reuse `_assert_causal`** — proven vacuous (see Traps).
   - Never substitute synthetic for real; never emit `{"valid": true}`; strict JSON `allow_nan=False`.
2. **Write `tests/test_real_tape_ingestion.py`** with **10–16 numeric-invariant tests**: discovery excludes `*_synthetic.json` and includes real patterns; adequate real fixture → `data_provenance="real"`; inadequate real fixture → NO-GO with exact shortfall; malformed/empty/synthetic-venue rejected; causal no-lookahead (**time-truncation invariance**, not row-removal); **row-order invariance** (two permutations of the same tape → byte-identical artifact, using the canonical sort); microstructure rejects bad price/size/side/timestamps; adequacy counts match helpers; strict serialization/no `{"valid": true}`; determinism (two runs byte-identical); fingerprint changes on tape change; CLI writes `.json` and `.md`.
3. **CLI:** `python -m src.analytics.real_tape_ingestion --out research_state/ [--data-dir data/raw]` → `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}`.
4. **Run and record verification:**
   - `python3 -m py_compile src/analytics/real_tape_ingestion.py tests/test_real_tape_ingestion.py`
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py`
   - `python3 -m pytest -q tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py` → expect **45 passed** (~134s; allow 150s)
5. **Seal in place:** update this handoff with measured verdict/checks/evidence/artifact paths and set next active task (**EVAL-23B** if no adequate real tape — today's case; else **EVAL-23**). Commit partial work if incomplete — never leave a clean tree with EVAL-22 pending.

### EVAL-22 verdict contract (use sealed `compute_verdict` verbatim)
Call `compute_verdict(adequacy, sizing_consistent, sizing_detail, sharpe_ok, sharpe_detail, degeneracy, cost_detail, ic_detail, determinism_ok, never_valid_true)` → exactly 8 checks: `measurement_reproducible`, `sample_adequate_declared`, `sizing_consistent`, `sharpe_basis_valid`, `non_degenerate_pillars_reported`, `net_of_cost_honest`, `ic_reported_with_power`, `strict_serialization`. The **only** in-repo call site is `measurement_validity_evaluation.py:945` — copy that wiring verbatim (EVAL-21 at `sample_adequacy_acquisition.py:700` builds checks inline instead; either is acceptable, but `compute_verdict` is the sealed checker and is what the EVAL-20 tests assert on).
- `sample_adequate_declared`: `n_returns >= 1000` and `n_windows >= 20`. **Measured both-gates minimum: `n_bars = 1001` → 1000 returns and 22 windows** (at 15s bars). Emit both.
- `sizing_detail`: `requested_max_position_pct`, `risk_config_max_position_pct`, `rejections`, `max_drawdown_limit`, `sizing_consistent` (true iff `|enforced-requested| <= 1e-12` and `rejections == 0`). `config/settings.yaml` sets `risk.max_position_pct: 0.1` — pass it explicitly.
- `sharpe_detail`: `annualisation`, `expected_annualisation`, `sharpe`, `abs_error`; ok iff annualisation matches `periods_per_year(bar_duration_seconds)` and sharpe reproduces.
- `cost_detail`: `complete` and `non_negative` (all series carry `gross_return_total, net_return_total, turnover, total_cost_bps`, `total_cost_bps >= 0`).
- `ic_detail`: must contain `ic_mean` and `min_detectable_ic_at_n`. **Both keys come from different places**: `ic_mean` is `ic_report(...)["ic_mean"]`, and `min_detectable_ic_at_n` is `adequacy_report(...)["min_detectable_ic_at_n"]` — `ic_report` does **not** emit that key. Copy the call-site dict: `{"ic_mean": of_ic["ic_mean"], "min_detectable_ic_at_n": adequacy["min_detectable_ic_at_n"]}`. Do **not** invent an `MDE <= 0.05` gate — MDE at n=1000 is `0.0886` (2.802/√1000); report MDE at observed n and declare effect only when `|IC| >= MDE(n)`.
- EVAL-22 module-level assertions (in artifact/tests, **not** as invented verdict checks): `real_tape_discovery`, `real_tape_loaded` (provenance/path/venue/symbol/fingerprint), `causal_no_lookahead`, `microstructure_sane`.

### Traps — verified defects (do NOT re-open sealed files; contain in EVAL-22)
- **`_assert_causal` is vacuous** (`sample_adequacy_acquisition.py:820`): it iterates trades with no per-bar boundary comparison and unconditionally `return True`. Proven: an obviously leaky snapshot returns `True`. **EVAL-22 must implement its own causality check** — but test it *correctly*: the valid property is **time-truncation invariance** (build bars from only trades with `ts <= bar_end[k]`; the first `k+1` closes must equal the full-tape values — verified `True` for horizons 0/5/50/150). Do **not** assert "removing the last N rows leaves earlier bars unchanged": that legitimately shifts bars because the tape is unsorted (see tie-order trap below).
- **`DataLoader._parse_dt` silently substitutes `datetime.now()`** for unparseable timestamps (`src/data/loader.py:51`); `_load_orderflow` swallows per-trade exceptions and only logs. Proven: a trade with `"timestamp":"not-a-date"` loads as *now* instead of raising. **EVAL-22 must assert raw timestamp parseability itself**, not trust the loader.
- **Empty/blank tapes load without error** — `venue=""`, `symbol=""`, `trades=[]` produces an empty snapshot. Reject explicitly.
- `src/analytics/sample_adequacy_acquisition.py:346` `acquire_tape()` + hardcoded `load_btc_orderflow` (`src/analytics/integrated_options_orderflow_evaluation.py:1033`) prevents real-tape discovery and would mislabel the canonical synthetic file as real if it were adequate. **Do not modify sealed EVAL-21.**
- `measurement_validity_evaluation.py:751` `evaluate_measurement_validity()` takes no snapshot and calls the hardcoded loader — **drive lower-level primitives instead** (`build_pillar_signals` at `:230` *is* snapshot-parametric and safe).
- **Bar-close determinism depends on tape row order** (measured, EVAL-22 scope). `_build_bars` sorts by timestamp only, so trades sharing a timestamp keep their input order; the synthetic tape has **118 timestamps shared by >1 trade** (max multiplicity 3, 872 distinct of 1000) and **495 timestamp inversions**. Measured effect: shuffling trade order changed **20 of 240 bar closes**, hence different returns and a different Sharpe — i.e. sealed metrics are **not invariant to row order**. This is *not* lookahead (bar membership is correct and time-truncation prefixes reproduce earlier bars exactly), it is **tie-order nondeterminism**. **EVAL-22 must canonicalize** before building bars: `sorted(trades, key=lambda t: (ts, trade_id, price, size, side))` — verified to make closes order-invariant across 5 shuffles. Add a test asserting two permutations of the same tape give byte-identical artifacts. Do **not** modify the sealed bar builder; canonicalize in the ingestion layer.

### Data contract (exact request when no real tape — today's outcome)
Drop a real orderflow tape at `data/raw/orderflow_<venue>_<symbol>_<UTC>.json` (or `..._<venue>_<symbol>.json`) as a bare list or `{"trades":[...],"liquidations":[...],"funding_rates":[...],"symbol":...,"venue":...}`. Each trade needs `timestamp, price, size, side` (buy/sell; optional `trade_id`). Adequacy: **>= 1000 per-bar returns and >= 20 walk-forward windows** — measured minimum **>= 1001 bars @15s** (~4.2h continuous prints; today's tape gives 239 returns / 3 windows, shortfall **761 returns / 17 windows**).

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs (incl. EVAL-21). Do not widen WF params to manufacture windows or fabricate "real" data.
- Do not modify `src/analytics/sample_adequacy_acquisition.py` or `src/analytics/measurement_validity_evaluation.py`.
- Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`.
- `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only, out of scope.
- **Do not `pip install` anything beyond the verified set above**; no new runtime deps.

### Session completion gate
- [ ] `src/analytics/real_tape_ingestion.py` exists and `py_compile` passes.
- [ ] `tests/test_real_tape_ingestion.py` has >= 10 tests and passes.
- [ ] `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}` exists with `verdict` and `verdict_checks` (or explicit NO-GO + shortfall).
- [ ] Regression baseline still passes (45 tests, ~134s).
- [ ] This handoff updated with measured numbers/artifacts and next task.
- [ ] New files committed or explicitly recorded here.

---

## NEXT FOCUS CAMPAIGN (heavy-work floor per session)

| Eval | Focus | Dependency | Heavy-work floor | If data absent |
|---|---|---|---|---|
| **EVAL-22 (ACTIVE)** | Real-tape ingestion gate | none | `real_tape_ingestion.py` + 10–16 tests + CLI + strict artifact; NO-GO if no real tape | seal NO-GO with shortfall + data contract |
| **EVAL-23B** | Exchange export adapters (fallback) | none | `src/data/exchange_exports.py`: deterministic OKX/Binance/Deribit trade-export parsers → `OrderflowSnapshot`; fixtures + 12 tests + CLI; no network | n/a |
| **EVAL-23** | Real net-of-cost verdict | EVAL-22 finds adequate real tape | drive sealed EVAL-20 primitives on real tape (not the hardcoded top-level fn); GO only if net-of-cost + multiple-testing corrected | go to EVAL-23B |
| **EVAL-24** | Options-leg validity | real option chain | `src/analytics/options_chain_validation.py`: quote sanity, put-call parity, no-arb bounds, greeks/IV surface; tests + CLI. Start from the sealed surface builder `src/analytics/options_surface_greeks_evaluation.py` and the loader `DataLoader.load_options_chain` (`src/data/loader.py:188`, returns `OptionsChain` with `.quotes` of `OptionQuote(contract, bid, ask, last, mark, bid_iv, ask_iv, mark_iv, delta, gamma, theta, vega, open_interest, volume, timestamp)`). Today's fixture is **30 quotes, venue `synthetic`, 3 expiries, internally inconsistent (EVAL-16)** — ship validator + NO-GO with exact chain shortfall | ship validator + tests |
| **EVAL-25** | Real-tape falsification | EVAL-23 | parameter perturbation, placebo/label shuffle, subperiod stability, Benjamini-Hochberg correction; artifact | n/a |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If data-gated, execute the fallback; never idle.

---

## BOTTLENECK REMOVAL — 2026-11-13T21:40:24Z
- **Single actionable handoff enforced:** root handoffs verified as retired pointers; only this file actionable.
- **Primary throughput bottleneck (EVAL-22 unstarted) cleared:** explicitly active with zero-discovery task, exact reuse points, verified defects, verdict contract, and a hard completion gate.
- **Environment bottleneck removed (new):** the prior handoff did not say deps were missing; runner had *no* numpy/pandas/pytest. Verified install command + exact working versions recorded above. A session that silently assumed a ready env would have wasted its budget.
- **Stale baseline corrected:** 84.56s → **measured 134.07s**; regression timeout budget corrected to ~150s so a correct run is not misread as a hang.
- **Four latent traps documented and proven** so the next agent cannot ship a vacuous causality test, trust loader timestamp fallbacks, or inherit order-dependent metrics: `_assert_causal` vacuous, `_parse_dt` now-fallback, empty-tape acceptance, plus a measured **bar-close order-dependence** (118 duplicate timestamps / 495 inversions; 20/240 closes change on shuffle) with the verified canonical-sort fix.
- **Data bottleneck converted to a non-blocking gate:** synthetic-only `data/raw/` documented with measured shortfall (761 returns / 17 windows); EVAL-22 seals `NO-GO (no adequate real tape)` and the campaign advances to **EVAL-23B**.
- **Sealed defects contained:** EVAL-22 bypasses hardcoded synthetic loaders via `DataLoader(cache=False).load_orderflow` and lower-level EVAL-20 primitives; no sealed-file edits.
- **Safety/invariants re-verified:** `.env` absent, paper-only, NEXT9 out of scope, no workflow/credential mutation, no full-suite runs, no `research_state/` enumeration, no new phase wrappers.
- **Regression re-verified:** 45/45 targeted tests passed in 134.07s; no code changed by this refresh.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7` (1000 trades/20 liq/8 funding, 2026-10-31T06:16:23.656379Z–07:16:21.656379Z, ~1h, venue `synthetic`, BTCUSDT → 240 bars/239 returns/3 windows @15s). `data/raw/options_btc_synthetic.json` (30 quotes, venue `synthetic`). `data/processed/*.json` synthetic-derived.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; `src.config_settings.RiskConfig` (default `max_position_pct=0.1`; `config/settings.yaml` risk.max_position_pct=0.1 — pass explicitly); `src.backtest.engine.WalkForwardBacktest`/`BacktestEngine`.
- **EVAL-20 (sealed, import not fork)** — `src.analytics.measurement_validity_evaluation`: `build_pillar_signals`(:230), `simulate_pillar`(:319), `adequacy_report`(:465), `periods_per_year`(:154), `sharpe_from_returns`(:162), `per_bar_returns`(:173), `min_detectable_ic`(:221), `power_for_ic`(:205), `degeneracy_report`(:285), `ic_report`(:501), `cost_grid_report`(:551), `pillar_metrics`(:613), `compute_verdict`(:650), `evaluate_measurement_validity`(:751 — **do not use**). Constants: `DEFAULT_MIN_RETURNS=1000`(:96), `DEFAULT_MIN_WINDOWS=20`(:97).
- **EVAL-21 helpers (reuse):** `src.analytics.sample_adequacy_acquisition` — `_orderflow_candidates`(:130), `_count_windows_for_bars`(:137), `_tape_adequacy`(:147), `build_synthetic_orderflow_tape`(:181), `_snapshot_to_orderflow_dict`(:315), `_fingerprint_tape`(:331), `acquire_tape`(:346 — **defective, do not use for real verdicts**), `evaluate_sample_adequacy`(:428 — template), `_assert_causal`(:820 — **vacuous**). `build_pillar_signals` return keys: `bars`, `bar_ends_dt`, `bar_closes`, `options_signal`, `orderflow_signal`, `toxicities`, `combined_signal`, `positions`, `opt_components`, `n_bars`, `bar_duration_seconds`, `spot` (:261–282).
- **Bar builder:** `_build_bars` at `src/analytics/integrated_options_orderflow_evaluation.py:288` — causal, `(bar_start, bar_end]`, close carried forward; returns `bar_ends/bar_ends_dt/bar_closes/bar_trades/n_bars/start_timestamp/end_timestamp/bar_duration_seconds`.
- **Loader:** `DataLoader(cache=True)` (`src/data/loader.py:55`) `.load_orderflow(path, venue=..., symbol=...)` (:103); `OrderflowSnapshot` (`src/data/schemas.py:122`), `Trade` (:71). `validate_trade` (`src/data/validators.py:10`) accepts price/size `>= 0` (zero allowed) and side ∈ {buy,sell}.
- **Window math:** `_count_windows_for_bars(n_bars, 120, 40, 40)`; both-gates minimum `n_bars = 1001`.
- `ic_detail` (ic_report :501) emits `ic_mean`, `ic_std`, `ic_tstat`, `ic_by_horizon`, `horizons`, `n_horizons`, `power_note` — **not** `min_detectable_ic_at_n`; that key is from `adequacy_report`(:465). `adequacy_report` also emits `min_detectable_ic_at_floor`, `returns_floor_met`, `windows_floor_met`, `n_ic_observations`, `bar_return_mean_bps`, `bar_return_std_bps`, `bar_return_tstat`.
- **EVAL-20 verdict call site:** `measurement_validity_evaluation.py:945` — the single in-repo `compute_verdict` invocation; copy its `ic_detail` dict and `determinism_ok` fingerprint pattern (`_fingerprint()` over returns/pillars/cost/adequacy/degeneracy, two consecutive builds).
- **Environment:** Python 3.12.3; installed at 2026-11-13T21:40Z: numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, pyyaml, requests, websocket-client, python-dateutil. No mypy/ruff/flake8 — verify via `py_compile` + targeted pytest only.
- **Regression baseline:** 45 passed in 134.07s (2026-11-13T21:38Z, EVAL-20 26 + EVAL-21 19).

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..EVAL-21 SEALED. EVAL-22 ACTIVE (`INIT-2026-11-13T21:40:24Z-EVAL-22-REAL-TAPE-GATE`).** New EVALs must ship module + numeric-invariant tests + CLI + strict artifact.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.