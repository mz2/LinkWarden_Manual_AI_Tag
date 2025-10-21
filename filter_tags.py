import os
import json
import requests
from typing import List, Dict, Set
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TagFilter:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('LINKWARDEN_API_KEY')
        self.base_url = os.getenv('LINKWARDEN_BASE_URL', 'http://localhost:3002/api/v1')

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def load_allowed_tags(self, tags_file: str = 'tags.txt') -> Set[str]:
        """Load allowed tags from file."""
        try:
            with open(tags_file, 'r') as f:
                tags = {line.strip() for line in f if line.strip() and not line.startswith('#')}
                logger.info(f"Loaded {len(tags)} allowed tags from {tags_file}")
                return tags
        except FileNotFoundError:
            logger.error(f"Tags file {tags_file} not found")
            return set()

    def get_all_links(self) -> List[Dict]:
        try:
            response = requests.get(f'{self.base_url}/links', headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching links: {str(e)}")
            return []

    def update_link_tags(self, link_id: int, link_data: Dict, filtered_tags: List[str]) -> bool:
        try:
            update_data = {
                "id": link_id,
                "name": link_data.get('name', ''),
                "url": link_data.get('url', ''),
                "description": link_data.get('description', ''),
                "tags": [{"name": tag} for tag in filtered_tags],
                "collection": link_data.get('collection', {"id": 0})
            }

            response = requests.put(
                f'{self.base_url}/links/{link_id}',
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating link {link_id}: {e}")
            return False

    def filter_link_tags(self, allowed_tags: Set[str]):
        """Remove tags from links that aren't in the allowed list."""
        links = self.get_all_links()
        logger.info(f"Found {len(links)} links to process")

        modified_count = 0
        removed_tags_count = 0

        for link in links:
            link_id = link.get('id')
            name = link.get('name', '')
            existing_tags = [tag.get('name', '') for tag in link.get('tags', [])]

            # Filter tags to only include allowed ones
            filtered_tags = [tag for tag in existing_tags if tag in allowed_tags]

            # Check if any tags were removed
            if len(filtered_tags) < len(existing_tags):
                removed = set(existing_tags) - set(filtered_tags)
                removed_tags_count += len(removed)

                logger.info(f"Link '{name}': Removing tags {removed}")

                success = self.update_link_tags(link_id, link, filtered_tags)
                if success:
                    modified_count += 1
                    logger.info(f"Updated '{name}': {existing_tags} -> {filtered_tags}")
                else:
                    logger.error(f"Failed to update '{name}'")

        logger.info(f"Filter complete: Modified {modified_count} links, removed {removed_tags_count} tags")

def main():
    filter = TagFilter()

    # Load allowed tags
    allowed_tags = filter.load_allowed_tags('tags.txt')

    if not allowed_tags:
        logger.error("No allowed tags found. Please create tags.txt first using export_tags.py")
        return

    logger.info(f"Filtering tags to allowed list: {sorted(allowed_tags)}")

    # Confirm before proceeding
    print(f"\nThis will remove all tags NOT in tags.txt from all links.")
    print(f"Allowed tags ({len(allowed_tags)}): {', '.join(sorted(allowed_tags))}")
    response = input("\nProceed? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        filter.filter_link_tags(allowed_tags)
    else:
        logger.info("Cancelled by user")

if __name__ == "__main__":
    main()
