# trello_manager.py
# Fresh module: implement Trello API logic here.
# """

"""
TrelloManager: Encapsulates Trello API interactions for job application automation.
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

class TrelloManager:
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
            'pos': 'top'
        }
        try:
            resp = requests.post(create_url, params=params)
            resp.raise_for_status()
            card = resp.json()
            card_id = card['id']
            # Set custom fields
            self._set_custom_fields(card_id, job_data)
            # Add work mode label
            self._add_work_mode_label(card_id, job_data.get('work_mode'))
            # Attach job posting URL
        url = f"{self.base_url}/card/{card_id}/customField/{field_id}/item"
        requests.put(url, params=self.auth_params, json={'idValue': option_id})

    def _add_work_mode_label(self, card_id: str, work_mode: Optional[str]):
        if not work_mode:
            return
        label_id = None
        work_mode_lower = work_mode.lower()
        if 'remote' in work_mode_lower or 'homeoffice' in work_mode_lower:
            if 'hybrid' in work_mode_lower:
                label_id = self.labels.get('hybrid')
            else:
                label_id = self.labels.get('remote')
        else:
            label_id = self.labels.get('onsite')
        if label_id:
            url = f"{self.base_url}/cards/{card_id}/idLabels"
            requests.post(url, params={**self.auth_params, 'value': label_id})

    def _add_attachment(self, card_id: str, url: str, name: str):
        attach_url = f"{self.base_url}/cards/{card_id}/attachments"
        params = {**self.auth_params, 'url': url, 'name': name}
        requests.post(attach_url, params=params)

    def _copy_checklist_from_template(self, card_id: str):
        try:
            template_url = f"{self.base_url}/cards/{self.template_card_id}/checklists"
            resp = requests.get(template_url, params=self.auth_params)
            if resp.status_code == 200:
                checklists = resp.json()
                for checklist in checklists:
                    create_url = f"{self.base_url}/checklists"
                    params = {**self.auth_params, 'idCard': card_id, 'name': checklist['name']}
                    new_checklist = requests.post(create_url, params=params).json()
                    for item in checklist['checkItems']:
                        item_url = f"{self.base_url}/checklists/{new_checklist['id']}/checkItems"
                        item_params = {**self.auth_params, 'name': item['name']}
                        requests.post(item_url, params=item_params)
        except Exception as e:
            print(f"Warning: Could not copy checklist: {e}")

# Test function
if __name__ == "__main__":
    # Minimal test: instantiate and print config
    manager = TrelloManager()
    print("TrelloManager loaded. Board ID:", manager.board_id)
    # Optionally, test card creation with dummy data (uncomment to use):
    # job_data = {
    #     'company_name': 'Test Company',
    #     'job_title': 'Test Position',
    #     'location': 'Test City',
    #     'work_mode': 'remote',
    #     'company_address': 'Test Street 1',
    #     'publication_date': '2025-10-11',
    #     'job_description': 'Test job description.',
    #     'contact_person': {'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '123456789'},
    #     'source_url': 'https://example.com/job',
    # }
    # card = manager.create_card_from_job_data(job_data)
    # print("Created card:", card)