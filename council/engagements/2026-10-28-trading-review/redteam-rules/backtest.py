"""Backtest of the CLAUDE.md trading rules on daily Coinbase candles.

Usage: python3 -I backtest/backtest.py [--start 2023-01-01] [--end YYYY-MM-DD] [--capital 1000]
                                       [--weekly 0] [--spread 0.0095] [--trades]

Model (one cycle per day, run on the just-completed daily candle):
  * Orders fill at that day's close, with `spread` charged per side (0.0095 ~ market-maker routing).
  * Stop orders rest between cycles: if the next day's open is at/below the stop, fill at the open (gap),
    else if its low reaches the stop, fill at the stop.
  * Entries (coins above their 200d average only):
      - breakout: close above the prior 20-day high on volume >= 1.5x its 20-day average
      - pullback: close below the 20d average, within 4% of the 30-day low, support not broken on heavy volume
    stop  = lower of (support - 1%) and (entry - 1.5 x ATR14); skip if more than 20% away
    target = nearest of the 60/180/365-day highs that is >= entry + 8%; if none (blue sky), entry + 3 x risk
    require target >= entry + 8% and reward >= 2.5 x risk; rank by rs30 vs BTC, then rs7
    size = 2% of equity at risk, capped by 50% position / 25% speculative limits and available cash
  * Management: at target sell half; at +8% move stop to cost + 1%; then trail the stop to just below the
    lower of the 20d average and the 10-day low; stops only move up.
  * BTC trend filter: below its 200d average, no new speculative buys and speculative holdings are trimmed
    to 10% after 3 days.
  * Cash limit 10% with a 3-day grace period, waived while BTC is below its 200d average; on the deadline,
    fall back to the best top-20 coin above its 200d average with reward >= 1.5 x risk.
  * Max 3 agent trades per cycle (stop fills don't count). Min order $10.
  * Circuit breaker at -30% from peak: no buys for 30 days (stand-in for owner review), then peak resets.
  * Core (--core, --core-eth, --core-dep): untraded BTC (and ETH) held apart; trading equity excludes it.
  * BTC cap (--btc-cap X --cap-mode M), measured on total BTC (core + trading) vs total equity:
      soft-cash  above the cap, the core share of a deposit stays as trading cash (only the part that fits buys BTC)
      soft-eth   same, but the diverted part buys core ETH
      trading    no new trading BTC position beyond the cap; the core keeps buying
      hard       soft-cash + trading, and each cycle core BTC is sold back to the cap once it is
                 --cap-band (2 points) over it; proceeds become trading cash
Simplifications: no additions to existing positions, one entry per coin at a time, universe fixed to coins
that are large today (survivorship bias: this flatters altcoin results)."""
import argparse, datetime as dt, json, math, os

DIR = os.path.dirname(os.path.abspath(__file__))
TOP20 = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "XLM", "BCH", "LTC", "DOT", "SUI", "HBAR", "SHIB"]
SPEC = ["NEAR", "AAVE", "UNI"]
DAY = 86400

p = argparse.ArgumentParser()
p.add_argument("--start", default="2023-01-01")
p.add_argument("--end", default=None)
p.add_argument("--capital", type=float, default=1000)
p.add_argument("--weekly", type=float, default=0)
p.add_argument("--spread", type=float, default=0.0095)
p.add_argument("--trades", action="store_true", help="print every closed trade")
p.add_argument("--setups", default="breakout,pullback", help="entry setups to allow")
p.add_argument("--no-cash-limit", action="store_true", help="disable the 10%% cash limit and its fallback buys")
p.add_argument("--cash-to-btc", action="store_true", help="on the cash-limit deadline, park excess cash in BTC (sold to fund new trades) instead of forced trades")
p.add_argument("--risk", type=float, default=0.02, help="fraction of trading equity risked per new position")
p.add_argument("--spec-cap", type=float, default=0.25, help="max speculative share of trading equity")
p.add_argument("--max-pos", type=float, default=0.50, help="max single position share of trading equity")
p.add_argument("--breakout-days", type=int, default=20, help="breakout = close above the prior N-day high")
p.add_argument("--exit", default="trail", choices=["trail", "low"], help="trail = breakeven at +8%% then trail below min(20d avg, 10d low); low = trail at the N-day low from entry")
p.add_argument("--exit-days", type=int, default=20, help="N for --exit low")
p.add_argument("--no-targets", action="store_true", help="don't sell half at the target")
p.add_argument("--pyramid", type=int, default=0, help="max extra tranches added to a winner")
p.add_argument("--pyr-step", type=float, default=1.0, help="add when close >= last buy + step x entry ATR")
p.add_argument("--pyr-size", type=float, default=0.5, help="added tranche size as a fraction of the first buy")
p.add_argument("--core", type=float, default=0, help="fraction of capital and deposits held as untraded BTC core; rules trade the rest")
p.add_argument("--core-dep", type=float, default=None, help="fraction of each deposit bought as core BTC (default: same as --core)")
p.add_argument("--core-eth", type=float, default=0, help="fraction of the starting core held as untraded ETH instead of BTC")
p.add_argument("--btc-cap", type=float, default=0, help="max BTC share of total equity, core + trading (0 = no cap)")
p.add_argument("--cap-mode", default="soft-cash", choices=["soft-cash", "soft-eth", "trading", "hard"],
               help="soft-cash/soft-eth: above the cap the core share of a deposit stays as trading cash / buys core ETH; "
                    "trading: no new trading BTC above the cap; hard: soft-cash + trading + sell core BTC back to the cap")
