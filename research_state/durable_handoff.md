# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-13T23:53:07Z (UTC).** Handoff refreshed/verified at HEAD `6235a05a4` (working tree dirty in this session: `src/data/exchange_exports.py`, `tests/test_exchange_exports.py`, `data/examples/exchange_exports/*`, `data/examples/normalized/*`, `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.{json,md}`, this handoff updated).
`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

**State (measured 2026-11-13T23:53Z):** EVAL-02..EVAL-22 **SEALED**. **EVAL-22 SEALED `NO-GO (no adequate real tape)`.** **EVAL-23B SEALED this session: adapter `PASS`, no real export, tape `NO-GO` on adequacy floors.** `.env` **ABSENT** (paper-only) — verified. `data/raw/` contains **only synthetic**: `orderflow_btcusdt_synthetic.json` (SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`; 1000 trades / 20 liq / 8 funding; 2026-10-31T06:16:23.656379Z→07:16:21.656379Z; venue `synthetic`, symbol `BTCUSDT`; 240 bars / 239 returns / **3 windows**) and `options_btc_synthetic.json` (30 quotes; internally inconsistent, EVAL-16). Real-tape discovery `data/raw` (excluding `*_synthetic*`) → **0 candidates**. No real tape, no real option chain. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` human-only, out of scope.

**NEXT FOCUS CAMPAIGN:** **EVAL-24A (ACTIVE) → EVAL-24 → EVAL-25.** Never idle; each session ships a module + tests + artifact.

---

## EVAL-23B EXCHANGE EXPORT ADAPTERS — SEALED 2026-11-13T23:53Z

- **Verdict:** adapter **PASS**; overall `NO-GO (no adequate real export)` — synthetic never substituted, no provenance fabricated.
- **Module:** `src/data/exchange_exports.py` — deterministic, offline, paper-only, no exchange/network calls.
  - Parses OKX / Binance / Deribit trade-export **CSV and JSON** into `Trade` / `OrderflowSnapshot`.
  - Strict timestamp parsing (ISO-8601, epoch s/ms/µs/ns; no `now()` fallback), strict finite/positive price/size, buy/sell sides, duplicate-id rejection, empty-export rejection.
  - Binance `IsBuyerMaker` / `isBuyerMaker` side inversion: maker-buyer ⇒ taker **sell**; otherwise taker **buy**.
  - Canonical trade order `(timestamp, trade_id, price, size, side)`; row-order-invariant fingerprint; deterministic auto ids for id-less exports.
  - `write_normalized_orderflow_tape(...)` emits loader-compatible `orderflow_<venue>_<symbol>_<UTC>.json`.
- **Tests:** `tests/test_exchange_exports.py` — **20 passed in 0.96s** (venue parsers, side semantics, strict timestamp/price/size/side rejection, empty/duplicate/synthetic-filename rejection, canonical order + fingerprint invariance, determinism, loader compatibility, directory/file tape emission, strict artifact/no `{"valid": true}`, adequacy GO/NO-GO, CLI artifacts).
- **Fixtures:** `data/examples/exchange_exports/okx_btcusdt_sample.csv`, `binance_btcusdt_sample.csv`, `deribit_btc_perpetual_sample.json` (format fixtures, not real data).
- **CLI:** `python3 -m src.data.exchange_exports --in data/examples/exchange_exports/okx_btcusdt_sample.csv --venue okx --symbol BTC-USDT --out research_state --data-dir data/examples/normalized --timestamp 2026-11-13T23:52:47Z` → RC 0.
- **Artifact:** `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.json`, `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.md` (`report_id=EXCHANGE_EXPORT_ADAPTERS_23B`, `data_provenance=exchange_export`, `authenticity_verified=false`, `adapter_verdict=PASS`, `overall_verdict=NO-GO`, `floors: min_returns=1000, min_windows=20, bar_duration_seconds=15.0`).
- **Normalized fixture tape:** `data/examples/normalized/orderflow_okx_BTCUSDT_20261113T235247Z.json` (3 trades; **not** a real tape; EVAL-22 must re-validate any real candidate).
- **Sealed EVAL regression:** `tests/test_real_tape_ingestion.py` + `tests/test_sample_adequacy_acquisition.py` + `tests/test_measurement_validity_evaluation.py` = **60 passed in 116.53s** (re-measured 2026-11-13T23:52Z).
- **Blocker removed:** trade-export acquisition is now code-complete and testable. EVAL-23 remains blocked by **data availability**, not by a missing parser.

---

## INITIAL TASK MESSAGE — 2026-11-13T23:53:07Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-13T23:53:07Z-EVAL-24A-OPTIONS-EXPORT-ADAPTERS`
**STATUS:** **ACTIVE, not started.** Start here — zero discovery needed.

> **Hard floor:** a session ending without new EVAL-24A artifacts (`src/data/options_exports.py` + `tests/test_options_exports.py` + `research_state/OPTIONS_EXPORT_ADAPTERS_<UTC>.{json,md}` + recorded verification evidence) is **FAILED**. Handoff-only work is FAILED. Adapters must be deterministic, offline parsers from exchange option-export formats to `OptionContract` / `OptionQuote` / `OptionsChain` (no network). If no real option export is available, ship adapters + fixtures/tests and seal an artifact documenting supported formats and readiness.

### Environment setup (verified)
Deps present in runner (re-verified 2026-11-13T23:53Z): Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3. If missing: `python3 -m pip install --quiet numpy pandas scipy pytest pyyaml pydantic requests websocket-client python-dateutil`. `python3 -m py_compile` + targeted `pytest` only (no mypy/ruff/flake8). **Never run the full suite (5297 tests). Never enumerate `research_state/` (75k files / ~5.0 GB).**

