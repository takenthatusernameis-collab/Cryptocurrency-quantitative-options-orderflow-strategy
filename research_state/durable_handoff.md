# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T02:04:19Z (UTC).** Handoff refreshed/verified at HEAD working tree 2026-11-14T02:04:19Z. Prior sealed artifacts: `src/data/options_exports.py`, `tests/test_options_exports.py`, `src/data/exchange_exports.py`, `tests/test_exchange_exports.py`, `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py`, `src/analytics/real_data_falsification.py`, `tests/test_real_data_falsification.py`, `data/examples/options_exports/*`, `data/examples/exchange_exports/*`, `data/examples/normalized/*`, `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.{json,md}`, `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.{json,md}`, `research_state/REAL_TAPE_INGESTION_20261113T233551Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T004500Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T014115Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T014525Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T015523Z.{json,md}`, `research_state/REAL_DATA_FALSIFICATION_20261114T020419Z.{json,md}`, `research_state/REAL_DATA_ACQUISITION_ATTEMPT_20261114T014525Z.md`, `research_state/REAL_DATA_ACQUISITION_ATTEMPT_20261114T020419Z.md`.
`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

**State (measured 2026-11-14T02:04:19Z):** EVAL-02..EVAL-24A **SEALED**. EVAL-25 **SEALED code-complete; measured NO-GO (0 real candidates)**. `.env` **ABSENT** (paper-only) — re-verified. `data/raw/` contains **only synthetic** (re-verified): `orderflow_btcusdt_synthetic.json` (222534 bytes, SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`; 1000 trades / 20 liq / 8 funding; venue `synthetic`, symbol `BTCUSDT`) and `options_btc_synthetic.json` (18273 bytes; 30 quotes, internally inconsistent EVAL-16). No non-`*_synthetic*` files in `data/raw/`.
**Gate re-run (no-write, 2026-11-14T02:04:19Z):** `python3 -m src.analytics.real_data_falsification --repo . --data-dir data/raw --no-write --timestamp 2026-11-14T02:04:19Z` → `overall_verdict=NO-GO`, `n_candidates=0`, `n_adequate_orderflow=0`, `n_adequate_options=0`, `canonical_fingerprint=5aaebcfcb56083014098992449414b413dcd38a694a1147e8f29171e1eac708c` (deterministic for state/timestamp). Written artifact (this session): `research_state/REAL_DATA_FALSIFICATION_20261114T020419Z.{json,md}` (`report_id=REAL_DATA_FALSIFICATION_25`, same fingerprint). Documented acquisition attempt: `research_state/REAL_DATA_ACQUISITION_ATTEMPT_20261114T020419Z.md` (data/raw+data inventory searched, no real non-synthetic export found, network acquisition refused by paper-only constraints). `research_state/NEXT9_APPROVAL_VALIDATION_*.json` human-only, out of scope.

**NEXT FOCUS CAMPAIGN:** **EVAL-25 (SEALED, code-complete) — real-data acquisition & gate re-validation (DATA-BLOCKED).** Gate is code-complete/testable; sole blocker is **data availability**. Every session must either (a) acquire/place a real venue orderflow tape + option export as non-`*_synthetic*` files in `data/raw/` and re-run `python -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw [--timestamp <UTC>]` producing a new `REAL_DATA_FALSIFICATION_<UTC>.{json,md}`, or (b) if still no real export, ship a refreshed measured NO-GO artifact (new timestamp) + re-verified regression and record the acquisition attempt. EVAL-23 / EVAL-24 unblock **only** when an adequate real tape passes EVAL-22 (`min_returns=1000, min_windows=20, bar_duration_seconds=15.0`) AND an adequate real option chain passes EVAL-24 (`min_contracts=8, min_quotes=8, min_expiries=2`) through this gate. Never idle, never relabel synthetic as real, never fabricate provenance, never emit `{"valid": true}`. Network acquisition refused (paper-only / no credentials).

---

## EVAL-24A EXCHANGE OPTION EXPORT ADAPTERS — SEALED 2026-11-14T00:45Z

- **Verdict:** adapter **PASS**; overall `NO-GO (no adequate real export)` — synthetic never substituted, no provenance fabricated.
- **Module:** `src/data/options_exports.py` — deterministic, offline, paper-only, no exchange/network calls.
  - Parses OKX / Binance / Deribit option trade & quote export CSV/JSON into `OptionContract` / `OptionQuote` / `OptionsChain`.
  - Strict timestamp + expiry parsing (ISO-8601, epoch s/ms/µs/ns; no `now()` fallback); reject unparseable/empty.
  - Microstructure validation: strike > 0, expiry > timestamp, option_type in `call`/`put` (inferred from symbol suffix when absent), bid/ask finite non-negative, bid <= ask (tolerance 1e-9), IV/greeks finite-or-None, contract_size > 0.
  - `parse_options_export(path, venue, underlying, format_hint=None) -> OptionsChain`; `write_normalized_options_chain(chain, out_path)` emits loader-compatible JSON.
