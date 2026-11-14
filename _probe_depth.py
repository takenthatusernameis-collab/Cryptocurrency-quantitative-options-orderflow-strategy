import requests, time
from src.data.public_export_acquisition import _bar_count

s = requests.Session()
url = "https://www.okx.com/api/v5/market/history-trades"
after = "485524306"
trades = []
t0 = time.time()
for i in range(2500):
    try:
        r = s.get(url, params={"instId": "BTC-USD-SWAP", "limit": "100", "after": after}, timeout=20)
        d = r.json()
        rows = d.get("data") or []
        if not rows:
            print("empty at page", i)
            break
        after = str(rows[-1].get("tradeId"))
        for row in rows:
            trades.append({"ts": int(row.get("ts")), "id": str(row.get("tradeId"))})
    except Exception as e:
        print("ERR", i, e)
        break
trades.sort(key=lambda x: x["ts"])
print("pages", i + 1, "n", len(trades), "elapsed", round(time.time() - t0, 1))
print("oldest", trades[0]["ts"], "newest", trades[-1]["ts"])
print("span_h", round((trades[-1]["ts"] - trades[0]["ts"]) / 3600000, 2))
print("bars@15s", _bar_count([{"timestamp_ms": t["ts"]} for t in trades], 15))