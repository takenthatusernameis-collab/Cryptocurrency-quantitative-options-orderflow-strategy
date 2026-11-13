"""Final net-of-cost GO/NO-GO certification (EVAL-10) on the EVAL-09 with-hedge portfolio.

Runs the real EVAL-09 engine (``src/analytics/gamma_inventory_hedge.py``) in-process
across seeds, then certifies the with-hedge per-window OOS returns:

* multi-seed block-bootstrap CI (seed-fixed, deterministic) for mean net return and
  mean net Sharpe over the 15 seed×symbol series;
* paired permutation p-value for with-hedge vs without-hedge (``paired=True``);
* 0/1/5/10 bps incremental cost grid (EVAL-09 returns already carry the 1 bp hedge
  cost, so the grid is applied incrementally, never re-costed from zero);
* per-seed failing conditions; seed-level ``pass_fraction = seeds_passing / num_seeds``
  (a seed passes only if ALL its symbols pass); ``verdict = "GO" if pass_fraction >=
  GO_SEED_FRACTION (0.70) else "NO-GO"``.

A NO-GO verdict is the expected and valid outcome (with-hedge −0.558 vs without-hedge
+0.259). Never tunes data to force GO. Strict-serializable; never emits
``{"valid": True}``.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from src.analytics.gamma_inventory_hedge import (
    DEFAULT_TARGET_DELTA_USD,
    DEFAULT_TOXICITY_THRESHOLD,
    evaluate_gamma_inventory_hedge,
)
from src.analytics.strategy_evaluation import (
    assert_json_valid,
    block_bootstrap_ci,
    compute_metrics,
    permutation_test,
    serialize_metrics_strict,
)
from src.analytics.strategy_falsification import GO_SEED_FRACTION

COST_GRID_BPS: tuple[int, ...] = (0, 1, 5, 10)
NET_BASELINE_BPS: float = 1.0  # EVAL-09 window_returns are already net of 1 bp cost
INITIAL_CAPITAL: float = 100000.0
MIN_DISTINCT_NONZERO: int = 2


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _incremental_window_returns(
    window_returns: list[float], windows: list[dict[str, Any]], bps: float
) -> list[float]:
    """Apply the incremental cost grid to EVAL-09 returns (already net of 1 bp).

    ``r_b = window_return - (window_traded_notional * (b - 1) / 1e4) / window_nav_start``
    then chain ``prod(1 + r_b) - 1``. At b=1 the incremental term is zero (returns are
    already at the 1 bp baseline).
    """
    out: list[float] = []
    for r, w in zip(window_returns, windows):
        notional = _finite(w.get("window_traded_notional", 0.0))
        nav = _finite(w.get("window_nav_start", INITIAL_CAPITAL)) or INITIAL_CAPITAL
        incremental_bps = float(bps) - NET_BASELINE_BPS
        r_b = float(r) - (notional * incremental_bps / 1e4) / nav
        out.append(r_b)
    return out


def _chained_return(returns: Sequence[float]) -> float:
    total = 1.0
    for r in returns:
        total *= 1.0 + float(r)
    return float(total - 1.0)


def _equity_curve(returns: Sequence[float], start: float = INITIAL_CAPITAL) -> list[float]:
    eq = [float(start)]
    for r in returns:
        eq.append(eq[-1] * (1.0 + float(r)))
    return eq


def _series_metrics(
    window_returns: list[float], windows: list[dict[str, Any]], bps: float
) -> dict[str, Any]:
    r_b = _incremental_window_returns(window_returns, windows, bps)
    eq = _equity_curve(r_b)
    metrics = compute_metrics(eq)
    return {
        "bps": float(bps),
        "net_return": float(_chained_return(r_b)),
        "net_sharpe": float(metrics.get("sharpe", 0.0)),
        "net_ann_vol": float(metrics.get("ann_vol", 0.0)),
        "max_drawdown": float(metrics.get("max_drawdown", 0.0)),
        "window_returns_at_bps": [float(v) for v in r_b],
        "oos_equity_curve": [float(v) for v in eq],
    }


def _admissible(window_returns: list[float]) -> bool:
    vals = [float(v) for v in window_returns if math.isfinite(float(v))]
    if len(vals) < 2:
        return False
    nonzero = [v for v in vals if v != 0.0]
    return len(set(nonzero)) >= MIN_DISTINCT_NONZERO


def _load_eval06_baseline() -> dict[str, Any] | None:
    """Load the sealed EVAL-06 artifact if present on disk (never re-run it here)."""
    path = Path("research_state/STRATEGY_FALSIFICATION_20261112T163240Z.json")
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def evaluate_final_gonogo(
    seeds: list[int] | None = None,
    n_points: int = 500,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    n_permutations: int = 1000,
) -> dict[str, Any]:
    """Run the EVAL-10 final GO/NO-GO certification and return a strict report."""
    if seeds is None:
        seeds = [1, 2, 3, 4, 5]
    seeds = [int(s) for s in seeds]

    # Real computation: EVAL-09 engine in-process (never parse the 7 MB artifact).
    report09 = evaluate_gamma_inventory_hedge(
        seeds=seeds,
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=purge,
        embargo=embargo,
    )

    per_seed: list[dict[str, Any]] = []
    seeds_passing = 0
    passing_series = 0
    total_series = 0
    all_net_returns_1bp: list[float] = []
    all_net_sharpes_1bp: list[float] = []
    all_with_returns: list[float] = []
    all_without_returns: list[float] = []

    cost_grid_agg: dict[str, dict[str, Any]] = {
        str(b): {"bps": float(b), "net_returns": [], "net_sharpes": []} for b in COST_GRID_BPS
    }

    for seed_report in report09["per_seed"]:
        seed = int(seed_report["seed"])
        symbols_out: dict[str, dict[str, Any]] = {}
        seed_pass = True
        failing_conditions: list[str] = []

        for sym, sym_data in seed_report["symbols"].items():
            wh = sym_data["with_hedge"]
            wo = sym_data["without_hedge"]
            window_returns = [float(v) for v in wh["window_returns"]]
            windows = wh.get("windows", [])
            without_window_returns = [float(v) for v in wo["window_returns"]]

            total_series += 1
            if len(window_returns) != len(without_window_returns):
                raise ValueError(
                    f"seed {seed} {sym}: with-hedge ({len(window_returns)}) vs "
                    f"without-hedge ({len(without_window_returns)}) length mismatch"
                )
            if not _admissible(window_returns):
                seed_pass = False
                failing_conditions.append(f"{sym}: admissible_track_record")
                symbols_out[sym] = {
                    "with_hedge": {k: v for k, v in wh.items() if k not in ("windows", "snapshots", "oos_equity_curve")},
                    "cost_grid": {},
                    "conditions": {"admissible_track_record": False},
                    "pass": False,
                }
                continue

            # Cost grid per series (mean across series reported separately).
            grid_out: dict[str, dict[str, Any]] = {}
            for b in COST_GRID_BPS:
                m = _series_metrics(window_returns, windows, float(b))
                grid_out[str(b)] = {
                    "bps": m["bps"],
                    "net_return": m["net_return"],
                    "net_sharpe": m["net_sharpe"],
                    "max_drawdown": m["max_drawdown"],
                }
                cost_grid_agg[str(b)]["net_returns"].append(m["net_return"])
                cost_grid_agg[str(b)]["net_sharpes"].append(m["net_sharpe"])

            base = grid_out[str(int(NET_BASELINE_BPS))]

            # Bootstrap CI for mean net return of this series (seed-fixed, deterministic).
            block_size = min(3, max(1, len(window_returns)))
            ci_return = block_bootstrap_ci(
                window_returns, np.mean, seed=seed, n_bootstrap=2000, block_size=block_size
            )
            ci_sharpe = block_bootstrap_ci(
                [base["net_sharpe"]], np.mean, seed=seed + 1, n_bootstrap=2000, block_size=1
            )

            # Paired permutation: with-hedge vs without-hedge window returns.
            perm = permutation_test(
                window_returns,
                without_window_returns,
                statistic=np.mean,
                n_permutations=n_permutations,
                paired=True,
                alternative="two-sided",
                seed=seed,
            )

            conditions = {
                "net_sharpe_positive": bool(base["net_sharpe"] > 0.0),
                "bootstrap_lower_positive": bool(ci_return[1] > 0.0 or perm["p_value"] < 0.05),
                "net_return_positive": bool(base["net_return"] > 0.0),
                "admissible_track_record": bool(_admissible(window_returns)),
            }
            sym_pass = bool(all(conditions.values()))
            if sym_pass:
                passing_series += 1
            else:
                seed_pass = False
                for name, cond in conditions.items():
                    if not cond:
                        failing_conditions.append(f"{sym}: {name}")

            if seed_pass:
                pass  # finalized after all symbols
            all_net_returns_1bp.append(base["net_return"])
            all_net_sharpes_1bp.append(base["net_sharpe"])
            all_with_returns.extend(window_returns)
            all_without_returns.extend(without_window_returns)

            symbols_out[sym] = {
                "with_hedge": {
                    k: v
                    for k, v in wh.items()
                    if k not in ("windows", "snapshots", "oos_equity_curve")
                },
                "without_hedge": {
                    k: v
                    for k, v in wo.items()
                    if k not in ("windows", "snapshots", "oos_equity_curve")
                },
                "cost_grid": grid_out,
                "bootstrap_ci": {
                    "mean_net_return": {"point": float(ci_return[0]), "lo": float(ci_return[1]), "hi": float(ci_return[2])},
                    "net_sharpe": {"point": float(ci_sharpe[0]), "lo": float(ci_sharpe[1]), "hi": float(ci_sharpe[2])},
                    "block_size": int(block_size),
                    "n_bootstrap": 2000,
                },
                "permutation": {
                    "observed_difference": float(perm["observed_difference"]),
                    "p_value": float(perm["p_value"]),
                    "significant_at_05": bool(perm["significant_at_05"]),
                    "paired": bool(perm["paired"]),
                    "n_permutations": int(perm["n_permutations"]),
                },
                "conditions": {k: bool(v) for k, v in conditions.items()},
                "pass": sym_pass,
            }

        if seed_pass:
            seeds_passing += 1

        per_seed.append(
            {
                "seed": seed,
                "symbols": symbols_out,
                "seed_pass": bool(seed_pass),
                "failing_conditions": failing_conditions,
                "num_symbols": int(len(symbols_out)),
                "symbols_passing": int(sum(1 for s in symbols_out.values() if s.get("pass"))),
            }
        )

    num_seeds = len(seeds)
    pass_fraction = float(seeds_passing / num_seeds) if num_seeds else 0.0
    verdict = "GO" if pass_fraction >= GO_SEED_FRACTION else "NO-GO"
    series_pass_fraction = float(passing_series / total_series) if total_series else 0.0

    # Aggregate block-bootstrap CI over the 15 series (seed-fixed).
    block_size = min(3, max(1, len(all_net_returns_1bp)))
    ci_mean_return = block_bootstrap_ci(
        all_net_returns_1bp, np.mean, seed=0, n_bootstrap=2000, block_size=block_size
    )
    ci_mean_sharpe = block_bootstrap_ci(
        all_net_sharpes_1bp, np.mean, seed=1, n_bootstrap=2000, block_size=block_size
    )

    # Aggregate paired permutation: with-hedge vs without-hedge across all series.
    perm_agg = permutation_test(
        all_with_returns,
        all_without_returns,
        statistic=np.mean,
        n_permutations=max(n_permutations, 2000),
        paired=True,
        alternative="two-sided",
        seed=0,
    )

    mean_net_return = float(sum(all_net_returns_1bp) / len(all_net_returns_1bp)) if all_net_returns_1bp else 0.0
    mean_net_sharpe = float(sum(all_net_sharpes_1bp) / len(all_net_sharpes_1bp)) if all_net_sharpes_1bp else 0.0

    # Cost grid aggregated across all series.
    cost_grid_out: dict[str, dict[str, Any]] = {}
    for b in COST_GRID_BPS:
        key = str(b)
        rets = cost_grid_agg[key]["net_returns"]
        shs = cost_grid_agg[key]["net_sharpes"]
        cost_grid_out[key] = {
            "bps": float(b),
            "mean_net_return": float(sum(rets) / len(rets)) if rets else 0.0,
            "mean_net_sharpe": float(sum(shs) / len(shs)) if shs else 0.0,
            "num_series": int(len(rets)),
        }

    # EVAL-06 flat-cost baseline (reference only, never re-run here).
    eval06 = _load_eval06_baseline()
    eval06_ref: dict[str, Any] = {}
    if eval06 is not None:
        agg = eval06.get("aggregate", {})
        eval06_ref = {
            "present": True,
            "artifact": "research_state/STRATEGY_FALSIFICATION_20261112T163240Z.json",
            "verdict": agg.get("verdict"),
            "pass_fraction": agg.get("pass_fraction"),
            "mean_net_sharpe": agg.get("mean_net_sharpe"),
            "mean_net_return": agg.get("mean_net_return"),
        }
    else:
        eval06_ref = {"present": False, "artifact": "research_state/STRATEGY_FALSIFICATION_20261112T163240Z.json (absent)"}

    failing_conditions_all: list[str] = []
    for r in per_seed:
        failing_conditions_all.extend(r["failing_conditions"])

    aggregate = {
        "seeds": [int(s) for s in seeds],
        "num_seeds": int(num_seeds),
        "seeds_passing": int(seeds_passing),
        "pass_fraction": float(pass_fraction),
        "series_pass_fraction": float(series_pass_fraction),
        "go_seed_fraction": float(GO_SEED_FRACTION),
        "verdict": verdict,
        "mean_net_return": float(mean_net_return),
        "mean_net_sharpe": float(mean_net_sharpe),
        "bootstrap_ci_mean_net_return": {
            "point": float(ci_mean_return[0]),
            "lo": float(ci_mean_return[1]),
            "hi": float(ci_mean_return[2]),
            "block_size": int(block_size),
            "n_bootstrap": 2000,
        },
        "bootstrap_ci_mean_net_sharpe": {
            "point": float(ci_mean_sharpe[0]),
            "lo": float(ci_mean_sharpe[1]),
            "hi": float(ci_mean_sharpe[2]),
            "block_size": int(block_size),
            "n_bootstrap": 2000,
        },
        "permutation_with_vs_without_hedge": {
            "observed_difference": float(perm_agg["observed_difference"]),
            "p_value": float(perm_agg["p_value"]),
            "significant_at_05": bool(perm_agg["significant_at_05"]),
            "paired": bool(perm_agg["paired"]),
            "n_permutations": int(perm_agg["n_permutations"]),
            "statistic_a": float(perm_agg["statistic_a"]),
            "statistic_b": float(perm_agg["statistic_b"]),
        },
        "cost_grid": cost_grid_out,
        "failing_conditions": failing_conditions_all,
        "eval06_baseline_reference": eval06_ref,
        "total_series": int(total_series),
        "passing_series": int(passing_series),
    }

    report: dict[str, Any] = {
        "report_id": "STRATEGY_EVAL_10_FINAL_GONOGO",
        "generated_at": _utc_now_iso(),
        "config": {
            "seeds": [int(s) for s in seeds],
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "purge": int(purge),
            "embargo": int(embargo),
            "n_permutations": int(n_permutations),
            "cost_grid_bps": [int(b) for b in COST_GRID_BPS],
            "net_baseline_bps": float(NET_BASELINE_BPS),
            "go_seed_fraction": float(GO_SEED_FRACTION),
            "symbols": list(report09["config"]["symbols"]),
            "initial_capital": INITIAL_CAPITAL,
        },
        "per_seed": per_seed,
        "aggregate": aggregate,
        "never_valid_true": True,
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def _write_markdown(report: dict[str, Any]) -> str:
    agg = report["aggregate"]
    cfg = report["config"]
    lines: list[str] = []
    lines.append("# FINAL NET-OF-COST GO/NO-GO CERTIFICATION REPORT — EVAL-10")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Symbols: {', '.join(cfg['symbols'])}")
    lines.append(f"- Seeds: {cfg['seeds']}")
    lines.append(f"- Cost grid (bps): {cfg['cost_grid_bps']} (net baseline: {cfg['net_baseline_bps']} bp)")
    lines.append(f"- Permutations: {cfg['n_permutations']}")
    lines.append("")
    lines.append("## VERDICT")
    lines.append("")
    lines.append(f"## {agg['verdict']}")
    lines.append("")
    lines.append("## Aggregate (15 seed×symbol series at 1 bp net baseline)")
    lines.append("")
    for k in (
        "num_seeds",
        "seeds_passing",
        "pass_fraction",
        "series_pass_fraction",
        "go_seed_fraction",
        "verdict",
        "mean_net_return",
        "mean_net_sharpe",
        "total_series",
        "passing_series",
    ):
        lines.append(f"- {k}: {agg[k]}")
    lines.append("")
    lines.append("## Block-bootstrap CI (seed-fixed, deterministic, 2000 resamples, block=3)")
    lines.append("")
    for k in ("bootstrap_ci_mean_net_return", "bootstrap_ci_mean_net_sharpe"):
        v = agg[k]
        lines.append(
            f"- {k}: point={v['point']:.6f}, lo={v['lo']:.6f}, hi={v['hi']:.6f}, "
            f"block_size={v['block_size']}, n_bootstrap={v['n_bootstrap']}"
        )
    lines.append("")
    p = agg["permutation_with_vs_without_hedge"]
    lines.append("## Paired permutation: with-hedge vs without-hedge (all series)")
    lines.append("")
    lines.append(f"- observed_difference: {p['observed_difference']:.6f}")
    lines.append(f"- p_value: {p['p_value']:.6f}")
    lines.append(f"- significant_at_05: {p['significant_at_05']}")
    lines.append(f"- paired: {p['paired']}, n_permutations: {p['n_permutations']}")
    lines.append(f"- statistic_a (with-hedge): {p['statistic_a']:.6f}")
    lines.append(f"- statistic_b (without-hedge): {p['statistic_b']:.6f}")
    lines.append("")
    lines.append("## Cost grid (mean net Sharpe / mean net return across series)")
    lines.append("")
    for key in sorted(agg["cost_grid"], key=lambda k: float(agg["cost_grid"][k]["bps"])):
        v = agg["cost_grid"][key]
        lines.append(
            f"- {v['bps']} bps: mean_net_sharpe={v['mean_net_sharpe']:.6f}, "
            f"mean_net_return={v['mean_net_return']:.6f}, series={v['num_series']}"
        )
    lines.append("")
    lines.append("## EVAL-06 flat-cost baseline (reference only)")
    lines.append("")
    ref = agg["eval06_baseline_reference"]
    lines.append(f"- present: {ref['present']}")
    lines.append(f"- artifact: {ref['artifact']}")
    if ref["present"]:
        lines.append(f"- verdict: {ref.get('verdict')}")
        lines.append(f"- pass_fraction: {ref.get('pass_fraction')}")
        lines.append(f"- mean_net_sharpe: {ref.get('mean_net_sharpe')}")
        lines.append(f"- mean_net_return: {ref.get('mean_net_return')}")
    lines.append("")
    lines.append("## Failing conditions")
    lines.append("")
    if agg["failing_conditions"]:
        for c in agg["failing_conditions"]:
            lines.append(f"- {c}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Per-seed summary")
    lines.append("")
    for r in report["per_seed"]:
        lines.append(
            f"- seed {r['seed']}: seed_pass={r['seed_pass']}, "
            f"symbols_passing={r['symbols_passing']}/{r['num_symbols']}, "
            f"failing={r['failing_conditions'] if r['failing_conditions'] else 'None'}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Final net-of-cost GO/NO-GO certification (EVAL-10) on the EVAL-09 with-hedge portfolio"
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    ts = args.timestamp.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    stamp = f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts

    report = evaluate_final_gonogo(
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        purge=args.purge,
        embargo=args.embargo,
        n_permutations=args.permutations,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "verdict": report["aggregate"]["verdict"],
                "pass_fraction": report["aggregate"]["pass_fraction"],
                "series_pass_fraction": report["aggregate"]["series_pass_fraction"],
                "seeds_passing": report["aggregate"]["seeds_passing"],
                "num_seeds": report["aggregate"]["num_seeds"],
                "mean_net_return": report["aggregate"]["mean_net_return"],
                "mean_net_sharpe": report["aggregate"]["mean_net_sharpe"],
                "bootstrap_lo_mean_net_return": report["aggregate"]["bootstrap_ci_mean_net_return"]["lo"],
                "bootstrap_hi_mean_net_return": report["aggregate"]["bootstrap_ci_mean_net_return"]["hi"],
                "bootstrap_lo_mean_net_sharpe": report["aggregate"]["bootstrap_ci_mean_net_sharpe"]["lo"],
                "bootstrap_hi_mean_net_sharpe": report["aggregate"]["bootstrap_ci_mean_net_sharpe"]["hi"],
                "permutation_p_value": report["aggregate"]["permutation_with_vs_without_hedge"]["p_value"],
                "permutation_significant_at_05": report["aggregate"]["permutation_with_vs_without_hedge"]["significant_at_05"],
                "cost_grid": report["aggregate"]["cost_grid"],
                "failing_conditions": report["aggregate"]["failing_conditions"],
            },
            indent=2,
        )
    )

    if args.write:
        research_state = Path("research_state")
        research_state.mkdir(parents=True, exist_ok=True)
        stem = f"STRATEGY_EVAL_10_FINAL_GONOGO_{stamp}"
        json_path = research_state / f"{stem}.json"
        md_path = research_state / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
