# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for next agentic work session): 2026-11-13T22:42:24Z (UTC).** Handoff refreshed/verified: 2026-11-13T23:36:40Z (UTC) at HEAD `e09902e86` (working tree dirty in this session: `src/analytics/real_tape_ingestion.py` modified, `tests/test_real_tape_ingestion.py` added, EVAL-22 artifacts added, this handoff updated).
`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

**State (measured 2026-11-13T23:36Z):** EVAL-02..EVAL-21 **SEALED**. **EVAL-22 SEALED (this session): `NO-GO (no adequate real tape)`**. `.env` **ABSENT** (paper-only) — verified. `data/raw/` contains **only synthetic**: `orderflow_btcusdt_synthetic.json` (SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`; 1000 trades / 20 liq / 8 funding; 2026-10-31T06:16:23.656379Z→07:16:21.656379Z; venue `synthetic`, symbol `BTCUSDT`; 240 bars / 239 returns / **3 windows**) and `options_btc_synthetic.json` (30 quotes; internally inconsistent, EVAL-16). Real-tape discovery `data/raw` (excluding `*_synthetic*`) → **0 candidates**. No real tape. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` human-only, out of scope.

**NEXT FOCUS CAMPAIGN:** **EVAL-23B (ACTIVE) → EVAL-23 → EVAL-24 → EVAL-25.** Never idle; each session ships a module + tests + artifact.

---

## EVAL-22 REAL-TAPE INGESTION — SEALED 2026-11-13T23:36Z

- **Verdict:** `NO-GO (no adequate real tape)` — synthetic never substituted.
- **Discovery:** `discover_real_orderflow_tapes('data/raw')` → `[]` (1 synthetic file excluded). `n_candidates=0`, `n_adequate=0`.
- **Module:** `src/analytics/real_tape_ingestion.py` — deterministic, offline, paper-only, no exchange/network calls. Discovery excludes `*synthetic*`, strict `_parse_ts` (no `now()` fallback), `cache=False` loader, canonical trade ordering for row-order-invariant bars, time-truncation causal check (not vacuous row-removal), microstructure/venue/symbol/provenance validation, sealed EVAL-20 primitives for adequate real tapes, strict serialization/no `{"valid": true}`. Small hardening applied this session: `_parse_ts` now wraps `fromisoformat` failures as `RealTapeRejected`.
- **Tests:** `tests/test_real_tape_ingestion.py` — **15 passed in 0.89s** (numeric invariants: discovery filter/sort, provenance, synthetic-venue/bad-filename/empty/unparseable/microstructure rejection, causal time-truncation invariance, row-order/canonical-fingerprint invariance, inadequate-tape NO-GO with exact shortfall, overall NO-GO when no real tapes, strict serialization/no `valid`, determinism, CLI writes json+md).
- **CLI:** `python -m src.analytics.real_tape_ingestion --out research_state --data-dir data/raw --timestamp 2026-11-13T23:35:51Z` → RC 0.
- **Artifacts:** `research_state/REAL_TAPE_INGESTION_20261113T233551Z.json`, `research_state/REAL_TAPE_INGESTION_20261113T233551Z.md` (`report_id=REAL_TAPE_INGESTION_22`, `data_provenance=real`, `overall_verdict=NO-GO`, `floors: min_returns=1000, min_windows=20, bar_duration_seconds=15`).
- **Regression baseline:** `tests/test_sample_adequacy_acquisition.py` + `tests/test_measurement_validity_evaluation.py` = **45 passed in 114.43s** (re-measured 2026-11-13T23:36Z).
- **Measured shortfall (current real-tape availability):** no real candidates in `data/raw/`; cannot satisfy `n_returns >= 1000` and `n_windows >= 20` (>=1001 bars @15s, ~4.2h continuous prints). Synthetic tape provides only 239 returns / 3 windows (shortfall 761 / 17) and must never be substituted.

---

## INITIAL TASK MESSAGE — 2026-11-13T23:36:40Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-13T23:36:40Z-EVAL-23B-EXCHANGE-EXPORT-ADAPTERS`
**STATUS:** **ACTIVE, not started.** Start here — zero discovery needed.

> **Hard floor:** a session ending without new EVAL-23B artifacts (`src/data/exchange_exports.py` + `tests/test_exchange_exports.py` + `research_state/EXCHANGE_EXPORT_ADAPTERS_<UTC>.{json,md}` + recorded verification evidence) is **FAILED**. Handoff-only work is FAILED. Adapters must be deterministic, offline parsers from exchange trade-export formats to `OrderflowSnapshot` (no network). If no real export is available, ship adapters + fixtures/tests and seal an artifact documenting supported formats and readiness.

### Environment setup (verified)
Deps present in runner (re-verified 2026-11-13T23:36Z): Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3. If missing: `python3 -m pip install --quiet numpy pandas scipy pytest pyyaml pydantic requests websocket-client python-dateutil`. `python3 -m py_compile` + targeted `pytest` only (no mypy/ruff/flake8). **Never run the full suite (5297 tests). Never enumerate `research_state/`.**

