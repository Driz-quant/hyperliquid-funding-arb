import requests

URL = "https://api.hyperliquid.xyz/info"

response = requests.post(URL, json={"type": "metaAndAssetCtxs"})
data = response.json()

coins = data[0]["universe"]
stats = data[1]

print("Number of coins:", len(coins))
print("First coin:", coins[0]["name"])
print("Its hourly funding:", stats[0]["funding"])