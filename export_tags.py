import os
import requests
from typing import Set
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TagExporter:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('LINKWARDEN_API_KEY')
        self.base_url = os.getenv('LINKWARDEN_BASE_URL', 'http://localhost:3002/api/v1')

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_all_links(self):
        try:
            response = requests.get(f'{self.base_url}/links', headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching links: {str(e)}")
            return []

    def extract_all_tags(self) -> Set[str]:
        """Extract all unique tags from all links."""
        links = self.get_all_links()
        logger.info(f"Found {len(links)} links")

        all_tags = set()
        for link in links:
            tags = link.get('tags', [])
            for tag in tags:
                tag_name = tag.get('name', '').strip()
                if tag_name:
                    all_tags.add(tag_name)

        return all_tags

    def save_tags_to_file(self, tags: Set[str], filename: str = 'tags.txt'):
        """Save tags to a file, sorted alphabetically."""
        sorted_tags = sorted(tags)

        with open(filename, 'w') as f:
            f.write("# All tags extracted from LinkWarden\n")
            f.write("# Edit this file to keep only the tags you want to allow\n\n")
            for tag in sorted_tags:
                f.write(f"{tag}\n")

        logger.info(f"Saved {len(sorted_tags)} unique tags to {filename}")

def main():
    exporter = TagExporter()

    logger.info("Extracting all tags from LinkWarden...")
    tags = exporter.extract_all_tags()

    if tags:
        logger.info(f"Found {len(tags)} unique tags")
        exporter.save_tags_to_file(tags)
        logger.info("Done! Review tags.txt and remove any unwanted tags.")
    else:
        logger.warning("No tags found in LinkWarden")

if __name__ == "__main__":
    main()
