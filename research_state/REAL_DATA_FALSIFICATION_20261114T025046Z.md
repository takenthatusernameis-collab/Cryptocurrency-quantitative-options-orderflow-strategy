# REAL_DATA_FALSIFICATION_25 — REAL_DATA_FALSIFICATION (EVAL-25)

- generated_at: 2026-11-14T02:50:46Z
- overall_verdict: **GO**
- reason: adequate real orderflow tape(s) and option chain(s) passed the EVAL-22 / EVAL-24 adequacy floors
- trading_mode: paper
- data_provenance: real (authenticity_verified=false)
- repo_root: `.`
- data_dir: `data/raw`
- candidates discovered: 2 (orderflow 1, options 1)
- adequate real: orderflow 1, options 1
- floors: {'min_returns': 1000, 'min_windows': 20, 'bar_duration_seconds': 15.0, 'min_contracts': 8, 'min_quotes': 8, 'min_expiries': 2}
- canonical_fingerprint: `fc5b24c2f4e79333faaad5b4f98de90a99ef2046d82f9dd07f4ef2a31bd521ca`

## Candidates

### `options_okx_BTC_20261114T024736Z.json` (options)
- venue/symbol: `okx` / `BTC`
- content_sha256: `268bf34ef8a1099e…`
- verdict: **GO** — option chain clears EVAL-24 adequacy floors
- option adequacy (EVAL-24): 739/8 contracts, 739/8 quotes, 12/2 expiries, adequate=true

### `orderflow_okx_BTC-USD-SWAP.json` (orderflow)
- venue/symbol: `okx` / `BTCUSDSWAP`
- content_sha256: `865d2e06157331bb…`
- verdict: **GO** — orderflow tape clears EVAL-22 adequacy floors
- trade adequacy (EVAL-22): 1551/1000 returns, 35/20 windows, adequate=true

## Readiness

Offline deterministic gate; no network, no ``.env``, no live trading. Synthetic is never relabeled as real and the artifact never contains ``{"valid": true}``. A GO requires at least one adequate real orderflow tape AND at least one adequate real option chain; otherwise NO-GO stands and EVAL-23 / EVAL-24 remain data-blocked.
