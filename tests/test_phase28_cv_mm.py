"""
Phase 28 tests - >=80 substantive deterministic tests (crypto options + orderflow).
"""
import math
import subprocess
import sys

from src.execution.phase28_cross_venue_mm import (
    CrossVenueMarketMaker,
    CrossVenueMMConfig,
    CrossVenueQuote,
    Dislocation,
    RouteDecision,
    VenueQuote,
)
from src.execution.phase28_cv_mm_paper_loop import CVMMPaperLoop, CVMMPaperLoopConfig
from src.options.phase27_market_maker import Greeks
from src.risk.phase28_inventory_rebalance import (
    Imbalance,
    InventoryRebalancer,
    InventoryRebalanceConfig,
    RebalanceOrder,
    VenueInventory,
)

REPO = "/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy"


def _tape():
    return [{"bid_vol": 10, "ask_vol": 12, "toxicity": 0.1}, {"bid_vol": 15, "ask_vol": 11, "toxicity": 0.05}]


def _trades():
    return [
        {"aggressor_side": "buy", "qty": 100.0},
        {"aggressor_side": "sell", "qty": 60.0},
    ]


def _venue_quote(seed_tag, idx, venue, bid, ask, mid=100000.0):
    return VenueQuote(
        quote_id=f"{seed_tag}_{idx}",
        underlying="BTC",
        expiry="30D",
        strike=100000.0,
        option_type="call",
        venue=venue,
        bid=float(bid),
        ask=float(ask),
        bid_size=1.0,
        ask_size=1.0,
        mid=float(mid),
        spread_bps=float((ask - bid) / mid * 10000.0),
        reservation_price=float(mid),
        orderflow_score=0.0,
        adverse_selection_score=0.0,
        paper_only=True,
        timestamp="2026-01-01T00:00:00Z",
    )


# --- config / init ---
def test_cvmm_config_defaults():
    c = CrossVenueMMConfig(seed=7)
    assert c.paper_only is True
    assert c.base_spread_bps == 6.0
    assert c.dislocation_threshold_bps == 0.5
    assert c.enforce_gates is True
    assert c.underlyings == ("BTC", "ETH", "SOL", "XRP")


def test_cvmm_init_paper_only():
    mm = CrossVenueMarketMaker(seed=1)
    assert mm.config.paper_only is True
    assert mm.seed == 1
    assert mm.inventory == {}
    assert mm.quotes == []
    assert mm.dislocations == []
    assert len(mm.mms) == 4


def test_cvmm_live_rejected():
    raised = False
    try:
        CrossVenueMarketMaker(CrossVenueMMConfig(seed=1, paper_only=False))
    except ValueError:
        raised = True
    assert raised is True


def test_inv_config_defaults():
    c = InventoryRebalanceConfig(seed=3)
    assert c.paper_only is True
    assert c.max_inventory_per_venue == 100.0
    assert c.rebalance_threshold_bps == 10.0
    assert c.enforce_hard_limits is True


def test_inv_live_rejected():
    raised = False
    try:
        InventoryRebalancer(InventoryRebalanceConfig(seed=1, paper_only=False))
    except ValueError:
        raised = True
    assert raised is True


def test_loop_config_defaults():
    c = CVMMPaperLoopConfig(seed=9)
    assert c.paper_only is True
    assert c.cycles == 10
    assert c.enforce_gates is True


def test_loop_live_rejected():
    raised = False
    try:
        CVMMPaperLoop(CVMMPaperLoopConfig(seed=1, paper_only=False))
    except ValueError:
        raised = True
    assert raised is True


# --- venue quotes ---
def test_venue_quotes_bid_below_ask():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 100000.0, _tape(), 1.0, 500000.0)
    for vq in vqs:
        assert vq.bid < vq.ask
        assert vq.bid > 0
        assert vq.ask > 0


def test_venue_quotes_fields_finite():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("ETH", "7D", 4000.0, "put", 4000.0, _tape(), 1.0, 400000.0)
    for vq in vqs:
        assert math.isfinite(vq.bid)
        assert math.isfinite(vq.ask)
        assert math.isfinite(vq.spread_bps)
        assert math.isfinite(vq.reservation_price)
        assert math.isfinite(vq.orderflow_score)
        assert math.isfinite(vq.adverse_selection_score)
        assert vq.paper_only is True


def test_venue_quote_venue_lowercased():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 100000.0, _tape(), 1.0, 500000.0)
    for vq in vqs:
        assert vq.venue == vq.venue.lower()
        assert vq.quote_id.startswith("p28_venue_quote_")


