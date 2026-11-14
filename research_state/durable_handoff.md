# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T01:41:15Z (UTC).** Handoff refreshed/verified at HEAD `6add15519` (working tree clean; prior session artifacts: `src/data/options_exports.py`, `tests/test_options_exports.py`, `data/examples/options_exports/*`, `data/examples/normalized/options_deribit_BTC_*.json`, `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T004500Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}`).
`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

**State (measured 2026-11-14T01:41Z):** EVAL-02..EVAL-24A **SEALED**. EVAL-25 **SEALED code-complete; measured NO-GO (0 real candidates)** — gate+tests+artifact shipped (`research_state/REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}`, `report_id=REAL_DATA_FALSIFICATION_25`, `authenticity_verified=false`, `never_valid_true=true`, `canonical_fingerprint=e783ccde8d5c6c97b26750244a53207e376e55371a5d7f868e3c2ce78f769dc3`); 14 new tests passed in 0.83s; regression 103 passed in 108.63s. `.env` **ABSENT** (paper-only) — verified. `data/raw/` contains **only synthetic**: `orderflow_btcusdt_synthetic.json` (SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`; 1000 trades / 20 liq / 8 funding; venue `synthetic`, symbol `BTCUSDT`) and `options_btc_synthetic.json` (30 quotes; internally inconsistent, EVAL-16). Real-tape discovery `data/raw` (excluding `*_synthetic*`) → **0 candidates**. No real tape, no real option chain. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` human-only, out of scope.

**NEXT FOCUS CAMPAIGN:** **EVAL-25 (SEALED, code-complete) — real-data acquisition & gate re-validation.** The falsification gate is code-complete and testable; the only remaining blocker is **data availability**, not code. Every session must either (a) acquire a real venue orderflow tape + option export (non-`*_synthetic*` files in `data/raw/`) and re-run the gate, or (b) if still no real export, ship a refreshed measured NO-GO artifact (new timestamp) plus re-verified regression. EVAL-23 / EVAL-24 unblock **only** when an adequate real tape passes EVAL-22 and an adequate real option chain passes EVAL-24 through this gate. Never idle; never substitute synthetic; never fabricate provenance.

---

## EVAL-24A EXCHANGE OPTION EXPORT ADAPTERS — SEALED 2026-11-14T00:45Z

- **Verdict:** adapter **PASS**; overall `NO-GO (no adequate real export)` — synthetic never substituted, no provenance fabricated.
- **Module:** `src/data/options_exports.py` — deterministic, offline, paper-only, no exchange/network calls.
  - Parses OKX / Binance / Deribit option **trade & quote** export **CSV and JSON** into `OptionContract` / `OptionQuote` / `OptionsChain`.
  - Strict timestamp + expiry parsing (ISO-8601, epoch s/ms/µs/ns; no `now()` fallback); reject unparseable/empty.
  - Microstructure validation: strike > 0, expiry > timestamp, option_type in `call`/`put` (also inferred from `...-C/P` symbol suffix when column absent), bid/ask finite non-negative, bid <= ask (tolerance 1e-9), IV/greeks finite-or-None, contract_size > 0.
  - Canonical quote order `(timestamp, expiry, strike, option_type, symbol)`; reject duplicate `(symbol, timestamp)`.
  - `parse_options_export(path, venue, underlying, format_hint=None) -> OptionsChain`; `write_normalized_options_chain(chain, out_path)` emits loader-compatible `data/raw/options_<venue>_<underlying>_<UTC>.json`.
- **Tests:** `tests/test_options_exports.py` — **23 passed in 0.29s** (venue parsers, option-type inference, strict timestamp/expiry/strike/bid/ask/IV rejection, crossed-market rejection, empty/duplicate/synthetic-filename rejection, canonical order + fingerprint invariance, determinism, loader compatibility, strict serialization/no `{"valid": true}`, adequacy GO/NO-GO, CLI artifacts).
- **Fixtures:** `data/examples/options_exports/okx_btc_option_sample.csv`, `binance_btc_option_sample.csv`, `deribit_btc_option_sample.json` (format fixtures, not real data).
- **CLI:** `python3 -m src.data.options_exports --in data/examples/options_exports/deribit_btc_option_sample.json --venue deribit --underlying BTC --out research_state --data-dir data/examples/normalized --timestamp 2026-11-14T00:45:00Z` → RC 0.
- **Artifact:** `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.json`, `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.md` (`report_id=OPTIONS_EXPORT_ADAPTERS_24A`, `data_provenance=exchange_export`, `authenticity_verified=false`, `adapter_verdict=PASS`, `overall_verdict=NO-GO`, `floors: min_contracts=8, min_quotes=8, min_expiries=2`, `canonical_fingerprint=52c27da9c3f13ab1...`).
- **Normalized fixture chain:** `data/examples/normalized/options_deribit_BTC_20261114T004349Z.json` (3 quotes; **not** a real chain; EVAL-24 must re-validate any real candidate).
- **Sealed EVAL regression:** `test_real_tape_ingestion.py` + `test_sample_adequacy_acquisition.py` + `test_measurement_validity_evaluation.py` + `test_exchange_exports.py` + `test_options_exports.py` = **103 passed in 114.32s** (re-measured 2026-11-14T00:45Z).
- **Blocker removed:** option-chain acquisition is now code-complete and testable. EVAL-24 remains blocked by **data availability**, not by a missing parser.

---

## INITIAL TASK MESSAGE — 2026-11-14T01:41:15Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T01:41:15Z-EVAL-25-REAL-DATA-ACQUISITION-READINESS`
**STATUS:** **EVAL-25 SEALED (code-complete; measured NO-GO on data availability). Start here — zero discovery needed.**
> **Hard floor:** a session ending without either (a) a re-run gate artifact showing real-data progress (adequate real tape + chain → GO, or refreshed `REAL_DATA_FALSIFICATION_<UTC>.{json,md}` NO-GO with a new timestamp) **or** (b) a documented acquisition attempt plus re-verified regression evidence is **FAILED**. Handoff-only work is FAILED. The gate `src/analytics/real_data_falsification.py` is already code-complete; the next session's heavy work is **real-data acquisition**: obtain a user/venue orderflow tape and option export, place them as non-`*_synthetic*` files under `data/raw/`, and re-run `python -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw [--timestamp <UTC>]`. EVAL-23 / EVAL-24 unblock **only** when an adequate real tape passes EVAL-22 (`min_returns=1000, min_windows=20, bar_duration_seconds=15.0`) AND an adequate real option chain passes EVAL-24 (`min_contracts=8, min_quotes=8, min_expiries=2`) through this gate. Never relabel synthetic as real; never fabricate provenance; never emit `{"valid": true}`.

