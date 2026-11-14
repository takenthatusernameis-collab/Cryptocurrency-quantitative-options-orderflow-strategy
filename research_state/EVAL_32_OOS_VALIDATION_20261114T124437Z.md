# EVAL_32_OOS_VALIDATION — OOS validation of marginal EVAL-31 GO (held-out 30%)

- **Report ID:** `EVAL_32_OOS_VALIDATION`
- **Generated:** 2026-11-14T12:44:37.589774Z
- **Task ID:** `INIT-2026-11-14T12:38:04Z-EVAL-32-OOS-VALIDATION-MARGINAL-GO`
- **Verdict:** **NO-GO**
- **Reason:** Held-out validation NO-GO: combined Sharpe 5.019467 vs best control 4.811462 (orderflow_only), trades 108, perm p=0.2498, bootstrap CI [-6.8240,13.6434], PBO combined=0.5156 (valid_combos=4).
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.
- Caveat: Paper-only; no live trading; .env absent.

## Split (chronological, no lookahead)
- Total bars: 1553; split index 1087.
- Train: bars 0..1086 (1087 bars, through 2026-11-14T08:37:05.690000Z).
- Held-out: bars 1087..1552 (466 bars, 2026-11-14T08:37:20.690000Z → 2026-11-14T10:33:35.690000Z).
- Mechanism: positions computed on full 1553-bar causal series, then sliced [1087:].

## Fusion (pre-declared, no fitted parameters)
- fusion_rule: `A_options_regime_filter_orderflow_direction`
- constants: {"embargo": 5, "max_position_pct": 0.2, "n_points": 500, "purge": 10, "seed": 42, "signal_lookback_seconds": 60.0, "signal_threshold": 0.1, "step_size": 40, "test_window": 40, "toxicity_threshold": 0.7, "toxicity_window_trades": 5, "train_window": 120}
- held-out nonflat bars: combined=50, options_only=0, orderflow_only=77
- toxicity gate fraction (held-out): 0.8047210300429185; options risk-off fraction: 0.5429184549356223

## Held-out walk-forward (net-of-cost, seed=42)
- num_windows by config: {"combined": 9, "flat": 9, "options_only": 9, "orderflow_only": 9}
- **combined**: Sharpe 5.019467339381368, return 0.2930381262503177, maxDD 0.17578603758815967, trades 108, cost $122.07360953905403, notional $1093158.080860914
- **options_only**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.0, notional $0.0
- **orderflow_only**: Sharpe 4.811462185754629, return 0.28006839027539565, maxDD 0.1840532628635083, trades 129, cost $157.0180100586245, notional $1411865.6103790484
- **flat**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.0, notional $0.0

## Statistical defensibility (pre-declared)
- permutation vs orderflow_only: {"alternative": "two-sided", "best_control": "orderflow_only", "n_permutations": 1000, "null_mean": 3.274183445376583e-05, "observed_difference": 0.0009212324007424125, "p_value": 0.24975024975024976, "paired": true, "significant_at_05": false, "statistic_a": 0.035007625119525994, "statistic_b": 0.03408639271878358}
- DSR by benchmark: {"0.0": 0.0, "0.5": 0.0, "1.0": 0.0}
- bootstrap CI: {"block_size": 2, "ci": [5.019467339381366, -6.823961182100189, 13.643447383223773], "excludes_zero": false, "n_bootstrap": 1000}
- PBO (k_folds=4): {"config_valid_combinations": {"combined": 4, "flat": 4, "options_only": 4, "orderflow_only": 4}, "k_folds": 4, "overall_pbo": 0.25, "pbo_per_config": {"combined": 0.515625, "flat": 0.0, "options_only": 0.0, "orderflow_only": 0.5}}
- PBO (k_folds=8, invalid): {"config_valid_combinations": {"combined": 0, "flat": 0, "options_only": 0, "orderflow_only": 0}, "k_folds": 8, "note": "k_folds=8 on 466-bar held-out yields valid_combinations=0 -> INVALID; not a pass."}
- BH-FDR: {"alpha": 0.1, "m_tests": 1, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"combined_vs_best_control": 0.1}}

## Pre-declared validation criteria (ALL must pass)
- a_combined_superior_and_trades: True
- b_permutation_p_lt_0_05: False
- c_bootstrap_ci_excludes_zero: False
- d_pbo_combined_lt_0_5_valid: False
- **all_pass: False**

## Verdict
- **NO-GO** — Held-out validation NO-GO: combined Sharpe 5.019467 vs best control 4.811462 (orderflow_only), trades 108, perm p=0.2498, bootstrap CI [-6.8240,13.6434], PBO combined=0.5156 (valid_combos=4).
