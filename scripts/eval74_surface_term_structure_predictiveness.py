#!/usr/bin/env python3
"""EVAL-74: does the **options implied-volatility term structure** — the slope
between near-dated and far-dated near-ATM implied vol — predict subsequent
realized volatility? A distinct-surface-signal falsification that is runnable
**now** on the real on-disk three-way captures.

Why this rung exists (the next runnable-now heavy work)
------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + options order-flow + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now surface line
so far is:

* EVAL-71 sealed ``GO CONFIRMED`` — the causal options implied-vol *surface*
  (near-ATM IV **level** + put-call skew) predicts forward realized vol of the
  BTC/ETH perpetual (BTC best IC 0.335, ETH 0.263);
* EVAL-72 sealed ``NO-GO CONFIRMED (PASS)`` — that surface signal does **not**
  monetize net-of-cost via a signal-timed delta-hedged ATM straddle;
* EVAL-73 sealed ``GO CONFIRMED (PASS)`` — EVAL-71's predictiveness is stable
  across a disjoint early/late split of the same captures.

EVAL-71's surface signal is the *level* (atm_iv) and the *put-call skew* at the
front of the surface. It never asked the remaining, genuinely distinct
surface question: **does the *term structure* of implied vol — the near-minus-
far ATM IV slope across the real Deribit expiry ladder — carry portable
predictive information about forward realized vol?** This is a different signal
(a cross-expiry *shape*, not a level/skew), it is on the repo charter, and it is
runnable today because it needs only the already-acquired real three-way captures
(each option trade carries a real ``iv``, ``strike``, ``expiry`` and the perp
candles carry the reference spot) — **no new acquisition, no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each causal term-structure signal
``{term_slope, term_ratio}`` (``term_slope = IV(near expiry) - IV(far expiry)``
in vol points; ``term_ratio = IV(near)/IV(far) - 1``), each bar grid
``{60s, 300s}`` and each forward horizon ``H`` bars:

* the causal per-bar near-ATM IV is grouped by option expiry; ``near`` is the
  earliest expiry and ``far`` the latest expiry (each with at least
  ``MIN_EXPIRY_TRADES`` near-ATM trades in the trailing ``SIGNAL_WINDOW_SECONDS``
  window ending at bar end ``k``); both signals are expanding z-scored
  end-of-bar ``k`` exactly as EVAL-71 (``e61.expanding_zscore``); and
* the Spearman rank ``IC = rho(signal_z_k, rv_{k+1..k+H})`` and its directional
  permutation ``p`` (H1: ``IC > 0``) are computed with the sealed EVAL-65
  primitives; a steeper (higher) near-minus-far IV slope is hypothesised to
  predict *higher* forward realized vol (near-dated vol premium -> near-term
  stress), so ``H1: IC > 0``.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (the
term-structure slope does not add *portable* forward-vol predictiveness beyond
EVAL-71's level/skew).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
-------------------------------------------------------------------------------
EVAL-74 consumes the same trade-tape IV data as EVAL-71, so it reuses the sealed
EVAL-71 trade-tape floor verbatim on the full capture (option trades / near-ATM
trades / perp candles / span) AND additionally requires a term-structure
adequacy floor (at least ``MIN_DISTINCT_EXPIRIES`` distinct near-ATM expiries
with ``MIN_EXPIRY_TRADES`` trades each, and at least ``MIN_BARS_WITH_TERM`` bars
carrying a non-null term signal). Neither is weakened. Below the composed floor
it seals ``EVAL_74_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible
floor that governs the EVAL-67/68/69 ladder is untouched.

Seals ``EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-61/62/65 primitives + EVAL-71 surface machinery verbatim
# (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_BLOCKED"

# Pre-registered grid: term-structure signals x bar grid x horizons.
TERM_SIGNALS: Tuple[str, ...] = ("term_slope", "term_ratio")
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)

# Trailing window (seconds) over which option trades are aggregated into the
# per-expiry surface at each bar end; identical to EVAL-71.
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
# Near-ATM band; identical to EVAL-71.
ATM_BAND: float = e71.ATM_BAND

# Per-expiry adequacy: an expiry bucket must carry >= this many near-ATM trades
# in the window before its mean IV is trusted (derived, pre-registered).
MIN_EXPIRY_TRADES: int = 5
# Term-structure adequacy: at least this many distinct near-ATM expiries (with
# >= MIN_EXPIRY_TRADES trades) must exist over the capture, and at least this
# many bars must carry a non-null term signal (near AND far present).
MIN_DISTINCT_EXPIRIES: int = 2
MIN_BARS_WITH_TERM: int = 40

# Statistics reused verbatim from EVAL-65 / EVAL-62 (no forks).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# Pre-registered feasible floor for THIS campaign (reuses EVAL-71's floor
# verbatim on the full capture, plus a derived term-structure adequacy floor).
FLOOR: Dict[str, Any] = {
    "min_underlyings": e71.FLOOR["min_underlyings"],
    "min_distinct_expiries": MIN_DISTINCT_EXPIRIES,
    "min_expiry_trades": MIN_EXPIRY_TRADES,
    "min_bars_with_term": MIN_BARS_WITH_TERM,
    "note": (
        "EVAL-74 reuses the sealed EVAL-71 trade-tape IV floor verbatim on the "
        "full capture (NOT weakened) and additionally requires a term-structure "
        "adequacy floor (>= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with "
        ">= MIN_EXPIRY_TRADES trades each, and >= MIN_BARS_WITH_TERM bars carrying "
        "a non-null term signal). This is NOT the EVAL-64 options-surface snapshot "
        "floor, which governs the EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval74_surface_term_structure_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval74_surface_term_structure_predictiveness.py "
    "tests/test_eval74_surface_term_structure_predictiveness.py",
    "python3 -m pytest -q tests/test_eval74_surface_term_structure_predictiveness.py",
    "# no acquisition needed -- consume the already-acquired real captures:",
    "python3 scripts/eval74_surface_term_structure_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval74_surface_term_structure_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e61._finite(x, default)


def _parse_expiry(instrument: Any) -> Optional[str]:
    """``BTC-20NOV26-59000-P`` -> ``20NOV26``; ``None`` if malformed."""
    try:
        parts = str(instrument).split("-")
        if len(parts) < 4:
            return None
        expiry = parts[1].strip()
        return expiry or None
    except (IndexError, TypeError):
        return None


def _term_bars(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    signal_window_seconds: float = SIGNAL_WINDOW_SECONDS,
    atm_band: float = ATM_BAND,
    min_expiry_trades: int = MIN_EXPIRY_TRADES,
) -> List[Dict[str, Any]]:
    """Causal per-bar term-structure states on the ``bar_seconds`` grid.

    The bar grid, spot reference and ``close`` series are EVAL-71's
    (``e71.build_surface_bars``) verbatim; this only ADDS the cross-expiry
    term-structure fields (``term_slope``, ``term_ratio``) reconstructed from the
    real Deribit option trade tape over the trailing ``signal_window_seconds``
    window ending at bar end ``k``. Bars are ascending and non-overlapping.
    """
    base_bars = e71.build_surface_bars(
        capture, bar_seconds=bar_seconds, atm_band=atm_band
    )
    bar_ms = int(float(bar_seconds) * 1000)
    win_ms = int(float(signal_window_seconds) * 1000)

    trades: List[Dict[str, Any]] = []
    for t in capture.get("option_trades", []) or []:
        parsed = e71._parse_strike_type(t.get("instrument"))
        if parsed is None:
            continue
        strike, _typ = parsed
        iv = _finite(t.get("iv"), 0.0)
        ts = int(t.get("ts") or 0)
        amt = abs(_finite(t.get("amount"), 0.0))
        expiry = _parse_expiry(t.get("instrument"))
        if ts <= 0 or iv <= 0.0 or expiry is None:
            continue
        trades.append({"ts": ts, "strike": strike, "iv": iv, "amount": amt, "expiry": expiry})
    trades.sort(key=lambda t: t["ts"])
    trade_ts = [t["ts"] for t in trades]

    out: List[Dict[str, Any]] = []
    for bar in base_bars:
        bo = int(bar["bar_open_ms"])
        spot = float(bar.get("close") or 0.0)
        bar_end = bo + bar_ms
        lo = bar_end - win_ms
        i0 = bisect.bisect_left(trade_ts, lo)
        i1 = bisect.bisect_left(trade_ts, bar_end)
        window = trades[i0:i1]
        atm = [
            t for t in window
            if spot > 0.0 and abs(t["strike"] / spot - 1.0) <= atm_band
        ]
        count_by_exp: Dict[str, int] = {}
        wsum_by_exp: Dict[str, float] = {}
        asum_by_exp: Dict[str, float] = {}
        for t in atm:
            e = t["expiry"]
            count_by_exp[e] = count_by_exp.get(e, 0) + 1
            wsum_by_exp[e] = wsum_by_exp.get(e, 0.0) + t["iv"] * t["amount"]
            asum_by_exp[e] = asum_by_exp.get(e, 0.0) + t["amount"]
        mean_iv_by_exp: Dict[str, float] = {}
        for e, cnt in count_by_exp.items():
            if cnt < int(min_expiry_trades):
                continue
            amt = asum_by_exp.get(e, 0.0)
            mean_iv_by_exp[e] = (wsum_by_exp[e] / amt) if amt > 0.0 else 0.0
        exps = sorted(mean_iv_by_exp)
        term_slope: Optional[float] = None
        term_ratio: Optional[float] = None
        if len(exps) >= 2:
            near_iv = mean_iv_by_exp[exps[0]]
            far_iv = mean_iv_by_exp[exps[-1]]
            term_slope = near_iv - far_iv
            term_ratio = (near_iv / far_iv - 1.0) if far_iv > 0.0 else None
        rec = dict(bar)
        rec["term_slope"] = term_slope
        rec["term_ratio"] = term_ratio
        rec["n_atm_trades"] = len(atm)
        rec["n_term_expiries"] = len(exps)
        out.append(rec)
    return out


def _forward_rv(bars: Sequence[Dict[str, Any]], horizon_bars: int) -> List[float]:
    """Forward realized-vol series over the next ``H`` bars (EVAL-71 verbatim)."""
    return e71._forward_rv(bars, horizon_bars)


def _forward_fill(raw: Sequence[Optional[float]]) -> List[float]:
    return e71._forward_fill(raw)


def evaluate_term_predictiveness(
    capture: Dict[str, Any],
    *,
    term_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    bars = _term_bars(capture, bar_seconds=bar_seconds)
    ys_all = _forward_rv(bars, horizon_bars)
    if len(bars) < horizon_bars + 5:
        return {
            "underlying": inst, "signal": term_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient surface bars", "n_pairs": 0, "pass": False,
        }

    raw = [b.get(term_signal) for b in bars]
    sig_filled = _forward_fill(raw)
    sig_z = e61.expanding_zscore(sig_filled, ZWINDOW)

    xs: List[float] = []
    ys: List[float] = []
    for k in range(len(ys_all)):
        xs.append(float(sig_z[k]) if k < len(sig_z) else 0.0)
        ys.append(float(ys_all[k]))

    if len(xs) < 8:
        return {
            "underlying": inst, "signal": term_signal,
            "bar_seconds": float(bar_seconds), "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs", "n_pairs": len(xs), "pass": False,
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0 and len(xs) >= 20)
    n_term = int(sum(1 for b in bars if b.get("n_term_expiries", 0) >= 2))
    return {
        "underlying": inst,
        "signal": term_signal,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": len(xs),
        "n_surface_bars": len(bars),
        "n_bars_with_term": n_term,
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Per-underlying feasible floor (EVAL-71 floor on the full capture + term adequacy)
# ---------------------------------------------------------------------------
def _term_adequacy(capture: Dict[str, Any]) -> Dict[str, Any]:
    """Count distinct near-ATM expiries and bars carrying a term signal."""
    trades = capture.get("option_trades", []) or []
    count_by_exp: Dict[str, int] = {}
    for t in trades:
        parsed = e71._parse_strike_type(t.get("instrument"))
        if parsed is None:
            continue
        iv = _finite(t.get("iv"), 0.0)
        if iv <= 0.0:
            continue
        expiry = _parse_expiry(t.get("instrument"))
        if expiry is None:
            continue
        ip = _finite(t.get("index_price"), 0.0)
        strike = parsed[0]
        if ip > 0.0 and abs(strike / ip - 1.0) <= ATM_BAND:
            count_by_exp[expiry] = count_by_exp.get(expiry, 0) + 1
    distinct_expiries = sorted(
        e for e, c in count_by_exp.items() if c >= int(MIN_EXPIRY_TRADES)
    )

    bars_with_term = 0
    for bar_s in GRID_BAR_SECONDS:
        bars = _term_bars(capture, bar_seconds=bar_s)
        n = int(sum(1 for b in bars if b.get("n_term_expiries", 0) >= 2))
        bars_with_term = max(bars_with_term, n)

    checks = {
        "distinct_expiries_ok": len(distinct_expiries) >= int(MIN_DISTINCT_EXPIRIES),
        "bars_with_term_ok": bars_with_term >= int(MIN_BARS_WITH_TERM),
    }
    return {
        "n_distinct_expiries": len(distinct_expiries),
        "distinct_expiries": distinct_expiries,
        "bars_with_term_max": bars_with_term,
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


def _underlying_term_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    fl_full = e71._underlying_surface_floor(capture)  # sealed EVAL-71 floor, verbatim
    term = _term_adequacy(capture)
    ok = bool(fl_full.get("ok") and term["ok"])
    return {
        "underlying": inst,
        "eval71_floor_ok": bool(fl_full.get("ok")),
        "eval71_floor": fl_full,
        "term_adequacy": term,
        "checks": {
            "eval71_floor_ok": bool(fl_full.get("ok")),
            "distinct_expiries_ok": term["checks"]["distinct_expiries_ok"],
            "bars_with_term_ok": term["checks"]["bars_with_term_ok"],
        },
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-74",
        "title": "Options implied-volatility term structure (near-dated minus "
                 "far-dated near-ATM IV slope) -> forward realized-vol "
                 "predictiveness: a distinct-surface-signal wrapper-free rank "
                 "information coefficient falsification on the real on-disk "
                 "three-way captures",
        "extends": "EVAL-71 (identical Spearman rank-IC statistic, forward-rv "
                    "target and causal expanding-zscore) but a DIFFERENT, "
                    "distinct surface signal: the cross-expiry term-structure "
                    "SLOPE (near-minus-far ATM IV), not the near-ATM level/skew "
                    "EVAL-71 already sealed; no new acquisition",
        "supersedes": "nothing -- this is the term-structure complement to "
                      "EVAL-71's level/skew surface signal; it does not "
                      "re-litigate EVAL-71 (level/skew), EVAL-72 (straddle "
                      "monetization) or EVAL-73 (temporal stability)",
        "capture_dir": str(capture_dir),
        "term_signals": list(TERM_SIGNALS),
        "signal_window_seconds": float(SIGNAL_WINDOW_SECONDS),
        "atm_band": float(ATM_BAND),
        "min_expiry_trades": int(MIN_EXPIRY_TRADES),
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal per-bar implied-vol term structure from the real "
                  "Deribit option trade tape: near-ATM trades grouped by expiry; "
                  "term_slope = IV(near expiry) - IV(far expiry) (vol points), "
                  "term_ratio = IV(near)/IV(far) - 1; near = earliest and far = "
                  "latest expiry each with >= min_expiry_trades near-ATM trades "
                  "in the trailing window; both forward-filled then expanding-"
                  "zscored end-of-bar k (reused e61.expanding_zscore)",
        "target": "rv = sqrt(mean(log-return^2)) over the next H perp bars "
                  "(forward realized vol, strictly after the decision at k)",
        "statistic": "Spearman rank correlation IC = rho(signal_z_k, rv_forward_k); "
                     "directional permutation H1: IC>0 (a steeper/higher "
                     "near-minus-far IV slope predicts higher forward realized vol)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle realized-vol series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
        },
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and "
            "pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS) -- the "
            "term-structure slope does not add portable forward-vol predictiveness "
            "beyond EVAL-71's level/skew."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(option trades with real iv/strike/expiry + perp candles); no new "
                    "acquisition, no network; reuses EVAL-71's floor verbatim + a "
                    "term-structure adequacy floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
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


def run_eval74(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_one_capture_per_underlying(e61._capture_inventory(str(capture_dir_abs)))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_term_floor(c)

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
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_term_predictiveness(
                            cap, term_signal=sig, bar_seconds=bar_s,
                            horizon_bars=horizon,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::bar{bar_s}::"
                            f"h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}":
            _finite(r.get("permutation_p"), 1.0)
        for r in per_config
        if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = None
        if valid:
            best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9))
        pass_configs: List[str] = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::"
                f"h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::bar{best['bar_seconds']}::h{best['horizon_bars']}"
                if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS" if floor_ok
        else "EVAL_74_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal options implied-vol TERM STRUCTURE (near-minus-far ATM IV slope) "
            "and forward realized volatility on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 + term-structure "
                              "floor; no verdict"
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
            "The causal options implied-volatility TERM STRUCTURE (near-dated minus "
            "far-dated near-ATM IV slope, and its ratio) has a positive monotone "
            "(Spearman rank) relationship with subsequent forward realized "
            "volatility of the BTC/ETH perpetual (a steeper/higher near-minus-far "
            "IV slope indicates near-term vol stress and predicts higher forward "
            "realized vol), independent of any trading wrapper; tested on the "
            "already-acquired real on-disk captures at the composed EVAL-71 + "
            "term-structure floor."
        ),
        "extends": p["extends"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def _build_prereg_md(r: Dict[str, Any]) -> str:
    p = r["protocol"]
    fl = p["floor"]
    lines = [
        f"# {PREREG_ID} — options implied-vol term structure -> realized-vol "
        f"predictiveness (wrapper-free Spearman rank IC)",
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
        f"- Near-ATM band: {p['atm_band']}",
        f"- Min trades per expiry bucket: {p['min_expiry_trades']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Target: {p['target']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['stats']['zwindow']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered feasible floor (EVAL-71 floor + term-structure adequacy; NOT EVAL-64)",
        "",
        f"- {fl['note']}",
        f"- min underlyings: {fl['min_underlyings']}",
        f"- min distinct near-ATM expiries: {fl['min_distinct_expiries']}",
        f"- min trades per expiry bucket: {fl['min_expiry_trades']}",
        f"- min bars with a term signal: {fl['min_bars_with_term']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {r['report_id']} — options implied-vol term structure -> realized-vol "
        f"predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying floor (EVAL-71 floor + term-structure adequacy)",
        "",
        "| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |",
        "|---|---|---|---|---|",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        ta = fl["term_adequacy"]
        lines.append(
            f"| {inst} | {fl['eval71_floor_ok']} | {ta['n_distinct_expiries']} | "
            f"{ta['bars_with_term_max']} | {fl['ok']} |"
        )
    lines += ["", "## Per-underlying (best config by Spearman IC)", "",
              "| underlying | configs | best IC | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | "
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
        f"# {BLOCKED_ID} — options implied-vol term structure -> realized-vol "
        f"predictiveness (below the composed EVAL-71 + term-structure floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the composed EVAL-71 + term-structure adequacy "
        "floor, so no GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT "
        "use synthetic data, and do NOT emit NO-GO on under-floor data.",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-74: options implied-vol term structure -> "
                    "realized-vol predictiveness (Spearman rank IC) on the real "
                    "on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval74(
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