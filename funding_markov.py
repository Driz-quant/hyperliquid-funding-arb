import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

plt.style.use("dark_background")

URL = "https://api.hyperliquid.xyz/info"
COIN = "XMR"
DAYS = 20
POSITION = 1000
FEE = (2 * 0.00045 + 2 * 0.00070) * POSITION   # round trip, $2.30

SIM_HOURS = 168      # simulate one week ahead
N_SIMS = 1000        # number of simulated weeks
LOW_CUT = 0.00001    # below this = Low
HIGH_CUT = 0.00004   # above this = High

STATES = ["Low", "Normal", "High"]
COLORS = ["#ff4d6d", "#ffd166", "#06d6a0"]   # pink-red, gold, mint-green

# 1. Pull data
now_ms = int(time.time() * 1000)
start_ms = now_ms - DAYS * 24 * 60 * 60 * 1000
payload = {"type": "fundingHistory", "coin": COIN, "startTime": start_ms}
df = pd.DataFrame(requests.post(URL, json=payload).json())
df["fundingRate"] = df["fundingRate"].astype(float)
df["time"] = pd.to_datetime(df["time"], unit="ms")
df["annual_pct"] = df["fundingRate"] * 24 * 365 * 100

# 2. Label every hour with a regime: 0 = Low, 1 = Normal, 2 = High
df["state"] = np.select(
    [df["fundingRate"] < LOW_CUT, df["fundingRate"] < HIGH_CUT],
    [0, 1],
    default=2,
)
states = df["state"].values

# 3. Markov chain: count hour-to-hour switches
counts = np.zeros((3, 3))
for a, b in zip(states[:-1], states[1:]):
    counts[a, b] += 1

P = counts / np.maximum(counts.sum(axis=1, keepdims=True), 1)
for i in range(3):
    if counts[i].sum() == 0:
        P[i, i] = 1     # a regime we never left, so stay put

print("Hours in each regime (Low, Normal, High):", np.bincount(states, minlength=3))
print(pd.DataFrame(P, index=STATES, columns=STATES).round(2))

# 4. Monte Carlo: simulate many possible weeks
rng = np.random.default_rng(42)
rates_by_state = [df.loc[df["state"] == i, "fundingRate"].values for i in range(3)]
start_state = states[-1]
print("Current regime:", STATES[start_state])

paths = np.zeros((N_SIMS, SIM_HOURS))
for s in range(N_SIMS):
    state = start_state
    for h in range(SIM_HOURS):
        state = rng.choice(3, p=P[state])
        paths[s, h] = rng.choice(rates_by_state[state])

cum = paths.cumsum(axis=1) * POSITION
final = cum[:, -1]

print("Average 1-week funding earned: $", round(final.mean(), 2))
print("5th to 95th percentile: $", round(np.percentile(final, 5), 2),
      "to $", round(np.percentile(final, 95), 2))
print("Chance a week beats fees:", round((final > FEE).mean() * 100, 1), "%")

# 5. Charts
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
ax1, ax2, ax3, ax4 = axes.flatten()

# Chart 1: history coloured by regime
ax1.scatter(df["time"], df["annual_pct"], c=[COLORS[s] for s in states], s=12)
for i, name in enumerate(STATES):
    ax1.scatter([], [], color=COLORS[i], label=name)
ax1.legend()
ax1.set_title(f"{COIN} funding by regime (annualised %)")

# Chart 2: transition matrix heatmap
ax2.imshow(P, cmap="magma", vmin=0, vmax=1)
ax2.set_xticks(range(3))
ax2.set_xticklabels(STATES)
ax2.set_yticks(range(3))
ax2.set_yticklabels(STATES)
ax2.set_xlabel("Next hour")
ax2.set_ylabel("This hour")
ax2.set_title("Markov transition probabilities")
for i in range(3):
    for j in range(3):
        ax2.text(j, i, f"{P[i, j]:.2f}", ha="center", va="center", fontsize=14,
                 color="white" if P[i, j] < 0.5 else "black")

# Chart 3: rainbow of simulated weeks
cmap = plt.cm.rainbow
for i in range(150):
    ax3.plot(cum[i], color=cmap(i / 150), alpha=0.5, linewidth=0.8)
ax3.axhline(FEE, color="white", linestyle="--", label=f"Fees (${FEE:.2f})")
ax3.legend()
ax3.set_title("150 of 1000 simulated weeks")
ax3.set_xlabel("Hours ahead")
ax3.set_ylabel("Funding earned ($)")

# Chart 4: histogram, green = beats fees, red = doesn't
n, bins, patches = ax4.hist(final, bins=40, edgecolor="black")
for patch, left in zip(patches, bins[:-1]):
    patch.set_facecolor("#06d6a0" if left >= FEE else "#ff4d6d")
ax4.axvline(FEE, color="white", linestyle="--")
ax4.set_title("Where the 1000 weeks ended up")
ax4.set_xlabel("Funding earned after 1 week ($)")
ax4.set_ylabel("Number of simulations")

plt.tight_layout()
plt.show()