"""Unit tests for EVAL-50 real L2 order-book OFI net-of-cost falsification.

These tests verify the pure OFI / resampling / z-score / net-of-cost strategy
functions, the per-instrument evaluator, and the heavy-work floor (a short or
partial capture must NOT produce a GO/NO-GO verdict). They use deterministic
in-memory capture fixtures (unit-test inputs only) and never touch
``research_state/`` or real data. The EVAL-50 acquisition script is exercised
for its pure projection/trimming helpers only (no network).
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import scripts.eval50_acquire_l2_depth as acq
import scripts.eval50_l2_ofi_net_of_cost as e50


# ---------------------------------------------------------------------------
# OFI (Cont/Kukanov/Stoikov) multi-level
# ---------------------------------------------------------------------------
def test_ofi_bid_depth_increase_is_positive():
    prev = {"bids": [[100.0, 10.0], [99.0, 5.0]], "asks": [[101.0, 8.0]]}
    cur = {"bids": [[100.0, 20.0], [99.0, 5.0]], "asks": [[101.0, 8.0]]}
    assert e50.ofi_at(prev, cur, 10) == 10.0


def test_ofi_ask_depth_increase_is_negative():
    prev = {"bids": [[100.0, 10.0]], "asks": [[101.0, 8.0]]}
    cur = {"bids": [[100.0, 10.0]], "asks": [[101.0, 20.0]]}
    assert e50.ofi_at(prev, cur, 10) == -12.0


def test_ofi_new_and_removed_levels():
    prev = {"bids": [[100.0, 10.0]], "asks": [[101.0, 8.0]]}
    cur = {"bids": [[100.0, 10.0], [99.0, 4.0]], "asks": []}  # new bid +4, ask -8
    # bid delta +4, ask delta -8 -> OFI = 4 - (-8) = 12
    assert e50.ofi_at(prev, cur, 10) == 12.0


def test_ofi_respects_level_cap():
    prev = {"bids": [[100.0, 10.0], [99.0, 10.0]], "asks": [[101.0, 5.0]]}
    cur = {"bids": [[100.0, 10.0], [99.0, 30.0]], "asks": [[101.0, 5.0]]}
    # only top 1 level counts -> bid delta 0
    assert e50.ofi_at(prev, cur, 1) == 0.0


# ---------------------------------------------------------------------------
# Resampling + z-score + net-of-cost strategy
# ---------------------------------------------------------------------------
def _craft_capture(n=120, seed=0, inst="BTC-USD-SWAP"):
    rng = random.Random(seed)
    mid = 60000.0
    snaps = []
    ts = 1_700_000_000_000
    for i in range(n):
        # random-walk mid; OFI signal correlated with the up-move
        drift = rng.uniform(-1, 1)
        mid = max(1.0, mid * (1 + drift * 1e-4))
        half = 0.05
        snaps.append(
            {
                "ts": ts + i * 2000,
                "seqId": 1000 + i,
                "bids": [[mid - half, 100.0 + drift * 10], [mid - half - 1, 50.0]],
                "asks": [[mid + half, 100.0 - drift * 10], [mid + half + 1, 50.0]],
            }
        )
    return {"inst_id": inst, "count": n, "snapshots": snaps, "schema": "test_fixture"}


def test_resample_bars_aggregates_and_orders():
    cap = _craft_capture(n=40)
    bars = e50.resample_bars(cap["snapshots"], bar_seconds=10.0)
    assert len(bars) >= 2
    ends = [b["bar_end"] for b in bars]
    assert ends == sorted(ends)
    assert all(b["mid"] > 0 for b in bars)
    assert all(math.isfinite(b["ofi"]) for b in bars)


def test_expanding_zscore_zero_before_min_periods():
    zs = e50.expanding_zscore([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], window=5, min_periods=5)
    assert zs[0] == 0.0 and zs[1] == 0.0 and zs[2] == 0.0 and zs[3] == 0.0
    assert zs[4] != 0.0


def test_strategy_returns_rising_book_is_long_and_profitable():
    bars = [{"bar_end": i * 5000, "ofi": float(i), "mid": 100.0 + i * 0.05,
             "spread_bps": 0.02} for i in range(12)]
    sr = e50.strategy_returns(bars, z_clamp=1.0)
    assert len(sr["returns"]) == len(bars) - 1
    assert sr["nonzero"] > 0
    assert e50._sharpe_of_returns(sr["returns"]) > 0


def test_max_drawdown_and_kill_switch():
    assert e50._max_drawdown([0.1, -0.5, 0.1]) > 0.3
    assert e50.kill_switch_breach(0.25) is True
    assert e50.kill_switch_breach(0.1) is False


# ---------------------------------------------------------------------------
# Evaluator + floor
# ---------------------------------------------------------------------------
def test_evaluate_instrument_runs_without_error():
    cap = _craft_capture(n=200, seed=1)
    res = e50.evaluate_instrument(cap, bar_seconds=5.0, z_clamp=2.0)
    assert res["instrument"] == "BTC-USD-SWAP"
    assert res["n_returns"] > 0
    assert math.isfinite(res["sharpe"])
    assert 0.0 <= res["permutation_p"] <= 1.0
    assert len(res["bootstrap_ci"]) == 3
    assert isinstance(res["pass"], bool)


def test_run_eval50_floor_blocks_short_capture(tmp_path):
    cap = _craft_capture(n=120, seed=2, inst="BTC-USD-SWAP")
    (tmp_path / "l2_depth_BTC-USD-SWAP_20260101T000000Z.json").write_text(json.dumps(cap))
    report = e50.run_eval50(
        capture_dir=str(tmp_path),
        write=False,
        min_snapshots=400,
        min_span=900.0,
        min_instruments=2,
    )
    # 120 snapshots < 400 floor and 1 instrument < 2 -> floor not ok, no verdict
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"


def test_run_eval50_no_write_seals_nothing(tmp_path):
    cap = _craft_capture(n=200, seed=3, inst="BTC-USD-SWAP")
    (tmp_path / "l2_depth_BTC-USD-SWAP_20260101T000000Z.json").write_text(json.dumps(cap))
    before = set(p.name for p in e50.OUT_DIR.glob("EVAL_50_*"))
    e50.run_eval50(capture_dir=str(tmp_path), write=False)
    after = set(p.name for p in e50.OUT_DIR.glob("EVAL_50_*"))
    assert before == after


def test_capture_inventory_keeps_newest_per_instrument(tmp_path):
    old = _craft_capture(n=100, seed=4, inst="BTC-USD-SWAP")
    old["end_ts_ms"] = 1000
    new = _craft_capture(n=300, seed=5, inst="BTC-USD-SWAP")
    new["end_ts_ms"] = 9000
    (tmp_path / "l2_depth_BTC-USD-SWAP_20260101T000000Z.json").write_text(json.dumps(old))
    (tmp_path / "l2_depth_BTC-USD-SWAP_20260102T000000Z.json").write_text(json.dumps(new))
    inv = e50._capture_inventory(str(tmp_path))
    assert len(inv) == 1
    assert inv[0]["count"] == 300  # newest kept, not double-counted


# ---------------------------------------------------------------------------
# Acquisition helpers (pure, no network)
# ---------------------------------------------------------------------------
def test_acquire_trim_levels_projects_price_size():
    rows = [["100", "5", "0", "1"], ["99", "2", "0", "1"], ["bad"]]
    out = acq._trim_levels(rows, 5)
    assert out == [[100.0, 5.0], [99.0, 2.0]]


def test_acquire_summarize_flags_degenerate_and_real():
    flat = {"inst_id": "X", "count": 3, "snapshots": [
        {"ts": 1000, "seqId": 1, "bids": [[100, 1]], "asks": [[101, 1]]},
        {"ts": 2000, "seqId": 2, "bids": [[100, 1]], "asks": [[101, 1]]},
        {"ts": 3000, "seqId": 3, "bids": [[100, 1]], "asks": [[101, 1]]},
    ]}
    s = acq.summarize_capture(flat)
    assert s["degenerate"] is True
    moving = {"inst_id": "X", "count": 3, "snapshots": [
        {"ts": 1000, "seqId": 1, "bids": [[100, 1]], "asks": [[101, 1]]},
        {"ts": 2000, "seqId": 2, "bids": [[100.5, 1]], "asks": [[101.5, 1]]},
        {"ts": 3000, "seqId": 3, "bids": [[101, 1]], "asks": [[102, 1]]},
    ]}
    s2 = acq.summarize_capture(moving)
    assert s2["non_degenerate_ofi_ready"] is True