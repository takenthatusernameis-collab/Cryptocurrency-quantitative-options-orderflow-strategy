# REAL_DATA_FALSIFICATION_25 — REAL_DATA_FALSIFICATION (EVAL-25)

- generated_at: 2026-11-14T01:41:15Z
- overall_verdict: **NO-GO**
- reason: no real-data candidates under data/raw/ (all exports are synthetic or absent); synthetic never substituted
- trading_mode: paper
- data_provenance: real (authenticity_verified=false)
- repo_root: `.`
- data_dir: `data/raw`
- candidates discovered: 0 (orderflow 0, options 0)
- adequate real: orderflow 0, options 0
- floors: {'min_returns': 1000, 'min_windows': 20, 'bar_duration_seconds': 15.0, 'min_contracts': 8, 'min_quotes': 8, 'min_expiries': 2}
- canonical_fingerprint: `e783ccde8d5c6c97b26750244a53207e376e55371a5d7f868e3c2ce78f769dc3`

## Candidates

## Readiness

Offline deterministic gate; no network, no ``.env``, no live trading. Synthetic is never relabeled as real and the artifact never contains ``{"valid": true}``. A GO requires at least one adequate real orderflow tape AND at least one adequate real option chain; otherwise NO-GO stands and EVAL-23 / EVAL-24 remain data-blocked.
