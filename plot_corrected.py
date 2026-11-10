import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis import load_session, add_tyre_info, clean_laps, fit_tyre_model

SESSION_KEY = 9912
DRIVER = 1
COLORS = {"SOFT": "red", "MEDIUM": "gold", "HARD": "gray"}

laps, stints = load_session(SESSION_KEY)
clean = clean_laps(add_tyre_info(laps, stints))
model, coefs = fit_tyre_model(clean)

fuel_per_lap = coefs["lap_number"]
clean["corrected"] = clean["lap_duration"] - fuel_per_lap * (clean["lap_number"] - 1)

driver = clean[clean["driver_number"] == DRIVER]

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

for _, stint in driver.groupby("stint_number"):
    color = COLORS.get(stint["compound"].iloc[0], "black")
    label = stint["compound"].iloc[0]
    axes[0].plot(stint["lap_number"], stint["lap_duration"], marker="o", markersize=3, color=color, label=label)
    axes[1].plot(stint["lap_number"], stint["corrected"], marker="o", markersize=3, color=color, label=label)

axes[0].set_title("Gemessen")
axes[1].set_title(f"Ohne Kraftstoff-Effekt ({fuel_per_lap:.3f} s pro Runde)")
for ax in axes:
    ax.set_xlabel("Runde")
    ax.set_ylabel("Rundenzeit (s)")
    ax.grid(alpha=0.3)
    ax.legend()

fig.suptitle(f"Fahrer {DRIVER}, Monza 2025")
plt.savefig(f"corrected_driver_{DRIVER}.png", dpi=150, bbox_inches="tight")
print("Gespeichert")