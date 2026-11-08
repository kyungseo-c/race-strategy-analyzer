import pandas as pd


def load_session(session_key):
    laps = pd.read_csv(f"cache/laps_{session_key}.csv")
    stints = pd.read_csv(f"cache/stints_{session_key}.csv")
    return laps, stints


def add_tyre_info(laps, stints):
    # Runden ohne passenden Stint fallen weg (z. B. unvollendete Runde bei Ausfall)
    merged = laps.merge(
        stints[["driver_number", "stint_number", "lap_start", "lap_end", "compound", "tyre_age_at_start"]],
        on="driver_number",
    )
    in_stint = (merged["lap_number"] >= merged["lap_start"]) & (merged["lap_number"] <= merged["lap_end"])
    merged = merged[in_stint].copy()
    merged["tyre_age"] = merged["tyre_age_at_start"] + (merged["lap_number"] - merged["lap_start"])
    return merged


def clean_laps(laps_with_tyres, threshold=1.03):
    df = laps_with_tyres.copy()

    df = df[df["lap_duration"].notna()]
    df = df[df["lap_number"] > 1]
    df = df[~df["is_pit_out_lap"]]

    last_stint = df.groupby("driver_number")["stint_number"].transform("max")
    is_in_lap = (df["lap_number"] == df["lap_end"]) & (df["stint_number"] < last_stint)
    df = df[~is_in_lap]

    median = df.groupby("driver_number")["lap_duration"].transform("median")
    df = df[df["lap_duration"] < median * threshold]

    return df