### Do now (heavy work required)
1. **Implement `src/data/options_exports.py`** — deterministic, offline, paper-only, **no network calls**.
   - Parse common OKX / Binance / Deribit **option trade and quote export** CSV/JSON into `src.data.schemas.OptionContract` / `OptionQuote` / `OptionsChain`.
   - Strict timestamp/expiry parsing (ISO-8601, epoch s/ms/µs/ns; no `now()` fallback); reject unparseable/empty.
   - Validate microstructure: strike > 0, expiry > timestamp, option_type in `call`/`put`, bid/ask finite and non-negative, bid <= ask (allow documented tiny tolerance or reject), IV/greeks finite or None, contract size > 0.
   - Canonicalize quote order `(timestamp, underlying, expiry, strike, option_type, symbol)` and reject duplicate `(symbol, timestamp)` / ambiguous contracts.
   - `parse_options_export(path, venue, underlying, format_hint=None) -> OptionsChain`; `write_normalized_options_chain(chain, out_path)` emitting loader-compatible `data/raw/options_<venue>_<underlying>_<UTC>.json`.
   - CLI: `python -m src.data.options_exports --in <file> --venue <okx|binance|deribit> --underlying <BTC> --out research_state/ [--data-dir data/examples/normalized]` producing `OPTIONS_EXPORT_ADAPTERS_<UTC>.{json,md}`.
2. **Write `tests/test_options_exports.py`** with **>=12 numeric-invariant tests**: OKX/Binance/Deribit fixtures parse correctly; contracts/quotes normalized; strict timestamp/expiry/strike/bid/ask/IV rejection; duplicate/ambiguous contract rejection; canonical order invariance; normalized output loadable by `DataLoader(cache=False).load_options_chain`; strict serialization/no `{"valid": true}`; determinism; CLI/artifact emission; adequacy/readiness reporting.
3. **Run and record verification:**
   - `python3 -m py_compile src/data/options_exports.py tests/test_options_exports.py`
   - `python3 -m pytest -q tests/test_options_exports.py`
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py tests/test_exchange_exports.py` (expect 80 passed incl. EVAL-23B 20)
4. **Seal in place:** update this handoff with measured verdict/checks/evidence/artifact paths and set next active task (**EVAL-24** only if an adequate real option chain now exists and passes the EVAL-24 validity gate; otherwise keep campaign advancing toward real-data acquisition/validation readiness per EVAL-25 dependencies as data allows). Commit partial work if incomplete — never leave a clean tree with EVAL-24A pending.

### Reuse / traps
- Reuse `src/data/loader.py` (`DataLoader(cache=False).load_options_chain`), `src/data/schemas.py` (`OptionContract`, `OptionQuote`, `OptionsChain`), `src/data/validators.py` (`validate_options_chain`), and EVAL-23B canonicalization/validation patterns in `src/data/exchange_exports.py`.
- `data/raw/options_btc_synthetic.json` is internally inconsistent (EVAL-16) and must never be relabeled as a real chain.
- Real option chain for EVAL-24 requires a venue export with enough strikes/expiries to validate surface/greeks consistency; a 30-quote synthetic fixture is not adequate.
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
| **EVAL-24A (ACTIVE)** | Options export adapters | **NOT STARTED** — ship adapters/fixtures/tests/CLI/artifact |
| **EVAL-23** | Real net-of-cost verdict | blocked on adequate real tape passing EVAL-22 |
| **EVAL-24** | Options-leg validity | blocked on real option chain; EVAL-24A unblocks acquisition |
| **EVAL-25** | Real-tape falsification | blocked on EVAL-23 |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If blocked by data, ship the acquisition/validation adapter and a measured NO-GO artifact; never substitute synthetic and never fabricate provenance.

---

## BOTTLENECK LEDGER

- **Removed this session:** EVAL-23B trade-export ingestion (code, tests, fixtures, artifact). Future sessions can acquire/normalize venue trade exports without writing a parser.
- **Remaining data bottleneck:** no real trade tape and no real option chain in `data/raw/`. EVAL-23 and EVAL-24 are data-blocked, not code-blocked. Acquisition requires a user/venue export; do not fabricate or relabel synthetic data.
- **Test bottleneck:** 878 test files / 5,297 tests. Run only the targeted files named above; never the full suite.
- **Workspace bottleneck:** `research_state/` is ~5.0 GB / 75k files (historical phaseNN trees). Never enumerate it; read exact paths only.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` SHA-256 `c75ced...cef7` (239 returns / 3 windows @15s). `data/raw/options_btc_synthetic.json` (30 quotes, venue `synthetic`, EVAL-16 inconsistent). `data/examples/exchange_exports/*` format fixtures. `data/examples/normalized/orderflow_okx_BTCUSDT_20261113T235247Z.json` normalized fixture (3 trades, not real).
- **EVAL-22 artifacts:** `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py` (15 tests), `research_state/REAL_TAPE_INGESTION_20261113T233551Z.{json,md}` (`NO-GO`, 0 candidates).
- **EVAL-23B artifacts:** `src/data/exchange_exports.py`, `tests/test_exchange_exports.py` (20 tests), `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.{json,md}` (`adapter PASS`, `NO-GO`).
- **Loader/schemas:** `DataLoader(cache=False).load_orderflow` (`src/data/loader.py:103`), `load_options_chain`; `OrderflowSnapshot`/`Trade` (`src/data/schemas.py`).
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3.
- **Regression baseline:** 80 passed in 116.23s (`test_real_tape_ingestion.py` 15 + `test_sample_adequacy_acquisition.py` 26 + `test_measurement_validity_evaluation.py` 19 + `test_exchange_exports.py` 20).

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..EVAL-22 sealed; EVAL-23B sealed; EVAL-24A ACTIVE.**
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.