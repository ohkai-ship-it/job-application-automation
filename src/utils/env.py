"""Environment variable handling for the application.

This module provides a consistent way to load and access environment variables
from the config/.env file and environment-specific overrides.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Get path to config directory
CONFIG_DIR = Path(__file__).parent.parent.parent / 'config'
ENV_PATH = CONFIG_DIR / '.env'

def load_env() -> bool:
    """Load environment variables from config files.
    
    Priority (highest to lowest):
    1. config/.env.{APP_ENV} (e.g., .env.production, .env.development, .env.test)
    2. config/.env (default/fallback)
    
    APP_ENV defaults to 'development' if not set.
    
    Returns:
        bool: True if successful, False if no config files found
    """
    app_env = os.getenv('APP_ENV', 'development')
    
    # Try environment-specific file first
    env_specific_path = CONFIG_DIR / f'.env.{app_env}'
    if env_specific_path.exists():
        load_dotenv(env_specific_path)
        # Also load base .env for any missing values
        if ENV_PATH.exists():
            load_dotenv(ENV_PATH, override=False)  # Don't override values from .env.{env}
        return True
    
    # Fall back to base .env
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
        return True
    
    return False

def validate_env(required_vars: list[str]) -> None:
    """Validate that required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Raises:
        ValueError: If any required variables are missing
    """
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your {ENV_PATH} file."
        )

def get_str(name: str, default: Optional[str] = None) -> str:
    """Get a string environment variable.
    
    Args:
        name: Name of the environment variable
        default: Default value if variable is not set or empty. If None, returns empty string.
        
    Returns:
        str: The environment variable value, default, or empty string
    """
    value = os.getenv(name)
    if value is not None:
        value = value.strip()
        if value:
            return value
    
    return default if default is not None else ""

def validate_all_env() -> None:
    """Validate all required environment variables at startup.
    
    This function checks all required variables for:
    - OpenAI configuration
    - Trello configuration
    - Flask configuration
    - Directory paths
    
    Raises:
        ValueError: If any required variables are missing or invalid
    """
    # Load environment first
    if not load_env():
        raise ValueError(f"Could not load environment file at {ENV_PATH}")
    
    # Required variables by category
    openai_vars: list[str] = ['OPENAI_API_KEY']
    trello_vars: list[str] = ['TRELLO_KEY', 'TRELLO_TOKEN', 'TRELLO_BOARD_ID', 'TRELLO_LIST_ID_LEADS']
    flask_vars: list[str] = ['FLASK_HOST', 'FLASK_PORT']
    path_vars: list[str] = ['DATA_DIR', 'OUTPUT_DIR']
    
    all_required: dict[str, list[str]] = {
        'OpenAI': openai_vars,
        'Trello': trello_vars,
        'Flask': flask_vars,
        'Paths': path_vars
    }
    
    # Check each category
    errors = []
    for category, vars in all_required.items():
        missing = [var for var in vars if not get_str(var)]
        if missing:
            errors.append(f"{category}: Missing {', '.join(missing)}")
    
    # Validate specific values
    if get_str('FLASK_PORT'):
        try:
            port = int(get_str('FLASK_PORT'))
            if port < 1 or port > 65535:
                errors.append("Flask: FLASK_PORT must be between 1 and 65535")
        except ValueError:
            errors.append("Flask: FLASK_PORT must be a valid integer")
            
    # Raise with all errors if any found
    if errors:
        raise ValueError(
            "Environment validation failed:\n" + 
            "\n".join(f"- {error}" for error in errors) +
            f"\n\nPlease check your {ENV_PATH} file."
        )
