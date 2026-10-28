"""Corrected simplified rule comparison, NOT exact replication of supplied engine.
Only public local candle files are read. All output remains beside this file.
Initial/core deposits execute at open. Prior completed signals execute next open.
Existing gap stops precede decisions; intraday lows follow decisions. Entry gap
revalidates risk/reward. All marks are net liquidation; costs use source haircuts.
No pyramids, fallback buys, BTC concentration caps or cross-sleeve transfers.
"""
import contextlib
import datetime as dt
import io
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
S = .0095
DAY = 86400
SPEC = {'NEAR', 'AAVE', 'UNI'}

def load_indicators():
    # Execute only inspected data/indicator prefix; never the source simulator.
    text = (ROOT / 'backtest.reference.py').read_text()
    prefix = text.split('# ---------- simulation ----------')[0]
    old = sys.argv
    sys.argv = [str(ROOT / 'backtest.reference.py'), '--breakout-days', '55']
    ns = {'__file__': str(ROOT / 'backtest.reference.py'), '__name__': 'lab_indicators'}
    try:
        exec(compile(prefix, 'audited_indicator_prefix', 'exec'), ns)
    finally:
        sys.argv = old
    return ns


def metric(hist, flows, capital):
    prev = capital
    unit = peak = 1.0
    dd = 0.0
    for date, value, flow in hist:
        unit *= value / (prev + flow)
        peak = max(peak, unit)
        dd = min(dd, unit / peak - 1)
        prev = value
    final = hist[-1][1]
    t0 = hist[0][0]
    terminal = hist[-1][0] + dt.timedelta(days=1)
    yrs = (terminal - t0).days / 365.25
    cashflows = [(t0, -capital)] + [(d, -f) for d, f in flows] + [(terminal, final)]
    def npv(rate):
        return sum(v / (1 + rate)**((d-t0).days/365.25) for d, v in cashflows)
    lo, hi = -.9999, 100.0
    if npv(lo) * npv(hi) > 0:
        irr = None
    else:
        for _ in range(120):
            mid = (lo+hi)/2
            if npv(mid) > 0:
                lo = mid
            else:
                hi = mid
        irr = (lo+hi)/2
    return dict(final=final, contributions=capital+sum(f for _, f in flows),
                profit=final-capital-sum(f for _, f in flows), twr=unit-1,
                cagr=unit**(1/yrs)-1, mdd=dd, xirr=irr)


