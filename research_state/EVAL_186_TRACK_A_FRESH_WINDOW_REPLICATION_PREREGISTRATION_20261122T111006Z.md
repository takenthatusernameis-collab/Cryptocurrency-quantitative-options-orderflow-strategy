# EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_PREREGISTRATION - TRACK A fresh-window replication of the dual traded-form NO-GO

- Generated: `2026-11-22T11:10:06Z`
- Task: `EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`
- Hypothesis: The EVAL-69 order-flow and EVAL-184 surface traded-form NO-GO results are temporally robust on a strictly forward, floor-compliant BTC+ETH capture that does not overlap the sealed EVAL-64/65 or EVAL-84/185 windows. A GO in either family refutes the dual NO-GO; under-floor or overlapping data is BLOCKED and never NO-GO.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval185cap`
- Previous EVAL-84/185 window: `2026-11-18T13:58:43Z` .. `2026-11-22T06:46:43Z`
- Earliest strictly forward 3.7-day capture end: `2026-11-25T23:34:43Z`
- Recommended acquisition end: `2026-11-26T00:00:00Z`

## Pre-declared replication families

- Order flow: EVAL-69 runner, `write=False`, unchanged GO bar and power floor.
- Surface: EVAL-184 runner, `write=False`, unchanged GO bar and power floor.
- Neither sealed EVAL-69 nor EVAL-184 artifact is re-sealed or modified.

## Pre-declared GO bar

GO CONFIRMED if either family independently returns GO CONFIRMED on the fresh forward capture. NO-GO CONFIRMED (PASS) only if both families return NO-GO CONFIRMED (PASS) and both are power adequate. INCONCLUSIVE (UNDERPOWERED) if neither is GO and either is underpowered. BLOCKED if an underlying is missing, the EVAL-64 floor fails, or the capture overlaps the sealed EVAL-64/65 window or the EVAL-84/185 window. Under-floor or non-disjoint data is never NO-GO.

## Pre-registered feasible floor

- EVAL-64 floor reused verbatim; both BTC and ETH required.
- Minimum pooled returns per family: 790.

## Acquisition

```bash
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --end 2026-11-26T00:00:00Z --max-per-expiry 30 --out-dir data/raw/eval185cap --seal
```
