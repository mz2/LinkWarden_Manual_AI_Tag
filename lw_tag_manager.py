import os
import json
import requests
from typing import List, Dict
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkWardenManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('LINKWARDEN_API_KEY')
        
        # Use environment variables with default values
        self.base_url = os.getenv('LINKWARDEN_BASE_URL', 'https://localhost:3002/api/v1')
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # New environment variable to skip links with existing tags
        self.skip_tagged_links = os.getenv('SKIP_LINKS_WITH_TAGS', 'false').lower() in ['true', '1', 'yes']
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def get_ollama_tags(self, text: str) -> List[str]:
        """Get auto-generated tag suggestions from Ollama."""
        # Check if text is empty or too short
        if not text or len(text.strip()) < 10:
            logger.warning(f"Text too short for tag suggestion: '{text}'")
            return []

        try:
            # Construct a more detailed prompt for auto-generation
            prompt = f"""
You are an expert at extracting relevant tags from content.
Analyze the following text and generate appropriate tags.

Guidelines:
- Generate concise, relevant tags (1-2 words each)
- Be precise and selective
- Return tags as a comma-separated list
- Minimum 1 tag, Maximum 5 tags
- Use lowercase
- Focus on main topics, technologies, categories

Text to analyze (len: {len(text)}):
{text[:1000]}

Suggested Tags:"""

            # Log the full prompt being sent
            logger.debug(f"Full Ollama Prompt:\n{prompt}")

            # Prepare the request payload
            payload = {
                "model": "qwen3:30b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
                "num_predict": 100,
            }
            
            # Send request to Ollama
            response = requests.post(
                f'{self.ollama_url}/api/generate',
                json=payload,
                timeout=120  # Increased timeout for large models like gpt-oss:20b
            )
            
            # Check response status
            if response.status_code != 200:
                logger.error(f"Ollama returned non-200 status code: {response.status_code}")
                logger.error(f"Response content: {response.text}")
                return []
            
            # Parse the response
            try:
                result = response.json()
            except ValueError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return []
            
            # Extract and process response
            if 'response' in result:
                response_text = result['response'].lower().strip()
                logger.debug(f"Raw Ollama response: {response_text}")

                # Parse tags - accept all generated tags
                suggested = [tag.strip() for tag in response_text.split(',')]
                # Filter out empty tags and limit to 5
                suggested_tags = [tag for tag in suggested if tag and len(tag) > 0]

                logger.debug(f"Generated tags: {suggested_tags}")

                return suggested_tags[:5]

            logger.warning("No response key found in Ollama result")
            return []
            
        except requests.exceptions.RequestException as req_error:
            logger.error(f"Network error getting Ollama tags: {req_error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting Ollama tags: {e}", exc_info=True)
            return []

    def load_approved_tags(self, tags_file: str) -> List[str]:
        try:
            with open(tags_file, 'r') as f:
                # Log each tag being loaded
                tags = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                logger.debug(f"Loaded tags: {tags}")
                return tags
        except FileNotFoundError:
            logger.error(f"Tags file {tags_file} not found")
            return []

    def get_all_links(self) -> List[Dict]:
        """Fetch all links using cursor-based pagination."""
        try:
            all_links = []
            cursor = None
            page = 1

            while True:
                # Build URL with cursor parameter
                if cursor is None:
                    url = f'{self.base_url}/links'
                    logger.info(f"Fetching page {page} of links (initial request)...")
                else:
                    url = f'{self.base_url}/links?cursor={cursor}'
                    logger.info(f"Fetching page {page} of links (cursor={cursor})...")

                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                links = data.get('response', [])

                if not links:
                    logger.info("No more links returned - reached end of data")
                    break

                logger.debug(f"Page {page}: Retrieved {len(links)} links (IDs: {links[0].get('id')} to {links[-1].get('id')})")
                all_links.extend(links)

                # Set cursor to the ID of the last link for the next request
                cursor = links[-1].get('id')
                page += 1

                # Safety limit to prevent infinite loops
                if page > 100:
                    logger.warning("Reached safety limit of 100 pages")
                    break

            # Log details about all the links
            logger.info(f"Total links retrieved across {page-1} pages: {len(all_links)}")
            for link in all_links:
                logger.debug(f"Link details - Name: {link.get('name')}, URL: {link.get('url')}")

            return all_links
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching links: {str(e)}")
            return []

    def update_link_tags(self, link_id: int, link_data: Dict, new_tags: List[str], merge: bool = True) -> bool:
        try:
            # Get existing tags
            existing_tags = [tag.get('name', '') for tag in link_data.get('tags', [])]

            # Merge or replace tags based on merge parameter
            if merge:
                # Combine existing and new tags, removing duplicates while preserving order
                all_tags = existing_tags + [tag for tag in new_tags if tag not in existing_tags]
                logger.debug(f"Merging tags - Existing: {existing_tags}, New: {new_tags}, Result: {all_tags}")
            else:
                all_tags = new_tags
                logger.debug(f"Replacing tags - Old: {existing_tags}, New: {all_tags}")

            update_data = {
                "id": link_id,
                "name": link_data.get('name', ''),
                "url": link_data.get('url', ''),
                "description": link_data.get('description', ''),
                "tags": [{"name": tag} for tag in all_tags],
                "collection": link_data.get('collection', {"id": link_data.get('collectionId', 0)}),
                "ownerId": link_data.get('collection', {}).get('ownerId', 1)
            }

            # Log the update details
            logger.debug(f"Updating link {link_id} with tags: {all_tags}")
            logger.debug(f"Full update payload: {json.dumps(update_data, indent=2)}")

            response = requests.put(
                f'{self.base_url}/links/{link_id}',
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            logger.info(f"Successfully updated tags for link {link_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating link {link_id}: {e}")
            return False

def main():
    manager = LinkWardenManager()

    logger.info("Auto-generating tags using AI (no predefined tag list)")

    # Get all links
    all_links = manager.get_all_links()
    logger.info(f"Found {len(all_links)} total links")

    # Filter to only current user's links (owner ID 1)
    # Skip links from other users/shared collections
    links = [link for link in all_links if link.get('collection', {}).get('ownerId') == 1]
    logger.info(f"Filtered to {len(links)} links owned by current user (owner ID 1)")
    logger.info(f"Skipped {len(all_links) - len(links)} links from other owners")

    # Process each link
    for link in links:
        name = link.get('name', '')
        description = link.get('description', '')
        text_content = link.get('textContent', '')
        url = link.get('url', '')
        existing_tags = link.get('tags', [])

        # Check if we should skip links with existing tags
        if manager.skip_tagged_links and existing_tags:
            logger.info(f"Skipping '{name}' - already has {len(existing_tags)} tags")
            continue

        # Combine text for analysis, prioritizing content
        text_to_analyze = text_content or description or name

        logger.debug(f"Analyzing link: {name}")
        logger.debug(f"Text length for tag suggestion: {len(text_to_analyze)}")

        # Get auto-generated tag suggestions from Ollama
        suggested_tags = manager.get_ollama_tags(text_to_analyze)

        if suggested_tags:
            success = manager.update_link_tags(
                link_id=link['id'],
                link_data=link,
                new_tags=suggested_tags
            )
            if success:
                logger.info(f"Updated tags for '{name}': {suggested_tags}")
            else:
                logger.error(f"Failed to update tags for '{name}'")
        else:
            logger.warning(f"No tags suggested for '{name}'")

if __name__ == "__main__":
    main()
