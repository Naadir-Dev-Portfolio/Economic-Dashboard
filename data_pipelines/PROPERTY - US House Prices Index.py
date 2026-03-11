#!/usr/bin/env python3
"""
Metric: US National House Price Index (Case-Shiller, Seasonally Adjusted)

Definition:
  The S&P/Case-Shiller U.S. National Home Price Index measures changes
  in residential real estate values, seasonally adjusted.

Importance:
  • Reflects broad housing-market trends and homeowner equity.
  • Rapid >5% YoY increases can signal overheating.
  • Declines >5% YoY can signal market corrections or stress.

When to worry:
  Sustained >5% decline over 12 months often precedes broader downturns.
"""

import os, sys, subprocess
import pandas as pd
import requests
from datetime import date

# Try to import for fallback
try:
    from pandas_datareader import data as pdr
except ImportError:
    pdr = None

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
SERIES       = "CSUSHPISA"    # Case-Shiller U.S. National HPI, SA
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_house_price_index.xlsx")
SHEET_NAME   = "US_HPI_CS"

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Fetch via FRED API ─────────────────────────────────────────────────────────
df = None
try:
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={SERIES}&api_key={FRED_API_KEY}"
        f"&file_type=json&observation_start={START_DATE}"
        f"&observation_end={END_DATE}&frequency=m"
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
    print("✔ Fetched HPI via FRED API")
except Exception as e:
    print(f"⚠ API fetch failed: {e}")
    if pdr:
        try:
            df = pdr.DataReader(SERIES, "fred",
                                START_DATE, END_DATE,
                                api_key=FRED_API_KEY)
            df.rename(columns={SERIES:"HPI"}, inplace=True)
            df.index = pd.to_datetime(df.index)
            print("✔ Fetched HPI via pandas_datareader")
        except Exception as e2:
            print(f"❌ pandas_datareader fetch failed: {e2}")
    else:
        print("❌ pandas_datareader not installed; cannot fallback.")
    if df is None:
        sys.exit(1)

# ─── Align to month-end ─────────────────────────────────────────────────────────
df = df.to_period("M").to_timestamp("M")

# ─── Write to Excel + line chart ───────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df.reset_index().rename(columns={"index":"Date"})
    out.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]
    chart = wb.add_chart({"type":"line"})
    rows = len(out)
    chart.add_series({
        "name":       "US National HPI (CS, SA)",
        "categories": [SHEET_NAME, 1, 0, rows, 0],
        "values":     [SHEET_NAME, 1, 1, rows, 1],
    })
    chart.set_title({"name":"US National House Price Index"})
    chart.set_x_axis({"name":"Date","date_axis":True})
    chart.set_y_axis({"name":"Index (SA)"})
    chart.set_legend({"position":"none"})
    ws.insert_chart("D2", chart, {"x_scale":1.5,"y_scale":1.2})

print(f"✅ Excel file created: {OUT_FILE}")

# ─── Open workbook automatically ────────────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform=="darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
