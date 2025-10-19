# 🔄 Processing Pipeline - Step-by-Step Breakdown

**Date:** October 18, 2025  
**Current Status:** Processing 1 of 2 jobs (50%)

---

## 📊 Current Processing Flow

```
┌─────────────────────────────────────────────────────────┐
│  Processing: 1 of 2                              50%    │
│  ██████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Job Pipeline Architecture

Each job goes through **4 major phases** with detailed substeps:

```
JOB INPUT
    ↓
PHASE 1: SCRAPING (Collecting Info)
    ├─ Fetch URL
    ├─ Parse HTML/JSON-LD
    ├─ Extract Job Data
    │   ├─ Company Name
    │   ├─ Job Title
    │   ├─ Job Description
    │   ├─ Location
    │   ├─ Company Address
    │   └─ Career Portal Link
    ├─ Validate Data
    └─ Save to job_data dict
    ↓
PHASE 2: TRELLO INTEGRATION
    ├─ Authenticate with Trello API
    ├─ Create Trello Card
    ├─ Set Custom Fields
    │   ├─ Quelle (Source: LinkedIn/Stepstone)
    │   ├─ Status
    │   ├─ Location
    │   └─ Seniority Level
    ├─ Add Labels
    ├─ Attach Job Description
    ├─ Attach Career Portal Link
    ├─ Copy Checklist from Template
    └─ Get Trello Card URL
    ↓
PHASE 3: COVER LETTER GENERATION
    ├─ Load User CV (DE/EN)
    ├─ Detect Job Language
    ├─ Detect Seniority Level
    ├─ Build AI Prompt
    ├─ Call OpenAI API
    ├─ Generate Cover Letter (180-240 words)
    ├─ Validate Word Count
    └─ Save as TXT file
    ↓
PHASE 4: DOCUMENT GENERATION
    ├─ Load DOCX Template
    ├─ Replace Placeholders
    │   ├─ {{COMPANY_NAME}}
    │   ├─ {{JOB_TITLE}}
    │   ├─ {{LOCATION}}
    │   ├─ {{SENDER_NAME}}
    │   ├─ {{SALUTATION}}
    │   ├─ {{COVER_LETTER_BODY}}
    │   └─ {{VALEDICTION}}
    ├─ Generate DOCX File
    ├─ Convert to PDF (optional)
    └─ Save Files
    ↓
COMPLETION
    └─ Return Results (file paths, Trello URL, success status)
```

---

## 📋 Current Example: Job 1 of 2 (50%)

### **Job Details**
```
URL: https://www.stepstone.de/stellenangebote--...
Status: PROCESSING
Queue Position: 1 of 2
Progress: 50%
```

### **Processing Timeline**

#### **PHASE 1: SCRAPING (20% → 40%)**

**Step 1.1: Fetch & Parse** ✅
```javascript
// Frontend reports this step
job.status = 'processing';
job.progress = 20;
updateProgressBar(); // 20%
```
**Backend executes:**
```python
result = process_job_posting(url, generate_cover_letter=True)
# Step 1: Scrape job posting
logger.info("STEP 1: Scraping job posting...")
job_data = scraper.scrape_job(url)
```
**Data extracted:**
- ✅ Company Name: "TechCorp GmbH"
- ✅ Job Title: "Senior Frontend Developer"
- ✅ Location: "Berlin, Germany"
- ✅ Description: (7,825+ characters with Playwright)
- ✅ Company Address: (regex-extracted)
- ✅ Career Portal: (auto-generated link)

**Step 1.2: Validation** ✅
```python
# Check job_data has required fields
assert job_data['company_name']
assert job_data['job_title']
assert job_data['job_description']
assert job_data['location']
```

**Progress indicator:** `progress = 20%` ✅

---

#### **PHASE 2: TRELLO INTEGRATION (40% → 60%)**

**Step 2.1: Create Trello Card** ✅
```python
logger.info("STEP 2: Creating Trello card...")
trello_result = TrelloManager.create_card_from_job_data(job_data)
```

**Trello API calls:**
```
POST /1/cards
├─ name: "Senior Frontend Developer - TechCorp GmbH"
├─ desc: "[Job description content]"
├─ idList: [LEADS_LIST_ID]
├─ labels: ["Active", "Frontend"]
└─ Response: { id: "68f25b3a042143ca8c111509" }
```

**Step 2.2: Set Custom Fields** ✅
```python
# Set Quelle (Source)
trello_api.set_field(card_id, 'Quelle', 'LinkedIn')
# Result: 67adec40a91936eec7f48587 (option ID)

