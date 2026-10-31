"""Numbers for the 2026-11-01 crypto trading-agent briefing (council/meetings/2026-11-01-briefings/1-crypto.md).
Offline and read-only: inputs are values copied from robinhood-agent-cloud/journal.md (State + cycle log, as of the
2026-10-31 00:25 UTC cycle) plus `git log` commit times. No broker tool is called.
Run: python3 -I briefing_2026-11-01.py [/home/claude/robinhood-agent-cloud]
"""
import re, subprocess, sys, datetime as dt
REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/robinhood-agent-cloud"
J = open(f"{REPO}/journal.md").read()

# ---- State as of 2026-10-31 cycle (journal State block) ----
equity, cash, crypto = 2147.14, 692.47, 1454.67
peak = 2228.08
dep_total, dep_cash, dep_inkind = 2260.47, 1118.49, 554.66 + 586.02 + 1.30
btc_mark, eth_mark = 77270.0, 2244.61
core_btc, core_eth = 0.011772, 0.242172
core_val = core_btc * btc_mark + core_eth * eth_mark
te = equity - 1453.20                 # journal's trading equity (core 1453.20)
print("== 1. performance")
print(f"deposits {dep_total:.2f} (cash {dep_cash:.2f} + in-kind {dep_inkind:.2f}); equity {equity:.2f}; net {equity-dep_total:+.2f} ({(equity/dep_total-1)*100:+.2f}%)")
print(f"core value recomputed {core_val:.2f} (journal 1453.20); cash share of equity {cash/equity*100:.1f}%; sleeve cash share {cash/te*100:.1f}%")
print(f"circuit breaker level {peak*0.7:.2f}; equity is {(1-equity/peak)*100:.1f}% below peak; further fall to trip {(1-peak*0.7/equity)*100:.1f}%")

# hold-BTC benchmark (B1) from the journal's listed purchases
cashdep = [(250,81471),(100,81474),(200,82197),(5.97,82306),(262.52,81333),(100,81622),(200,80341.75)]
u_cash = sum(u/p for u,p in cashdep)
b1_units = u_cash + 0.006829 + 586.02/82306 + 1.30/82306
b1 = b1_units * btc_mark
print(f"B1 hold-BTC units {b1_units:.8f} (journal 0.02770879) -> {b1:.2f}; equity - B1 = {equity-b1:+.2f} ({(equity/b1-1)*100:+.2f}%)")
prem = 0.0093
spread_on_cash = sum(u for u,_ in cashdep) * prem/(1+prem) * (btc_mark/ (sum(u for u,_ in cashdep)/u_cash))/ (sum(u for u,_ in cashdep)/u_cash) if False else None
# B2: same 0.93% buy premium on the cash deposits (units bought = usd/(price*(1+prem)))
b2_units = sum(u/(p*(1+prem)) for u,p in cashdep) + 0.006829 + 586.02/82306 + 1.30/82306
b2 = b2_units*btc_mark
print(f"B2 hold-BTC with 0.93% buy premium on cash deposits: {b2:.2f}; equity - B2 = {equity-b2:+.2f} ({(equity/b2-1)*100:+.2f}%)")

# B3 passive twin per prereg_2027-01-13.yaml: in-kind BTC/ETH/XRP held as is; each cash deposit 50% BTC, 50% idle cash
xrp_val = 1.47                                   # journal-implied (crypto - core); State text says ~1.22
def twin(p):
    btc = 0.006829 + sum(0.5*u/(p_*(1+p)) for u,p_ in cashdep)
    idle = 0.5*sum(u for u,_ in cashdep)
    return btc*btc_mark + core_eth*eth_mark + xrp_val + idle
for lab, p in (("frictionless", 0.0), ("0.93% buy premium", prem)):
    t = twin(p); print(f"B3 passive twin ({lab}): {t:.2f}; equity - B3 = {equity-t:+.2f} ({(equity/t-1)*100:+.2f}%)")
