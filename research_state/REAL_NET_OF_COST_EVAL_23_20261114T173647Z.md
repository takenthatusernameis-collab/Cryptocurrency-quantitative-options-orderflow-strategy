# REAL_NET_OF_COST_EVAL_23 — REAL NET-OF-COST EVALUATION (paper-only)

**Generated:** 2026-11-14T17:36:47Z
**Verdict:** **NO-GO** (8/11 checks)
**Data provenance:** `real` (authenticity_verified=false)
**Venue:** okx · **orderflow:** BTC

## Measured evidence

| Metric | Value |
|---|---|
| real trades | 84800 |
| real bars | 1602 |
| option quotes / contracts | 827 |
| expiries / strikes | 14 / 93 |
| spot used | 67028.5 |
| combined IC mean | -2.902292e-02 |
| orderflow IC mean | -1.008665e-02 |
| options IC mean | -3.965946e-18 |
| combined OOS Sharpe | 1.8584 |
| combined OOS return | 0.2901 |
| combined trades / cost USD | 232 / 415.64 |
| orderflow-only Sharpe | -5.3493 |
| orderflow-only trades | 614 |
| options leg degenerate | true |

## Fusion adjudication

- sealed rule unchanged: `True`
- flat because options degenerate: `false`
- Both pillars produced time variation; the fusion rule is not the binding constraint.

## Checks

| Check | Pass | Observed | Reason |
|---|---|---|---|
| options_signal_exists | false | 3.96595e-18 | FAIL: options mean IC -3.965946e-18 indistinguishable from zero (<= 1e-09) |
| orderflow_signal_exists | true | 0.0100867 | PASS: orderflow mean IC -1.008665e-02 nonzero (> 1e-09) |
| combined_ic_significant | true | 1.80668 | PASS: combined IC significant (/t/=1.8067 > 1.96, permutation p=0.0010) |
| combined_net_of_cost_superior | false | -2.38764 | FAIL: combined not superior (combined 1.858414 vs options 4.246051, orderflow -5.349272, flat 0.000000; cost applied True) |
| toxicity_gate_measured | true | 0.857231 | PASS: toxicity mean 0.8572 in (0,1), gate engages fraction 0.8065 (measured EVAL-17 VPIN) |
| no_lookahead_asserted | true | 1 | PASS: causal no-lookahead signal asserted and tested |
| guardrails_consistent_with_eval13_14_15 | true | 1 | PASS: guardrails consistent (delta band ±323.77 USD around -20000.0, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 0.2/tox 0.8/cost 5.0 bps, max notional 1000000.0 USD, max daily loss 50000.0 USD) |
| real_data_provenance | true | 1 | PASS: inputs loaded from real OKX public exports (no synthetic fallback) |
| real_data_adequate | true | 1 | PASS: 84800 trades / 1602 bars, 827 quotes / 14 expiries / 93 strikes |
| orderflow_signal_non_degenerate | true | 0.0100867 | PASS: orderflow mean IC -1.008665e-02 nonzero (> 1e-09) |
| options_signal_tradable | false | 0 | FAIL: options leg degenerate — options signal is constant across bars (stdev 0.000e+00 <= 1.0e-12): the real chain is a single cross-section, so broadcasting it produces no time variation; options IC magnitude 3.966e-18 <= 1.0e-12: no measured relation to forward returns |

## Provenance / constraints

- Real OKX public read-only exports; no `.env`, no credentials, no order placement.
- `authenticity_verified=false`: no signed venue attestation; tape is inverse BTC-USD-SWAP, chain is spot.
- Never emits `{"valid": true}`. A trustworthy NO-GO is a full success.
