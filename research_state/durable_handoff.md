# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T04:43:31Z (UTC).** Handoff refreshed/verified at HEAD working tree 2026-11-14T04:43:31Z (clean tree; no EVAL-23/24 artifacts landed since 2026-11-14T03:00:10Z). Prior sealed artifacts: `src/data/options_exports.py`, `tests/test_options_exports.py`, `src/data/exchange_exports.py`, `tests/test_exchange_exports.py`, `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py`, `src/analytics/real_data_falsification.py`, `tests/test_real_data_falsification.py`, `data/examples/options_exports/*`, `data/examples/exchange_exports/*`, `data/examples/normalized/*`, `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.{json,md}`, `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.{json,md}`, `research_state/REAL_TAPE_INGESTION_20261113T233551Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T004500Z.{json,md}`.
`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

**State (measured 2026-11-14T03:00:10Z):** EVAL-02..EVAL-22 **SEALED**. EVAL-25 **GO** (2 real candidates, 1 adequate orderflow + 1 adequate option chain). EVAL-26 **SEALED** (public acquisition module + real data acquired). EVAL-23 **dry-run NO-GO (4/7 checks); sealing required**. EVAL-24 **real chain loaded; sealing required**. `.env` **ABSENT** (paper-only). `data/raw/` now contains **real OKX public exports** plus the original synthetic fixtures (never relabeled).
**Gate re-run (2026-11-14T02:50:46Z):** `python3 -m src.analytics.real_data_falsification --repo . --out research_state --data-dir data/raw --timestamp 2026-11-14T02:50:46Z` → `overall_verdict=GO`, `n_candidates=2`, `n_adequate_orderflow=1`, `n_adequate_options=1`, `canonical_fingerprint=fc5b24c2f4e79333faaad5b4f98de90a99ef2046d82f9dd07f4ef2a31bd521ca`. Artifact: `research_state/REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`.
**EVAL-22 re-run (2026-11-14T02:53:22Z):** `python3 -m src.analytics.real_tape_ingestion --out research_state --data-dir data/raw` → `overall_verdict=GO`, 1 adequate real tape, `causal_no_lookahead=true`, `microstructure_sane=true`, 8/8 checks. Artifact: `research_state/REAL_TAPE_INGESTION_20261114T025322Z.{json,md}`.
**Acquisition artifact:** `research_state/PUBLIC_EXPORT_ACQUISITION_20261114T024736Z.{json,md}` (`report_id=PUBLIC_EXPORT_ACQUISITION_26`).

**NEXT FOCUS CAMPAIGN:** **EVAL-23 / EVAL-24 — real net-of-cost verdict and options-leg validity (DATA UNBLOCKED).** Every session must seal at least one of: (a) `REAL_NET_OF_COST_EVAL_23_<UTC>.{json,md}` with measured net-of-cost metrics and a GO/NO-GO verdict on the real tape+chain, or (b) `OPTIONS_LEG_VALIDITY_24_<UTC>.{json,md}` with measured options-leg validity on the real chain. Never idle, never relabel synthetic as real, never fabricate provenance, never emit `{"valid": true}`. A trustworthy NO-GO is a full success.

---

## INITIAL TASK MESSAGE — 2026-11-14T04:43:31Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T04:43:31Z-EVAL-23-24-REAL-NET-OF-COST-AND-OPTIONS-LEG`
**STATUS:** **ACTIVE — real data unblocked; EVAL-23/EVAL-24 are the only remaining gates. Start here; zero acquisition discovery needed.**
> **Hard floor:** a session ending without a sealed `REAL_NET_OF_COST_EVAL_23_<UTC>.{json,md}` (or `OPTIONS_LEG_VALIDITY_24_<UTC>.{json,md}`) containing measured numbers, artifact paths, and a GO/NO-GO verdict is **FAILED**. Handoff-only work is FAILED. A trustworthy NO-GO is success; a fabricated GO is failure.

### Environment setup (verified)

Deps present: Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0. If missing: `python3 -m pip install --quiet numpy pandas scipy pytest pyyaml pydantic requests websocket-client python-dateutil`. Use `python3 -m py_compile` + targeted `pytest` only (no mypy/ruff/flake8). **Never run the full suite (5,297 tests). Never enumerate `research_state/` (75k files / ~5.0 GB).**

### Do now (heavy work required)

