import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SESSION_KEY = 9912
DRIVER = 1
COLORS = {"SOFT": "red", "MEDIUM": "gold", "HARD": "lightgray"}


def load_driver_data(session_key, driver):
    laps = pd.read_csv(f"cache/laps_{session_key}.csv")
    stints = pd.read_csv(f"cache/stints_{session_key}.csv")
    driver_laps = laps[laps["driver_number"] == driver]
    driver_stints = stints[stints["driver_number"] == driver]
    return driver_laps, driver_stints


driver_laps, driver_stints = load_driver_data(SESSION_KEY, DRIVER)

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