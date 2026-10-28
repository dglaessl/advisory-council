"""Re-derive the hold-BTC benchmark and attribute the equity-vs-benchmark gap.
Inputs are the numbers in council/engagements/2026-10-28-trading-review/BRIEF.md and journal.md (no network).
Run: python3 -I benchmark_check.py
"""
P = 81287.0                       # BTC mark, brief
# (usd, btc_price_at_arrival) cash deposits and in-kind, as listed in journal.md line 6
cash = [(250,81471),(100,81474),(200,82197),(5.97,82306),(262.52,81333),(100,81622),(200,80341.75)]
units_cash = sum(u/p for u,p in cash)
units = units_cash + 0.006829 + 586.02/82306 + 1.30/82306
dep = sum(u for u,_ in cash) + 554.66 + 586.02 + 1.30
bench = units*P
equity = 2232.23
print(f"deposits ${dep:,.2f}  (brief 2,260.47)")
print(f"bench units {units:.8f} BTC -> ${bench:,.2f}  (brief 2,252.38)  gap {equity-bench:,.2f} ({(equity/bench-1)*100:.2f}%)")
print(f"bench pays no spread; a real buy of the ${sum(u for u,_ in cash):,.0f} cash at +0.93%% would cost ~${sum(u for u,_ in cash)*0.0093/1.0093:,.1f}")
print(f"mark-to-bid: equity 2215.88 vs bench*(1-0.0095)={bench*(1-0.0095):,.2f} -> gap {2215.88-bench*(1-0.0095):,.2f}")

# attribution (approximate: marks/fills from brief + journal)
eth_mark = 39.71/0.016814
eth_leg = 0.242172*eth_mark - (586.02/82306)*P            # in-kind ETH converted to BTC in the benchmark
core_spread = -405.50*0.0093/1.0093                        # core BTC market fills ~0.93% over mark
lots_cost = 118.01+41+40.50
lot_spread = -lots_cost*0.0095/1.0095
near_total = -7.50
near_vs_btc = near_total + 49.98*(1-81000/81500)        # BTC fell ~0.6% over the hold, so bench lost ~$0.31 too
near_spread = -49.98*0.0095
parts = {"ETH core leg vs BTC (in-kind, owner's choice)": eth_leg,
         "Core BTC buy spread (6 market fills)": core_spread,
         "Trading lots entry spread (BTC/ETH/SOL)": lot_spread,
         "NEAR realized loss, net of BTC drift": near_vs_btc,
         }
tot = equity-bench
for k,v in parts.items(): print(f"{k:55s} {v:8.2f}")
print(f"{'Residual (lot price moves, cash timing, rounding)':55s} {tot-sum(parts.values()):8.2f}")
print(f"{'TOTAL gap':55s} {tot:8.2f}")
print("\nCleaner views of the same data:")
trading_in = 1118.49 - 405.50 + 1.30
print(f"Active-trading P&L vs idle cash: trading equity 703.34 - capital in {trading_in:,.2f} = {703.34-trading_in:,.2f} "
      f"({(703.34/trading_in-1)*100:.2f}%) -> NEAR -7.50, open lots {196.03-lots_cost:,.2f}")
print(f"Gap ex-ETH leg (passive twin: owner's ETH stays ETH): {tot-eth_leg:,.2f}")
print(f"Gap ex-ETH leg and ex-unavoidable buy spread: {tot-eth_leg-core_spread-lot_spread:,.2f}")
print(f"$21.24 misclassification: spread cost ~${21.24*0.0097:,.2f}; P&L effect ~0, process effect = 3% of trading capital moved to untouchable core")