# actual-core twin: the core exactly as bought, every other cash dollar idle -> isolates the active sleeve
core_buys = [100.01, 134.25, 50.00, 21.24, 100.00]    # 10-19, 10-20, 10-23, 10-24 (mistake), 10-26
cb = sum(core_buys)
twin_act = 1453.20 + (dep_cash - cb) + xrp_val
print(f"core BTC bought {cb:.2f}; actual-core twin {twin_act:.2f}; equity - twin = {equity-twin_act:+.2f}")
cap_in = dep_cash - cb + 1.30
print(f"trading capital in {cap_in:.2f}; trading equity {te:.2f}; sleeve P&L {te-cap_in:+.2f} ({(te/cap_in-1)*100:+.2f}%)")

print("\n== closed trades (cost = qty*fill; proceeds from stop fills)")
trades = [("NEAR 10-24", 10*4.998, 10*4.2488),
          ("SOL  10-29", 0.38647*104.79, 0.38647*97.007),
          ("ETH  10-29", 0.016814*2438.38, 0.016814*2249.81),
          ("BTC  10-29a", 0.0012159*82241.13, 0.0012159*77493.51),
          ("BTC  10-29b", 0.00021892*82225.31, 0.00021892*77490.99)]
tot = 0; so = 0
for n,c,p in trades:
    tot += p-c
    if n != trades[0][0]: so += p-c
    print(f"{n:12s} cost {c:7.2f} proceeds {p:7.2f} pnl {p-c:+6.2f} ({(p/c-1)*100:+5.1f}%)")
print(f"four stop-outs {so:+.2f}; all five closed trades {tot:+.2f}  (journal 10-30 entry says ~-26 for the four: not reproduced)")
print(f"win rate 0/5; avg {(tot/5):+.2f}$ per trade")

print("\n== spread paid")
core_fills = [("2026-10-19 11:47","core BTC",0.00120529,82967.62,82196.78),
              ("2026-10-20 13:09","core BTC",0.00163534,82087.72,81333.01),
              ("2026-10-23 12:55","core BTC",0.00060704,82366.75,81622.22),
              ("2026-10-24 14:55","core BTC",0.00026222,80998.80,80218.65),
              ("2026-10-26 10:55","core BTC",0.00123311,81095.36,80341.75)]
pr = []; dollars = 0
for ts, k, q, fill, mark in core_fills:
    d = fill/mark-1; pr.append(d*100); dollars += q*(fill-mark)
    print(f"{ts} {k:9s} qty {q:.8f} fill {fill:10.2f} mark {mark:10.2f}  {d*100:+.2f}%  ${q*(fill-mark):.2f}")
m = sum(pr)/len(pr); sd = (sum((x-m)**2 for x in pr)/(len(pr)-1))**0.5
print(f"core buys (n={len(pr)}): mean {m:+.3f}%  sd {sd:.3f}  min {min(pr):+.2f}  max {max(pr):+.2f}; measured premium ${dollars:.2f}")
entry_cost = 0.0094*(199.51+49.98); exit_val = 42.488+186.49
print(f"est. entry premium on 10-17 trading buys (mark not logged; assume 0.94%): ${entry_cost:.2f}")
print(f"est. exit spread on stop sells (~0.95% below mark on ${exit_val:.2f}): ${0.0095*exit_val:.2f}")
print(f"total est. spread paid ${dollars+entry_cost+0.0095*exit_val:.2f} (measured part ${dollars:.2f})")
for x in (1.0, 1.2, 1.5, 2.0):
    print(f"guard x={x}%: would have skipped {sum(p>x for p in pr)} of {len(pr)} logged fills")
print("stop exits vs trigger: " + ", ".join(f"{n} {(f/t-1)*100:+.3f}%" for n,f,t in
      [("NEAR",4.2488,4.25),("SOL",97.007,97),("ETH",2249.81,2250),("BTCa",77493.51,77500),("BTCb",77490.99,77500)]))
