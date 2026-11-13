# SINGLE DURABLE HANDOFF — READ FIRST

**Handoff refreshed:** 2026-11-13T20:48:42Z (UTC) — repo state re-verified at session start. `research_state/durable_handoff.md` is the only actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action and do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness.

**State (measured at 2026-11-13T20:48:42Z):** EVAL-02..EVAL-21 **SEALED** (EVAL-21 GO on synthetic tape only; validates measurement battery, not real alpha). **EVAL-22 ACTIVE and UNSTARTED** — absent: `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py`, `research_state/REAL_TAPE_INGESTION_*`. `.env` **ABSENT** (paper-only). Only tape in `data/raw/` is synthetic: `orderflow_btcusdt_synthetic.json` (SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`, 240 bars / 239 returns / 3 windows @15s; `options_btc_synthetic.json` present but 30 internally-inconsistent quotes). No adequate real tape. Regression baseline: `tests/test_sample_adequacy_acquisition.py` + `tests/test_measurement_validity_evaluation.py` = **45 passed in 84.56s** (2026-11-13T20:48Z verification; budget ~90s due to module-scope fixtures). Working tree clean at verification; no other in-repo blocked session beyond documented real-data absence.

**NEXT FOCUS CAMPAIGN:** **EVAL-22 → EVAL-23B → EVAL-24 → EVAL-25**. (EVAL-23 is data-blocked until an adequate real tape is found; do not idle.)

---

## INITIAL TASK MESSAGE — 2026-11-13T20:48:42Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-13T20:48:42Z-EVAL-22-REAL-TAPE-GATE`
**STATUS:** **ACTIVE, not started.** Start here — no discovery needed.

> **Hard floor:** a session that ends without new EVAL-22 artifacts (`src/analytics/real_tape_ingestion.py` + `tests/test_real_tape_ingestion.py` + `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}` + recorded verification evidence) is **FAILED**. Handoff-only work is FAILED. If no adequate real tape exists, ship the module/tests and seal an explicit **`NO-GO (no adequate real tape)`** artifact with measured shortfall + exact data contract (legitimate seal), then set next active task to **EVAL-23B**.

### Do now (heavy work required)
1. **Implement `src/analytics/real_tape_ingestion.py`** (deterministic, offline, paper-only, no exchange/network calls).
   - `discover_real_orderflow_tapes(data_raw_dir=Path("data/raw")) -> List[Path]`: glob `orderflow_*.json`; **exclude** any name containing `synthetic`; deterministic sort.
   - `load_real_tape(path) -> dict`: load via `DataLoader().load_orderflow(path, venue=<from filename>, symbol=<from filename>)` (`src/data/loader.py:103`); reject if venue/symbol empty or synthetic, or matches canonical synthetic tape; record path, venue, symbol, content SHA-256, span, n_trades, n_bars, n_returns, n_windows.
   - `validate_real_tape(...)`: adequacy (`n_returns >= 1000` and `n_windows >= 20`), causal no-lookahead (bars from `_build_bars`; no trade after `bar_end[t]` may affect bar `t`), microstructure sanity (price > 0, size > 0, side in {buy,sell}, timestamps monotone non-decreasing), symbol/venue consistency.
   - If adequate real tape found: drive the **same sealed EVAL-20 primitives** on the real snapshot following `sample_adequacy_acquisition.py:428` `evaluate_sample_adequacy` pattern — `build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `ic_report`, `compute_verdict`, `pillar_metrics`, etc. **Do NOT call `evaluate_measurement_validity()`** (hardcodes synthetic loader, no snapshot param). If none: emit `NO-GO (no adequate real tape)` with per-candidate counts and exact shortfall.
   - Reuse/import (do not fork): `_build_bars` (`src/analytics/integrated_options_orderflow_evaluation.py:288`), `per_bar_returns`, `adequacy_report`, `ic_report`, `periods_per_year`, `sharpe_from_returns`, `compute_verdict`, `serialize_metrics_strict`, `assert_json_valid`; helpers `_count_windows_for_bars`/`_tape_adequacy` (`sample_adequacy_acquisition.py:137,147`).
   - Never substitute synthetic for real; never emit `{"valid": true}`; strict JSON `allow_nan=False`.
2. **Write `tests/test_real_tape_ingestion.py`** with **10–16 numeric-invariant tests**: discovery excludes `*_synthetic.json` and includes real patterns; adequate real fixture → `data_provenance="real"`; inadequate real fixture → `NO-GO` with exact shortfall; malformed/empty/synthetic-venue rejected; causal no-lookahead (mutating future trade must not change earlier bars); microstructure rejects bad price/size/side/timestamps; adequacy counts match helpers; strict serialization/no `{"valid": true}`; determinism (two runs byte-identical); fingerprint changes on tape change; CLI writes `.json` and `.md`.
3. **Add CLI:** `python -m src.analytics.real_tape_ingestion --out research_state/ [--data-dir data/raw]` producing `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}`.
4. **Run and record verification:**
   - `python3 -m py_compile src/analytics/real_tape_ingestion.py tests/test_real_tape_ingestion.py`
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py`
   - `python3 -m pytest -q tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py` (expect **45 passed** — regression gate)
