# Backtest results (run 2026-10-18)

Daily Coinbase candles, 18 coins (15 large caps + NEAR, AAVE, UNI), $1,000 start, no deposits unless noted.
Spread is per side: 0.95% is about what market-maker routing has cost in the live account so far;
0.3% is a guess at exchange routing (not verified). Model details are in the docstring of `backtest.py`.

## Jan 2023 to Oct 2026 (annual return, max drawdown)

| Variant | Strategy | Hold BTC |
|---|---|---|
| Current rules, 0.95% spread | +9.4%, -57% | +51.9%, -53% |
| Current rules, 0.3% spread | +39.4%, -48% | +51.9%, -53% |
| Current rules, no costs | +42.1%, -43% | +51.9%, -53% |
| No cash-limit fallback, 0.95% | +14.8%, -44% | |
| Breakouts only, no cash limit, 0.95% | +25.6%, -37% | |
| Breakouts only, no cash limit, 0.3% | +36.0%, -30% (Sharpe 1.11 vs 1.13) | |
| Current rules + $100/week, 0.95% | $25.0k final vs $35.2k hold BTC | |

## Later start dates (annual return)

| Start | Current rules, 0.95% | Breakouts only, 0.95% | Breakouts only, 0.3% | Hold BTC |
|---|---|---|---|---|
| 2024-01-01 | +15.6% | +22.6% | +30.3% | +24.2% |
| 2025-01-01 | -22.3% | -5.2% | +3.8% | -8.1% |

## Findings
- The current rules lost badly to simply holding BTC in every period tested.
- Trading costs are the largest drag: the spread paid roughly equalled the starting capital.
- The cash-limit fallback (forced buys) and the pullback setup both lost money on their own.
- Breakout trades carried the edge. Breakouts only, with lower costs, beat holding BTC from 2024 and 2025
  starts with roughly half the drawdown, but trailed from the 2023 start (a BTC bear-market low).

