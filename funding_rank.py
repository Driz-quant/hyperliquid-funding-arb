import requests
import pandas as pd

URL = "https://api.hyperliquid.xyz/info"
data = requests.post(URL, json={"type": "metaAndAssetCtxs"}).json()

coins = data[0]["universe"]
stats = data[1]

rows = []
for coin, stat in zip(coins, stats):
    hourly = float(stat["funding"])
    rows.append({"coin": coin["name"], "hourly": hourly})

df = pd.DataFrame(rows)
df["annual_pct"] = df["hourly"] * 24 * 365 * 100
df = df.sort_values("annual_pct", ascending=False)
print(df.head(10))