### Environment setup (verified)

Deps present in runner (re-verified 2026-11-14T01:41Z): Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3. If missing: `python3 -m pip install --quiet numpy pandas scipy pytest pyyaml pydantic requests websocket-client python-dateutil`. `python3 -m py_compile` + targeted `pytest` only (no mypy/ruff/flake8). **Never run the full suite (5297 tests). Never enumerate `research_state/` (75k files / ~5.0 GB).**

### Do now (heavy work required)

1. **Attempt real-data acquisition.** Place a real venue orderflow tape (`orderflow_<venue>_<symbol>.json`) and/or real option export (`options_<venue>_<underlying>_<UTC>.json`) under `data/raw/` — file names must NOT contain `synthetic`. If none is available, this session's work is a documented acquisition attempt (record what was sought and the outcome).
2. **Re-run the gate:** `python -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw [--no-write] [--timestamp <UTC>]` producing `REAL_DATA_FALSIFICATION_<UTC>.{json,md}`; record `overall_verdict`, `n_candidates`, `n_adequate_orderflow`, `n_adequate_options`, `canonical_fingerprint`.
3. **Run and record verification:**
   - `python3 -m py_compile src/analytics/real_data_falsification.py tests/test_real_data_falsification.py`
   - `python3 -m pytest -q tests/test_real_data_falsification.py` (expect 14 passed)
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py tests/test_exchange_exports.py tests/test_options_exports.py` (expect 103 passed)
4. **Seal in place:** update this handoff with the measured verdict/checks/evidence/artifact paths and set the next active task (EVAL-23 / EVAL-24 only if an adequate real export now exists and passes the EVAL-25 gate; otherwise keep the campaign on real-data acquisition readiness). Commit partial work if incomplete — never leave a clean tree with EVAL-25 pending.

### Reuse / traps
- Reuse `src/data/loader.py` (`DataLoader(cache=False).load_orderflow` / `load_options_chain`), `src/analytics/real_tape_ingestion.py` (EVAL-22), `src/data/exchange_exports.py` (EVAL-23B), `src/data/options_exports.py` (EVAL-24A), `src/data/schemas.py`, `src/data/validators.py`, and `src/analytics/integrated_options_orderflow_evaluation._build_bars` for adequacy.
- `data/raw/options_btc_synthetic.json` is internally inconsistent (EVAL-16) and must never be relabeled as a real chain; `orderflow_btcusdt_synthetic.json` is synthetic.
- Do not modify sealed EVAL modules. Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs. `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only, out of scope.

