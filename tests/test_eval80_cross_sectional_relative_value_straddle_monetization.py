"""Unit tests for EVAL-80: the **cross-sectional relative-value** monetization of
EVAL-77's cross-sectional implied-volatility basis.

EVAL-80 is the on-charter, runnable-now traded-form capstone: it takes EVAL-77's
BTC-vs-ETH relative near-ATM IV / skew basis (a GO predictiveness signal) and
trades it through a two-leg relative-value delta-hedged ATM straddle spread (long
the relatively-cheap-vol underlying, short the relatively-rich-vol underlying),
with the correct EVAL-62 mark-path net-of-cost P&L per leg, summed. It needs no
new acquisition and no network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin eight things the next session must not break:
1. the artifact ids are EVAL-80;
2. the sealed machinery (EVAL-57/61/62/71/77 helpers) is reused verbatim, not forked;
3. ``build_atm_straddle_states`` builds causal per-bar ATM straddle instrument
   states keyed by bar_ms;
4. ``build_relative_value_legs`` aligns the two underlyings on the common grid and
   sets the BTC leg side = sign(rel_z), the ETH leg side = -sign(rel_z);
5. the two legs' EVAL-62 mark-path returns are summed into the relative-value
   return series;
6. the composed floor ANDs the EVAL-61/62 traded floor, the EVAL-71 surface floor
   (both underlyings) and the cross-sectional straddle alignment floor (none
   weakened);
7. ``run_eval80(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
8. the Sharpe/statistics are deterministic.
"""

from __future__ import annotations

import json
import math
import random
import tempfile
from pathlib import Path

import scripts.eval57_vrp_net_of_cost as e57
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61
import scripts.eval62_orderflow_realized_vol_markpath as e62
import scripts.eval71_surface_iv_rv_predictiveness as e71
import scripts.eval77_cross_sectional_surface_basis_rv_predictiveness as e77
import scripts.eval80_cross_sectional_relative_value_straddle_monetization as e80

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _craft_capture(inst="BTC", n_bars=200, seed=0, base_iv=0.8,
                   base_ms=_BASE_MS, bar_ms=_BAR_MS, with_snapshots=True):
    """Deterministic three-way capture with perp candles, a near-ATM option trade
    tape (real ``iv`` per trade) and (optionally) surface snapshots with quotes so
    the ATM straddle prices on each bar."""
    rng = random.Random(seed)
    px = 60000.0 if inst == "BTC" else 3000.0
    candles = []
    trades = []
    snaps = []
    for i in range(n_bars):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        ts = base_ms + i * bar_ms
        candles.append({"ts": ts, "open": px, "high": px, "low": px, "close": px})
        iv_level = max(0.05, base_iv + 0.1 * math.sin(i * 0.1)
                       + rng.uniform(-0.005, 0.005))
        for opt in ("C", "P"):
            iv = max(0.05, iv_level + (0.03 if opt == "P" else -0.03)
                     + rng.uniform(-0.003, 0.003))
            trades.append({
                "ts": ts + 1,
                "instrument": f"{inst}-OPT-{int(round(px))}-{opt}",
                "direction": "buy",
                "amount": rng.uniform(0.5, 2.0),
                "price": 0.01,
                "index_price": px,
                "iv": iv,
                "option_type": "call" if opt == "C" else "put",
                "strike": round(px, 2),
                "expiry": "2026-12-30T08:00:00Z",
            })
        if with_snapshots:
            # one ATM straddle snapshot per bar: a call and a put at the ATM strike
            # with a real mark/bid/ask so EVAL-57 can back out greeks.
            k = round(px, 2)
            snaps.append({
                "bar_ms": ts,
                "spot": px,
                "quotes": [
                    {"strike": k, "option_type": "call",
                     "mark": 0.02, "bid": 0.019, "ask": 0.021,
                     "expiry": "2026-12-30T08:00:00Z"},
                    {"strike": k, "option_type": "put",
                     "mark": 0.02, "bid": 0.019, "ask": 0.021,
                     "expiry": "2026-12-30T08:00:00Z"},
                ],
            })

    return {
        "schema": "three_way_options_surface_orderflow_okx_perp_capture_v1",
        "underlying": inst,
        "venue": "deribit+okx",
        "window_start": "2023-11-14T00:00:00Z",
        "window_end": "2023-11-15T00:00:00Z",
        "surface": {"bar_seconds": 300, "resolution": "5",
                    "snapshots": snaps if with_snapshots else []},
        "option_trades": trades,
        "perp_candles": candles,
        "okx_inst_id": f"{inst}-USD-SWAP",
        "okx_perp_trades": [],
        "source": {"authenticated": False, "public_read_only": True,
                   "venue": "deribit+okx"},
    }


