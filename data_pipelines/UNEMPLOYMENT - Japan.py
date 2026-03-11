#!/usr/bin/env python3
"""
Metric: Japan Unemployment Rate via FRED API

Definition:
  The unemployment rate measures the percentage of the Japanese labor force 
  that is jobless and actively seeking work, seasonally adjusted.

Importance:
  • Rising unemployment signals weakening labor markets and economic slowdown.  
  • Sharp increases (>1 percentage point over six months) often precede downturns.

When to worry:
  If unemployment exceeds ~5% or jumps by more than 1 percentage point within six months,
  it indicates increased economic stress.
"""

import os
import sys
import subprocess
import pandas as pd
import requests
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "LRHUTTTTJPM156S"  # FRED code for Japan unemployment rate (OECD via FRED)
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "jpn_unemployment_rate.xlsx")
SHEET_NAME   = "Unemployment_JPN"

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
observations = resp.json().get("observations", [])

# ─── Parse into DataFrame ─────────────────────────────────────────────────────
dates = []
values = []
for obs in observations:
    val = obs["value"]
    if val != ".":
        dates.append(obs["date"])
        values.append(float(val))
df = pd.DataFrame({"Date": pd.to_datetime(dates), "UnemploymentPct": values})
df = df.set_index("Date").to_period("M").to_timestamp("M")

# ─── Write to Excel with line chart ───────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index()
    out.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(out)
    chart.add_series({
        "name":       "Japan Unemployment (%)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "Japan Unemployment Rate"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Rate (%)"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open workbook automatically ────────────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
