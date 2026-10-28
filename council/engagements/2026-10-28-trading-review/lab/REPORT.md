# Disposable trading rules lab — verified variant, not live-account replication

## Data and method
Public Coinbase daily candles retrieved 2026-10-28 UTC. BTC range 2021-06-01–2026-10-27 (1,975 rows); last fully completed returned candle: 2026-10-27, ending 2026-10-28 00:00 UTC. Current-day candle excluded. All 18 assets gap-free after their first returned candle; XRP starts 2023-07-13, SUI 2023-05-18, NEAR 2022-09-01, HBAR 2022-10-13. Full coverage.json records all listing-dependent ranges. HTTP data was validated structurally, not independently cross-vendor verified. No unavailable history was synthesized.

$1,000 initial capital. Start Jan 1 of each indicated year; common end Oct 27, 2026. Core+cash and active variants initially allocate 50% BTC core, 50% cash/trading. Deposits split 50/50; hold BTC invests 100%. No core rebalancing. 0.0095 haircut each side for every asset, including core and terminal net liquidation. Cash yield zero. Signals use prior completed day; fills next open. 55-day breakout, 1.5x prior-20-day volume, own 200d average, 4% risk of trading equity, 50% single-position cap, source ATR/support stop and target rules, target half sales/trailing stops. Entry gaps revalidate risk/reward. Spec caps apply ONLY to NEAR/AAVE/UNI and trading-sleeve equity; caps are entry constraints, not daily hard rebalances. BTC trend blocks new SPEC buys and trims to 10% after 3 days. Three discretionary trading actions/day; stops exempt.

Changes versus supplied simulator: next-open execution, source indicator prefix reused unchanged with breakout-days=55, no pullbacks/fallback/pyramiding/concentration caps, net-liquidation accounting from inception, beginning-day deposits, independent XIRR, unitized TRADING-SLEEVE 30% breaker with 30-day buy pause. This breaker differs from source total-account raw-equity breaker. These are explicitly simplified corrected variants, not minimal behavioral-equivalence patches. The separate reference file is byte-identical to source; no source edits. Core-filter column applies ONLY to the 50% BTC core of core+cash: daily prior-close > 200d, next-open all-in/all-out, no core stops/breaker. It is not rotation.py trend and is not combined with active trading.

## Terminal values after modeled exit costs

### Weekly deposits $0

| Start | Contributions | Core+cash | Active .10 | Active .25 | Active .50 | Hold BTC | Core-only filter + cash |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022 | $1,000 | $1,358 | $2,773 | $3,256 | $3,824 | $1,715 | $1,767 |
| 2023 | $1,000 | $2,898 | $4,499 | $5,030 | $5,653 | $4,795 | $1,767 |
| 2024 | $1,000 | $1,437 | $2,098 | $2,419 | $2,704 | $1,875 | $1,175 |
| 2025 | $1,000 | $925 | $832 | $898 | $988 | $849 | $906 |
| 2026 | $1,000 | $953 | $950 | $1,023 | $1,124 | $906 | $1,072 |

### Weekly deposits $200

| Start | Contributions | Core+cash | Active .10 | Active .25 | Active .50 | Hold BTC | Core-only filter + cash |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022 | $51,200 | $73,289 | $110,918 | $122,904 | $137,378 | $95,378 | $64,675 |
| 2023 | $40,800 | $52,908 | $76,671 | $84,694 | $94,801 | $65,016 | $46,288 |
| 2024 | $30,400 | $31,464 | $36,624 | $40,474 | $44,610 | $32,528 | $30,834 |
| 2025 | $19,800 | $19,015 | $18,425 | $19,707 | $21,548 | $18,231 | $20,096 |
| 2026 | $9,400 | $9,730 | $9,791 | $10,375 | $11,242 | $10,061 | $9,931 |

## Weekly $200: annual money-weighted return / unitized maximum drawdown

| Start | Core+cash | Active .10 | Active .25 | Active .50 | Hold BTC | Core-only filter + cash |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | +14.8% / -40.2% | +32.7% / -41.0% | +37.3% / -41.0% | +42.3% / -41.0% | +26.1% / -68.7% | +9.6% / -26.4% |
| 2023 | +13.6% / -38.6% | +34.3% / -38.1% | +40.2% / -37.9% | +46.9% / -37.8% | +24.9% / -53.2% | +6.5% / -24.7% |
| 2024 | +2.4% / -33.2% | +13.3% / -38.5% | +20.8% / -38.2% | +28.3% / -38.2% | +4.7% / -53.4% | +1.0% / -21.6% |
| 2025 | -4.2% / -30.0% | -7.3% / -40.3% | -0.5% / -40.2% | +9.1% / -40.2% | -8.4% / -53.7% | +1.6% / -20.3% |
| 2026 | +7.9% / -22.1% | +9.3% / -22.3% | +23.9% / -22.3% | +46.9% / -22.3% | +16.0% / -41.6% | +12.8% / -4.2% |

## Interpretation and limits
Active .25 beats the matched cash twin in 4/5 start cohorts and loses in 2025, with materially worse drawdown in several cohorts. Larger SPEC caps improve these particular terminal values, but that is in-sample sensitivity, NOT evidence to adopt .50. Core-only filter reduces drawdown here but sacrifices substantial upside in 2023/2024 and loses money in the zero-deposit 2025 cohort. Deposit-weighted and time-weighted results differ: 2026 hold BTC has -16.0% TWR CAGR but +16.0% XIRR with weekly deposits. Positive terminal profit is not the same as positive TWR.

Five overlapping inception cohorts share one endpoint and are not five independent trials; durations vary from 10 months to nearly five years, not a matched 6–24-month probability study. No rolling-window/out-of-sample/bootstrap statistical validation, parameter search correction, point-in-time universe, taxes, operational costs or cash yield. Fixed survivors, daily idealized open fills, cost convention and changed breaker limit inference. Exact reference-engine reproduction and active+core-filter interaction not tested. Do not infer a probability of beating deposits or an adoption recommendation.

## Reproduction and checks
Run from this directory: `timeout 160s /opt/venv/bin/python -I -B fetch_lab.py > fetch.log 2>&1` (network, overwrites local fetched files); `timeout 60s /opt/venv/bin/python -I -B compare_lab.py > compare.log 2>&1` (local only). Existing data/results are preserved for review; no deletion performed.

Passed: deposit-neutral return/XIRR arithmetic; initial flat-price round-trip cost; four independent passive final-value closed forms; causal-prefix invariance; all traced next-open entry dates/prices; missing-date rejection; independently calculated weekly-deposit core-filter ledger. See compare.log. These are targeted checks, not exhaustive validation of all management branches.

Artifacts: AUDIT.md (pre-execution findings), fetch_lab.py, fetch.log, coverage.json, data/*.json, compare_lab.py, backtest.reference.py, results.json (all 60 records, including CAGR/TWR/XIRR/drawdown/costs), compare.log, source-before.sha256. No brokerage, secrets, account access, publishing, settings changes or delegation. All writes confined to this lab.
