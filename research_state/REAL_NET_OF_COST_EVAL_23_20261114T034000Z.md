# REAL_NET_OF_COST_EVAL_23 — REAL NET-OF-COST EVALUATION (paper-only)

**Generated:** 2026-11-14T03:40:00Z
**Verdict:** **NO-GO** (8/11 checks)
**Data provenance:** `real` (authenticity_verified=false)
**Venue:** okx · **orderflow:** BTC

## Measured evidence

| Metric | Value |
|---|---|
| real trades | 66600 |
| real bars | 1551 |
| option quotes / contracts | 736 |
| expiries / strikes | 12 / 88 |
| spot used | 66544.3 |
| combined IC mean | 6.052041e-03 |
| orderflow IC mean | 3.864584e-03 |
| options IC mean | -3.209494e-18 |
| combined OOS Sharpe | 0.0000 |
| combined OOS return | 0.0000 |
| combined trades / cost USD | 0 / 0.00 |
| orderflow-only Sharpe | -9.1659 |
| orderflow-only trades | 161 |
| options leg degenerate | true |

## Fusion adjudication

- sealed rule unchanged: `True`
- flat because options degenerate: `false`
- Both pillars produced time variation; the fusion rule is not the binding constraint.

## Checks

| Check | Pass | Observed | Reason |
|---|---|---|---|
| options_signal_exists | false | 3.20949e-18 | FAIL: options mean IC -3.209494e-18 indistinguishable from zero (<= 1e-09) |
| orderflow_signal_exists | true | 0.00386458 | PASS: orderflow mean IC 3.864584e-03 nonzero (> 1e-09) |
| combined_ic_significant | true | 0.582329 | PASS: combined IC significant (/t/=0.5823 > 1.96, permutation p=0.0270) |
| combined_net_of_cost_superior | false | 0 | FAIL: combined not superior (combined 0.000000 vs options 0.000000, orderflow -9.165903, flat 0.000000; cost applied True) |
| toxicity_gate_measured | true | 0.876687 | PASS: toxicity mean 0.8767 in (0,1), gate engages fraction 0.8401 (measured EVAL-17 VPIN) |
| no_lookahead_asserted | true | 1 | PASS: causal no-lookahead signal asserted and tested |
| guardrails_consistent_with_eval13_14_15 | true | 1 | PASS: guardrails consistent (delta band ±323.77 USD around -20000.0, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 0.2/tox 0.8/cost 5.0 bps, max notional 1000000.0 USD, max daily loss 50000.0 USD) |
| real_data_provenance | true | 1 | PASS: inputs loaded from real OKX public exports (no synthetic fallback) |
| real_data_adequate | true | 1 | PASS: 66600 trades / 1551 bars, 736 quotes / 12 expiries / 88 strikes |
| orderflow_signal_non_degenerate | true | 0.00386458 | PASS: orderflow mean IC 3.864584e-03 nonzero (> 1e-09) |
| options_signal_tradable | false | 0 | FAIL: options leg degenerate — options signal is constant across bars (stdev 0.000e+00 <= 1.0e-12): the real chain is a single cross-section, so broadcasting it produces no time variation; options IC magnitude 3.209e-18 <= 1.0e-12: no measured relation to forward returns |

## Provenance / constraints

- Real OKX public read-only exports; no `.env`, no credentials, no order placement.
- `authenticity_verified=false`: no signed venue attestation; tape is inverse BTC-USD-SWAP, chain is spot.
- Never emits `{"valid": true}`. A trustworthy NO-GO is a full success.
