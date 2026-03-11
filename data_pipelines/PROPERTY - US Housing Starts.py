#!/usr/bin/env python3
"""
Metric: US Housing Starts (Monthly, SAAR)

Definition:
  Housing Starts measures the number of new residential building
  construction projects begun in the U.S., seasonally adjusted
  at an annual rate (SAAR).

Importance:
  • A key forward-looking indicator for the construction sector.
  • Declines often presage broader housing-market slowdowns.
  • Sharp drops (>10% in six months) can signal economic weak spots.

When to worry:
  If Housing Starts fall rapidly (e.g., >10% over two consecutive quarters),
  it may indicate housing bust risk and broader economic downturn.
"""

import os
import sys
import subprocess
import requests
import pandas as pd
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "HOUST"     # FRED code for US Housing Starts (SAAR)
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_housing_starts.xlsx")
SHEET_NAME   = "HousingStarts"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch via FRED API ─────────────────────────────────────────────────────────
url = (
    f"https://api.stlouisfed.org/fred/series/observations"
    f"?series_id={SERIES}"
    f"&api_key={FRED_API_KEY}"
    f"&file_type=json"
    f"&observation_start={START_DATE}"
    f"&observation_end={END_DATE}"
    f"&frequency=m"
)
resp = requests.get(url)
resp.raise_for_status()
obs = resp.json().get("observations", [])

# ─── Parse into DataFrame ─────────────────────────────────────────────────────
dates = []
values = []
for o in obs:
    if o["value"] != ".":
        dates.append(o["date"])
        values.append(float(o["value"]))
df = pd.DataFrame({"Date": pd.to_datetime(dates), "HousingStarts_SAAR": values})
df = df.set_index("Date").to_period("M").to_timestamp("M")

# ─── Write to Excel with line chart ────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index()
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(df_reset)
    chart.add_series({
        "name":       "Housing Starts (SAAR, '000s)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "US Housing Starts (SAAR)"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Starts (thousands)"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open workbook automatically ────────────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
