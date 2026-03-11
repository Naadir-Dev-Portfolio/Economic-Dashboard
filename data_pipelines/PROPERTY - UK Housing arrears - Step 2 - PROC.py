#!/usr/bin/env python3
"""
Step 3: Combine UK mortgage‐arrears rate (cases) and possession stats 
         into one Excel sheet with a line chart, then open it.

Metrics:
  • arrears_rate_cases       – “TOTAL” under (ii) Number of cases in arrears
  • new_possessions          – New possessions in quarter
  • possession_sales         – Possession sales in quarter
  • stock_possessions        – Stock of possessions at end of quarter
"""

import os
import datetime
import pandas as pd
import subprocess
import sys

# ─── Configuration ─────────────────────────────────────────────────────────────
IN_FILE   = "data/mlar-longrun-summary.xlsx"
SHEET_IDX = 3  # zero-based index for “Arrears and provisions” sheet
OUT_DIR   = "data"
OUT_FILE  = os.path.join(OUT_DIR, "uk_arrears_possessions.xlsx")
os.makedirs(OUT_DIR, exist_ok=True)

# ─── Load raw sheet ────────────────────────────────────────────────────────────
raw = pd.read_excel(IN_FILE, sheet_name=SHEET_IDX, header=None)

# Rows containing year and quarter headers
YEAR_ROW    = 12
QUARTER_ROW = 13

# Mapping: metric name → row number in raw sheet
mapping = {
    "arrears_rate_cases": 44,
    "new_possessions":    50,
    "possession_sales":   51,
    "stock_possessions":  52,
}

# Build list of (col, date) for each quarter column
year = None
col_dates = []
ncols = raw.shape[1]
for col in range(ncols):
    y = raw.iat[YEAR_ROW, col]
    if pd.notna(y):
        try:
            year = int(y)
        except:
            pass
    q = raw.iat[QUARTER_ROW, col]
    if year and isinstance(q, str):
        q = q.strip().upper()
        if q == "Q1":
            dt = datetime.date(year,  3, 31)
        elif q == "Q2":
            dt = datetime.date(year,  6, 30)
        elif q == "Q3":
            dt = datetime.date(year,  9, 30)
        elif q == "Q4":
            dt = datetime.date(year, 12, 31)
        else:
            continue
        col_dates.append((col, dt))

# Extract each metric series
data = {}
for metric, row_idx in mapping.items():
    series = []
    for col, dt in col_dates:
        v = raw.iat[row_idx, col]
        if pd.notna(v):
            series.append((dt, v))
    data[metric] = pd.Series({dt: val for dt, val in series})

# Combine into a DataFrame
df = pd.DataFrame(data).sort_index()
df.index.name = "Date"

# ─── Write to Excel with chart ────────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format='yyyy-mm-dd') as writer:
    df_reset = df.reset_index()
    df_reset.to_excel(writer, sheet_name="ArrearsPoss", index=False)
    workbook  = writer.book
    worksheet = writer.sheets["ArrearsPoss"]

    # Create a line chart with all four series
    chart = workbook.add_chart({"type": "line"})
    max_row = len(df_reset)
    for i, metric in enumerate(df.columns, start=1):
        chart.add_series({
            "name":       metric,
            "categories": ["ArrearsPoss", 1, 0, max_row, 0],
            "values":     ["ArrearsPoss", 1, i, max_row, i],
        })
    chart.set_title ({ "name": "UK Arrears & Possessions" })
    chart.set_x_axis({ "name": "Quarter End", "date_axis": True })
    chart.set_y_axis({ "name": "Percent / Counts" })
    chart.set_legend({ "position": "bottom" })
    worksheet.insert_chart("G2", chart, {"x_scale": 1.4, "y_scale": 1.2})

print(f"✅ Written combined data + chart to {OUT_FILE}")

# ─── Open the Excel file automatically ────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
