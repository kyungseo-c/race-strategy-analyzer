import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis import load_session, add_tyre_info, clean_laps, fit_tyre_model

SESSION_KEY = 9912
DRIVERS = {1: "VER", 16: "LEC"}
STYLES = {1: "-", 16: "--"}
COLORS = {"SOFT": "red", "MEDIUM": "gold", "HARD": "gray"}

laps, stints = load_session(SESSION_KEY)
clean = clean_laps(add_tyre_info(laps, stints))
model, coefs = fit_tyre_model(clean)
fuel_per_lap = coefs["lap_number"]
clean["corrected"] = clean["lap_duration"] - fuel_per_lap * (clean["lap_number"] - 1)

# 1. Tabelle pro Stint
rows = []
selected = clean[clean["driver_number"].isin(DRIVERS)]
for (driver, stint_no), g in selected.groupby(["driver_number", "stint_number"]):
    slope, _ = np.polyfit(g["tyre_age"], g["corrected"], 1)
    rows.append({
        "Fahrer": DRIVERS[driver],
        "Stint": stint_no,
        "Reifen": g["compound"].iloc[0],
        "Runden": f"{g['lap_start'].iloc[0]}-{g['lap_end'].iloc[0]}",
        "Pace (s)": g["corrected"].mean(),
        "Verschleiss (s/Runde)": slope,
    })
print(pd.DataFrame(rows).round(3).to_string(index=False))

# 2. Abstand ueber das Rennen
race = laps[laps["driver_number"].isin(DRIVERS)]
times = race.pivot(index="lap_number", columns="driver_number", values="lap_duration")
gap = times.cumsum()[16] - times.cumsum()[1]

# 3. Diagramme
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for driver, name in DRIVERS.items():
    d = clean[clean["driver_number"] == driver]
    for _, s in d.groupby("stint_number"):
        compound = s["compound"].iloc[0]
        axes[0].plot(s["lap_number"], s["corrected"], STYLES[driver],
                     color=COLORS.get(compound, "black"), marker="o", markersize=3,
                     label=f"{name} {compound}")

axes[1].plot(gap.index, gap.values, color="black")
axes[1].axhline(0, color="gray", linewidth=0.8)
for driver, name in DRIVERS.items():
    pit_laps = stints[(stints["driver_number"] == driver) & (stints["stint_number"] > 1)]["lap_start"]
    for lap in pit_laps:
        axes[1].axvline(lap, linestyle=STYLES[driver], color="red", alpha=0.6, label=f"Boxenstopp {name}")

axes[0].set_title("Pace ohne Kraftstoff-Effekt")
axes[0].set_ylabel("Rundenzeit (s)")
axes[1].set_title("Abstand LEC hinter VER")
axes[1].set_ylabel("Abstand (s)")
for ax in axes:
    ax.set_xlabel("Runde")
    ax.grid(alpha=0.3)
    ax.legend()

fig.suptitle("VER vs. LEC, Monza 2025")
plt.savefig("compare_ver_lec.png", dpi=150, bbox_inches="tight")
print("Gespeichert")