0. **If the real exports are absent (fresh checkout; they are gitignored), regenerate them first:**
   ```bash
   python3 -m src.data.public_export_acquisition --underlying BTC \
     --orderflow-instrument BTC-USD-SWAP --min-bars 1550 \
     --bar-duration-seconds 15 --max-pages 2000 --page-limit 100 \
     --request-delay-seconds 0.05 --timeout 25 --max-retries 5 \
     --data-dir data/raw --out research_state --timestamp <UTC>
   ```
   This writes `data/raw/orderflow_okx_BTC-USD-SWAP.json` and `data/raw/options_okx_BTC_<UTC>.json` and seals `PUBLIC_EXPORT_ACQUISITION_<UTC>.{json,md}`. Then re-run EVAL-25 to confirm GO.
1. **Load the real inputs with the new real-first loaders** (no synthetic fallback):
   ```python
   from datetime import datetime, timezone
   from pathlib import Path
   from src.campaign.integrated import load_real_orderflow, load_real_options_chain
   now = datetime(2026, 11, 14, 2, 47, 36, tzinfo=timezone.utc)
   spot = 67440.8  # last real tape trade price
   snap = load_real_orderflow("BTC", data_raw=Path("data/raw"))
   chain = load_real_options_chain("BTC", data_raw=Path("data/raw"))
   ```
   `load_real_orderflow` / `load_real_options_chain` raise `RealDataUnavailable` if no real export exists; they never fall back to synthetic.
2. **Wire the real inputs into the net-of-cost evaluation.** `src/analytics/integrated_options_orderflow_evaluation.evaluate_integrated_options_orderflow(...)` currently loads its own data and hardcodes `spot=65000.0`, `now=DETERMINISTIC_NOW` (2026-10-31). Add optional `chain=None, snapshot=None, spot=None, now=None` parameters (backward-compatible; keep synthetic defaults for existing tests) or create a new EVAL-23 wrapper that imports the sealed primitives. Use `spot=67440.8`, `now=2026-11-14T02:47:36Z`, `bar_duration_seconds=15.0`, default windows/seeds/costs, `max_position_pct=0.20`.
3. **Seal EVAL-23:** emit `research_state/REAL_NET_OF_COST_EVAL_23_<UTC>.{json,md}` with `report_id="REAL_NET_OF_COST_EVAL_23"`, `trading_mode="paper"`, `live_trading_enabled=false`, `data_provenance="real"`, `authenticity_verified=false`, `never_valid_true=true`. Include per-bar returns, IC by horizon, gross/net/turnover/cost bps, walk-forward windows, Sharpe/DSR/PBO, permutation p-values, the 7-check verdict matrix, and an evidence matrix (`n_trades=57400`, `n_options_quotes=739`, `n_bars=1552`, `venue=okx`).
4. **Seal EVAL-24:** validate the real option chain (739 quotes, 739 contracts, 12 expiries, 88 strikes) with the sealed options-surface/greeks/skew/term-structure/liquidity primitives; emit `research_state/OPTIONS_LEG_VALIDITY_24_<UTC>.{json,md}` with measured numbers and an explicit `options_leg_degenerate` flag.
5. **Adjudicate the fusion rule explicitly.** The current dry run is flat/NO-GO because the options signal is degenerate on a single snapshot and `_fuse_positions` requires both pillars to agree. Decide and document whether that is a genuine NO-GO for the current strategy or whether the fusion rule should be amended (e.g., allow orderflow-only when the options leg is explicitly degenerate). If amended, seal it as a **new** evaluation; do not silently change the sealed fusion rule and call it the same EVAL.
6. **Run and record verification:** at minimum `python3 -m pytest -q tests/test_public_export_acquisition.py tests/test_real_data_inputs.py tests/test_real_data_falsification.py tests/test_real_tape_ingestion.py tests/test_exchange_exports.py tests/test_options_exports.py tests/test_integrated_options_orderflow_evaluation.py tests/test_production_simulation_evaluation.py` → **162 passed in 35.05s** (2026-11-14T03:00:10Z). Add any new EVAL-23/24 tests.
7. **Seal in place:** update this handoff with measured verdict/checks/evidence/artifact paths, new task timestamp/id, and the next active task. Commit partial work if incomplete — never leave a clean tree with EVAL-23/24 pending. A handoff-only session is FAILED.

