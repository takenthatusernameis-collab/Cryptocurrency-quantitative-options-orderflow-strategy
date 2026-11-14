# ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35 — Orderflow-only second independent real data window validation (EVAL-35, paper-only)

- **Report ID:** `ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35`
- **Generated:** 2026-11-14T14:48:00.361757Z
- **Task ID:** `INIT-2026-11-14T14:48:00.361757Z-EVAL-35-ORDERFLOW-ONLY-SECOND-WINDOW-VALIDATION`
- **Verdict:** **NO-GO**
- **Reason:** orderflow-only second-window validation: decision=TERMINATE_NO_GO; Sharpe=-18.1777 (band ~4.8115), trades=1255 (band ~129), cost=$184.93 (band ~$157.02), max-DD=0.9662; non_degenerate=False, within_band=False
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- **Trading mode:** paper (live enabled: False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Inverse BTC-USD-SWAP orderflow tape.
- Caveat: Paper-only; no live trading; .env absent.
- Caveat: authenticity_verified=false.
- Caveat: Second independent real data window; distinct from EVAL-23..34 span.

## TAPE (second independent real data window, OKX BTC-USD-SWAP)
- Path: `data/raw/orderflow_okx_BTC-USD-SWAP_20261114T080515Z.json`
- Trades: 57600; Bars: 1565 (15.0s each)
- Span: 2026-11-14T08:08:15.925000Z -> 2026-11-14T14:39:17.438000Z
- Independent of EVAL-23..34 (2026-11-14T04:05:35Z->10:33:35Z): True
- Source: okx_public_history_trades (authenticated=False, public_read_only=True)

## ORDERFLOW-ONLY SIGNAL (causal, net_aggression via OrderflowAlphaEngine)
- Bars: 1565; long 153; short 123; flat 1289
- Gated flat (toxicity VPIN>=0.70->flat): 1130
- Mean signal: 0.088017

## TOXICITY (VPIN, causal, threshold 0.70)
- Mean 0.848736; p95 1.000000; range [0.000000, 1.000000]
- Fraction above threshold: 0.803195; gate engages: True; toxicity measured: True

## NET-OF-COST ORDERFLOW-ONLY WALK-FORWARD (capacity-aware sizing)
- Return: -0.966241; Sharpe: -18.177679; max-DD: 0.966246; ann_vol: 1.172419
- Cost: $184.93; notional: $924379.76; trades: 1255; windows: 37
- spread 2.0 bps; impact 0.01; max participation 0.125; cost budget 0.5 bps

## KILL-SWITCH TRIGGERS (read-only evaluation)
- max-DD 0.9662 >= 20%: True
- cost 18.4927 bps >= 5.0 bps: True
- toxicity gate active 0.8032 >= 80%: True
- notional $924379.76 >= $1,000,000.0: False
- Triggers: ['max_drawdown', 'cost_bps', 'toxicity']; any breach: True

## SUCCESS vs EVAL-34 HELD-OUT BAND
- Sharpe -22.9891 vs band 4.8115: ok=False (>1.0)
- Trades +1126 vs band 129: ok=True (>0)
- Cost $+27.91 vs band $157.02: ok=True (>0)
- Non-degenerate: False; within band: False

## PORTFOLIO CERTIFICATION DECISION
- **Decision:** **TERMINATE_NO_GO**

### Rationale
TERMINATE / NO-GO. Second independent real window failed to replicate the orderflow-only pillar: Sharpe -18.1777 <= 1.0 or non-finite; outside EVAL-34 held-out band; kill-switch breach: max_drawdown, cost_bps, toxicity. Measured: Sharpe -18.1777, 1255 trades, $184.93 cost, max-DD 0.9662. Options+orderflow remains NOT net-of-cost tradable; issue final termination memo (EVAL-36).

- Max notional: $1,000,000.0; max daily loss: $50,000.0
- Max drawdown: 20%; toxicity kill-switch: 80%; cost kill-switch: 5.0 bps
- Non-degenerate: False; within EVAL-34 band: False; kill-switch breach: True

## EVIDENCE MATRIX
- real_tape_loaded: True
- n_trades_total: 57600
- bars_constructed: True
- n_bars: 1565
- causal_orderflow_signal_computed: True
- toxicity_measured: True
- toxicity_gate_applied: True
- capacity_aware_sizing_applied: True
- walkforward_run: True
- paper_only: True
- live_trading_enabled: False
- no_synthetic_fallback: True
- never_valid_true: True

## COMMANDS
```bash
python3 -m py_compile scripts/eval35_orderflow_only_second_window_validation.py tests/test_eval35_orderflow_only_second_window_validation.py
```
```bash
python3 -m pytest -q tests/test_eval35_orderflow_only_second_window_validation.py
```
```bash
python3 scripts/eval35_orderflow_only_second_window_validation.py
```
