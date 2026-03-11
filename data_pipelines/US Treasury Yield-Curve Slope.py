#!/usr/bin/env python3
"""
Metric: US Treasury Yield-Curve Slope (10-Year minus 2-Year)

Definition:
  The yield-curve slope measures the difference between the 10-year and
  2-year U.S. Treasury yields (in percentage points). It reflects market
  expectations for future growth and inflation.

Importance:
  • A positive slope indicates normal upward-sloping yield curve (growth expectations).  
  • An inverted curve (slope < 0) has preceded every U.S. recession since 1955.  
  • Sustained inversion (>3 months) is a strong recession warning.

When to worry:
  If the slope turns negative and remains below 0 for several months,
  economic slowdown and market risk increase.
"""

import os
import sys
import subprocess
import requests
import pandas as pd
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "T10Y2Y"             # FRED series for 10Y minus 2Y slope (in %)
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_yield_curve_slope.xlsx")
SHEET_NAME   = "YC_Slope"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch observations via FRED API ──────────────────────────────────────────
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
data = resp.json().get("observations", [])

# ─── Parse into DataFrame ─────────────────────────────────────────────────────
dates = []
values = []
for obs in data:
    val = obs["value"]
    if val != ".":
        dates.append(obs["date"])
        values.append(float(val))
df = pd.DataFrame({"Date": pd.to_datetime(dates), "SlopePct": values})
df = df.set_index("Date").to_period("M").to_timestamp("M")

# ─── Write to Excel with line chart ───────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index()
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(df_reset)
    chart.add_series({
        "name":       "10Y-2Y Slope (%)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "US Yield-Curve Slope (10Y–2Y)"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Slope (%)"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the workbook automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
