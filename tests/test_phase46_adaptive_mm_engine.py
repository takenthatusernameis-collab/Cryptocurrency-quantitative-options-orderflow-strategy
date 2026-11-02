from src.errors import RiskLimitError
from src.execution.phase46_adaptive_mm_engine import (
    AdaptiveMMConfig,
    LatencyArbSignal,
    MMQuote,
    Phase46AdaptiveMM,
    Regime,
)


def test_phase46_engine_constructs_paper_only():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=7, cycles=12, paper_only=True))
    assert eng.paper_only is True
    assert eng.seed == 7
    assert eng.symbols == list(eng.cfg.symbols)
    assert eng.venues == list(eng.cfg.venues)


def test_phase46_engine_live_path_hard_gated():
    try:
        Phase46AdaptiveMM(AdaptiveMMConfig(seed=7, cycles=12, paper_only=False))
    except (ValueError, RiskLimitError):
        pass
    else:
        raise AssertionError("live path must be hard-gated")


def test_phase46_make_adaptive_quote_bid_ask_finite():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=11, cycles=12, paper_only=True))
    tape = [{"bid_vol": 10.0, "ask_vol": 12.0, "toxicity": 0.1}]
    q = eng.make_adaptive_quote("BTC-PERP", "deribit", 100000.0, tape, 1.0, 100000.0, 1)
    assert isinstance(q, MMQuote)
    assert q.paper_only is True
    assert q.symbol == "BTC-PERP"
    assert q.venue == "deribit"
    assert q.bid > 0 and q.ask > 0
    assert q.ask > q.bid
    assert q.spread_bps > 0
    assert q.bid_size > 0 and q.ask_size > 0
    import json
    json.dumps(q.to_dict(), allow_nan=False)


def test_phase46_toxicity_widens_spread():
    eng_low = Phase46AdaptiveMM(AdaptiveMMConfig(seed=3, cycles=12, paper_only=True))
    eng_high = Phase46AdaptiveMM(AdaptiveMMConfig(seed=3, cycles=12, paper_only=True))
    tape_low = [{"bid_vol": 10.0, "ask_vol": 10.0, "toxicity": 0.02}]
    tape_high = [{"bid_vol": 10.0, "ask_vol": 10.0, "toxicity": 0.9}]
    q_low = eng_low.make_adaptive_quote("ETH-PERP", "okx", 4000.0, tape_low, 1.0, 100000.0, 1)
    q_high = eng_high.make_adaptive_quote("ETH-PERP", "okx", 4000.0, tape_high, 1.0, 100000.0, 1)
    assert q_high.spread_bps >= q_low.spread_bps
    assert q_high.toxicity_score > q_low.toxicity_score


def test_phase46_inventory_skew_sizes_quotes():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=5, cycles=12, paper_only=True))
    # Long inventory: skew > 0 -> smaller bid, larger ask.
    eng.inventory["BTC-PERP"] = 400.0
    tape = [{"bid_vol": 10.0, "ask_vol": 10.0, "toxicity": 0.1}]
    q_long = eng.make_adaptive_quote("BTC-PERP", "deribit", 100000.0, tape, 1.0, 100000.0, 1)
    # Short inventory: skew < 0 -> larger bid, smaller ask.
    eng2 = Phase46AdaptiveMM(AdaptiveMMConfig(seed=5, cycles=12, paper_only=True))
    eng2.inventory["BTC-PERP"] = -400.0
    q_short = eng2.make_adaptive_quote("BTC-PERP", "deribit", 100000.0, tape, 1.0, 100000.0, 1)
    assert q_long.inventory_skew > 0
    assert q_short.inventory_skew < 0
    assert q_long.bid_size < q_short.bid_size
    assert q_long.ask_size > q_short.ask_size


