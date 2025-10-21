import os
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

api_key = os.getenv('LINKWARDEN_API_KEY')
base_url = "https://linkwarden.piipari.xyz/api/v1"

headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

# Check current user
print("Checking current user profile...")
profile_response = requests.get(f'{base_url}/profile', headers=headers)
if profile_response.status_code == 200:
    profile = profile_response.json()
    print(f"Current user ID: {profile.get('id')}")
    print(f"Username: {profile.get('username')}")
    print()

# Get first page of links
print("Fetching first page of links...")
response = requests.get(f'{base_url}/links?skip=0', headers=headers)
data = response.json()
links = data.get('response', [])

print(f"First page has {len(links)} links")
print()

# Check owner IDs
owner_ids = [link.get('collection', {}).get('ownerId') for link in links if link.get('collection')]
owner_counts = Counter(owner_ids)

print("Owner ID distribution:")
for owner_id, count in sorted(owner_counts.items()):
    print(f"  Owner ID {owner_id}: {count} links")
print()

# Try to get total count
print("Checking total links...")
all_links = []
skip = 0
page = 1

while True:  # Fetch ALL pages
    print(f"Fetching page {page} (skip={skip})...")
    response = requests.get(f'{base_url}/links?skip={skip}', headers=headers)
    data = response.json()
    page_links = data.get('response', [])

    if not page_links:
        break

    all_links.extend(page_links)
    skip += len(page_links)
    page += 1

print(f"\nRetrieved {len(all_links)} links across {page-1} pages")

# Count by owner
all_owner_ids = [link.get('collection', {}).get('ownerId') for link in all_links if link.get('collection')]
all_owner_counts = Counter(all_owner_ids)

print("\nTotal owner ID distribution (first 12 pages):")
for owner_id, count in sorted(all_owner_counts.items()):
    print(f"  Owner ID {owner_id}: {count} links")
