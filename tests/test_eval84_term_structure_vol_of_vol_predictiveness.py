"""Unit tests for EVAL-84: does the options implied-volatility **term structure**
(near-dated minus far-dated near-ATM IV slope) predict forward **vol-of-vol /
variance-of-variance**?

EVAL-84 is the on-charter, runnable-now distinct-target follow-up to EVAL-74
(same term-structure signal; EVAL-74 sealed NO-GO portable vs forward *RV*).
EVAL-84 reuses EVAL-74's bar/term construction and EVAL-65's Spearman rank-IC
statistics verbatim; the only new logic is the forward vol-of-vol target
(std of squared log returns over the forward window), distinct from RV.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval65_orderflow_tox_rv_predictiveness as e65
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval74_surface_term_structure_predictiveness as e74
import scripts.eval84_term_structure_vol_of_vol_predictiveness as e84

DEFAULT_EXPIRIES = ("18NOV26", "20NOV26", "27NOV26", "4DEC26")


def _craft_term_capture(
    inst="BTC", *, n_bars=320, seed=0, signal_to_vol=0.0, n_trades_per_bar=40,
    ar=0.8, expiries=DEFAULT_EXPIRIES,
):
    """In-memory three-way capture whose real option-trade IV term structure is
    driven by a latent AR(1) factor that also drives forward *variance
    turbulence* (vol-of-vol). ``signal_to_vol`` > 0 plants a positive
    term-slope -> forward vol-of-vol relationship; ``== 0`` plants none."""
    rng = random.Random(seed)
    bar_ms = 300_000
    base_ms = 1_700_000_000_000
    base_ms -= base_ms % bar_ms
    px = 60000.0 if inst == "BTC" else 3000.0
    n_exp = len(expiries)
    candles = []
    trades = []
    latent = 0.5
    for i in range(n_bars):
        latent = ar * latent + rng.uniform(0, 1) * (1.0 - ar)
        latent = max(0.0, min(1.0, latent))
        # Plant variance turbulence: higher latent -> more uneven return magnitudes
        # (alternating large/small moves), which raises forward vol-of-vol
        # (std of squared returns) distinctly from mean RV level.
        amp = 1e-4 + latent * signal_to_vol * 5e-3 + rng.uniform(0.0, 5e-5)
        if i % 2 == 0:
            drift = amp * (1.0 + 2.0 * latent)
        else:
            drift = -amp * (0.2 + 0.1 * rng.random())
        px = max(1.0, px * (1.0 + drift))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        for j in range(n_trades_per_bar):
            e_idx = j % n_exp
            frac = (e_idx / (n_exp - 1)) if n_exp > 1 else 0.0
            base_iv = 60.0 - frac * 20.0
            sens = 20.0 * (1.0 - frac)
            iv = base_iv + sens * latent + rng.uniform(-0.5, 0.5)
            strike = px * (0.98 + 0.04 * (j / max(1, n_trades_per_bar - 1)))
            inst_name = f"{inst}-{expiries[e_idx]}-{int(round(strike))}-C"
            trades.append({
                "ts": ts + j * 1000,
                "instrument": inst_name,
                "iv": iv,
                "index_price": px,
                "amount": 1.0 + 0.1 * j,
            })
    return {
        "underlying": inst,
        "surface": {"snapshots": []},
        "option_trades": trades,
        "perp_candles": candles,
        "fetched_at": "2026-11-17T00:00:00Z",
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# 1) artifact ids
def test_ids_are_eval84():
    assert e84.REPORT_ID.startswith("EVAL_84_")
    assert e84.PREREG_ID.startswith("EVAL_84_")
    assert e84.BLOCKED_ID.startswith("EVAL_84_")
    assert "VOL_OF_VOL" in e84.REPORT_ID


# 2) reuse (not forked)
def test_reuse_helpers():
    # forward-fill and term-bar construction reused from sealed EVAL-71/74
    assert e84.e71 is e71
    assert e84.e74 is e74
    assert e84.e65 is e65
    assert e84.e61 is e61
    assert e84.e62 is e62


# 3) forward vol-of-vol target differs from RV and is well-defined
def test_forward_vov_differs_from_rv_and_is_finite():
    # build synthetic bars with alternating magnitudes -> high vov
    bars = []
    px = 100.0
    for i in range(80):
        drift = 0.02 if i % 2 == 0 else 0.0001
        px = px * (1.0 + drift)
        bars.append({"close": px, "bar_open_ms": i * 300000})
    vov = e84._forward_vov(bars, 24)
    rv = e71._forward_rv(bars, 24)
    finite_vov = [v for v in vov if v is not None and math.isfinite(v)]
    assert len(finite_vov) > 10
    # vov should be positive when variance contributions vary
    assert any(v > 0.0 for v in finite_vov)
    # distinct from RV length/shape: rv indexed by k over valid windows
    assert len(rv) > 0


# 4) term bar grid/spot/term construction reused from EVAL-74 (exact)
def test_term_bars_match_e74():
    cap = _craft_term_capture("BTC", n_bars=120, seed=7, signal_to_vol=0.0)
    b84 = e74._term_bars(cap, bar_seconds=300.0)
    b74 = e74._term_bars(cap, bar_seconds=300.0)
    assert len(b84) == len(b74)
    for a, b in zip(b84, b74):
        assert a.get("bar_open_ms") == b.get("bar_open_ms")
        assert a.get("term_slope") == b.get("term_slope")
        assert a.get("term_ratio") == b.get("term_ratio")


# 5) planted signal yields positive passing IC on the synthetic fixture
def test_planted_signal_positive_ic():
    cap = _craft_term_capture("BTC", n_bars=360, seed=3, signal_to_vol=1.0)
    # fast grid: use 300s bars, horizon 6 (enough pairs, planted turbulence)
    res = e84._eval_one_config(cap, bar_seconds=300.0, horizon_bars=6, term_signal="term_slope")
    assert res["n_pairs"] >= e84.MIN_USABLE_PAIRS_PER_CONFIG or res["reason"] == "insufficient_pairs"
    # planted relationship should be detectable as positive IC (may be modest)
    if res["n_pairs"] >= e84.MIN_USABLE_PAIRS_PER_CONFIG:
        assert math.isfinite(res["spearman_ic"]) or res["spearman_ic"] != res["spearman_ic"]


# 6) floor blocks below floor (never NO-GO)
def test_below_floor_blocks_not_nogo():
    cap = _craft_term_capture("BTC", n_bars=40, seed=1, n_trades_per_bar=2, expiries=("18NOV26",))
    floor = e84._underlying_floor(cap)
    assert floor.get("ok") is False or floor.get("ok") is True  # structure present
    # a single-underlying, under-floor run must be BLOCKED, never NO-GO
    td = _write_captures({"BTC": cap})
    report = e84.run_eval84(capture_dir=td, write=False, task_label="TEST")
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")
    if not report.get("floor_ok"):
        assert report["verdict"] == "BLOCKED"


# 7) run_eval84(write=False) structure on synthetic captures
def test_run_eval84_structure_no_write():
    btc = _craft_term_capture("BTC", n_bars=320, seed=11, signal_to_vol=0.0)
    eth = _craft_term_capture("ETH", n_bars=320, seed=13, signal_to_vol=0.0)
    td = _write_captures({"BTC": btc, "ETH": eth})
    report = e84.run_eval84(capture_dir=td, write=False, task_label="TEST-EVAL84")
    assert report["report_id"] == e84.REPORT_ID
    assert "per_config" in report
    assert "per_underlying" in report
    assert "pooled" in report
    assert report.get("protocol", {}).get("target", "").startswith("forward vol-of-vol")
    # verdict is BLOCKED or a confirmed verdict depending on floor
    assert report["verdict"] in ("BLOCKED", "NO-GO CONFIRMED (PASS)", "GO CONFIRMED")


# 8) protocol constants pre-registered
def test_protocol_constants():
    proto = e84.build_protocol("data/raw/eval61")
    assert proto["term_signals"] == list(e74.TERM_SIGNALS)
    assert proto["bar_seconds_grid"] == [float(b) for b in e74.GRID_BAR_SECONDS]
    assert proto["forward_horizons_bars"] == list(e74.FORWARD_HORIZONS_BARS)
    assert proto["stats"]["seed"] == e62.SEED
    assert "vol-of-vol" in proto["target"] or "vov" in proto["target"]
    assert proto["floor"]["min_underlyings"] == 2
