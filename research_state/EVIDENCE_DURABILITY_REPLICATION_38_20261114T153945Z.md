# EVIDENCE_DURABILITY_REPLICATION_38 — Evidence durability: re-acquired tape replication test (EVAL-38, paper-only)

- **Report ID:** `EVIDENCE_DURABILITY_REPLICATION_38`
- **Generated:** 2026-11-14T15:39:45.971749Z
- **Task ID:** `INIT-2026-11-14T15:39:45.971749Z-EVAL-38-EVIDENCE-DURABILITY-REPLICATION`
- **Replication verdict:** **REPLICATION**
- **Durability status:** CONCLUSIONS_REPRODUCIBLE
- **Conclusion:** REPLICATION of EVAL-35 NO-GO. Re-acquired public OKX tape independently reproduces the orderflow-only failure: Sharpe -7.9539 (EVAL-35 -18.1777), 1221 trades (EVAL-35 1255), $179.28 cost (EVAL-35 $184.93), max-DD 0.8679 (EVAL-35 0.9662); kill-switch breach ['max_drawdown', 'cost_bps', 'toxicity']. The sealed EVAL-23..36 conclusions are recomputable from real raw data.
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- **Trading mode:** paper (live enabled: False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Inverse BTC-USD-SWAP orderflow tape, re-acquired 2026-11-14T15:33Z.
- Caveat: Paper-only; no live trading; .env absent.
- Caveat: authenticity_verified=false.
- Caveat: Tape independently re-acquired, not the sealed EVAL-35 window; span differs.

## RE-ACQUIRED TAPE (public OKX BTC-USD-SWAP)
- Path: `data/raw/orderflow_okx_BTC-USD-SWAP.json`
- SHA-256: `fa9e43b8edeeeace7b7c551b23158aa68778dbf3909898f7e629da843baa43b6`
- Trades: 77700; Bars: 1555 (15.0s each)
- Span: 2026-11-14T09:05:22.330000Z -> 2026-11-14T15:33:56.432000Z
- Acquisition artifact: `research_state/PUBLIC_EXPORT_ACQUISITION_20261114T153357Z.json`

## ORDERFLOW-ONLY SIGNAL (causal, net_aggression)
- Bars: 1555; long 113; short 121; flat 1321
- Gated flat (toxicity VPIN>=0.70->flat): 1151
- Mean signal: 0.031576

## TOXICITY (VPIN, causal, threshold 0.70)
- Mean 0.864765; p95 1.000000; range [0.007229, 1.000000]
- Fraction above threshold: 0.829582; gate engages: True

## NET-OF-COST ORDERFLOW-ONLY WALK-FORWARD (capacity-aware sizing)
- Return: -0.841568; Sharpe: -7.953898; max-DD: 0.867914; ann_vol: 1.446549
- Cost: $179.28; notional: $896141.99; trades: 1221; windows: 36

## KILL-SWITCH TRIGGERS (read-only)
- max-DD 0.8679 >= 20%: True
- cost 17.9277 bps >= 5.0 bps: True
- toxicity gate active 0.8296 >= 80%: True
- notional $896141.99 >= $1,000,000.0: False
- Triggers: ['max_drawdown', 'cost_bps', 'toxicity']; any breach: True

## REPLICATION vs EVAL-35 SEALED NO-GO
- EVAL-35: Sharpe -18.1777, trades 1255, cost $184.93, max-DD 0.9662, verdict NO-GO
- Re-acquired: Sharpe -7.9539 (+10.2238), trades 1221 (-34), cost $179.28 (-5.65), max-DD 0.8679 (-0.0983)
- Replicated: True; refuted: False

## EVIDENCE MATRIX
- reacquisition_performed: True
- reacquired_tape_loaded: True
- n_trades_total: 77700
- bars_constructed: True
- n_bars: 1555
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
python3 -m src.data.public_export_acquisition --underlying BTC --orderflow-instrument BTC-USD-SWAP --min-bars 1550 --bar-duration-seconds 15
```
```bash
python3 -m py_compile scripts/eval38_evidence_durability_replication.py tests/test_eval38_evidence_durability_replication.py
```
```bash
python3 -m pytest -q tests/test_eval38_evidence_durability_replication.py
```
```bash
python3 scripts/eval38_evidence_durability_replication.py
```