# Set Status
trello_api.set_field(card_id, 'Status', 'New')

# Set Location
trello_api.set_field(card_id, 'Location', 'Berlin')

# Set Seniority
trello_api.set_field(card_id, 'Seniority', 'Senior')
```

**Step 2.3: Add Attachments** ✅
```python
# Attach Job Description
trello_api.attach_file(card_id, 'Ausschreibung', job_description_url)

# Attach Career Portal Link
trello_api.attach_link(card_id, 'Career Portal', portal_url)
```

**Step 2.4: Copy Template Checklist** ✅
```python
# Get template card
template_card = TrelloManager.get_template_card()

# Copy all checklist items to new card
for item in template_card.checklists:
    trello_api.copy_checklist(template_id, card_id)
```

**Trello Card Created:**
```
✓ Card ID: 68f25b3a042143ca8c111509
✓ Card URL: https://trello.com/c/8KYhg3eA
✓ Title: "Senior Frontend Developer - TechCorp GmbH"
✓ Status: New / Active
✓ Location: Berlin
✓ Seniority: Senior
✓ Source: LinkedIn
✓ Attachments: ✓ Description ✓ Portal Link
✓ Checklist: ✓ Copied from template
```

**Progress indicator:** `progress = 60%` ✅

---

#### **PHASE 3: COVER LETTER GENERATION (60% → 80%)**

**Step 3.1: Prepare AI Context** ✅
```python
logger.info("STEP 3: Generating cover letter...")

# Load CV files
cv_de = CoverLetterGenerator.load_cv('data/cv_de.pdf')
cv_en = CoverLetterGenerator.load_cv('data/cv_en.pdf')
```

**Step 3.2: Language Detection** ✅
```python
# Detect job posting language
language = CoverLetterGenerator.detect_language(job_data['job_description'])
# Result: 'de' (German)

# Build appropriate prompt
if language == 'de':
    prompt = GERMAN_COVER_LETTER_PROMPT
    cv = cv_de
else:
    prompt = ENGLISH_COVER_LETTER_PROMPT
    cv = cv_en
```

**Step 3.3: Seniority Detection** ✅
```python
# Detect job level from title
seniority = CoverLetterGenerator.detect_seniority(job_data['job_title'])
# Result: 'senior' (from "Senior Frontend Developer")

# Adjust prompt tone accordingly
prompt = prompt.format(seniority=seniority)
```

**Step 3.4: Build & Send AI Prompt** ✅
```python
# Construct full prompt with CV + job data
full_prompt = f"""
[System prompt for German formal letter]

Candidate CV: {cv_content}
Company: {job_data['company_name']}
Job Title: {job_data['job_title']}
Job Description: {job_data['job_description']}
Required: 180-240 words
Seniority Level: {seniority}
"""

# Call OpenAI API
response = OpenAI.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": full_prompt}]
)
```

**Step 3.5: Validate & Format** ✅
```python
cover_letter_text = response['choices'][0]['message']['content']

# Validate word count (180-240 words required)
word_count = len(cover_letter_text.split())
assert 180 <= word_count <= 240, f"Word count {word_count} out of range"

# Format cover letter with salutation + body + valediction
formatted_letter = f"""
Liebes TechCorp-Team,

{cover_letter_text}

Beste Grüße,
Kai Voges
"""
```

**Cover Letter Generated:**
```
✓ Language: German (Deutsch)
✓ Seniority: Senior
✓ Word Count: 184 words (valid: 180-240)
✓ Format: Formal German letter
✓ Saved: output/cover_letters/Anschreiben - Kai Voges - 2025-10-18 - TechCorp.txt
```

**Progress indicator:** `progress = 80%` ✅

---

#### **PHASE 4: DOCUMENT GENERATION (80% → 100%)**

**Step 4.1: Load DOCX Template** ✅
```python
logger.info("STEP 4: Creating Word document...")

