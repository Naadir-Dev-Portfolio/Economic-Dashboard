import requests
import pandas as pd
import os
import webbrowser
from datetime import datetime

# ---------------- CONFIG ----------------
ADZUNA_APP_ID = '4a4d5eeb'       # Replace with your Adzuna App ID
ADZUNA_APP_KEY = 'a5212a158e66beb0e0749cac7a6722f3'     # Replace with your Adzuna App Key
COUNTRY = 'gb'                            # Country code (e.g., 'gb' = UK)
QUERY = 'software engineer'              # Job search term
RESULTS_PER_PAGE = 50
MAX_PAGES = 10                            # Limits API usage
# ----------------------------------------

# Create data folder if it doesn't exist
os.makedirs('data', exist_ok=True)

all_results = []

# Fetch job listings page by page
for page in range(1, MAX_PAGES + 1):
    url = f'https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}'
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'results_per_page': RESULTS_PER_PAGE,
        'what': QUERY,
        'sort_by': 'date',
        'content-type': 'application/json'
    }

    print(f"Fetching page {page}...")
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}: {response.status_code}")
        break

    jobs = response.json().get('results', [])
    if not jobs:
        break

    for job in jobs:
        all_results.append({
            'title': job.get('title'),
            'company': job.get('company', {}).get('display_name'),
            'location': job.get('location', {}).get('display_name'),
            'created': job.get('created'),
            'category': job.get('category', {}).get('label'),
            'salary_min': job.get('salary_min'),
            'salary_max': job.get('salary_max'),
            'description': job.get('description')[:200] if job.get('description') else ''
        })

# Convert to DataFrame
df = pd.DataFrame(all_results)

# Convert 'created' to datetime and remove timezone info
df['created'] = pd.to_datetime(df['created']).dt.tz_localize(None)

# Sort by date
df = df.sort_values(by='created', ascending=True)

# Save to Excel
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'data/job_data_{timestamp}.xlsx'
df.to_excel(filename, index=False)

# Open the Excel file
webbrowser.open(os.path.abspath(filename))

print(f"✅ Saved {len(df)} job records to {filename}")