5. **Seal in place:** update this handoff with measured verdict/checks/evidence/artifact paths and set next active task (**EVAL-23B** if no adequate real tape; else **EVAL-23**). Commit/record partial work if incomplete — never leave clean tree with EVAL-22 pending.

### EVAL-22 verdict contract (use sealed `compute_verdict` verbatim)
Call: `compute_verdict(adequacy, sizing_consistent, sizing_detail, sharpe_ok, sharpe_detail, degeneracy, cost_detail, ic_detail, determinism_ok, never_valid_true)` → exactly 8 checks: `measurement_reproducible`, `sample_adequate_declared`, `sizing_consistent`, `sharpe_basis_valid`, `non_degenerate_pillars_reported`, `net_of_cost_honest`, `ic_reported_with_power`, `strict_serialization`.
- `sample_adequate_declared`: `n_returns >= 1000` and `n_windows >= 20` (emit both; NO-GO legitimate if unmet).
- `sizing_detail`: `requested_max_position_pct`, `risk_config_max_position_pct`, `rejections`, `max_drawdown_limit`, `sizing_consistent` (true iff `|enforced-requested|<=1e-12` and `rejections==0`).
- `sharpe_detail`: `annualisation`, `expected_annualisation`, `sharpe`, `abs_error`; ok iff annualisation matches `periods_per_year(bar_duration_seconds)` and sharpe reproduces.
- `cost_detail`: `complete` and `non_negative` (all series have `gross_return_total, net_return_total, turnover, total_cost_bps` and `total_cost_bps >= 0`).
- `ic_detail`: must contain `ic_mean` and `min_detectable_ic_at_n` (reporting check; do **not** invent `MDE<=0.05` gate — MDE is 0.0886 at n=1000). Report MDE at observed n and declare effect only when `|IC| >= MDE(n)` in narrative.
- **EVAL-22-specific module-level assertions (in artifact/tests, not as invented verdict checks):** `real_tape_discovery` excludes synthetic/canonical file, `real_tape_loaded` with provenance/path/venue/symbol/fingerprint, `causal_no_lookahead`, `microstructure_sane`.

### Known defects — do NOT re-open sealed files; contain in EVAL-22
- `src/analytics/sample_adequacy_acquisition.py:346` + hardcoded synthetic loader (`src/campaign/integrated.py:188` via `load_btc_orderflow`) prevents real-tape discovery and would mislabel synthetic as real if adequate. **Do not modify sealed EVAL-21; implement strict real-only discovery via `DataLoader().load_orderflow`.**
- `src/analytics/measurement_validity_evaluation.py:751` `evaluate_measurement_validity()` takes no snapshot and calls hardcoded loader — **drive lower-level primitives instead**.

