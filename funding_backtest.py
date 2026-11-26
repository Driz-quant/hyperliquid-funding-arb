import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

URL = "https://api.hyperliquid.xyz/info"
COIN = "XMR"
DAYS = 20
POSITION = 1000      # dollars on each leg

PERP_FEE = 0.00045   # 0.045% taker
SPOT_FEE = 0.00070   # 0.070% taker

# Pull funding history
now_ms = int(time.time() * 1000)
start_ms = now_ms - DAYS * 24 * 60 * 60 * 1000

payload = {"type": "fundingHistory", "coin": COIN, "startTime": start_ms}
df = pd.DataFrame(requests.post(URL, json=payload).json())

df["fundingRate"] = df["fundingRate"].astype(float)
df["time"] = pd.to_datetime(df["time"], unit="ms")
df["cum_funding"] = df["fundingRate"].cumsum() * POSITION

# Backtest maths
funding_earned = df["fundingRate"].sum() * POSITION
fees = (2 * PERP_FEE + 2 * SPOT_FEE) * POSITION
net = funding_earned - fees

avg_hourly = df["fundingRate"].mean()
breakeven_hours = fees / (avg_hourly * POSITION)

print("Coin:", COIN, "| hours of data:", len(df))
print("Funding earned: $", round(funding_earned, 2))
print("Fees paid:      $", round(fees, 2))
print("Net profit:     $", round(net, 2))
print("Break-even after about", round(breakeven_hours), "hours")

# Chart
plt.figure(figsize=(10, 5))
plt.plot(df["time"], df["cum_funding"], label="Funding earned (running total)")
plt.axhline(fees, color="red", linestyle="--", label=f"Fees (${fees:.2f})")
plt.title(f"{COIN}: funding earned vs fees on ${POSITION} hedge")
plt.xlabel("Time")
plt.ylabel("Dollars")
plt.legend()
plt.grid(True)
plt.show()