# Load German template
template_docx = Document('data/template_de.docx')
```

**Step 4.2: Replace Placeholders** ✅
```python
# Define replacements
replacements = {
    '{{COMPANY_NAME}}': 'TechCorp GmbH',
    '{{JOB_TITLE}}': 'Senior Frontend Developer',
    '{{LOCATION}}': 'Berlin',
    '{{SENDER_NAME}}': 'Kai Voges',
    '{{SALUTATION}}': 'Liebes TechCorp-Team,',
    '{{COVER_LETTER_BODY}}': cover_letter_text,
    '{{VALEDICTION}}': 'Beste Grüße'
}

# Replace in all paragraphs (preserves formatting)
for paragraph in template_docx.paragraphs:
    for placeholder, value in replacements.items():
        if placeholder in paragraph.text:
            # Use _replace_in_paragraph to preserve runs
            WordCoverLetterGenerator._replace_in_paragraph(
                paragraph, placeholder, value
            )
```

**Step 4.3: Save DOCX** ✅
```python
# Generate filename
filename = f"Anschreiben - Kai Voges - {date} - TechCorp GmbH.docx"
docx_path = Path('output/cover_letters') / filename

# Save document
template_docx.save(docx_path)
# Result: output/cover_letters/Anschreiben - Kai Voges - 2025-10-18 - TechCorp.docx
```

**Step 4.4: Convert to PDF (optional)** ✅
```python
# Check if PDF generation enabled
if settings.generate_pdf:
    pdf_path = PDFGenerator.convert_to_pdf(docx_path)
    # Result: output/cover_letters/Anschreiben - Kai Voges - 2025-10-18 - TechCorp.pdf
```

**Documents Generated:**
```
✓ DOCX: output/cover_letters/Anschreiben - Kai Voges - 2025-10-18 - TechCorp.docx
✓ PDF: output/cover_letters/Anschreiben - Kai Voges - 2025-10-18 - TechCorp.pdf
✓ Formatting: ✓ Preserved ✓ Professional layout
```

**Progress indicator:** `progress = 100%` ✅

---

## 🔄 Real-Time Progress Updates

### **UI Progress Bar Stages**

```javascript
// Stage 1: Initialize
job.progress = 0;
job.status = 'processing';
updateProgressBar(); // 0%
// Display: "Processing: 1 of 2 | 0%"

// Stage 2: After scraping starts
job.progress = 20;
updateProgressBar();
// Display: "Processing: 1 of 2 | 20%"

// Stage 3: After Trello created
job.progress = 60;
updateProgressBar();
// Display: "Processing: 1 of 2 | 60%"

// Stage 4: After cover letter generated
job.progress = 80;
updateProgressBar();
// Display: "Processing: 1 of 2 | 80%"

// Stage 5: Complete
job.progress = 100;
job.status = 'completed';
updateProgressBar();
// Display: "Processing: 1 of 2 | 100%"

// Mark Job 1 Complete, Start Job 2
results.completed++;
processNextJob(); // Starts job 2

// Stage 6: Job 2 Processing
job.progress = 50;
job.status = 'processing';
updateProgressBar();
// Display: "Processing: 2 of 2 | 50%"
```

---

## 📊 Progress Visualization

### **Current State (50% - Job 1 Complete, Job 2 Processing)**

```
┌─ Job 1: COMPLETED ─┐
│ Senior Frontend Developer - TechCorp GmbH
│ Status: ✅ Completed
│ ├─ Scraping: ✅ 20% → 40%
│ ├─ Trello: ✅ 40% → 60%
│ ├─ Cover Letter: ✅ 60% → 80%
│ └─ Documents: ✅ 80% → 100%
│
├─ Files Generated:
│ ├─ ✅ Anschreiben - Kai Voges - 2025-10-18 - TechCorp.docx
│ ├─ ✅ Anschreiben - Kai Voges - 2025-10-18 - TechCorp.pdf
│ └─ ✅ Trello Card: https://trello.com/c/8KYhg3eA
│
├─ Custom Fields Set:
│ ├─ Quelle: LinkedIn
│ ├─ Status: New
│ ├─ Location: Berlin
│ └─ Seniority: Senior
└─

