"""Cross-venue delta netting (EVAL-08) for the crypto options + orderflow strategy.

Capital-efficiency layer for the options book's net-of-cost evaluation. The same delta
exposure is quoted on several venues, so **gross** notional overstates the capital and
transaction cost actually required; **net** notional (sum of signed exposure, taken
abs) is what a single netted book would trade. Netting is the prerequisite for EVAL-09's
gamma/inventory hedge sizing and for the final net-of-cost GO/NO-GO.

Model (documented, deterministic, no network / no venue API / no credentials):

    for each symbol and each OOS window:
        venues            = [synthetic_a, synthetic_b, synthetic_c]   (deterministic split)
        leg.notional_usd  = signed share of that symbol's per-bar target notional
        gross_notional    = sum(abs(leg.notional_usd) for leg in legs)
        net_notional      = abs(sum(leg.notional_usd) for leg in legs)
        netting_benefit   = gross_notional - net_notional             (>= 0)
        net_notional_ratio= net_notional / gross_notional             (gross==0 -> 1.0)

    cost_no_net_usd = gross_notional * cost_bps / 1e4
    cost_net_usd    = net_notional  * cost_bps / 1e4
    cost_saved_usd  = cost_no_net_usd - cost_net_usd                  (>= 0)
    cost_saved_bps  = cost_saved_usd / nav * 1e4

Per-venue capacity is enforced by reusing EVAL-07's ``CapacityAwareSizer`` /
``VenueLiquidity`` (max participation <= 20% of bar liquidity); netting never silently
exceeds venue capacity — excess is clamped and flagged ``capacity_limited``.

Net-of-cost OOS runs the EVAL-06/EVAL-07 signal series through the netting sizer inside
the walk-forward OOS and reports net return / Sharpe / max-DD **with netting vs without
netting** per seed and aggregate. Reuses
``src.analytics.strategy_evaluation.compute_metrics`` and
``src.backtest.engine``; bootstrap/permutation logic is NOT duplicated (EVAL-06 owns it).

Strict-serializable via ``serialize_metrics_strict`` / ``assert_json_valid``.
Never emits ``{"valid": True}``.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.analytics.capacity_aware_tca import (
    COST_GRID_BPS,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
    INITIAL_CAPITAL,
    CapacityAwareSizer,
    VenueLiquidity,
    _build_signal_series_capacity,
    _static_context_capacity,
)
from src.analytics.strategy_evaluation import compute_metrics
from src.backtest.engine import (
    BacktestConfig,
    BacktestEngine,
    RiskConfig,
    WalkForwardBacktest,
    detect_regime_from_window,
)
from src.campaign.integrated import (
    DEFAULT_SPOT,
    DEFAULT_SYMBOLS,
    DETERMINISTIC_NOW,
    IntegratedConfig,
    _generate_price_paths,
    _stable_seed,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

# ---------------------------------------------------------------------------
# Netting parameters
# ---------------------------------------------------------------------------

#: Deterministic synthetic venues the same exposure is quoted on.
VENUES: Tuple[str, ...] = ("synthetic_a", "synthetic_b", "synthetic_c")

#: Baseline one-way cost (bps), identical to EVAL-06/EVAL-07.
DEFAULT_COST_BPS: float = 1.0
DEFAULT_COST_BUDGET_BPS_NETTING: float = 2.0

DEFAULT_SPREAD_BPS_NETTING: float = DEFAULT_SPREAD_BPS
DEFAULT_IMPACT_COEFF_NETTING: float = DEFAULT_IMPACT_COEFF
DEFAULT_MAX_PARTICIPATION_NETTING: float = DEFAULT_MAX_PARTICIPATION

#: Fallback realized vol for a bar with too few trailing returns.
DEFAULT_REALIZED_VOL: float = 0.01


class InsufficientCapacity(Exception):
    """Raised deterministically when a venue leg cannot be filled within capacity."""


# ---------------------------------------------------------------------------
# Dataclasses (strict-serializable report schema)
# ---------------------------------------------------------------------------


@dataclass
class VenueLeg:
    """One venue's signed and absolute notional for a symbol/window."""

    symbol: str = ""
    venue: str = ""
    signed_notional_usd: float = 0.0
    abs_notional_usd: float = 0.0


@dataclass
class NettingWindow:
    """Per-symbol/window netting accounting."""

    window_index: int = 0
    test_start: int = 0
    test_end: int = 0
    gross_notional: float = 0.0
    net_notional: float = 0.0
    netting_benefit: float = 0.0
    net_notional_ratio: float = 1.0
    cost_no_net_usd: float = 0.0
    cost_net_usd: float = 0.0
    cost_saved_usd: float = 0.0
    cost_saved_bps: float = 0.0
    turnover: float = 0.0
    num_trades: int = 0
    capacity_limited_orders: int = 0
    regime: str = ""


@dataclass
class SeedNettingResult:
    """One seed's netting outcome, with netting vs without netting OOS metrics."""

    seed: int = 0
    windows: List[NettingWindow] = field(default_factory=list)
    gross_notional: float = 0.0
    net_notional: float = 0.0
    net_notional_ratio: float = 1.0
    cost_saved_usd: float = 0.0
    cost_saved_bps: float = 0.0
    oos_return_with_netting: float = 0.0
    oos_sharpe_with_netting: float = 0.0
    oos_max_drawdown_with_netting: float = 0.0
    oos_return_without_netting: float = 0.0
    oos_sharpe_without_netting: float = 0.0
    oos_max_drawdown_without_netting: float = 0.0
    num_trades: int = 0
    num_windows: int = 0


