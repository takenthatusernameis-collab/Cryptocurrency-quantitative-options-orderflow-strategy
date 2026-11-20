# EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED — pooled BTC+ETH OOS replication of suggestive EVAL-65 slice (below the pre-registered feasible floor and/or missing an underlying and/or overlapping the sealed window)

- Generated: `2026-11-20T01:48:19Z`
- Task: `EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`
- Verdict: **BLOCKED** (measured; not NO-GO)
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval68`
- Underlyings: BTC, ETH
- Missing underlyings: []
- Floor met: False
- Disjointness met: True

The capture does not meet the pre-registered feasible floor (reused from sealed EVAL-64), is missing a required underlying, and/or overlaps the sealed EVAL-64/65 window (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z), so no GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor or non-disjoint data.

## Disjointness

- BTC: {"underlying": "BTC", "ok": true, "reason": "disjoint", "capture_window": ["2026-11-16T08:04:50Z", "2026-11-20T00:52:50Z"], "sealed_window": ["2026-11-09T06:48:16Z", "2026-11-16T06:48:16Z"], "overlap_seconds": 0.0, "capture_span_seconds": 319680.0, "meets_min_span": true}
- ETH: {"underlying": "ETH", "ok": true, "reason": "disjoint", "capture_window": ["2026-11-16T08:04:50Z", "2026-11-20T00:52:50Z"], "sealed_window": ["2026-11-09T06:48:16Z", "2026-11-16T06:48:16Z"], "overlap_seconds": 0.0, "capture_span_seconds": 319680.0, "meets_min_span": true}

## Per-underlying floor

- BTC: {"snapshots_ok": true, "surface_instruments_ok": false, "surface_bars_ok": true, "trades_ok": true, "of_instruments_ok": false, "of_span_ok": true, "of_bars_ok": true, "perp_bars_ok": true, "perp_span_ok": true, "common_overlap_ok": true}
- ETH: {"snapshots_ok": true, "surface_instruments_ok": true, "surface_bars_ok": true, "trades_ok": false, "of_instruments_ok": false, "of_span_ok": true, "of_bars_ok": true, "perp_bars_ok": true, "perp_span_ok": true, "common_overlap_ok": true}
