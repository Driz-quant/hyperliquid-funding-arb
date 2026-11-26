Hyperliquid Funding Rate Arbitrage (Backtest & Paper Only)

A set of Python scripts that explore perpetual funding rate arbitrage on Hyperliquid, using the exchange's free, read-only public API.

Backtest and paper only. No wallet, no API keys, no real money, and nothing here is financial advice. This is a learning project in quantitative finance.

The idea

Perpetual futures have no expiry, so exchanges use a funding rate to keep the perp price close to the spot price. On Hyperliquid, funding is paid every hour: when the rate is positive, longs pay shorts.

A hedged position (short the perp, long the same amount of spot) cancels out most of the price risk, so you mostly collect funding. The questions this project asks:

Which coins pay the most funding right now?
Does the funding earned beat the trading fees?
Can a simple entry/exit rule do better than just staying in?
What does a Markov chain say about how long funding spikes last?

Annualised funding = hourly rate x 24 x 365. Hyperliquid's baseline is 0.0000125 per hour, about 10.95% a year.

Scripts
Script	What it does
funding_scanner.py	First API call: counts coins and prints one coin's hourly funding
funding_rank.py	Pulls funding for every coin, annualises it, and ranks the top 10
funding_history.py	Pulls hourly funding history for one coin (default XMR)
funding_backtest.py	Backtests an "always on" hedge: funding earned minus fees, with a chart
funding_rules.py	Tests an entry/exit rule (enter after high funding for X hours) against always-on
funding_markov.py	3-state Markov chain (Low / Normal / High funding) plus a 1000-run Monte Carlo of the next week
