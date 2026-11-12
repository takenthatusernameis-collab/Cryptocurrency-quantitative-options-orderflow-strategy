from src.data.loader import DataLoader


def test_load_orderflow_synthetic():
    d = DataLoader(cache=False)
    of = d.load_orderflow('data/raw/orderflow_btcusdt_synthetic.json', venue='synthetic', symbol='BTCUSDT')
    assert len(of.trades) > 0
    assert len(of.liquidations) >= 0
    assert len(of.funding_rates) >= 0


def test_load_options_chain_synthetic():
    d = DataLoader(cache=False)
    oc = d.load_options_chain('data/raw/options_btc_synthetic.json', venue='synthetic', underlying='BTC')
    assert len(oc.quotes) > 0


def test_load_trades_unwraps_dict_wrapped_payload(tmp_path):
    """A {"trades": [...]} document must yield records, not its string keys."""
    import json

    payload = {
        "trades": [
            {"trade_id": "t1", "symbol": "BTCUSDT", "price": 64000.0, "size": 0.5,
             "side": "buy", "timestamp": "2026-10-31T06:32:42.656379Z"},
            {"trade_id": "t2", "symbol": "BTCUSDT", "price": 64010.0, "size": 0.25,
             "side": "sell", "timestamp": "2026-10-31T06:33:42.656379Z"},
        ],
        "liquidations": [],
        "venue": "synthetic",
    }
    p = tmp_path / "wrapped.json"
    p.write_text(json.dumps(payload), encoding="utf-8")

    trades = DataLoader(cache=False).load_trades(p, venue="synthetic")
    assert len(trades) == 2
    assert [t.price for t in trades] == [64000.0, 64010.0]
    assert trades[0].trade_id == "t1"


def test_load_trades_accepts_bare_list(tmp_path):
    import json

    p = tmp_path / "bare.json"
    p.write_text(json.dumps([
        {"trade_id": "b1", "symbol": "ETHUSDT", "price": 3000.0, "size": 1.0,
         "side": "buy", "timestamp": "2026-10-31T00:00:00Z"},
    ]), encoding="utf-8")

    trades = DataLoader(cache=False).load_trades(p, venue="synthetic")
    assert len(trades) == 1
    assert trades[0].price == 3000.0


def test_load_trades_real_synthetic_orderflow_file():
    trades = DataLoader(cache=False).load_trades(
        'data/raw/orderflow_btcusdt_synthetic.json', venue='synthetic'
    )
    assert len(trades) > 0
    assert all(t.price > 0 for t in trades)


def test_load_trades_unknown_shape_returns_empty(tmp_path):
    import json

    p = tmp_path / "weird.json"
    p.write_text(json.dumps({"venue": "x", "count": 3}), encoding="utf-8")
    assert DataLoader(cache=False).load_trades(p) == []
