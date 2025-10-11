"""Test environment variable loading"""
from dotenv import load_dotenv
import os
from pathlib import Path

def test_env():
    """Test loading environment variables from config/.env"""
    # Get absolute path to config/.env
    env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
    print(f"Looking for .env at: {env_path}")
    
    # Try to load environment variables
    load_success = load_dotenv(env_path)
    print(f"Load successful: {load_success}")
    
    # Check if we can access variables (without printing actual values)
    vars_to_check = [
        'OPENAI_API_KEY',
        'OPENAI_MODEL',
        'TRELLO_KEY',
        'TRELLO_TOKEN',
        'TRELLO_BOARD_ID',
        'TRELLO_LIST_ID_LEADS',
        'TRELLO_TEMPLATE_CARD_ID',
        'DEBUG',
        'FLASK_ENV',
        'FLASK_APP'
    ]
    
    print("\nChecking variables:")
    for var in vars_to_check:
        value = os.getenv(var)
        print(f"{var}: {'✓ Set' if value else '✗ Not set'}")

if __name__ == '__main__':
    test_env()