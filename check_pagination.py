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

# Try different pagination parameters
print("Testing pagination...")

# Test 1: Default
response = requests.get(f'{base_url}/links', headers=headers)
data = response.json()
print(f"\nDefault request: {len(data.get('response', []))} links")
print(f"Response keys: {list(data.keys())}")

# Test 2: With take parameter
response = requests.get(f'{base_url}/links?take=1000', headers=headers)
data = response.json()
print(f"\nWith take=1000: {len(data.get('response', []))} links")

# Test 3: Check if there's pagination info
response = requests.get(f'{base_url}/links', headers=headers)
data = response.json()
print(f"\nFull response structure:")
for key in data.keys():
    if key != 'response':
        print(f"  {key}: {data[key]}")
