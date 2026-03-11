# Global Economic Intelligence Dashboard

> 20+ live macroeconomic indicators · 8 countries · Python data pipelines · Plotly visualisation

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FRED API](https://img.shields.io/badge/FRED_API-St._Louis_Fed-CC0000)](https://fred.stlouisfed.org)
[![Status](https://img.shields.io/badge/Status-In_Development-amber)](https://github.com/Naadir-Dev-Portfolio/Python-Economic-Dashboard)

---

## Overview

A comprehensive macroeconomic monitoring dashboard that tracks the indicators serious investors
and analysts actually watch. Each script is a self-contained data pipeline: it fetches data from
FRED (Federal Reserve Economic Data) or other sources, processes it, and exports a clean Excel/CSV.
The front-end dashboard (in development) will display all indicators in a single live web interface.

---

## Indicators Tracked

### 🏦 Fixed Income / Rates
| Script | Indicator | Source |
|--------|-----------|--------|
| `US Treasury Yield-Curve Slope.py` | 10Y minus 2Y US Treasuries | FRED |
| `UK 10-Year Gilt Yield.py` | UK Government 10-Year bond yield | FRED |
| `US 10-Year Real Yield.py` | TIPS-implied real yield | FRED |

### 🏠 Housing & Property
| Script | Indicator | Source |
|--------|-----------|--------|
| `PROPERTY - UK Residential Property Prices.py` | UK HPI | FRED / ONS |
| `PROPERTY - US House Prices Index.py` | Case-Shiller US HPI | FRED |
| `PROPERTY - US Housing Starts.py` | US new residential construction | FRED |
| `PROPERTY - UK Housing Starts.py` | UK new build starts | FRED |
| `PROPERTY - UK Housing arrears - Step 1/2.py` | UK mortgage arrears pipeline | FRED |
| `PROPERTY - Australia Residential Property Prices.py` | AUS property prices | FRED |
| `PROPERTY - China Residential Property Prices.py` | China new home prices | FRED |
| `PROPERTY - Japan Residential Property Price Index.py` | Japan land/housing index | FRED |
| `US National House Price Index.py` | FHFA national HPI | FRED |

### 📊 Equity & Valuation
| Script | Indicator | Source |
|--------|-----------|--------|
| `Shiller CAPE.py` | Cyclically Adjusted P/E Ratio | Shiller / FRED |
| `STOCK MARKET - Indexes.py` | Major global equity indices | Yahoo Finance |
| `adjusted for inflation - stock.py` | Real (CPI-adjusted) equity returns | FRED |

### 😟 Labour Market
| Script | Indicator | Source |
|--------|-----------|--------|
| `UNEMPLOYMENT - US.py` | US unemployment rate | FRED |
| `UNEMPLOYMENT - UK.py` | UK unemployment rate | FRED |
| `UNEMPLOYMENT - Euro Area.py` | Euro Area unemployment | FRED |
| `UNEMPLOYMENT - Australia.py` | Australia unemployment | FRED |
| `UNEMPLOYMENT - China.py` | China urban unemployment | FRED |
| `UNEMPLOYMENT - Japan.py` | Japan unemployment | FRED |

### 💳 Credit & Debt
| Script | Indicator | Source |
|--------|-----------|--------|
| `us_hy_oas.py` | US High-Yield Option-Adjusted Spread | FRED |
| `us_credit_to_gdp.py` | US Private non-financial sector credit/GDP | BIS/FRED |
| `us_mortgage_delinquency.py` | US mortgage delinquency rate | FRED |
| `uk_debt_interest.py` | UK government debt interest payments | ONS |

### 🌍 Leading Indicators
| Script | Indicator | Source |
|--------|-----------|--------|
| `US Leading Economic Index.py` | Conference Board LEI | FRED |
| `House price crash.py` | Composite crash signal analysis | Multiple |
| `Job Vacanices.py` | US job openings (JOLTS) | FRED |

---

## Setup

```bash
# 1. Clone
git clone https://github.com/Naadir-Dev-Portfolio/Python-Economic-Dashboard.git
cd Python-Economic-Dashboard

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and add your FRED API key
# Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html
```

---

## Run a Pipeline

```bash
# Run any individual indicator script
python data_pipelines/US\ Treasury\ Yield-Curve\ Slope.py

# Output: data/us_yield_curve_slope.xlsx
```

---

## Requirements

```
pandas
requests
openpyxl
pandas_datareader
plotly
python-dotenv
```

---

## Roadmap

- [x] Individual data pipeline scripts for 25+ indicators
- [ ] Unified runner that refreshes all indicators at once
- [ ] Interactive Plotly web dashboard
- [ ] Deployed live site (Netlify / Streamlit Cloud)
- [ ] Recession probability composite signal

---

## API Keys

This project uses the [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html) (free).
Copy `.env.example` to `.env` and add your key. **Never commit your `.env` file.**
