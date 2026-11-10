from analysis import load_session, add_tyre_info, clean_laps, stint_slopes, fit_tyre_model

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

slopes = stint_slopes(clean)
print()
print(slopes.sort_values("slope").round(3))
print()
print(slopes.groupby("compound")["slope"].agg(["count", "median"]).round(3))

model, coefs = fit_tyre_model(clean)

print()
print("--- Mehrfache Regression ---")
print(coefs[["lap_number", "age_HARD", "age_MEDIUM", "age_SOFT"]].round(3))
print()
print("Basis-Unterschied zu HARD (s):")
print(coefs[["compound_MEDIUM", "compound_SOFT"]].round(3))