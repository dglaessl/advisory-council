"""Download daily Coinbase candles for the backtest universe.
Usage: python3 -I backtest/fetch_history.py [START_DATE]   (default 2022-06-01)
Saves backtest/data/<SYM>.json as [time, low, high, open, close, volume] rows, oldest first."""
import json, os, sys, time, datetime as dt, urllib.request

UNIVERSE = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "XLM", "BCH", "LTC", "DOT",
            "SUI", "HBAR", "SHIB", "NEAR", "AAVE", "UNI"]
DAY = 86400
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(out, exist_ok=True)
start = dt.datetime.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2022-06-01").replace(tzinfo=dt.timezone.utc)
end = dt.datetime.now(dt.timezone.utc)

for sym in UNIVERSE:
    rows, t0 = {}, start
    while t0 < end:
        t1 = min(t0 + dt.timedelta(days=299), end)
        url = (f"https://api.exchange.coinbase.com/products/{sym}-USD/candles?granularity={DAY}"
               f"&start={t0.strftime('%Y-%m-%dT%H:%M:%SZ')}&end={t1.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        req = urllib.request.Request(url, headers={"User-Agent": "rh-agent-backtest"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = json.load(r)
                break
            except Exception as e:
                if attempt == 2:
                    print(f"{sym} {t0.date()} failed: {e}"); data = []
                time.sleep(1.5)
        if isinstance(data, list):
            for row in data:
                if isinstance(row, list) and len(row) == 6:
                    rows[int(row[0])] = [float(x) for x in row]
        t0 = t1
        time.sleep(0.25)
    series = [rows[k] for k in sorted(rows)]
    json.dump(series, open(os.path.join(out, sym + ".json"), "w"))
    first = dt.datetime.fromtimestamp(series[0][0], dt.timezone.utc).date() if series else None
    print(f"{sym}: {len(series)} days from {first}")
