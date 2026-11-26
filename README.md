# Hyperliquid Funding Rate Arbitrage (Backtest & Paper Only)

A set of Python scripts that explore **perpetual funding rate arbitrage** on [Hyperliquid](https://hyperliquid.xyz), using the exchange's free, read-only public API.

> **Backtest and paper only.** No wallet, no API keys, no real money, and nothing here is financial advice. This is a learning project in quantitative finance.

## The idea

Perpetual futures have no expiry, so exchanges use a **funding rate** to keep the perp price close to the spot price. On Hyperliquid, funding is paid **every hour**: when the rate is positive, longs pay shorts.

A **hedged position** (short the perp, long the same amount of spot) cancels out most of the price risk, so you mostly collect funding. The questions this project asks:

- Which coins pay the most funding right now?
- Does the funding earned beat the trading fees?
- Can a simple entry/exit rule do better than just staying in?
- What does a Markov chain say about how long funding spikes last?

Annualised funding = hourly rate x 24 x 365. Hyperliquid's baseline is 0.0000125 per hour, about 10.95% a year.

## Scripts

| Script | What it does |
|---|---|
| `funding_scanner.py` | First API call: counts coins and prints one coin's hourly funding |
| `funding_rank.py` | Pulls funding for every coin, annualises it, and ranks the top 10 |
| `funding_history.py` | Pulls hourly funding history for one coin (default XMR) |
| `funding_backtest.py` | Backtests an "always on" hedge: funding earned minus fees, with a chart |
| `funding_rules.py` | Tests an entry/exit rule (enter after high funding for X hours) against always-on |
| `funding_markov.py` | 3-state Markov chain (Low / Normal / High funding) plus a 1000-run Monte Carlo of the next week |

## How to run

```bash
pip install requests pandas numpy matplotlib
python funding_rank.py
python funding_backtest.py
```

Every script fetches **live data** each time it runs, so your numbers will differ from the ones below. Settings like `COIN`, `DAYS`, `POSITION` and the fee rates sit at the top of each script.

## Fee assumptions

Base-tier Hyperliquid fees at the time of writing: perps 0.045% taker, spot 0.070% taker. A round trip on a hedged position (open and close both legs) costs about 0.23% of the position size, or $2.30 on $1,000. Check Hyperliquid's fee page for current rates.

## What I found

Results from one 20-day window of XMR data (ending 26 Nov 2026), on a $1,000 hedge:

- **Always-on:** about $27.76 funding earned, $2.30 fees, **+$25.46 net**. Most of the profit came from a single multi-day burst; outside it, funding earned roughly $0.50 a day.
- **Entry/exit rule:** **-$5.20 net** across 11 trades and 82 hours in the market. The rule picked profitable hours, but paid about $25 in fees re-entering. Fees were the whole story.
- **Funding comes in bursts.** Spikes of 50% to 130% annualised often faded back to baseline within hours, and funding went negative at times.
- **Markov and Monte Carlo:** simulated weeks averaged about $10.25 in funding (5th to 95th percentile: $4.24 to $17.39), and about 99% of simulated weeks beat the fees. See the caveats below before trusting that number.

**Takeaway:** fees set the break-even, funding is bursty, and trading in and out too often can cost more than it earns.

## Limitations

- One coin and 20 days of data. The API returns at most about 500 hourly records per request.
- Everything is **in-sample**. There is no out-of-sample test, so the rule's settings could be overfitted.
- The Monte Carlo only recycles funding rates it has already seen, and the 20-day window contains one large spike.
- Not modelled: slippage, price gaps between the two legs, margin and liquidation risk on the short.
- Capital is split across two legs, so real returns are roughly half of what the dollar figures suggest.
- The spot leg of the hedge may not exist for every coin on Hyperliquid (XMR included).

## Possible next steps

- Run the backtest and rules across many coins instead of one.
- Page through the API to get months of history.
- Test entry/exit settings out-of-sample.
- Add slippage and a liquidation check.

## Built with

Python, requests, pandas, numpy, matplotlib.
