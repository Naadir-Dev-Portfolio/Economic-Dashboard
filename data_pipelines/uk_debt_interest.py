#!/usr/bin/env python3
"""
Metric: UK Government Debt Interest Payments

Definition:
  Monthly net interest payments on central government debt, in £ million.
  Tracks how much the government pays each month to service its debt.

Importance:
  • Payments > £15 bn/month signal rising fiscal strain.
  • Sudden jumps can force spending cuts or tax rises.
"""

import os, sys, subprocess
import pandas as pd
from dbnomics import fetch_series
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
OUT_DIR  = "data"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "uk_debt_interest.xlsx")
SHEET    = "DebtInterest"

# ─── Fetch the ONS PUSF NMFX.M series via DBnomics ─────────────────────────────
# (Central government net interest payable, GBP million, monthly)
try:
    raw = fetch_series("ONS","PUSF","NMFX.M")
except Exception as e:
    print("❌ Fetch failed:", e)
    sys.exit(1)

# ─── Clean & parse ─────────────────────────────────────────────────────────────
# Keep only the 'period' and 'value' columns
df = raw[["period","value"]].dropna().copy()
df.columns = ["Date","InterestGBPm"]

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")        # infer any ISO string
df["Date"] = df["Date"].dt.to_period("M").dt.to_timestamp("M")  

# Set index
df.set_index("Date", inplace=True)

# ─── Write to Excel with an embedded line chart ────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    df_reset = df.reset_index()
    df_reset.to_excel(writer, sheet_name=SHEET, index=False)
    workbook  = writer.book
    worksheet = writer.sheets[SHEET]

    chart = workbook.add_chart({"type":"line"})
    max_row = len(df_reset)

    chart.add_series({
        "name":       "Interest Payments (£ m)",
        "categories": [SHEET, 1, 0, max_row, 0],
        "values":     [SHEET, 1, 1, max_row, 1],
    })
    chart.set_title ({"name": "UK Govt Debt Interest Payments"})
    chart.set_x_axis({"name":"Date","date_axis":True})
    chart.set_y_axis({"name":"GBP million"})
    chart.set_legend({"position":"none"})
    worksheet.insert_chart("D2", chart, {"x_scale":1.5,"y_scale":1.2})

print(f"✅ Created {OUT_FILE}")

# ─── Open the Excel file automatically ─────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform=="darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
