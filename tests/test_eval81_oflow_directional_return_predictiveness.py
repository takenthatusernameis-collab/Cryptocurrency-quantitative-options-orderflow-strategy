"""Unit tests for EVAL-81: the **options order-flow imbalance -> subsequent
signed (directional) return** predictiveness.

EVAL-81 is the on-charter, runnable-now cell that EVAL-65 (options flow -> RV),
EVAL-70 (perp flow -> signed return) and EVAL-78/79 (options flow x surface -> RV)
leave open: the causal options order-flow signed-aggressor imbalance vs the
subsequent *signed return* (direction) of the underlying. It reuses the sealed
EVAL-61/62/65/71 signal reconstructions verbatim, needs no new acquisition and no
network.

Deterministic in-memory fixtures only (unit-test inputs). No real data, no
research_state writes, no network.

These tests pin the things the next session must not break:
1. the artifact ids are EVAL-81;
2. the sealed machinery (EVAL-61/62/65/71 helpers) is reused verbatim, not forked;
3. ``evaluate_predictiveness`` targets the forward **signed return** (not RV) and
   its Spearman IC / permutation / bootstrap inference is bounded and deterministic;
4. the composed floor ANDs the EVAL-71 surface floor and the order-flow state floor
   (neither weakened);
5. ``run_eval81(write=False)`` reports BLOCKED below the composed floor and a
   verdict above it;
6. the protocol/floor constants are the pre-registered ones.
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
import scripts.eval81_oflow_directional_return_predictiveness as e81

_BASE_MS = 1_700_000_000_000
_BAR_MS = 300_000


def _states(n=220, seed=0, spot0=60000.0):
    """Deterministic per-bar order-flow states (spot random walk + signed z)."""
    rng = random.Random(seed)
    px = spot0
    out = []
    for i in range(n):
        px = max(1.0, px * (1 + rng.uniform(-1, 1) * 1e-4))
        out.append({"bar_ms": _BASE_MS + i * _BAR_MS, "spot": px,
                    "signal_z": rng.uniform(-2.0, 2.0)})
    return out


def _captures():
    """Minimal capture dicts (one per underlying); ``build_states`` is
    monkeypatched in the tests that need priceable states."""
    return {
        "BTC": {"underlying": "BTC", "surface": {"snapshots": []},
                "option_trades": [], "perp_candles": []},
        "ETH": {"underlying": "ETH", "surface": {"snapshots": []},
                "option_trades": [], "perp_candles": []},
    }


def _write_captures(caps):
    td = tempfile.mkdtemp()
    for inst, cap in caps.items():
        p = Path(td) / f"three_way_{inst}_20230101T000000Z.json"
        p.write_text(json.dumps(cap))
    return td


# ---------------------------------------------------------------------------
# 1) artifact ids
# ---------------------------------------------------------------------------
def test_ids_are_eval81():
    assert e81.REPORT_ID.startswith("EVAL_81_")
    assert e81.PREREG_ID.startswith("EVAL_81_")
    assert e81.BLOCKED_ID.startswith("EVAL_81_")
    assert "DIRECTIONAL_RETURN" in e81.REPORT_ID


# ---------------------------------------------------------------------------
# 2) sealed machinery reused verbatim
# ---------------------------------------------------------------------------
def test_reuses_sealed_machinery_verbatim():
    assert e81.e61 is e61
    assert e81.e62 is e62
    assert e81.e65 is e65
    assert e81.e71 is e71
    # EVAL-71 surface floor, EVAL-62 states, EVAL-65 IC stats — verbatim
    assert e81.e71._underlying_surface_floor is e71._underlying_surface_floor
    assert e81.e62.build_states is e62.build_states
    assert e81.e65._perm_p_ic is e65._perm_p_ic
    assert e81.e65._boot_ci_ic is e65._boot_ci_ic
    # stats / cost constants match the sealed sources exactly
    assert e81.PERMUTATION_PERMS == e65.PERMUTATION_PERMS
    assert e81.BOOTSTRAP_RESAMPLES == e65.BOOTSTRAP_RESAMPLES
    assert e81.BOOTSTRAP_BLOCK == e65.BOOTSTRAP_BLOCK
    assert e81.SEED == e62.SEED
    assert e81.ZWINDOW == e62.ZWINDOW
    assert e81.FDR_ALPHA == e62.FDR_ALPHA


# ---------------------------------------------------------------------------
# 3) evaluate_predictiveness targets the forward signed return
# ---------------------------------------------------------------------------
def test_evaluate_predictiveness_targets_signed_return(monkeypatch):
    monkeypatch.setattr(e81, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e81, "BOOTSTRAP_RESAMPLES", 50)
    states = _states(n=220, seed=0)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states)
    res = e81.evaluate_predictiveness(
        {"underlying": "BTC"}, oflow_signal="imbalance",
        bar_seconds=300.0, horizon_bars=6,
    )
    assert res["target"] == "signed_return"
    assert res["underlying"] == "BTC"
    # n_pairs = len(states) - horizon
    assert res["n_pairs"] == 220 - 6
    assert -1.0 <= res["spearman_ic"] <= 1.0
    assert 0.0 <= res["permutation_p"] <= 1.0
    ci = res["bootstrap_ci"]
    assert len(ci) == 3 and ci[1] <= ci[0] <= ci[2]
    assert res["pass"] == (
        res["spearman_ic"] > 0.0
        and res["permutation_p"] < 0.05
        and ci[1] > 0.0
    )


def test_target_is_the_signed_return_not_rv(monkeypatch):
    """Deterministic proof the target is the *signed* sum of log returns: build a
    spot path whose two-bar forward log-return exactly equals the signed z, then
    the Spearman IC must be ~1 (perfect rank correlation)."""
    monkeypatch.setattr(e81, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e81, "BOOTSTRAP_RESAMPLES", 50)
    n = 220
    rng = random.Random(7)
    spots = [100.0]
    for _ in range(n):
        spots.append(spots[-1] * (1 + rng.uniform(-0.02, 0.02)))
    lr = [math.log(spots[i + 1] / spots[i]) for i in range(len(spots) - 1)]
    states = []
    for k in range(n):
        fwd2 = (lr[k] + lr[k + 1]) if (k + 1) < len(lr) else 0.0
        states.append({"bar_ms": _BASE_MS + k * _BAR_MS, "spot": spots[k],
                       "signal_z": fwd2})
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states)
    res = e81.evaluate_predictiveness(
        {"underlying": "BTC"}, oflow_signal="imbalance",
        bar_seconds=300.0, horizon_bars=2,
    )
    # signal_z[k] == forward 2-bar signed return -> rank IC ~ 1
    assert res["spearman_ic"] > 0.99
    assert res["pass"] is True


def test_evaluate_predictiveness_is_deterministic(monkeypatch):
    monkeypatch.setattr(e81, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e81, "BOOTSTRAP_RESAMPLES", 50)
    states = _states(n=220, seed=3)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states)
    a = e81.evaluate_predictiveness(
        {"underlying": "ETH"}, oflow_signal="imbalance",
        bar_seconds=300.0, horizon_bars=6,
    )
    b = e81.evaluate_predictiveness(
        {"underlying": "ETH"}, oflow_signal="imbalance",
        bar_seconds=300.0, horizon_bars=6,
    )
    assert a["spearman_ic"] == b["spearman_ic"]
    assert a["permutation_p"] == b["permutation_p"]
    assert a["bootstrap_ci"] == b["bootstrap_ci"]


def test_evaluate_predictiveness_insufficient_states(monkeypatch):
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: _states(n=5, seed=1))
    res = e81.evaluate_predictiveness(
        {"underlying": "BTC"}, oflow_signal="imbalance",
        bar_seconds=300.0, horizon_bars=6,
    )
    assert res["n_pairs"] == 0
    assert res["pass"] is False
    assert "error" in res


# ---------------------------------------------------------------------------
# 4) composed floor
# ---------------------------------------------------------------------------
def test_campaign_floor_composes_both_floors(monkeypatch):
    ok_floor = {"ok": True, "n_option_trades": 100}
    monkeypatch.setattr(e71, "_underlying_surface_floor", lambda cap: ok_floor)
    states_250 = [{"bar_ms": _BASE_MS + i * _BAR_MS, "spot": 1.0, "signal_z": 0.1}
                  for i in range(250)]
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states_250)

    caps = _captures()
    fl = e81.campaign_floor(caps)
    assert fl["ok"] is True
    assert fl["checks"]["all_underlyings_ok"] is True
    for u in fl["per_underlying"].values():
        assert u["surface_floor_ok"] is True
        assert u["oflow_ok"] is True
        assert u["ok"] is True

    # surface floor fails for one underlying -> not ok
    monkeypatch.setattr(
        e71, "_underlying_surface_floor",
        lambda cap: {"ok": cap.get("underlying") == "BTC", "n_option_trades": 100},
    )
    assert e81.campaign_floor(caps)["ok"] is False


def test_campaign_floor_blocks_below_oflow_floor(monkeypatch):
    monkeypatch.setattr(e71, "_underlying_surface_floor",
                        lambda cap: {"ok": True, "n_option_trades": 100})
    few = [{"bar_ms": _BASE_MS + i * _BAR_MS, "spot": 1.0, "signal_z": 0.1}
           for i in range(5)]
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: few)
    fl = e81.campaign_floor(_captures())
    assert fl["ok"] is False
    assert all(u["oflow_ok"] is False for u in fl["per_underlying"].values())


def test_campaign_floor_blocks_short_capture():
    caps = {"BTC": {"underlying": "BTC", "surface": {"snapshots": []},
                    "option_trades": [], "perp_candles": []}}
    fl = e81.campaign_floor(caps)
    assert fl["ok"] is False


# ---------------------------------------------------------------------------
# 5) orchestration (write=False; no research_state writes)
# ---------------------------------------------------------------------------
def test_run_eval81_no_write_blocks_below_floor():
    caps = _captures()
    td = _write_captures(caps)
    report = e81.run_eval81(capture_dir=td, write=False)
    assert report["floor_ok"] is False
    assert report["verdict"] == "BLOCKED"
    assert report["report_id"] == e81.REPORT_ID


def test_run_eval81_no_write_meets_floor_and_summarizes(monkeypatch):
    monkeypatch.setattr(e81, "GRID_BAR_SECONDS", (300.0,))
    monkeypatch.setattr(e81, "FORWARD_HORIZONS_BARS", (6,))
    monkeypatch.setattr(e81, "PERMUTATION_PERMS", 50)
    monkeypatch.setattr(e81, "BOOTSTRAP_RESAMPLES", 50)
    monkeypatch.setattr(
        e81, "campaign_floor",
        lambda captures: {"underlyings": sorted(captures), "ok": True,
                          "per_underlying": {i: {"ok": True} for i in captures},
                          "checks": {"all_underlyings_ok": True}},
    )
    states = _states(n=220, seed=5)
    monkeypatch.setattr(e62, "build_states",
                        lambda cap, tox_signal, bar_seconds: states)
    td = _write_captures(_captures())
    report = e81.run_eval81(capture_dir=td, write=False)
    assert report["floor_ok"] is True
    assert report["verdict"] in ("GO CONFIRMED", "NO-GO CONFIRMED (PASS)")
    assert set(report["underlyings"]) == {"BTC", "ETH"}
    # one config per underlying (1 sig x 1 grid x 1 horizon) x 2 underlyings
    assert len(report["per_config"]) == 2
    assert all("underlying" in c for c in report["per_config"])


# ---------------------------------------------------------------------------
# 6) protocol / floor constants
# ---------------------------------------------------------------------------
def test_protocol_and_floor_constants():
    p = e81.build_protocol("data/raw/eval61")
    assert p["floor"]["min_underlyings"] == 2
    assert p["floor"]["min_oflow_states_per_underlying"] == 200
    assert p["floor"]["min_usable_pairs_per_config"] == e81.MIN_USABLE_PAIRS_PER_CONFIG
    assert p["oflow_signals"] == ["imbalance"]
    assert p["target"] == "signed_return"
    assert p["bar_seconds_grid"] == [60.0, 300.0]
    assert p["forward_horizons_bars"] == [6, 24, 72]
    assert "EVAL-65" in p["extends"]
    assert "EVAL-70" in p["extends"]
    assert "EVAL-71" in p["floor"]["note"]
    assert "signed" in p["target_detail"].lower()
    assert "direction" in p["title"].lower()