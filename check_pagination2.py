import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('LINKWARDEN_API_KEY')
base_url = "https://linkwarden.piipari.xyz/api/v1"

headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

print("Testing different pagination approaches...")

# Test skip parameter
all_links = []
skip = 0
page = 1

while True:
    print(f"\nFetching page {page} (skip={skip})...")
    response = requests.get(f'{base_url}/links?skip={skip}', headers=headers)
    data = response.json()
    links = data.get('response', [])

    print(f"  Got {len(links)} links")

    if not links or len(links) == 0:
        break

    all_links.extend(links)
    skip += len(links)
    page += 1

    # Safety limit
    if page > 15:
        print("  (Safety limit reached)")
        break

print(f"\nTotal links retrieved: {len(all_links)}")