## Caveats
Survivorship bias (today's large caps, which flatters altcoin trading). Fills at the daily close. No
additions to existing positions. The circuit breaker is modeled as a 30-day pause. A single 3.8-year
history, so tuning the rules to fit it risks overfitting.

## Options 2-4 (run 2026-10-18; annual return / max drawdown / Sharpe)

New flags: `--cash-to-btc` (option 2), `--setups breakout` (option 3), `--core 0.5` (option 4).

0.95% spread per side:

| Variant | From 2023 | From 2024 | From 2025 |
|---|---|---|---|
| A current rules | +9.4% / -57% / 0.42 | +15.6% / -57% / 0.55 | -22.3% / -52% / -0.54 |
| B opt2 excess cash to BTC | +4.4% / -65% / 0.33 | +1.9% / -65% / 0.28 | -28.3% / -64% / -0.55 |
| C opt3 breakouts only | +25.3% / -53% / 0.74 | +6.9% / -53% / 0.37 | -20.5% / -50% / -0.54 |
| D opt2+3 | +34.3% / -61% / 0.86 | +20.1% / -61% / 0.62 | -22.7% / -60% / -0.41 |
| E opt4 50% core, breakouts, no cash limit | +40.7% / -47% / 1.09 | +23.4% / -44% / 0.78 | -6.6% / -44% / -0.09 |
| F opt4 70% core, breakouts, no cash limit | +45.4% / -50% / 1.11 | +24.2% / -47% / 0.75 | -7.4% / -47% / -0.05 |
| G 50% core, breakouts, excess cash to BTC | +45.3% / -53% / 1.04 | +23.9% / -53% / 0.69 | -9.3% / -53% / -0.01 |
| Control: 50% BTC + 50% cash, no trading | +32.8% / -47% / 0.97 | +13.2% / -39% / 0.57 | -4.0% / -30% / -0.10 |
| Hold BTC | +51.9% / -53% / 1.13 | +24.2% / -53% / 0.69 | -8.1% / -53% / 0.02 |

0.3% spread per side: E = +46.5% / -45% / 1.22, +30.5% / -42% / 0.96, -2.0% / -42% / 0.07
(best Sharpe of all variants in every period; beats holding BTC from the 2024 and 2025 starts).

Findings:
- Option 2 on its own makes things worse: parking cash in BTC and selling it to fund trades adds spread
  churn and BTC drawdown on top of the trading losses.
- Option 3 helps, but inconsistently on its own (better from 2023, worse from 2024).
- Option 4 (50% BTC core, breakouts only, no cash limit) is the most consistent. It is close to holding BTC
  on return, with lower drawdowns, and its trading half adds about 8-10 points a year over the no-trading
  control in 2023 and 2024 (it lost ~2.6 points in 2025 at current costs).
- Adding the cash limit back on top of option 4 (G) didn't help and raised drawdowns.
- Differences of a few points between close variants (e.g. 50% vs 70% core) are within noise for one history.

## Aggressive variants and new strategies (run 2026-10-18; annual / max drawdown / Sharpe)

Breakouts only, no cash limit. New flags in backtest.py: `--risk`, `--spec-cap`, `--max-pos`.

| Variant | Spread | From 2023 | From 2024 | From 2025 |
|---|---|---|---|---|
| E current (50% core, 2% risk, spec 25%) | 0.95% | +40.7% / -47% / 1.09 | +23.4% / -44% / 0.78 | -6.6% / -44% / -0.09 |
| Aggressive (30% core, 4% risk, spec 50%) | 0.95% | +43.9% / -42% / 1.16 | +24.4% / -41% / 0.79 | -10.6% / -41% / -0.26 |
| E current | 0.3% | +46.5% / -45% / 1.22 | +30.5% / -42% / 0.96 | -2.0% / -42% / 0.07 |
| Aggressive | 0.3% | +58.9% / -40% / 1.43 | +38.2% / -39% / 1.09 | -4.8% / -41% / -0.04 |
| Hold BTC | either | +51.9% / -53% / 1.13 | +24.2% / -53% / 0.69 | -8.1% / -53% / 0.02 |

rotation.py (weekly, spot, 25-35% trailing stops, circuit breaker):
- Momentum rotation (top 2/3/5 coins by 30d+90d momentum): lost money in every period and setting tested
  (e.g. top 3 from 2024: -40% to -62% a year, drawdowns -75% to -93%). It buys after big run-ups and gets
  stopped out on the reversals. Dead end.
- BTC trend (hold BTC above its 200d average, else cash): +21-27% (2023 start), +7-17% (2024), -6% to +3%
  (2025), with drawdowns of -26% to -43%. Lower return than holding BTC in rising markets, smaller losses
  in falling ones. Not better than option E overall.

Findings: the aggressive variant beats holding BTC in all three periods only with ~0.3% costs (and with
smaller drawdowns); at current costs it is about even with E and slightly worse in the 2025 bear market.
More risk per trade helps in bull markets and hurts in bear markets. Survivorship bias matters more with a
50% speculative limit.

## 55-day breakouts (run 2026-10-18; annual / max drawdown, 0.95% spread unless noted)

| Variant | From 2023 | From 2024 | From 2025 |
|---|---|---|---|
| Aggressive (30% core, 4% risk, spec 50%), 20-day | +43.9% / -42% | +24.4% / -41% | -10.6% / -41% |
| Aggressive, 55-day | +58.9% / -36% | +46.4% / -34% | +2.8% / -35% |
| Live today (60% core, 2% risk, spec 25%), 20-day | +43.1% / -48% | +23.8% / -46% | -6.9% / -46% |
| 60% core, 2% risk, spec 25%, 55-day | +45.0% / -46% | +26.8% / -42% | -6.1% / -42% |
| 60% core, 4% risk, spec 50%, 55-day | +56.0% / -43% | +37.7% / -41% | -1.7% / -43% |
| Same, 0.3% spread | +67.5% / -40% | +49.2% / -38% | +2.6% / -42% |
| Hold BTC | +51.9% / -53% | +24.2% / -53% | -8.1% / -53% |

55-day beat 20-day in every variant, period and cost level. Breakout-length check (aggressive, 0.95%):
30d +45/+27/-8, 40d +43/+28/-7, 55d +59/+46/+3, 70d +49/+45/+2, 90d +27/+11/-12, 120d +29/+14/-10.
55-70 days is a plateau, but 40 and 90 are clearly worse, so part of the edge is luck in this history.
55 was chosen in advance (the classic "turtle" rule), not found by searching.

## Listing effect (listing_study.py, run 2026-10-18)

48 Robinhood-offered coins that started trading on Coinbase between mid-2022 and mid-2026. After a 1.9%
round trip, measured against BTC over the same window:

| Entry | Hold 7d | Hold 30d | Hold 90d |
|---|---|---|---|
| Close of listing day | median -10.0%, beat BTC 31% | median -20.7%, beat BTC 27% | median -20.2%, beat BTC 29% |
| Close of day 1 | median -11.9%, 25% | median -23.6%, 29% | median -23.3%, 31% |
| Close of day 7 | median -6.0%, 40% | median -19.7%, 25% | median -25.6%, 25% |

Means at 90 days are positive (+15% to +28%) only because a few coins went up many times over: a lottery
ticket profile, with the typical new listing losing 20%+ against BTC. A small Robinhood-date sample (PEPE,
PNUT, PENGU, POPCAT; dates partly uncertain) pointed the same way at 7 and 30 days.
Finding: buying new listings is a losing strategy. If anything, new listings should be avoided for their
first ~90 days.

## Exchange Routing check (2026-10-19)
Owner's actual rates: maker 0.5%, taker 0.95% (market-maker routing costs ~0.95% per side). Market and stop
orders save nothing; only resting limit orders that fill as maker save. Live setup (60% core, 55-day, 4% risk,
spec 50%): 0.95% -> +56/+38/-2%; ~0.84% (half the entries as maker) -> +58/+40/-1%; ~0.73% (all entries as
maker, best case) -> +59/+41/-1%. A gain of ~2-4 points a year, and taker fills (stops, fallbacks, the owner's
other account) cost slightly more. Decision: stay on market-maker routing. The earlier 0.3% assumption was too
optimistic.

## Exit rules and adding to winners (run 2026-10-19; live setup: 60% core, 55-day, 4% risk, spec 50%, 0.95%)
New flags: `--exit low --exit-days N`, `--no-targets`, `--pyramid N --pyr-step X --pyr-size Y`.

| Variant | From 2023 | From 2024 | From 2025 |
|---|---|---|---|
| Current exit (half at target, breakeven at +8%, trail min(20d avg, 10d low)) | +56.0% / -43% | +37.7% / -41% | -1.7% / -43% |
| 20-day low exit, keep half at target | +45.3% / -47% | +24.5% / -45% | -9.2% / -46% |
| 20-day low exit, no targets (classic turtle) | +42.6% / -49% | +18.1% / -47% | -10.4% / -46% |
| Current exit + add to winners (2 adds, +1 ATR, half size) | +49.2% / -44% | +22.6% / -44% | -4.3% / -42% |
| 20-day low, no targets + adds | +41.1% / -48% | +20.6% / -45% | -7.5% / -43% |
| Low exit, 10 / 30 / 40 days | +51 / +45 / +49% | +31 / +24 / +20% | -9 / -10 / -12% |
| Adds at 0.5 ATR, 2 ATR, or one full-size add | +42 / +43 / +46% | +21 / +18 / +19% | -8 / -4 / -4% |

Finding: both ideas are worse than the current exit in every period and every setting tried, with deeper
drawdowns. Crypto breakouts reverse sharply; the current rules bank half at the target and tighten the stop
early, while a looser N-day-low exit gives back more, and adds buy at higher prices just before reversals
(paying the spread again each time). Decision: keep the current exit, no adding to winners.

## BTC share caps (run 2026-10-23; annual return / max drawdown / highest BTC share of the account)
Question from the owner: should BTC (core + trading) be capped as a share of the whole account?
Model: the live setup (55-day breakouts only, 4% risk, speculative up to 50%, no cash limit, 0.95% spread),
with the core starting at 70% of capital (41% of it ETH, like today) and 50% of each deposit buying core BTC.
$1,000 + $100/week keeps today's ratio ($2k + $200/week). Data: Coinbase daily candles to 2026-10-22.
New flags in backtest.py: `--core-dep`, `--core-eth`, `--btc-cap`, `--cap-mode soft-cash|soft-eth|trading|hard`,
`--cap-band`, `--json`. Check: the earlier "60% core, 4% risk, spec 50%, 55-day" run reproduces
(+55.9% / -43% from 2023 vs +56.0% / -43% before).

With $100/week:

| Variant | Cap | From 2023 | From 2024 | From 2025 |
|---|---|---|---|---|
| No cap (today's rules) | | +59.2% / -39% / 77% | +40.6% / -40% / 75% | -2.7% / -42% / 73% |
| 1 Soft cap, diverted deposits stay as trading cash | 50% | +62.0% / -37% / 73% | +42.8% / -38% / 72% | -0.7% / -40% / 71% |
| 1 Soft cap, diverted deposits stay as trading cash | 60% | +61.1% / -38% / 74% | +41.8% / -39% / 73% | -1.2% / -40% / 72% |
| 1 Soft cap, diverted deposits stay as trading cash | 70% | +59.6% / -39% / 76% | +41.2% / -39% / 73% | -2.5% / -42% / 72% |
| 1b Soft cap, diverted deposits buy core ETH | 50% | +57.5% / -40% / 71% | +40.3% / -41% / 72% | -0.6% / -44% / 71% |
| 1b Soft cap, diverted deposits buy core ETH | 60% | +58.3% / -40% / 73% | +40.9% / -40% / 73% | -1.2% / -43% / 72% |
| 1b Soft cap, diverted deposits buy core ETH | 70% | +59.2% / -40% / 76% | +41.0% / -40% / 73% | -2.4% / -42% / 72% |
| 2 Trading-side cap (no new trading BTC above cap) | 50% | +56.5% / -40% / 58% | +37.4% / -40% / 58% | -4.0% / -42% / 56% |
| 2 Trading-side cap (no new trading BTC above cap) | 60% | +59.0% / -39% / 67% | +39.3% / -40% / 67% | -3.6% / -42% / 63% |
| 2 Trading-side cap (no new trading BTC above cap) | 70% | +59.2% / -39% / 76% | +40.6% / -40% / 75% | -2.9% / -42% / 71% |
| 3 Hard cap (also sells core BTC back to cap) | 50% | +61.1% / -37% / 52% | +38.9% / -39% / 52% | -3.3% / -41% / 52% |
| 3 Hard cap (also sells core BTC back to cap) | 60% | +61.6% / -37% / 62% | +40.8% / -39% / 62% | -3.3% / -42% / 62% |
| 3 Hard cap (also sells core BTC back to cap) | 70% | +60.3% / -38% / 72% | +41.3% / -39% / 72% | -2.8% / -42% / 71% |
| Control: no cap, 40% of deposits to core | | +61.2% / -37% / 74% | +43.9% / -37% / 72% | -0.8% / -40% / 69% |
| Control: no cap, 30% of deposits to core | | +63.2% / -35% / 70% | +47.1% / -35% / 68% | +1.0% / -37% / 66% |
| Hold BTC (same deposits) | | +51.0% / -53% / 100% | +23.3% / -53% / 100% | -9.1% / -53% / 100% |

No deposits (soft caps do nothing without deposits):

| Variant | Cap | From 2023 | From 2024 | From 2025 |
|---|---|---|---|---|
| No cap (today's rules) | | +48.1% / -47% / 74% | +29.4% / -46% / 69% | -9.0% / -51% / 63% |
| 2 Trading-side cap | 50% | +45.3% / -48% / 62% | +25.0% / -47% / 54% | -6.9% / -50% / 52% |
| 2 Trading-side cap | 60% | +45.2% / -48% / 62% | +28.9% / -46% / 64% | -8.4% / -51% / 60% |
| 2 Trading-side cap | 70% | +47.9% / -48% / 73% | +29.4% / -46% / 69% | -9.0% / -51% / 63% |
| 3 Hard cap | 50% | +47.6% / -46% / 52% | +24.6% / -47% / 52% | -6.2% / -50% / 52% |
| 3 Hard cap | 60% | +45.2% / -48% / 62% | +29.3% / -46% / 62% | -8.4% / -51% / 60% |
| 3 Hard cap | 70% | +48.4% / -47% / 72% | +29.4% / -46% / 69% | -9.0% / -51% / 63% |
| Hold BTC | | +51.8% / -53% / 100% | +24.2% / -53% / 100% | -7.9% / -53% / 100% |

Findings:
- Without a cap, BTC peaked at 73-77% of the account with deposits (63-74% without; average 45-53%): rallies
  push the core up, and the trading side can add a BTC breakout position on top.
- Soft caps don't hold the line: they only redirect new deposits, so BTC still reached 71-76% in rallies.
  Sending the diverted money to trading cash added 0.2 to 2.8 points a year with up to ~2 points less
  drawdown; sending it to core ETH was about even or worse, with deeper drawdowns from 2025.
- The trading-side cap was the weakest: it blocks BTC breakout trades. With deposits it never helped and cost
  up to 3.2 points a year; without deposits it was mixed (-4.4 to +2.1). BTC still reached 56-76% via the core.
- The hard cap is the only one that actually limits BTC (52% / 62% / 72% at most). Results were mixed: with
  deposits +1.1 to +2.4 points a year from 2023, -1.7 to +0.7 from 2024, -0.6 to -0.1 from 2025, with 0.5-2.4
  points less drawdown; without deposits -4.8 to +2.8. It sells core BTC (against "never sell the core") and
  pays extra spread on the trims.
- The controls explain the soft-cash gain: simply putting 40% (or 30%) of each deposit into the core, with
  no cap, did as well as or better than any cap. The gain comes from giving the trading side more money,
  which earned more than BTC in this history, not from the cap's timing.
- All differences are a few points a year on one 3.8-year history, so they're within noise (as noted above),
  and the trading side's edge carries survivorship bias. Nothing here clearly favours adding a cap.
