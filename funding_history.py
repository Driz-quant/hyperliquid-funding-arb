import requests
import pandas as pd
import time

URL = "https://api.hyperliquid.xyz/info"

now_ms = int(time.time() * 1000)
week_ago_ms = now_ms - 7 * 24 * 60 * 60 * 1000

payload = {"type": "fundingHistory", "coin": "XMR", "startTime": week_ago_ms}
history = requests.post(URL, json=payload).json()

df = pd.DataFrame(history)
df["fundingRate"] = df["fundingRate"].astype(float)
df["time"] = pd.to_datetime(df["time"], unit="ms")
df["annual_pct"] = df["fundingRate"] * 24 * 365 * 100

print(df[["time", "fundingRate", "annual_pct"]].tail(24))
print("Average annualised over the week:", df["annual_pct"].mean())