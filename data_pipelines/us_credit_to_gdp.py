#!/usr/bin/env python3
"""
Metric: US Credit-to-GDP Ratio (via FRED API)

Definition:
  The ratio of total credit market debt outstanding to GDP (percentage).
  Measures the economy’s overall leverage level.

Importance:
  • High ratios (>150%) signal elevated financial leverage.
  • Rapid increases can foreshadow credit stress or deleveraging.
  • Persistent levels above ~150% indicate heightened default risk.
"""

import os, sys, subprocess, requests, pandas as pd
from datetime import date

# ─── Configuration ─────────────────────────────────────────────────────────────
FRED_API_KEY = os.getenv("FRED_API_KEY", "YOUR_FRED_API_KEY_HERE")
START_DATE   = "1970-01-01"
END_DATE     = date.today().strftime("%Y-%m-%d")
OUT_DIR      = "data"
OUT_FILE     = os.path.join(OUT_DIR, "us_credit_to_gdp.xlsx")
SHEET_NAME   = "Credit_to_GDP"

os.makedirs(OUT_DIR, exist_ok=True)

def fetch_fred_series(series_id, start, end, freq="q"):
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}"
        f"&api_key={FRED_API_KEY}"
        f"&file_type=json"
        f"&observation_start={start}"
        f"&observation_end={end}"
        f"&frequency={freq}"
    )
    r = requests.get(url)
    r.raise_for_status()
    obs = r.json()["observations"]
    dates = [o["date"] for o in obs]
    vals  = [None if o["value"]=="." else float(o["value"]) for o in obs]
    return pd.Series(vals, index=pd.to_datetime(dates), name=series_id)

# ─── Fetch credit & GDP ────────────────────────────────────────────────────────
credit = fetch_fred_series("TCMDO", START_DATE, END_DATE, freq="q")
gdp    = fetch_fred_series("GDP",   START_DATE, END_DATE, freq="q")

# ─── Compute ratio & align ─────────────────────────────────────────────────────
df = pd.concat([credit, gdp], axis=1)
df.columns = ["Credit", "GDP"]
df["Credit_to_GDP_pct"] = df["Credit"] / df["GDP"] * 100
df.index = df.index.to_period("Q").to_timestamp("Q")

# ─── Write to Excel + chart ────────────────────────────────────────────────────
with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    out = df[["Credit_to_GDP_pct"]].reset_index().rename(columns={"index":"Date"})
    out.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    wb = writer.book
    ws = writer.sheets[SHEET_NAME]

    chart = wb.add_chart({"type":"line"})
    max_row = len(out)
    chart.add_series({
        "name":       "Credit-to-GDP (%)",
        "categories": [SHEET_NAME, 1, 0, max_row, 0],
        "values":     [SHEET_NAME, 1, 1, max_row, 1],
    })
    chart.set_title ({"name":"US Credit-to-GDP Ratio"})
    chart.set_x_axis({"name":"Date","date_axis":True})
    chart.set_y_axis({"name":"Percent"})
    chart.set_legend({"position":"none"})
    ws.insert_chart("D2", chart, {"x_scale":1.5,"y_scale":1.2})

print(f"✅ Excel file created: {OUT_FILE}")

# ─── Open file automatically ───────────────────────────────────────────────────
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    opener = "open" if sys.platform=="darwin" else "xdg-open"
    subprocess.call([opener, OUT_FILE])
