import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SESSION_KEY = 9912
DRIVER = 1
COLORS = {"SOFT": "red", "MEDIUM": "gold", "HARD": "lightgray"}

laps = pd.read_csv(f"cache/laps_{SESSION_KEY}.csv")
stints = pd.read_csv(f"cache/stints_{SESSION_KEY}.csv")

driver_laps = laps[laps["driver_number"] == DRIVER]
driver_stints = stints[stints["driver_number"] == DRIVER]

median_time = driver_laps["lap_duration"].median()
clean = driver_laps[driver_laps["lap_duration"] < median_time * 1.03]

plt.figure(figsize=(10, 5))

for _, stint in driver_stints.iterrows():
    plt.axvspan(
        stint["lap_start"] - 0.5,
        stint["lap_end"] + 0.5,
        color=COLORS.get(stint["compound"], "white"),
        alpha=0.25,
        label=stint["compound"],
    )

plt.plot(clean["lap_number"], clean["lap_duration"], marker="o", markersize=3, color="black")
plt.xlabel("Runde")
plt.ylabel("Rundenzeit (s)")
plt.title(f"Rundenzeiten Fahrer {DRIVER}, Monza 2025 (ohne Start- und Boxenrunden)")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig(f"laps_driver_{DRIVER}.png", dpi=150, bbox_inches="tight")
print(f"{len(driver_laps) - len(clean)} Runden entfernt")