# R:R sensitivity to entry premium: setup at exactly R:R 2.5 (stop 12% below, target 30% above plan entry 100)
for extra in (0, 0.5, 1.0, 1.5):
    e = 100*(1+extra/100); stop, tgt = 88.0, 130.0
    print(f"extra ask premium {extra:.1f}pp: R:R {(tgt-e)/(e-stop):.2f} (min 2.5)")

print("\n== heat cap geometry (live formula): max size as % of trading equity for one position")
for sd_ in (0.08, 0.12, 0.15, 0.20):
    f = 1.01-0.95*(1-sd_)
    print(f"stop {sd_*100:.0f}% below entry: heat per $ {f:.3f}; 4%-risk size {4/ (sd_*100)*100:.0f}% of TE; 8%-heat size {8/(f*100)*100:.0f}% of TE")
bt = {"hold BTC":(51.0,23.3,-9.1),"4%/8% heat (live)":(39.0,23.7,-1.0),"4%/12%":(47.2,30.3,0.3),"4%/16%":(49.1,32.5,0.5),"4%/no cap":(64.1,48.6,1.9)}
live = bt["4%/8% heat (live)"]; nocap = bt["4%/no cap"]; hold = bt["hold BTC"]
print("RESULTS.md 2026-10-30 table (model output, not re-run):")
print("  live minus no-cap (pts/yr, starts 2023/24/25):", [round(a-b,1) for a,b in zip(live,nocap)])
print("  live minus hold BTC:", [round(a-b,1) for a,b in zip(live,hold)])

print("\n== operations")
heads = re.findall(r"^### (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC", J, re.M)
since = [h for h in heads if h[0] >= "2026-10-28"]
print(f"cycle entries in log: {len(heads)}; since 10-28: {len(since)}: {since}")
print(f"entries with brk=Y signals: {len(re.findall(r'brk=Y: (?!none)', J))} (Signals lines present: {len(re.findall('Signals: brk=Y', J))})")
print(f"entries with a Heat line: {len(re.findall(r'Heat: ', J))}; UNRESOLVED mentions as live state: {len(re.findall(r'UNRESOLVED <|UNRESOLVED [0-9a-f]{8}', J))}")
log = subprocess.run(["git","-C",REPO,"log","--since=2026-10-28","--format=%h|%aI|%s","--reverse"],capture_output=True,text=True).stdout.splitlines()
commits = [l.split("|",2) for l in log]
for h,t,s in commits:
    if s.startswith("cycle") or s.startswith("lock"):
        print(f"  {h} {t} {s}")
# journal header time vs real commit time
for h,t,s in commits:
    mm = re.match(r"cycle (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC", s)
    if mm:
        claimed = dt.datetime.fromisoformat(f"{mm.group(1)}T{mm.group(2)}:00+00:00")
        real = dt.datetime.fromisoformat(t).astimezone(dt.timezone.utc)
        print(f"  {h}: log/watermark time {mm.group(2)}Z vs commit {real:%H:%M:%S}Z -> watermark ahead by {(claimed-real).total_seconds()/60:+.1f} min")
lock = {}
for h,t,s in commits:
    mm = re.match(r"lock (\S+)", s)
    if mm: lock[h]=dt.datetime.fromisoformat(t)
ks = [(h,dt.datetime.fromisoformat(t),s) for h,t,s in commits]
for i,(h,t,s) in enumerate(ks):
    if s.startswith("lock") and i+1 < len(ks) and ks[i+1][2].startswith("cycle"):
        print(f"  lock {h} -> release/cycle commit {ks[i+1][0]}: {(ks[i+1][1]-t).total_seconds():.0f} s")
print("weekday of 2027-01-09:", dt.date(2027,1,9).strftime("%A"), "| 2027-01-13:", dt.date(2027,1,13).strftime("%A"),
      "| next Monday deposit date:", dt.date(2026,11,2).strftime("%A"))
print("paper-lab: day 1 if 11-15 + 60 days =", dt.date(2026,11,15)+dt.timedelta(days=60), "; day 1 11-01 + 60 =", dt.date(2026,11,1)+dt.timedelta(days=60))
print("NAV: account", round(equity/2138.51,4), "| sleeve", round(te/693.94,4))
