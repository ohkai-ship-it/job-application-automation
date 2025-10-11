# trello_connect.py
"""
TrelloConnect: Encapsulates Trello API interactions for job application automation.
Creates cards, sets custom fields and labels, copies checklists from a template card.
Credentials/IDs are read from config/.env (with hardcoded fallbacks for dev).
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
try:
    from .utils.env import load_env, get_str
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.env import load_env, get_str

class TrelloConnect:
    def __init__(self):
        load_env()
        self.api_key = get_str('TRELLO_KEY', default='your-trello-key')
        self.token = get_str('TRELLO_TOKEN', default='your-trello-token')
        self.board_id = get_str('TRELLO_BOARD_ID', default='your-board-id')
        self.leads_list_id = get_str('TRELLO_LIST_ID_LEADS', default='67ade7af134e9f72c55b4dd9')
        self.template_card_id = get_str('TRELLO_TEMPLATE_CARD_ID', default='your-template-card-id')
        self.base_url = "https://api.trello.com/1"
        self.auth_params = {'key': self.api_key, 'token': self.token}
        # Custom field and label IDs (update as needed for your board)
        self.custom_fields = {
            'company_name': get_str('TRELLO_CF_COMPANY', default='your-cf-company'),
            'job_title': get_str('TRELLO_CF_TITLE', default='your-cf-title'),
            'source': get_str('TRELLO_CF_SOURCE', default='your-cf-source'),
            'language': get_str('TRELLO_CF_LANG', default='your-cf-lang'),
            'publication_date': get_str('TRELLO_CF_PUBDATE', default='your-cf-pubdate'),
            'application_portal': get_str('TRELLO_CF_PORTAL', default='your-cf-portal'),
            'company_person': get_str('TRELLO_CF_PERSON', default='your-cf-person'),
            'company_email': get_str('TRELLO_CF_EMAIL', default='your-cf-email'),
            'company_phone': get_str('TRELLO_CF_PHONE', default='your-cf-phone'),
        }
        self.stepstone_option_id = get_str('TRELLO_STEPSTONE_OPTION_ID', default='67adec40a91936eec7f48587')
        self.labels = {
            'remote': get_str('TRELLO_LABEL_REMOTE', default='your-label-remote'),
            'hybrid': get_str('TRELLO_LABEL_HYBRID', default='your-label-hybrid'),
            'onsite': get_str('TRELLO_LABEL_ONSITE', default='your-label-onsite'),
            'interesting': get_str('TRELLO_LABEL_INTERESTING', default='your-label-interesting'),
        }

    def create_card_from_job_data(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Creates a Trello card from normalized job_data dict."""
        card_name = f"{job_data.get('company_name', 'Unknown')} - {job_data.get('job_title', 'Unknown')}"
        description = self._build_card_description(job_data)
        create_url = f"{self.base_url}/cards"
        params = {
            **self.auth_params,
            'idList': self.leads_list_id,
            'name': card_name,
            'desc': description,
            'pos': 'top',
        }
        response = requests.post(create_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Trello API error: {response.status_code} - {response.text}")
            return None

    def _build_card_description(self, job_data: Dict[str, Any]) -> str:
        lines = [
            f"Company: {job_data.get('company_name', '')}",
            f"Title: {job_data.get('job_title', '')}",
            f"Location: {job_data.get('location', '')}",
            f"Source: {job_data.get('source_url', '')}",
            f"Description: {job_data.get('job_description', '')[:200]}...",
        ]
        return "\n".join(lines)
