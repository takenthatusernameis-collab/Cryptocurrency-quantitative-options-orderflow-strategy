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