def _captures(n_bars=200, seed_btc=1, seed_eth=2, with_snapshots=True):
    return {
        "BTC": _craft_capture("BTC", n_bars=n_bars, seed=seed_btc, base_iv=0.8,
                              with_snapshots=with_snapshots),
        "ETH": _craft_capture("ETH", n_bars=n_bars, seed=seed_eth, base_iv=0.9,
                              with_snapshots=with_snapshots),
    }


def test_ids_are_eval80():
    assert e80.REPORT_ID.startswith("EVAL_80_")
    assert e80.PREREG_ID.startswith("EVAL_80_")
    assert e80.BLOCKED_ID.startswith("EVAL_80_")
    assert "CROSS_SECTIONAL" in e80.REPORT_ID
    assert "RELATIVE_VALUE" in e80.REPORT_ID


def test_reuses_sealed_machinery_verbatim():
    """EVAL-80 must reuse the sealed EVAL-57/61/62/71/77 helpers, not fork them."""
    assert e80.e57 is e57
    assert e80.e61 is e61
    assert e80.e62 is e62
    assert e80.e71 is e71
    assert e80.e77 is e77
    # EVAL-77 cross-section + relative signal, verbatim
    assert e80.e77.build_cross_section is e77.build_cross_section
    assert e80.e77._relative_signal_series is e77._relative_signal_series
    # EVAL-71 surface, EVAL-62 mark-path P&L, EVAL-57 greeks, verbatim
    assert e80.e71.build_surface_bars is e71.build_surface_bars
    assert e80.e71._forward_fill is e71._forward_fill
    assert e80.e71._underlying_surface_floor is e71._underlying_surface_floor
    assert e80.e62.markpath_returns is e62.markpath_returns
    assert e80.e62.build_states is e62.build_states
    assert e80.e61._underlying_floor is e61._underlying_floor
    # stats / cost constants match the sealed sources exactly
    assert e80.ZWINDOW == e62.ZWINDOW
    assert e80.SIZE_CAP == e62.SIZE_CAP
    assert e80.PERMUTATION_PERMS == e62.PERMUTATION_PERMS
    assert e80.BOOTSTRAP_RESAMPLES == e62.BOOTSTRAP_RESAMPLES
    assert e80.BOOTSTRAP_BLOCK == e62.BOOTSTRAP_BLOCK
    assert e80.SEED == e62.SEED
    assert e80.FDR_ALPHA == e62.FDR_ALPHA


def test_build_atm_straddle_states_keyed_by_bar_ms():
    cap = _craft_capture("BTC", n_bars=30, seed=3)
    states = e80.build_atm_straddle_states(cap, bar_seconds=300.0)
    assert len(states) > 0
    for bar_ms, st in states.items():
        assert isinstance(bar_ms, int)
        assert st["spot"] > 0.0
        assert st["straddle_mark"] > 0.0
        assert math.isfinite(st["straddle_delta"])
        assert math.isfinite(st["spread_usd"])


def test_build_relative_value_legs_sides_are_mirror(monkeypatch):
    """BTC leg side = sign(rel_z); ETH leg side = -sign(rel_z); equal exposure."""
    caps = _captures(n_bars=60, seed_btc=5, seed_eth=6)
    legs = e80.build_relative_value_legs(caps, surface_signal="atm_iv",
                                         bar_seconds=300.0)
    assert len(legs["btc_leg"]) == len(legs["eth_leg"])
    assert len(legs["btc_leg"]) > 0
    for b, e in zip(legs["btc_leg"], legs["eth_leg"]):
        assert b["bar_ms"] == e["bar_ms"]
        assert b["side"] == -e["side"]
        assert abs(b["exposure"] - e["exposure"]) < 1e-12
        # side is the sign of the (shared) signal_z
        z = b["signal_z"]
        expected_side = 1 if z > 1e-9 else (-1 if z < -1e-9 else 0)
        assert b["side"] == expected_side
        assert e["signal_z"] == b["signal_z"]


def test_relative_value_returns_sum_two_markpath_legs(monkeypatch):
    """The combined return is the sum of the two per-leg EVAL-62 mark-path returns."""
    caps = _captures(n_bars=160, seed_btc=7, seed_eth=8)
    legs = e80.build_relative_value_legs(caps, surface_signal="skew",
                                         bar_seconds=300.0)
    rb = e62.markpath_returns(legs["btc_leg"])["returns"]
    re = e62.markpath_returns(legs["eth_leg"])["returns"]
    n = min(len(rb), len(re))
    res = e80.evaluate_config(caps, basis_signal="skew", bar_seconds=300.0)
    # evaluate_config's mean_return must equal the mean of the summed series
    expected = [rb[k] + re[k] for k in range(n)]
    assert abs(res["mean_return"] - e62._mean(expected)) < 1e-12
    assert res["n_states"] == len(legs["btc_leg"])


