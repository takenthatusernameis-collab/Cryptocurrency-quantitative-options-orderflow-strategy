#!/usr/bin/env python3
"""EVAL-75: can the **options implied-volatility term structure** (EVAL-74's
newly-measured surface signal) be **monetized net-of-cost** by a signal-timed
delta-hedged ATM straddle?

Why this rung exists (the missing predictiveness -> monetization pairing)
------------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now surface line
so far is:

* EVAL-71 sealed ``GO CONFIRMED`` — the causal options implied-vol *surface*
  (near-ATM IV **level** + put-call skew) predicts forward realized vol
  (BTC best IC 0.335, ETH 0.263);
* EVAL-72 sealed ``NO-GO CONFIRMED (PASS)`` — that **level/skew** signal does
  **not** monetize net-of-cost via a signal-timed delta-hedged ATM straddle;
* EVAL-73 sealed ``GO CONFIRMED (PASS)`` — EVAL-71's predictiveness is stable
  across a disjoint OOS split;
* EVAL-74 sealed ``NO-GO CONFIRMED (PASS)`` — the *term-structure* slope
  (near-minus-far ATM IV) predicts ETH forward RV (8 BH-FDR rejections) but is
  null on BTC, so it does **not** add *portable* predictiveness beyond EVAL-71.

EVAL-72 monetized EVAL-71's *level/skew* signal. It never asked the remaining,
genuinely distinct traded-form question about the **other** predictive surface
signal: **does EVAL-74's term-structure signal — the one surface signal that is
predictive on ETH — survive a real, net-of-cost traded form?** This is a distinct
signal -> monetization pairing (term structure, not level/skew), it is on the
repo charter, and it is runnable **today** because it needs only the
already-acquired real three-way captures (the option trade tape carries the
per-expiry IVs; the surface snapshots carry the real marks/quotes) — **no new
acquisition, no network**. It does not re-litigate any sealed result:

* EVAL-57 traded a **static** VRP straddle (NO-GO);
* EVAL-61/62 traded an **options order-flow**-timed straddle (NO-GO);
* EVAL-72 traded an EVAL-71 **level/skew**-timed straddle (NO-GO);
* **EVAL-75** trades an EVAL-74 **term-structure**-timed straddle.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal term-structure signal
``{term_slope, term_ratio}`` (near-minus-far near-ATM IV slope / ratio from the
real option trade tape, expanding z-scored end-of-bar ``k``), and each bar grid
``{60s, 300s}``: build the real ATM straddle state (front expiry, common strike
nearest spot, IV backed out of the real mark), set ``side_k = sign(z_k)``,
``exposure_k = min(|z_k|, SIZE_CAP)``, and compute the correct mark-path
net-of-cost return (EVAL-62 ``markpath_returns``: delta-hedge + half real 2-leg
spread + hedge fee, spot-normalized). **GO only if, on BOTH BTC and ETH and at
least one config:** net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20),
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower > 0, nonzero
positions > 0, and pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED
(PASS)`` (the term-structure signal does not monetize net-of-cost — predictive is
not monetizable for the term-structure signal either).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-75 consumes BOTH the traded-instrument data (real surface snapshots / perp
candles / option trades) AND the term-structure signal data (per-expiry near-ATM
option trade tape). It therefore composes two honestly pre-registered floors and
requires both:

* the EVAL-61/62 heavy-work floor (surface snapshots / instruments / perp bars /
  option trades / common 5m bars), reused verbatim; and
* the EVAL-74 term-structure floor (which itself reuses the EVAL-71 trade-tape IV
  floor verbatim AND adds a term-structure adequacy floor: >= 2 distinct near-ATM
  expiries with >= 5 trades each, and >= 40 bars carrying a non-null term signal),
  reused verbatim.

Neither is weakened. Below the composed floor it seals
``EVAL_75_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_PREREGISTRATION_<UTC>`` then
``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-57/61/62 traded-form machinery + the EVAL-74 term-structure
# signal verbatim (no forks, no src edits).
import scripts.eval57_vrp_net_of_cost as e57  # noqa: E402
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
import scripts.eval74_surface_term_structure_predictiveness as e74  # noqa: E402
from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
    _sharpe_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)
from src.analytics.strategy_evaluation import (  # noqa: E402
    block_bootstrap_ci,
    permutation_test,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_COMBINED"
PREREG_ID = "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_PREREGISTRATION"
BLOCKED_ID = "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_BLOCKED"

# Pre-registered grid: term-structure signals x bar grid (identical stat grid to
# EVAL-72 / EVAL-62). The term signals are EVAL-74's, reused verbatim.
TERM_SIGNALS: Tuple[str, ...] = e74.TERM_SIGNALS
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
SIGNAL_WINDOW_SECONDS: float = e74.SIGNAL_WINDOW_SECONDS

# Stats / cost / risk constants reused verbatim from EVAL-62 (no forks).
ZWINDOW = e62.ZWINDOW
SIZE_CAP = e62.SIZE_CAP
PERMUTATION_PERMS = e62.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e62.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e62.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
KILL_SWITCH_MAX_DD = e62.KILL_SWITCH_MAX_DD
HEDGE_FEE_BPS = e62.HEDGE_FEE_BPS

# A config must produce at least this many priced states to be evaluable (a
# result-quality guard, not a data floor).
MIN_STATES_PER_CONFIG = 100

# Composed heavy-work floor (both EVAL-61/62 and EVAL-74 floors, unchanged).
FLOOR: Dict[str, Any] = {
    "min_underlyings": e62.MIN_UNDERLYINGS,
    "note": (
        "EVAL-75 consumes both the traded-instrument data (surface snapshots / "
        "perp candles; EVAL-61/62 floor) and the term-structure signal data "
        "(per-expiry near-ATM option trade tape; EVAL-74 term-structure floor, "
        "which itself reuses the sealed EVAL-71 trade-tape IV floor verbatim). Both "
        "sealed floors are reused verbatim and BOTH must pass; neither is weakened. "
        "This is NOT the EVAL-64 options-surface snapshot floor, which governs the "
        "EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "scripts/eval57_vrp_net_of_cost.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
    "scripts/eval75_term_structure_straddle_monetization.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval75_term_structure_straddle_monetization.py "
    "tests/test_eval75_term_structure_straddle_monetization.py",
    "python3 -m pytest -q tests/test_eval75_term_structure_straddle_monetization.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval75_term_structure_straddle_monetization.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval75_term_structure_straddle_monetization.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION",
)


# ---------------------------------------------------------------------------
# Term-structure signal -> causal position (EVAL-74 signal, EVAL-62 state grid)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def term_signal_by_bar_end(
    capture: Dict[str, Any], *, term_signal: str, bar_seconds: float
) -> Dict[int, Optional[float]]:
    """Causal per-bar term-structure signal on the EVAL-62 bar-end grid.

    Reuses EVAL-74's ``_term_bars`` (trailing near-ATM option trade-tape IV grouped
    by expiry -> ``term_slope`` / ``term_ratio``) and maps each value to its bar
    *end* so it aligns exactly with ``e61.toxicity_per_bar`` / ``e62.build_states``
    (``bar_end = ((ts//grid)+1)*grid``). Returns ``{bar_end_ms: raw_signal_or_None}``.
    """
    bars = e74._term_bars(capture, bar_seconds=bar_seconds)
    grid_ms = int(float(bar_seconds) * 1000)
    out: Dict[int, Optional[float]] = {}
    for b in bars:
        end_ms = int(b["bar_open_ms"]) + grid_ms
        out[end_ms] = b.get(term_signal)
    return out


def build_term_straddle_states(
    capture: Dict[str, Any], *, term_signal: str, bar_seconds: float
) -> List[Dict[str, Any]]:
    """Per-bar causal straddle states with the *term-structure* signal as
    side/exposure.

    Identical state schema and straddle construction to EVAL-72 ``build_skew_states``
    (and EVAL-62 ``build_states``: front expiry, common strike nearest spot, IV
    backed out of the real mark), except the driving signal is EVAL-74's causal
    term-structure signal rather than the EVAL-71 level/skew.
    ``side_k = sign(z_k)``, ``exposure_k = min(|z_k|, SIZE_CAP)``; state is
    end-of-bar and the hedge is set at ``k`` and held over ``[k, k+1]`` (strictly
    causal).
    """
    snapshots = sorted(
        capture.get("surface", {}).get("snapshots", []) or [],
        key=lambda s: int(s.get("bar_ms") or 0),
    )
    grid_ms = int(float(bar_seconds) * 1000)
    snap_by_bar_end: Dict[int, Tuple[float, List[Dict[str, Any]]]] = {}
    for snap in snapshots:
        bm = int(snap.get("bar_ms") or 0)
        if bm <= 0:
            continue
        be = ((bm // grid_ms) + 1) * grid_ms
        spot = e61._finite(snap.get("spot"), 0.0)
        quotes = snap.get("quotes") or []
        if spot > 0.0 and quotes:
            snap_by_bar_end[be] = (spot, quotes)

    # Same bar grid as EVAL-62 (perp candles -> bar_end); toxicity itself unused.
    bar_ends, _closes, _tox, _imb = e61.toxicity_per_bar(capture, bar_seconds)

    raw_by_end = term_signal_by_bar_end(
        capture, term_signal=term_signal, bar_seconds=bar_seconds
    )
    raw = [raw_by_end.get(int(be)) for be in bar_ends]
    filled = e71._forward_fill(raw)
    sig_z = e61.expanding_zscore(filled, ZWINDOW)

    states: List[Dict[str, Any]] = []
    for i, bar_end in enumerate(bar_ends):
        hit = snap_by_bar_end.get(int(bar_end))
        if hit is None:
            continue
        spot, quotes = hit
        bar_ms = int(bar_end) - grid_ms
        if bar_ms <= 0:
            continue
        state_time = datetime.fromtimestamp(
            (bar_ms + int(e62.BAR_SECONDS) * 1000) / 1000.0, tz=timezone.utc
        )
        exp = e62._front_expiry(quotes, state_time)
        if not exp:
            continue
        pick = e57._pick_straddle_quotes(quotes, spot, exp)
        if not pick or not pick.get("valid"):
            continue
        legs: List[Dict[str, float]] = []
        ok = True
        for key in ("call", "put"):
            q = pick[key]
            g = e57._iv_and_greeks(
                e61._finite(q.get("mark"), 0.0), e61._finite(q.get("bid"), 0.0),
                e61._finite(q.get("ask"), 0.0), spot, e61._finite(q.get("strike"), 0.0),
                q.get("expiry"), state_time,
                str(q.get("option_type") or key).lower(),
            )
            if g is None:
                ok = False
                break
            legs.append({"key": key, **g})
        if not ok or not legs:
            continue
        straddle_delta = sum(l["delta"] for l in legs)
        straddle_mark = sum(
            e61._finite(q.get("mark"), 0.0) for q in (pick["call"], pick["put"])
        )
        if straddle_mark <= 0.0:
            continue
        z = float(sig_z[i]) if i < len(sig_z) else 0.0
        side = 1 if z > 1e-9 else (-1 if z < -1e-9 else 0)
        exposure = min(abs(z), SIZE_CAP) if side != 0 else 0.0
        states.append({
            "bar_ms": int(bar_ms),
            "spot": float(spot),
            "side": int(side),
            "exposure": float(exposure),
            "straddle_delta": float(straddle_delta),
            "straddle_mark": float(straddle_mark),
            "spread_usd": float(pick.get("spread_usd", 0.0)),
            "signal_z": float(z),
            "strike": float(pick.get("strike", spot)),
        })
    return states


# ---------------------------------------------------------------------------
# Per-config evaluation (statistics reused verbatim from EVAL-62 / EVAL-72)
# ---------------------------------------------------------------------------
def evaluate_config(
    capture: Dict[str, Any], *, term_signal: str, bar_seconds: float
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    states = build_term_straddle_states(
        capture, term_signal=term_signal, bar_seconds=bar_seconds
    )
    if len(states) < MIN_STATES_PER_CONFIG:
        return {
            "underlying": inst, "signal": term_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient priced states", "n_states": len(states),
            "n_returns": 0, "pass": False,
        }
    sr = e62.markpath_returns(states)
    rets = sr["returns"]
    if len(rets) < 3:
        return {
            "underlying": inst, "signal": term_signal,
            "bar_seconds": float(bar_seconds),
            "error": "insufficient returns", "n_states": len(states),
            "n_returns": len(rets), "pass": False,
        }
    sharpe = _sharpe_of_returns(rets)
    mdd = e62._max_drawdown(rets)
    flat = [0.0] * len(rets)
    perm = permutation_test(
        rets, flat, statistic=e62._mean, n_permutations=PERMUTATION_PERMS,
        paired=True, seed=SEED,
    )
    boot = block_bootstrap_ci(
        rets, statistic=_sharpe_of_returns, n_bootstrap=BOOTSTRAP_RESAMPLES,
        block_size=BOOTSTRAP_BLOCK, seed=SEED,
    )
    wf = e62.walkforward_folds(
        rets, train=max(10, len(rets) // 3),
        test=max(10, len(rets) // 5), step=max(10, len(rets) // 5),
    )
    breach = e62.kill_switch_breach(mdd)
    perm_p = e62._finite(perm.get("p_value"), 1.0)
    ci_low = e62._finite(boot[1], 0.0)
    ci_high = e62._finite(boot[2], 0.0)
    passed = bool(
        sharpe > 0.0
        and not breach
        and perm_p < 0.05
        and ci_low > 0.0
        and sr["nonzero"] > 0,
    )
    return {
        "underlying": inst,
        "signal": term_signal,
        "bar_seconds": float(bar_seconds),
        "n_states": len(states),
        "n_returns": len(rets),
        "nonzero_positions": sr["nonzero"],
        "n_hedge_rebalances": sr["n_hedge_rebalances"],
        "n_side_flips": sr["n_side_flips"],
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "kill_switch_breach": breach,
        "permutation_p": perm_p,
        "bootstrap_ci": [boot[0], ci_low, ci_high],
        "dsr": _dsr_of_returns(rets),
        "walkforward": wf,
        "mean_return": e62._mean(rets),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-61/62 traded floor AND EVAL-74 term floor)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    fl_traded = e61._underlying_floor(capture)          # surface snapshots / perp / trades
    fl_signal = e74._underlying_term_floor(capture)     # EVAL-71 trade-tape floor + term adequacy
    ok = bool(fl_traded.get("ok") and fl_signal.get("ok"))
    return {
        "underlying": inst,
        "traded_floor_ok": bool(fl_traded.get("ok")),
        "signal_floor_ok": bool(fl_signal.get("ok")),
        "traded_floor": fl_traded,
        "signal_floor": fl_signal,
        "checks": {
            "traded_floor_ok": bool(fl_traded.get("ok")),
            "signal_floor_ok": bool(fl_signal.get("ok")),
        },
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-75",
        "title": "Options implied-volatility term structure (EVAL-74 near-minus-far "
                 "near-ATM IV slope) -> signal-timed delta-hedged ATM straddle with "
                 "correct mark-path net-of-cost P&L: traded-form monetization "
                 "falsification on the real on-disk three-way captures",
        "extends": "EVAL-72 (identical correct mark-path net-of-cost delta-hedged "
                    "ATM straddle traded form) but a different, on-charter signal "
                    "source: EVAL-74's term-structure slope (near-minus-far near-ATM "
                    "IV) rather than the EVAL-71 level/skew; no new acquisition",
        "supersedes": "nothing — this is the traded-form monetization complement to "
                      "EVAL-74's term-structure predictiveness; EVAL-57 traded a "
                      "static VRP straddle (NO-GO), EVAL-61/62 traded an order-flow-"
                      "timed straddle (NO-GO), and EVAL-72 traded an EVAL-71 level/"
                      "skew-timed straddle (NO-GO), so a term-structure-timed straddle "
                      "is genuinely new",
        "capture_dir": str(capture_dir),
        "term_signals": list(TERM_SIGNALS),
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "position": "side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal "
                    "decision at bar k; z_k = expanding-z of the causal EVAL-74 "
                    "term-structure signal",
        "traded_form": "ATM straddle (front expiry, common strike nearest spot, IV "
                       "backed out of the real mark via EVAL-57 helpers) with the "
                       "EVAL-62 mark-path net-of-cost P&L: delta-hedge + half real "
                       "2-leg spread + hedge fee, spot-normalized",
        "zwindow": int(ZWINDOW),
        "size_cap": float(SIZE_CAP),
        "hedge_fee_bps": float(HEDGE_FEE_BPS),
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
        },
        "kill_switch_max_dd": KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one grid config, net-of-cost "
            "Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional "
            "permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions "
            "> 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "floor": {
            "composed_of": ["EVAL-61/62 traded-instrument floor",
                            "EVAL-74 term-structure floor (EVAL-71 trade-tape floor + term adequacy)"],
            "min_underlyings": int(FLOOR["min_underlyings"]),
            "note": FLOOR["note"],
        },
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def _select_one_capture_per_underlying(
    captures: Sequence[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Richest (most real option trades) real capture per underlying; deterministic."""
    best: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = str(c.get("underlying") or "?")
        score = len(c.get("option_trades", []) or [])
        if inst not in best or score > len(best[inst].get("option_trades", []) or []):
            best[inst] = c
    return [best[k] for k in sorted(best)]


def run_eval75(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_one_capture_per_underlying(e61._capture_inventory(str(capture_dir_abs)))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)

    floor_ok = bool(
        len(captures) >= int(FLOOR["min_underlyings"])
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for sig in TERM_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                try:
                    res = evaluate_config(
                        cap, term_signal=sig, bar_seconds=bar_s
                    )
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{cap.get('underlying')}::{sig}::bar{bar_s}: {exc!r}")
                    continue
                per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}":
            e62._finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_returns", 0) > 0]
        best = max(valid, key=lambda r: e62._finite(r.get("sharpe"), -1e9)) if valid else None
        pass_configs = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": e62._finite(best.get("sharpe"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}" if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION" if floor_ok
        else "EVAL_75_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "term-structure-timed delta-hedged ATM straddle with correct mark-path "
            "net-of-cost P&L (traded-form monetization of EVAL-74's predictive "
            "term-structure signal) on the real on-disk captures"
            if floor_ok else "capture below the composed pre-registered floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": dict(FLOOR),
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    prereg = _build_prereg(report)
    e62._seal(PREREG_ID, prereg, _build_prereg_md)

    if not floor_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), _build_blocked_md)
        return report

    e62._seal(REPORT_ID, report, _build_md)
    return report


# ---------------------------------------------------------------------------
# Seal artifact builders
# ---------------------------------------------------------------------------
def _build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "The causal options implied-volatility TERM STRUCTURE (EVAL-74 near-dated "
            "minus far-dated near-ATM IV slope, and its ratio) can be monetized "
            "net-of-cost by a signal-timed delta-hedged ATM straddle on the BTC/ETH "
            "perpetual, on the already-acquired real on-disk captures at the composed "
            "floor."
        ),
        "extends": p["extends"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    lines = [
        f"# {PREREG_ID} — term-structure signal -> signal-timed delta-hedged ATM "
        f"straddle net-of-cost monetization falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Term signals: {p['term_signals']}",
        f"- Signal window (s): {p['signal_window_seconds']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Position: {p['position']}",
        f"- Traded form: {p['traded_form']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation_paired']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['zwindow']} / size_cap {p['size_cap']}",
        f"- Kill-switch max-DD: {p['kill_switch_max_dd']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered composed floor (both sealed floors; neither weakened)",
        "",
        f"- {p['floor']['note']}",
        f"- Composed of: {p['floor']['composed_of']}",
        f"- Min underlyings: {p['floor']['min_underlyings']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — term-structure signal -> signal-timed delta-hedged ATM "
        f"straddle net-of-cost monetization falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor (composed)",
        "",
        "| underlying | traded floor ok | term-signal floor ok | ok |",
        "|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"| {inst} | {fl['traded_floor_ok']} | {fl['signal_floor_ok']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config by Sharpe)", "",
              "| underlying | configs | best Sharpe | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_sharpe']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- All underlyings pass: {r['pooled']['all_underlyings_pass']}"]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "underlyings": r["underlyings"],
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — term-structure signal -> signal-timed delta-hedged ATM "
        f"straddle (below the composed pre-registered floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the composed EVAL-61/62 + EVAL-74 floor, so no "
        "GO/NO-GO verdict is emitted. Do NOT weaken either floor, do NOT use "
        "synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(
            f"- {inst}: traded_floor_ok={fl.get('traded_floor_ok')} "
            f"signal_floor_ok={fl.get('signal_floor_ok')}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-75: term-structure-timed delta-hedged ATM straddle "
                    "net-of-cost monetization falsification on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval75(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(),
                "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "per_underlying_floor": {},
                "floor": dict(FLOOR),
                "floor_ok": False,
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, _build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying": report.get("per_underlying"),
        "bh_fdr_rejected": report.get("pooled", {}).get("bh_fdr", {}).get("rejected"),
        "n_configs": len(report.get("per_config", [])),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())