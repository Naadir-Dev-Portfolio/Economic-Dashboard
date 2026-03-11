#!/usr/bin/env python3
"""
Metric: UK 10-Year Gilt Yield

Definition:
  The UK 10-Year Gilt Yield is the annualized return on UK government
  debt maturing in 10 years.

Importance:
  • Reflects market inflation and growth expectations in the UK.
  • Yields above ~5% have historically pressured equity markets and
    signaled tighter monetary conditions.
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
SERIES       = "IRLTLT01GBM156N"  # 10-Year UK Gilt Yield
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "uk_10y_gilt_yield.xlsx")
SHEET_NAME   = "GiltYield"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch data from FRED ───────────────────────────────────────────────────────
df = pdr.DataReader(SERIES, "fred", START_DATE, END_DATE, api_key=FRED_API_KEY)
df.rename(columns={SERIES: "GiltYieldPct"}, inplace=True)
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
        "name":       "Gilt Yield (%)",
        "categories": [SHEET_NAME, 1, 0, max_row, 0],
        "values":     [SHEET_NAME, 1, 1, max_row, 1],
    })
    chart.set_title ({"name": "UK 10-Year Gilt Yield"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "Yield (%)"})
    chart.set_legend({"position": "none"})

    worksheet.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel file created: {OUT_FILE}")

# ─── Open the Excel file automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
