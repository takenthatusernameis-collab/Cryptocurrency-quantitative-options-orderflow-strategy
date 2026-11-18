#!/usr/bin/env python3
"""EVAL-87: does the causal **near-ATM implied vol level** carry monotone
information about the subsequent **forward return tail asymmetry** of the same
underlying? A distinct predictiveness falsification that is runnable **now** on
the real on-disk three-way captures.

Why this rung exists (anti-avoidance priority cell 2)
-----------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line
EVAL-70..86 is sealed:

* EVAL-71 sealed ``GO CONFIRMED`` — own-asset surface (near-ATM IV level /
  put-call skew) predicts the *same* underlying's forward *RV level*; EVAL-73
  confirmed OOS stability.
* EVAL-85 sealed ``GO CONFIRMED`` — put-call skew (surface) predicts the *same*
  underlying's forward return *tail asymmetry*.
* EVAL-86 sealed ``GO CONFIRMED`` — put-call skew (surface) predicts the *same*
  underlying's forward *volatility risk premium* (VRP).
* Every traded-form monetization cell (straddle EVAL-72/75, risk reversal EVAL-76,
  butterfly EVAL-82, relative-value spread EVAL-80) sealed NO-GO.
* EVAL-81 (order-flow -> forward signed return mean), EVAL-70/78/79 (order-flow
  predictiveness), EVAL-74/82/80/75/72/76 all sealed NO-GO/BLOCKED.

None of them covers an **atm_iv -> forward return tail asymmetry** cell: does
the causal near-ATM implied vol level (a surface signal, not order-flow) predict
how asymmetric the subsequent forward return distribution's tails are — distinct
from EVAL-85's put-call skew -> forward return *tail asymmetry* (different
signal) and from EVAL-71's atm_iv+skew -> forward *RV level* (different signal
set + target). Not a monetization/traded-form claim — only a predictiveness
falsification — so it does not re-litigate EVAL-72/75/76/80/82.

EVAL-87 asks the genuinely distinct, on-charter, runnable-**now** question:

    Does the causal near-ATM implied vol at bar k carry monotone information
    about the subsequent forward return tail asymmetry of the SAME underlying
    over bars k+1..k+H — i.e. does elevated atm_iv precede more lopsided
    forward return tails?

This is **not** EVAL-71 (atm_iv+skew -> forward RV *level*), **not** EVAL-85
(skew -> forward return *tail asymmetry*), **not** EVAL-86 (skew -> forward
*VRP*), and **not** any sealed traded-form cell. It is runnable **today** on the
already-acquired real on-disk captures (option trade tape with IV + perp candles
for both underlyings), with **no new acquisition** and **no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), the causal near-ATM implied vol signal ``atm_iv``
(expanding-z-scored end-of-bar k, EVAL-71 ``build_surface_bars`` +
EVAL-61 ``expanding_zscore``, reused verbatim), each bar grid ``{60s, 300s}``
and each forward horizon ``H`` bars:

    x_k     = causal expanding-z-scored near-ATM IV z at bar k
    y_k     = forward return tail asymmetry over bars k+1..k+H:
              let r_i = log(close_i / close_{i-1}) for the forward window and
              y_k = (q95(r) - median(r)) - (median(r) - q05(r)) — upper-tail spread
              minus lower-tail spread, i.e. forward return skewness/tail asymmetry
              (nearest-rank quantiles, degenerate -> 0).

Compute Spearman rank ``IC = rho(x_k, y_k)`` with the sealed EVAL-65 directional
permutation and block bootstrap (H1: ``IC > 0`` — elevated atm_iv precedes more
asymmetric forward return tails). A config **passes** only if ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and
at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs.

**GO only if, on BOTH BTC and ETH and at least one config:** ``IC > 0``,
directional permutation ``p < 0.05``, block-bootstrap 95% CI lower ``> 0``, and
pooled BH-FDR rejects that config; else ``NO-GO CONFIRMED (PASS)`` (near-ATM IV
does not portably predict forward return tail asymmetry).

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-87 consumes the same trade-tape IV data as EVAL-71, so it reuses the sealed
EVAL-71 trade-tape/surface floor verbatim on the full capture (option trades /
near-ATM trades / perp candles / span) for each underlying. Below the floor it
seals ``EVAL_87_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor
that governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-71 measured atm_iv+skew ->
forward RV *level*; EVAL-85 measured skew -> forward return *tail asymmetry*;
EVAL-86 measured skew -> forward *VRP*; EVAL-87 measures atm_iv -> forward return
*tail asymmetry*, reusing all sealed signal reconstructions and the sealed
EVAL-65 inference verbatim.

Seals ``EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_PREREGISTRATION_<UTC>``
then ``..._COMBINED_<UTC>`` (or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
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

# Reuse the sealed EVAL-61/62/65/71 primitives verbatim (no forks, no src).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_COMBINED"
PREREG_ID = "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_PREREGISTRATION"
BLOCKED_ID = "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_BLOCKED"

# Pre-registered grid: surface signal x bar grid x forward horizons. The target is
# the SAME underlying's forward return tail asymmetry (a new signal x target cell).
SURFACE_SIGNALS: Tuple[str, ...] = ("atm_iv",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "forward_return_tail_asymmetry"

# Map a surface signal name to its per-bar z-series key.
SIGNAL_Z_KEY: Dict[str, str] = {"atm_iv": "atm_iv_z"}

# Trailing window / near-ATM band reused verbatim from the sealed EVAL-71 surface.
SIGNAL_WINDOW_SECONDS: float = e71.SIGNAL_WINDOW_SECONDS
ATM_BAND: float = e71.ATM_BAND

# Statistics reused verbatim from EVAL-65 (identical permutation / bootstrap / seed).
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

MIN_USABLE_PAIRS_PER_CONFIG = 100

# Composed heavy-work floor (EVAL-71 surface floor for each underlying; not the
# EVAL-64 ladder floor; not weakened).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-87 consumes each underlying's causal options-surface series (real "
        "option trade tape for the IV surface, real perp candles for forward "
        "returns) and reuses the sealed EVAL-71 surface floor for EACH underlying "
        "(verbatim, neither weakened). Below the composed floor the campaign seals "
        "BLOCKED, never NO-GO. This is NOT the EVAL-64 options-surface snapshot "
        "floor, which governs the EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval87_surface_atm_iv_forward_tail_asymmetry.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval87_surface_atm_iv_forward_tail_asymmetry.py "
    "tests/test_eval87_surface_atm_iv_forward_tail_asymmetry.py",
    "python3 -m pytest -q tests/test_eval87_surface_atm_iv_forward_tail_asymmetry.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval87_surface_atm_iv_forward_tail_asymmetry.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval87_surface_atm_iv_forward_tail_asymmetry.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY",
)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


def _nearest_rank_quantile(sorted_vals: Sequence[float], p: float) -> float:
    """Nearest-rank quantile (1-indexed rank ceil(p/100 * n), clamped). Pure
    Python, deterministic, well-defined for small forward windows."""
    s = list(sorted_vals)
    n = len(s)
    if n == 0:
        return 0.0
    idx = int(math.ceil(p / 100.0 * n)) - 1
    idx = max(0, min(n - 1, idx))
    return float(s[idx])


# ---------------------------------------------------------------------------
# Forward return tail-asymmetry target (distinct from EVAL-71 forward RV level
# and EVAL-81 forward signed return mean): same target as EVAL-85 but driven by
# the near-ATM IV level signal instead of put-call skew.
# ---------------------------------------------------------------------------
def _forward_return_tail_asym(
    bars: Sequence[Dict[str, Any]], horizon_bars: int
) -> List[Optional[float]]:
    """Forward return tail asymmetry over the next ``H`` bars.

    For decision bar ``k`` (target strictly after k) uses log returns
    ``r_i = log(close_i / close_{i-1})`` over bars ``k+1..k+H``. Returns
    ``(q95(r) - median(r)) - (median(r) - q05(r))`` — the upper-tail spread minus
    the lower-tail spread, i.e. forward return skewness / tail asymmetry.

    Strictly distinct from EVAL-71 forward RV ``sqrt(mean(r^2))`` (level) and from
    EVAL-81 forward signed return *mean* (direction). Returns a list indexed by
    bar ``k`` of length ``len(bars)``; incomplete tail entries are ``None``.
    """
    closes = [float(b["close"]) for b in bars]
    lr = [math.log(closes[i + 1] / closes[i]) for i in range(len(closes) - 1)] if len(closes) >= 2 else []
    h = int(horizon_bars)
    out: List[Optional[float]] = []
    for k in range(0, len(lr) - h + 1):
        seg = lr[k:k + h]
        s = sorted(seg)
        med = _nearest_rank_quantile(s, 50.0)
        q95 = _nearest_rank_quantile(s, 95.0)
        q05 = _nearest_rank_quantile(s, 5.0)
        out.append((q95 - med) - (med - q05))
    return out


# ---------------------------------------------------------------------------
# Per-asset causal surface z-series + forward return tail asymmetry
# ---------------------------------------------------------------------------
def _asset_surface_series(
    capture: Dict[str, Any],
    *,
    bar_seconds: float,
    horizon_bars: int,
    signal_window_seconds: float = SIGNAL_WINDOW_SECONDS,
    atm_band: float = ATM_BAND,
) -> Dict[int, Dict[str, Any]]:
    """Causal per-bar surface signal z-series and forward return tail asymmetry
    for one asset.

    Returns ``{bar_open_ms: {"atm_iv_z", "atm_iv", "fwd_tail_asym"}}`` where:

    * ``atm_iv_z`` is the causal near-ATM IV surface signal forward-filled then
      expanding-z-scored (EVAL-61 ``expanding_zscore``), reusing EVAL-71
      ``build_surface_bars`` verbatim;
    * ``atm_iv`` is the near-ATM implied vol at bar k (forward-filled);
    * ``fwd_tail_asym`` is the forward return tail asymmetry over the *next* H
      perp bars (strictly after the decision at bar k).
    """
    bars = e71.build_surface_bars(
        capture,
        bar_seconds=bar_seconds,
        signal_window_seconds=signal_window_seconds,
        atm_band=atm_band,
    )
    fwd = _forward_return_tail_asym(bars, horizon_bars)

    atm_iv_filled = e71._forward_fill([b.get("atm_iv") for b in bars])
    atm_iv_z = e61.expanding_zscore(atm_iv_filled, ZWINDOW)

    out: Dict[int, Dict[str, Any]] = {}
    n_fwd = len(fwd)
    for k, b in enumerate(bars):
        out[int(b["bar_open_ms"])] = {
            "atm_iv_z": float(atm_iv_z[k]) if k < len(atm_iv_z) else 0.0,
            "atm_iv": float(atm_iv_filled[k]) if k < len(atm_iv_filled) else 0.0,
            "fwd_tail_asym": float(fwd[k]) if k < n_fwd else None,
        }
    return out


# ---------------------------------------------------------------------------
# Per-(underlying, signal, grid, horizon) predictiveness
# ---------------------------------------------------------------------------
def evaluate_config(
    capture: Dict[str, Any],
    *,
    surface_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    """Own-asset: near-ATM IV z at bar k -> forward return tail asymmetry over
    bars k+1..k+H."""
    underlying = str(capture.get("underlying", "UNDERLYING"))
    zkey = SIGNAL_Z_KEY[surface_signal]

    series = _asset_surface_series(
        capture, bar_seconds=bar_seconds, horizon_bars=horizon_bars
    )

    xs: List[float] = []
    ys: List[float] = []
    for t in sorted(series):
        y = series[t].get("fwd_tail_asym")
        if y is None:
            continue
        xs.append(float(series[t].get(zkey, 0.0)))
        ys.append(float(y))

    n_pairs = len(xs)
    base = {
        "underlying": underlying,
        "signal": surface_signal,
        "target": TARGET,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": n_pairs,
    }
    if n_pairs < int(MIN_USABLE_PAIRS_PER_CONFIG):
        base.update({
            "spearman_ic": float("nan"),
            "permutation_p": 1.0,
            "bootstrap_ci": [float("nan"), float("nan"), float("nan")],
            "pass": False,
            "reason": "insufficient_pairs",
        })
        return base

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(ic > 0.0 and perm_p < 0.05 and ci_lo > 0.0)
    base.update({
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_median": med,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "pass": passed,
        "reason": "ok" if passed else "gate_fail",
    })
    return base


# ---------------------------------------------------------------------------
# Floor composition (reuse EVAL-71 surface floor verbatim)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any]) -> Dict[str, Any]:
    return e71._underlying_surface_floor(capture)


def _campaign_floor(per_underlying: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    n_ok = sum(1 for v in per_underlying.values() if v.get("ok"))
    checks = {
        "underlyings_ok": n_ok >= int(FLOOR["min_underlyings"]),
        "all_underlyings_ok": bool(per_underlying) and all(v.get("ok") for v in per_underlying.values()),
    }
    return {"checks": checks, "ok": bool(all(checks.values()))}


# ---------------------------------------------------------------------------
# Report / sealing
# ---------------------------------------------------------------------------
def _select_captures(capture_dir: str) -> List[Dict[str, Any]]:
    all_caps = e61._capture_inventory(capture_dir)
    best: Dict[str, Dict[str, Any]] = {}
    for c in all_caps:
        inst = c.get("underlying", "UNKNOWN")
        score = len(c.get("option_trades", []) or [])
        prev = best.get(inst)
        if prev is None or score > len(prev.get("option_trades", []) or []):
            best[inst] = c
    order = [k for k in ("BTC", "ETH") if k in best] + [k for k in sorted(best) if k not in ("BTC", "ETH")]
    return [best[k] for k in order]


def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-87",
        "title": "Causal near-ATM implied vol -> subsequent forward return tail "
                 "asymmetry (Spearman rank IC) predictiveness on the real on-disk "
                 "captures",
        "extends": "EVAL-71 (own-asset surface atm_iv+skew -> own forward RV "
                   "level) and EVAL-85 (skew -> forward return tail asymmetry): "
                   "same Spearman rank-IC statistic and sealed signal "
                   "reconstructions reused verbatim, but a distinct on-charter "
                   "signal x target cell — near-ATM IV level (surface) -> forward "
                   "return *tail asymmetry*; no new acquisition",
        "supersedes": "nothing — complements EVAL-71/81/85/86; does not re-litigate "
                      "them and makes no traded-form claim",
        "capture_dir": str(capture_dir),
        "surface_signals": list(SURFACE_SIGNALS),
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal near-ATM implied vol z (EVAL-71 build_surface_bars + "
                  "EVAL-61 expanding_zscore, end-of-bar k)",
        "target_detail": "forward return tail asymmetry = (q95 - median) - "
                         "(median - q05) over the SAME underlying's next H perp "
                         "log returns (strictly after the decision at bar k)",
        "statistic": "Spearman rank correlation IC = rho(atm_iv_z_k, "
                     "forward_tail_asym_k); directional permutation H1: IC > 0",
        "go_bar": (
            "GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, "
            "directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and "
            "pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS)."
        ),
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle target series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "data_availability": {
            "note": "uses already-acquired real on-disk three-way captures (option "
                    "trades + perp candles); no new acquisition, no network",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval87(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = _select_captures(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor(c)

    campaign_floor = _campaign_floor(per_underlying_floor)
    floor_ok = bool(campaign_floor.get("ok"))

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for cap in captures:
        for sig in SURFACE_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_config(
                            cap,
                            surface_signal=sig,
                            bar_seconds=bar_s,
                            horizon_bars=horizon,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{cap.get('underlying')}::{sig}::bar{bar_s}::h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
        for r in per_config if r.get("n_pairs", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=FDR_ALPHA) if p_values else {"rejected": []}
    rejected = set(bh.get("rejected") or [])

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r.get("underlying", "?"), []).append(r)

    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        valid = [r for r in rows if r.get("n_pairs", 0) > 0]
        best = max(valid, key=lambda r: _finite(r.get("spearman_ic"), -1e9)) if valid else None
        pass_configs: List[str] = []
        for r in valid:
            key = f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}::h{r['horizon_bars']}"
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
        "EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY" if floor_ok
        else "EVAL_87_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free Spearman rank IC between causal near-ATM implied vol and "
            "forward return tail asymmetry on real captures"
            if floor_ok else "capture below the composed EVAL-71 surface floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": dict(FLOOR),
        "per_underlying_floor": per_underlying_floor,
        "campaign_floor": campaign_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {"bh_fdr": bh, "all_underlyings_pass": all_pass, "campaign_state": campaign_state},
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
            "The causal near-ATM implied vol (EVAL-71 near-ATM IV, "
            "expanding-z-scored) has a positive monotone (Spearman rank) relationship "
            "with the subsequent forward return tail asymmetry of the SAME underlying "
            "(upper-tail spread minus lower-tail spread over the next H perp log "
            "returns), reconstructed from the real Deribit option trade tape and real "
            "perp candles, tested on the already-acquired real on-disk captures at the "
            "composed EVAL-71 surface floor."
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
        f"# {PREREG_ID} — causal near-ATM implied vol -> forward return tail asymmetry "
        f"predictiveness (Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Surface signals: {p['surface_signals']}",
        f"- Target: {p['target']} — {p['target_detail']}",
        f"- Bar grid (s): {p['bar_seconds_grid']}",
        f"- Forward horizons (bars): {p['forward_horizons_bars']}",
        f"- Signal: {p['signal']}",
        f"- Statistic: {p['statistic']}",
        f"- Stats: perm {p['stats']['permutation_perms']} ({p['stats']['permutation']}) / "
        f"bootstrap {p['stats']['bootstrap_resamples']} block {p['stats']['bootstrap_block']} / "
        f"BH-FDR alpha {p['stats']['fdr_alpha']} / seed {p['stats']['seed']} / "
        f"zwindow {p['stats']['zwindow']} / "
        f"min usable pairs {p['stats']['min_usable_pairs_per_config']}",
        "",
        "## Pre-declared GO bar",
        "",
        p["go_bar"],
        "",
        "## Pre-registered composed floor (EVAL-71 surface, not the EVAL-64 ladder floor)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — causal near-ATM implied vol -> forward return tail "
        f"asymmetry predictiveness (Spearman rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Verdict detail: {r['verdict_detail']}",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying surface floor (EVAL-71, reused verbatim)",
        "",
        "| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl.get("per_underlying", {}).items():
        lines.append(
            f"| {inst} | {u.get('n_option_trades')} | {u.get('n_near_atm_option_trades')} | "
            f"{u.get('n_perp_candles')} | {u.get('perp_span_seconds')} | {u.get('ok')} |"
        )
    lines += ["", "## Per-underlying (best config by Spearman IC)", "",
              "| underlying | configs | best IC | best config | n pass | any pass |",
              "|---|---|---|---|---|---|"]
    for s in r.get("per_underlying", []):
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r.get('pooled', {}).get('bh_fdr', {}).get('rejected')}",
              f"- All underlyings pass: {r.get('pooled', {}).get('all_underlyings_pass')}",
              f"- Campaign state: {r.get('pooled', {}).get('campaign_state')}"]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task", "EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY"),
        "verdict": "BLOCKED",
        "verdict_detail": "capture below the composed EVAL-71 surface floor; no verdict (never a NO-GO)",
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "per_underlying_floor": r.get("per_underlying_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — near-ATM implied vol -> forward return tail asymmetry: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        "",
        "The capture is below the composed EVAL-71 surface floor; no predictiveness "
        "verdict is emitted (never a NO-GO).",
    ]
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-87: causal near-ATM implied vol -> forward return tail "
                    "asymmetry predictiveness (Spearman rank IC)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval87(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": _utc_now_iso(), "task": args.task_label,
                "capture_dir": args.capture_dir, "underlyings": [],
                "floor": dict(FLOOR), "per_underlying_floor": {}, "errors": [repr(exc)],
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
