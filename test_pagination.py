import requests
import os

# Read from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('LINKWARDEN_API_KEY='):
            api_key = line.split('=', 1)[1].strip()
        elif line.startswith('LINKWARDEN_BASE_URL='):
            base_url = line.split('=', 1)[1].strip()

headers = {'Authorization': f'Bearer {api_key}'}

# Test 1: Default request
print("=== Test 1: Default request ===")
resp = requests.get(f'{base_url}/links', headers=headers)
data = resp.json()
links = data.get('response', [])
print(f'Count: {len(links)}')
if links:
    print(f'First ID: {links[0].get("id")}')
    print(f'Last ID: {links[-1].get("id")}')

# Test 2: With take=10
print("\n=== Test 2: With take=10 ===")
resp = requests.get(f'{base_url}/links?take=10', headers=headers)
data = resp.json()
links = data.get('response', [])
print(f'Count: {len(links)}')
if links:
    print(f'First ID: {links[0].get("id")}')
    print(f'Last ID: {links[-1].get("id")}')

# Test 3: With cursor (using last ID from test 2)
if links:
    cursor = links[-1].get('id')
    print(f"\n=== Test 3: With cursor={cursor} and take=10 ===")
    resp = requests.get(f'{base_url}/links?cursor={cursor}&take=10', headers=headers)
    data = resp.json()
    links = data.get('response', [])
    print(f'Count: {len(links)}')
    if links:
        print(f'First ID: {links[0].get("id")}')
        print(f'Last ID: {links[-1].get("id")}')
