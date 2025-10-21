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

# Check current user
print("Current user profile:")
profile_response = requests.get(f'{base_url}/profile', headers=headers)
if profile_response.status_code == 200:
    profile = profile_response.json()
    print(f"  User ID: {profile.get('id')}")
    print(f"  Username: {profile.get('username')}")
    print(f"  Name: {profile.get('name')}")
    print()

# Check user's own collections
print("User's collections:")
collections_response = requests.get(f'{base_url}/collections', headers=headers)
if collections_response.status_code == 200:
    collections = collections_response.json().get('response', [])
    for coll in collections[:5]:  # Show first 5
        print(f"  Collection: {coll.get('name')} (ID: {coll.get('id')}, Owner ID: {coll.get('ownerId')})")