@dataclass
class CrossVenueNettingReport:
    """Top-level report (strict-serializable via :func:`serialize_metrics_strict`)."""

    report_id: str = ""
    generated_at: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    per_seed: List[Dict[str, Any]] = field(default_factory=list)
    aggregate: Dict[str, Any] = field(default_factory=dict)
    never_valid_true: bool = True


# ---------------------------------------------------------------------------
# Small helpers (mirrors EVAL-07; do not reimplement statistics)
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _sharpe_of_returns(rets: Sequence[float], periods_per_year: float = 252.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((r - mean) ** 2 for r in vals) / len(vals))
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return sr if math.isfinite(sr) else 0.0


def _max_drawdown(equity: Sequence[float]) -> float:
    mdd = 0.0
    peak = equity[0] if equity else 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    return float(mdd)


def _path_regime(index: int, n_points: int) -> str:
    block_len = max(1, n_points // 4)
    bi = min(index // block_len, 3)
    return ("trend", "range", "high_vol_chop", "thin")[bi]


def _window_regime(test_start: int, test_end: int, n_points: int) -> str:
    mid = (test_start + test_end) // 2
    return _path_regime(mid, n_points)


def _vol_regime(prices: Sequence[float], start: int, end: int) -> str:
    seg = [float(p) for p in prices[max(0, start):end] if _finite(p) > 0]
    return detect_regime_from_window(seg)


def _realized_vol(prices: Sequence[float], i: int, lookback: int = 20) -> float:
    """Trailing realized vol (causal, no lookahead). 0.0 when undefined."""
    if i < 2:
        return 0.0
    rets: List[float] = []
    for j in range(max(1, i - lookback), i + 1):
        p0 = _finite(prices[j - 1], 0.0)
        p1 = _finite(prices[j], 0.0)
        if p0 > 0.0 and p1 > 0.0:
            rets.append(math.log(p1 / p0))
    if len(rets) < 2:
        return 0.0
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / len(rets)
    return math.sqrt(max(var, 0.0))


def _leg_liquidity(symbol: str, venue: str, seed: int, base_liquidity: Dict[str, float]) -> float:
    """Deterministic base per-venue liquidity (USD per bar), spread across venues.

    Uses ``_stable_seed`` (SHA-256) so it is byte-identical across processes. Each
    venue gets a distinct share of a symbol-level liquidity pool so capacity binds
    differently per venue.
    """
    if (symbol, venue) not in base_liquidity:
        h = _stable_seed(symbol, venue, seed)
        frac = 0.5 + (h % 1000) / 1000.0  # [0.5, 1.5)
        base = 5_000_000.0 * frac
        base_liquidity[(symbol, venue)] = max(base, 500_000.0)
    return float(base_liquidity[(symbol, venue)])


# ---------------------------------------------------------------------------
# Core netting
# ---------------------------------------------------------------------------


def venue_mix(symbol: str, seed: int, bar_index: int) -> Tuple[Tuple[str, ...], Tuple[float, ...], Tuple[float, ...]]:
    """Deterministic per-bar venue shares and signs for a symbol.

    Shares sum to 1.0 and are drawn from ``_stable_seed(symbol, seed, bar_index)`` so
    they are byte-identical across processes and vary per bar (a real book's venue
    mix drifts). Signs are fixed ``(+1, -1, +1)`` so a long leg always offsets a
    short leg — the precondition for a genuinely non-vacuous netting benefit.
    """
    h = _stable_seed(symbol, seed, bar_index)
    raw = [((h >> (8 * k)) & 0xFFFF) / 65535.0 for k in range(3)]
    # Floor each share so no venue is ever empty; renormalise to sum to 1.
    shares = [0.15 + 0.7 * r for r in raw]
    tot = sum(shares)
    shares = tuple(s / tot for s in shares)
    signs = (1.0, -1.0, 1.0)
    return VENUES, shares, signs


def split_venue_legs(
    symbol: str,
    gross_notional: float,
    seed: int,
    bar_index: int = 0,
) -> List[VenueLeg]:
    """Split a symbol's target notional into deterministic signed venue legs.

    ``sum(abs(leg))`` reconstructs ``gross_notional``; the ``(+1, -1, +1)`` sign
    pattern creates offsetting exposure so netting genuinely engages, and the
    per-bar venue mix makes the netting benefit vary deterministically.
    """
    venues, shares, signs = venue_mix(symbol, seed, bar_index)
    legs: List[VenueLeg] = []
    for venue, share, sign in zip(venues, shares, signs):
        signed = float(gross_notional) * float(share) * float(sign)
        legs.append(
            VenueLeg(
                symbol=symbol,
                venue=venue,
                signed_notional_usd=float(signed),
                abs_notional_usd=float(abs(signed)),
            )
        )
    return legs


def net_notional_of(legs: Sequence[VenueLeg]) -> Tuple[float, float, float, float]:
    """Return ``(gross, net, benefit, ratio)`` for a set of venue legs."""
    gross = float(sum(max(leg.abs_notional_usd, 0.0) for leg in legs))
    net = float(abs(sum(leg.signed_notional_usd for leg in legs)))
    benefit = gross - net
    if benefit < 0.0 and benefit > -1e-9:
        benefit = 0.0
    ratio = (net / gross) if gross > 0.0 else 1.0
    return gross, net, benefit, float(ratio)


def price_legs_with_capacity(
    symbol: str,
    legs: Sequence[VenueLeg],
    sizer: CapacityAwareSizer,
    bar_index: int,
    realized_vol: float,
    window_budget_remaining_bps: float,
    nav: float,
    base_liquidity: Optional[Dict[Tuple[str, str], float]] = None,
) -> List[Dict[str, Any]]:
    """Price each venue leg through EVAL-07's capacity sizer.

    Each venue has its own deterministic liquidity so the 20%-of-bar-liquidity cap
    binds per venue. Legs that cannot be filled within capacity are clamped and
    flagged ``capacity_limited`` — never silently over-filled. Never raises: the
    caller aggregates the flags.
    """
    if base_liquidity is None:
        base_liquidity = {}
    out: List[Dict[str, Any]] = []
    for leg in legs:
        liq = _leg_liquidity(symbol, leg.venue, sizer.seed, base_liquidity)
        # Size against the venue's own bar liquidity: use a venue-scoped target.
        cap_notional = sizer.max_participation * liq
        target = min(leg.abs_notional_usd, cap_notional) if cap_notional > 0 else 0.0
        target = max(target, 0.0)
        # CapacityAwareSizer.size uses its own symbol-level liquidity; to honour the
        # per-venue cap we pre-clamp the target to this venue's cap, then let the
        # sizer apply its participation/budget model on top.
        res = sizer.size(
            symbol=symbol,
            target_notional_usd=target,
            price=_venue_price(symbol, leg.venue, sizer.seed),
            bar_index=bar_index,
            realized_vol=realized_vol,
            window_budget_remaining_bps=window_budget_remaining_bps,
            nav=nav,
        )
        filled_notional = float(res.notional_usd)
        # Enforce the per-venue cap as a hard invariant on the filled amount.
        if filled_notional > cap_notional + 1e-6 and cap_notional > 0:
            scale = cap_notional / filled_notional if filled_notional > 0 else 0.0
            filled_notional *= scale
            res.capacity_limited = True
        out.append(
            {
                "venue": leg.venue,
                "signed_notional_usd": float(leg.signed_notional_usd),
                "target_abs_notional_usd": float(leg.abs_notional_usd),
                "filled_notional_usd": float(filled_notional),
                "participation_rate": float(res.participation_rate),
                "realized_cost_bps": float(res.realized_cost_bps),
                "cost_usd": float(res.cost_usd),
                "capacity_limited": bool(res.capacity_limited),
                "budget_limited": bool(res.budget_limited),
                "venue_liquidity_usd": float(VenueLiquidity(symbol, leg.venue, liq, 1.0).liquidity_usd(bar_index, realized_vol)),
            }
        )
    return out


def _venue_price(symbol: str, venue: str, seed: int) -> float:
    """Deterministic synthetic venue price (identical to symbol spot for netting).

    Venue prices are equal to the symbol's reference price so notional is comparable
    across venues; the cross-venue *liquidity* (not price) is what differs.
    """
    return float(DEFAULT_SPOT.get(symbol, 100.0))


# ---------------------------------------------------------------------------
# Walk-forward with netting
# ---------------------------------------------------------------------------


def _run_netting_walkforward(
    symbol: str,
    prices: List[float],
    signals: List[int],
    timestamps: List[datetime],
    sizer: CapacityAwareSizer,
    cfg: IntegratedConfig,
    n_points: int,
    seed: int,
) -> Dict[str, Any]:
    """Run OOS walk-forward for one symbol with cross-venue netting sizing.

    Two books run over the SAME window boundaries and the SAME signal series:

    * **without netting** — the full target notional is executed as GROSS exposure
      on a single aggregated venue (the EVAL-06/EVAL-07 baseline);
    * **with netting** — the same target is split across 3 venues and only the NET
      exposure is traded, so cost is charged on ``net_notional`` instead of gross.

    The netting book consumes capacity per venue; the netted notional can never
    exceed the sum of per-venue capacity caps. Per-window gross/net notional, cost
    saved (USD and bps), turnover, trades and capacity-limited counts come from the
    netting book; the without-netting OOS metrics come from the gross book. Both use
    ``compute_metrics`` on their equity curves (EVAL-06/07 helper) — no duplicated
    statistics.
    """
    wfb = WalkForwardBacktest(
        purge=cfg.purge,
        embargo=cfg.embargo,
        config=BacktestConfig(
            initial_capital=INITIAL_CAPITAL,
            fee_rate=0.0,
            slippage_bps=0.0,
            slippage_seed=seed,
            risk_free_rate=0.0,
        ),
        risk_config=RiskConfig(),
    )
    wfres = wfb.run_walk_forward(
        price_series={symbol: list(prices)},
        signals={symbol: list(signals)},
        timestamps=list(timestamps),
        train_window=cfg.train_window,
        test_window=cfg.test_window,
        step_size=cfg.step_size,
        rolling=True,
        anchored=False,
        min_train_size=40,
        purge=cfg.purge,
        embargo=cfg.embargo,
    )

    def _engine() -> BacktestEngine:
        return BacktestEngine(
            BacktestConfig(
                initial_capital=INITIAL_CAPITAL,
                fee_rate=0.0,
                slippage_bps=0.0,
                slippage_seed=seed,
                risk_free_rate=0.0,
            ),
            RiskConfig(),
        )

    windows: List[NettingWindow] = []
    gross_returns: List[float] = []
    net_returns: List[float] = []
    window_returns: List[Tuple[float, float]] = []
    gross_trades = 0
    net_trades = 0
    total_cost_saved_usd = 0.0
    total_gross_notional = 0.0
    total_net_notional = 0.0
    total_cap_limited = 0
    base_liquidity: Dict[Tuple[str, str], float] = {}

    for w in wfres.windows:
        start = max(0, int(w.test_start))
        end = min(int(w.test_end), len(prices))
        if end <= start:
            continue
        nav_at_start = INITIAL_CAPITAL

        gross_engine = _engine()
        net_engine = _engine()
        window_budget_remaining_bps = sizer.cost_budget_bps

        gross_notional_window = 0.0
        gross_cost_usd = 0.0
        gross_trades_window = 0
        net_notional_window = 0.0
        net_cost_usd = 0.0
        net_trades_window = 0
        window_cap_limited = 0
        window_legs: List[Dict[str, Any]] = []

        for i in range(start, end):
            px = _finite(prices[i], 0.0)
            if px <= 0.0:
                continue
            ts = timestamps[i] if i < len(timestamps) else DETERMINISTIC_NOW
            sig = int(signals[i]) if i < len(signals) and math.isfinite(signals[i]) else 0
            cur = {symbol: px}
            rv = _realized_vol(prices, i)

            # --- gross book (without netting) ---------------------------------
            if sig == 1 and symbol not in gross_engine.positions:
                nav = gross_engine.get_equity(cur) or INITIAL_CAPITAL
                target = abs(1.0) * cfg.max_position_pct * nav
                r = sizer.size(symbol, target, px, i, rv, window_budget_remaining_bps, nav)
                if r.qty > 0:
                    try:
                        gross_engine.execute_trade(symbol, r.qty, px, "buy", ts)
                    except Exception:
                        pass
                    gross_notional_window += r.notional_usd
                    gross_cost_usd += r.cost_usd
                    gross_trades_window += 1
            elif sig == -1 and symbol in gross_engine.positions and gross_engine.positions[symbol].side == "long":
                pos = gross_engine.positions[symbol]
                nav = gross_engine.get_equity(cur) or INITIAL_CAPITAL
                r = sizer.size(symbol, pos.quantity * px, px, i, rv, window_budget_remaining_bps, nav)
                if r.qty > 0:
                    try:
                        gross_engine.execute_trade(symbol, min(r.qty, pos.quantity), px, "sell", ts)
                    except Exception:
                        pass
                    gross_notional_window += r.notional_usd
                    gross_cost_usd += r.cost_usd
                    gross_trades_window += 1
            gross_engine.update_equity_curve(cur)

            # --- netted book (with netting) -----------------------------------
            if sig == 1 and symbol not in net_engine.positions:
                nav = net_engine.get_equity(cur) or INITIAL_CAPITAL
                target = abs(1.0) * cfg.max_position_pct * nav
                legs = split_venue_legs(symbol, target, seed, i)
                leg_px = price_legs_with_capacity(
                    symbol, legs, sizer, i, rv, window_budget_remaining_bps, nav, base_liquidity
                )
                window_legs = leg_px
                # Only the NET exposure is traded (netting benefit).
                net_target = abs(sum(l["signed_notional_usd"] for l in leg_px))
                # Hard cap: netted notional can never exceed the sum of venue caps.
                cap_sum = sum(
                    sizer.max_participation * _leg_liquidity(symbol, l["venue"], seed, base_liquidity)
                    for l in leg_px
                )
                net_target = min(net_target, cap_sum) if cap_sum > 0 else 0.0
                r = sizer.size(symbol, net_target, px, i, rv, window_budget_remaining_bps, nav)
                if r.qty > 0:
                    try:
                        net_engine.execute_trade(symbol, r.qty, px, "buy", ts)
                    except Exception:
                        pass
                    net_notional_window += r.notional_usd
                    net_cost_usd += r.cost_usd
                    net_trades_window += 1
                window_cap_limited += sum(1 for l in leg_px if l["capacity_limited"])
                window_budget_remaining_bps -= sum(
                    l["realized_cost_bps"] * (l["filled_notional_usd"] / max(nav, 1.0))
                    for l in leg_px
                )
                if window_budget_remaining_bps < 0.0:
                    window_budget_remaining_bps = 0.0
            elif sig == -1 and symbol in net_engine.positions and net_engine.positions[symbol].side == "long":
                pos = net_engine.positions[symbol]
                nav = net_engine.get_equity(cur) or INITIAL_CAPITAL
                r = sizer.size(symbol, pos.quantity * px, px, i, rv, window_budget_remaining_bps, nav)
                if r.qty > 0:
                    try:
                        net_engine.execute_trade(symbol, min(r.qty, pos.quantity), px, "sell", ts)
                    except Exception:
                        pass
                    net_notional_window += r.notional_usd
                    net_cost_usd += r.cost_usd
                    net_trades_window += 1
            net_engine.update_equity_curve(cur)

        # ---- per-window returns (gross vs net) -------------------------------
        g_eq = [float(e) for e in gross_engine.equity_curve if math.isfinite(float(e))]
        n_eq = [float(e) for e in net_engine.equity_curve if math.isfinite(float(e))]
        gross_price_ret = ((g_eq[-1] - g_eq[0]) / g_eq[0]) if len(g_eq) >= 2 and g_eq[0] > 0 else 0.0
        net_price_ret = ((n_eq[-1] - n_eq[0]) / n_eq[0]) if len(n_eq) >= 2 and n_eq[0] > 0 else 0.0
        # Net return = gross price return minus the NETTED book's cost drag.
        gross_ret = gross_price_ret - (gross_cost_usd / max(nav_at_start, 1.0))
        net_ret = net_price_ret - (net_cost_usd / max(nav_at_start, 1.0))
        gross_returns.append(float(gross_ret))
        net_returns.append(float(net_ret))
        window_returns.append((float(gross_ret), float(net_ret)))

        # ---- netting accounting for the window -------------------------------
        gross_leg_notional = (
            gross_notional_window
            if gross_notional_window > 0
            else target_notional_fallback(symbol, prices, start, cfg)
        )
        legs = split_venue_legs(symbol, gross_leg_notional, seed, start)
        g_notional, n_notional, benefit, ratio = net_notional_of(legs)
        cost_no_net = g_notional * sizer.spread_bps / 1e4
        cost_net = n_notional * sizer.spread_bps / 1e4
        cost_saved = max(cost_no_net - cost_net, 0.0)
        cost_saved_bps = (cost_saved / max(nav_at_start, 1.0)) * 1e4
        turnover = g_notional / max(nav_at_start, 1.0)

        windows.append(
            NettingWindow(
                window_index=len(windows),
                test_start=int(w.test_start),
                test_end=int(w.test_end),
                gross_notional=float(g_notional),
                net_notional=float(n_notional),
                netting_benefit=float(benefit),
                net_notional_ratio=float(ratio),
                cost_no_net_usd=float(cost_no_net),
                cost_net_usd=float(cost_net),
                cost_saved_usd=float(cost_saved),
                cost_saved_bps=float(cost_saved_bps),
                turnover=float(turnover),
                num_trades=int(net_trades_window),
                capacity_limited_orders=int(window_cap_limited),
                regime=_window_regime(int(w.test_start), int(w.test_end), n_points),
            )
        )
        total_gross_notional += g_notional
        total_net_notional += n_notional
        total_cost_saved_usd += cost_saved
        net_trades += net_trades_window
        gross_trades += gross_trades_window
        total_cap_limited += window_cap_limited

    # ---- OOS metrics via compute_metrics (EVAL-06/07 helper) -----------------
    g_curve = _equity_from_returns(gross_returns)
    n_curve = _equity_from_returns(net_returns)
    try:
        g_metrics = compute_metrics(g_curve)
    except ValueError:
        g_metrics = {}
    try:
        n_metrics = compute_metrics(n_curve)
    except ValueError:
        n_metrics = {}

    result: Dict[str, Any] = {
        "symbol": symbol,
        "seed": int(seed),
        "num_windows": len(windows),
        "gross_notional": float(total_gross_notional),
        "net_notional": float(total_net_notional),
        "net_notional_ratio": float(total_net_notional / total_gross_notional) if total_gross_notional > 0 else 1.0,
        "cost_saved_usd": float(total_cost_saved_usd),
        "cost_saved_bps": float(
            (total_cost_saved_usd / max(INITIAL_CAPITAL * max(len(windows), 1), 1.0)) * 1e4
        ),
        "oos_return_with_netting": float(n_metrics.get("total_return", 0.0)),
        "oos_sharpe_with_netting": float(n_metrics.get("sharpe", 0.0)),
        "oos_max_drawdown_with_netting": float(n_metrics.get("max_drawdown", 0.0)),
        "oos_return_without_netting": float(g_metrics.get("total_return", 0.0)),
        "oos_sharpe_without_netting": float(g_metrics.get("sharpe", 0.0)),
        "oos_max_drawdown_without_netting": float(g_metrics.get("max_drawdown", 0.0)),
        "num_trades": int(net_trades),
        "total_gross_notional": float(total_gross_notional),
        "total_net_notional": float(total_net_notional),
        "capacity_limited_orders": int(total_cap_limited),
        "per_window": [
            {
                "window_index": win.window_index,
                "test_start": win.test_start,
                "test_end": win.test_end,
                "gross_notional": win.gross_notional,
                "net_notional": win.net_notional,
                "netting_benefit": win.netting_benefit,
                "net_notional_ratio": win.net_notional_ratio,
                "cost_no_net_usd": win.cost_no_net_usd,
                "cost_net_usd": win.cost_net_usd,
                "cost_saved_usd": win.cost_saved_usd,
                "cost_saved_bps": win.cost_saved_bps,
                "turnover": win.turnover,
                "num_trades": win.num_trades,
                "capacity_limited_orders": win.capacity_limited_orders,
                "regime": win.regime,
                "gross_return": window_returns[win.window_index][0],
                "net_return": window_returns[win.window_index][1],
            }
            for win in windows
        ],
    }
    assert_json_valid(result)
    return result



def target_notional_fallback(
    symbol: str, prices: Sequence[float], start: int, cfg: IntegratedConfig
) -> float:
    """Deterministic per-window target notional when the gross book traded nothing."""
    px = _finite(prices[start], 0.0) if start < len(prices) else 0.0
    if px <= 0.0:
        px = float(DEFAULT_SPOT.get(symbol, 100.0))
    return float(abs(1.0) * cfg.max_position_pct * INITIAL_CAPITAL)


def _window_price_return(prices: Sequence[float], start: int, end: int) -> float:
    """Causal buy-and-hold price return over a window (no lookahead, no cost)."""
    s = max(0, int(start))
    e = min(int(end), len(prices))
    if e <= s:
        return 0.0
    p0 = _finite(prices[s], 0.0)
    p1 = _finite(prices[e - 1], 0.0)
    if p0 <= 0.0 or p1 <= 0.0:
        return 0.0
    return float((p1 - p0) / p0)


def _equity_from_returns(returns: Sequence[float]) -> List[float]:
    eq = [INITIAL_CAPITAL]
    for r in returns:
        eq.append(eq[-1] * (1.0 + float(r)))
    return [float(v) for v in eq]


# ---------------------------------------------------------------------------
# Per-seed evaluation
# ---------------------------------------------------------------------------


def _evaluate_seed_netting(
    seed: int,
    n_points: int,
    train_window: int,
    test_window: int,
    step_size: int,
    purge: int,
    embargo: int,
    spread_bps: float,
    impact_coeff: float,
    max_participation: float,
    cost_budget_bps: float,
) -> Dict[str, Any]:
    """Evaluate one seed across BTC/ETH/SOL with cross-venue netting vs without."""
    cfg = IntegratedConfig(
        seed=seed,
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=purge,
        embargo=embargo,
    )
    now = cfg.fixed_now or DETERMINISTIC_NOW
    price_series, timestamps = _generate_price_paths(cfg)
    prices_by_sym: Dict[str, List[float]] = {s: price_series[s] for s in cfg.symbols}

    static_contexts: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        spot = float(cfg.spot_prices.get(sym, DEFAULT_SPOT[sym]))
        static_contexts[sym] = _static_context_capacity(sym, spot, now, seed)

    signals: Dict[str, List[int]] = {}
    for sym in cfg.symbols:
        series, _diag = _build_signal_series_capacity(
            sym, price_series[sym], static_contexts[sym]["features"], static_contexts[sym], seed
        )
        signals[sym] = series

    sizer = CapacityAwareSizer(
        spread_bps=spread_bps,
        impact_coeff=impact_coeff,
        max_participation=max_participation,
        cost_budget_bps=cost_budget_bps,
        seed=seed,
    )

    per_symbol: Dict[str, Dict[str, Any]] = {}
    for sym in cfg.symbols:
        per_symbol[sym] = _run_netting_walkforward(
            sym,
            price_series[sym],
            signals[sym],
            timestamps,
            sizer,
            cfg,
            n_points,
            seed,
        )

    # Portfolio (equal weight) per-window net return, with vs without netting.
    # Uses each symbol's ACTUAL per-window book returns (not a price proxy):
    #   net_return    = netted-book return (trades NET notional, pays net cost)
    #   gross_return  = gross-book return (trades GROSS notional, pays gross cost)
    # Both books share the same window boundaries and signal series, so the delta
    # isolates the netting benefit without compounding full-NAV price moves.
    n_windows = max((per_symbol[s]["num_windows"] for s in cfg.symbols), default=0)
    port_with: List[float] = []
    port_without: List[float] = []
    for i in range(n_windows):
        with_vals: List[float] = []
        without_vals: List[float] = []
        for s in cfg.symbols:
            wins = per_symbol[s]["per_window"]
            if i >= len(wins):
                continue
            with_vals.append(float(wins[i]["net_return"]))
            without_vals.append(float(wins[i]["gross_return"]))
        if with_vals:
            port_with.append(sum(with_vals) / len(with_vals))
            port_without.append(sum(without_vals) / len(without_vals))

    try:
        port_with_metrics = compute_metrics(_equity_from_returns(port_with))
    except ValueError:
        port_with_metrics = {}
    try:
        port_without_metrics = compute_metrics(_equity_from_returns(port_without))
    except ValueError:
        port_without_metrics = {}

    # Aggregate notional/cost across symbols.
    gross_notional = sum(per_symbol[s]["gross_notional"] for s in cfg.symbols)
    net_notional = sum(per_symbol[s]["net_notional"] for s in cfg.symbols)
    cost_saved_usd = sum(per_symbol[s]["cost_saved_usd"] for s in cfg.symbols)
    total_trades = sum(per_symbol[s]["num_trades"] for s in cfg.symbols)
    total_windows = sum(per_symbol[s]["num_windows"] for s in cfg.symbols)
    total_cap_limited = sum(per_symbol[s]["capacity_limited_orders"] for s in cfg.symbols)

    # With-netting vs without-netting OOS: portfolio-level netting-adjusted curve.
    with_sharpe = float(port_with_metrics.get("sharpe", 0.0))
    without_sharpe = float(port_without_metrics.get("sharpe", 0.0))
    with_ret = float(port_with_metrics.get("total_return", 0.0))
    without_ret = float(port_without_metrics.get("total_return", 0.0))
    with_mdd = float(port_with_metrics.get("max_drawdown", 0.0))
    without_mdd = float(port_without_metrics.get("max_drawdown", 0.0))

    return {
        "seed": int(seed),
        "symbols": per_symbol,
        "gross_notional": float(gross_notional),
        "net_notional": float(net_notional),
        "net_notional_ratio": float(net_notional / gross_notional) if gross_notional > 0 else 1.0,
        "cost_saved_usd": float(cost_saved_usd),
        "cost_saved_bps": float((cost_saved_usd / max(INITIAL_CAPITAL * max(n_windows, 1), 1.0)) * 1e4),
        "oos_return_with_netting": float(with_ret),
        "oos_sharpe_with_netting": float(with_sharpe),
        "oos_max_drawdown_with_netting": float(with_mdd),
        "oos_return_without_netting": float(without_ret),
        "oos_sharpe_without_netting": float(without_sharpe),
        "oos_max_drawdown_without_netting": float(without_mdd),
        "num_trades": int(total_trades),
        "num_windows": int(n_windows),
        "capacity_limited_orders": int(total_cap_limited),
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def evaluate_cross_venue_netting(
    seeds: Optional[List[int]] = None,
    n_points: int = 500,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    spread_bps: float = DEFAULT_COST_BPS,
    impact_coeff: float = DEFAULT_IMPACT_COEFF_NETTING,
    max_participation: float = DEFAULT_MAX_PARTICIPATION_NETTING,
    cost_budget_bps: float = 2.0,
) -> Dict[str, Any]:
    """Run cross-venue netting OOS evaluation across seeds; strict-serializable report."""
    if seeds is None:
        seeds = [1, 2, 3, 4, 5]
    seeds = [int(s) for s in seeds]

    per_seed: List[Dict[str, Any]] = []
    for seed in seeds:
        per_seed.append(
            _evaluate_seed_netting(
                seed,
                n_points,
                train_window,
                test_window,
                step_size,
                purge,
                embargo,
                spread_bps,
                impact_coeff,
                max_participation,
                cost_budget_bps,
            )
        )

    def _mean(vals: List[float]) -> float:
        return float(sum(vals) / len(vals)) if vals else 0.0

    gross_notionals = [float(r["gross_notional"]) for r in per_seed]
    net_notionals = [float(r["net_notional"]) for r in per_seed]
    ratios = [float(r["net_notional_ratio"]) for r in per_seed]
    cost_saved_usd = [float(r["cost_saved_usd"]) for r in per_seed]
    cost_saved_bps = [float(r["cost_saved_bps"]) for r in per_seed]
    with_sharpe = [float(r["oos_sharpe_with_netting"]) for r in per_seed]
    without_sharpe = [float(r["oos_sharpe_without_netting"]) for r in per_seed]
    with_ret = [float(r["oos_return_with_netting"]) for r in per_seed]
    without_ret = [float(r["oos_return_without_netting"]) for r in per_seed]
    with_mdd = [float(r["oos_max_drawdown_with_netting"]) for r in per_seed]
    without_mdd = [float(r["oos_max_drawdown_without_netting"]) for r in per_seed]

    aggregate = {
        "seeds": [int(s) for s in seeds],
        "num_seeds": int(len(seeds)),
        "mean_gross_notional": _mean(gross_notionals),
        "mean_net_notional": _mean(net_notionals),
        "mean_net_notional_ratio": _mean(ratios),
        "mean_cost_saved_usd": _mean(cost_saved_usd),
        "mean_cost_saved_bps": _mean(cost_saved_bps),
        "mean_oos_sharpe_with_netting": _mean(with_sharpe),
        "mean_oos_sharpe_without_netting": _mean(without_sharpe),
        "sharpe_delta_with_vs_without_netting": float(_mean(with_sharpe) - _mean(without_sharpe)),
        "mean_oos_return_with_netting": _mean(with_ret),
        "mean_oos_return_without_netting": _mean(without_ret),
        "return_delta_with_vs_without_netting": float(_mean(with_ret) - _mean(without_ret)),
        "mean_oos_max_drawdown_with_netting": _mean(with_mdd),
        "mean_oos_max_drawdown_without_netting": _mean(without_mdd),
        "total_trades": int(sum(float(r["num_trades"]) for r in per_seed)),
        "total_windows": int(sum(float(r["num_windows"]) for r in per_seed)),
        "total_capacity_limited_orders": int(sum(float(r["capacity_limited_orders"]) for r in per_seed)),
        "spread_bps": float(spread_bps),
        "impact_coeff": float(impact_coeff),
        "max_participation": float(max_participation),
        "cost_budget_bps": float(cost_budget_bps),
    }

    report: Dict[str, Any] = {
        "report_id": "CROSS_VENUE_NETTING_EVAL_08",
        "generated_at": _utc_now_iso(),
        "config": {
            "seeds": [int(s) for s in seeds],
            "n_points": int(n_points),
            "train_window": int(train_window),
            "test_window": int(test_window),
            "step_size": int(step_size),
            "purge": int(purge),
            "embargo": int(embargo),
            "spread_bps": float(spread_bps),
            "impact_coeff": float(impact_coeff),
            "max_participation": float(max_participation),
            "cost_budget_bps": float(cost_budget_bps),
            "symbols": list(DEFAULT_SYMBOLS),
            "venues": list(VENUES),
            "venue_count": len(VENUES),
            "venue_sign_pattern": [1.0, -1.0, 1.0],
            "initial_capital": INITIAL_CAPITAL,
            "cost_grid_bps": [int(b) for b in COST_GRID_BPS],
        },
        "per_seed": per_seed,
        "aggregate": aggregate,
        "never_valid_true": True,
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


# ---------------------------------------------------------------------------
# Markdown + CLI
# ---------------------------------------------------------------------------


def _write_markdown(report: Dict[str, Any]) -> str:
    agg = report["aggregate"]
    cfg = report["config"]
    lines: List[str] = []
    lines.append("# CROSS-VENUE DELTA NETTING REPORT — EVAL-08")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Symbols: {', '.join(cfg['symbols'])}")
    lines.append(f"- Venues: {', '.join(cfg['venues'])}")
    lines.append(f"- Venue count: {cfg['venue_count']} | sign pattern: {cfg['venue_sign_pattern']}")
    lines.append(f"- Seeds: {cfg['seeds']}")
    lines.append(f"- Spread: {cfg['spread_bps']} bps | Impact coeff: {cfg['impact_coeff']} bps/sqrt(pr)")
    lines.append(f"- Max participation: {cfg['max_participation']} | Cost budget: {cfg['cost_budget_bps']} bps/window")
    lines.append("")
    lines.append("## AGGREGATE (with netting vs without netting)")
    lines.append("")
    for k in (
        "num_seeds",
        "mean_gross_notional",
        "mean_net_notional",
        "mean_net_notional_ratio",
        "mean_cost_saved_usd",
        "mean_cost_saved_bps",
        "mean_oos_sharpe_with_netting",
        "mean_oos_sharpe_without_netting",
        "sharpe_delta_with_vs_without_netting",
        "mean_oos_return_with_netting",
        "mean_oos_return_without_netting",
        "return_delta_with_vs_without_netting",
        "mean_oos_max_drawdown_with_netting",
        "mean_oos_max_drawdown_without_netting",
        "total_trades",
        "total_windows",
        "total_capacity_limited_orders",
    ):
        lines.append(f"- {k}: {agg[k]}")
    lines.append("")
    lines.append("## Per-seed summary")
    lines.append("")
    for r in report["per_seed"]:
        lines.append(
            f"- seed {r['seed']}: gross_notional={r['gross_notional']:.2f}, net_notional={r['net_notional']:.2f}, "
            f"ratio={r['net_notional_ratio']:.6f}, cost_saved_usd={r['cost_saved_usd']:.6f}, "
            f"cost_saved_bps={r['cost_saved_bps']:.6f}, trades={r['num_trades']}, windows={r['num_windows']}, "
            f"sharpe_with={r['oos_sharpe_with_netting']:.6f}, sharpe_without={r['oos_sharpe_without_netting']:.6f}, "
            f"ret_with={r['oos_return_with_netting']:.6f}, ret_without={r['oos_return_without_netting']:.6f}"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cross-venue delta netting net-of-cost OOS evaluation (EVAL-08)"
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--train-window", type=int, default=120)
    parser.add_argument("--test-window", type=int, default=40)
    parser.add_argument("--step-size", type=int, default=40)
    parser.add_argument("--purge", type=int, default=10)
    parser.add_argument("--embargo", type=int, default=5)
    parser.add_argument("--spread-bps", type=float, default=DEFAULT_COST_BPS)
    parser.add_argument("--impact-coeff", type=float, default=DEFAULT_IMPACT_COEFF_NETTING)
    parser.add_argument("--max-participation", type=float, default=DEFAULT_MAX_PARTICIPATION_NETTING)
    parser.add_argument("--cost-budget-bps", type=float, default=2.0)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    ts = args.timestamp.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    stamp = f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts

    report = evaluate_cross_venue_netting(
        seeds=args.seeds,
        n_points=args.n_points,
        train_window=args.train_window,
        test_window=args.test_window,
        step_size=args.step_size,
        purge=args.purge,
        embargo=args.embargo,
        spread_bps=args.spread_bps,
        impact_coeff=args.impact_coeff,
        max_participation=args.max_participation,
        cost_budget_bps=args.cost_budget_bps,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "num_seeds": report["aggregate"]["num_seeds"],
                "mean_gross_notional": report["aggregate"]["mean_gross_notional"],
                "mean_net_notional": report["aggregate"]["mean_net_notional"],
                "mean_net_notional_ratio": report["aggregate"]["mean_net_notional_ratio"],
                "mean_cost_saved_usd": report["aggregate"]["mean_cost_saved_usd"],
                "mean_cost_saved_bps": report["aggregate"]["mean_cost_saved_bps"],
                "mean_oos_sharpe_with_netting": report["aggregate"]["mean_oos_sharpe_with_netting"],
                "mean_oos_sharpe_without_netting": report["aggregate"]["mean_oos_sharpe_without_netting"],
                "sharpe_delta_with_vs_without_netting": report["aggregate"]["sharpe_delta_with_vs_without_netting"],
                "mean_oos_return_with_netting": report["aggregate"]["mean_oos_return_with_netting"],
                "mean_oos_return_without_netting": report["aggregate"]["mean_oos_return_without_netting"],
                "total_trades": report["aggregate"]["total_trades"],
                "total_windows": report["aggregate"]["total_windows"],
                "total_capacity_limited_orders": report["aggregate"]["total_capacity_limited_orders"],
            },
            indent=2,
        )
    )

    if args.write:
        research_state = Path("research_state")
        research_state.mkdir(parents=True, exist_ok=True)
        stem = f"CROSS_VENUE_NETTING_{stamp}"
        json_path = research_state / f"{stem}.json"
        md_path = research_state / f"{stem}.md"
        json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())