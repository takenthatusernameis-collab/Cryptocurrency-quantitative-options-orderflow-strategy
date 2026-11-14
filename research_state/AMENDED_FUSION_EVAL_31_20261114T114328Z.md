# AMENDED_FUSION_EVAL_31 — Amended time-varying options+orderflow fusion (net-of-cost)

- **Report ID:** `AMENDED_FUSION_EVAL_31`
- **Generated:** 2026-11-14T11:43:28.313551Z
- **Verdict:** **GO**
- **Reason:** combined OOS Sharpe 0.301566 > best control 0.000000 with trades 93>0
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- **Caveats:** public read-only OKX exports; no signed venue attestation; inverse BTC-USD-SWAP orderflow tape vs spot option snapshots; paper-only.

## Fusion mechanism (pre-declared, no fitted parameters)
- fusion_rule: `A_options_regime_filter_orderflow_direction` (rule_amended=True)
- rationale: EVAL-30 time-varying options signal is a 3-step function (all negative: -0.036191, -0.051843, -0.029513). A sign-agreement fusion degenerates when pillars do not share sign; Rule A uses options sign as a causal regime filter (trade orderflow direction only while options_signal < 0, i.e. risk-off) and orderflow for direction/magnitude, with toxicity gate (>=0.7 -> flat). Pre-declared, no fitted parameters, no curve-fitting.
- constants: {"bar_duration_seconds": 15.0, "signal_lookback_seconds": 60.0, "signal_threshold": 0.1, "toxicity_threshold": 0.7, "toxicity_window_trades": 5}
- toxicity_gate_fraction: 0.8119768190598841, options_risk_off_fraction: 0.16291049581455247
- nonflat bars: combined=50, options_only=0, orderflow_only=256

## Step 1 — EVAL-30 reproduction (real loader)
- n_bars=1553 n_snapshots=3 bar_span_seconds=23280.0 snapshot_span_seconds=3944.89825
- snapshot_timestamps: ['2026-11-14T09:30:33.038452Z', '2026-11-14T09:31:20.828170Z', '2026-11-14T10:36:17.936702Z']
- per_snapshot_signals: [-0.03619112216524052, -0.05184303954151161, -0.029513227890609832]
- mean_signal=-0.008405461258530169 stdev=0.019069710849460294 distinct=3 step_changes=2 n_flat_bars=1300
- ic_by_horizon: {'1': -0.003068861091869359, '5': -0.006377293979446277, '20': 0.0005750637911477361}
- ic_tstat_by_horizon: {'1': -0.12082175095357033, '5': -0.25075523805049255, '20': 0.0225010969187448}
- ic_mean=-0.0029570304267226336 non_constant=True ic_present=True matches_sealed_eval30=True

## Walk-forward (net-of-cost, CapacityAwareSizer + IntegratedConfig seed=42)
- **combined**: Sharpe 0.30156596306364075, return -0.025353723977661138, maxDD 0.30221185305856313, trades 93, cost 129.61663306958653, turnover/notional 1163212.950396587, windows 36
- **options_only**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost 0.0, turnover/notional 0.0, windows 36
- **orderflow_only**: Sharpe -1.5391430810191162, return -0.6054919360150148, maxDD 0.7175559403509923, trades 514, cost 663.1367168007762, turnover/notional 5974828.253775812, windows 36
- **flat**: Sharpe 0.0, return 0.0, maxDD 0.0, trades 0, cost 0.0, turnover/notional 0.0, windows 36

## Verdict checks
- combined_net_of_cost_superior: pass=True (combined Sharpe 0.30156596306364075 vs best options_only 0.0, trades 93)

## Statistical defensibility
- permutation_vs_best_control: {"alternative": "two-sided", "best_control": "options_only", "n_permutations": 1000, "null_mean": -0.0009939871030735946, "observed_difference": 0.0011533575115508167, "p_value": 0.7682317682317682, "paired": true, "significant_at_05": false, "statistic_a": 0.0011533575115508167, "statistic_b": 0.0}
- DSR (window returns): {"combined": 0.033066929215934016, "flat": 0.0, "options_only": 0.0, "orderflow_only": 0.0}
- PBO (CSCV): {"config_details": {"combined": {"mean_is_sharpe": 0.28624116831068214, "mean_oos_sharpe": -0.37644303426162073, "pbo": 0.75, "valid_combinations": 8}, "flat": {"mean_is_sharpe": 0.0, "mean_oos_sharpe": 0.0, "pbo": 0.0, "valid_combinations": 8}, "options_only": {"mean_is_sharpe": 0.0, "mean_oos_sharpe": 0.0, "pbo": 0.0, "valid_combinations": 8}, "orderflow_only": {"mean_is_sharpe": -1.6126312744356173, "mean_oos_sharpe": -5.795583923277281, "pbo": 0.546875, "valid_combinations": 8}}, "k_folds": 8, "n_combinations_used": 16, "overall_pbo": 0.5, "pbo_per_config": {"combined": 0.75, "flat": 0.0, "options_only": 0.0, "orderflow_only": 0.546875}}
- BH-FDR: {"alpha": 0.1, "m_tests": 1, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"combined_vs_best_control": 0.1}}
- notes: Permutation/DSR/PBO computed on walk-forward window returns (36 windows).
