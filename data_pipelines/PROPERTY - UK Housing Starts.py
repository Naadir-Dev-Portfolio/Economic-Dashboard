#!/usr/bin/env python3
"""
Metric: UK Dwelling Starts (Number of Dwellings Started, Quarterly)

Definition:
  Work Started: Construction: Dwellings and Residential Buildings: Total 
  for the United Kingdom (number of units begun), seasonally adjusted.

Importance:
  • Tracks new housing supply—key for construction activity and economic growth.
  • A sharp decline (>10% year-over-year) signals housing-market cooling.
  • Prolonged weakness can presage broader economic slowdown.

When to worry:
  If quarterly starts fall >10% compared to the same quarter a year earlier,
  the housing sector may be entering a downturn.
"""

import os
import sys
import subprocess
import pandas as pd
import requests
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "WSCNDW01GBQ470S"  # Work Started: Dwellings (UK)
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "uk_dwelling_starts.xlsx")
SHEET_NAME   = "DwellingStarts"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch quarterly data via FRED API ────────────────────────────────────────
url = (
    f"https://api.stlouisfed.org/fred/series/observations"
    f"?series_id={SERIES}"
    f"&api_key={FRED_API_KEY}"
    f"&file_type=json"
    f"&observation_start={START_DATE}"
    f"&observation_end={END_DATE}"
    f"&frequency=q"
)
resp = requests.get(url)
resp.raise_for_status()
data = resp.json().get("observations", [])

# ─── Parse into DataFrame ─────────────────────────────────────────────────────
dates = []
values = []
for obs in data:
    if obs["value"] != ".":
        dates.append(pd.to_datetime(obs["date"]))
        values.append(float(obs["value"]))
df = pd.DataFrame({"Date": dates, "DwellingStarts": values})
df = df.set_index("Date").to_period("Q").to_timestamp("Q")

# ─── Write to Excel with line chart ───────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index()
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(df_reset)
    chart.add_series({
        "name":       "Dwelling Starts (units)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "UK Dwelling Starts (Quarterly)"})
    chart.set_x_axis({"name": "Quarter End", "date_axis": True})
    chart.set_y_axis({"name": "Number of Units"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the workbook automatically ──────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