p.add_argument("--cap-band", type=float, default=0.02, help="hard cap: trim only when BTC share exceeds the cap by this much")
p.add_argument("--json", action="store_true", help="print one JSON line of results instead of the report")
a = p.parse_args()
DEP_CORE = a.core if a.core_dep is None else a.core_dep

def day_of(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()

# ---------- data & indicators ----------
raw = {s: json.load(open(os.path.join(DIR, "data", s + ".json"))) for s in TOP20 + SPEC}
days = sorted({day_of(r[0]) for r in raw["BTC"]})
idx = {d: i for i, d in enumerate(days)}
N = len(days)

def series(rows):
    o = [None]*N; h = [None]*N; l = [None]*N; c = [None]*N; v = [None]*N
    for r in rows:
        i = idx.get(day_of(r[0]))
        if i is not None:
            l[i], h[i], o[i], c[i], v[i] = r[1], r[2], r[3], r[4], r[5]
    return o, h, l, c, v

def window(arr, i, n):
    w = arr[max(0, i-n+1):i+1]
    return w if len(w) == n and None not in w else None

D = {}
for s in TOP20 + SPEC:
    o, h, l, c, v = series(raw[s])
    ind = []
    atr = None; trs = []
    ag = al = None; gains = []
    for i in range(N):
        x = {}
        if c[i] is None:
            ind.append(None); atr = None; trs = []; ag = al = None; gains = []; continue
        # ATR14 (Wilder)
        if i > 0 and c[i-1] is not None:
            tr = max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1]))
            if atr is None:
                trs.append(tr)
                if len(trs) == 14: atr = sum(trs)/14
            else:
                atr = (atr*13 + tr)/14
        # RSI14 (Wilder)
        if i > 0 and c[i-1] is not None:
            ch = c[i]-c[i-1]
            if ag is None:
                gains.append(ch)
                if len(gains) == 14:
                    ag = sum(max(g, 0) for g in gains)/14; al = sum(max(-g, 0) for g in gains)/14
            else:
                ag = (ag*13 + max(ch, 0))/14; al = (al*13 + max(-ch, 0))/14
        w200 = window(c, i, 200); w20 = window(c, i, 20)
        prev20h = window(h, i-1, a.breakout_days) if i > 0 else None
        prev20v = window(v, i-1, 20) if i > 0 else None
        lo30 = window(l, i, 30); lo10 = window(l, i, 10); lon = window(l, i, a.exit_days)
        if None in (w200, w20, prev20h, prev20v, lo30, lon, atr) or i < 30 or c[i-30] is None or c[i-7] is None:
            ind.append(None); continue
        x.update(o=o[i], h=h[i], l=l[i], c=c[i], atr=atr, ma20=sum(w20)/20, ma200=sum(w200)/200,
                 hi20=max(prev20h), volx=v[i]/(sum(prev20v)/20 or 1), lo30=min(lo30), lo10=min(lo10), lon=min(lon),
                 r7=c[i]/c[i-7]-1, r30=c[i]/c[i-30]-1,
                 res=[max(w) for w in (window(h, i, 60), window(h, i, 180), window(h, i, 365)) if w])
        ind.append(x)
    D[s] = (o, h, l, c, ind)

