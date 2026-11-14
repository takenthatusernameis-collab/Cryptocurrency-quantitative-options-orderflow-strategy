# OPTIONS_LEG_FALSIFICATION_33 — Exhaustive options-leg falsification (EVAL-33)

- **Report ID:** `OPTIONS_LEG_FALSIFICATION_33`
- **Generated:** 2026-11-14T13:41:05.692346Z
- **Task ID:** `INIT-2026-11-14T13:41:05.692346Z-EVAL-33-OPTIONS-LEG-FALSIFICATION`
- **Verdict:** **NO-GO**
- **Reason:** No options-only variant passed all three criteria: best Sharpe=0.000000 vs best_control=orderflow_only (4.811462), best perm_p=0.5325, best CI=[0.0000, 0.0000]
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.
- Caveat: Paper-only; no live trading; .env absent.

## Split (chronological, no lookahead)
- Total bars: 1553; split index 1087.
- Train: 1087 bars.
- Held-out: 466 bars (2026-11-14T08:37:20.690000Z → 2026-11-14T10:33:35.690000Z).

## EVAL-30 Reproduction
- n_bars=1553, n_snapshots=3
- per_snapshot_signals: [-0.03619112216524052, -0.05184303954151161, -0.029513227890609832]
- mean_signal=-0.008405, ic_mean=-2.957030e-03
- non_constant=True, ic_present=True, matches_sealed=True

## Step 1 — Per-expiry / Per-component IC (cross-sectional buckets)
### Snapshot 2026-11-14T09:30:33.038452Z (signal=-0.036191)
- n_expiries=14, n_iv_points=14
  - **ATM**: calls=46, puts=46, all=92
    - calls: n=46, mean_iv=0.4875, iv_stdev=0.0598
    - puts: n=46, mean_iv=0.3228, iv_stdev=0.1194
    - all: n=92, mean_iv=0.4052, iv_stdev=0.1253
  - **NEAR**: calls=68, puts=69, all=137
    - calls: n=68, mean_iv=0.5043, iv_stdev=0.1311
    - puts: n=69, mean_iv=0.2639, iv_stdev=0.1955
    - all: n=137, mean_iv=0.3832, iv_stdev=0.2055
  - **WING**: calls=275, puts=321, all=596
    - calls: n=275, mean_iv=0.5508, iv_stdev=0.1869
    - puts: n=321, mean_iv=0.1650, iv_stdev=0.2410
    - all: n=596, mean_iv=0.3430, iv_stdev=0.2905
### Snapshot 2026-11-14T09:31:20.828170Z (signal=-0.051843)
- n_expiries=14, n_iv_points=14
  - **ATM**: calls=46, puts=46, all=92
    - calls: n=46, mean_iv=0.4894, iv_stdev=0.0611
    - puts: n=46, mean_iv=0.3198, iv_stdev=0.1192
    - all: n=92, mean_iv=0.4046, iv_stdev=0.1271
  - **NEAR**: calls=68, puts=69, all=137
    - calls: n=68, mean_iv=0.5080, iv_stdev=0.1364
    - puts: n=69, mean_iv=0.2598, iv_stdev=0.1977
    - all: n=137, mean_iv=0.3830, iv_stdev=0.2105
  - **WING**: calls=274, puts=321, all=595
    - calls: n=274, mean_iv=0.5500, iv_stdev=0.1879
    - puts: n=321, mean_iv=0.1647, iv_stdev=0.2407
    - all: n=595, mean_iv=0.3421, iv_stdev=0.2906
### Snapshot 2026-11-14T10:36:17.936702Z (signal=-0.029513)
- n_expiries=14, n_iv_points=14
  - **ATM**: calls=47, puts=47, all=94
    - calls: n=47, mean_iv=0.4832, iv_stdev=0.0668
    - puts: n=47, mean_iv=0.2934, iv_stdev=0.1282
    - all: n=94, mean_iv=0.3883, iv_stdev=0.1394
  - **NEAR**: calls=68, puts=68, all=136
    - calls: n=68, mean_iv=0.5131, iv_stdev=0.1493
    - puts: n=68, mean_iv=0.2502, iv_stdev=0.1930
    - all: n=136, mean_iv=0.3817, iv_stdev=0.2169
  - **WING**: calls=266, puts=321, all=587
    - calls: n=266, mean_iv=0.5478, iv_stdev=0.1939
    - puts: n=321, mean_iv=0.1629, iv_stdev=0.2389
    - all: n=587, mean_iv=0.3373, iv_stdev=0.2915

