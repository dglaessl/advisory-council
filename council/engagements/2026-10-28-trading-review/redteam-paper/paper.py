"""Prototype paper-lab engine (stdlib, no network). Deterministic, idempotent, per-day.
Candle rows: {date: (open, high, low, close, vol)} per symbol, from data/daily/*.json (completed days only).
Rule: signal on completed day D-1 (close), fill at open of D, cost S per side, same for every strategy.
State: state/paper/<name>.json  {last_date, cash, qty{}, stops{}, units, unit_peak, flows[], fees, trades[]}
Deposits come from ONE shared file state/paper/deposits.json [[date, amount]], split by core share, so all strategies
get identical cash. Core sleeve = BTC bought at open; trading sleeve = strategy-controlled.
"""
import json, sys, datetime as dt
from pathlib import Path
S = 0.0095; CORE_SHARE = 0.25; COLLAR = 0.05

def new_state(cash0=0.0):
    return dict(last_date=None, cash=cash0, qty={}, stops={}, core=0.0, fees=0.0, units=1.0, unit_peak=1.0,
                mdd=0.0, prev_value=cash0, flows=[], trades=[], curve=[])

def value(st, px):  # net liquidation (exit cost included), same convention as lab
    return st['cash'] + sum(q * px[s] * (1 - S) for s, q in st['qty'].items()) + st['core'] * px['BTC'] * (1 - S)

def step(st, day, bars, deposit, strategy):
    """Process ONE completed day `day` (fills at its open, uses signals from data < day). Idempotent: skips if done."""
    if st['last_date'] and str(day) <= st['last_date']:
        return st
    op = {s: b[day][0] for s, b in bars.items() if day in b}
    lo = {s: b[day][2] for s, b in bars.items() if day in b}
    cl = {s: b[day][3] for s, b in bars.items() if day in b}
    flow = deposit
    if flow:  # identical for all strategies: core share buys BTC at open, rest to trading cash
        st['core'] += flow * CORE_SHARE * (1 - S) / op['BTC']; st['fees'] += flow * CORE_SHARE * S
        st['cash'] += flow * (1 - CORE_SHARE); st['flows'].append([str(day), flow])
    for s in list(st['qty']):  # stops: gap at open, collar, then intraday
        stop = st['stops'].get(s)
        if stop is None or s not in op: continue
        px = None
        if op[s] <= stop:  px = op[s] if op[s] >= stop * (1 - COLLAR) else None  # collar: gap too deep -> unfilled
        elif lo[s] <= stop: px = stop
        if px: _sell(st, s, st['qty'][s], px, day, 'stop')
    hist = {s: {d: v for d, v in b.items() if d < day} for s, b in bars.items()}  # NO lookahead
    for act in strategy(hist, st, day):  # ('buy', sym, dollars, stop) | ('sell', sym, frac)
        if act[0] == 'sell' and act[1] in st['qty']:
            _sell(st, act[1], st['qty'][act[1]] * act[2], op[act[1]], day, 'signal')
        elif act[0] == 'buy' and act[1] in op:
            amt = min(act[2], st['cash'])
            if amt >= 10:
                st['cash'] -= amt; st['fees'] += amt * S
                st['qty'][act[1]] = st['qty'].get(act[1], 0) + amt * (1 - S) / op[act[1]]
                st['stops'][act[1]] = act[3]; st['trades'].append([str(day), 'buy', act[1], op[act[1]], amt])
    v = value(st, cl)
    st['units'] *= v / (st['prev_value'] + flow) if st['prev_value'] + flow else 1  # unit value: deposit-neutral
    st['unit_peak'] = max(st['unit_peak'], st['units']); st['mdd'] = min(st['mdd'], st['units'] / st['unit_peak'] - 1)
    st['prev_value'] = v; st['last_date'] = str(day); st['curve'].append([str(day), v, st['units']])
    return st

def _sell(st, s, qty, px, day, why):
    st['cash'] += qty * px * (1 - S); st['fees'] += qty * px * S; st['qty'][s] -= qty
    if st['qty'][s] < 1e-12: del st['qty'][s]; st['stops'].pop(s, None)
    st['trades'].append([str(day), 'sell', s, px, qty * px, why])

def catch_up(path, bars, deposits, strategy, days):
    """Restart-safe: replays every missing completed day in order; days already processed are skipped."""
    path = Path(path); st = json.loads(path.read_text()) if path.exists() else new_state()
    done = dt.date.fromisoformat(st['last_date']) if st['last_date'] else None
    for d in days:
        if done and d <= done: continue
        st = step(st, d, bars, deposits.get(str(d), 0.0), strategy)
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(st)); tmp.replace(path)  # atomic
    return st

def hold_btc(hist, st, day): return [('buy', 'BTC', st['cash'], 0.0)] if st['cash'] > 10 else []
def idle(hist, st, day): return []

if __name__ == '__main__':  # synthetic self-test only
    import random, tempfile
    random.seed(1); d0 = dt.date(2026, 1, 1); days = [d0 + dt.timedelta(i) for i in range(120)]
    bars = {}
    for s in ('BTC', 'ETH'):
        p = 100.0; bars[s] = {}
        for d in days:
            o = p; p *= 1 + random.gauss(0, .03); bars[s][d] = (o, max(o, p) * 1.01, min(o, p) * .99, p, 1.0)
    dep = {str(d): 200.0 for d in days[::7]}
    t = Path(tempfile.mkdtemp())
    a = catch_up(t / 'a.json', bars, dep, hold_btc, days)
    b = catch_up(t / 'b.json', bars, dep, hold_btc, days[:50]); b = catch_up(t / 'b.json', bars, dep, hold_btc, days)  # missed days, then restart
    c = catch_up(t / 'a.json', bars, dep, hold_btc, days)  # re-run: no-op
    assert a['curve'] == b['curve'] == c['curve'], 'restart/idempotency broken'
    i = catch_up(t / 'i.json', bars, dep, idle, days)
    assert abs(i['units'] - 1) < 0.25 and i['cash'] > 0
    print('PASS idempotent+restart; deposit-neutral units; units(hold)=%.3f mdd=%.3f fees=%.2f' % (a['units'], a['mdd'], a['fees']))