- **Tests:** `tests/test_options_exports.py` — 23 passed. **Artifact:** `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.{json,md}` (`adapter_verdict=PASS`, `overall_verdict=NO-GO`, `canonical_fingerprint=52c27da9c3f13ab1...`).
- **Blocker removed:** option-chain acquisition is now code-complete/testable. EVAL-24 remains blocked by **data availability**.

---

## INITIAL TASK MESSAGE — 2026-11-14T02:04:19Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T02:04:19Z-EVAL-25-REAL-DATA-ACQUISITION-AND-GATE-REVALIDATION`
**STATUS:** **ACTIVE — DATA-BLOCKED but work-mandatory. Start here; zero discovery needed.** Gate is code-complete; next session must do real-data acquisition and/or a fresh measured gate run. No handoff-only session.
> **Hard floor:** a session ending without either (a) a re-run gate artifact showing real-data progress (adequate real tape + chain → GO, or refreshed `REAL_DATA_FALSIFICATION_<UTC>.{json,md}` NO-GO with a new timestamp) **or** (b) a documented acquisition attempt plus re-verified regression evidence is **FAILED**. Handoff-only work is FAILED. The gate `src/analytics/real_data_falsification.py` is already code-complete; the next session's heavy work is **real-data acquisition**: obtain a user/venue orderflow tape and option export, place them as non-`*_synthetic*` files under `data/raw/`, and re-run `python -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw [--timestamp <UTC>]`. EVAL-23 / EVAL-24 unblock **only** when an adequate real tape passes EVAL-22 (`min_returns=1000, min_windows=20, bar_duration_seconds=15.0`) AND an adequate real option chain passes EVAL-24 (`min_contracts=8, min_quotes=8, min_expiries=2`) through this gate. Never relabel synthetic as real; never fabricate provenance; never emit `{"valid": true}`.

### Environment setup (verified)

Deps present in runner (re-verified 2026-11-14T02:04Z): Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3. If missing: `python3 -m pip install --quiet numpy pandas scipy pytest pyyaml pydantic requests websocket-client python-dateutil`. `python3 -m py_compile` + targeted `pytest` only (no mypy/ruff/flake8). **Never run the full suite (5297 tests). Never enumerate `research_state/` (75k files / ~5.0 GB).**

### Do now (heavy work required)

