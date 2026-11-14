# FINAL_TERMINATION_MEMO_36 — Final termination memo (EVAL-36, paper-only)

- **Report ID:** `FINAL_TERMINATION_MEMO_36`
- **Generated:** 2026-11-14T14:54:19.370751Z
- **Task ID:** `INIT-2026-11-14T14:54:19.370751Z-EVAL-36-FINAL-TERMINATION-MEMO`
- **Verdict:** **NO-GO**
- **Decision:** **TERMINATE_NO_GO**
- **Campaign status:** TERMINATED
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- **Trading mode:** paper (live enabled: False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.
- Caveat: Paper-only; no live trading; .env absent.
- Caveat: authenticity_verified=false.

## Final Decision

TERMINATE / NO-GO. The options+orderflow campaign is not net-of-cost tradable on the available real data. EVAL-23..33 proved the options leg has no net-of-cost alpha (all options-only variants flat; parity is additive only). EVAL-34 provisionally selected orderflow-only with caveats, but EVAL-35 failed to replicate it on a second independent real OKX BTC-USD-SWAP window (2026-11-14T08:08:15Z to 14:39:17Z, 57,600 trades, 1565 bars): Sharpe -18.1777 vs EVAL-34 band ~4.8115, 1255 trades vs ~129, $184.93 cost vs ~$157.02, max-DD 0.9662, kill-switch triggers ['max_drawdown', 'cost_bps', 'toxicity']. No paper rollout certification is granted. No live enablement. No further queue.

- Paper rollout certified: False
- Options leg zero alpha confirmed: True
- Orderflow-only replication failed: True
- Live trading enabled: False

## Consolidated Evidence (EVAL-23 through EVAL-35)

| Eval | Report ID | Verdict | Sharpe | Trades | Cost USD | Key Reason |
|------|-----------|---------|--------|--------|----------|------------|
| EVAL-23 | REAL_NET_OF_COST_EVAL_23 | NO-GO | 4.7018 | 219 | $364.40 | Combined IC mean -0.0168 adverse (|t|=4.10, p=0.0020); options leg degenerate (constant broadcast, IC=0.0); fusion adds no measurable net-of-cost edge. |
| EVAL-24 | OPTIONS_LEG_VALIDITY_24 | NO-GO | n/a | n/a | n/a | Parity-consistent but options_leg_tradable FAIL; venue IV/greeks/OI coverage 0%. |
| EVAL-27 | OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z | NO-GO | n/a | n/a | n/a | Time-series ingestion NO-GO; amended fusion NO-GO. |
| EVAL-28 | OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z | GO | n/a | n/a | n/a | GO (additive): per-expiry forward-calibrated put-call parity 1017/1017 pairs (100%), min R^2=0.999919. |
| EVAL-29 | OPTIONS_LEG_TRADABILITY_29 | NO-GO | n/a | n/a | n/a | Parity GO but broadcast-static signal mean IC 0.0 (options_signal_exists FAIL); combined net-of-cost not superior. |
| EVAL-30 | OPTIONS_LEG_TRADABILITY_30 | NO-GO | 7.7591 | 171 | $350.62 | Time-varying options signal measured (ic_mean -0.002957, |t|<0.25 all horizons) but integrated net-of-cost verdict NO-GO; options leg degenerate (IC ~0). |
| EVAL-31 | AMENDED_FUSION_EVAL_31 | GO | 0.3016 | 93 | $129.62 | GO (marginal): combined Sharpe 0.3016 > best control 0.0 with 93 trades; but perm p=0.768, PBO combined=0.75, options_only 0 trades, toxicity gate 81.2%. |
| EVAL-32 | EVAL_32_OOS_VALIDATION | NO-GO | 5.0195 | 108 | $122.07 | Held-out validation NO-GO (1/4 criteria): combined Sharpe 5.0195 indistinguishable from orderflow-only 4.8115 (perm p=0.2498, CI [-6.82,13.64], PBO 0.5156). Options leg added zero net-of-cost value. |
| EVAL-33 | OPTIONS_LEG_FALSIFICATION_33 | NO-GO | 5.0195 | 108 | $122.07 | Exhaustive options-leg falsification NO-GO: all 6 options-only variants 0 trades / Sharpe 0.0 / $0 cost; orderflow-only is the only non-degenerate pillar (Sharpe 4.8115, 129 trades, $157.02 cost on held-out 466 bars). |
| EVAL-34 | FINAL_STRATEGY_FALSIFICATION_34 | NO-GO | 5.0195 | 108 | $122.07 | Final consolidated falsification NO-GO: options+orderflow combined is not net-of-cost tradable; options leg is a zero-alpha cost center; EVAL-34 provisionally selected orderflow-only with caveats, pending independent replication. |
| EVAL-35 | ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35 | NO-GO | -18.1777 | 1255 | $184.93 | Second independent real orderflow window NO-GO: Sharpe -18.1777 vs ~4.8115 band, 1255 trades vs ~129, $184.93 cost vs ~$157.02, max-DD 0.9662; kill-switch breached [max_drawdown,cost_bps,toxicity]; non_degenerate=False, within_band=False. |

## EVAL-35 Independent Replication Result

- Tape: `data/raw/orderflow_okx_BTC-USD-SWAP_20261114T080515Z.json`
- Trades: 57600.0; Bars: 1565.0
- Span: 2026-11-14T08:08:15.925000Z -> 2026-11-14T14:39:17.438000Z
- Sharpe: -18.1777 (EVAL-34 band ~4.8115)
- Trades: 1255 (EVAL-34 band ~129)
- Cost: $184.93 (EVAL-34 band ~$157.02)
- Max drawdown: 0.9662
- Kill-switch triggers: ['max_drawdown', 'cost_bps', 'toxicity']
- Non-degenerate: False; within EVAL-34 band: False

## Lessons Learned
- A second independent real window invalidated the EVAL-34 orderflow-only deployment candidate: Sharpe -18.1777 vs +4.8115, 1255 trades vs 129, max-DD 0.9662.
- The options leg produced zero net-of-cost alpha across EVAL-23..33; parity calibration is additive only and cannot carry a trading strategy.
- Single-window or single-tape results are not sufficient for deployment certification; independent replication must be a hard gate.
- The toxicity gate engaged 80.3% of bars and the kill-switch still breached; risk controls cannot rescue a negative-expectancy signal.
- No synthetic fallback and no live enablement were used; the negative result is sealed as trustworthy evidence.

## Infrastructure Disposition
- options_leg: TERMINATED
- orderflow_only: NOT_CERTIFIED
- combined_strategy: TERMINATED
- paper_rollout: False
- live_trading_enabled: False
- env_file_present: False
- data_retention: Keep real public exports and sealed artifacts; do not delete evidence.
- real_loaders: Must raise RealDataUnavailable; no synthetic fallback.
- next_actions: NONE — campaign terminated.
- never_valid_true: True

## Caveats
- authenticity_verified=false; public exports have no signed venue attestation.
- Available real data covers BTC/OKX only; no claim is made for other venues or assets.
- The second independent window is still a single historical period; no forward deployment follows.

## Commands
```bash
python3 -m py_compile scripts/eval36_final_termination_memo.py tests/test_eval36_final_termination_memo.py
```
```bash
python3 -m pytest -q tests/test_eval36_final_termination_memo.py
```
```bash
python3 scripts/eval36_final_termination_memo.py
```
