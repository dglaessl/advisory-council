"""Numeric check of the draft unit-NAV rules (CLAUDE.md "Unit tracking") and heat cap.
Run: python3 -I units_check.py   (stdlib only; no network)
Rule implemented literally: NAV_before = (value - flow)/units ; units += flow/NAV_before ; NAV = value/units.
"""
class Ledger:
    def __init__(s, value):
        s.u = value; s.nav = 1.0; s.peak = 1.0
    def cycle(s, value, flow=0.0):
        if flow:
            nb = (value - flow) / s.u
            s.u += flow / nb
        s.nav = value / s.u
        s.peak = max(s.peak, s.nav)
        return s.nav, s.peak, s.nav / s.peak - 1
def show(tag, r): print(f"{tag:58s} NAV {r[0]:.4f} peak {r[1]:.4f} dd {r[2]*100:+.2f}%")
fails = []
def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok: fails.append(name)

# T1 init at current State values (account 2228.08, sleeve 702.82)
A = Ledger(2228.08); S = Ledger(702.82)
# T2 deposit alone: $200 arrives, core buy $50 at mark (no slippage), markets flat
r = A.cycle(2228.08 + 200, 200); show("T2 account, $200 deposit, flat market", r)
check("T2 account NAV unchanged by deposit", abs(r[0] - 1) < 1e-9)
r = S.cycle(702.82 + 150, 150); show("T2 sleeve, flow 150, flat", r)
check("T2 sleeve NAV unchanged by deposit", abs(r[0] - 1) < 1e-9)
# T3 loss same cycle as deposit: trading book -5% (702.82 -> 667.68), core flat, deposit 200 (core 50)
A = Ledger(2228.08); S = Ledger(702.82)
loss = -0.05 * 702.82
r = A.cycle(2228.08 + loss + 200, 200); show("T3 account, -$35.14 trading loss + $200 deposit", r)
check("T3 account NAV shows the loss (<1)", r[0] < 1)
r = S.cycle(702.82 + loss + 150, 150); show("T3 sleeve, same", r)
check("T3 sleeve NAV = -5.00%", abs(r[0] - 0.95) < 1e-9)
# T4 in-kind ETH $586 to core: account flow 586, sleeve flow 0
A = Ledger(2228.08); S = Ledger(702.82)
r = A.cycle(2228.08 + 586, 586); check("T4 in-kind: account NAV unchanged", abs(r[0] - 1) < 1e-9)
r = S.cycle(702.82, 0); check("T4 in-kind: sleeve NAV unchanged (flow 0)", abs(r[0] - 1) < 1e-9)
# T5 UNBOOKED deposit (Check A -> owner action) then booked 3 cycles later; market flat
A = Ledger(2228.08)
r1 = A.cycle(2228.08 + 100, 0); show("T5 cycle N: $100 unbooked cash in equity, flow 0", r1)
r2 = A.cycle(2228.08 + 100, 100); show("T5 cycle N+3: booked ($100 flow), market flat", r2)
check("T5 NAV spike on unbooked deposit stays out of peak (EXPECT FAIL)", A.peak < 1.0001)
print(f"   -> phantom drawdown left after booking: {r2[2]*100:+.2f}% (true performance 0.00%)")
# T6 first cycle contains an unbooked deposit, init uses value incl. cash, booked later
A = Ledger(2228.08 + 100)
r = A.cycle(2228.08 + 100, 100); show("T6 init incl. unbooked $100, then booked", r)
check("T6 init with unbooked cash then booking keeps NAV=1 (EXPECT FAIL)", abs(r[0] - 1) < 1e-6)
# T7 sleeve double counting of owed core: deposit cycle under NO_NEW_ENTRIES
S = Ledger(702.82)
r = S.cycle(702.82 + 200, 200)   # literal: flow = 200 - core bought (0) = 200
show("T7 sleeve, NO_NEW_ENTRIES deposit, flow 200", r)
r = S.cycle(702.82 + 200 - 50, -50); show("T7 later cycle pays owed $50 core, flow -50", r)
check("T7 owed-core path nets to NAV 1 when applied once", abs(r[0] - 1) < 1e-9)
S = Ledger(702.82)
r = S.cycle(702.82 + 200, 150)   # NO_NEW_ENTRIES: cash 200 sits in trading equity, LLM wrongly nets the owed 50
show("T7b sleeve, flow wrongly 150 when owed core not yet bought", r)
check("T7b netting owed core in deposit cycle keeps NAV=1 (EXPECT FAIL)", abs(r[0] - 1) < 1e-6)
# T8 slippage on core buy hits sleeve
S = Ledger(702.82); r = S.cycle(702.82 + 150 - 0.45, 150); show("T8 sleeve: $50 core buy 0.9% above mark", r)

# Heat (cap 8% of trading equity 702.82). Marks approx from journal: BTC 81149 ETH 2353.60 SOL 102.0
print("\n-- heat --")
TE = 702.82
pos = [("BTC", 0.00143482, 81149, 77500), ("ETH", 0.016814, 2353.60, 2250), ("SOL", 0.38647, 102.0, 97.0)]
h = 0
for n, q, m, st in pos:
    x = q * (m - 0.95 * st); h += x; print(f"{n} heat {x:.2f}")
h += 1.30; print(f"XRP dust (no stop) 1.30 ; total {h:.2f} = {h/TE*100:.2f}% of TE ; cap {0.08*TE:.2f}")
def size(entry, stop, ask=None):
    e = ask or entry
    risk_sz = 0.04 * TE / ((e - stop) / e)
    f = 1.01 - 0.95 * stop / e
    head = 0.08 * TE - h
    heat_sz = head / f
    return risk_sz, f, risk_sz * f, heat_sz, min(risk_sz, heat_sz, 0.5 * TE, 505.98)
# Scenario 5: entry 100, stop 90 (10% away)
r, f, hn, hs, fin = size(100, 90)
print(f"S5 stop -10%: risk-size {r:.2f}, heat factor {f:.3f}, heat of that size {hn:.2f}, heat-cap size {hs:.2f}, final {fin:.2f}")
print(f"   total heat after: {h+fin*f:.2f} = {(h+fin*f)/TE*100:.2f}%")
# tight stop 5% away: risk-size vs 50% cap
r, f, hn, hs, fin = size(100, 95)
print(f"   stop -5%: risk-size {r:.2f}, factor {f:.3f}, heat-cap size {hs:.2f}, final {fin:.2f}")
# Scenario 6: entry 100 target 125 stop 90 -> RR 2.5 ; ask 101.5
for ask in (100, 100.5, 101.5):
    rew, rk = 125 - ask, ask - 90
    print(f"S6 ask {ask}: reward {rew:.2f} risk {rk:.2f} RR {rew/rk:.2f} -> {'ok' if rew/rk>=2.5 and rew/ask>=0.08 else 'SKIP'}")
# negative-heat edge: mark below 0.95*stop
print("edge: BTC mark 73000 with stop 77500 -> heat term", round(0.00143482*(73000-0.95*77500),4), "(negative, no floor in text)")
print("\nFAILS (by design where marked EXPECT FAIL):", len(fails))