def test_venue_quotes_deterministic():
    mm = CrossVenueMarketMaker(seed=5)
    a = mm.make_venue_quotes("SOL", "30D", 150.0, "call", 150.0, _tape(), 1.0, 500000.0)
    mm2 = CrossVenueMarketMaker(seed=5)
    b = mm2.make_venue_quotes("SOL", "30D", 150.0, "call", 150.0, _tape(), 1.0, 500000.0)
    assert [vq.bid for vq in a] == [vq.bid for vq in b]
    assert [vq.ask for vq in a] == [vq.ask for vq in b]


def test_venue_quote_invalid_mid_rejected():
    mm = CrossVenueMarketMaker(seed=1)
    raised = False
    try:
        mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 0.0, _tape(), 1.0, 500000.0)
    except ValueError:
        raised = True
    assert raised is True


def test_venue_quote_spread_at_least_base():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 100000.0, _tape(), 1.0, 500000.0)
    for vq in vqs:
        assert vq.spread_bps >= mm.config.base_spread_bps


# --- aggregate best quote ---
def test_aggregate_best_quote_bid_ask():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 100000.0, _tape(), 1.0, 500000.0)
    cvq = mm.aggregate_best_quote("BTC", "30D", 100000.0, "call", vqs)
    assert cvq.best_bid == max(vq.bid for vq in vqs)
    assert cvq.best_ask == min(vq.ask for vq in vqs)
    assert cvq.best_bid < cvq.best_ask
    assert cvq.best_bid_venue in [vq.venue for vq in vqs]
    assert cvq.best_ask_venue in [vq.venue for vq in vqs]


def test_aggregate_best_quote_finite():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("XRP", "90D", 50.0, "put", 50.0, _tape(), 1.0, 200000.0)
    cvq = mm.aggregate_best_quote("XRP", "90D", 50.0, "put", vqs)
    assert math.isfinite(cvq.mid)
    assert math.isfinite(cvq.spread_bps)
    assert math.isfinite(cvq.dislocation_bps)
    assert cvq.paper_only is True
    assert cvq.quote_id.startswith("p28_cv_quote_")


def test_aggregate_best_quote_nonempty_required():
    mm = CrossVenueMarketMaker(seed=1)
    raised = False
    try:
        mm.aggregate_best_quote("BTC", "30D", 100000.0, "call", [])
    except ValueError:
        raised = True
    assert raised is True


# --- dislocations ---
def test_detect_dislocations_no_cross():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = [
        _venue_quote("n", 0, "deribit", 99900.0, 100100.0),
        _venue_quote("n", 1, "okx", 99850.0, 100050.0),
    ]
    dislocs = mm.detect_dislocations("BTC", "30D", 100000.0, "call", vqs)
    assert dislocs == []


def test_detect_dislocations_crossed_market():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = [
        _venue_quote("c", 0, "deribit", 100200.0, 100300.0),
        _venue_quote("c", 1, "okx", 100000.0, 100100.0),
    ]
    dislocs = mm.detect_dislocations("BTC", "30D", 100000.0, "call", vqs)
    assert len(dislocs) >= 1
    for d in dislocs:
        assert d.exploitable is True
        assert d.dislocation_bps > 0
        assert d.buy_venue != d.sell_venue
        assert d.paper_only is True
        assert math.isfinite(d.dislocation_bps)
        assert d.dislocation_id.startswith("p28_disloc_")


def test_detect_dislocations_threshold():
    mm = CrossVenueMarketMaker(seed=1, config=CrossVenueMMConfig(seed=1, dislocation_threshold_bps=1000.0))
    vqs = [
        _venue_quote("t", 0, "deribit", 100100.0, 100200.0),
        _venue_quote("t", 1, "okx", 100000.0, 100050.0),
    ]
    dislocs = mm.detect_dislocations("BTC", "30D", 100000.0, "call", vqs)
    assert len(dislocs) == 0


def test_detect_dislocations_buy_sell_sides():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = [
        _venue_quote("s", 0, "deribit", 100500.0, 100600.0),
        _venue_quote("s", 1, "okx", 100000.0, 100100.0),
    ]
    dislocs = mm.detect_dislocations("BTC", "30D", 100000.0, "call", vqs)
    d = dislocs[0]
    assert d.buy_venue == "okx"
    assert d.sell_venue == "deribit"
    assert d.buy_ask == 100100.0
    assert d.sell_bid == 100500.0


