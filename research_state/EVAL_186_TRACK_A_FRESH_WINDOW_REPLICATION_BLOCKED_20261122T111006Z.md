# EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED - TRACK A fresh-window replication BLOCKED

- Generated: `2026-11-22T11:10:06Z`
- Task: `EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`
- Verdict: **BLOCKED** (measured; not NO-GO)
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval185cap`
- Floor OK: False
- Strictly-forward disjointness OK: True

The capture is missing a required underlying, is below the pre-registered EVAL-64 feasible floor, or overlaps the sealed EVAL-64/65 or EVAL-84/185 window. No GO/NO-GO verdict is emitted.

## Forward disjointness

- BTC: {"capture_span_seconds": 319680.0, "capture_window": ["2026-11-22T07:12:00Z", "2026-11-26T00:00:00Z"], "meets_min_span": true, "ok": true, "previous_overlap_seconds": 0.0, "previous_window": ["2026-11-18T13:58:43Z", "2026-11-22T06:46:43Z"], "reason": "strictly_forward_disjoint", "sealed_overlap_seconds": 0.0, "sealed_window": ["2026-11-09T06:48:16Z", "2026-11-16T06:48:16Z"], "starts_after_previous": true, "underlying": "BTC"}
- ETH: {"capture_span_seconds": 319680.0, "capture_window": ["2026-11-22T07:12:00Z", "2026-11-26T00:00:00Z"], "meets_min_span": true, "ok": true, "previous_overlap_seconds": 0.0, "previous_window": ["2026-11-18T13:58:43Z", "2026-11-22T06:46:43Z"], "reason": "strictly_forward_disjoint", "sealed_overlap_seconds": 0.0, "sealed_window": ["2026-11-09T06:48:16Z", "2026-11-16T06:48:16Z"], "starts_after_previous": true, "underlying": "ETH"}

## Per-underlying floor

- BTC: {"common_overlap_ok": false, "of_bars_ok": false, "of_instruments_ok": false, "of_span_ok": false, "perp_bars_ok": false, "perp_span_ok": false, "snapshots_ok": false, "surface_bars_ok": false, "surface_instruments_ok": true, "trades_ok": false}
- ETH: {"common_overlap_ok": false, "of_bars_ok": false, "of_instruments_ok": false, "of_span_ok": false, "perp_bars_ok": false, "perp_span_ok": false, "snapshots_ok": false, "surface_bars_ok": false, "surface_instruments_ok": true, "trades_ok": false}
