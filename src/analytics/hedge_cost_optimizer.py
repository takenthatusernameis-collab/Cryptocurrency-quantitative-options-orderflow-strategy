"""Hedge-drag / cost-efficiency optimizer (EVAL-11) on the EVAL-09 engine.

EVAL-10 sealed a NO-GO for the with-hedge book (mean net return -0.5580,
mean net Sharpe -22.7659). This module searches the *effective* hedge levers
that EVAL-09 actually uses:

* ``target_delta_usd`` — where the delta hedge aims;
* ``toxicity_threshold`` — the orderflow gate that can skip hedging;
* ``cost_budget_bps`` — the per-window cost budget that scales order size.

``hedge_cost_bps`` is recorded by EVAL-09 but is not applied by the sizer, so a
cost-bps axis is not trusted here. The optimizer runs the real EVAL-09 engine
for every grid point, computes net-of-cost metrics from the with-hedge window
returns, applies an explicit delta constraint, and seals the best feasible
config with a final multi-seed run. It also reports the no-hedge control so a
"best" config that merely disables hedging is visible.

Strict-serializable via ``serialize_metrics_strict`` / ``assert_json_valid``.
Never emits ``{"valid": True}``.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.analytics.gamma_inventory_hedge import (
    DEFAULT_HEDGE_COST_BPS,
    DEFAULT_IMPACT_COEFF_HEDGE,
    DEFAULT_MAX_PARTICIPATION_HEDGE,
    DEFAULT_SPREAD_BPS_HEDGE,
    evaluate_gamma_inventory_hedge,
)
from src.analytics.strategy_evaluation import compute_metrics
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

INITIAL_CAPITAL: float = 100_000.0
NET_BASELINE_BPS: float = 1.0
MAX_ABS_DELTA_USD: float = 50_000.0
MIN_HEDGES_PER_SEED: int = 1

TARGET_DELTA_GRID_USD: tuple[float, ...] = (-20_000.0, 0.0, 20_000.0)
TOXICITY_THRESHOLD_GRID: tuple[float, ...] = (0.5, 0.7, 0.9)
COST_BUDGET_GRID_BPS: tuple[float, ...] = (0.5, 2.0, 5.0)

SEARCH_SEEDS: tuple[int, ...] = (1, 2, 3)
FINAL_SEEDS: tuple[int, ...] = (1, 2, 3, 4, 5)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        value = float(x)
    except Exception:
        return default
    return value if math.isfinite(value) else default


def _config_key(config: dict[str, float]) -> tuple[float, float, float]:
    return (
        float(config["target_delta_usd"]),
        float(config["toxicity_threshold"]),
        float(config["cost_budget_bps"]),
    )


def _incremental_window_returns(
    window_returns: list[float], windows: list[dict[str, Any]], bps: float
) -> list[float]:
    """Apply the incremental cost grid to EVAL-09 returns (already net of 1 bp)."""
    out: list[float] = []
    for raw_return, window in zip(window_returns, windows):
        notional = _finite(window.get("window_traded_notional", 0.0))
        nav = _finite(window.get("window_nav_start", INITIAL_CAPITAL)) or INITIAL_CAPITAL
        incremental_bps = float(bps) - NET_BASELINE_BPS
        out.append(float(raw_return) - (notional * incremental_bps / 1e4) / nav)
    return out


def _chained_return(returns: list[float]) -> float:
    total = 1.0
    for value in returns:
        total *= 1.0 + float(value)
    return float(total - 1.0)


def _equity_curve(returns: list[float], start: float = INITIAL_CAPITAL) -> list[float]:
    curve = [float(start)]
    for value in returns:
        curve.append(curve[-1] * (1.0 + float(value)))
    return curve


def _series_metrics(
    window_returns: list[float], windows: list[dict[str, Any]], bps: float = NET_BASELINE_BPS
) -> dict[str, Any]:
    values = _incremental_window_returns(window_returns, windows, bps)
    equity = _equity_curve(values)
    metrics = compute_metrics(equity)
    return {
        "bps": float(bps),
        "net_return": float(_chained_return(values)),
        "net_sharpe": float(metrics.get("sharpe", 0.0)),
        "net_ann_vol": float(metrics.get("ann_vol", 0.0)),
        "max_drawdown": float(metrics.get("max_drawdown", 0.0)),
        "window_returns_at_bps": [float(v) for v in values],
    }


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _summarize_report(
    report: dict[str, Any],
    config: dict[str, float],
    *,
    max_abs_delta_usd: float = MAX_ABS_DELTA_USD,
    min_hedges_per_seed: int = MIN_HEDGES_PER_SEED,
) -> dict[str, Any]:
    series: list[dict[str, Any]] = []
    all_nonzero_returns: set[float] = set()
    for seed_report in report["per_seed"]:
        for symbol, symbol_report in seed_report["symbols"].items():
            with_hedge = symbol_report["with_hedge"]
            window_returns = [float(v) for v in with_hedge.get("window_returns", [])]
            windows = list(with_hedge.get("windows", []))
            metrics = _series_metrics(window_returns, windows)
            series.append(
                {
                    "seed": int(seed_report["seed"]),
                    "symbol": str(symbol),
                    "num_windows": len(window_returns),
                    "mean_abs_delta_usd": float(with_hedge.get("mean_abs_delta_usd", 0.0)),
                    "total_cost_usd": float(with_hedge.get("total_cost_usd", 0.0)),
                    "num_hedges": int(with_hedge.get("num_hedges", 0)),
                    "total_traded_notional": float(
                        with_hedge.get("total_traded_notional", 0.0)
                    ),
                    "toxic_gate_active_fraction": float(
                        with_hedge.get("toxic_gate_active_fraction", 0.0)
                    ),
                    **metrics,
                }
            )
            all_nonzero_returns.update(
                round(float(v), 12) for v in metrics["window_returns_at_bps"] if float(v) != 0.0
            )

    num_seeds = len(report["per_seed"])
    num_series = len(series)
    total_hedges = int(sum(item["num_hedges"] for item in series))
    total_cost = float(sum(item["total_cost_usd"] for item in series))
    total_notional = float(sum(item["total_traded_notional"] for item in series))
    mean_abs_delta = _mean([item["mean_abs_delta_usd"] for item in series])
    mean_sharpe = _mean([item["net_sharpe"] for item in series])
    mean_return = _mean([item["net_return"] for item in series])
    finite = all(
        math.isfinite(item["net_sharpe"])
        and math.isfinite(item["net_return"])
        and math.isfinite(item["mean_abs_delta_usd"])
        for item in series
    )
    admissible = (
        num_series > 0
        and all(item["num_windows"] >= 2 for item in series)
        and len(all_nonzero_returns) >= 2
    )
    delta_ok = finite and mean_abs_delta <= float(max_abs_delta_usd)
    cost_ok = float(config["cost_budget_bps"]) >= 0.0
    hedge_active = total_hedges >= int(min_hedges_per_seed) * max(num_seeds, 1)
    reasons: list[str] = []
    if not finite:
        reasons.append("non_finite_metrics")
    if not admissible:
        reasons.append("inadmissible_track_record")
    if not delta_ok:
        reasons.append("delta_constraint_exceeded")
    if not cost_ok:
        reasons.append("negative_cost_budget")
    if not hedge_active:
        reasons.append("insufficient_hedge_activity")
    return {
        "config": dict(config),
        "num_seeds": int(num_seeds),
        "num_series": int(num_series),
        "mean_net_return": mean_return,
        "mean_net_sharpe": mean_sharpe,
        "mean_abs_delta_usd": mean_abs_delta,
        "total_cost_usd": total_cost,
        "total_hedges": total_hedges,
        "total_traded_notional": total_notional,
        "distinct_nonzero_returns": int(len(all_nonzero_returns)),
        "feasible": bool(finite and admissible and delta_ok and cost_ok and hedge_active),
        "failure_reasons": reasons,
        "series": series,
    }


def _summarize_no_hedge_control(report: dict[str, Any]) -> dict[str, Any]:
    returns: list[float] = []
    sharpes: list[float] = []
    for seed_report in report["per_seed"]:
        for symbol_report in seed_report["symbols"].values():
            without = symbol_report["without_hedge"]
            returns.append(float(without.get("oos_return", 0.0)))
            sharpes.append(float(without.get("oos_sharpe", 0.0)))
    return {
        "mean_oos_return": _mean(returns),
        "mean_oos_sharpe": _mean(sharpes),
        "num_series": len(returns),
    }


def _best_surface_point(surface: list[dict[str, Any]]) -> dict[str, Any] | None:
    feasible = [item for item in surface if item["feasible"]]
    if not feasible:
        return None
    return sorted(
        feasible,
        key=lambda item: (
            -item["mean_net_sharpe"],
            -item["mean_net_return"],
            -item["mean_abs_delta_usd"],
            _config_key(item["config"]),
        ),
    )[0]


def evaluate_hedge_cost_optimizer(
    search_seeds: list[int] | None = None,
    *,
    final_seeds: list[int] | None = None,
    target_delta_grid: list[float] | None = None,
    toxicity_threshold_grid: list[float] | None = None,
    cost_budget_grid: list[float] | None = None,
    max_abs_delta_usd: float = MAX_ABS_DELTA_USD,
    min_hedges_per_seed: int = MIN_HEDGES_PER_SEED,
    n_points: int = 500,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    spread_bps: float = DEFAULT_SPREAD_BPS_HEDGE,
    impact_coeff: float = DEFAULT_IMPACT_COEFF_HEDGE,
    max_participation: float = DEFAULT_MAX_PARTICIPATION_HEDGE,
    hedge_cost_bps: float = DEFAULT_HEDGE_COST_BPS,
) -> dict[str, Any]:
    """Run the EVAL-11 hedge-cost grid search and seal the best feasible config."""
    search_seeds = [int(s) for s in (search_seeds or list(SEARCH_SEEDS))]
    final_seeds = [int(s) for s in (final_seeds or list(FINAL_SEEDS))]
    targets = [float(v) for v in (target_delta_grid or list(TARGET_DELTA_GRID_USD))]
    toxicities = [
        float(v) for v in (toxicity_threshold_grid or list(TOXICITY_THRESHOLD_GRID))
    ]
    budgets = [float(v) for v in (cost_budget_grid or list(COST_BUDGET_GRID_BPS))]

    if not search_seeds:
        raise ValueError("search_seeds must not be empty")
    if not final_seeds:
        raise ValueError("final_seeds must not be empty")
    if not targets or not toxicities or not budgets:
        raise ValueError("optimizer grids must not be empty")
    for value in targets + toxicities + budgets:
        if not math.isfinite(value):
            raise ValueError("optimizer grid values must be finite")
    for value in budgets:
        if value < 0.0:
            raise ValueError("cost_budget_bps grid values must be >= 0")

    surface: list[dict[str, Any]] = []
    for target in targets:
        for threshold in toxicities:
            for budget in budgets:
                config = {
                    "target_delta_usd": float(target),
                    "toxicity_threshold": float(threshold),
                    "cost_budget_bps": float(budget),
                }
                report = evaluate_gamma_inventory_hedge(
                    seeds=search_seeds,
                    n_points=n_points,
                    train_window=train_window,
                    test_window=test_window,
                    step_size=step_size,
                    purge=purge,
                    embargo=embargo,
                    target_delta_usd=float(target),
                    toxicity_threshold=float(threshold),
                    hedge_cost_bps=float(hedge_cost_bps),
                    spread_bps=float(spread_bps),
                    impact_coeff=float(impact_coeff),
                    max_participation=float(max_participation),
                    cost_budget_bps=float(budget),
                )
                surface.append(
                    _summarize_report(
                        report,
                        config,
                        max_abs_delta_usd=max_abs_delta_usd,
                        min_hedges_per_seed=min_hedges_per_seed,
                    )
                )

    best_search = _best_surface_point(surface)
    best_config: dict[str, Any] | None = None
    best_final: dict[str, Any] | None = None
    no_hedge_control: dict[str, Any] | None = None
    verdict = "NO_FEASIBLE_CONFIG"

    if best_search is not None:
        best_config = dict(best_search)
        final_report = evaluate_gamma_inventory_hedge(
            seeds=final_seeds,
            n_points=n_points,
            train_window=train_window,
            test_window=test_window,
            step_size=step_size,
            purge=purge,
            embargo=embargo,
            target_delta_usd=float(best_search["config"]["target_delta_usd"]),
            toxicity_threshold=float(best_search["config"]["toxicity_threshold"]),
            hedge_cost_bps=float(hedge_cost_bps),
            spread_bps=float(spread_bps),
            impact_coeff=float(impact_coeff),
            max_participation=float(max_participation),
            cost_budget_bps=float(best_search["config"]["cost_budget_bps"]),
        )
        best_final = _summarize_report(
            final_report,
            best_search["config"],
            max_abs_delta_usd=max_abs_delta_usd,
            min_hedges_per_seed=min_hedges_per_seed,
        )
        no_hedge_control = _summarize_no_hedge_control(final_report)
        if best_final["feasible"] and best_final["mean_net_sharpe"] > 0.0:
            verdict = "FEASIBLE_POSITIVE_SHARPE"
        elif best_final["feasible"]:
            verdict = "NO_FEASIBLE_POSITIVE_SHARPE"
        else:
            verdict = "FINAL_CONFIG_INFEASIBLE"

    report = {
        "report_id": "HEDGE_COST_OPTIMIZER_EVAL_11",
        "generated_at": _utc_now_iso(),
        "config": {
            "search_seeds": search_seeds,
            "final_seeds": final_seeds,
            "target_delta_grid_usd": targets,
            "toxicity_threshold_grid": toxicities,
            "cost_budget_grid_bps": budgets,
            "max_abs_delta_usd": float(max_abs_delta_usd),
            "min_hedges_per_seed": int(min_hedges_per_seed),
            "objective": "mean_net_sharpe",
            "net_baseline_bps": NET_BASELINE_BPS,
            "hedge_cost_bps": float(hedge_cost_bps),
            "hedge_cost_bps_inert": True,
            "hedge_cost_bps_note": (
                "EVAL-09 records hedge_cost_bps but the sizer does not apply it; "
                "the search varies cost_budget_bps, target_delta_usd and toxicity_threshold."
            ),
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "purge": int(purge),
            "embargo": int(embargo),
            "spread_bps": float(spread_bps),
            "impact_coeff": float(impact_coeff),
            "max_participation": float(max_participation),
        },
        "search": {
            "num_configs": len(surface),
            "num_feasible": int(sum(1 for item in surface if item["feasible"])),
            "surface": surface,
        },
        "best_config": best_config,
        "best_config_final": best_final,
        "no_hedge_control": no_hedge_control,
        "verdict": verdict,
        "never_valid_true": True,
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def _write_markdown(report: dict[str, Any]) -> str:
    cfg = report["config"]
    search = report["search"]
    best = report["best_config"]
    best_final = report["best_config_final"]
    control = report["no_hedge_control"]
    lines: list[str] = []
    lines.append("# HEDGE-DRAG / COST-EFFICIENCY OPTIMIZER REPORT — EVAL-11")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Search seeds: {cfg['search_seeds']} | Final seeds: {cfg['final_seeds']}")
    lines.append(
        f"- Grids: target_delta={cfg['target_delta_grid_usd']}, "
        f"toxicity={cfg['toxicity_threshold_grid']}, "
        f"cost_budget_bps={cfg['cost_budget_grid_bps']}"
    )
    lines.append(f"- Delta constraint: |mean_abs_delta_usd| <= {cfg['max_abs_delta_usd']}")
    lines.append(
        f"- hedge_cost_bps={cfg['hedge_cost_bps']} is inert in EVAL-09; "
        "cost_budget_bps is the effective cost lever."
    )
    lines.append("")
    lines.append(f"## SEARCH SURFACE ({search['num_configs']} configs, {search['num_feasible']} feasible)")
    lines.append("")
    lines.append(
        "| target_delta_usd | toxicity_threshold | cost_budget_bps | mean_net_sharpe | "
        "mean_net_return | mean_abs_delta_usd | total_hedges | feasible |"
    )
    lines.append("|---:|---:|---:|---:|---:|---:|---:|:---:|")
    for item in search["surface"]:
        c = item["config"]
        lines.append(
            f"| {c['target_delta_usd']:.0f} | {c['toxicity_threshold']:.2f} | "
            f"{c['cost_budget_bps']:.2f} | {item['mean_net_sharpe']:.6f} | "
            f"{item['mean_net_return']:.6f} | {item['mean_abs_delta_usd']:.2f} | "
            f"{item['total_hedges']} | {item['feasible']} |"
        )
    lines.append("")
    lines.append("## BEST FEASIBLE CONFIG (SEARCH)")
    lines.append("")
    if best is None:
        lines.append("- No feasible config found.")
    else:
        c = best["config"]
        lines.append(
            f"- target_delta_usd={c['target_delta_usd']}, "
            f"toxicity_threshold={c['toxicity_threshold']}, "
            f"cost_budget_bps={c['cost_budget_bps']}"
        )
        lines.append(f"- mean_net_sharpe={best['mean_net_sharpe']:.6f}")
        lines.append(f"- mean_net_return={best['mean_net_return']:.6f}")
        lines.append(f"- mean_abs_delta_usd={best['mean_abs_delta_usd']:.2f}")
        lines.append(f"- total_hedges={best['total_hedges']}")
    lines.append("")
    lines.append("## BEST FEASIBLE CONFIG (FINAL MULTI-SEED)")
    lines.append("")
    if best_final is None:
        lines.append("- No final config run.")
    else:
        lines.append(f"- mean_net_sharpe={best_final['mean_net_sharpe']:.6f}")
        lines.append(f"- mean_net_return={best_final['mean_net_return']:.6f}")
        lines.append(f"- mean_abs_delta_usd={best_final['mean_abs_delta_usd']:.2f}")
        lines.append(f"- total_hedges={best_final['total_hedges']}")
        lines.append(f"- feasible={best_final['feasible']}")
        lines.append(f"- failure_reasons={best_final['failure_reasons']}")
    lines.append("")
    if control is not None:
        lines.append("## NO-HEDGE CONTROL (FINAL MULTI-SEED)")
        lines.append("")
        lines.append(f"- mean_oos_return={control['mean_oos_return']:.6f}")
        lines.append(f"- mean_oos_sharpe={control['mean_oos_sharpe']:.6f}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hedge-drag / cost-efficiency optimizer on the EVAL-09 engine (EVAL-11)"
    )
    parser.add_argument("--search-seeds", type=int, nargs="+", default=list(SEARCH_SEEDS))
    parser.add_argument("--final-seeds", type=int, nargs="+", default=list(FINAL_SEEDS))
    parser.add_argument(
        "--target-delta-grid", type=float, nargs="+", default=list(TARGET_DELTA_GRID_USD)
    )
    parser.add_argument(
        "--toxicity-threshold-grid", type=float, nargs="+", default=list(TOXICITY_THRESHOLD_GRID)
    )
    parser.add_argument(
        "--cost-budget-grid", type=float, nargs="+", default=list(COST_BUDGET_GRID_BPS)
    )
    parser.add_argument("--max-abs-delta-usd", type=float, default=MAX_ABS_DELTA_USD)
    parser.add_argument("--min-hedges-per-seed", type=int, default=MIN_HEDGES_PER_SEED)
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_SPREAD_BPS_HEDGE)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF_HEDGE)
    parser.add_argument(
        "--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION_HEDGE
    )
    parser.add_argument("--hedge-cost-bps", type=float, default=DEFAULT_HEDGE_COST_BPS)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out-dir", type=str, default="research_state")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    report = evaluate_hedge_cost_optimizer(
        search_seeds=args.search_seeds,
        final_seeds=args.final_seeds,
        target_delta_grid=args.target_delta_grid,
        toxicity_threshold_grid=args.toxicity_threshold_grid,
        cost_budget_grid=args.cost_budget_grid,
        max_abs_delta_usd=args.max_abs_delta_usd,
        min_hedges_per_seed=args.min_hedges_per_seed,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        purge=args.purge,
        embargo=args.embargo,
        spread_bps=args.spread_bps,
        impact_coeff=args.impact_coeff,
        max_participation=args.max_participation,
        hedge_cost_bps=args.hedge_cost_bps,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "verdict": report["verdict"],
                "num_configs": report["search"]["num_configs"],
                "num_feasible": report["search"]["num_feasible"],
                "best_config": report["best_config"],
                "best_config_final": report["best_config_final"],
                "no_hedge_control": report["no_hedge_control"],
            },
            sort_keys=True,
        )
    )

    if args.write:
        ts = (
            args.timestamp.replace(":", "")
            .replace("-", "")
            .replace("T", "")
            .replace("Z", "")
            .split(".")[0]
        )
        stamp = f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"HEDGE_COST_OPTIMIZER_{stamp}.json"
        md_path = out_dir / f"HEDGE_COST_OPTIMIZER_{stamp}.md"
        json_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())