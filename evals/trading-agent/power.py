"""What can a short/small sample say? Sample-size and noise arithmetic (no network).
Run: python3 -I power.py
"""
import math, random
random.seed(1)
# 1) Noise in equity-vs-benchmark gap over 11 days (portfolio ~88% BTC/ETH, ~32% trading side).
# ETH/BTC relative daily sd ~1% on 26% weight; alt-type lots ~3% sd on ~7% weight (ASSUMED; observed step sd of the journal gap is ~0.25pp); BTC lots track benchmark.
d = math.sqrt((0.26*0.01)**2 + (0.07*0.03)**2)
print(f"daily tracking-error sd ~{d*100:.2f}%  -> 11-day sd ~{d*math.sqrt(11)*100:.2f}%  (observed gap -0.89%)")
print(f"=> gap/sd(11d) ~ {-0.89/(d*math.sqrt(11)*100):.1f} sigma: not distinguishable from zero skill")
print(f"3-month (92d) tracking sd ~{d*math.sqrt(92)*100:.1f}%  vs the 5% OWNER REVIEW trigger")
# 2) Trades needed to see an edge. R-multiple per trade: sd ~1.6R (stops + half-at-target + trail), win rate ~35-40%.
for edge in (0.1,0.2,0.3,0.5):
    n = ((1.96+0.84)*1.6/edge)**2
    print(f"mean edge {edge:.1f}R after costs -> ~{n:,.0f} trades for 80% power (two-sided 5%)")
# 3) Probability of seeing zero entries in 9 days if signal rate is lam per year
for lam in (6,12,24,48):
    print(f"expected {lam}/yr entries -> P(0 in 9 days) = {math.exp(-lam*9/365):.2f}; expected by 2027-01-13 (86d from 10-19): {lam*86/365:.1f}")
# 4) Bootstrap: with n trades, 90% CI width of mean R (sd 1.6)
for n in (5,10,20,50):
    print(f"n={n}: 90% CI half-width on mean R = +/-{1.645*1.6/math.sqrt(n):.2f}R")