# ---------- simulation ----------
S = a.spread
start_i = idx[dt.date.fromisoformat(a.start)] if dt.date.fromisoformat(a.start) in idx else 0
end_i = idx[dt.date.fromisoformat(a.end)] if a.end and dt.date.fromisoformat(a.end) in idx else N-1
cash = a.capital
pos = {}          # sym -> dict(qty, cost, stop, target, risk_usd, scaled, trailing, entry_day, kind, invested)
closed = []       # finished trades
equity_hist = []  # (date, equity, flow)
bench_btc = a.capital*(1-S)/D["BTC"][3][start_i]
bench_hist = []
peak = a.capital; pause_until = -1; over_since = None; spec_over_since = None
spread_paid = 0.0; contributions = a.capital; breaker_hits = 0
invested_frac = []
core_btc = 0.0   # untraded BTC: the fixed core (--core) or parked cash (--cash-to-btc)
core_eth = 0.0   # untraded ETH in the core (--core-eth, or deposits diverted by --cap-mode soft-eth)
cap_stats = dict(diverted=0.0, trims=0, trimmed=0.0, blocked_btc_buys=0, days_capped=0)
btc_share_hist = []
if a.core:
    btc_part, eth_part = a.core*(1-a.core_eth), a.core*a.core_eth
    core_btc = a.capital*btc_part*(1-S)/D["BTC"][3][start_i]
    core_eth = a.capital*eth_part*(1-S)/D["ETH"][3][start_i]
    spread_paid += a.capital*a.core*S; cash -= a.capital*a.core

def price(s, i): return D[s][3][i]
def ind(s, i): return D[s][4][i]

def equity_at(i):
    return (cash + core_btc*price("BTC", i) + core_eth*price("ETH", i)
            + sum(q["qty"]*price(s, i) for s, q in pos.items() if price(s, i) is not None))

def trade_eq(i):
    # equity the trading rules size against: a fixed core is excluded, parked BTC is not
    return equity_at(i) - ((core_btc*price("BTC", i) + core_eth*price("ETH", i)) if a.core else 0)

def btc_value(i):
    return core_btc*price("BTC", i) + (pos["BTC"]["qty"]*price("BTC", i) if "BTC" in pos else 0)

def btc_room(i):
    # dollars of BTC that can be added before BTC reaches the cap (inf when there is no cap)
    return max(0.0, a.btc_cap*equity_at(i) - btc_value(i)) if a.btc_cap else float("inf")

def sell(s, qty, px, i, why):
    global cash, spread_paid
    q = pos[s]
    proceeds = qty*px*(1-S); spread_paid += qty*px*S
    cash += proceeds
    q["realized"] += proceeds; q["qty"] -= qty
    if q["qty"] <= 1e-12:
        pnl = q["realized"] - q["invested"]
        closed.append(dict(sym=s, kind=q["kind"], entry=days[q["entry_day"]], exit=days[i], why=why,
                           pnl=pnl, r=pnl/q["risk_usd"] if q["risk_usd"] else 0, invested=q["invested"]))
        del pos[s]

def plan(s, i, rr_min, require_setup=True):
    x = ind(s, i)
    if not x or x["c"] <= x["ma200"]: return None
    c = x["c"]
    breakout = c > x["hi20"] and x["volx"] >= 1.5
    pullback = c < x["ma20"] and c <= x["lo30"]*1.04 and not (c < x["lo30"]*1.0001 and x["volx"] >= 1.5)
    allowed = a.setups.split(",")
    breakout = breakout and "breakout" in allowed; pullback = pullback and "pullback" in allowed
    if require_setup and not (breakout or pullback): return None
    support = x["hi20"] if breakout else x["lo30"]
    stop = min(support*0.99, c - 1.5*x["atr"])
    risk = c - stop
    if risk <= 0 or risk/c > 0.20: return None
    above = [r for r in x["res"] if r >= c*1.08]
    target = min(above) if above else c + 3*risk
    if target < c*1.08 or (target-c) < rr_min*risk: return None
    b = D["BTC"][4][i]
    return dict(sym=s, stop=stop, target=target, risk_pct=risk/c, kind="breakout" if breakout else ("pullback" if pullback else "fallback"),
                rank=(x["r30"]-b["r30"], x["r7"]-b["r7"]))

