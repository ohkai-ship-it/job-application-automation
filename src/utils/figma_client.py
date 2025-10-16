"""
Figma API Client
Connects to Figma API and fetches design data for code generation
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from utils.log_config import get_logger

load_dotenv('config/.env')
logger = get_logger(__name__)


class FigmaClient:
    """
    Client for interacting with Figma REST API
    """
    
    BASE_URL = "https://api.figma.com/v1"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Figma client
        
        Args:
            access_token: Figma Personal Access Token (or from env)
        """
        self.access_token = access_token or os.getenv('FIGMA_ACCESS_TOKEN')
        
        if not self.access_token:
            raise ValueError(
                "Figma access token not found. "
                "Set FIGMA_ACCESS_TOKEN in config/.env or pass to constructor. "
                "Get token from: https://www.figma.com/settings"
            )
        
        self.headers = {
            'X-Figma-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        logger.info("Figma client initialized")
    
    def get_file(self, file_key: str) -> Dict[str, Any]:
        """
        Fetch a Figma file by key
        
        Args:
            file_key: Figma file ID (from URL: figma.com/file/<FILE_KEY>/...)
        
        Returns:
            Full file data including document tree
        """
        url = f"{self.BASE_URL}/files/{file_key}"
        
        logger.info(f"Fetching Figma file: {file_key}")
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"✓ Fetched file: {data.get('name', 'Unknown')}")
        
        return data
    
    def get_file_nodes(self, file_key: str, node_ids: list[str]) -> Dict[str, Any]:
        """
        Fetch specific nodes from a Figma file
        
        Args:
            file_key: Figma file ID
            node_ids: List of node IDs to fetch
        
        Returns:
            Node data for requested nodes
        """
        url = f"{self.BASE_URL}/files/{file_key}/nodes"
        params = {'ids': ','.join(node_ids)}
        
        logger.info(f"Fetching {len(node_ids)} nodes from file {file_key}")
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_images(self, file_key: str, node_ids: list[str], 
                   format: str = 'png', scale: float = 2.0) -> Dict[str, str]:
        """
        Export images from Figma file
        
        Args:
            file_key: Figma file ID
            node_ids: List of node IDs to export
            format: Image format ('png', 'jpg', 'svg', 'pdf')
            scale: Export scale (1.0 = 1x, 2.0 = 2x, etc.)
        
        Returns:
            Dict mapping node_id -> image URL
        """
        url = f"{self.BASE_URL}/images/{file_key}"
        params = {
            'ids': ','.join(node_ids),
            'format': format,
            'scale': scale
        }
        
        logger.info(f"Exporting {len(node_ids)} images from file {file_key}")
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json().get('images', {})
    
    @staticmethod
    def extract_file_key(url: str) -> str:
        """
        Extract file key from Figma URL
        
        Args:
            url: Figma file URL (e.g., https://www.figma.com/file/ABC123/...)
        
        Returns:
            File key (e.g., 'ABC123')
        """
        import re
        
        # Match pattern: figma.com/file/<FILE_KEY>/
        match = re.search(r'figma\.com/(?:file|design)/([a-zA-Z0-9]+)', url)
        
        if not match:
            raise ValueError(f"Invalid Figma URL: {url}")
        
        return match.group(1)
    
    def find_nodes_by_name(self, document: Dict[str, Any], 
                          name_pattern: str) -> list[Dict[str, Any]]:
        """
        Recursively find nodes matching a name pattern
        
        Args:
            document: Figma document tree (from get_file()['document'])
            name_pattern: Node name to search for (supports wildcards)
        
        Returns:
            List of matching nodes
        """
        import fnmatch
        
        matches = []
        
        def traverse(node):
            if fnmatch.fnmatch(node.get('name', ''), name_pattern):
                matches.append(node)
            
            # Recurse into children
            for child in node.get('children', []):
                traverse(child)
        
        traverse(document)
        return matches


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("FIGMA CLIENT TEST")
    print("=" * 80)
    
    try:
        # Initialize client (will load token from .env)
        client = FigmaClient()
        print("✓ Figma client initialized")
        
        # Test with a file URL (user should replace this)
        test_url = input("\nEnter Figma file URL (or press Enter to skip): ").strip()
        
        if test_url:
            file_key = FigmaClient.extract_file_key(test_url)
            print(f"\n✓ Extracted file key: {file_key}")
            
            # Fetch file
            file_data = client.get_file(file_key)
            print(f"\n✓ File name: {file_data.get('name')}")
            print(f"✓ Last modified: {file_data.get('lastModified')}")
            print(f"✓ Version: {file_data.get('version')}")
            
            # List top-level pages
            print("\nPages in file:")
            for page in file_data.get('document', {}).get('children', []):
                print(f"  - {page.get('name')} ({page.get('type')})")
        else:
            print("\nSkipping file fetch test")
            print("\nTo test with a real file:")
            print("1. Create a Figma file")
            print("2. Get your access token from https://www.figma.com/settings")
            print("3. Add to config/.env: FIGMA_ACCESS_TOKEN=your_token_here")
            print("4. Run this script again with the file URL")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("1. You have a FIGMA_ACCESS_TOKEN in config/.env")
        print("2. The token is valid (check https://www.figma.com/settings)")
        print("3. You have access to the Figma file")
