"""Quick exploratory probe for EVAL-30 measurement wiring (throwaway)."""
from __future__ import annotations

from src.campaign.integrated import load_real_orderflow, RealDataUnavailable
from src.analytics.integrated_options_orderflow_evaluation import _build_bars
from src.analytics.options_time_varying_signal import (
    load_snapshot_signals,
    measure_time_varying_signal,
    align_options_signal_to_bars,
)

try:
    snap = load_real_orderflow("BTC")
except RealDataUnavailable as e:
    print("REAL ORDERFLOW MISSING:", e)
    raise SystemExit(2)

bars = _build_bars(snap)
print("n_bars:", bars["n_bars"], "span:", bars["start_timestamp"], "->", bars["end_timestamp"])

sigs = load_snapshot_signals("BTC")
print("n_snapshots:", len(sigs))
for s in sigs:
    print("  ", s.snapshot_timestamp, "raw=", round(s.options_signal_raw, 6),
          "fwd_slope=", round(s.forward_curve_slope, 6),
          "atm_iv_term_slope=", round(s.atm_iv_term_slope, 6),
          "iv_skew=", round(s.iv_skew, 6),
          "pcr=", round(s.put_call_ratio, 6),
          "n_expiries=", s.n_expiries, "n_iv=", s.n_iv_points, "warnings=", s.warnings)

m = measure_time_varying_signal(sigs, bars["bar_ends_dt"], bars["bar_closes"])
for k, v in m.items():
    print(f"  {k}: {v}")