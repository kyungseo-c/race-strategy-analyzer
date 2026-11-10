import requests
import pandas as pd

BASE_URL = "https://api.openf1.org/v1"
SESSION_KEY = 9912  # Monza 2025, Rennen


def fetch(endpoint, **params):
    params["session_key"] = SESSION_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=30)
    response.raise_for_status()
    return pd.DataFrame(response.json())


laps = fetch("laps")
stints = fetch("stints")
pits = fetch("pit")

print("Anzahl Runden:", len(laps))
print("Spalten laps:", list(laps.columns))
print()
print(laps[["driver_number", "lap_number", "lap_duration", "is_pit_out_lap"]].head(10))
print()
print(stints.head(10))

laps.to_csv(f"cache/laps_{SESSION_KEY}.csv", index=False)
stints.to_csv(f"cache/stints_{SESSION_KEY}.csv", index=False)
pits.to_csv(f"cache/pits_{SESSION_KEY}.csv", index=False)
print("Gespeichert in cache/")