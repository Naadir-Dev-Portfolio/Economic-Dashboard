#!/usr/bin/env python3
"""
Metric: US Leading Economic Index (Conference Board LEI)

Definition:
  The LEI aggregates ten leading indicators (e.g., manufacturing orders,
  stock prices, jobless claims) into a composite index (2016=100).

Importance:
  • A sustained drop (>2% over six months) signals weakening economic momentum.
  • Historically, six-month LEI declines precede U.S. recessions.

When to worry:
  If LEI falls by more than ~2% over the prior six months, recession odds rise sharply.
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
SERIES       = "USSLIND"            # FRED code for Leading Index (2016=100)
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_leading_economic_index.xlsx")
SHEET_NAME   = "LEI"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch data from FRED ───────────────────────────────────────────────────────
try:
    df = pdr.DataReader(SERIES, "fred", START_DATE, END_DATE, api_key=FRED_API_KEY)
except Exception as e:
    print("❌ Failed to fetch LEI:", e)
    sys.exit(1)

df.rename(columns={SERIES: "LEI_Index"}, inplace=True)
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
        "name":       "LEI (2016=100)",
        "categories": [SHEET_NAME, 1, 0, max_row, 0],
        "values":     [SHEET_NAME, 1, 1, max_row, 1],
    })
    chart.set_title ({"name": "US Leading Economic Index"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Index (2016=100)"})
    chart.set_legend({"position": "none"})

    worksheet.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel file created: {OUT_FILE}")

# ─── Open the Excel file automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
