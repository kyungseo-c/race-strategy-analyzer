from analysis import load_session, add_tyre_info
from analysis import clean_laps

laps, stints = load_session(9912)
laps_with_tyres = add_tyre_info(laps, stints)

print("Runden vorher:", len(laps))
print("Runden nachher:", len(laps_with_tyres))
print()

driver_1 = laps_with_tyres[laps_with_tyres["driver_number"] == 1]
print(driver_1[["lap_number", "lap_duration", "stint_number", "compound", "tyre_age"]].iloc[33:42])

clean = clean_laps(laps_with_tyres)
print()
print("Saubere Runden:", len(clean), "von", len(laps_with_tyres))
print("Entfernt pro Fahrer:")
before = laps_with_tyres.groupby("driver_number").size()
after = clean.groupby("driver_number").size()
removed = before.sub(after, fill_value=0).astype(int)
print(removed.sort_values(ascending=False))