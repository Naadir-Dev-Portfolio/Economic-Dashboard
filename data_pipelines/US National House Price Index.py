#!/usr/bin/env python3
"""
Metric: US National House Price Index (Case-Shiller, Seasonally Adjusted)

Definition:
  The S&P/Case-Shiller U.S. National Home Price Index measures changes
  in the value of residential real estate nationally, seasonally adjusted.

Importance:
  • Reflects broad U.S. housing market trends and homeowner equity.  
  • Rapid increases (>5% year-over-year) can signal overheating;  
  • Declines (>5% year-over-year) signal market corrections or stress.

When to worry:
  If the index falls more than ~5% over a year, housing-market distress
  may be emerging, often preceding broader economic slowdown.
"""

import os
import sys
import subprocess
import pandas as pd
import requests
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "CSUSHPISA"   # S&P/Case-Shiller U.S. National Home Price Index, SA
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_house_price_index.xlsx")
SHEET_NAME   = "US_HPI_CS"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch observations via FRED API ──────────────────────────────────────────
url = (
    "https://api.stlouisfed.org/fred/series/observations"
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
dates, values = [], []
for o in obs:
    v = o["value"]
    if v != ".":
        dates.append(o["date"])
        values.append(float(v))
df = pd.DataFrame({"Date": pd.to_datetime(dates), "HPI": values})
df = df.set_index("Date").to_period("M").to_timestamp("M")

# ─── Write to Excel with line chart ───────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index()
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb  = writer.book
    ws  = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(df_reset)
    chart.add_series({
        "name":       "US National HPI (CS, SA)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "US National House Price Index"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Index (SA)"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open workbook automatically ───────────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])