## Step 2 — Options-only Net-of-Cost Frontier (held-out)
### Controls
- **orderflow_only**: Sharpe 4.811462185754629, return 0.28006839027539565, maxDD 0.1840532628635083, trades 129, cost $157.02, notional $1411865.61, windows 9
- **flat**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9
- **combined_reference**: Sharpe 5.019467339381368, return 0.2930381262503177, maxDD 0.17578603758815967, trades 108, cost $122.07, notional $1093158.08, windows 9

### Options-only Variants
- **options_only_long_thresh0.1**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9, tox_gate_frac 0.8047
- **options_only_long_thresh0.2**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9, tox_gate_frac 0.8047
- **options_only_long_thresh0.5**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9, tox_gate_frac 0.8047
- **options_only_short_thresh0.1**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9, tox_gate_frac 0.8047
- **options_only_short_thresh0.2**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9, tox_gate_frac 0.8047
- **options_only_short_thresh0.5**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost $0.00, notional $0.00, windows 9, tox_gate_frac 0.8047

## Step 3 — Falsification Verdict
- **Verdict: NO-GO**
- Reason: No options-only variant passed all three criteria: best Sharpe=0.000000 vs best_control=orderflow_only (4.811462), best perm_p=0.5325, best CI=[0.0000, 0.0000]
- Best control: orderflow_only (Sharpe 4.811462)
- Any variant passed all criteria: False
  - options_only_long_thresh0.1: Sharpe=0.000000, trades=0, superior=False, perm_p=0.5325 (pass=False), CI=[0.0000,0.0000] (excl0=False), ALL_PASS=False
  - options_only_long_thresh0.2: Sharpe=0.000000, trades=0, superior=False, perm_p=0.5325 (pass=False), CI=[0.0000,0.0000] (excl0=False), ALL_PASS=False
  - options_only_long_thresh0.5: Sharpe=0.000000, trades=0, superior=False, perm_p=0.5325 (pass=False), CI=[0.0000,0.0000] (excl0=False), ALL_PASS=False
  - options_only_short_thresh0.1: Sharpe=0.000000, trades=0, superior=False, perm_p=0.5325 (pass=False), CI=[0.0000,0.0000] (excl0=False), ALL_PASS=False
  - options_only_short_thresh0.2: Sharpe=0.000000, trades=0, superior=False, perm_p=0.5325 (pass=False), CI=[0.0000,0.0000] (excl0=False), ALL_PASS=False
  - options_only_short_thresh0.5: Sharpe=0.000000, trades=0, superior=False, perm_p=0.5325 (pass=False), CI=[0.0000,0.0000] (excl0=False), ALL_PASS=False

## Step 3 — Statistical Defensibility
- Best variant: options_only_long_thresh0.1 (Sharpe 0.000000)
- Permutation vs orderflow_only: {"alternative": "two-sided", "control": "orderflow_only", "n_permutations": 1000, "null_mean": 0.0021584173238362973, "observed_difference": -0.03408639271878358, "p_value": 0.5324675324675324, "paired": true, "significant_at_05": false, "statistic_a": 0.0, "statistic_b": 0.03408639271878358}
- Permutation vs flat: {"alternative": "two-sided", "control": "flat", "n_permutations": 1000, "null_mean": 0.0, "observed_difference": 0.0, "p_value": 1.0, "paired": true, "significant_at_05": false, "statistic_a": 0.0, "statistic_b": 0.0}
- DSR: {"best_variant": {"0.0": 0.0, "0.5": 0.0, "1.0": 0.0}, "flat": {"0.0": 0.0, "0.5": 0.0, "1.0": 0.0}, "orderflow_only": {"0.0": 0.0, "0.5": 0.0, "1.0": 0.0}}
- Bootstrap CI: {"block_size": 2, "ci": [0.0, 0.0, 0.0], "excludes_zero": false, "n_bootstrap": 1000}
- PBO (k_folds=4): {"config_valid_combinations": {"best_variant": 4, "flat": 4, "orderflow_only": 4}, "k_folds": 4, "overall_pbo": 0.0, "pbo_per_config": {"best_variant": 0.0, "flat": 0.0, "orderflow_only": 0.4375}}
- BH-FDR: {"alpha": 0.1, "m_tests": 2, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"best_vs_flat": 0.1, "best_vs_orderflow": 0.05}}

## Commands
```bash
python3 -m py_compile src/analytics/options_time_varying_signal.py src/analytics/integrated_options_orderflow_evaluation.py scripts/eval33_options_leg_falsification.py tests/test_eval33_options_leg_falsification.py
```
```bash
python3 -m pytest -q tests/test_eval33_options_leg_falsification.py
```
```bash
python3 scripts/eval33_options_leg_falsification.py
```