def test_campaign_floor_composes_all_three_floors(monkeypatch):
    ok_floor = {"ok": True, "n_option_trades": 100}
    monkeypatch.setattr(e71, "_underlying_surface_floor", lambda cap: ok_floor)
    monkeypatch.setattr(e61, "_underlying_floor", lambda cap: {"ok": True})
    monkeypatch.setattr(e80, "_common_straddle_bars",
                        lambda captures, bar_seconds: 250)
    caps = _captures(n_bars=200, seed_btc=9, seed_eth=10)
    fl = e80.campaign_floor(caps)
    assert fl["ok"] is True
    assert fl["underlyings_ok"] is True and fl["aligned_ok"] is True
    assert fl["aligned_common_straddle_bars_binding"] == 250

    # one underlying below the traded floor -> not ok
    monkeypatch.setattr(
        e61, "_underlying_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC"},
    )
    fl2 = e80.campaign_floor(caps)
    assert fl2["ok"] is False and fl2["underlyings_ok"] is False

    # floors restored but alignment below 200 -> not ok
    monkeypatch.setattr(e61, "_underlying_floor", lambda cap: {"ok": True})
    monkeypatch.setattr(e80, "_common_straddle_bars",
                        lambda captures, bar_seconds: 10)
    fl3 = e80.campaign_floor(caps)
    assert fl3["ok"] is False and fl3["aligned_ok"] is False


def test_campaign_floor_blocks_short_capture():
    caps = _captures(n_bars=10, seed_btc=11, seed_eth=12)
    fl = e80.campaign_floor(caps)
    assert fl["ok"] is False
    assert fl["underlyings_ok"] is False or fl["aligned_ok"] is False


def test_evaluate_config_runs_and_is_bounded(monkeypatch):
    monkeypatch.setattr(e80, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e80, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=13, seed_eth=14)
    res = e80.evaluate_config(caps, basis_signal="atm_iv", bar_seconds=300.0)
    assert res["n_states"] >= e80.MIN_STATES_PER_CONFIG
    assert res["n_returns"] >= 3
    assert math.isfinite(res["sharpe"])
    assert 0.0 <= res["permutation_p"] <= 1.0
    ci = res["bootstrap_ci"]
    assert len(ci) == 3
    assert res["pass"] == (
        res["sharpe"] > 0.0
        and not res["kill_switch_breach"]
        and res["permutation_p"] < 0.05
        and ci[1] > 0.0
        and res["nonzero_positions"] > 0
    )


def test_evaluate_config_is_deterministic(monkeypatch):
    monkeypatch.setattr(e80, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e80, "BOOTSTRAP_RESAMPLES", 50)
    caps = _captures(n_bars=200, seed_btc=15, seed_eth=16)
    a = e80.evaluate_config(caps, basis_signal="skew", bar_seconds=300.0)
    b = e80.evaluate_config(caps, basis_signal="skew", bar_seconds=300.0)
    assert a["sharpe"] == b["sharpe"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_run_eval80_no_write_blocks_below_floor():
    caps = _captures(n_bars=20, seed_btc=17, seed_eth=18)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e80.run_eval80(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e80.REPORT_ID


def test_run_eval80_no_write_meets_floor_and_summarizes(monkeypatch):
    """Orchestration above the composed floor (forced green here to keep the test
    fast; the real floor is exercised on the real captures by the driver)."""
    monkeypatch.setattr(e80, "BASIS_SIGNALS", ("atm_iv",))
    monkeypatch.setattr(e80, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e80, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e80, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e80, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "per_underlying": {},
                          "underlyings_ok": True, "aligned_ok": True,
                          "aligned_common_straddle_bars_by_grid": {"300.0": 250},
                          "aligned_common_straddle_bars_binding": 250, "ok": True,
                          "checks": {}},
    )
    caps = _captures(n_bars=200, seed_btc=19, seed_eth=20)
    with tempfile.TemporaryDirectory() as td:
        for inst, cap in caps.items():
            p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
            p.write_text(json.dumps(cap))
        report = e80.run_eval80(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    assert report["summary"]["n_configs"] == 1
    assert len(report["per_config"]) == 1
    cs = report["protocol"]["cross_section"]
    assert cs["baseline"] == "BTC"
    assert cs["relative"] == "ETH"
    assert "relative-value" in cs["combination"].lower() or "ret_rel" in cs["combination"]


def test_protocol_and_floor_constants():
    p = e80.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_aligned_common_straddle_bars"] == 200
    assert p["stats"]["min_states_per_config"] == e80.MIN_STATES_PER_CONFIG
    assert set(p["basis_signals"]) == {"atm_iv", "skew"}
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["cross_section"]["baseline"] == "BTC"
    assert p["cross_section"]["relative"] == "ETH"
    assert "EVAL-77" in p["extends"]
    assert "EVAL-76" in p["extends"]
    assert "cross-sectional" in p["title"].lower()
    assert "EVAL-71" in p["floor"]["note"]