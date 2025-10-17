# Trello Card Layout Implementation

## Overview

The Trello card layout feature provides structured, consistent card creation with automatic label mapping, custom field population, and intelligent field detection.

## Card Name Format

```
[Company Name] Job Title (Location)
```

**Example:**
```
[Acme Inc.] Senior Software Engineer (Remote)
```

## Card Description Structure

The description uses structured markdown with the following sections:

### 1. Key Facts (Top Section)
- **Job Title:** Clean job title (gender markers removed)
- **Company:** Company name
- **Location:** Job location
- **Work Mode:** Remote/Hybrid/Onsite
- **Language:** DE/EN (auto-detected)
- **Seniority:** Junior/Mid/Senior/Lead (auto-detected)

### 2. Source & IDs
- **Source:r** Original Stepstone URL
- **Stepstone ID:** Extracted fom URL
- **Company Reference:** Company's internal job reference number

### 3. Job Description Excerpt
- First 300 characters of the job description

### 4. Company Information
- **Company Address:** Full address (if available)
- **Career Page:** Company career page link
- **Direct Apply:** Direct application link (if found)

## Automatic Field Detection

### Language Detection
- **Method:** Word frequency analysis
- **German indicators:** und, der, die, das, sie, mit, für, auf, von, zu
- **English indicators:** the, and, you, with, for, our, your, this, that, are
- **Result:** Sets `job_data['language']` to 'DE' or 'EN'

### Seniority Detection
- **Lead:** Matches "lead", "principal", "head of", "director", "chief"
- **Senior:** Matches "senior", "sr.", "expert"
- **Junior:** Matches "junior", "jr.", "entry", "trainee", "graduate"
- **Mid:** Default when no indicators found
- **Result:** Sets `job_data['seniority']`

### Work Mode Normalization
- **Remote:** "remote", "homeoffice" (not hybrid)
- **Hybrid:** Contains both "remote"/"homeoffice" AND "hybrid"
- **Onsite:** "office", "onsite", "vor ort", or default
- **Result:** Normalizes `job_data['work_mode']` to 'remote', 'hybrid', or 'onsite'

## Label Mapping

Labels are automatically applied based on detected/enriched fields:

| Field | Value | Label ENV Variable | Notes |
|-------|-------|-------------------|-------|
| work_mode | remote | TRELLO_LABEL_REMOTE | |
| work_mode | hybrid | TRELLO_LABEL_HYBRID | |
| work_mode | onsite | TRELLO_LABEL_ONSITE | |
| language | DE | TRELLO_LABEL_DE | |
| language | EN | TRELLO_LABEL_EN | |
| seniority | junior | TRELLO_LABEL_JUNIOR | |
| seniority | mid | TRELLO_LABEL_MID | Also matches "mid-level" |
| seniority | senior | TRELLO_LABEL_SENIOR | |
| seniority | lead | TRELLO_LABEL_LEAD | |

## Custom Fields

Custom fields are set using best-effort PUT requests (non-fatal on failure):

| Custom Field | Source | ENV Variable | Max Length |
|--------------|--------|--------------|------------|
| Company | `company_name` | TRELLO_FIELD_COMPANY | 120 chars |
| Job Title | `job_title_clean` or `job_title` | TRELLO_FIELD_JOB_TITLE | 120 chars |
| Source | `source_url` | TRELLO_FIELD_SOURCE | 120 chars |
| Language | `language` (uppercase) | TRELLO_FIELD_LANGUAGE | 120 chars |
| Work Mode | `work_mode` (capitalized) | TRELLO_FIELD_WORK_MODE | 120 chars |
| Seniority | `seniority` (capitalized) | TRELLO_FIELD_SENIORITY | 120 chars |

## Idempotency

The system prevents duplicate cards by checking:
1. **Card name match:** Exact match with existing card names in the leads list
2. **Source URL match:** Source URL found in card description

If a match is found, the existing card ID is returned instead of creating a duplicate.

## Configuration

### Required Environment Variables
```bash
TRELLO_KEY=your-trello-key
TRELLO_TOKEN=your-trello-token
TRELLO_BOARD_ID=your-board-id
TRELLO_LIST_ID_LEADS=your-list-id
```

