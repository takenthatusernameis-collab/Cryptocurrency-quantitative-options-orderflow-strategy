# REAL-DATA ACQUISITION ATTEMPT — EVAL-25 (2026-11-14T02:04:19Z)

## Outcome: NO REAL DATA ACQUIRED — DOCUMENTED ATTEMPT (paper-only)

Session performed mandatory acquisition attempt for the
`Cryptocurrency-quantitative-options-orderflow-strategy` repo: searched for a real
venue orderflow tape and/or real option-chain export to place under `data/raw/`
with non-`*_synthetic*` filenames, then re-ran the EVAL-25 falsification gate.

**No real data was acquired.** Gate is code-complete; blocker remains **data availability**.

## Acquisition checks (offline, paper-only)

1. **`data/raw/` inventory (re-verified):** only
   - `orderflow_btcusdt_synthetic.json` (222534 bytes, SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`, venue `synthetic`, 1000 trades / 20 liq / 8 funding)
   - `options_btc_synthetic.json` (18273 bytes, venue `synthetic`, internally inconsistent per EVAL-16)
   No non-`*_synthetic*` candidates.
2. **`data/` discovery (all 27 tracked/example data files reviewed by path):**
   `data/processed/*.json` are aggregate summaries only (e.g. `num_trades`, `num_quotes`, `put_call_ratio`) with no raw reconstructable trade tape or option chain.
   `data/examples/exchange_exports/*`, `data/examples/options_exports/*`, `data/examples/normalized/*` are format/normalized fixtures, not real venue exports.
3. **Repository-wide candidate search:** no real orderflow/options export files found outside known synthetic/fixture locations for ingestion as `data/raw/` non-synthetic candidates.
4. **Network acquisition:** not performed/refused by hard constraints — `.env` absent, `LIVE_TRADING_ENABLED=false`, paper-only, no venue credentials/config, no exchange network calls permitted. Gate CLI additionally blocks outbound socket connections.

## Gate re-run (measured)

- Command (no-write pre-check): `python3 -m src.analytics.real_data_falsification --repo . --data-dir data/raw --no-write --timestamp 2026-11-14T02:04:19Z`
  - `overall_verdict=NO-GO`, `n_candidates=0`, `n_adequate_orderflow=0`, `n_adequate_options=0`
  - `canonical_fingerprint=5aaebcfcb56083014098992449414b413dcd38a694a1147e8f29171e1eac708c`
- Written artifact: `python3 -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw --timestamp 2026-11-14T02:04:19Z`
  - `research_state/REAL_DATA_FALSIFICATION_20261114T020419Z.json`
  - `research_state/REAL_DATA_FALSIFICATION_20261114T020419Z.md`
  - `report_id=REAL_DATA_FALSIFICATION_25`, `overall_verdict=NO-GO`, `n_candidates=0`, `n_adequate_orderflow=0`, `n_adequate_options=0`, `data_provenance=real`, `authenticity_verified=false`, `never_valid_true=true`

## Verification (measured this session)

- `python3 -m py_compile src/analytics/real_data_falsification.py tests/test_real_data_falsification.py` → exit 0
- `python3 -m pytest -q tests/test_real_data_falsification.py` → (see handoff)
- `python3 -m pytest -q tests/test_real_tape_ingestion.py tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py tests/test_exchange_exports.py tests/test_options_exports.py` → (see handoff)

## Blocker / next action

EVAL-23 and EVAL-24 remain **data-blocked, not code-blocked**. To unblock: place a real venue orderflow tape and/or real option export as non-`*_synthetic*` files in `data/raw/` (or normalize via `src/data/exchange_exports.py` / `src/data/options_exports.py`), re-run `python -m src.analytics.real_data_falsification --repo . --out research_state/ --data-dir data/raw [--timestamp <UTC>]`, and only advance EVAL-23/EVAL-24 when at least one adequate real tape passes EVAL-22 (`min_returns=1000, min_windows=20, bar_duration_seconds=15.0`) AND one adequate real option chain passes EVAL-24 (`min_contracts=8, min_quotes=8, min_expiries=2`). Never relabel synthetic as real; never fabricate provenance; never emit `{"valid": true}`.
