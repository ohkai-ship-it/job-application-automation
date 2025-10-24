"""
Credentials validation and startup checks
Ensures all required environment variables are present before running
"""

import os
import sys
from dotenv import load_dotenv


def validate_credentials():
    """
    Validate all required credentials are present on startup
    
    Returns:
        bool: True if all credentials are valid, False otherwise
    """
    # Load from config/.env file
    env_file = 'config/.env'
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()  # Fallback to system environment
    
    required_creds = {
        'OPENAI_API_KEY': 'OpenAI API key (for cover letter generation)',
        'TRELLO_KEY': 'Trello API key',
        'TRELLO_TOKEN': 'Trello API token',
        'TRELLO_BOARD_ID': 'Trello board ID',
        'TRELLO_LIST_ID_LEADS': 'Trello list ID for leads'
    }
    
    missing = []
    for key, description in required_creds.items():
        value = os.getenv(key)
        if not value or value.strip() == '':
            missing.append(f"  ❌ {key}: {description}")
        else:
            # Validate format for sensitive keys
            if key == 'OPENAI_API_KEY' and not value.startswith('sk-'):
                missing.append(f"  ⚠️  {key}: Invalid format (should start with 'sk-')")
            elif key == 'TRELLO_TOKEN' and len(value) < 20:
                missing.append(f"  ⚠️  {key}: Looks invalid (too short)")
    
    if missing:
        print("\n" + "="*80)
        print("🚨 MISSING OR INVALID REQUIRED CREDENTIALS")
        print("="*80)
        print("\nPlease set the following in config/.env:\n")
        print("\n".join(missing))
        print("\n" + "="*80)
        print("Setup Guide: See PRODUCTION_SETUP.md")
        print("="*80 + "\n")
        return False
    
    print("\n✅ All credentials validated successfully\n")
    return True


def get_credential(key, required=True):
    """
    Get a credential value safely
    
    Args:
        key: Environment variable name
        required: If True, raise error if not found
        
    Returns:
        str: Credential value or None
        
    Raises:
        ValueError: If required credential is missing
    """
    value = os.getenv(key)
    if not value and required:
        raise ValueError(f"Required credential missing: {key}")
    return value