### Reuse / traps
- **Real tape:** `data/raw/orderflow_okx_BTC-USD-SWAP.json` — 57,400 trades, 1,552 bars, 1,551 returns, 35 windows, 23,265.964s span (2026-11-13T20:19:45.772Z → 2026-11-14T02:47:31.736Z), venue `okx`, inverse BTC-USD-SWAP, SHA-256 `865d2e06157331bba01b067eafaefa839f9ce872a73830511289bf922837df83`.
- **Real chain:** `data/raw/options_okx_BTC_20261114T024736Z.json` — 739 quotes/contracts, 12 expiries, 88 strikes, venue `okx`, SHA-256 `268bf34ef8a1099ea79bf353ddfa337388bb071ac4f0968b107fbd1bcb3cc8fa`.
- **Reuse:** `src/campaign/integrated.load_real_orderflow` / `load_real_options_chain` (EVAL-23/24 entry points); `src/data/public_export_acquisition.py` (EVAL-26, public OKX read-only); `src/data/loader.py`; `src/data/schemas.py`; `src/analytics/integrated_options_orderflow_evaluation.py` (sealed EVAL-18 primitives); `src/analytics/production_simulation_evaluation.py`; `src/analytics/measurement_validity_evaluation.py`.
- **Synthetic traps:** `data/raw/orderflow_btcusdt_synthetic.json` is synthetic (SHA-256 `c75ced...cef7`, 1000 trades); `data/raw/options_btc_synthetic.json` is synthetic and internally inconsistent (EVAL-16). Never relabel either as real. `data/examples/*` are fixtures only.
- **Do not** run the full suite, enumerate `research_state/`, modify sealed EVALs (except the documented correctness fixes), create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests, or modify `.github/workflows/main.yml`.
- **Network:** public OKX read-only endpoints (`/api/v5/market/history-trades`, `/api/v5/public/instruments`, `/api/v5/market/tickers`) are allowed for acquisition. No authenticated calls, no order placement, no `.env`, no live trading.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no order placement.
- Do not re-open sealed EVALs. `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only, out of scope.

---

## PRELIMINARY EVAL-23 DRY RUN (NO-WRITE; NOT A SEALED ARTIFACT)

Measured 2026-11-14T02:58:57Z via a temporary script that loaded the real tape/chain and called the sealed EVAL-18 evaluation with the sizing/risk fixes. This is **evidence for the next session, not a substitute for the sealed EVAL-23 artifact**:

- `verdict=NO-GO`, `n_checks_passed=4/7`.
- `n_bars=1552`, `n_trades=57400`, `n_options_quotes=739`, `venue=okx`.
- `combined_ic_mean=0.006072698846805076`, `orderflow_ic_mean=0.0006555322687913788`, `options_ic_mean=0.0` (options leg degenerate on one snapshot).
- `combined_return=0.0`, `combined_sharpe=0.0`, `orderflow_only_sharpe=-8.790675715682735`, `flat_sharpe=0.0`.
- `failed_checks=["options_signal_exists", "combined_ic_significant", "combined_net_of_cost_superior"]`.
- No `short_notional_breach` after the sizing fix; the earlier run rejected trades because `RiskConfig()` defaulted to `max_position_pct=0.10` while the strategy sized at `0.20`.
- **Interpretation:** the harness now executes trades, but the combined strategy stays flat because the options signal is degenerate and fusion requires both pillars. This is a real research finding, not a harness artifact; EVAL-23 must seal it with the full artifact and an explicit fusion adjudication.

---

## BOTTLENECK LEDGER

- **Removed this session (2026-11-14T03:00:10Z):**
  - **Data acquisition (EVAL-26):** `src/data/public_export_acquisition.py` + `tests/test_public_export_acquisition.py` fetch read-only public OKX history-trades/instruments/tickers, write loader-compatible real exports, and seal provenance. Real tape and chain acquired; EVAL-25 GO.
  - **Loader discovery:** `src/campaign/integrated.py` now exposes `load_real_orderflow` / `load_real_options_chain` (real-first, no synthetic fallback) + `tests/test_real_data_inputs.py`.
  - **Sizing/risk mismatch:** `src/analytics/integrated_options_orderflow_evaluation.py` now passes `RiskConfig(max_position_pct=max_position_pct)` to both `WalkForwardBacktest` and `BacktestEngine`, and sizes off the conservative of nav/cash with 0.5% headroom. Previously every trade was rejected by a float-level notional overshoot, making the walk-forward vacuous.
  - **Causal gap false-negative:** `src/analytics/real_tape_ingestion.py` `assert_causal_time_truncation` now carries forward empty bars instead of returning fewer than `k+1` closes; `tests/test_real_tape_ingestion.py` covers the gapped-tape case.
  - **Stale test:** `tests/test_real_data_falsification.py` no longer asserts `data/raw` has zero real candidates; it asserts synthetic exclusion and honest GO/NO-GO reporting.
  - **Regression:** 162 passed across the 10 targeted test files (35.05s).
- **Remaining bottlenecks:**
  - **EVAL-23/24 not sealed.** The dry run is not an artifact; the next session must emit the sealed JSON/MD.
  - **Options leg degenerate on a single snapshot.** EVAL-18's options signal is constant across bars when the chain is a single cross-section; this is expected but must be explicitly flagged/adjudicated.
  - **Combined fusion requires both pillars.** With a degenerate options leg, the combined strategy is flat; decide whether the fusion rule should allow orderflow-only when options is explicitly degenerate (new sealed evaluation), or record a genuine NO-GO for the current strategy.
  - **Orderflow-only Sharpe is negative after costs** on the real tape (`-8.79`). That is a measured NO-GO signal, not a harness error; do not hide it.
- **Clean tree at 2026-11-14T04:43:31Z.** No EVAL-23/24 sealed artifacts landed since 03:00:10Z; the sealing bottleneck persists unchanged — the next session must emit the sealed JSON/MD, not re-discover data.
  - **Data provenance:** real public OKX exports have `authenticity_verified=false` (no signed venue attestation); the tape is inverse BTC-USD-SWAP, not spot. Document this in EVAL-23/24.

---

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| **EVAL-02..EVAL-22** | Sealed prior gates | **SEALED** |
| **EVAL-23B** | Exchange export adapters (trade) | **SEALED** — adapter PASS |
| **EVAL-24A** | Options export adapters | **SEALED** — adapter PASS |
| **EVAL-25** | Real-data acquisition & falsification gate | **GO** — 2 candidates, 1 adequate orderflow + 1 adequate options; artifact `REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`; fingerprint `fc5b24c2…` |
| **EVAL-26** | Public real-data acquisition | **SEALED** — `src/data/public_export_acquisition.py`; artifact `PUBLIC_EXPORT_ACQUISITION_20261114T024736Z.{json,md}` |
| **EVAL-23** | Real net-of-cost verdict | **ACTIVE** — real tape/chain loaded; dry-run NO-GO (4/7); seal `REAL_NET_OF_COST_EVAL_23_<UTC>.{json,md}` |
| **EVAL-24** | Options-leg validity | **ACTIVE** — real chain loaded (739 quotes, 12 expiries); seal `OPTIONS_LEG_VALIDITY_24_<UTC>.{json,md}` |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If blocked by data, ship the acquisition/validation adapter and a measured NO-GO artifact; never substitute synthetic and never fabricate provenance.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_okx_BTC-USD-SWAP.json` (57,400 trades; 1,552 bars; 1,551 returns; 35 windows; span 23,265.964s; SHA-256 `865d2e0…df83`); `data/raw/options_okx_BTC_20261114T024736Z.json` (739 quotes/contracts; 12 expiries; 88 strikes; SHA-256 `268bf34…c8fa`). Synthetic fixtures remain in `data/raw/` and are never used by the real loaders.
- **EVAL-22:** `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py`, `research_state/REAL_TAPE_INGESTION_20261114T025322Z.{json,md}` (GO, causal true, 8/8).
- **EVAL-25:** `src/analytics/real_data_falsification.py`, `tests/test_real_data_falsification.py`, `research_state/REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}` (GO, 2 candidates, fingerprint `fc5b24c2…`).
- **EVAL-26:** `src/data/public_export_acquisition.py`, `tests/test_public_export_acquisition.py`, `research_state/PUBLIC_EXPORT_ACQUISITION_20261114T024736Z.{json,md}`.
- **EVAL-23/24 entry points:** `src/campaign/integrated.load_real_orderflow`, `load_real_options_chain`; `tests/test_real_data_inputs.py`; `src/analytics/integrated_options_orderflow_evaluation.py`; `src/analytics/production_simulation_evaluation.py`.
- **Loader/schemas:** `DataLoader(cache=False).load_orderflow` / `load_options_chain` (`src/data/loader.py`); `OptionsChain`/`OptionContract`/`OptionQuote`/`OrderflowSnapshot`/`Trade` (`src/data/schemas.py`); validators `src/data/validators.py`.
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0.
- **Regression baseline (2026-11-14T03:00:10Z):** 162 passed across `test_public_export_acquisition.py`, `test_real_data_inputs.py`, `test_real_data_falsification.py`, `test_real_tape_ingestion.py`, `test_exchange_exports.py`, `test_options_exports.py`, `test_integrated_campaign.py`, `test_integrated_signal_series.py`, `test_integrated_options_orderflow_evaluation.py`, `test_production_simulation_evaluation.py`.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..22 sealed; EVAL-25 GO; EVAL-26 sealed; EVAL-23/24 active and must be sealed with measured real-data artifacts.**
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.