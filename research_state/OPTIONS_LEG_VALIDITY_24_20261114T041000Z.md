# OPTIONS_LEG_VALIDITY_24 — REAL OPTIONS-LEG VALIDITY (paper-only)

**Generated:** 2026-11-14T04:10:00Z
**Verdict:** **NO-GO** (3/8 checks)
**Options leg degenerate:** `true`
**Venue:** okx · **spot:** 66825.3

## Measured evidence

| Metric | Value |
|---|---|
| quotes / strikes / expiries | 728 / 88 / 12 |
| calls / puts | 339 / 389 |
| venue IV coverage | 0.00% |
| venue greeks coverage | 0.00% |
| open interest coverage | 0.00% |
| positive mid coverage | 100.00% |
| surface points / expiries | 728 / 12 |
| butterfly / calendar violations | 0 / 1 |
| analytic-vs-FD match (delta/vega) | 0.9245 / 0.9698 |
| ATM tenors | 12 (stdev 0.0021) |
| risk-reversal tenors | 10 (mean -0.0110) |
| GEX raw / enriched | 0.00 / 0.00 |
| put-call ratio | 1.0316 |

## ATM term structure (solved IV)

| tenor (years) | ATM IV |
|---|---|
| 0.002292 | 0.0111 |
| 0.005030 | 0.0077 |
| 0.007768 | 0.0063 |
| 0.015981 | 0.0046 |
| 0.035146 | 0.0040 |
| 0.054311 | 0.0033 |
| 0.111806 | 0.0066 |
| 0.207631 | 0.0074 |
| 0.284291 | 0.0044 |
| 0.360951 | 0.0058 |
| 0.610095 | 0.0067 |
| 0.859239 | 0.0057 |

## Checks

| Check | Pass | Observed | Reason |
|---|---|---|---|
| chain_richness | true | 728 | PASS: 728 quotes, 88 strikes, 12 expiries, 100.00% positive mids |
| surface_reconstructed | false | 0.472747 | FAIL: surface points=728, IV range [0.0000, 0.4727] |
| surface_calibration_residual | true | 0 | PASS: residual max abs 0.000e+00 <= 1.0e-06 |
| surface_arbitrage_free | false | 1 | FAIL: 1 violations |
| greeks_analytic_vs_finite_difference | false | 0.924451 | FAIL: match fraction 0.9245 < 0.99 |
| put_call_parity | false | 133173 | FAIL: 338 pairs, parity residual max abs 133172.8503 |
| term_structure_non_degenerate | true | 12 | PASS: 12 ATM tenors, stdev 0.0021 |
| options_leg_tradable | false | 0 | FAIL: options leg cannot produce a time-varying tradable signal (term structure varies=True, enriched GEX non-zero=False) |

## Provenance / constraints

- Real OKX public read-only export; no `.env`, no credentials, no order placement.
- `authenticity_verified=false`: no signed venue attestation.
- The venue ships no IV/greeks/OI for this snapshot; IV is solved from mid prices.
- Never emits `{"valid": true}`. A trustworthy NO-GO is a full success.