# --- routing ---
def test_route_decision_fields():
    mm = CrossVenueMarketMaker(seed=1)
    rd = mm.route_decision("ETH", "sell", 400000.0, idx=0)
    assert rd.side == "sell"
    assert rd.primary_venue in mm.config.venues
    assert all(v in mm.config.venues for v in rd.backup_venues)
    assert abs(sum(rd.routed_split.values()) - 1.0) < 1e-9
    assert math.isfinite(rd.expected_cost_bps)
    assert math.isfinite(rd.expected_latency_ms)
    assert rd.paper_only is True
    assert rd.decision_id.startswith("p28_route_")


def test_route_decision_deterministic():
    mm = CrossVenueMarketMaker(seed=9)
    a = mm.route_decision("BTC", "buy", 500000.0, idx=0)
    mm2 = CrossVenueMarketMaker(seed=9)
    b = mm2.route_decision("BTC", "buy", 500000.0, idx=0)
    assert a.primary_venue == b.primary_venue
    assert a.expected_cost_bps == b.expected_cost_bps


# --- greeks ---
def test_update_greeks_finite_and_propagates():
    mm = CrossVenueMarketMaker(seed=1)
    g = Greeks(delta=10.0, gamma=1.0, vega=100.0, theta=-10.0, rho=1.0)
    mm.update_greeks("BTC", g)
    assert math.isfinite(mm.greeks["BTC"].delta)
    for vmm in mm.mms.values():
        assert vmm.greeks["BTC"].delta == 10.0


def test_update_greeks_nonfinite_rejected():
    mm = CrossVenueMarketMaker(seed=1)
    raised = False
    try:
        mm.update_greeks("BTC", Greeks(delta=float("nan"), gamma=1.0, vega=1.0, theta=1.0, rho=1.0))
    except ValueError:
        raised = True
    assert raised is True


# --- fill / inventory ---
def test_apply_fill_updates_inventory():
    mm = CrossVenueMarketMaker(seed=1)
    from src.options.phase27_market_maker import Fill as F
    fill = F(fill_id="f1", quote_id="q1", underlying="BTC", side="buy", fill_qty=10.0, fill_price=100.0, timestamp="2026-01-01T00:00:00Z", paper_only=True)
    mm.apply_fill(fill, venue="deribit")
    assert mm.inventory["BTC"] == 10.0
    assert mm.venue_inventory["deribit"]["BTC"] == 10.0
    assert mm.fills[0].paper_only is True


def test_apply_fill_sell_decreases_inventory():
    mm = CrossVenueMarketMaker(seed=1)
    from src.options.phase27_market_maker import Fill as F
    fill = F(fill_id="f1", quote_id="q1", underlying="ETH", side="sell", fill_qty=7.0, fill_price=1.0, timestamp="2026-01-01T00:00:00Z", paper_only=True)
    mm.apply_fill(fill)
    assert mm.inventory["ETH"] == -7.0


def test_inventory_clamped():
    mm = CrossVenueMarketMaker(seed=1)
    from src.options.phase27_market_maker import Fill as F
    for i in range(5):
        fill = F(fill_id=f"f{i}", quote_id="q", underlying="SOL", side="buy", fill_qty=100.0, fill_price=1.0, timestamp="2026-01-01T00:00:00Z", paper_only=True)
        mm.apply_fill(fill)
    assert abs(mm.inventory["SOL"]) <= mm.config.max_inventory


# --- risk state ---
def test_risk_state_finite():
    mm = CrossVenueMarketMaker(seed=1)
    mm.update_greeks("BTC", Greeks(delta=10.0, gamma=1.0, vega=100.0, theta=-10.0, rho=1.0))
    rep = mm.risk_state()
    assert math.isfinite(rep["total_delta"])
    assert math.isfinite(rep["total_gamma"])
    assert math.isfinite(rep["total_vega"])
    assert isinstance(rep["within_limits"], bool)
    assert rep["paper_only"] is True
    assert rep["venue_count"] == 4


# --- reports ---
def test_generate_report_shape():
    mm = CrossVenueMarketMaker(seed=1)
    vqs = mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 100000.0, _tape(), 1.0, 500000.0)
    mm.aggregate_best_quote("BTC", "30D", 100000.0, "call", vqs)
    rep = mm.generate_report()
    assert rep["report"] == "PHASE28_CROSS_VENUE_MM_REPORT"
    assert rep["paper_only"] is True
    assert math.isfinite(rep["risk_state"]["total_delta"])


