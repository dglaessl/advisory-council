**Answer.** I found no source showing that a crypto trading edge survives a ~1.9% round trip at retail scale. Every positive result I found assumed costs of 0.1–1.0% and mostly liquid coins. The most credible levers for this account are low turnover, trend rules used as rare risk-off switches, and cheaper execution. On Robinhood, the "collar" is a price buffer on market orders, and exchange routing is a real but uncertain lower-cost option.

**Key findings**

1. **Time-series trend.** [Catching Crypto Trends](https://abarbon.com/papers/catching-crypto-trends) tests an ensemble of Donchian breakouts with volatility sizing. It reports a Sharpe above 1.5 net of fees and ~10.8% annual alpha vs BTC. It assumed costs of only 0.10%, 0.25% and 0.50% ([CXO summary](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/)), and its data ran to March 2025. I did not retrieve its drawdowns or cost-sensitivity table. Credibility is medium-low: it is a practitioner working paper on a bull-heavy sample, with costs far below Daniel's. I found no peer-reviewed test of a single BTC 200-day filter net of retail costs.
2. **Cross-sectional momentum.**
   - [Liu, Tsyvinski and Wu](https://papers.ssrn.com/abstract=3379131) find momentum is a real factor, but the evidence is long-short, which Daniel can't do in spot.
   - [Begusic and Kostanjcar](https://arxiv.org/pdf/1904.00890) (711 coins, 2015–19) find momentum only in the most liquid coins. A long-only liquid-winners strategy had an information ratio of 1.59 gross and 1.27 at 100 bp cost. It rebalanced every two weeks, so turnover is high.
   - [Fieberg et al. (JFQA)](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/trend-factor-for-the-cross-section-of-cryptocurrency-returns/4C1509ACBA33D5DCAF0AC24379148178) says its trend factor survives costs, but I saw no cost figures.
   - The effect exists, but at 1.9% round trip frequent rebalancing probably consumes it.
3. **Volatility targeting.** [Moreira and Muir](https://www.nber.org/papers/22208) show Sharpe gains in equity factors, not crypto. For crypto I found only [Kaya and Mostowfi](https://ideas.repec.org/a/eee/finlet/v46y2022ipbs1544612321004116.html) (2017–21), which is about low-volatility coin selection plus a stop-loss, not volatility targeting. The benefit is mainly smoother drawdowns. The existing ATR-based sizing already does this.
4. **DCA, lump sum and rebalancing.** Vanguard's study, cited secondhand by [Masterworks](https://www.masterworks.com/academy/posts/dollar-cost-averaging-vs-lump-sum-investing), found lump sum beat 12-month DCA about two-thirds of the time. That covered the US, UK and Australia from 1976 to 2022, with an average margin of 1.2–2.4 points. It is equities and bonds only, with no crypto evidence. Daniel's weekly deposits are cash flow, not a DCA choice. The real question is cash drag on the idle trading-cash half. I found no primary evidence on BTC/ETH/cash rebalancing, so treat any such claim as unverified.
5. **Frequency and costs.** [Barber and Odean](https://faculty.haas.berkeley.edu/odean/papers/returns/returns.html) is equities in the 1990s, with far lower costs than 1.9%, but the direction is robust. The average household's gross return was 17.7% and its net 15.3%. The most active fifth earned 10.0% net. Credibility on direction is high.
6. **Robinhood execution (primary sources).**
   - **Market-maker routing:** per [Crypto order routing](https://robinhood.com/us/en/support/articles/crypto-order-routing/?hcs=true), it is the default. Orders go to unnamed liquidity providers with no fee. Robinhood is paid from the spread, receiving $0.95 per $100 as of June 15, 2026. Fills are at bid or ask, not mid. That matches Daniel's ~0.93% fills above mark, so the cost is structural, not slippage.
   - **Exchange routing:** this is the lower-cost option. It is available only for some coins, only in the app, and not in North Carolina. It charges 0–0.95% instead of the spread, falling with 30-day volume. Limit orders generally rest on Bitstamp and may never fill. Robinhood says all-in cost may be higher or lower. The help page does not say whether the API account can use it, so that is an open question.
   - **Collar:** per [Buying and selling crypto](https://robinhood.com/us/en/support/articles/360001298246/) and [Legend order behaviors](https://robinhood.com/us/en/support/articles/legend-behaviors-and-settings), a stop becomes a market order when triggered. That market order is collared: buys can fill up to 1% above the last ask, and sells up to 5% below the last bid. A stop-limit caps the price but may not fill. The stop price is not a guaranteed price.
   - **Limit-at-mark entries:** they fill only when the ask reaches the limit, so 0/5 fills is expected.

**Confidence.** Medium on the Robinhood mechanics, since the sources are primary and dated 2026. Medium-low on the strategy evidence, because crypto history is short and the studies assume lower costs than Daniel pays. I did not verify that the API behaves like the app.

**Red flags**
- A beincrypto article on the "2% spread" failed to fetch, and I left out its claims.
- The Barber and Odean sample years come from my memory, not the fetched page.
- The DeMiguel et al. critique of volatility management is characterized from its title only.
- The Vanguard figures are secondary.
- The growthpilot.it.com mirror of a Robinhood page appeared in search results, and I ignored it.
- Fetched pages were summarized by a small model, so figures are as returned and not independently checked against the PDFs.
- No instructions or injection attempts appeared in any fetched page.

Full write-up: `/home/claude/advisory-council/council/research/2026-10-28-crypto-rules-evidence.md`