### Optional Label IDs
```bash
# Work Mode Labels
TRELLO_LABEL_REMOTE=
TRELLO_LABEL_HYBRID=
TRELLO_LABEL_ONSITE=

# Language Labels
TRELLO_LABEL_DE=
TRELLO_LABEL_EN=

# Seniority Labels
TRELLO_LABEL_JUNIOR=
TRELLO_LABEL_MID=
TRELLO_LABEL_SENIOR=
TRELLO_LABEL_LEAD=
```

### Optional Custom Field IDs
```bash
TRELLO_FIELD_COMPANY=
TRELLO_FIELD_JOB_TITLE=
TRELLO_FIELD_SOURCE=
TRELLO_FIELD_LANGUAGE=
TRELLO_FIELD_WORK_MODE=
TRELLO_FIELD_SENIORITY=
```

## Finding Label & Custom Field IDs

Use the diagnostics CLI to inspect your Trello board:

```powershell
python -m src.helper.cli trello-inspect
```

This will display:
- Board information
- All lists with IDs
- All labels with colors and IDs
- All custom fields with types and IDs

## Implementation Details

### Key Methods

#### `_enrich_job_data(job_data)`
- Detects language, seniority, and normalizes work_mode
- Returns enriched copy without modifying original
- Only enriches missing fields (preserves existing values)

#### `_build_card_name(job_data)`
- Formats: `[{company}] {title} ({location})`
- Uses `job_title_clean` (gender markers removed) if available

#### `_build_card_description(job_data)`
- Builds structured markdown description
- Handles missing optional fields gracefully (shows "N/A")

#### `_get_label_ids(job_data)`
- Collects applicable label IDs based on work_mode, language, seniority
- Only includes labels with configured IDs

#### `_check_existing_card(card_name, source_url)`
- Queries leads list for existing cards
- Checks by name and source URL
- Returns card ID if found, None otherwise

#### `_set_custom_fields(card_id, job_data)`
- Best-effort PUT requests to set text custom fields
- Non-fatal: logs warnings on failure but doesn't stop card creation
- Truncates values to 120 characters

### Workflow

```
job_data (from scraper)
    ↓
_enrich_job_data() → enriched_data
    ↓
_build_card_name(enriched_data)
_build_card_description(enriched_data)
_get_label_ids(enriched_data)
    ↓
_check_existing_card() → existing card or None
    ↓
CREATE card with labels (if not exists)
    ↓
_set_custom_fields() → best-effort custom field population
    ↓
Return card data
```

## Testing

### Test Coverage
- **test_trello_card_layout.py:** 11 tests covering card formatting, label mapping, idempotency
- **test_trello_enrichment.py:** 17 tests covering language/seniority detection, work mode normalization
- **test_trello_manager.py:** Updated for new attribute-based implementation
- **test_trello_connect_requests.py:** Updated for new card name format

### Running Tests
```powershell
# Run all tests
pytest -v

# Run specific test file
pytest -v tests/unit/test_trello_card_layout.py
pytest -v tests/unit/test_trello_enrichment.py
```

All **108 tests** pass as of this implementation.

## Example Output

### Console Output
```
✓ Trello card created: https://trello.com/c/abc123
```

### Card on Trello Board
**Name:** `[Acme Inc.] Senior Software Engineer (Remote)`

**Labels:** 🏷️ Remote | 🏷️ EN | 🏷️ Senior

**Description:**
```markdown
**Job Title:** Senior Software Engineer
**Company:** Acme Inc.
**Location:** Remote
**Work Mode:** Remote
**Language:** EN
**Seniority:** Senior

---

**Source:** https://www.stepstone.de/...
**Stepstone ID:** 12345678
**Company Reference:** REF-2024-001

---

**Job Description (excerpt):**
We are looking for a Senior Software Engineer to join our team...

---

**Company Address:**
123 Main Street
12345 Berlin

**Career Page:** https://www.acmeinc.de/karriere
```

**Custom Fields:**
- Company: Acme Inc.
- Job Title: Senior Software Engineer
- Source: https://www.stepstone.de/...
- Language: EN
- Work Mode: Remote
- Seniority: Senior

## Future Enhancements (Backlog)

- Template card checklist copying (already partially implemented)
- Additional custom field types (dropdown, date, number)
- More sophisticated language detection (using ML or external library)
- Configurable enrichment behavior (enable/disable per field)
- Bulk card operations (update existing cards)

## See Also

- [API Documentation](API.md)
- [Development Guide](DEVELOPMENT.md)
- [Configuration Reference](../config/.env.example)
