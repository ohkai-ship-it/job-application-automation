# trello_connect.py
"""
TrelloConnect: Encapsulates Trello API interactions for job application automation.
Creates cards with structured layout, labels, and custom fields.
Supports idempotent card creation to avoid duplicates.
Credentials/IDs are read from config/.env.
"""

import os
import requests
from typing import Callable, Dict, Any, Optional
try:
    from .utils.logging import get_logger
    from .utils.env import load_env, get_str
    from .utils.http import request_with_retries
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.logging import get_logger
    from utils.env import load_env, get_str
    from utils.http import request_with_retries


class TrelloConnect:
    """Manages Trello card creation with idempotency, labels, and custom fields."""
    
    def __init__(self, requester: Optional[Callable[..., requests.Response]] = None) -> None:
        """
        Initialize Trello connector.
        
        Args:
            requester: Optional callable for HTTP requests (for testing).
                      Defaults to utils.http.request_with_retries.
        """
        self.logger = get_logger(__name__)
        load_env()
        
        # Core Trello configuration
        self.api_key = get_str('TRELLO_KEY', default='')
        self.token = get_str('TRELLO_TOKEN', default='')
        self.board_id = get_str('TRELLO_BOARD_ID', default='')
        self.leads_list_id = get_str('TRELLO_LIST_ID_LEADS', default='')
        self.template_card_id = get_str('TRELLO_TEMPLATE_CARD_ID', default='')
        
        # Label IDs for work mode
        self.label_remote = get_str('TRELLO_LABEL_REMOTE', default='')
        self.label_hybrid = get_str('TRELLO_LABEL_HYBRID', default='')
        self.label_onsite = get_str('TRELLO_LABEL_ONSITE', default='')
        
        # Label IDs for language
        self.label_de = get_str('TRELLO_LABEL_DE', default='')
        self.label_en = get_str('TRELLO_LABEL_EN', default='')
        
        # Label IDs for seniority
        self.label_junior = get_str('TRELLO_LABEL_JUNIOR', default='')
        self.label_mid = get_str('TRELLO_LABEL_MID', default='')
        self.label_senior = get_str('TRELLO_LABEL_SENIOR', default='')
        self.label_lead = get_str('TRELLO_LABEL_LEAD', default='')
        
        # Custom field IDs (from previous implementation)
        # Text fields
        self.field_company = get_str('TRELLO_FIELD_FIRMENNAME', default='')  # Firmenname
        self.field_job_title = get_str('TRELLO_FIELD_ROLLENTITEL', default='')  # Rollentitel
        self.field_source_url = get_str('TRELLO_FIELD_SOURCE_URL', default='')  # For URL storage if needed
        
        # List/dropdown fields
        self.field_source_list = get_str('TRELLO_FIELD_QUELLE', default='')  # Quelle (Stepstone, LinkedIn, etc.)
        self.field_source_stepstone_option = get_str('TRELLO_FIELD_QUELLE_STEPSTONE', default='')  # Stepstone option ID
        
        # Date fields
        self.field_publication_date = get_str('TRELLO_FIELD_AUSSCHREIBUNGSDATUM', default='')  # Ausschreibungsdatum
        
        # Additional text field
        self.field_firma_person = get_str('TRELLO_FIELD_FIRMA_PERSON', default='')  # Firma - Person
        
        self.base_url = "https://api.trello.com/1"
        self.auth_params = {'key': self.api_key, 'token': self.token}
        
        # Injectable requester to ease testing; defaults to utils.http.request_with_retries
        self.requester: Callable[..., requests.Response] = requester or request_with_retries

    
    def _build_card_name(self, job_data: Dict[str, Any]) -> str:
        """
        Build card name: [Company] Job Title (Location)
        
        Args:
            job_data: Normalized job data dict
            
        Returns:
            Formatted card name
        """
        company = job_data.get('company_name', 'Unknown Company')
        title = job_data.get('job_title_clean') or job_data.get('job_title', 'Unknown Position')
        location = job_data.get('location', 'Unknown Location')
        
        return f"[{company}] {title} ({location})"
    
    def _build_card_description(self, job_data: Dict[str, Any]) -> str:
        """
        Build structured markdown description for Trello card.
        
        Args:
            job_data: Normalized job data dict
            
        Returns:
            Markdown-formatted description string
        """
        # Helper to get value or N/A
        def get_val(key: str, default: str = 'N/A') -> str:
            val = job_data.get(key)
            return str(val) if val else default
        
        # Top section: key facts
        # Prefer job_title_clean if available, otherwise job_title
        title = job_data.get('job_title_clean') or job_data.get('job_title', 'N/A')
        company = get_val('company_name')
        location = get_val('location')
        
        # Format work_mode, language, seniority (capitalize only if not N/A)
        work_mode_raw = get_val('work_mode', 'N/A')
        work_mode = work_mode_raw.capitalize() if work_mode_raw != 'N/A' else 'N/A'
        
        language_raw = get_val('language', 'N/A')
        language = language_raw.upper() if language_raw != 'N/A' else 'N/A'
        
        seniority_raw = get_val('seniority', 'N/A')
        seniority = seniority_raw.capitalize() if seniority_raw != 'N/A' else 'N/A'
        
        desc = f"""**Job Title:** {title}
**Company:** {company}
**Location:** {location}
**Work Mode:** {work_mode}
**Language:** {language}
**Seniority:** {seniority}

---

"""
        
        # Source and IDs
        source_url = job_data.get('source_url', '')
        stepstone_id = get_val('stepstone_job_id')
        company_ref = get_val('company_job_reference')
        
        if source_url:
            desc += f"**Source:** {source_url}\n"
        desc += f"**Stepstone ID:** {stepstone_id}\n"
        desc += f"**Company Reference:** {company_ref}\n\n---\n\n"
        
        # Job description excerpt (first 300 chars)
        job_desc = job_data.get('job_description', '')
        if job_desc:
            excerpt = job_desc[:300].strip()
            if len(job_desc) > 300:
                excerpt += "..."
            desc += f"**Job Description (excerpt):**\n{excerpt}\n\n---\n\n"
        
        # Company address and links
        addr_line1 = get_val('company_address_line1', '')
        addr_line2 = get_val('company_address_line2', '')
        career_page = job_data.get('career_page_link', '')
        direct_apply = job_data.get('direct_apply_link', '')
        
        if addr_line1 or addr_line2:
            desc += "**Company Address:**\n"
            if addr_line1:
                desc += f"{addr_line1}\n"
            if addr_line2:
                desc += f"{addr_line2}\n"
            desc += "\n"
        
        if career_page:
            desc += f"**Career Page:** {career_page}\n"
        if direct_apply:
            desc += f"**Direct Apply:** {direct_apply}\n"
        
        return desc.strip()
    
    def _enrich_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich job_data with detected language, seniority, and normalized work_mode.
        
        Args:
            job_data: Original job data dict
            
        Returns:
            Enriched copy of job_data with language, seniority, and work_mode normalized
        """
        enriched = job_data.copy()
        
        # Detect language if not already present
        if not enriched.get('language'):
            job_desc = enriched.get('job_description', '')
            if job_desc:
                # Simple heuristic: count German vs English common words
                de_words = ['und', 'der', 'die', 'das', 'sie', 'mit', 'für', 'auf', 'von', 'zu']
                en_words = ['the', 'and', 'you', 'with', 'for', 'our', 'your', 'this', 'that', 'are']
                
                desc_lower = job_desc.lower()
                de_count = sum(desc_lower.count(w) for w in de_words)
                en_count = sum(desc_lower.count(w) for w in en_words)
                
                enriched['language'] = 'DE' if de_count > en_count else 'EN'
                self.logger.debug("Detected language: %s (DE:%d EN:%d)", enriched['language'], de_count, en_count)
        
        # Detect seniority if not already present
        if not enriched.get('seniority'):
            job_title = (enriched.get('job_title') or '').lower()
            job_desc = (enriched.get('job_description') or '').lower()
            combined = f"{job_title} {job_desc}"
            
            # Seniority patterns
            if any(word in combined for word in ['lead', 'principal', 'head of', 'director', 'chief']):
                enriched['seniority'] = 'lead'
            elif any(word in combined for word in ['senior', 'sr.', 'expert']):
                enriched['seniority'] = 'senior'
            elif any(word in combined for word in ['junior', 'jr.', 'entry', 'trainee', 'graduate']):
                enriched['seniority'] = 'junior'
            else:
                enriched['seniority'] = 'mid'
            
            self.logger.debug("Detected seniority: %s", enriched['seniority'])
        
        # Normalize work_mode
        work_mode = (enriched.get('work_mode') or '').lower()
        if 'remote' in work_mode or 'homeoffice' in work_mode:
            if 'hybrid' in work_mode:
                enriched['work_mode'] = 'hybrid'
            else:
                enriched['work_mode'] = 'remote'
        elif 'hybrid' in work_mode:
            enriched['work_mode'] = 'hybrid'
        elif 'office' in work_mode or 'onsite' in work_mode or 'vor ort' in work_mode:
            enriched['work_mode'] = 'onsite'
        elif not enriched.get('work_mode'):
            # Default if not detected
            enriched['work_mode'] = 'onsite'
            self.logger.debug("Defaulting work_mode to onsite")
        
        return enriched
    
    def _get_label_ids(self, job_data: Dict[str, Any]) -> list:
        """
        Build list of label IDs to apply based on job_data.
        
        Args:
            job_data: Normalized job data dict
            
        Returns:
            List of label IDs to apply
        """
        labels = []
        
        # Work mode labels
        work_mode = (job_data.get('work_mode') or '').lower()
        if work_mode == 'remote' and self.label_remote:
            labels.append(self.label_remote)
        elif work_mode == 'hybrid' and self.label_hybrid:
            labels.append(self.label_hybrid)
        elif work_mode == 'onsite' and self.label_onsite:
            labels.append(self.label_onsite)
        
        # Language labels
        language = (job_data.get('language') or '').upper()
        if language == 'DE' and self.label_de:
            labels.append(self.label_de)
        elif language == 'EN' and self.label_en:
            labels.append(self.label_en)
        
        # Seniority labels
        seniority = (job_data.get('seniority') or '').lower()
        if seniority == 'junior' and self.label_junior:
            labels.append(self.label_junior)
        elif seniority in ['mid', 'mid-level'] and self.label_mid:
            labels.append(self.label_mid)
        elif seniority == 'senior' and self.label_senior:
            labels.append(self.label_senior)
        elif seniority == 'lead' and self.label_lead:
            labels.append(self.label_lead)
        
        return labels
    
    def _check_existing_card(self, card_name: str, source_url: str) -> Optional[str]:
        """
        Check if a card with the same name or source URL already exists in the leads list.
        
        Args:
            card_name: The card name to check
            source_url: The source URL to check in descriptions
            
        Returns:
            Card ID if found, None otherwise
        """
        if not self.leads_list_id:
            return None
        
        try:
            url = f"{self.base_url}/lists/{self.leads_list_id}/cards"
            resp = self.requester('GET', url, params=self.auth_params, timeout=10)
            
            if getattr(resp, 'status_code', 200) == 200:
                cards = resp.json() if hasattr(resp, 'json') else []
                for card in cards:
                    # Ensure card is a dict (not a string)
                    if not isinstance(card, dict):
                        continue
                    
                    # Check by name
                    if card.get('name') == card_name:
                        self.logger.info("Found existing card by name: %s", card.get('id'))
                        return card.get('id')
                    
                    # Check by source URL in description
                    desc = card.get('desc', '')
                    if source_url and source_url in desc:
                        self.logger.info("Found existing card by source URL: %s", card.get('id'))
                        return card.get('id')
            else:
                self.logger.warning("Failed to check existing cards: %s", resp.status_code)
        except Exception as e:
            self.logger.warning("Error checking for existing card: %s", e)
        
        return None
    
    def _set_custom_fields(self, card_id: str, job_data: Dict[str, Any]) -> None:
        """
        Best-effort set custom fields on a card (text, list/dropdown, and date types).
        
        Args:
            card_id: The Trello card ID
            job_data: Normalized job data dict
        """
        # Text fields
        text_fields = [
            (self.field_company, job_data.get('company_name')),
            (self.field_job_title, job_data.get('job_title_clean') or job_data.get('job_title')),
            (self.field_firma_person, "Für Arbeitgeber"),  # Default value matching previous implementation
        ]
        
        for field_id, value in text_fields:
            if not field_id or not value:
                continue
            
            try:
                url = f"{self.base_url}/cards/{card_id}/customField/{field_id}/item"
                payload = {'value': {'text': str(value)[:120]}}
                resp = self.requester(
                    'PUT',
                    url,
                    params=self.auth_params,
                    json=payload,
                    timeout=10
                )
                
                if getattr(resp, 'status_code', 200) in (200, 201):
                    self.logger.debug("Set text field %s = %s", field_id, value)
                else:
                    self.logger.warning("Failed to set text field %s: %s", field_id, resp.status_code)
            except Exception as e:
                self.logger.warning("Error setting text field %s: %s", field_id, e)
        
        # List/dropdown field: Quelle (Source) - set to "Stepstone" for Stepstone URLs
        if self.field_source_list and self.field_source_stepstone_option:
            source_url = job_data.get('source_url', '')
            if 'stepstone' in source_url.lower():
                try:
                    url = f"{self.base_url}/cards/{card_id}/customField/{self.field_source_list}/item"
                    payload = {'idValue': self.field_source_stepstone_option}
                    resp = self.requester(
                        'PUT',
                        url,
                        params=self.auth_params,
                        json=payload,
                        timeout=10
                    )
                    
                    if getattr(resp, 'status_code', 200) in (200, 201):
                        self.logger.debug("Set source to Stepstone")
                    else:
                        self.logger.warning("Failed to set source field: %s", resp.status_code)
                except Exception as e:
                    self.logger.warning("Error setting source field: %s", e)
        
        # Date field: Ausschreibungsdatum (Publication Date)
        if self.field_publication_date and job_data.get('publication_date'):
            try:
                pub_date = job_data['publication_date']
                # Ensure ISO 8601 format
                if not pub_date.endswith('Z') and 'T' in pub_date:
                    pub_date = pub_date + 'Z' if '+' not in pub_date else pub_date
                
                url = f"{self.base_url}/cards/{card_id}/customField/{self.field_publication_date}/item"
                payload = {'value': {'date': pub_date}}
                resp = self.requester(
                    'PUT',
                    url,
                    params=self.auth_params,
                    json=payload,
                    timeout=10
                )
                
                if getattr(resp, 'status_code', 200) in (200, 201):
                    self.logger.debug("Set publication date: %s", pub_date)
                else:
                    self.logger.warning("Failed to set publication date: %s", resp.status_code)
            except Exception as e:
                self.logger.warning("Error setting publication date: %s", e)
    
    def create_card_from_job_data(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a Trello card from job data with idempotency, labels, and custom fields.
        
        Args:
            job_data: Normalized job data dict
            
        Returns:
            Response JSON if successful, None otherwise
        """
        if not self.api_key or not self.token:
            self.logger.error("Trello credentials missing")
            print("ERROR: Trello credentials not configured")
            return None
        
        if not self.leads_list_id:
            self.logger.error("Trello leads list ID missing")
            print("ERROR: TRELLO_LIST_ID_LEADS not configured")
            return None
        
        # Enrich job_data with detected language, seniority, normalized work_mode
        enriched_data = self._enrich_job_data(job_data)
        
        # Build card components from enriched data
        card_name = self._build_card_name(enriched_data)
        card_desc = self._build_card_description(enriched_data)
        label_ids = self._get_label_ids(enriched_data)
        source_url = enriched_data.get('source_url', '')
        
        # Check for existing card (idempotency)
        existing_id = self._check_existing_card(card_name, source_url)
        if existing_id:
            self.logger.info("Card already exists: %s", existing_id)
            short_url = f"https://trello.com/c/{existing_id}"
            print(f"Card already exists: {short_url}")
            return {'id': existing_id, 'shortUrl': short_url, 'already_exists': True}
        
        # Create the card
        url = f"{self.base_url}/cards"
        params = dict(self.auth_params)
        params.update({
            'idList': self.leads_list_id,
            'name': card_name,
            'desc': card_desc,
            'pos': 'top',
        })
        
        # Add labels if any
        if label_ids:
            params['idLabels'] = ','.join(label_ids)
        
        try:
            resp = self.requester('POST', url, params=params, timeout=10)
            
            if getattr(resp, 'status_code', 200) in (200, 201):
                card_data = resp.json()
                card_id = card_data.get('id')
                card_url = card_data.get('shortUrl', f"https://trello.com/c/{card_id}")
                
                self.logger.info("Created Trello card: %s", card_id)
                print(f"✓ Trello card created: {card_url}")
                
                # Best-effort: set custom fields
                if card_id:
                    self._set_custom_fields(card_id, enriched_data)
                
                return card_data
            else:
                self.logger.error("Failed to create card: %s %s", resp.status_code, getattr(resp, 'text', ''))
                print(f"ERROR: Failed to create Trello card (status {resp.status_code})")
                return None
                
        except Exception as e:
            self.logger.error("Exception creating card: %s", e, exc_info=True)
            print(f"ERROR: Exception creating Trello card: {e}")
            return None