def test_phase46_determinism_same_seed():
    def run_seq(seed):
        eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=seed, cycles=12, paper_only=True))
        out = []
        for c in range(1, 6):
            tape = [{"bid_vol": 10.0, "ask_vol": 12.0, "toxicity": 0.2}]
            q = eng.make_adaptive_quote("SOL-PERP", "bybit", 150.0, tape, 1.0, 100000.0, c)
            out.append((q.bid, q.ask, q.spread_bps, q.bid_size, q.ask_size))
        return out
    # Determinism: same seed + same inputs -> identical quotes across engines.
    assert run_seq(99) == run_seq(99)
    assert run_seq(42) == run_seq(42)


def test_phase46_latency_arb_detects_crossed_quotes():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=1, cycles=12, paper_only=True))
    tape = [{"bid_vol": 10.0, "ask_vol": 10.0, "toxicity": 0.1}]
    q_a = eng.make_adaptive_quote("BTC-PERP", "deribit", 100000.0, tape, 1.0, 100000.0, 1)
    # Force a cross: venue B bid above venue A ask.
    q_b = MMQuote(
        quote_id="x", symbol="BTC-PERP", venue="okx", cycle=1, timestamp="t",
        bid=q_a.ask * 1.001, ask=q_a.ask * 1.002, bid_size=1.0, ask_size=1.0,
        mid=q_a.mid, reservation_price=q_a.mid, spread_bps=2.0,
        inventory_skew=0.0, toxicity_score=0.1, orderflow_score=0.1,
        adverse_selection_score=0.1, regime="ranging", paper_only=True,
    )
    sigs = eng.detect_latency_arb("BTC-PERP", [q_a, q_b], 1, notional_usd=100000.0)
    exploitable = [s for s in sigs if s.exploitable]
    assert len(exploitable) >= 1
    for s in exploitable:
        assert isinstance(s, LatencyArbSignal)
        assert s.paper_only is True
        assert s.dislocation_bps >= eng.cfg.latency_arb_threshold_bps
        assert s.buy_venue in ("deribit", "okx") and s.sell_venue in ("deribit", "okx")
        import json
        json.dumps(s.to_dict(), allow_nan=False)


def test_phase46_run_campaign_gates_ok():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=13, cycles=20, paper_only=True,
                                             delta_limit=100000.0, max_inventory=100000.0))
    rep = eng.run_campaign()
    assert rep["phase"] == "PHASE46_ADAPTIVE_MM_ENGINE"
    assert rep["paper_only"] is True
    assert rep["gates_ok"] is True
    assert rep["cycles_run"] == 20
    assert rep["n_quotes"] > 0
    assert rep["risk_state"]["within_limits"] is True
    assert isinstance(rep["n_dislocations"], int)
    import json
    json.dumps(rep, allow_nan=False)


def test_phase46_snapshot_restore_deterministic():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=17, cycles=30, paper_only=True))
    snap = eng.snapshot()  # fresh: no cycles run, inventory all 0.0, not halted
    import json
    json.dumps(snap, allow_nan=False)
    # Mutate state via cycles + direct mutation.
    eng.run_cycle(1, eng._synthetic_market_data(1))
    eng.run_cycle(2, eng._synthetic_market_data(2))
    eng._halted = True
    eng.inventory["BTC-PERP"] = 999.0
    eng.restore(snap)
    assert eng._halted is False
    assert eng.inventory["BTC-PERP"] == 0.0


def test_phase46_all_cycle_artifacts_jsonable():
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=2, cycles=10, paper_only=True))
    rep = eng.run_campaign()
    import json
    json.dumps(rep, allow_nan=False)
    for cyc in eng.cycles_run:
        json.dumps(cyc, allow_nan=False)


def test_phase46_generate_reports_writes_artifacts(tmp_path):
    eng = Phase46AdaptiveMM(AdaptiveMMConfig(seed=4, cycles=10, paper_only=True,
                                             outdir=str(tmp_path),
                                             delta_limit=100000.0, max_inventory=100000.0))
    paths = eng.generate_reports()
    import json, os
    assert os.path.exists(paths["json"])
    assert os.path.exists(paths["md"])
    assert os.path.exists(paths["campaign_json"])
    assert os.path.exists(paths["campaign_md"])
    data = json.loads(open(paths["json"]).read())
    assert data["gates_ok"] is True
    json.dumps(data, allow_nan=False)
