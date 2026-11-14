# OPTIONS_LEG_TRADABILITY_29 — Options-leg tradability / net-of-cost

- **Report ID:** `OPTIONS_LEG_TRADABILITY_29`
- **Generated:** 2026-11-14T09:31:49.684Z
- **Verdict:** **NO-GO**
- **Provenance:** real_public_exchange_export (authenticity_verified=false)
- **Reason:** Options leg is parity-consistent (GO) but the broadcast-static signal yields mean IC 0.0 (options_signal_exists FAIL) and combined net-of-cost is not superior; no defensible options-leg edge on current real data.

## Measured state (real data re-acquired this session)
- Real options snapshots: 2 (span 47.8s)
- Parity calibration: GO — per-expiry forward-calibrated put-call parity holds on 777/777 pairs (100.0%) across 2 snapshot(s); min R2=0.999903
- Integrated eval: NO-GO (5/7 checks); failed=['options_signal_exists', 'combined_net_of_cost_superior']
- Options-only WF: Sharpe -483.876, trades 114, cost $55.83
- Orderflow-only WF: Sharpe 0.785, trades 97, cost $58.26
- Combined WF: Sharpe -100.333, trades 51, cost $53.35

## Measured root cause (removes the 'unblocked' ambiguity)
- Code: `src/analytics/integrated_options_orderflow_evaluation.py` :: `_causal_options_signal_series`
- Behavior: Broadcasts a single static options snapshot value to every bar; a constant signal has zero time-variation so mean IC == 0.0 and options_signal_exists FAILs. The options leg cannot yield a time-varying edge until the signal is computed per-snapshot over time.
- Evidence: options_mean_ic=0.0, options_signal_exists_pass=False

## Environment (verified this session)
- Python 3.12.3; numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0
- Deps were NOT installed in a fresh checkout; `pip3 install -r requirements.txt` required first.
- Real data is gitignored; re-acquire with `python -m src.data.public_export_acquisition`.

## Next concrete step
Compute a per-snapshot time-varying options signal (not broadcast-static) over >=3 real snapshots separated in wall-clock time; re-run net-of-cost; seal EVAL-30.
