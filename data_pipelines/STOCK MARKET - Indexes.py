#!/usr/bin/env python3
"""
Download monthly index/ETF data for major global markets, with yfinance primary
and FRED fallbacks, write to one Excel, chart each sheet, and open file.

Tickers & FRED fallback series:
  SPY   → SP500           (S&P 500 price index)
  ^FTSE → SPASTT01GBM661N (UK share prices, index 2015=100)
  ^DJI  → DJIA            (Dow Jones Industrial Avg)
  ^IXIC → NASDAQCOM       (NASDAQ Composite)
  EWJ   → SPASTT01JPM657N (Japan share prices, index 2015=100)
  FXI   → SPASTT01CNM657N (China share prices, index 2015=100)
  VGK   → FRED not available; uses yfinance only
  EWG   → SPASTT01DEM661N (Germany share prices, index 2015=100)
  EWQ   → SPASTT01FRM661N (France share prices, index 2015=100)
"""

import os
import sys
import subprocess
from datetime import date

import pandas as pd
from pandas_datareader import data as pdr

# ensure yfinance
try:
    import yfinance as yf
except ImportError:
    print("Install yfinance: pip install yfinance")
    sys.exit(1)

# config
START="1970-01-01"
END=date.today().strftime("%Y-%m-%d")
OUT_DIR="data"
OUT_FILE=os.path.join(OUT_DIR,"global_markets.xlsx")
os.makedirs(OUT_DIR, exist_ok=True)

# mapping ticker -> (label, fallback_fred)
MAPPING = {
    # US
    "SPY":   ("S&P 500 TR (SPY)",           "SP500"),            # US equity proxy
    "^DJI":  ("Dow Jones Industrial Avg",    "DJIA"),
    "^IXIC": ("NASDAQ Composite",           "NASDAQCOM"),

    # UK
    "^FTSE": ("FTSE 100",                   "SPASTT01GBM661N"),  # UK share prices

    # Japan
    "EWJ":   ("iShares MSCI Japan ETF",     "SPASTT01JPM657N"),  # Japan equity ETF
                                          
    # China
    "FXI":   ("iShares China Large-Cap ETF","SPASTT01CNM657N"),  # Top 50 Chinese firms (HK-listed)
    "^HSI":  ("Hang Seng Index",            None),               # Broader HK equity index

    # Europe
    "VGK":   ("Vanguard FTSE Europe ETF",   None),               # Pan-Europe ETF
    "EWG":   ("iShares MSCI Germany ETF",   "SPASTT01DEM661N"),  # Germany share index
    "EWQ":   ("iShares MSCI France ETF",    "SPASTT01FRM661N"),  # France share index
}

with pd.ExcelWriter(OUT_FILE, engine="xlsxwriter", datetime_format='yyyy-mm-dd') as writer:
    book = writer.book
    skipped=[]
    for ticker,(label,fallback) in MAPPING.items():
        df=None
        # attempt yfinance
        try:
            tmp = yf.download(ticker, start=START, end=END, progress=False)[["Adj Close"]]
            tmp.index=pd.to_datetime(tmp.index)
            df=tmp.resample("M").last()
            df.index=df.index.to_period("M").to_timestamp("M")
            df.columns=["Value"]
        except Exception as e:
            print(f"⚠ yfinance failed for {ticker}: {e}")
        # fallback to FRED if no df and fallback provided
        if (df is None or df.empty) and fallback:
            try:
                tmp = pdr.DataReader(fallback, "fred", START, END, api_key="dc30946f9c9493ee4a04e3b3a1731ab2")
                tmp.rename(columns={fallback:"Value"}, inplace=True)
                tmp.index=pd.to_datetime(tmp.index).to_period("M").to_timestamp("M")
                df=tmp
            except Exception as e:
                print(f"⚠ FRED fallback failed for {fallback}: {e}")
        if df is None or df.empty:
            skipped.append(ticker)
            continue
        # write sheet
        sheet=ticker.strip("^")[:31]
        out=df.reset_index().rename(columns={"index":"Date"})
        out.to_excel(writer, sheet_name=sheet, index=False)
        ws=writer.sheets[sheet]
        # add chart
        chart=book.add_chart({"type":"line"})
        r=len(out)
        chart.add_series({
            "name":label,
            "categories":[sheet,1,0,r,0],
            "values":[sheet,1,1,r,1],
        })
        chart.set_title({"name": label})
        chart.set_x_axis({"name":"Date","date_axis":True})
        chart.set_y_axis({"name":"Value"})
        chart.set_legend({"position":"none"})
        ws.insert_chart("D2", chart, {"x_scale":1.4,"y_scale":1.2})
    print(f"\n✅ Written to {OUT_FILE}")
    if skipped:
        print("Skipped:", skipped)

# open file
if sys.platform.startswith("win"):
    os.startfile(OUT_FILE)
else:
    cmd="open" if sys.platform=="darwin" else "xdg-open"
    subprocess.call([cmd, OUT_FILE])
