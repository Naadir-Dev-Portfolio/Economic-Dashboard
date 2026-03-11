#!/usr/bin/env python3
"""
Metric: Euro Area Unemployment Rate via FRED API

Definition:
  The Euro Area unemployment rate measures the percentage of the labor force 
  in the Eurozone (19 countries) that is jobless and actively seeking work,
  seasonally adjusted.

Importance:
  • Reflects health of the broader European economy and consumer demand.
  • Surges (>1 percentage point over six months) often signal economic slowdown.
  • Divergence from ECB targets can influence monetary policy decisions.

When to worry:
  If unemployment rises above ~10% or increases by more than 1 percentage point
  over six months, it indicates significant labor-market weakness.
"""

import os
import sys
import subprocess
import pandas as pd
import requests
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "LRHUTTTTEUM156S"  # Euro Area unemployment rate (OECD via FRED)
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "eur_unemployment_rate.xlsx")
SHEET_NAME   = "Unemployment_EUR"

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

# ─── Write to Excel with chart ───────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index()
    out.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(out)
    chart.add_series({
        "name":       "Euro Area Unemployment (%)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "Euro Area Unemployment Rate"})
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