def buy(pl, i, budget, eq):
    global cash, spread_paid, core_btc
    s = pl["sym"]; c = price(s, i)
    available = cash + (core_btc*price("BTC", i)*(1-S) if a.cash_to_btc else 0)
    notional = min(a.risk*eq/pl["risk_pct"], a.max_pos*eq, budget, available)
    if s == "BTC" and a.btc_cap and a.cap_mode in ("trading", "hard"):
        room = btc_room(i)
        if room < 10: cap_stats["blocked_btc_buys"] += 1
        notional = min(notional, room)
    if s in SPEC:
        spec_val = sum(q["qty"]*price(k, i) for k, q in pos.items() if k in SPEC)
        notional = min(notional, a.spec_cap*eq - spec_val)
    if notional < 10: return 0
    if notional > cash:  # fund the shortfall by selling parked BTC
        bp = price("BTC", i); q = min(core_btc, (notional - cash)/(bp*(1-S)))
        core_btc -= q; cash += q*bp*(1-S); spread_paid += q*bp*S
        notional = min(notional, cash)
    qty = notional*(1-S)/c; spread_paid += notional*S
    cash -= notional
    pos[s] = dict(qty=qty, cost=c/(1-S), stop=pl["stop"], target=pl["target"], risk_usd=qty*(c-pl["stop"]) + notional*S,
                  scaled=False, trailing=False, entry_day=i, kind=pl["kind"], invested=notional, realized=0.0,
                  n=ind(s, i)["atr"], last_buy=c, adds=0, first=notional)
    return notional

