#!/usr/bin/env python3
"""
Metric: Australia Residential Property Prices (BIS, QAUN628BIS)

Definition:
  The quarterly index of residential property prices for Australia (2010=100),
  published by the Bank for International Settlements.

Importance:
  • Tracks broad housing-market valuation trends in Australia.  
  • Quarter-over-quarter changes >5% signal rapid market moves.  
  • Sustained declines >5% q/q can presage broader economic slowdown.

When to worry:
  If the index falls by more than ~5% compared to the previous quarter,
  significant housing-market stress may be underway.
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import date
from pandas_datareader import data as pdr

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "QAUN628BIS"   # BIS Australia residential property prices (2010=100)
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "aus_residential_property_prices.xlsx")
SHEET_NAME   = "AUS_HPI_BIS"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch via pandas_datareader ───────────────────────────────────────────────
try:
    df = pdr.DataReader(SERIES, "fred", START_DATE, END_DATE, api_key=FRED_API_KEY)
except Exception as e:
    print("❌ Failed to fetch Australia HPI:", e)
    sys.exit(1)

# ─── Clean & align ──────────────────────────────────────────────────────────────
df.rename(columns={SERIES: "HPI_Index"}, inplace=True)
df.index = pd.to_datetime(df.index).to_period("Q").to_timestamp("Q")

# ─── Write to Excel with line chart ────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index().rename(columns={"index": "Date"})
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    workbook  = writer.book
    worksheet = writer.sheets[SHEET_NAME]

    chart = workbook.add_chart({"type": "line"})
    max_row = len(df_reset)
    chart.add_series({
        "name":       "AUS Property Price Index (2010=100)",
        "categories": [SHEET_NAME, 1, 0, max_row, 0],
        "values":     [SHEET_NAME, 1, 1, max_row, 1],
    })
    chart.set_title   ({"name": "Australia Residential Property Prices"})
    chart.set_x_axis  ({"name": "Quarter End", "date_axis": True})
    chart.set_y_axis  ({"name": "Index (2010=100)"})
    chart.set_legend  ({"position": "none"})
    worksheet.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the Excel file automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
