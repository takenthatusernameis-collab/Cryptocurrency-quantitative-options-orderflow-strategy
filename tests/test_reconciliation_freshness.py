"""Regression coverage for reconciliation freshness (slo_reconciliation_freshness).

Ensures reconciliation_freshness is genuinely emitted from the monitor cycle
(reflecting actual last-reconciliation age vs the 60s window) and is not a
hardcoded constant. Paper-only; no live path.
"""

from __future__ import annotations

import math

from src.monitoring.continuous_monitor import ContinuousMonitor
from src.monitoring.slo import SLOMonitor


def _make_monitor(seed: int = 7) -> ContinuousMonitor:
    # Private SLOMonitor so SLI measurements are not shared across tests via the
    # module-level default_slo_monitor singleton.
    return ContinuousMonitor(
        service="crypto-options-orderflow", seed=seed, paper_only=True, slo_monitor=SLOMonitor()
    )


def test_reconciliation_freshness_zero_when_never_reconciled():
    mon = _make_monitor()
    snap = mon.monitor_cycle()
    freshness = snap["metrics"]["metrics"]["reconciliation_freshness"]
    assert math.isfinite(freshness)
    assert freshness == 0.0, freshness


def test_reconciliation_freshness_at_least_target_when_reconciled_within_window():
    mon = _make_monitor()
    mon.record_reconciliation()
    snap = mon.monitor_cycle()
    freshness = snap["metrics"]["metrics"]["reconciliation_freshness"]
    assert math.isfinite(freshness)
    assert freshness >= 0.99, freshness

    slo_evals = mon.slo_monitor.evaluate_all()
    recon = next((e for e in slo_evals if e.get("slo_id") == "slo_reconciliation_freshness"), None)
    assert recon is not None, slo_evals
    assert recon["met"] is True, recon
    assert recon["current_value"] >= 0.99, recon
    assert recon["num_measurements"] >= 1, recon


def test_reconciliation_freshness_decays_beyond_window():
    mon = _make_monitor()
    mon.record_reconciliation()
    # Force the recorded timestamp far in the past to simulate staleness.
    mon._last_reconciliation_ts = 0.0  # noqa: SLF001 - test hook on internal state
    snap = mon.monitor_cycle()
    freshness = snap["metrics"]["metrics"]["reconciliation_freshness"]
    assert math.isfinite(freshness)
    assert freshness < 0.99, freshness
