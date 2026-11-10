import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

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


def stint_slopes(clean, min_laps=5):
    rows = []
    for (driver, stint), group in clean.groupby(["driver_number", "stint_number"]):
        if len(group) < min_laps:
            continue
        slope, intercept = np.polyfit(group["tyre_age"], group["lap_duration"], 1)
        rows.append({
            "driver_number": driver,
            "stint_number": stint,
            "compound": group["compound"].iloc[0],
            "laps": len(group),
            "slope": slope,
        })
    return pd.DataFrame(rows)


def fit_tyre_model(clean):
    df = clean.copy()

    X = pd.DataFrame({"lap_number": df["lap_number"]})

    for compound in sorted(df["compound"].unique()):
        X[f"age_{compound}"] = df["tyre_age"] * (df["compound"] == compound)

    X = X.join(pd.get_dummies(df["compound"], prefix="compound", drop_first=True, dtype=int))
    X = X.join(pd.get_dummies(df["driver_number"], prefix="driver", drop_first=True, dtype=int))

    y = df["lap_duration"]

    model = LinearRegression()
    model.fit(X, y)

    coefs = pd.Series(model.coef_, index=X.columns)
    return model, coefs


def load_pits(session_key):
    return pd.read_csv(f"cache/pits_{session_key}.csv")


def race_gap(laps, driver_ahead, driver_behind):
    pair = laps[laps["driver_number"].isin([driver_ahead, driver_behind])]
    times = pair.pivot(index="lap_number", columns="driver_number", values="lap_duration")
    total = times.cumsum()
    return total[driver_behind] - total[driver_ahead]


def pit_phase_gain(laps, pits, driver_ahead, driver_behind):
    gap = race_gap(laps, driver_ahead, driver_behind)
    pair_pits = pits[pits["driver_number"].isin([driver_ahead, driver_behind])]

    first_in_lap = pair_pits["lap_number"].min()
    last_out_lap = pair_pits["lap_number"].max() + 1

    gap_before = gap.loc[first_in_lap - 1]
    gap_after = gap.loc[last_out_lap]
    return gap_before, gap_after, gap_before - gap_after