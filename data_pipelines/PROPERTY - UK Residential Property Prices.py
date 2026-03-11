#!/usr/bin/env python3
"""
Metric: UK Residential Property Prices (BIS, QGBN628BIS)

Definition:
  Quarterly index of residential property prices for the United Kingdom,
  published by the Bank for International Settlements (2010=100).

Importance:
  • Tracks broad UK house-price movements.  
  • Rapid index jumps (>5% q/q) can signal overheating or bubble risk.  
  • Sharp declines (>5% q/q) often coincide with market corrections.

When to worry:
  If the quarterly index rises or falls by more than ~5% compared to
  the previous quarter, it indicates significant market stress.
"""

import os
import sys
import subprocess
import pandas as pd
import requests
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "QGBN628BIS"   # BIS UK residential property prices (2010=100)
START_DATE   = "1920-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "uk_residential_property_prices.xlsx")
SHEET_NAME   = "UK_HPI_BIS"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch quarterly data via FRED API ────────────────────────────────────────
url = (
    "https://api.stlouisfed.org/fred/series/observations"
    f"?series_id={SERIES}"
    f"&api_key={FRED_API_KEY}"
    f"&file_type=json"
    f"&observation_start={START_DATE}"
    f"&observation_end={END_DATE}"
    f"&frequency=q"
)
resp = requests.get(url)
resp.raise_for_status()
obs = resp.json().get("observations", [])

# ─── Parse into DataFrame ─────────────────────────────────────────────────────
dates, values = [], []
for o in obs:
    if o["value"] != ".":
        dates.append(pd.to_datetime(o["date"]))
        values.append(float(o["value"]))
df = pd.DataFrame({"Date": dates, "HPI_Index": values})
df = df.set_index("Date").to_period("Q").to_timestamp("Q")

# ─── Write to Excel with line chart ───────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index()
    out.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(out)
    chart.add_series({
        "name":       "UK Property Price Index (2010=100)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "UK Residential Property Prices (BIS)"})
    chart.set_x_axis({"name": "Quarter End", "date_axis": True})
    chart.set_y_axis({"name": "Index (2010=100)"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# ─── Open the workbook automatically ───────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