for i in range(start_i, end_i+1):
    flow = 0.0
    if a.weekly and i > start_i and (i-start_i) % 7 == 0:
        cash += a.weekly; contributions += a.weekly; flow = a.weekly
        amt = a.weekly*DEP_CORE
        if amt > 0:
            to_btc = amt
            if a.btc_cap and a.cap_mode in ("soft-cash", "soft-eth", "hard"):
                to_btc = min(amt, btc_room(i))
                if to_btc < 10: to_btc = 0.0
            rest = amt - to_btc
            core_btc += to_btc*(1-S)/price("BTC", i); spread_paid += to_btc*S; cash -= to_btc
            if rest > 0:
                cap_stats["diverted"] += rest
                if a.cap_mode == "soft-eth" and rest >= 10:
                    core_eth += rest*(1-S)/price("ETH", i); spread_paid += rest*S; cash -= rest
                # otherwise the diverted core share stays as trading cash
        bench_btc += a.weekly*(1-S)/price("BTC", i)
    # 1) resting stop orders during day i
    for s in list(pos):
        o, h, l, c, _ = D[s]
        if l[i] is None: continue
        q = pos[s]
        if o[i] <= q["stop"]: sell(s, q["qty"], o[i], i, "stop (gap)")
        elif l[i] <= q["stop"]: sell(s, q["qty"], q["stop"], i, "stop")
    # 2) cycle at the close of day i
    # hard BTC cap: sell core BTC back down to the cap (proceeds become trading cash)
    if a.btc_cap and a.cap_mode == "hard":
        e, bv, bp = equity_at(i), btc_value(i), price("BTC", i)
        if e > 0 and bv/e > a.btc_cap + a.cap_band and core_btc > 0:
            q = min(core_btc, (bv - a.btc_cap*e)/bp)
            if q*bp >= 10:
                core_btc -= q; cash += q*bp*(1-S); spread_paid += q*bp*S
                cap_stats["trims"] += 1; cap_stats["trimmed"] += q*bp
    eq = equity_at(i)
    peak = max(peak, eq)
    if eq <= 0.70*peak and i > pause_until:
        pause_until = i + 30; breaker_hits += 1
    if i == pause_until: peak = eq
    paused = i <= pause_until
    btc = ind("BTC", i); btc_up = btc is not None and btc["c"] > btc["ma200"]
    actions = 0
    teq = trade_eq(i)
    # manage positions
    for s in list(pos):
        q = pos[s]; x = ind(s, i)
        if not x: continue
        c = x["c"]
        if not a.no_targets and not q["scaled"] and c >= q["target"] and actions < 3:
            sell(s, q["qty"]/2, c, i, "target half"); actions += 1
            if s in pos:
                pos[s]["scaled"] = True; pos[s]["trailing"] = True
                if a.exit == "trail": pos[s]["stop"] = max(pos[s]["stop"], pos[s]["cost"]*1.01)
            continue
        if a.exit == "trail":
            if c >= q["cost"]*1.08 and not q["trailing"]:
                q["stop"] = max(q["stop"], q["cost"]*1.01); q["trailing"] = True
            if q["trailing"]:
                q["stop"] = max(q["stop"], min(x["ma20"], x["lo10"])*0.995)
        else:
            q["stop"] = max(q["stop"], x["lon"]*0.995)
        # add to a winner: +step x entry ATR above the last buy, within all limits
        if a.pyramid and q["adds"] < a.pyramid and not paused and actions < 3 and c >= q["last_buy"] + a.pyr_step*q["n"]:
            pos_val = q["qty"]*c
            add = min(q["first"]*a.pyr_size, a.max_pos*teq - pos_val, cash)
            if s in SPEC:
                add = min(add, a.spec_cap*teq - sum(z["qty"]*price(k, i) for k, z in pos.items() if k in SPEC))
            if add >= 10:
                new_stop = max(q["stop"], c - 1.5*q["n"])
                aq = add*(1-S)/c; spread_paid += add*S; cash -= add
                q["cost"] = (q["cost"]*q["qty"] + (c/(1-S))*aq)/(q["qty"] + aq)
                q["qty"] += aq; q["invested"] += add; q["risk_usd"] += aq*max(c - new_stop, 0) + add*S
                q["stop"] = new_stop; q["last_buy"] = c; q["adds"] += 1; actions += 1
    # BTC trend filter: trim speculative to 10% after 3 days
    spec_val = sum(q["qty"]*price(k, i) for k, q in pos.items() if k in SPEC)
    if not btc_up and spec_val > 0.10*teq:
        spec_over_since = i if spec_over_since is None else spec_over_since
        if i - spec_over_since >= 2:
            for s in sorted([k for k in pos if k in SPEC], key=lambda k: ind(k, i)["r30"] if ind(k, i) else -9):
                if actions >= 3 or spec_val <= 0.10*teq: break
                excess = spec_val - 0.10*teq; val = pos[s]["qty"]*price(s, i)
                qty = pos[s]["qty"] if val <= excess + 10 else pos[s]["qty"]*excess/val
                sell(s, qty, price(s, i), i, "trend-filter trim"); actions += 1
                spec_val = sum(q["qty"]*price(k, i) for k, q in pos.items() if k in SPEC)
    else:
        spec_over_since = None
    # entries
    eq = trade_eq(i)
    if not paused:
        universe = [s for s in TOP20 + SPEC if s not in pos and (btc_up or s not in SPEC)]
        plans = [pl for pl in (plan(s, i, 2.5) for s in universe) if pl]
        for pl in sorted(plans, key=lambda z: z["rank"], reverse=True):
            if actions >= 3: break
            if buy(pl, i, float("inf"), eq): actions += 1
        # cash limit with 3-day grace, waived when BTC is below its 200d average
        eq = trade_eq(i)
        if btc_up and cash > 0.10*eq and not a.no_cash_limit:
            over_since = i if over_since is None else over_since
            if i - over_since >= 2 and a.cash_to_btc:
                excess = cash - 0.10*eq
                if excess >= 10:
                    core_btc += excess*(1-S)/price("BTC", i); spread_paid += excess*S; cash -= excess
            elif i - over_since >= 2:
                fb = [pl for pl in (plan(s, i, 1.5, require_setup=False) for s in TOP20 if s not in pos) if pl]
                for pl in sorted(fb, key=lambda z: z["rank"], reverse=True):
                    excess = cash - 0.10*trade_eq(i)
                    if actions >= 3 or excess < 10: break
                    if buy(pl, i, excess, trade_eq(i)): actions += 1
        else:
            over_since = None
    equity_hist.append((days[i], equity_at(i), flow))
    share = btc_value(i)/equity_at(i) if equity_at(i) > 0 else 0
    btc_share_hist.append(share)
    if a.btc_cap and share >= a.btc_cap - 0.005: cap_stats["days_capped"] += 1
    invested_frac.append(1 - cash/equity_at(i) if equity_at(i) > 0 else 0)
    bench_hist.append((days[i], bench_btc*price("BTC", i), flow))