### Data contract (exact request if no real tape)
Drop a real orderflow tape at `data/raw/orderflow_<venue>_<symbol>_<UTC>.json` (or `..._<venue>_<symbol>.json`) as bare list or `{"trades":[...],"liquidations":[...],"funding_rates":[...],"symbol":...,"venue":...}`. Each trade needs `timestamp, price, size, side` (buy/sell; optional `trade_id`). Adequacy: **>= 1000 per-bar returns** and **>= 20 walk-forward windows** (≈ >= 1000 bars @15s, ~4.2h+ continuous prints). Without it, EVAL-22 seals `NO-GO (no adequate real tape)` with exact shortfall.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs (incl. EVAL-21). Do not widen WF params to manufacture windows or fabricate "real" data.
- Do not modify `src/analytics/sample_adequacy_acquisition.py` or `src/analytics/measurement_validity_evaluation.py`.
- Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite (5297 tests). Do not modify `.github/workflows/main.yml`.
- `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only, out of scope.

### Session completion gate
- [ ] `src/analytics/real_tape_ingestion.py` exists and `py_compile` passes.
- [ ] `tests/test_real_tape_ingestion.py` has >= 10 tests and passes.
- [ ] `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}` exists with `verdict` and `verdict_checks` (or explicit NO-GO + shortfall).
- [ ] Regression baseline still passes (45 tests).
- [ ] This handoff updated with measured numbers/artifacts and next task.
- [ ] New files committed or explicitly recorded here.

---

## NEXT FOCUS CAMPAIGN (heavy-work floor per session)

| Eval | Focus | Dependency | Heavy-work floor | If data absent |
|---|---|---|---|---|
| **EVAL-22 (ACTIVE)** | Real-tape ingestion gate | none | `real_tape_ingestion.py` + 10–16 tests + CLI + strict artifact; NO-GO if no real tape | seal NO-GO with shortfall + data contract |
| **EVAL-23B** | Exchange export adapters (fallback) | none | `src/data/exchange_exports.py`: deterministic OKX/Binance/Deribit trade-export parsers → `OrderflowSnapshot`; fixtures + 12 tests + CLI; no network | n/a |
| **EVAL-23** | Real net-of-cost verdict | EVAL-22 finds adequate real tape | drive sealed EVAL-20 primitives on real tape (not hardcoded top-level fn); GO only if net-of-cost + multiple-testing corrected; artifact | go to EVAL-23B |
| **EVAL-24** | Options-leg validity | real option chain | `src/analytics/options_chain_validation.py`: quote sanity, put-call parity, no-arb bounds, greeks/IV surface; tests + CLI; NO-GO with exact chain shortfall | ship validator + tests |
| **EVAL-25** | Real-tape falsification | EVAL-23 | parameter perturbation, placebo/label shuffle, subperiod stability, Benjamini-Hochberg correction; artifact | n/a |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If data-gated, execute fallback; never idle.

---

## BOTTLENECK REMOVAL — 2026-11-13T20:48:42Z
- **Single actionable handoff enforced:** root handoffs verified as retired pointers; only this file actionable.
- **Primary throughput bottleneck (EVAL-22 unstarted):** explicitly made active with zero-discovery task, exact reuse points, defects, verdict contract, and hard completion gate.
- **Data bottleneck converted to non-blocking gate:** synthetic-only `data/raw/` documented; EVAL-22 must seal `NO-GO (no adequate real tape)` with measured shortfall if no real tape, and campaign advances to **EVAL-23B**.
- **Known sealed defects contained:** EVAL-22 must bypass hardcoded synthetic loaders by using `DataLoader().load_orderflow` and lower-level EVAL-20 primitives; no sealed-file edits.
- **Safety/invariants re-verified:** `.env` absent, paper-only, NEXT9 out of scope, no workflow/credential mutation, no full-suite runs, no `research_state/` enumeration, no new phase wrappers.
- **Regression re-verified:** 45/45 targeted tests passed in 84.56s; no code changed by this handoff refresh.
- **No other in-repo blocked sessions found:** session-gate scripts/docs present; workflow diagnostics not agent-actionable in-repo.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7` (1000 trades/20 liqs/8 funding, 2026-10-31T06:16:23Z–07:16:21Z, ~1h, venue synthetic, BTCUSDT → 240 bars/239 returns/3 windows @15s). `data/raw/options_btc_synthetic.json` (30 BTC quotes, 3 expiries, internally inconsistent EVAL-16). No ETH/SOL raw options/orderflow. `data/processed/*.json` synthetic-derived.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; `src.config_settings.RiskConfig` (default `max_position_pct=0.1`, pass explicitly); `src.backtest.engine.WalkForwardBacktest`/`BacktestEngine`.
- **EVAL-20 (sealed, import not fork):** `src.analytics.measurement_validity_evaluation` — `build_pillar_signals`(:230), `simulate_pillar`(:319), `adequacy_report`(:465), `periods_per_year`(:154), `sharpe_from_returns`(:162), `per_bar_returns`(:173), `min_detectable_ic`(:221), `power_for_ic`(:205), `degeneracy_report`(:285), `ic_report`(:501), `cost_grid_report`(:551), `pillar_metrics`(:613), `compute_verdict`(:650), `evaluate_measurement_validity`(:751). **Caveat:** `evaluate_measurement_validity()` hardcoded/no snapshot — do not use for real verdicts.
- **EVAL-21 helpers (reuse):** `src.analytics.sample_adequacy_acquisition` — `_count_windows_for_bars`(:137), `_tape_adequacy`(:147), `_snapshot_to_orderflow_dict`(:315), `_fingerprint_tape`(:331), `build_synthetic_orderflow_tape`(:181), `acquire_tape`(:346), `evaluate_sample_adequacy`(:428). **Do not call `acquire_tape()` for real verdicts** (defect).
- **Bar builder:** `_build_bars` at `src/analytics/integrated_options_orderflow_evaluation.py:288` (causal, `(bar_start,bar_end]`, close carried forward).
- **Loader:** `DataLoader().load_orderflow(path, venue=..., symbol=...)` at `src/data/loader.py:103`; `OrderflowSnapshot` at `src/data/schemas.py:122`.
- **Constants:** `DEFAULT_BAR_DURATION_SECONDS=15.0`, `TRAIN=120`, `TEST=40`, `STEP=40`, `MIN_RETURNS=1000`, `MIN_WINDOWS=20`, `DEFAULT_MAX_POSITION_PCT=0.20`, `POWER_ALPHA=0.05`, `POWER_TARGET=0.80`.
- **Environment:** Python 3.12.3; numpy/pandas/scipy/pydantic/pytest/PyYAML/requests installed. No mypy/ruff/flake8 — verify via `py_compile` + targeted pytest only. Never run full suite (5297 tests). Never enumerate `research_state/`.
- **Regression baseline:** 45 passed (EVAL-20 26 + EVAL-21 19), 2026-11-13T20:48:42Z, 84.56s.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..EVAL-21 SEALED. EVAL-22 ACTIVE (`INIT-2026-11-13T20:48:42Z-EVAL-22-REAL-TAPE-GATE`).** New EVALs must ship module + numeric-invariant tests + CLI + strict artifact.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
