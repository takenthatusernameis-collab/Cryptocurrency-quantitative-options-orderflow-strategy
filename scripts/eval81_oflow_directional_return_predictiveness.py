#!/usr/bin/env python3
"""EVAL-81: does the **options order-flow imbalance predict the subsequent
DIRECTION (signed return) of the underlying?** — a distinct, runnable-**now**
predictiveness falsification on the real on-disk three-way captures.

Why this rung exists (the one on-charter signal x target cell never measured)
---------------------------------------------------------------------------
Repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is *crypto options **surface** + **options order-flow** + underlying order-flow ->
tradeable, net-of-cost alpha on REAL public data*. The runnable-now line so far
has measured these signal x target cells:

* EVAL-65 sealed ``NO-GO CONFIRMED`` — the *unconditional* **options** order-flow
  toxicity / signed-aggressor imbalance vs subsequent **realized volatility** (RV);
* EVAL-67/68/69 (forward-gated) — **options** order-flow toxicity vs RV OOS;
* EVAL-70 sealed ``NO-GO CONFIRMED`` — the **underlying (OKX perp)** order-flow
  imbalance/toxicity vs forward **RV** *and* **signed return**;
* EVAL-71/73/74/77/78/79 (predictiveness) and EVAL-72/75/76/80 (monetization) —
  the options *surface* / cross-sectional basis vs RV (and its traded forms).

EVERY options-order-flow rung (EVAL-65, EVAL-67/68/69, EVAL-78, EVAL-79) targets
**realized volatility** — an unsigned magnitude. EVAL-70 targets **signed return**
but from the **perp (underlying) tape**, not the **options tape**. The one
genuinely distinct, on-charter, runnable-**now** cell none of them covers is:

    Does the causal **options** order-flow imbalance carry monotone information
    about the subsequent **signed (directional) return** of the underlying?

That is exactly the cell that matters most for *tradeable net-of-cost alpha*: a
volatility forecast only monetizes through a vol structure (and every vol
structure so far sealed NO-GO: EVAL-72/75/76/80), whereas a **directional**
forecast monetizes directly by trading the underlying in the predicted
direction. Options order-flow is a classic informed-leverage signal (participants
buy calls / sell puts to express a directional view), so a signed-aggressor
imbalance that precedes the *direction* of the underlying is the sharpest
untested expression of the repo thesis. EVAL-81 measures exactly that on the
already-acquired real on-disk captures (surface snapshots + option trade tape
with direction + perp candles), with **no new acquisition** and **no network**.

Hypothesis / GO bar (fixed, pre-registered; NOT a weakening of any sealed floor)
--------------------------------------------------------------------------------
For each underlying (BTC, ETH), each bar grid ``{60s, 300s}`` and each forward
horizon ``H`` bars, on the causal options order-flow states (EVAL-61/62):

    sig_z_k    = causal expanding-z-scored options order-flow imbalance at bar k
                 (EVAL-62 ``build_states(tox_signal="imbalance")``)
    signed_k   = sum(log-return) over bars k+1..k+H   (strictly after decision k;
                 the forward signed log-return = subsequent direction)

Compute the Spearman rank ``IC = rho(sig_z_k, signed_k)``. **GO only if, on EACH of
BTC and ETH, at least one config** has ``IC > 0`` (buy-heavy options flow precedes
a positive forward return), directional permutation ``p < 0.05``, block-bootstrap
95% CI lower ``> 0``, at least ``MIN_USABLE_PAIRS_PER_CONFIG`` usable pairs, and
pooled BH-FDR rejects that (underlying, config); else ``NO-GO CONFIRMED (PASS)``.

Feasible floor (pre-registered for THIS campaign; NOT the EVAL-64 ladder floor)
--------------------------------------------------------------------------------
EVAL-81 consumes each underlying's causal options order-flow states (which need
the real surface snapshots for spot + straddle quotes, and the option trade tape
for signed-aggressor flow) and the real perp candles for the forward return. It
therefore composes two honestly pre-registered floors, requiring both for **each**
underlying:

* the sealed EVAL-71 surface floor (option trades / near-ATM trades / perp
  candles / span), reused verbatim (neither weakened); and
* an options order-flow adequacy floor: at least
  ``MIN_OFLOW_STATES_PER_UNDERLYING`` priceable per-bar order-flow states (real
  surface snapshots carrying a front-expiry straddle and a causal order-flow z).

None is weakened. Below the composed floor it seals
``EVAL_81_..._BLOCKED_<UTC>`` (never a NO-GO). The EVAL-64 feasible floor that
governs the EVAL-67/68/69 ladder is untouched.

This does **not** re-litigate any sealed result: EVAL-65 measured options
order-flow vs *RV*; EVAL-70 measured *perp* order-flow vs signed return;
EVAL-78/79 measured options order-flow vs RV interacted with the surface. EVAL-81
measures options order-flow vs the *signed return* of the underlying, reusing all
sealed signal reconstructions verbatim.

Seals ``EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_PREREGISTRATION_<UTC>``
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

# Reuse the sealed EVAL-61/62 measurement helpers, EVAL-65 statistics, and the
# EVAL-71 surface reconstruction verbatim (no forks, no src edits).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
import scripts.eval65_orderflow_tox_rv_predictiveness as e65  # noqa: E402
import scripts.eval71_surface_iv_rv_predictiveness as e71  # noqa: E402
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_COMBINED"
PREREG_ID = "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_PREREGISTRATION"
BLOCKED_ID = "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_BLOCKED"

# Pre-registered grid: signed-aggressor options order-flow signal x bar grid x
# forward horizons. The target is always the forward signed log-return (direction).
OFLOW_SIGNALS: Tuple[str, ...] = ("imbalance",)
GRID_BAR_SECONDS: Tuple[float, ...] = (60.0, 300.0)
FORWARD_HORIZONS_BARS: Tuple[int, ...] = (6, 24, 72)
TARGET = "signed_return"

# Statistics reused verbatim from EVAL-62/65 (identical permutation / bootstrap /
# seed) so the EVAL-81 inference is byte-for-byte the sealed line's.
PERMUTATION_PERMS = e65.PERMUTATION_PERMS
BOOTSTRAP_RESAMPLES = e65.BOOTSTRAP_RESAMPLES
BOOTSTRAP_BLOCK = e65.BOOTSTRAP_BLOCK
FDR_ALPHA = e62.FDR_ALPHA
SEED = e62.SEED
ZWINDOW = e62.ZWINDOW

# A config needs at least this many usable (signal, signed_return) pairs to be
# evaluable (a result-quality guard, not a data floor).
MIN_USABLE_PAIRS_PER_CONFIG = 120

# Composed heavy-work floor (EVAL-71 surface floor for each underlying AND an
# order-flow state floor; none weakened).
FLOOR: Dict[str, Any] = {
    "min_underlyings": 2,
    "min_oflow_states_per_underlying": 200,
    "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
    "note": (
        "EVAL-81 consumes each underlying's causal options order-flow states (surface "
        "snapshots for spot + straddle quotes, option trade tape for signed-aggressor "
        "flow) and the real perp candles for the forward signed return. It composes the "
        "sealed EVAL-71 surface floor (applied to EACH underlying, reused verbatim, "
        "neither weakened) with an options order-flow adequacy floor (>= "
        "min_oflow_states_per_underlying priceable per-bar order-flow states per "
        "underlying). This is NOT the EVAL-64 options-surface snapshot floor, which "
        "governs the EVAL-67/68/69 ladder and is untouched here."
    ),
}

CODE_PATHS: Tuple[str, ...] = (
    "src/analytics/real_walkforward_certification.py",
    "scripts/eval61_orderflow_realized_vol_net_of_cost.py",
    "scripts/eval62_orderflow_realized_vol_markpath.py",
    "scripts/eval65_orderflow_tox_rv_predictiveness.py",
    "scripts/eval71_surface_iv_rv_predictiveness.py",
    "scripts/eval81_oflow_directional_return_predictiveness.py",
)

COMMANDS: Tuple[str, ...] = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval81_oflow_directional_return_predictiveness.py "
    "tests/test_eval81_oflow_directional_return_predictiveness.py",
    "python3 -m pytest -q tests/test_eval81_oflow_directional_return_predictiveness.py",
    "# no acquisition needed — consume the already-acquired real captures:",
    "python3 scripts/eval81_oflow_directional_return_predictiveness.py "
    "--capture-dir data/raw/eval61 --no-write",
    "python3 scripts/eval81_oflow_directional_return_predictiveness.py "
    "--capture-dir data/raw/eval61 --seal --task-label "
    "EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS",
)


# ---------------------------------------------------------------------------
# Small helpers (local; no src edits)
# ---------------------------------------------------------------------------
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(x: Any, default: float = 0.0) -> float:
    return e71._finite(x, default)


# ---------------------------------------------------------------------------
# Per-underlying predictiveness (options order-flow imbalance -> forward signed
# return). Mirrors EVAL-65's causal-state alignment verbatim, changing only the
# target from RV to the forward signed log-return (direction).
# ---------------------------------------------------------------------------
def evaluate_predictiveness(
    capture: Dict[str, Any],
    *,
    oflow_signal: str,
    bar_seconds: float,
    horizon_bars: int,
) -> Dict[str, Any]:
    inst = capture.get("underlying", "UNKNOWN")
    states = e62.build_states(capture, tox_signal=oflow_signal, bar_seconds=bar_seconds)
    pts = [
        (float(s["spot"]), float(s.get("signal_z", 0.0)))
        for s in states
        if float(s.get("spot", 0.0)) > 0.0
    ]
    if len(pts) < horizon_bars + 5:
        return {
            "underlying": inst,
            "signal": oflow_signal,
            "target": TARGET,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient priced states",
            "n_pairs": 0,
            "pass": False,
        }
    spot = [p[0] for p in pts]
    sigz = [p[1] for p in pts]
    lr = [math.log(spot[i + 1] / spot[i]) for i in range(len(spot) - 1)]

    xs: List[float] = []
    ys: List[float] = []
    for k in range(0, len(lr) - horizon_bars + 1):
        seg = lr[k:k + horizon_bars]
        signed = sum(seg)  # forward signed log-return over bars k+1..k+H (direction)
        xs.append(sigz[k])
        ys.append(signed)

    if len(xs) < int(MIN_USABLE_PAIRS_PER_CONFIG):
        return {
            "underlying": inst,
            "signal": oflow_signal,
            "target": TARGET,
            "bar_seconds": float(bar_seconds),
            "horizon_bars": int(horizon_bars),
            "error": "insufficient aligned pairs",
            "n_pairs": len(xs),
            "pass": False,
        }

    ic, perm_p = e65._perm_p_ic(xs, ys, PERMUTATION_PERMS, SEED)
    med, ci_lo, ci_hi = e65._boot_ci_ic(xs, ys, BOOTSTRAP_RESAMPLES, BOOTSTRAP_BLOCK, SEED)
    passed = bool(
        ic > 0.0
        and perm_p < 0.05
        and ci_lo > 0.0
        and len(xs) >= int(MIN_USABLE_PAIRS_PER_CONFIG)
    )
    return {
        "underlying": inst,
        "signal": oflow_signal,
        "target": TARGET,
        "bar_seconds": float(bar_seconds),
        "horizon_bars": int(horizon_bars),
        "n_pairs": len(xs),
        "n_states": len(states),
        "spearman_ic": ic,
        "permutation_p": perm_p,
        "bootstrap_ci": [med, ci_lo, ci_hi],
        "nonzero_signal_pairs": int(sum(1 for v in xs if abs(v) > 1e-9)),
        "pass": passed,
    }


# ---------------------------------------------------------------------------
# Composed heavy-work floor (EVAL-71 surface floor AND order-flow state floor)
# ---------------------------------------------------------------------------
def _underlying_floor(capture: Dict[str, Any], *, inst: str) -> Dict[str, Any]:
    """Composed per-underlying floor: EVAL-71 surface floor AND order-flow
    states (max over the two bar grids)."""
    surface = e71._underlying_surface_floor(capture)

    n_oflow_states = 0
    for bar_s in GRID_BAR_SECONDS:
        states = e62.build_states(capture, tox_signal="imbalance", bar_seconds=bar_s)
        n_oflow_states = max(n_oflow_states, len(states))
    oflow_ok = n_oflow_states >= int(FLOOR["min_oflow_states_per_underlying"])

    return {
        "underlying": inst,
        "surface_floor_ok": bool(surface.get("ok")),
        "surface_floor": surface,
        "n_oflow_states": n_oflow_states,
        "oflow_ok": oflow_ok,
        "checks": {
            "surface_floor_ok": bool(surface.get("ok")),
            "oflow_ok": oflow_ok,
        },
        "ok": bool(surface.get("ok") and oflow_ok),
    }


def campaign_floor(captures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    insts = sorted(captures)
    per_underlying = {
        i: _underlying_floor(captures[i], inst=i) for i in insts
    }
    ok = bool(
        len(insts) >= int(FLOOR["min_underlyings"])
        and per_underlying
        and all(v["ok"] for v in per_underlying.values())
    )
    return {
        "underlyings": insts,
        "per_underlying": per_underlying,
        "checks": {
            "all_underlyings_ok": ok,
        },
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-81",
        "title": "Options order-flow imbalance -> subsequent signed (directional) "
                 "return: wrapper-free rank information coefficient "
                 "(predictiveness) falsification on the real on-disk three-way "
                 "captures",
        "extends": "EVAL-65 (unconditional options order-flow -> RV) and EVAL-70 "
                   "(perp order-flow -> RV / signed return): the same Spearman "
                   "rank-IC statistic and all sealed signal reconstructions reused "
                   "verbatim, but a distinct, on-charter signal x target cell — the "
                   "*options* order-flow imbalance vs the *signed return* of the "
                   "underlying; no new acquisition",
        "supersedes": "nothing — this is the options-order-flow -> direction "
                      "complement to EVAL-65/67/68/69/78/79 (options flow -> RV) "
                      "and EVAL-70 (perp flow -> signed return); none measured "
                      "options flow vs the underlying's signed return",
        "capture_dir": str(capture_dir),
        "oflow_signals": list(OFLOW_SIGNALS),
        "target": TARGET,
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "forward_horizons_bars": list(FORWARD_HORIZONS_BARS),
        "signal": "causal options order-flow imbalance z (EVAL-61/62 build_states, "
                  "expanding-z-scored, end-of-bar k)",
        "target_detail": "signed = sum(log-return) over the next H perp bars "
                         "(strictly after the decision at bar k); the subsequent "
                         "direction of the underlying",
        "statistic": "Spearman rank correlation IC = rho(sig_z_k, signed_k) over the "
                     "causal order-flow states (H1: IC > 0, buy-heavy options flow "
                     "precedes a positive forward return)",
        "stats": {
            "permutation_perms": PERMUTATION_PERMS,
            "permutation": "directional (H1: IC>0), shuffle the signed-return series",
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "fdr_alpha": FDR_ALPHA,
            "seed": SEED,
            "zwindow": ZWINDOW,
            "min_usable_pairs_per_config": int(MIN_USABLE_PAIRS_PER_CONFIG),
        },
        "go_bar": (
            "GO only if, on EACH of BTC and ETH, at least one config (bar grid x "
            "horizon) has Spearman IC > 0, directional permutation p < 0.05, "
            "block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config "
            "usable pairs, and pooled BH-FDR rejects that (underlying, config); else "
            "NO-GO CONFIRMED (PASS)."
        ),
        "data_availability": {
            "note": "uses the already-acquired real on-disk three-way captures "
                    "(surface snapshots + option trade tape with direction + perp "
                    "candles); no new acquisition, no network; composes the EVAL-71 "
                    "surface floor for each underlying with an order-flow state floor",
            "capture_dir": str(capture_dir),
        },
        "floor": dict(FLOOR),
        "code_paths": list(CODE_PATHS),
        "commands": list(COMMANDS),
    }


def run_eval81(
    *,
    capture_dir: str = "data/raw/eval61",
    write: bool = True,
    task_label: str = "EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS",
) -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    selected = e61._capture_inventory(str(capture_dir_abs))
    captures: Dict[str, Dict[str, Any]] = {}
    for cap in selected:
        inst = str(cap.get("underlying"))
        if inst and inst not in captures:
            captures[inst] = cap

    floor = campaign_floor(captures)
    floor_ok = bool(floor["ok"])

    per_config: List[Dict[str, Any]] = []
    errors: List[str] = []
    for inst in sorted(captures):
        cap = captures[inst]
        for sig in OFLOW_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                for horizon in FORWARD_HORIZONS_BARS:
                    try:
                        res = evaluate_predictiveness(
                            cap,
                            oflow_signal=sig,
                            bar_seconds=bar_s,
                            horizon_bars=horizon,
                        )
                    except BaseException as exc:  # noqa: BLE001
                        errors.append(
                            f"{inst}::{sig}::{TARGET}::bar{bar_s}::h{horizon}: {exc!r}"
                        )
                        continue
                    per_config.append(res)

    p_values = {
        f"{r['underlying']}::{r['signal']}::{r['target']}::bar{r['bar_seconds']}::"
        f"h{r['horizon_bars']}": _finite(r.get("permutation_p"), 1.0)
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
        pass_configs = []
        for r in valid:
            key = (
                f"{r['underlying']}::{r['signal']}::{r['target']}::"
                f"bar{r['bar_seconds']}::h{r['horizon_bars']}"
            )
            if r.get("pass") and key in rejected:
                pass_configs.append(key)
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_ic": _finite(best.get("spearman_ic"), 0.0) if best else 0.0,
            "best_config": (
                f"{best['signal']}::{best['target']}::bar{best['bar_seconds']}::"
                f"h{best['horizon_bars']}" if best else "n/a"
            ),
            "n_pass": len(pass_configs),
            "pass_configs": pass_configs,
            "any_pass": bool(pass_configs),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    go = bool(floor_ok and all_pass and len(rejected) >= 1)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = (
        "EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS" if floor_ok
        else "EVAL_81_BLOCKED_FLOOR"
    )

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "wrapper-free information-content test: Spearman rank IC between the "
            "causal options order-flow imbalance and the forward signed (directional) "
            "return of the underlying on the real on-disk captures"
            if floor_ok else "capture below the composed EVAL-71 + order-flow floor; "
                             "no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(captures),
        "floor": dict(FLOOR),
        "campaign_floor": floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "bh_fdr": bh,
            "any_config_pass": all_pass,
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
            "The causal options order-flow signed-aggressor imbalance (EVAL-61/62 "
            "build_states, expanding-z-scored) has a positive monotone (Spearman "
            "rank) relationship with the subsequent signed log-return (direction) of "
            "the underlying, reconstructed from the real Deribit option trade tape and "
            "real perp candles. Tested on the already-acquired real on-disk captures "
            "at the composed EVAL-71 + order-flow floor."
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
        f"# {PREREG_ID} — options order-flow imbalance -> subsequent signed "
        f"(directional) return predictiveness (wrapper-free Spearman rank IC)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Hypothesis: {r['hypothesis']}",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Extends: {p['extends']}",
        "",
        "## Pre-declared protocol",
        "",
        f"- Order-flow signals: {p['oflow_signals']}",
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
        "## Pre-registered composed floor (EVAL-71 surface + order-flow state)",
        "",
        f"- {fl['note']}",
        f"- Min underlyings: {fl['min_underlyings']}",
        f"- Min order-flow states per underlying: {fl['min_oflow_states_per_underlying']}",
        f"- Min usable pairs per config: {fl['min_usable_pairs_per_config']}",
        "",
    ]
    return "\n".join(lines) + "\n"


def _build_md(r: Dict[str, Any]) -> str:
    fl = r["campaign_floor"]
    lines = [
        f"# {r['report_id']} — options order-flow imbalance -> subsequent signed "
        f"(directional) return predictiveness (wrapper-free rank IC) falsification",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        f"- Verdict: **{r['verdict']}**",
        f"- Floor OK: {r['floor_ok']} (underlyings {', '.join(r['underlyings'])})",
        "",
        "## Per-underlying composed floor",
        "",
        "| underlying | surface floor ok | n option trades | n oflow states | oflow ok | ok |",
        "|---|---|---|---|---|---|",
    ]
    for inst, u in fl["per_underlying"].items():
        s = u["surface_floor"]
        lines.append(
            f"| {inst} | {u['surface_floor_ok']} | {s.get('n_option_trades')} | "
            f"{u.get('n_oflow_states')} | {u.get('oflow_ok')} | {u['ok']} |"
        )
    lines += ["", "## Configs (best first by Spearman IC)", ""]
    lines += ["| underlying | signal | target | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    rows = sorted(
        [c for c in r["per_config"] if c.get("n_pairs", 0) > 0],
        key=lambda c: _finite(c.get("spearman_ic"), -1e9),
        reverse=True,
    )
    for c in rows:
        ci = c.get("bootstrap_ci") or [0.0, 0.0, 0.0]
        lines.append(
            f"| {c['underlying']} | {c['signal']} | {c['target']} | "
            f"{c['bar_seconds']:.0f} | {c['horizon_bars']} | {c['n_pairs']} | "
            f"{c['spearman_ic']:.4f} | {c['permutation_p']:.4f} | "
            f"[{ci[0]:.4f}, {ci[1]:.4f}, {ci[2]:.4f}] | {c['pass']} |"
        )
    lines += ["", "## Per-underlying", ""]
    lines += ["| underlying | n_configs | best IC | best config | n_pass | any_pass |",
              "|---|---|---|---|---|---|"]
    for s in r["per_underlying"]:
        lines.append(
            f"| {s['underlying']} | {s['n_configs']} | {s['best_ic']:.4f} | "
            f"{s['best_config']} | {s['n_pass']} | {s['any_pass']} |"
        )
    lines += ["", "## Pooled", "",
              f"- BH-FDR rejected: {r['pooled']['bh_fdr'].get('rejected')}",
              f"- Any config pass (all underlyings): {r['pooled']['any_config_pass']}",
              f"- Campaign state: {r['pooled']['campaign_state']}"]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r.get("generated_at", _utc_now_iso()),
        "task": r.get("task", "EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS"),
        "verdict": "BLOCKED",
        "verdict_detail": (
            "capture below the composed EVAL-71 surface + order-flow floor; no "
            "predictiveness verdict is emitted (never a NO-GO)"
        ),
        "floor_ok": False,
        "capture_dir": r.get("capture_dir"),
        "underlyings": r.get("underlyings", []),
        "floor": r.get("floor", dict(FLOOR)),
        "campaign_floor": r.get("campaign_floor", {}),
        "errors": r.get("errors", []),
    }


def _build_blocked_md(r: Dict[str, Any]) -> str:
    fl = r.get("campaign_floor") or {}
    lines = [
        f"# {BLOCKED_ID} — options order-flow imbalance -> subsequent signed "
        f"return predictiveness: BELOW FLOOR",
        "",
        f"- Generated: `{r.get('generated_at')}`",
        f"- Task: `{r.get('task')}`",
        f"- Verdict: **BLOCKED**",
        f"- Capture dir: `{r.get('capture_dir')}`",
        f"- Underlyings: {', '.join(r.get('underlyings', [])) or '(none)'}",
        "",
        "The capture is below the composed EVAL-71 surface + order-flow floor; no "
        "predictiveness verdict is emitted (never a NO-GO).",
    ]
    per = fl.get("per_underlying") or {}
    if per:
        lines += ["", "## Per-underlying floor", "",
                  "| underlying | surface floor ok | n oflow states | oflow ok | ok |",
                  "|---|---|---|---|---|"]
        for inst, u in per.items():
            lines.append(
                f"| {inst} | {u.get('surface_floor_ok')} | {u.get('n_oflow_states')} | "
                f"{u.get('oflow_ok')} | {u.get('ok')} |"
            )
    if r.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in r["errors"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-81: wrapper-free options order-flow imbalance -> "
                    "subsequent signed (directional) return predictiveness "
                    "(Spearman rank IC) on the real on-disk captures"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval61")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval81(
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
                "floor": dict(FLOOR),
                "campaign_floor": {},
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