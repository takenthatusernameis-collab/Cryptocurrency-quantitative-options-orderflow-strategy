# FINAL_STRATEGY_FALSIFICATION_34 — Final consolidated strategy falsification + portfolio decision (EVAL-34)

- **Report ID:** `FINAL_STRATEGY_FALSIFICATION_34`
- **Generated:** 2026-11-14T13:54:16.022445Z
- **Task ID:** `INIT-2026-11-14T13:54:16.022445Z-EVAL-34-FINAL-STRATEGY-FALSIFICATION`
- **Verdict:** **NO-GO**
- **Reason:** options+orderflow combined is NOT net-of-cost tradable; deploy orderflow-only with caveats (options leg terminated as zero-alpha cost center)
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.
- Caveat: Paper-only; no live trading; .env absent.
- Caveat: authenticity_verified=false.

## Eval Chain Consolidated (EVAL-23 through EVAL-33)

| Eval | Report ID | Verdict | Sharpe | Trades | Cost USD | Key Reason |
|------|-----------|---------|--------|--------|----------|------------|
| EVAL-23 | REAL_NET_OF_COST_EVAL_23 | NO-GO | 4.701791314886216 | 219.0 | $364.40 | Combined IC mean -0.0168 adverse (|t|=4.10, p=0.0020); options leg degenerate (constant broadcast, IC=0.0); fusion adds no measurable net-of-cost edge. |
| EVAL-24 | OPTIONS_LEG_VALIDITY_24 | NO-GO | n/a | n/a | $0.00 | Parity-consistent but options_leg_tradable FAIL; venue IV/greeks/OI coverage 0%. |
| EVAL-27 | OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z | NO-GO | n/a | n/a | $0.00 | Time-series ingestion NO-GO; amended fusion NO-GO. |
| EVAL-28 | OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z | GO | n/a | n/a | $0.00 | GO (additive): per-expiry forward-calibrated put-call parity 1017/1017 pairs (100%), min R^2=0.999919. |
| EVAL-29 | OPTIONS_LEG_TRADABILITY_29 | NO-GO | n/a | n/a | $0.00 | Parity GO but broadcast-static signal mean IC 0.0 (options_signal_exists FAIL); combined net-of-cost not superior. |
| EVAL-30 | OPTIONS_LEG_TRADABILITY_30 | NO-GO | 7.759061793517281 | 171.0 | $350.62 | Time-varying options signal measured (ic_mean -0.002957, |t|<0.25 all horizons) but integrated net-of-cost verdict NO-GO; options leg degenerate (IC ~0). |
| EVAL-31 | AMENDED_FUSION_EVAL_31 | GO | 0.30156596306364075 | 93.0 | $129.62 | GO (marginal): combined Sharpe 0.3016 > best control 0.0 with 93 trades; but perm p=0.768, PBO combined=0.75, options_only 0 trades, toxicity gate 81.2%. |
| EVAL-32 | EVAL_32_OOS_VALIDATION | NO-GO | 5.019467339381368 | 108.0 | $122.07 | Held-out validation NO-GO (1/4 criteria): combined Sharpe 5.0195 indistinguishable from orderflow-only 4.8115 (perm p=0.2498, CI [-6.82,13.64], PBO 0.5156). Options leg added zero net-of-cost value. |
| EVAL-33 | OPTIONS_LEG_FALSIFICATION_33 | NO-GO | 5.019467339381368 | 108.0 | $122.07 | Exhaustive options-leg falsification NO-GO: all 6 options-only variants 0 trades / Sharpe 0.0 / $0 cost; orderflow-only is the only non-degenerate pillar (Sharpe 4.8115, 129 trades, $157.02 cost on held-out 466 bars). |

## Final Falsification Statement

The options+orderflow combined strategy is NOT net-of-cost tradable on the available real data (BTC, OKX, 3 option snapshots spanning ~6.5h, 50.9k inverse BTC-USD-SWAP trades, 1553 bars, held-out 466 bars at bar 1087..1552). Evidence: (a) EVAL-23 combined IC mean -0.0168 adverse (|t|=4.10, p=0.0020), options leg degenerate; (b) EVAL-24 options leg not tradable (venue IV/greeks/OI coverage 0%); (c) EVAL-27 time-series ingestion NO-GO; (d) EVAL-28 parity GO (additive only, 1017/1017 pairs 100%, min R^2=0.999919) but produces no alpha; (e) EVAL-29 tradability NO-GO (broadcast-static signal mean IC 0.0); (f) EVAL-30 time-varying signal NO-GO (measurement ic_mean -0.002957, all |t|<0.25, integrated net-of-cost FAIL); (g) EVAL-31 marginal GO (combined Sharpe 0.3016) invalidated by EVAL-32 held-out validation NO-GO (1/4 criteria, perm p=0.2498, bootstrap CI [-6.82,13.64], PBO 0.5156); (h) EVAL-33 exhaustive falsification NO-GO (all 6 options-only variants 0 trades, Sharpe 0.0, $0.00 cost). The combined edge (Sharpe 5.0195 on held-out) is entirely attributable to the orderflow-only pillar (Sharpe 4.8115, 129 trades, $157.02 cost).

- **Combined strategy net-of-cost tradable:** False
- **Options leg carries positive net-of-cost alpha:** False
- **Orderflow-only is only non-degenerate pillar:** True
- **Orderflow-only held-out Sharpe:** 4.8115
- **Orderflow-only held-out trades:** 129
- **Orderflow-only held-out cost:** $157.02

## Portfolio Decision

- **Decision:** **DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS**

### Rationale
DEPLOY ORDERFLOW-ONLY WITH CAVEATS. The orderflow-only pillar is the only non-degenerate, net-of-cost-measurable edge (held-out Sharpe 4.8115, 129 trades, $157.02 cost on 466 held-out bars). The options leg is a proven cost center with zero net-of-cost alpha across EVAL-23..33 (all 6 options-only variants: 0 trades, Sharpe 0.0, $0.00 cost; EVAL-33 NO-GO). Maintaining options infrastructure (parity calibration, IV surface, greeks, OI ingestion) for zero return is negative EV. The combined options+orderflow edge (Sharpe 5.0195) is indistinguishable from orderflow-only (perm p=0.2498, bootstrap CI includes 0, EVAL-32 NO-GO).

### Caveats
- Paper-only trading (live_trading_enabled=false; .env absent; no live enablement, venue/config/credential mutation, or order placement).
- Toxicity gate: VPIN >= 0.70 -> flat (toxicity gate engaged 80.5% on held-out).
- Capacity-aware sizing: spread 0.5 bps, impact coeff 10.0, max participation 20%, cost budget 2 bps, max position 20%.
- Continuous net-of-cost monitoring with kill-switch: max drawdown 20%, toxicity 80%, cost 5 bps.
- Max notional $1,000,000; max daily loss $50,000.
- Options leg terminated as a cost center (zero alpha); do not maintain parity calibration, IV surface, greeks, or OI ingestion for trading.
- Re-validate on a second independent real data window before scaling (EVAL-35).

- Max notional: $1,000,000.0; max daily loss: $50,000.0
- Max drawdown: 20%; toxicity kill-switch: 80%; cost kill-switch: 5.0 bps

## Commands
```bash
python3 -m py_compile scripts/eval34_final_strategy_falsification.py tests/test_eval34_final_strategy_falsification.py
```
```bash
python3 -m pytest -q tests/test_eval34_final_strategy_falsification.py
```
```bash
python3 scripts/eval34_final_strategy_falsification.py
```
