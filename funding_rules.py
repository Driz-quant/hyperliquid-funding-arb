import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

URL = "https://api.hyperliquid.xyz/info"
COIN = "XMR"
DAYS = 20
POSITION = 1000

PERP_FEE = 0.00045
SPOT_FEE = 0.00070
TRADE_FEE = (2 * PERP_FEE + 2 * SPOT_FEE) * POSITION   # round trip

ENTRY_RATE = 0.00004    # hourly, about 35% a year
EXIT_RATE = 0.000015    # just above the 0.0000125 baseline
WAIT_HOURS = 3          # hours of high funding before we enter

now_ms = int(time.time() * 1000)
start_ms = now_ms - DAYS * 24 * 60 * 60 * 1000
payload = {"type": "fundingHistory", "coin": COIN, "startTime": start_ms}
df = pd.DataFrame(requests.post(URL, json=payload).json())
df["fundingRate"] = df["fundingRate"].astype(float)
df["time"] = pd.to_datetime(df["time"], unit="ms")

in_trade = False
high_streak = 0
earned = 0.0
fees = 0.0
trades = 0
hours_in = 0
equity = []

for rate in df["fundingRate"]:
    if in_trade:
        earned += rate * POSITION
        hours_in += 1
        if rate <= EXIT_RATE:
            in_trade = False
            high_streak = 0
    else:
        if rate >= ENTRY_RATE:
            high_streak += 1
        else:
            high_streak = 0
        if high_streak >= WAIT_HOURS:
            in_trade = True
            fees += TRADE_FEE
            trades += 1
    equity.append(earned - fees)

df["rule_net"] = equity
df["always_net"] = df["fundingRate"].cumsum() * POSITION - TRADE_FEE

print("Rule:      net $", round(equity[-1], 2), "| trades:", trades, "| hours in market:", hours_in)
print("Always-on: net $", round(df["always_net"].iloc[-1], 2), "| hours in market:", len(df))

plt.figure(figsize=(10, 5))
plt.plot(df["time"], df["always_net"], label="Always on")
plt.plot(df["time"], df["rule_net"], label="Entry/exit rule")
plt.axhline(0, color="red", linestyle="--")
plt.title(f"{COIN}: rule vs always-on (net of fees)")
plt.xlabel("Time")
plt.ylabel("Net dollars")
plt.legend()
plt.grid(True)
plt.show()