### Do now (heavy work required)
1. **Implement `src/data/exchange_exports.py`** — deterministic, offline, paper-only, **no network calls**.
   - Parse common OKX/Binance/Deribit trade-export CSV/JSON into `src.data.schemas.Trade` / `OrderflowSnapshot` (venue, symbol, timestamp, price, size, side buy/sell, trade_id). Use strict timestamp parsing (raise on unparseable, no `now()` fallback). Canonicalize trade order `(timestamp, trade_id, price, size, side)`.
   - `parse_exchange_export(path, venue, symbol, format_hint=None) -> OrderflowSnapshot`; `write_normalized_orderflow_tape(snapshot, out_path)` emitting loader-compatible `data/raw/orderflow_<venue>_<symbol>_<UTC>.json`.
   - Validate microstructure (price>0, size>0, side in buy/sell, monotone non-decreasing after sort) and reject empty tapes. CLI: `python -m src.data.exchange_exports --in <file> --venue <okx|binance|deribit> --symbol <SYM> --out research_state/ [--data-dir data/raw]` producing `EXCHANGE_EXPORT_ADAPTERS_<UTC>.{json,md}`.
2. **Write `tests/test_exchange_exports.py`** with **>=12 numeric-invariant tests**: OKX/Binance/Deribit fixtures parse correctly; timestamps/prices/sizes/sides/trade_ids normalized; bad timestamp/price/size/side/empty rejected; canonical sort/order invariance; normalized output loadable by `DataLoader(cache=False).load_orderflow`; strict serialization/no `{"valid": true}`; determinism; CLI/artifact emission.
3. **Run and record verification:**
   - `python3 -m py_compile src/data/exchange_exports.py tests/test_exchange_exports.py`
   - `python3 -m pytest -q tests/test_exchange_exports.py`
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py` (expect 60 passed incl. EVAL-22 15)
4. **Seal in place:** update this handoff with measured verdict/checks/evidence/artifact paths and set next active task (**EVAL-23** only if an adequate real tape now exists and passes EVAL-22 gate; otherwise keep campaign advancing toward real-tape acquisition/validation readiness per EVAL-24/EVAL-25 dependencies as data allows). Commit partial work if incomplete — never leave a clean tree with EVAL-23B pending.

### Reuse / traps
- Reuse `src/data/loader.py` (`DataLoader(cache=False).load_orderflow`), `src/data/schemas.py` (`Trade`, `OrderflowSnapshot`), and EVAL-22 canonicalization/validation patterns in `src/analytics/real_tape_ingestion.py` (do not modify sealed EVAL modules). Do **not** trust loader `_parse_dt` `now()` fallback — parse timestamps yourself.
- Adequate real tape for EVAL-23 requires **>=1000 returns and >=20 windows** (>=1001 bars @15s). EVAL-22 CLI: `python -m src.analytics.real_tape_ingestion --out research_state --data-dir data/raw`.
- `data/raw` currently synthetic-only; discovery excludes `*synthetic*`. Normalized real tapes must not contain `synthetic` in venue/name and must have provenance distinguishable from SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs. Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`.
- `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only, out of scope.

---

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| **EVAL-02..EVAL-21** | Sealed prior gates | **SEALED** |
| **EVAL-22** | Real-tape ingestion gate | **SEALED NO-GO** (no adequate real tape; module+tests+artifact) |
| **EVAL-23B (ACTIVE)** | Exchange export adapters (fallback) | **NOT STARTED** — ship adapters/fixtures/tests/CLI/artifact |
| **EVAL-23** | Real net-of-cost verdict | blocked on adequate real tape passing EVAL-22 |
| **EVAL-24** | Options-leg validity | blocked on real option chain; ship validator+tests+NO-GO if absent |
| **EVAL-25** | Real-tape falsification | blocked on EVAL-23 |

**Campaign rule:** each session ships at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` SHA-256 `c75ced...cef7` (239 returns / 3 windows @15s). `data/raw/options_btc_synthetic.json` (30 quotes, venue `synthetic`, EVAL-16 inconsistent).
- **EVAL-22 artifacts:** `src/analytics/real_tape_ingestion.py`, `tests/test_real_tape_ingestion.py` (15 tests), `research_state/REAL_TAPE_INGESTION_20261113T233551Z.{json,md}` (`NO-GO`, 0 candidates).
- **Loader/schemas:** `DataLoader(cache=False).load_orderflow` (`src/data/loader.py:103`), `OrderflowSnapshot`/`Trade` (`src/data/schemas.py`).
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3.
- **Regression baseline:** 45 passed in 114.43s (EVAL-20 26 + EVAL-21 19), plus EVAL-22 15 = 60 targeted tests green this session.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Queue: **EVAL-02..EVAL-22 sealed (EVAL-22 NO-GO no adequate real tape). EVAL-23B ACTIVE.**
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
