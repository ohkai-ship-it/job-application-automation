import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('config/credentials.env')

class TrelloManager:
    """
    Manages Trello card creation and updates for job applications
    """
    
    def __init__(self):
        #self.api_key = os.getenv('TRELLO_KEY')
        #self.token = os.getenv('TRELLO_TOKEN')
        #self.board_id = os.getenv('TRELLO_BOARD_ID')
        #self.leads_list_id = os.getenv('TRELLO_LIST_ID_LEADS')
        #self.template_card_id = os.getenv('TRELLO_TEMPLATE_CARD_ID')

        
        # Hardcoded credentials (temporary fix)
        self.api_key = "0e7aa288ad7ee04d6bc72481cc071579"
        self.token = "ATTAb139469c8e9ad52ad7183c812b7ed69b29399040b3867cc058a3332f99913b60520DDEAD"
        self.board_id = "67ade85d017673cf0c5599ba"
        self.leads_list_id = "67ade85d52bbd32a499bed5c"
        self.template_card_id = "67adf71aec1dabfa78c38cf8"
        
        self.base_url = "https://api.trello.com/1"
        self.auth_params = {
            'key': self.api_key,
            'token': self.token
        }
        
        # Custom field IDs (from your board)
        self.custom_fields = {
            'company_name': '67adf6220fdc6275aca7b534',
            'job_title': '67ade94f323ea62041d1665d',
            'source': '67adec40a91936eec7f48586',  # Dropdown
            'language': '67adead1f1fc6e764c163fdb',  # Dropdown
            'publication_date': '67af420c3e6ce3228172fb1f',
            'application_portal': '67adeccaf57fac30c53a61dd',  # Dropdown
            'company_person': '67b33aa93990ecdb94de23c0',
            'company_email': '67b33ad706da202d65ecda12',
            'company_phone': '67b33abbd14e7bc2a724af44',
        }
        
        # Label IDs
        self.labels = {
            'remote': '67ade85d017673cf0c559a0d',
            'hybrid': '68cbe36915a2d763ea79c337',
            'onsite': '68cbe3759a2bf71a401a8d4d',
            'interesting': '67ade85d017673cf0c559a0e',
        }
        
        # Get dropdown options
        self._load_dropdown_options()
    
    def _load_dropdown_options(self):
        """Load dropdown option IDs for custom fields"""
        try:
            url = f"{self.base_url}/boards/{self.board_id}/customFields"
            response = requests.get(url, params=self.auth_params)
            
            if response.status_code == 200:
                fields = response.json()
                
                # Find Stepstone option ID in Source field
                for field in fields:
                    if field['id'] == self.custom_fields['source']:
                        for option in field.get('options', []):
                            if option['value']['text'] == 'Stepstone':
                                self.stepstone_option_id = option['id']
                                break
        except Exception as e:
            print(f"Warning: Could not load dropdown options: {e}")
    
    def create_card_from_job_data(self, job_data):
        """
        Creates a Trello card from scraped job data
        
        Args:
            job_data (dict): Dictionary containing job information from scraper
            
        Returns:
            dict: Created card data or None if failed
        """
        
        try:
            print(f"\n--- Creating Trello Card ---")
            
            # 1. Generate card name from template
            company = job_data.get('company_name', 'Unknown Company')
            title = job_data.get('job_title', 'Unknown Position')
            card_name = f"{company} - {title}"
            
            # Trello card names have a 16384 character limit, but keep it reasonable
            if len(card_name) > 200:
                card_name = card_name[:197] + "..."
            
            print(f"Card name: {card_name}")
            
            # 2. Create card description
            description = self._build_card_description(job_data)
            
            # 3. Create the card
            create_url = f"{self.base_url}/cards"
            card_params = {
                **self.auth_params,
                'name': card_name,
                'desc': description,
                'idList': self.leads_list_id,
                'pos': 'top'  # Put at top of list
            }
            
            response = requests.post(create_url, params=card_params)
            response.raise_for_status()
            card = response.json()
            card_id = card['id']
            
            print(f"✓ Card created: {card['shortUrl']}")
            
            # 4. Set custom fields
            self._set_custom_fields(card_id, job_data)
            
            # 5. Add labels based on work mode
            self._add_work_mode_label(card_id, job_data.get('work_mode'))
            
            # 6. Add job posting URL as attachment
            if job_data.get('source_url'):
                self._add_attachment(card_id, job_data['source_url'], 'Job Posting')
            
            # 7. Copy checklist from template (if template exists)
            if self.template_card_id:
                self._copy_checklist_from_template(card_id)
            
            print(f"✓ Card fully configured!")
            print(f"✓ View card: {card['shortUrl']}")
            
            return card
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating card: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_card_description(self, job_data):
        """Build card description from job data"""
        
        parts = []
        
        # Job description preview
        if job_data.get('job_description'):
            desc = job_data['job_description']
            preview = desc[:500] + "..." if len(desc) > 500 else desc
            parts.append(f"**Job Description:**\n{preview}\n")
        
        # Key details
        details = []
        if job_data.get('location'):
            details.append(f"📍 Location: {job_data['location']}")
        if job_data.get('work_mode'):
            details.append(f"💼 Work Mode: {job_data['work_mode']}")
        if job_data.get('company_address'):
            details.append(f"🏢 Address: {job_data['company_address']}")
        if job_data.get('publication_date'):
            details.append(f"📅 Published: {job_data['publication_date']}")
        
        if details:
            parts.append("\n**Details:**\n" + "\n".join(details))
        
        # Links
        links = []
        if job_data.get('website_link'):
            links.append(f"🌐 Company Page: {job_data['website_link']}")
        if job_data.get('career_page_link'):
            links.append(f"💼 Career Page: {job_data['career_page_link']}")
        if job_data.get('source_url'):
            links.append(f"🔗 Original Posting: {job_data['source_url']}")
        
        if links:
            parts.append("\n**Links:**\n" + "\n".join(links))
        
        # Contact info (if available)
        contact = job_data.get('contact_person', {})
        if any(contact.values()):
            contact_info = []
            if contact.get('name'):
                contact_info.append(f"👤 Name: {contact['name']}")
            if contact.get('email'):
                contact_info.append(f"📧 Email: {contact['email']}")
            if contact.get('phone'):
                contact_info.append(f"📞 Phone: {contact['phone']}")
            
            if contact_info:
                parts.append("\n**Contact:**\n" + "\n".join(contact_info))
        
        return "\n".join(parts)
    
    def _set_custom_fields(self, card_id, job_data):
        """Set custom field values on the card"""
        
        print("Setting custom fields...")
        
        # Text fields
        text_fields = {
            'company_name': job_data.get('company_name'),
            'job_title': job_data.get('job_title'),
            'company_person': job_data.get('contact_person', {}).get('name'),
            'company_email': job_data.get('contact_person', {}).get('email'),
            'company_phone': job_data.get('contact_person', {}).get('phone'),
        }
        
        for field_name, value in text_fields.items():
            if value:
                self._set_text_field(card_id, self.custom_fields[field_name], value)
        
        # Date field - publication date
        if job_data.get('publication_date'):
            self._set_date_field(card_id, self.custom_fields['publication_date'], 
                                job_data['publication_date'])
        
        # Dropdown - Source (Stepstone)
        if hasattr(self, 'stepstone_option_id'):
            self._set_dropdown_field(card_id, self.custom_fields['source'], 
                                    self.stepstone_option_id)
        
        print("✓ Custom fields set")
    
    def _set_text_field(self, card_id, field_id, value):
        """Set a text custom field"""
        url = f"{self.base_url}/card/{card_id}/customField/{field_id}/item"
        data = {
            **self.auth_params,
            'value': {'text': str(value)}
        }
        requests.put(url, params=self.auth_params, json={'value': {'text': str(value)}})
    
    def _set_date_field(self, card_id, field_id, date_value):
        """Set a date custom field"""
        url = f"{self.base_url}/card/{card_id}/customField/{field_id}/item"
        
        # Convert date string to ISO format if needed
        if isinstance(date_value, str):
            try:
                # Try parsing ISO format
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                date_value = date_obj.isoformat()
            except:
                pass
        
        requests.put(url, params=self.auth_params, json={'value': {'date': date_value}})
    
    def _set_dropdown_field(self, card_id, field_id, option_id):
        """Set a dropdown custom field"""
        url = f"{self.base_url}/card/{card_id}/customField/{field_id}/item"
        requests.put(url, params=self.auth_params, json={'idValue': option_id})
    
    def _add_work_mode_label(self, card_id, work_mode):
        """Add label based on work mode (remote/hybrid/onsite)"""
        
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
            print(f"✓ Added {work_mode} label")
    
    def _add_attachment(self, card_id, url, name):
        """Add URL attachment to card"""
        attach_url = f"{self.base_url}/cards/{card_id}/attachments"
        params = {
            **self.auth_params,
            'url': url,
            'name': name
        }
        requests.post(attach_url, params=params)
        print(f"✓ Added attachment: {name}")
    
    def _copy_checklist_from_template(self, card_id):
        """Copy checklist from template card"""
        try:
            # Get template checklists
            template_url = f"{self.base_url}/cards/{self.template_card_id}/checklists"
            response = requests.get(template_url, params=self.auth_params)
            
            if response.status_code == 200:
                checklists = response.json()
                
                for checklist in checklists:
                    # Create checklist on new card
                    create_url = f"{self.base_url}/checklists"
                    params = {
                        **self.auth_params,
                        'idCard': card_id,
                        'name': checklist['name']
                    }
                    new_checklist = requests.post(create_url, params=params).json()
                    
                    # Add checklist items
                    for item in checklist['checkItems']:
                        item_url = f"{self.base_url}/checklists/{new_checklist['id']}/checkItems"
                        item_params = {
                            **self.auth_params,
                            'name': item['name']
                        }
                        requests.post(item_url, params=item_params)
                
                print(f"✓ Copied checklist from template")
        except Exception as e:
            print(f"Warning: Could not copy checklist: {e}")


# Test function
if __name__ == "__main__":
    # Test with sample data
    test_job_data = {
        'company_name': 'Test Company GmbH',
        'job_title': 'Senior Python Developer',
        'location': 'Berlin',
        'work_mode': 'hybrid',
        'company_address': 'Teststraße 123, 10115 Berlin',
        'publication_date': '2025-10-10T12:00:00Z',
        'job_description': 'This is a test job description for a senior Python developer position.',
        'source_url': 'https://www.stepstone.de/test-job',
        'website_link': 'https://www.testcompany.com',
        'contact_person': {
            'name': 'Max Mustermann',
            'email': 'max@testcompany.com',
            'phone': '+49 30 12345678'
        }
    }
    
    manager = TrelloManager()
    card = manager.create_card_from_job_data(test_job_data)
    
    if card:
        print(f"\n✓ Test successful! Card created: {card['shortUrl']}")
    else:
        print("\n✗ Test failed!")