# ---------- report ----------
def stats(hist):
    idxv = [1.0]; rets = []
    for k in range(1, len(hist)):
        prev, (d, e, f) = hist[k-1][1], hist[k]
        r = (e - f)/prev - 1 if prev > 0 else 0
        rets.append(r); idxv.append(idxv[-1]*(1+r))
    yrs = (hist[-1][0]-hist[0][0]).days/365.25
    cagr = idxv[-1]**(1/yrs)-1 if yrs > 0 else 0
    pk, mdd = 1, 0
    for v in idxv:
        pk = max(pk, v); mdd = min(mdd, v/pk-1)
    mu = sum(rets)/len(rets); sd = math.sqrt(sum((r-mu)**2 for r in rets)/len(rets))
    return dict(final=hist[-1][1], twr=idxv[-1]-1, cagr=cagr, mdd=mdd, sharpe=mu/sd*math.sqrt(365) if sd else 0, idx=idxv)

st, bt = stats(equity_hist), stats(bench_hist)
if a.json:
    print(json.dumps(dict(
        start=str(days[start_i]), end=str(days[end_i]), contributions=contributions,
        final=st["final"], cagr=st["cagr"], mdd=st["mdd"], sharpe=st["sharpe"],
        bench_final=bt["final"], bench_cagr=bt["cagr"], bench_mdd=bt["mdd"], bench_sharpe=bt["sharpe"],
        btc_share_avg=sum(btc_share_hist)/len(btc_share_hist), btc_share_max=max(btc_share_hist),
        btc_share_end=btc_share_hist[-1], spread_paid=spread_paid, trades=len(closed),
        days=len(btc_share_hist), **cap_stats)))
    raise SystemExit
print(f"Period {days[start_i]} to {days[end_i]} | capital ${a.capital:,.0f} | weekly ${a.weekly:,.0f} | "
      f"spread {S*100:.2f}% per side | contributions ${contributions:,.0f}")
print(f"exit {a.exit}{a.exit_days if a.exit == 'low' else ''}{' no targets' if a.no_targets else ''} | pyramid {a.pyramid} | setups {a.setups} | cash limit {'off' if a.no_cash_limit else ('excess to BTC' if a.cash_to_btc else 'forced trades')} | "
      f"BTC core {a.core:.0%}")
print(f"{'':22}{'Strategy':>12}{'Hold BTC':>12}")
for k, lab, fmt in [("final", "Final value", "${:,.0f}"), ("twr", "Total return", "{:+.1%}"), ("cagr", "Annual return", "{:+.1%}"),
                    ("mdd", "Max drawdown", "{:.1%}"), ("sharpe", "Sharpe ratio", "{:.2f}")]:
    print(f"{lab:22}{fmt.format(st[k]):>12}{fmt.format(bt[k]):>12}")
years = sorted({d.year for d, _, _ in equity_hist})
print("\nBy calendar year (time-weighted return):")
for y in years:
    ks = [k for k, (d, _, _) in enumerate(equity_hist) if d.year == y]
    k0, k1 = max(ks[0]-1, 0), ks[-1]
    print(f"  {y}: strategy {st['idx'][k1]/st['idx'][k0]-1:+7.1%}   hold BTC {bt['idx'][k1]/bt['idx'][k0]-1:+7.1%}")
wins = [t for t in closed if t["pnl"] > 0]
n = len(closed)
print(f"\nClosed trades: {n} | win rate {len(wins)/n:.0%} | avg result {sum(t['r'] for t in closed)/n:+.2f}R | "
      f"best {max(t['r'] for t in closed):+.1f}R | worst {min(t['r'] for t in closed):+.1f}R" if n else "\nClosed trades: 0")
for kind in ("breakout", "pullback", "fallback"):
    ts = [t for t in closed if t["kind"] == kind]
    if ts:
        print(f"  {kind:9}: {len(ts):3} trades, win rate {sum(t['pnl'] > 0 for t in ts)/len(ts):.0%}, "
              f"avg {sum(t['r'] for t in ts)/len(ts):+.2f}R, P&L ${sum(t['pnl'] for t in ts):+,.0f}")
print(f"Spread paid: ${spread_paid:,.0f} | avg invested {sum(invested_frac)/len(invested_frac):.0%} | "
      f"circuit breaker trips: {breaker_hits} | open positions at end: {len(pos)}")
if a.trades:
    for t in closed:
        print(f"  {t['entry']} -> {t['exit']} {t['sym']:5} {t['kind']:9} {t['why']:17} ${t['pnl']:+8.2f} {t['r']:+5.2f}R")