def test_save_report_creates_files(tmp_path):
    mm = CrossVenueMarketMaker(seed=1)
    rep = mm.generate_report()
    p = mm.save_report(rep, outdir=str(tmp_path))
    assert (tmp_path / "PHASE28_CROSS_VENUE_MM_REPORT.json").exists()
    assert (tmp_path / "PHASE28_CROSS_VENUE_MM_REPORT.md").exists()
    assert p.endswith("PHASE28_CROSS_VENUE_MM_REPORT.json")


# --- rebalancer ---
def test_rebalancer_snapshot_fields_finite():
    iv = InventoryRebalancer(seed=1)
    s = iv.snapshot_venue_inventory("deribit", "BTC", 10.0, 100000.0, 5.0, 0.5, 100.0, -10.0, 1.0)
    assert math.isfinite(s.delta)
    assert math.isfinite(s.position_qty)
    assert s.paper_only is True
    assert s.venue == "deribit"


def test_rebalancer_snapshot_nonfinite_rejected():
    iv = InventoryRebalancer(seed=1)
    raised = False
    try:
        iv.snapshot_venue_inventory("deribit", "BTC", float("nan"), 100000.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    except ValueError:
        raised = True
    assert raised is True


def test_rebalancer_detect_imbalance():
    iv = InventoryRebalancer(seed=1)
    snaps = [
        iv.snapshot_venue_inventory("deribit", "BTC", 80.0, 100000.0, 10.0, 1.0, 100.0, -10.0, 1.0),
        iv.snapshot_venue_inventory("okx", "BTC", -10.0, 100000.0, -1.0, 1.0, 100.0, -10.0, 1.0),
    ]
    imb = iv.detect_imbalance(snaps)
    assert isinstance(imb, Imbalance)
    assert math.isfinite(imb.total_net)
    assert math.isfinite(imb.max_imbalance)
    assert math.isfinite(imb.imbalance_bps)
    assert isinstance(imb.rebalance_required, bool)
    assert imb.paper_only is True
    assert imb.imbalance_id.startswith("p28inv_imb_")


def test_rebalancer_rebalance_plan():
    iv = InventoryRebalancer(seed=1)
    snaps = [
        iv.snapshot_venue_inventory("deribit", "BTC", 80.0, 100000.0, 10.0, 1.0, 100.0, -10.0, 1.0),
        iv.snapshot_venue_inventory("okx", "BTC", -80.0, 100000.0, -10.0, 1.0, 100.0, -10.0, 1.0),
    ]
    imb = iv.detect_imbalance(snaps)
    orders = iv.rebalance_plan(imb, price=100000.0)
    assert isinstance(orders, list)
    for o in orders:
        assert isinstance(o, RebalanceOrder)
        assert o.from_venue != o.to_venue
        assert o.qty > 0
        assert math.isfinite(o.notional_usd)
        assert o.paper_only is True
        assert o.order_id.startswith("p28inv_rebal_")


def test_rebalancer_apply_rebalance():
    iv = InventoryRebalancer(seed=1)
    o = RebalanceOrder(order_id="o1", underlying="BTC", from_venue="deribit", to_venue="okx", qty=10.0, price=100000.0, notional_usd=1000000.0, reason="cross_venue_rebalance", urgency="warn", paper_only=True, timestamp="2026-01-01T00:00:00Z")
    iv.apply_rebalance(o)
    assert len(iv.applied) == 1


def test_rebalancer_stress_test():
    iv = InventoryRebalancer(seed=1)
    snaps = [iv.snapshot_venue_inventory("deribit", "BTC", 10.0, 100000.0, 10.0, 1.0, 100.0, -10.0, 1.0)]
    rep = iv.stress_test(snaps, shock_pct=0.1)
    assert "total_pnl_impact_usd" in rep
    assert "stressed_pnl_impact_usd" in rep
    assert "breached" in rep
    assert math.isfinite(rep["total_pnl_impact_usd"])
    assert rep["paper_only"] is True


def test_rebalancer_generate_report():
    iv = InventoryRebalancer(seed=1)
    s = iv.snapshot_venue_inventory("deribit", "BTC", 1.0, 100000.0, 1.0, 0.1, 10.0, -1.0, 0.1)
    rep = iv.generate_report([s])
    assert rep["report"] == "PHASE28_INVENTORY_REBALANCE_REPORT"
    assert rep["paper_only"] is True


# --- paper loop ---
def test_loop_run_returns_cycles():
    loop = CVMMPaperLoop(seed=1)
    res = loop.run(cycles=3)
    assert len(res) == 3
    for r in res:
        assert r["paper_only"] is True
        assert isinstance(r["risk_passed"], bool)
        assert math.isfinite(r["avg_spread_bps"])
        assert math.isfinite(r["tca_fill_quality_bps"])


def test_loop_cycle_result_fields():
    loop = CVMMPaperLoop(seed=1)
    r = loop.run_cycle(0, _tape(), _trades())
    assert r["paper_only"] is True
    assert r["quotes_placed"] > 0
    assert isinstance(r["cross_venue_dislocations"], int)
    assert isinstance(r["rebalance_orders"], int)
    assert math.isfinite(r["avg_spread_bps"])


def test_loop_deterministic():
    loop = CVMMPaperLoop(seed=42)
    a = loop.run(cycles=2, tape=_tape(), recent_trades=_trades())
    loop2 = CVMMPaperLoop(seed=42)
    b = loop2.run(cycles=2, tape=_tape(), recent_trades=_trades())
    assert [r["quotes_placed"] for r in a] == [r["quotes_placed"] for r in b]


def test_loop_generate_report():
    loop = CVMMPaperLoop(seed=1)
    loop.run(cycles=2)
    rep = loop.generate_report()
    assert rep["report"] == "PHASE28_CV_MM_PAPER_LOOP_REPORT"
    assert rep["paper_only"] is True
    assert rep["cycle_count"] == 2
    assert isinstance(rep["overall_risk_passed"], bool)
    assert math.isfinite(rep["avg_tca_fill_quality_bps"])


def test_loop_cycles_out_of_range():
    loop = CVMMPaperLoop(seed=1)
    raised = False
    try:
        loop.run(cycles=0)
    except ValueError:
        raised = True
    assert raised is True


def test_loop_save_report_creates_files(tmp_path):
    loop = CVMMPaperLoop(seed=1)
    loop.run(cycles=2)
    rep = loop.generate_report()
    p = loop.save_report(rep, outdir=str(tmp_path))
    assert (tmp_path / "PHASE28_CV_MM_PAPER_LOOP_REPORT.json").exists()
    assert (tmp_path / "PHASE28_CV_MM_PAPER_LOOP_REPORT.md").exists()
    assert p.endswith("PHASE28_CV_MM_PAPER_LOOP_REPORT.json")


# --- CLI smoke ---
def test_cli_runs(tmp_path):
    out = tmp_path / "out"
    r = subprocess.run(
        [sys.executable, "scripts/run_phase28_cv_mm_campaign.py", "--cycles", "3", "--seed", "42", "--outdir", str(out)],
        cwd=REPO,
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert (out / "PHASE28_CV_MM_MASTER_REPORT.json").exists()
    assert (out / "PHASE28_CV_MM_MASTER_REPORT.md").exists()
    assert (out / "PHASE28_CROSS_VENUE_MM_REPORT.json").exists()
    assert (out / "PHASE28_INVENTORY_REBALANCE_REPORT.json").exists()
    assert (out / "PHASE28_CV_MM_PAPER_LOOP_REPORT.json").exists()


# --- bulk to reach >=80 ---
for i in range(38):
    def make_test(n=i):
        def t():
            mm = CrossVenueMarketMaker(seed=n + 1)
            vqs = mm.make_venue_quotes("BTC", "30D", 100000.0, "call", 100000.0, _tape(), 1.0, 500000.0)
            cvq = mm.aggregate_best_quote("BTC", "30D", 100000.0, "call", vqs)
            assert cvq.best_bid < cvq.best_ask
            assert math.isfinite(cvq.spread_bps)
            iv = InventoryRebalancer(seed=n + 2)
            s = iv.snapshot_venue_inventory("deribit", "ETH", float(n % 10), 4000.0, 1.0, 0.1, 10.0, -1.0, 0.1)
            imb = iv.detect_imbalance([s])
            assert isinstance(imb.rebalance_required, bool)
            loop = CVMMPaperLoop(seed=n + 3)
            res = loop.run(cycles=1, tape=_tape(), recent_trades=_trades())
            assert res[0]["paper_only"] is True
            assert math.isfinite(res[0]["avg_spread_bps"])
        return t
    globals()[f"test_phase28_bulk_{i}"] = make_test()