1. **Attempt real-data acquisition (mandatory).** Place a real venue orderflow tape (`orderflow_<venue>_<symbol>.json`) and/or real option export (`options_<venue>_<underlying>_<UTC>.json`) under `data/raw/` — file names must NOT contain `synthetic`. For each candidate, ensure it can pass `DataLoader`/validators and adequacy floors (orderflow: EVAL-22 `min_returns=1000, min_windows=20, bar_duration_seconds=15.0`; options: EVAL-24 `min_contracts=8, min_quotes=8, min_expiries=2`). Use `src/data/exchange_exports.py` / `src/data/options_exports.py` to normalize venue CSV/JSON exports. If no user/venue export is provided in-session, record a concrete acquisition attempt with what was sought, what was checked (repo `data/` + exact discovery scope), and the blocker.
2. **Run the gate and produce artifacts:** `python -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw [--timestamp <UTC>]` producing a new `REAL_DATA_FALSIFICATION_<UTC>.{json,md}` (or `--no-write` for a pre-check, but session must end with a written artifact unless impossible). Record `overall_verdict`, `n_candidates`, `n_adequate_orderflow`, `n_adequate_options`, `canonical_fingerprint`. If data now yields GO, immediately plan/execute EVAL-23 (real net-of-cost) / EVAL-24 (options-leg validity) on those validated inputs.
3. **Run and record verification:**
   - `python3 -m py_compile src/analytics/real_data_falsification.py tests/test_real_data_falsification.py` → **exit 0** (2026-11-14T02:04:19Z)
   - `python3 -m pytest -q tests/test_real_data_falsification.py` → **14 passed in 0.83s**
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py tests/test_exchange_exports.py tests/test_options_exports.py` → **103 passed in 109.22s** (combined 117)
4. **Seal in place:** update this handoff with the measured verdict/checks/evidence/artifact paths, new task timestamp/id, and set the next active task (EVAL-23 / EVAL-24 only if an adequate real export now exists and passes the EVAL-25 gate; otherwise keep campaign on real-data acquisition with explicit next action). Commit partial work if incomplete — never leave a clean tree with EVAL-25 pending. A handoff-only session is FAILED.

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
| **EVAL-22** | Real-tape ingestion gate | **SEALED NO-GO** (no adequate real tape) |
| **EVAL-23B** | Exchange export adapters (trade) | **SEALED** — adapter PASS; no real export |
| **EVAL-24A** | Options export adapters | **SEALED** — adapter PASS; no real export |
| **EVAL-25** | Real-data acquisition & falsification gate re-validation | **ACTIVE / DATA-BLOCKED** — gate code-complete; measured NO-GO re-verified 2026-11-14T02:04:19Z (`n_candidates=0, n_adequate_orderflow=0, n_adequate_options=0, fingerprint 5aaebcfc…`). Artifact: `REAL_DATA_FALSIFICATION_20261114T020419Z.{json,md}`. Attempt: `REAL_DATA_ACQUISITION_ATTEMPT_20261114T020419Z.md`. Next: acquire real non-synthetic exports → new `REAL_DATA_FALSIFICATION_<UTC>.{json,md}`; unblock EVAL-23/24 only on adequate pass |
| **EVAL-23** | Real net-of-cost verdict | blocked on adequate real tape passing EVAL-22 |
| **EVAL-24** | Options-leg validity | blocked on real option chain; EVAL-24A unblocks acquisition |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If blocked by data, ship the acquisition/validation adapter and a measured NO-GO artifact; never substitute synthetic and never fabricate provenance.

---

## BOTTLENECK LEDGER

- **Removed this session (2026-11-14T02:04:19Z):** performed mandatory acquisition attempt (data/raw + data inventory re-verified, no real non-synthetic export found), re-ran gate (no-write + written) producing fresh `REAL_DATA_FALSIFICATION_20261114T020419Z.{json,md}` with deterministic fingerprint `5aaebcfc…`, re-verified regressions: py_compile exit 0, `test_real_data_falsification.py` 14 passed, sealed baseline 103 passed (117 total). Canonical handoff refreshed as single durable task source.
- **Remaining data bottleneck (primary):** no real trade tape and no real option chain in `data/raw/`. EVAL-23/EVAL-24 are data-blocked, not code-blocked. Requires user/venue export (credentials/network not available in sandbox). Do not fabricate or relabel synthetic data.
- **Test bottleneck:** 878 test files / 5,297 tests. Run only targeted files; never the full suite.
- **Workspace bottleneck:** `research_state/` is ~5.0 GB / 75k files. Never enumerate it; read exact paths only.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` SHA-256 `c75ced...cef7`; `data/raw/options_btc_synthetic.json` (synthetic, EVAL-16 inconsistent). `data/examples/*` format/normalized fixtures only. No real non-synthetic candidate in `data/raw/`.
- **EVAL-22:** `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py`, `research_state/REAL_TAPE_INGESTION_20261113T233551Z.{json,md}` (NO-GO).
- **EVAL-23B:** `src/data/exchange_exports.py`, `tests/test_exchange_exports.py`, `research_state/EXCHANGE_EXPORT_ADAPTERS_20261113T235247Z.{json,md}` (adapter PASS, NO-GO).
- **EVAL-24A:** `src/data/options_exports.py`, `tests/test_options_exports.py`, `research_state/OPTIONS_EXPORT_ADAPTERS_20261114T004500Z.{json,md}` (adapter PASS, NO-GO).
- **EVAL-25:** `src/analytics/real_data_falsification.py`, `tests/test_real_data_falsification.py` (14). Latest artifact: `research_state/REAL_DATA_FALSIFICATION_20261114T020419Z.{json,md}` (`NO-GO`, 0 candidates, fingerprint `5aaebcfc…`). Prior: `004500Z`, `014115Z`, `014525Z`, `015523Z`. Attempts: `REAL_DATA_ACQUISITION_ATTEMPT_20261114T014525Z.md`, `REAL_DATA_ACQUISITION_ATTEMPT_20261114T020419Z.md`.
- **Loader/schemas:** `DataLoader(cache=False).load_orderflow` / `load_options_chain` (`src/data/loader.py`); `OptionsChain`/`OptionContract`/`OptionQuote`/`OrderflowSnapshot`/`Trade` (`src/data/schemas.py`); validators `src/data/validators.py`.
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3.
- **Regression baseline (this session):** py_compile exit 0; 14 passed (gate) + 103 passed (sealed baseline) = **117 passed**.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..EVAL-24A sealed; EVAL-25 code-complete (measured NO-GO, latest `REAL_DATA_FALSIFICATION_20261114T020419Z.{json,md}`); real-data acquisition & gate re-validation pending.**
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