def simulate(ns, start, end, mode, cap=.25, weekly=0, core_filter=False, capital=1000, trace=False):
    days, idx, D = ns['days'], ns['idx'], ns['D']
    start, end = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    assert start in idx and end in idx and idx[start] >= 200 and start < end
    i0, i1 = idx[start], idx[end]
    assert all((days[i]-days[i-1]).days == 1 for i in range(1, len(days)))
    cash = capital if mode == 'hold' else capital*.5
    corecash = 0.0 if mode == 'hold' else capital*.5
    core = 0.0
    positions = {}
    fees = 0.0
    buys = sells = 0
    hist, flows, events = [], [], []
    unit = peak = 1.0
    pause_until = -1
    last_teq = cash
    over_since = None

    def price(s, i, field=3):
        p = D[s][field][i]
        assert p is not None and p > 0, (s, days[i], field)
        return p

    def ind(s, j):
        return D[s][4][j] if j >= 0 else None

    def trade_value(i, field):
        return cash + sum(q['qty']*price(s, i, field)*(1-S) for s, q in positions.items())

    def sell(s, fraction, px, i, reason):
        nonlocal cash, fees, sells
        q = positions[s]
        qty = q['qty']*fraction
        cash += qty*px*(1-S)
        fees += qty*px*S
        q['qty'] -= qty
        sells += 1
        if trace: events.append([str(days[i]), 'sell', s, px, reason])
        if fraction == 1: del positions[s]

    for i in range(i0, i1+1):
        j = i-1
        flow = weekly if i > i0 and (i-i0) % 7 == 0 else 0
        if flow:
            flows.append((days[i], flow))
            if mode == 'hold': corecash += flow
            else: corecash += flow*.5; cash += flow*.5
        btc = ind('BTC', j)
        up = btc is not None and btc['c'] > btc['ma200']
        # Core-only 200d filter, DAILY signals, no stops/breaker on core.
        # Hold comparator invests all starting cash through this same mechanism.
        if mode == 'hold' and i == i0:
            corecash += cash; cash = 0.0
        if core_filter and not up and core:
            gross = core*price('BTC', i, 0)
            corecash += gross*(1-S); fees += gross*S; core = 0.0; sells += 1
        if (not core_filter or up) and corecash:
            core += corecash*(1-S)/price('BTC', i, 0)
            fees += corecash*S; buys += 1; corecash = 0.0
        # Existing resting gap stops, before open-time discretionary actions.
        for s in list(positions):
            if price(s, i, 0) <= positions[s]['stop']:
                sell(s, 1, price(s, i, 0), i, 'gap stop')
        actions = 0
        for s in list(positions):
            q, x = positions[s], ind(s, j)
            if not x: continue
            if not q['scaled'] and x['c'] >= q['target'] and actions < 3:
                sell(s, .5, price(s, i, 0), i, 'prior-close target')
                q['scaled'] = q['trailing'] = True
                q['stop'] = max(q['stop'], q['cost']*1.01)
                actions += 1
                continue
            if x['c'] >= q['cost']*1.08:
                q['trailing'] = True
                q['stop'] = max(q['stop'], q['cost']*1.01)
            if q['trailing']:
                q['stop'] = max(q['stop'], min(x['ma20'], x['lo10'])*.995)
        teq = trade_value(i, 0)
        specval = sum(q['qty']*price(s, i, 0) for s, q in positions.items() if s in SPEC)
        if not up and specval > .10*teq:
            over_since = i if over_since is None else over_since
            if i-over_since >= 2:
                for s in sorted([s for s in positions if s in SPEC], key=lambda s: ind(s, j)['r30']):
                    if actions >= 3 or specval <= .10*teq: break
                    val = positions[s]['qty']*price(s, i, 0)
                    fraction = min(1, (specval-.10*teq)/val)
                    sell(s, fraction, price(s, i, 0), i, 'BTC trend trim')
                    specval -= val*fraction; actions += 1
        else: over_since = None
        # Breaker uses prior close unitized trading-sleeve equity, not cash deposits.
        plans = []
        if mode == 'active' and i > pause_until:
            for s in D:
                x = ind(s, j)
                if s in positions or not x or (s in SPEC and not up): continue
                if x['c'] <= x['ma200'] or x['c'] <= x['hi20'] or x['volx'] < 1.5: continue
                stop = min(x['hi20']*.99, x['c']-1.5*x['atr'])
                risk = x['c']-stop
                resistance = [r for r in x['res'] if r >= x['c']*1.08]
                target = min(resistance) if resistance else x['c']+3*risk
                if not 0 < risk/x['c'] <= .20 or target < x['c']*1.08 or target-x['c'] < 2.5*risk: continue
                plans.append((x['r30']-btc['r30'], x['r7']-btc['r7'], s, stop, target))
            eq = trade_value(i, 0)
            for _, _, s, stop, target in sorted(plans, reverse=True):
                if actions >= 3: break
                px = price(s, i, 0)
                risk = px-stop
                if not 0 < risk/px <= .20 or target < px*1.08 or target-px < 2.5*risk: continue
                amt = min(.04*eq/(risk/px), .50*eq, cash)
                if s in SPEC:
                    specval = sum(q['qty']*price(k, i, 0) for k, q in positions.items() if k in SPEC)
                    amt = min(amt, cap*eq-specval)
                if amt < 10: continue
                positions[s] = dict(qty=amt*(1-S)/px, stop=stop, target=target, cost=px/(1-S), scaled=False, trailing=False)
                cash -= amt; fees += amt*S; buys += 1; actions += 1
                if trace: events.append([str(days[i]), 'buy', s, px, str(days[j])])
        # Newly established/raised stops are valid for this day, including new entries.
        for s in list(positions):
            stop = positions[s]['stop']
            if price(s, i, 0) <= stop: sell(s, 1, price(s, i, 0), i, 'new stop marketable')
            elif price(s, i, 2) <= stop: sell(s, 1, stop, i, 'intraday stop')
        teq = trade_value(i, 3)
        trading_flow = flow*.5 if mode != 'hold' else 0
        if mode != 'hold':
            unit *= teq/(last_teq+trading_flow)
            peak = max(peak, unit)
            if i == pause_until: peak = unit
            elif unit <= .70*peak and i > pause_until: pause_until = i+30
        last_teq = teq
        value = teq + corecash + core*price('BTC', i, 3)*(1-S)
        hist.append((days[i], value, flow))
        assert cash >= -1e-8 and corecash >= -1e-8
    result = metric(hist, flows, capital)
    result.update(start=str(start), end=str(end), mode=mode, spec_cap=cap if mode=='active' else None,
                  weekly=weekly, core_filter=core_filter, paid_costs=fees, buys=buys, sells=sells,
                  terminal_exit_cost=sum(q['qty']*price(s, i1, 3)*S for s, q in positions.items())+core*price('BTC', i1, 3)*S)
    return result, hist, events


