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
    from .utils.log_config import get_logger
    from .utils.env import load_env, get_str
    from .utils.http_utils import request_with_retries
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.log_config import get_logger
    from utils.env import load_env, get_str
    from utils.http_utils import request_with_retries


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
        
        # Label IDs for location
        self.label_ddd = get_str('TRELLO_LABEL_DDD', default='')  # Düsseldorf
        
        # Label IDs for language (deprecated - using custom field instead)
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
        self.field_source_linkedin_option = get_str('TRELLO_FIELD_QUELLE_LINKEDIN', default='')  # LinkedIn option ID
        
        self.field_sprache = get_str('TRELLO_FIELD_SPRACHE', default='')  # Sprache (Language)
        self.field_sprache_de_de = get_str('TRELLO_FIELD_SPRACHE_DE_DE', default='')  # DE -> DE
        self.field_sprache_en_en = get_str('TRELLO_FIELD_SPRACHE_EN_EN', default='')  # EN -> EN
        self.field_sprache_en_de = get_str('TRELLO_FIELD_SPRACHE_EN_DE', default='')  # EN -> DE
        self.field_sprache_de_en = get_str('TRELLO_FIELD_SPRACHE_DE_EN', default='')  # DE -> EN
        
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
        Build card description with ONLY the complete job description text.
        No formatting, no company info - just the raw JD text.
        
        Args:
            job_data: Normalized job data dict
            
        Returns:
            Job description text only
        """
        # Return only the job description text, nothing else
        return job_data.get('job_description', 'No job description available')
    
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
        
        # Location labels - add DDD if Düsseldorf
        location = (job_data.get('location') or '').lower()
        if 'düsseldorf' in location and self.label_ddd:
            labels.append(self.label_ddd)
        
        # Language labels (deprecated - using custom field instead, but keeping for backwards compatibility)
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
        
        # List/dropdown field: Quelle (Source) - set to "Stepstone" or "LinkedIn" based on URL
        if self.field_source_list:
            source_url = job_data.get('source_url', '')
            source_option_id = None
            source_name = None
            
            if 'stepstone' in source_url.lower() and self.field_source_stepstone_option:
                source_option_id = self.field_source_stepstone_option
                source_name = "Stepstone"
            elif 'linkedin' in source_url.lower() and self.field_source_linkedin_option:
                source_option_id = self.field_source_linkedin_option
                source_name = "LinkedIn"
            
            if source_option_id:
                try:
                    url = f"{self.base_url}/cards/{card_id}/customField/{self.field_source_list}/item"
                    payload = {'idValue': source_option_id}
                    resp = self.requester(
                        'PUT',
                        url,
                        params=self.auth_params,
                        json=payload,
                        timeout=10
                    )
                    
                    if getattr(resp, 'status_code', 200) in (200, 201):
                        self.logger.debug("Set source to %s", source_name)
                    else:
                        self.logger.warning("Failed to set source field: %s", resp.status_code)
                except Exception as e:
                    self.logger.warning("Error setting source field: %s", e)
        
        # List/dropdown field: Sprache (Language) - set based on detected language
        if self.field_sprache:
            language = (job_data.get('language') or '').upper()
            sprache_option_id = None
            
            # Map language to Sprache field option
            if language == 'DE' and self.field_sprache_de_de:
                sprache_option_id = self.field_sprache_de_de  # DE -> DE
            elif language == 'EN' and self.field_sprache_en_en:
                sprache_option_id = self.field_sprache_en_en  # EN -> EN
            
            if sprache_option_id:
                try:
                    url = f"{self.base_url}/cards/{card_id}/customField/{self.field_sprache}/item"
                    payload = {'idValue': sprache_option_id}
                    resp = self.requester(
                        'PUT',
                        url,
                        params=self.auth_params,
                        json=payload,
                        timeout=10
                    )
                    
                    if getattr(resp, 'status_code', 200) in (200, 201):
                        self.logger.debug("Set Sprache to %s", language)
                    else:
                        self.logger.warning("Failed to set Sprache field: %s", resp.status_code)
                except Exception as e:
                    self.logger.warning("Error setting Sprache field: %s", e)
        
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
    
    def _set_card_location(self, card_id: str, job_data: Dict[str, Any]) -> None:
        """
        Set card location (map) based on job location.
        - If remote: set to "Germany"
        - If location is Düsseldorf: keep default (Düsseldorf)
        - Otherwise: set to job location city
        
        Args:
            card_id: The Trello card ID
            job_data: Normalized job data dict
        """
        work_mode = (job_data.get('work_mode') or '').lower()
        location = job_data.get('location', 'Düsseldorf')
        
        # Determine what location to set
        location_name = None
        if work_mode == 'remote':
            location_name = 'Germany'
        elif 'düsseldorf' not in location.lower():
            # Extract just city name (remove country, postal codes, etc.)
            # Simple heuristic: take first part before comma
            city = location.split(',')[0].strip()
            # Add ", Deutschland" to help Trello geocode correctly (Trello uses German locale)
            location_name = f"{city}, Deutschland"
        # else: keep Düsseldorf as default (don't set location, let template default apply)
        
        if location_name:
            try:
                url = f"{self.base_url}/cards/{card_id}"
                # Try setting both locationName and address for compatibility
                payload = {
                    'locationName': location_name,
                    'address': location_name
                }
                resp = self.requester(
                    'PUT',
                    url,
                    params=self.auth_params,
                    json=payload,
                    timeout=10
                )
                
                if getattr(resp, 'status_code', 200) in (200, 201):
                    self.logger.debug("Set card location to: %s", location_name)
                else:
                    self.logger.warning("Failed to set card location: %s", resp.status_code)
            except Exception as e:
                self.logger.warning("Error setting card location: %s", e)
    
    def _add_attachments(self, card_id: str, job_data: Dict[str, Any]) -> None:
        """
        Add attachments to the card:
        - Stepstone link as "Ausschreibung"
        - Company career page as "Firmenportal" (if available)
        
        Args:
            card_id: The Trello card ID
            job_data: Normalized job data dict
        """
        attachments_to_add = []
        
        # Add Stepstone link (source URL)
        source_url = job_data.get('source_url', '')
        if source_url:
            attachments_to_add.append(('Ausschreibung', source_url))
        
        # Add career page if available
        career_page = job_data.get('career_page_link', '')
        if career_page:
            attachments_to_add.append(('Firmenportal', career_page))
        
        # Add each attachment
        for name, url_to_attach in attachments_to_add:
            try:
                url = f"{self.base_url}/cards/{card_id}/attachments"
                payload = {
                    'name': name,
                    'url': url_to_attach
                }
                resp = self.requester(
                    'POST',
                    url,
                    params=self.auth_params,
                    json=payload,
                    timeout=10
                )
                
                if getattr(resp, 'status_code', 200) in (200, 201):
                    self.logger.debug("Added attachment '%s': %s", name, url_to_attach)
                else:
                    self.logger.warning("Failed to add attachment '%s': %s", name, resp.status_code)
            except Exception as e:
                self.logger.warning("Error adding attachment '%s': %s", name, e)
    
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
                
                # Best-effort: set custom fields and attachments
                if card_id:
                    self._set_custom_fields(card_id, enriched_data)
                    # TODO: Location/map feature - Trello's geocoding is unreliable via API
                    # self._set_card_location(card_id, enriched_data)
                    self._add_attachments(card_id, enriched_data)
                
                return card_data
            else:
                self.logger.error("Failed to create card: %s %s", resp.status_code, getattr(resp, 'text', ''))
                print(f"ERROR: Failed to create Trello card (status {resp.status_code})")
                return None
                
        except Exception as e:
            self.logger.error("Exception creating card: %s", e, exc_info=True)
            print(f"ERROR: Exception creating Trello card: {e}")
            return None
