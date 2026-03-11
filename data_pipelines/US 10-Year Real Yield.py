#!/usr/bin/env python3
"""
Metric: US 10-Year Real Yield

Definition:
  The 10-Year Real Yield is the yield on a nominal 10-year Treasury
  minus expected inflation. It reflects the true borrowing cost
  and policy stance.

Importance:
  • Rising real yields signal tightening conditions.
  • Levels above ~2.0% often precede slowdowns or market stress.
"""

import os
import sys
import subprocess
import pandas as pd
from datetime import date
from pandas_datareader import data as pdr

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
SERIES       = "REAINTRATREARAT10Y"
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_10y_real_yield.xlsx")
SHEET_NAME   = "RealYield"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch data from FRED ───────────────────────────────────────────────────────
df = pdr.DataReader(SERIES, "fred", START_DATE, END_DATE, api_key=FRED_API_KEY)
df.rename(columns={SERIES: "RealYieldPct"}, inplace=True)
df.index = pd.to_datetime(df.index).to_period("M").to_timestamp("M")

# ─── Write to Excel with chart ──────────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter") as writer:
    df_reset = df.reset_index().rename(columns={"index": "Date"})
    df_reset.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    workbook  = writer.book
    worksheet = writer.sheets[SHEET_NAME]

    chart = workbook.add_chart({"type": "line"})
    max_row = len(df_reset)

    chart.add_series({
        "name":       "Real Yield (%)",
        "categories": [SHEET_NAME, 1, 0, max_row, 0],
        "values":     [SHEET_NAME, 1, 1, max_row, 1],
    })
    chart.set_title ({"name": "US 10-Year Real Yield"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Real Yield (%)"})
    chart.set_legend({"position": "none"})

    worksheet.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the Excel file automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
