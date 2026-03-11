#!/usr/bin/env python3
"""
Metric: Shiller CAPE (Cyclically Adjusted P/E) via web scrape

Definition:
  Ratio of S&P 500 price to 10-year avg earnings. CAPE >30 often precedes crashes.

This version fixes date parsing for entries like "Aug 1, 2025".
"""

import os
import sys
import subprocess
import io
import pandas as pd
import requests
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
URL       = "https://www.multpl.com/shiller-pe/table"
OUT_DIR   = "data"
OUT_FILE  = os.path.join(OUT_DIR, "us_shiller_cape.xlsx")
SHEET     = "Shiller_CAPE"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch and parse HTML ───────────────────────────────────────────────────────
resp = requests.get(URL, headers={"User-Agent":"Mozilla/5.0"})
resp.raise_for_status()
# Use StringIO to avoid deprecation warning
tables = pd.read_html(io.StringIO(resp.text))
df = tables[0].copy()

# Expect columns ["Date", "Value"]
df.columns = ["Date", "Shiller_CAPE"]

# ─── Parse dates with day included, then align to month-end ────────────────────
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # handles "Aug 1, 2025"
df = df.dropna(subset=["Date", "Shiller_CAPE"])
df = df.set_index("Date").sort_index()
df.index = df.index.to_period("M").to_timestamp("M")

# ─── Write to Excel with line chart ────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index()
    out.to_excel(writer, sheet_name=SHEET, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET]
    chart = wb.add_chart({"type": "line"})
    rows = len(out)
    chart.add_series({
        "name":       "Shiller CAPE",
        "categories": [SHEET, 1, 0, rows, 0],
        "values":     [SHEET, 1, 1, rows, 1],
    })
    chart.set_title({"name": "Shiller CAPE Ratio"})
    chart.set_x_axis({"name": "Date", "date_axis": True})
    chart.set_y_axis({"name": "CAPE Ratio"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the workbook automatically ───────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform=="darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
