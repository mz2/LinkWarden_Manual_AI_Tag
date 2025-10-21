import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('LINKWARDEN_API_KEY')
base_url = "https://linkwarden.piipari.xyz/api/v1"

headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Get all links
response = requests.get(f'{base_url}/links', headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if data.get('response') and len(data['response']) > 0:
        first_link = data['response'][0]
        print("\nFirst link structure:")
        print(json.dumps(first_link, indent=2))

        # Try to update with ownerId
        link_id = first_link['id']
        update_data = {
            "id": link_id,
            "name": first_link.get('name', ''),
            "url": first_link.get('url', ''),
            "description": first_link.get('description', ''),
            "tags": first_link.get('tags', []),
            "collection": first_link.get('collection', {}),
            "ownerId": first_link.get('ownerId', 1)
        }

        print(f"\n\nTrying to update link {link_id} with:")
        print(json.dumps(update_data, indent=2))

        update_response = requests.put(
            f'{base_url}/links/{link_id}',
            headers=headers,
            json=update_data
        )

        print(f"\n\nUpdate status: {update_response.status_code}")
        print(f"Update response: {update_response.text}")
else:
    print(f"Error: {response.text}")
