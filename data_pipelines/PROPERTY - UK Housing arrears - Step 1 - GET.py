#!/usr/bin/env python3
"""
Step 1: Download the MLAR Excel with a browser header to avoid 403.
"""

import os
import requests

# ─── Configuration ─────────────────────────────────────────────────────────────
URL      = "https://www.bankofengland.co.uk/-/media/boe/files/statistics/mortgage-lenders-and-administrators/mlar-longrun-summary.xlsx"
OUT_DIR  = "data"
OUT_FILE = os.path.join(OUT_DIR, "mlar-longrun-summary.xlsx")
HEADERS  = {"User-Agent": "Mozilla/5.0"}

# ─── Download with requests ────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
print(f"Downloading MLAR file from:\n  {URL}\n→ {OUT_FILE}")

resp = requests.get(URL, headers=HEADERS)
resp.raise_for_status()  # will raise HTTPError if download failed

with open(OUT_FILE, "wb") as f:
    f.write(resp.content)

print("✅ Download complete")
