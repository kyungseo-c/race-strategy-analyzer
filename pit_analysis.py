from analysis import load_session, load_pits, pit_phase_gain

SESSION_KEY = 9912

laps, stints = load_session(SESSION_KEY)
pits = load_pits(SESSION_KEY)

print(pits[pits["driver_number"].isin([1, 16])][["driver_number", "lap_number", "stop_duration", "lane_duration"]])
print()

before, after, gain = pit_phase_gain(laps, pits, driver_ahead=1, driver_behind=16)
print(f"Abstand vor den Stopps:  {before:.2f} s")
print(f"Abstand nach den Stopps: {after:.2f} s")
print(f"Gewinn LEC durch Undercut: {gain:.2f} s")