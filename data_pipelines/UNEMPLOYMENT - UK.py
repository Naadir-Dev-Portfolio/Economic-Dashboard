#!/usr/bin/env python3
"""
Metric: UK Unemployment Rate

Definition:
  The UK unemployment rate measures the percentage of the UK labour force 
  that is jobless and actively seeking work, seasonally adjusted.

Importance:
  • Rising unemployment signals weakening labour markets and economic slowdown.
  • Sharp increases (>1 percentage point over 6 months) often precede recessions.

When to worry:
  If the unemployment rate exceeds ~6% or jumps rapidly (e.g., >1% in six months),
  it indicates broader economic stress and potential downturn.
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import date
from pandas_datareader import data as pdr

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "LRUN64TTGBQ156N"  # FRED code for UK Unemployment Rate
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "uk_unemployment_rate.xlsx")
SHEET_NAME   = "Unemployment_UK"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch via pandas_datareader ──────────────────────────────────────────────
try:
    df = pdr.DataReader(SERIES, "fred", START_DATE, END_DATE, api_key=FRED_API_KEY)
except Exception as e:
    print(f"❌ Failed to fetch UK unemployment: {e}")
    sys.exit(1)

# ─── Clean & align ──────────────────────────────────────────────────────────────
df.rename(columns={SERIES: "UnemploymentPct"}, inplace=True)
df.index = pd.to_datetime(df.index).to_period("M").to_timestamp("M")

# ─── Write to Excel with chart ─────────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index().rename(columns={"index": "Date"})
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    workbook  = writer.book
    worksheet = writer.sheets[SHEET_NAME]

    chart = workbook.add_chart({"type": "line"})
    max_row = len(df_reset)
    chart.add_series({
        "name":       "UK Unemployment Rate (%)",
        "categories": [SHEET_NAME, 1, 0, max_row, 0],
        "values":     [SHEET_NAME, 1, 1, max_row, 1],
    })
    chart.set_title   ({"name": "UK Unemployment Rate"})
    chart.set_x_axis  ({"name": "Date", "date_axis": True})
    chart.set_y_axis  ({"name": "Rate (%)"})
    chart.set_legend  ({"position": "none"})
    worksheet.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the Excel file automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])

