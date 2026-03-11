#!/usr/bin/env python3
"""
Metric: Japan Residential Property Price Index (Real, BIS - QJPR368BIS)

Definition:
  The real residential property price index for Japan (2010=100), 
  published by BIS. Measures inflation-adjusted housing prices.

Importance:
  • Tracks long-term housing valuation trends.  
  • >5% quarter-over-quarter changes signal rapid market swings.  
  • Persistent declines warn of housing-market stress.

When to worry:
  If the index falls by >5% q/q, it indicates significant market correction risk.
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

# ─── Config ────────────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES = "QJPR368BIS"  # Real Residential Property Prices for Japan [2010=100] citeturn0search1
START = "1970-01-01"
END   = date.today().strftime("%Y-%m-%d")
OUT_DIR = "data"
OUT_FILE = os.path.join(OUT_DIR, "jpn_residential_property_prices.xlsx")
SHEET = "JPN_HPI"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch via FRED API ────────────────────────────────────────────────────────
df = None
try:
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={SERIES}&api_key={FRED_API_KEY}"
        f"&file_type=json&observation_start={START}"
        f"&observation_end={END}&frequency=q"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    obs = resp.json().get("observations", [])
    dates, vals = [], []
    for o in obs:
        if o["value"] != ".":
            dates.append(o["date"])
            vals.append(float(o["value"]))
    df = pd.DataFrame({"Date": pd.to_datetime(dates), "HPI": vals})
    df = df.set_index("Date")
    print("✔ Fetched Japan HPI via FRED API")
except Exception as e:
    print(f"⚠ API fetch failed: {e}")
    if pdr:
        try:
            df = pdr.DataReader(SERIES, "fred", START, END, api_key=FRED_API_KEY)
            df.rename(columns={SERIES: "HPI"}, inplace=True)
            df.index = pd.to_datetime(df.index)
            print("✔ Fetched Japan HPI via pandas_datareader")
        except Exception as e2:
            print(f"❌ pandas_datareader fetch failed: {e2}")
    if df is None:
        sys.exit(1)

# Align to quarter-end
df = df.to_period("Q").to_timestamp("Q")

# ─── Write to Excel + chart ────────────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index().rename(columns={"index": "Date"})
    out.to_excel(writer, sheet_name=SHEET, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET]
    chart = wb.add_chart({"type": "line"})
    rows = len(out)
    chart.add_series({
        "name":       "Japan Real HPI (2010=100)",
        "categories": [SHEET, 1, 0, rows, 0],
        "values":     [SHEET, 1, 1, rows, 1],
    })
    chart.set_title({"name": "Japan Residential Property Prices"})
    chart.set_x_axis({"name": "Quarter End", "date_axis": True})
    chart.set_y_axis({"name": "Index (2010=100)"})
    chart.set_legend({"position": "none"})
    ws.insert_chart("D2", chart, {"x_scale": 1.5, "y_scale": 1.2})

print(f"✅ Excel workbook created: {OUT_FILE}")

# Open workbook
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    cmd = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([cmd, OUT_FILE])
