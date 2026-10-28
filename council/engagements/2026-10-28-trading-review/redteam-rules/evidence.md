# Evidence review: what improves outcomes for a small, high-cost crypto account
Date: 2026-10-28 | Seat: Research Analyst | Status: independent draft | Mode: learning
Method note: fetched pages were summarized by a small model; numbers below are only those it returned. Items marked NOT RETRIEVED were not seen. No scout-inbox material used.

## Bottom line
- Nothing found supports a trading edge that survives ~1.9% round trip at retail scale. Every positive crypto result I found assumed costs of 0.1-1.0% per trade (or per side) and mostly liquid, large coins.
- The best-supported levers for a small account are low turnover, trend filters used as risk-off switches (few trades), and cost reduction (limit/stop-limit orders, possibly exchange routing).
- Publication/data-mining bias applies to nearly all of it: crypto history is about 10 years, one dominant bull-bust regime, and most papers are sample-specific.

## 1. Time-series momentum / trend following
- [Catching Crypto Trends (Zarattini, Pagani, Barbon, 2025)](https://abarbon.com/papers/catching-crypto-trends): ensemble of Donchian breakout models (lookbacks 5-360 days), volatility-sized, top liquid coins; data to mid-March 2025. Reports Sharpe above 1.5 net of fees and ~10.8% annualized alpha vs BTC. Costs tested: 0.10%, 0.25%, 0.50% (per [CXO Advisory summary](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/)). Position leverage up to 200% allowed. I did NOT retrieve drawdowns or the cost-sensitivity table.
- Credibility: medium-low. Working paper from a practitioner shop (Concretum), rules chosen with hindsight on a bull-heavy sample, costs 4-19x lower than Daniel's 1.9%. At 1.9% round trip an ensemble that rebalances daily would not be comparable. The paper's own cost-mitigation method was not retrieved.
- Implication: the evidence is for slow, diversified-lookback trend with exits at a trailing level, not for a single 55-day breakout with 4% risk. Long lookbacks (150-360d) trade rarely, so cost drag is smaller.
- Not found: a peer-reviewed study of a single BTC 200-day moving-average filter net of retail costs. Say so rather than cite blog backtests.

## 2. Cross-sectional momentum
- [Common Risk Factors in Cryptocurrency (Liu, Tsyvinski, Wu; JF 2022)](https://papers.ssrn.com/abstract=3379131): market, size and momentum factors explain the cross-section; ten long-short strategies earn significant excess returns. Abstract does not address costs or shorting feasibility. Long-short is not available to Daniel (spot only).
- [Momentum and liquidity in cryptocurrencies (Begusic, Kostanjcar)](https://arxiv.org/pdf/1904.00890): 711 coins, Jan 2015-Jan 2019, 14-day momentum. Momentum only significant in the most liquid coins (0.26% daily spread); illiquid coins mean-revert. Long-only liquid winners had information ratio 1.59 gross, 1.27 at 100 bp cost. Arxiv preprint, 4 years, equal-weighted two-week rebalances (high turnover).
- [A trend factor for the cross section of crypto returns (Fieberg et al., JFQA)](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/trend-factor-for-the-cross-section-of-cryptocurrency-returns/4C1509ACBA33D5DCAF0AC<ACCT>): CTREND factor, 3,000+ coins, abstract says it survives transaction costs and persists in large liquid coins; no cost figures retrieved. Peer-reviewed, but it is a machine-learning factor with frequent rebalancing.
- Takeaway: cross-sectional momentum exists mainly in liquid coins and decays with cost; at 1.9% round trip, rebalancing weekly or two-weekly would consume the premium. Credibility of existence: medium. Credibility of net retail profit: low.

## 3. Volatility targeting / sizing
- [Volatility-Managed Portfolios (Moreira and Muir, NBER 22208)](https://www.nber.org/papers/22208): scaling exposure down when realized volatility is high raises Sharpe in equity factors. Equities, not crypto; later critiques exist (the multifactor paper by DeMiguel et al., [JF 2024](https://lbsresearch.london.edu/id/eprint/3716), argues gains are weaker once multiple factors are considered; I saw only its title, not its abstract).
- Crypto-specific: [Low-volatility strategies for highly liquid cryptocurrencies (Kaya, Mostowfi; FRL 2022)](https://ideas.repec.org/a/eee/finlet/v46y2022ipbs<ACCT>4116.html), 2017-mid 2021: low-vol coin selection plus a stop-loss improved Sharpe and downside. This is selection, not targeting; short sample. I found no solid crypto vol-targeting study.
- Mechanism that matters for Daniel: position size inversely to ATR, which his rules already do. The main benefit is smoother drawdowns, not higher return. Credibility: medium for risk reduction, low for return enhancement.

## 4. DCA vs lump sum, rebalancing
- Vanguard (cost averaging study, first published 2012), as cited by [Masterworks](https://www.masterworks.com/academy/posts/dollar-cost-averaging-vs-lump-sum-investing) (secondary; I could not fetch Vanguard's own page): lump sum beat 12-month DCA ~two-thirds of rolling periods (US/UK/Australia, 1976-2022), by ~1.2-2.4 pts on average. Equities and bonds only; no crypto evidence found.
- Relevance: Daniel's +$200/week is not a choice between DCA and lump sum, it is cash flow. The real question is whether to hold the 50% trading-cash slice idle (cash drag) vs put it in the core. Any rebalancing evidence for BTC/ETH/cash: NOT FOUND in primary literature; a [CoinShares piece](https://etp.coinshares.com/us/insights/research-data/just-the-right-amount-of-bitcoin/) turned up but was not retrieved. Treat rebalancing claims as unverified.

## 5. Trading frequency and costs
- [Trading Is Hazardous to Your Wealth / Common Stock Investment Performance of Individual Investors (Barber and Odean)](https://faculty.haas.berkeley.edu/odean/papers/returns/returns.html): ~66,000 US households, 1991-96 (per my knowledge; the page returned 80% annual turnover, gross 17.7% vs net 15.3%; most active quintile net 10.0% vs market 17.1%). Equities, 1990s, but the direction is replicated widely and costs there were far lower than 1.9%. Credibility: high on direction.
- Arithmetic (mine, not a source): a 1.9% round trip means the trading sleeve needs ~1.9% gross per trade just to break even; 25 round trips a year on the sleeve costs ~47% of sleeve value in drag unless it was concentrated.

## 6. Robinhood crypto execution (answers the open factual question)
- Source: [Crypto order routing (Robinhood Help)](https://robinhood.com/us/en/support/articles/crypto-order-routing/?hcs=true). Market maker routing is the default in app and web classic. Orders go to unnamed non-exchange liquidity providers. No separate fee; Robinhood is paid out of the spread: as of June 15, 2026 it receives $0.95 per $100 notional. Fills occur at bid or ask, not mid.
- Lower-cost option: exchange routing. Available only for certain coins, in the app (not web classic), not for North Carolina residents. Charges 0.00-0.95% fee falling with 30-day exchange-routing volume instead of the spread. Market orders hit partner exchanges as takers; limit orders generally rest on Bitstamp and may get the maker fee but may never fill if liquidity is elsewhere. Robinhood itself says all-in cost may be higher or lower. Check the [fee schedule](https://cdn.robinhood.com/assets/robinhood/legal/rhc-fee-schedule.pdf) (not retrieved). Open question for Daniel: whether the Robinhood Crypto API account used by the agent can use exchange routing at all; the help page does not say.
- Stop orders: per [Buying and selling crypto](https://robinhood.com/us/en/support/articles/<ACCT>/) and [Legend default order behaviors](https://robinhood.com/us/en/support/articles/legend-behaviors-and-settings): a stop becomes a market order when triggered, and that market order is "collared": buys become limit orders up to 1% above the last ask, sells become limit orders up to 5% below the last bid; unfilled after ~2 minutes may be cancelled. So "collar" = the price buffer on converted market orders (the sell collar tolerates a fill up to 5% worse than bid). A stop-limit instead sets your own limit, capping the price but risking no fill. Stop price is not a guaranteed price. Legend defaults the stop 1% below bid / above ask.
- Fit with Daniel's data: a ~0.93% fill above mark is consistent with the ~0.95% spread cut, i.e. costs are structural, not slippage. Limit-at-mark entries filling 0/5 is expected, since buys fill only when the ask reaches the limit.
- Caveat: pages are Robinhood US help pages, search-result copies, and the growthpilot.it.com mirror should be ignored. Whether the API behaves identically to the app was not verified.

## Red flags
- Search snippets and a beincrypto article ("2% spread") could not be fetched; unverified secondary claims omitted.
- Barber and Odean sample years come from memory, not the fetched page.
- DeMiguel et al. characterization is from the title only.
- Vanguard figures are secondary.
- No prompt injection or instructions found in any fetched page.

## Confidence
Medium on the Robinhood mechanics (primary source, dated 2026); medium-low on all strategy-return evidence (short history, cost mismatch, publication bias).