def checks(ns):
    # Independent flat-price/cashflow arithmetic checks, including inception costs.
    d = dt.date(2023,1,1)
    h = [(d,1000,0),(d+dt.timedelta(days=1),1200,200)]
    m = metric(h,[(h[-1][0],200)],1000)
    assert abs(m['twr']) < 1e-12 and abs(m['profit']) < 1e-12 and abs(m['xirr']) < 1e-12
    m = metric([(d,1000*(1-S)**2,0)],[],1000)
    assert abs(m['twr']-((1-S)**2-1)) < 1e-12
    # Closed form passive twins independently derived from candle opens/closes.
    for weekly in (0,200):
        for mode, frac in [('hold',1),('cash',.5)]:
            r,h,_ = simulate(ns,'2023-01-01','2023-12-31',mode,weekly=weekly)
            i0,i1=ns['idx'][dt.date(2023,1,1)],ns['idx'][dt.date(2023,12,31)]
            op,_,_,cl,_=ns['D']['BTC']
            units=1000*frac*(1-S)/op[i0]
            count=0
            for i in range(i0+7,i1+1,7): units+=weekly*frac*(1-S)/op[i]; count+=1
            expected=(1000+count*weekly)*(1-frac)+units*cl[i1]*(1-S)
            assert abs(r['final']-expected)<1e-7, (r,expected)
    # Causal prefix invariance: changing today's close/high/volume must not alter today's buys.
    date='2024-03-01'; i=ns['idx'][dt.date.fromisoformat(date)]
    _,_,before=simulate(ns,'2024-01-01',date,'active',trace=True)
    saved={s:(v[1][i],v[3][i],v[4][i]) for s,v in ns['D'].items()}
    try:
        for s,v in ns['D'].items():
            if v[3][i] is not None:
                v[1][i]*=2; v[3][i]*=1.5; v[4][i]=None
        _,_,after=simulate(ns,'2024-01-01',date,'active',trace=True)
        assert before==after
    finally:
        for s,(hi,cl,ind) in saved.items(): ns['D'][s][1][i]=hi; ns['D'][s][3][i]=cl; ns['D'][s][4][i]=ind
    _,_,events=simulate(ns,'2023-01-01','2026-10-27','active',trace=True)
    entries=[e for e in events if e[1]=='buy']
    assert len(entries)>20
    for date,_,sym,px,signal in entries:
        assert (dt.date.fromisoformat(date)-dt.date.fromisoformat(signal)).days==1
        assert px==ns['D'][sym][0][ns['idx'][dt.date.fromisoformat(date)]]
    try:
        simulate(ns,'2020-01-01','2026-10-27','cash')
    except AssertionError:
        pass
    else:
        raise AssertionError('missing date was accepted')
    # Independent core-filter ledger, no trading positions, including weekly cashflows.
    cash,qty=500.0,0.0
    i0=ns['idx'][dt.date(2023,1,1)]; i1=ns['idx'][dt.date(2026,10,27)]
    deposits=0
    for i in range(i0,i1+1):
        if i>i0 and (i-i0)%7==0: cash+=100; deposits+=1
        closes=ns['D']['BTC'][3][i-200:i]
        bullish=closes[-1]>sum(closes)/200
        px=ns['D']['BTC'][0][i]
        if bullish and cash: qty+=cash*(1-S)/px; cash=0.0
        elif not bullish and qty: cash+=qty*px*(1-S); qty=0.0
    expected=500+100*deposits+cash+qty*ns['D']['BTC'][3][i1]*(1-S)
    result,_,_=simulate(ns,'2023-01-01','2026-10-27','cash',weekly=200,core_filter=True)
    assert abs(result['final']-expected)<1e-7
    print('PASS: deposit neutrality, inception round-trip costs, four passive closed forms, causal prefix invariance,',len(entries),'next-open entries, absent-date rejection, independent core-filter ledger')


if __name__ == '__main__':
    ns=load_indicators()
    checks(ns)
    results=[]
    for weekly in (0,200):
        for year in (2022,2023,2024,2025,2026):
            for mode,cap,filt in [('cash',.25,False),('hold',.25,False),('active',.10,False),('active',.25,False),('active',.50,False),('cash',.25,True)]:
                r,h,_=simulate(ns,f'{year}-01-01','2026-10-27',mode,cap,weekly,filt)
                results.append(r)
    (ROOT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('wrote',len(results),'comparisons')