---

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| **EVAL-02..EVAL-21** | Sealed prior gates | **SEALED** |
| **EVAL-22** | Real-tape ingestion gate | **SEALED NO-GO** (no adequate real tape; module+tests+artifact) |
| **EVAL-23B** | Exchange export adapters (trade) | **SEALED** — adapter PASS; no real export; fixture NO-GO |
| **EVAL-24A** | Options export adapters | **SEALED** — adapter PASS; no real export; fixture NO-GO |
| **EVAL-25 (SEALED)** | Real-data falsification readiness | **SEALED code-complete; measured NO-GO (0 real candidates)** — gate+tests+artifact shipped (`research_state/REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}`, `canonical_fingerprint=e783ccde8d5c6c97b26750244a53207e376e55371a5d7f868e3c2ce78f769dc3`); awaiting real-data acquisition / gate re-validation |
| **EVAL-23** | Real net-of-cost verdict | blocked on adequate real tape passing EVAL-22 |
| **EVAL-24** | Options-leg validity | blocked on real option chain; EVAL-24A unblocks acquisition |
| **EVAL-25 (dep)** | Real-tape falsification | gated on EVAL-23; falsification-readiness gate is the prerequisite |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If blocked by data, ship the acquisition/validation adapter and a measured NO-GO artifact; never substitute synthetic and never fabricate provenance.

---

## BOTTLENECK LEDGER

- **Removed this session:** EVAL-24A option-export ingestion (code, tests, fixtures, artifact). EVAL-25 gate re-validated 2026-11-14T01:41Z → NO-GO artifact `research_state/REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}` (fingerprint `e783ccde...`); 14 gate tests + 103 regression tests re-passed. Future sessions can acquire/normalize venue option exports without writing a parser.
- **Remaining data bottleneck:** no real trade tape and no real option chain in `data/raw/`. EVAL-23 and EVAL-24 are data-blocked, not code-blocked. Acquisition requires a user/venue export; do not fabricate or relabel synthetic data.
- **Test bottleneck:** 878 test files / 5,297 tests. Run only the targeted files named above; never the full suite.
- **Workspace bottleneck:** `research_state/` is ~5.0 GB / 75k files (historical phaseNN trees). Never enumerate it; read exact paths only.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` SHA-256 `c75ced...cef7` (239 returns / 3 windows @15s). `data/raw/options_btc_synthetic.json` (30 quotes, venue `synthetic`, EVAL-16 inconsistent). `data/examples/exchange_exports/*` + `data/examples/options_exports/*` format fixtures. `data/examples/normalized/orderflow_okx_BTCUSDT_20261113T235247Z.json` (3 trades) and `options_deribit_BTC_20261114T004349Z.json` (3 quotes) — normalized fixtures, not real.
- **EVAL-22 artifacts:** `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py` (15 tests), `research_state/REAL_TAPE_INGESTION_20261113T233551Z.{json,md}` (`NO-GO`, 0 candidates).
- **EVAL-23B artifacts:** `src/data/exchange_exports.py`, `tests/test_exchange_exports.py` (20 tests), `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.{json,md}` (`adapter PASS`, `NO-GO`).
- **EVAL-24A artifacts:** `src/data/options_exports.py`, `tests/test_options_exports.py` (23 tests), `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.{json,md}` (`adapter PASS`, `NO-GO`).
- **Loader/schemas:** `DataLoader(cache=False).load_orderflow` (`src/data/loader.py:103`), `load_options_chain` (`src/data/loader.py:191`); `OptionsChain`/`OptionContract`/`OptionQuote`/`OrderflowSnapshot`/`Trade` (`src/data/schemas.py`).
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3.
- **Regression baseline:** 103 passed in 108.63s (`test_real_tape_ingestion.py` 15 + `test_sample_adequacy_acquisition.py` 26 + `test_measurement_validity_evaluation.py` 19 + `test_exchange_exports.py` 20 + `test_options_exports.py` 23).
- **EVAL-25 artifacts:** `src/analytics/real_data_falsification.py`, `tests/test_real_data_falsification.py` (14 tests), `research_state/REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}` (`NO-GO`, 0 candidates, fingerprint `e783ccde8d5c6c97b26750244a53207e376e55371a5d7f868e3c2ce78f769dc3`).

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..EVAL-24A sealed; EVAL-25 SEALED code-complete (measured NO-GO, artifact `REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}`); real-data acquisition & gate re-validation pending.**
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.