┌─ Job 2: PROCESSING (50%) ─┐
│ React Developer - StartUp Inc
│ Status: 🔄 Processing
│ ├─ Scraping: ✅ 20% → 40%
│ ├─ Trello: 🔄 Currently at 60%
│ ├─ Cover Letter: ⏳ Pending
│ └─ Documents: ⏳ Pending
│
└─ Current Step: Creating Trello Card...
```

### **Progress Bar Breakdown**

```
0%    20%   40%   60%   80%   100%
|     |     |     |     |     |
|-----|-----|-----|-----|-----|
SCRAPE TRELLO COVER LETTER DOCS
```

**Current Position (Job 1 + Job 2):**
- Job 1: 100% complete
- Job 2: 50% complete (Trello step)
- **Overall: (100 + 50) / 2 = 50%** ✅

---

## 🎯 Queue Table Display

```
┌────────────────────────────────────────────────────────────┐
│ Job Title              │ Company       │ Status      │ Actions
├────────────────────────────────────────────────────────────┤
│ Senior Frontend Dev    │ TechCorp GmbH │ ✅ Completed│ 📄 Word 🔗 Trello
├────────────────────────────────────────────────────────────┤
│ React Developer        │ StartUp Inc   │ 🔄 Processing│ --
└────────────────────────────────────────────────────────────┘
```

---

## 📈 Performance Metrics

### **Per-Job Timeline**

| Phase | Duration | Progress | Status |
|-------|----------|----------|--------|
| **Scraping** | ~3-5s | 0% → 20% | ✅ Parsing HTML/JSON-LD |
| **Trello** | ~5-10s | 20% → 60% | 🔄 API calls, attachments |
| **Cover Letter** | ~8-15s | 60% → 80% | ⏳ Waiting on AI |
| **Documents** | ~2-3s | 80% → 100% | ⏳ Template replacement |
| **TOTAL** | ~20-40s | 0% → 100% | Per job |

### **Batch Timeline (2 jobs)**

```
Job 1: [████████████████████████████] 20-40s
Job 2:                                [████████████] 10-20s (running)
────────────────────────────────────────────
Total elapsed: ~25 seconds (showing 50%)
Estimated total: ~40-60 seconds for all jobs
```

---

## 🔗 Results Summary After Completion

```
┌─ Results Summary ─────────────────────┐
│ ✅ 2 Cover Letters Generated
│ ✅ 2 Trello Cards Created
│ ❌ 0 Errors
│
├─ Recent Files:
│ 📄 Anschreiben - Kai Voges - 2025-10-18 - TechCorp.docx (2 min ago)
│ 📄 Anschreiben - Kai Voges - 2025-10-18 - StartUp.docx (1 min ago)
│
├─ Links:
│ 🔗 View All Outputs →
│
└─ Ready for next batch!
```

---

## 📝 Technical Flow Summary

```
INPUT URL
    ↓
[SCRAPER] Extract job_data
    - company_name: "TechCorp GmbH"
    - job_title: "Senior Frontend Developer"
    - job_description: "7,825+ chars"
    - location: "Berlin"
    - company_address: "extracted via regex"
    ↓
[TRELLO] Create Card & Set Fields
    - Create card with job data
    - Set Quelle (source: LinkedIn/Stepstone)
    - Set Status, Location, Seniority
    - Attach description, portal link
    - Copy template checklist
    ↓
[AI] Generate Cover Letter
    - Load CV (DE/EN)
    - Detect language: German/English
    - Detect seniority: Junior/Mid/Senior
    - Call OpenAI (GPT-4)
    - Validate word count (180-240)
    ↓
[DOCX] Generate Documents
    - Load template
    - Replace {{PLACEHOLDERS}}
    - Save DOCX
    - Convert to PDF (optional)
    ↓
OUTPUT
    - ✅ Trello URL
    - ✅ DOCX file path
    - ✅ PDF file path (optional)
    - ✅ Success status
```

---

**Status:** Currently processing Job 2 (50% complete in overall batch)
**Next Step:** Awaiting Trello API response to complete card creation
**ETA:** ~20 more seconds to completion

Built with ❤️ on October 18, 2025
