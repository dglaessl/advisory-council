"""Trend-core and momentum-rotation strategies on daily Coinbase candles.

Usage: python3 -I backtest/rotation.py [--start 2023-01-01] [--spread 0.0095] [--capital 1000]

Strategies (all spot, no leverage, weekly decisions at the daily close, `spread` charged per side):
  trend    BTC only: hold BTC while its close is above its 200-day average, otherwise cash.
  rotN     Momentum rotation: every 7 days, if BTC is above its 200d average, rank coins that are above their
           own 200d average by 0.5 x 30-day return + 0.5 x 90-day return and hold the top N. Holdings that drop
           out of the top N (or below their 200d) are sold; new entrants get an equal share of equity, funded
           from cash. Winners are not trimmed. BTC below its 200d average: sell everything to cash.
           Speculative coins (NEAR, AAVE, UNI) are capped at `spec_cap` of equity.
  combo    50% trend + 50% rot3, run as separate sleeves (no rebalancing between them).
Protections in every strategy: a resting trailing stop 25% below each position's highest close since entry
(checked against the daily low; gaps fill at the open), and a circuit breaker (equity 30% below peak ->
sell everything and make no buys for 30 days, then reset the peak).
Survivorship bias: the universe is today's large coins, which flatters rotation results."""
import argparse, datetime as dt, json, math, os

DIR = os.path.dirname(os.path.abspath(__file__))
TOP20 = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "XLM", "BCH", "LTC", "DOT", "SUI", "HBAR", "SHIB"]
SPEC = ["NEAR", "AAVE", "UNI"]

p = argparse.ArgumentParser()
p.add_argument("--start", default="2023-01-01")
p.add_argument("--spread", type=float, default=0.0095)
p.add_argument("--capital", type=float, default=1000)
p.add_argument("--trail", type=float, default=0.25)
p.add_argument("--spec-cap", type=float, default=0.25)
p.add_argument("--breaker-pause-only", action="store_true", help="circuit breaker pauses buys without selling (like the live rule)")
p.add_argument("--log", type=int, default=0, help="print the first N trades of rot3")
a = p.parse_args()
S = a.spread

def day_of(ts): return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()
raw = {s: json.load(open(os.path.join(DIR, "data", s + ".json"))) for s in TOP20 + SPEC}
days = sorted({day_of(r[0]) for r in raw["BTC"]}); idx = {d: i for i, d in enumerate(days)}; N = len(days)
C, L, O = {}, {}, {}
for s, rows in raw.items():
    c = [None]*N; l = [None]*N; o = [None]*N
    for r in rows:
        i = idx.get(day_of(r[0]))
        if i is not None: l[i], o[i], c[i] = r[1], r[3], r[4]
    C[s], L[s], O[s] = c, l, o

def ma(s, i, n):
    w = C[s][i-n+1:i+1]
    return sum(w)/n if i >= n-1 and len(w) == n and None not in w else None

def ret(s, i, n):
    return C[s][i]/C[s][i-n]-1 if i >= n and C[s][i] and C[s][i-n] else None

def above200(s, i):
    m = ma(s, i, 200); return m is not None and C[s][i] > m

start_i = idx.get(dt.date.fromisoformat(a.start), 0)
log = []

def sim(universe, top_n):
    cash = a.capital; pos = {}  # sym -> [qty, highest close]
    log.clear(); i_now = [0]
    peak = a.capital; pause_until = -1; hist = []; spread_paid = 0.0; trades = 0
    def value(i): return cash + sum(q*C[s][i] for s, (q, _) in pos.items())
    def sell(s, px):
        nonlocal cash, spread_paid, trades
        q = pos.pop(s)[0]; cash += q*px*(1-S); spread_paid += q*px*S; trades += 1
        log.append((days[i_now[0]], 'SELL', s, round(px, 6), round(q*px, 2)))
    for k, i in enumerate(range(start_i, N)):
        i_now[0] = i
        for s in list(pos):  # resting trailing stops
            stop = pos[s][1]*(1-a.trail)
            if O[s][i] <= stop: sell(s, O[s][i])
            elif L[s][i] <= stop: sell(s, stop)
        for s in pos: pos[s][1] = max(pos[s][1], C[s][i])
        eq = value(i); peak = max(peak, eq)
        if eq <= 0.70*peak and i > pause_until:
            if not a.breaker_pause_only:
                for s in list(pos): sell(s, C[s][i])
            pause_until = i + 30
        if i == pause_until: peak = value(i)
        if k % 7 == 0 and i > pause_until:
            if not above200("BTC", i):
                for s in list(pos): sell(s, C[s][i])
            else:
                ranked = []
                for s in universe:
                    if C[s][i] is None or not above200(s, i): continue
                    r30, r90 = ret(s, i, 30), ret(s, i, 90)
                    if r30 is None or r90 is None: continue
                    ranked.append((0.5*r30 + 0.5*r90, s))
                target = [s for _, s in sorted(ranked, reverse=True)[:top_n]]
                for s in list(pos):
                    if s not in target: sell(s, C[s][i])
                eq = value(i)
                for s in target:
                    if s in pos: continue
                    spec_val = sum(q*C[k2][i] for k2, (q, _) in pos.items() if k2 in SPEC)
                    amt = min(eq/top_n, cash)
                    if s in SPEC: amt = min(amt, a.spec_cap*eq - spec_val)
                    if amt < 10: continue
                    pos[s] = [amt*(1-S)/C[s][i], C[s][i]]; cash -= amt; spread_paid += amt*S; trades += 1
                    log.append((days[i], 'BUY', s, round(C[s][i], 6), round(amt, 2)))
        hist.append((days[i], value(i)))
    return hist, spread_paid, trades

def stats(hist):
    v = [e for _, e in hist]; yrs = (hist[-1][0]-hist[0][0]).days/365.25
    rets = [v[k]/v[k-1]-1 for k in range(1, len(v))]
    mu = sum(rets)/len(rets); sd = math.sqrt(sum((r-mu)**2 for r in rets)/len(rets))
    pk, mdd = v[0], 0
    for x in v: pk = max(pk, x); mdd = min(mdd, x/pk-1)
    return (v[-1]/v[0])**(1/yrs)-1, mdd, mu/sd*math.sqrt(365) if sd else 0, v[-1]

hold = [(days[i], a.capital*(1-S)/C["BTC"][start_i]*C["BTC"][i]) for i in range(start_i, N)]
results = {"hold BTC": (hold, 0, 1)}
results["trend (BTC > 200d)"] = sim(["BTC"], 1)
for n in (2, 3, 5):
    results[f"rot{n} (top {n} momentum)"] = sim(TOP20 + SPEC, n)
t, r3 = results["trend (BTC > 200d)"][0], results["rot3 (top 3 momentum)"][0]
rot3_log = list(log) if False else None
results["combo (50% trend + 50% rot3)"] = ([(d, (e1 + e2)/2) for (d, e1), (_, e2) in zip(t, r3)], 0, 0)
print(f"{days[start_i]} to {days[-1]} | spread {S*100:.2f}% per side | trailing stop {a.trail:.0%}")
for name, (h, sp, tr) in results.items():
    cagr, mdd, sh, fin = stats(h)
    print(f"  {name:30} annual {cagr:+7.1%} | max drawdown {mdd:6.1%} | Sharpe {sh:5.2f} | final ${fin:,.0f}"
          + (f" | trades {tr}" if tr > 1 else ""))

if a.log:
    sim(TOP20 + SPEC, 3)
    for row in log[:a.log]: print(*row)
