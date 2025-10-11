"""Trello utility helpers used by scripts and modules.

Centralizes API base URL and authentication parameter handling, ensuring
credentials are loaded from config/.env via utils.env only. Avoids hardcoding
secrets in helper scripts.
"""

from __future__ import annotations

from typing import Dict, Optional

import requests

from .env import load_env, get_str


TRELLO_API_BASE = "https://api.trello.com/1"


def get_auth_params() -> Dict[str, str]:
    """Return Trello API auth params from environment.

    Requires TRELLO_KEY and TRELLO_TOKEN present in config/.env or process env.
    Returns an empty dict if not available.
    """
    # Ensure env is loaded
    load_env()
    key = get_str("TRELLO_KEY") or get_str("TRELLO_API_KEY")
    token = get_str("TRELLO_TOKEN") or get_str("TRELLO_API_TOKEN")
    if not key or not token:
        return {}
    return {"key": key, "token": token}


def mask_secret(value: str, prefix: int = 4) -> str:
    """Mask a secret for display, keeping only a short prefix."""
    if not value:
        return ""
    return f"{value[:prefix]}..." if len(value) > prefix else "***"


def trello_get(path: str, params: Optional[Dict[str, str]] = None, timeout: int = 15) -> requests.Response:
    """Perform a GET request to the Trello API with auth parameters merged in."""
    auth = get_auth_params()
    merged = {**(params or {}), **auth} if auth else (params or {})
    url = f"{TRELLO_API_BASE}/{path.lstrip('/')}"
    return requests.get(url, params=merged, timeout=timeout)
