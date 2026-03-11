#!/usr/bin/env python3
"""
Metric: China Residential Property Prices (BIS, QCNN368BIS)

Definition:
  The quarterly index of residential property prices for China (2010=100),
  published by the Bank for International Settlements via FRED.

Importance:
  • Tracks housing market valuation trends in China.
  • Quarter-over-quarter moves >5% signal rapid market swings.  
  • Sustained declines >5% q/q can presage broader economic slowdown.

When to worry:
  If the index falls by more than ~5% compared to the previous quarter,
  significant housing-market stress may be underway.
"""

import os
import sys
import subprocess
import pandas as pd
import requests
from datetime import date

# Try pandas_datareader fallback
try:
    from pandas_datareader import data as pdr
except ImportError:
    pdr = None

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "QCNN368BIS"  # Residential Property Prices for China citeturn1search5
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "chn_residential_property_prices.xlsx")
SHEET_NAME   = "CHN_HPI_BIS"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch via FRED API ─────────────────────────────────────────────────────────
df = None
url = (
    "https://api.stlouisfed.org/fred/series/observations"
    f"?series_id={SERIES}&api_key={FRED_API_KEY}"
    "&file_type=json"
    f"&observation_start={START_DATE}&observation_end={END_DATE}&frequency=q"
)
try:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    obs = r.json().get("observations", [])
    dates, vals = [], []
    for o in obs:
        if o["value"] != ".":
            dates.append(o["date"])
            vals.append(float(o["value"]))
    df = pd.DataFrame({"Date": pd.to_datetime(dates), "HPI_Index": vals})
    df.set_index("Date", inplace=True)
    print("✔ Fetched China HPI via FRED API")
except Exception as e:
    print(f"⚠ FRED API fetch failed: {e}")
    if pdr:
        try:
            df = pdr.DataReader(SERIES, "fred", START_DATE, END_DATE, api_key=FRED_API_KEY)
            df.rename(columns={SERIES: "HPI_Index"}, inplace=True)
            df.index = pd.to_datetime(df.index)
            print("✔ Fetched China HPI via pandas_datareader")
        except Exception as e2:
            print(f"❌ pandas_datareader fetch failed: {e2}")
    if df is None:
        sys.exit(1)

# Align to quarter-end
df = df.to_period("Q").to_timestamp("Q")

# ─── Write to Excel with chart ─────────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index().rename(columns={"index": "Date"})
    out.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type": "line"})
    rows = len(out)
    chart.add_series({
        "name":       "China Property Price Index (2010=100)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name": "China Residential Property Prices"})
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
