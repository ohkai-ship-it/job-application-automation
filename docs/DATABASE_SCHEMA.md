# Database Schema Design

## Overview
**Lightweight SQLite database for duplicate detection and generation tracking.**

**Philosophy:** Trello is the source of truth for application tracking. The database serves as a support tool to:
1. ✅ Prevent accidentally applying to the same job twice
2. ✅ Track what was generated (cover letters, AI costs)
3. ✅ Link generated files to Trello cards
4. ✅ Provide generation history/audit trail

**NOT for:** Status tracking, analytics, application management (Trello does this)

**Database Location:** `data/applications.db`

---

## Tables

### 1. `processed_jobs` (Duplicate Detection)

**Purpose:** Simple tracking of which URLs have been processed to prevent re-processing.

```sql
CREATE TABLE processed_jobs (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Unique Job Identifier (SHA256 hash of source_url for fast lookup)
    job_id TEXT UNIQUE NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    
    -- Basic Job Info (for human reference)
    company_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    
    -- Processing Metadata
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cover_letter_generated BOOLEAN DEFAULT 1,
    
    -- Links to External Systems
    trello_card_id TEXT,
    trello_card_url TEXT,
    docx_file_path TEXT,
    
    -- Notes
    notes TEXT
);

-- Indexes for Fast Duplicate Checks
CREATE INDEX idx_jobs_job_id ON processed_jobs(job_id);
CREATE INDEX idx_jobs_url ON processed_jobs(source_url);
CREATE INDEX idx_jobs_processed_at ON processed_jobs(processed_at DESC);
```

**Key Features:**
- Fast duplicate detection via `job_id` (SHA256 hash of URL)
- Stores minimal info (company, title) for human reference
- Links to Trello card for full tracking
- Path to generated DOCX file

---

### 2. `generation_metadata` (AI Generation Tracking)

**Purpose:** Track AI usage, costs, and generation quality for each job.

```sql
CREATE TABLE generation_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,  -- Links to processed_jobs
    
    -- AI Generation Details
    ai_model TEXT NOT NULL,           -- "gpt-4o-mini", "claude-3-haiku"
    language TEXT CHECK(language IN ('de', 'en')),
    word_count INTEGER,
    generation_cost REAL,             -- USD
    
    -- Quality Metrics
    prompt_version TEXT,              -- Track prompt changes
    generation_time_seconds REAL,
    
    -- Generated Content (for comparison/regeneration)
    cover_letter_text TEXT,
    
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (job_id) REFERENCES processed_jobs(job_id) ON DELETE CASCADE
);

-- Index for retrieving generations
CREATE INDEX idx_metadata_job_id ON generation_metadata(job_id);
CREATE INDEX idx_metadata_model ON generation_metadata(ai_model);
CREATE INDEX idx_metadata_generated_at ON generation_metadata(generated_at DESC);
```

**Key Features:**
- Multiple generations per job (if regenerated)
- Track AI costs for budget monitoring
- Store text for comparison/reference
- Link to job via `job_id`

---

## Database Schema Diagram

```
┌─────────────────────┐
│  processed_jobs     │  ← Main table for duplicate detection
├─────────────────────┤
│ id (PK)            │
│ job_id (UNIQUE)    │  ← SHA256(source_url) for fast lookup
│ source_url (UNIQUE)│
│ company_name       │
│ job_title          │
│ trello_card_id     │  ← Link to Trello (source of truth)
│ trello_card_url    │
│ docx_file_path     │
│ processed_at       │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────────┐
│ generation_metadata  │  ← Track AI generations
├──────────────────────┤
│ id (PK)             │
│ job_id (FK)         │
│ ai_model            │
│ language            │
│ word_count          │
│ generation_cost     │
│ cover_letter_text   │
│ generated_at        │
└──────────────────────┘
```

**Flow:**
1. User pastes Stepstone URL
2. Calculate `job_id = SHA256(url)`
3. Check `processed_jobs.job_id` → If exists, warn "Already processed!"
4. If new, scrape job data
5. Generate cover letter with AI
6. Save to `processed_jobs` + `generation_metadata`
7. Create Trello card
8. Link Trello card ID back to database

---

## Key Features

### 1. Duplicate Detection (Primary Use Case)
```sql
-- Fast duplicate check before processing
SELECT id, company_name, job_title, processed_at, trello_card_url
FROM processed_jobs 
WHERE job_id = ?;  -- SHA256 hash lookup (indexed, instant)

-- Or by exact URL
SELECT id FROM processed_jobs WHERE source_url = ?;
```

**User Experience:**
```
$ python src/main.py https://stepstone.de/job/12345

⚠️  Already processed!
  Company: ACME Corp
  Job Title: Senior Python Developer
  Processed: 2025-10-10 14:30:00
  Trello Card: https://trello.com/c/abc123
  
  Continue anyway? (y/N):
```

### 2. Generation History Tracking
```sql
-- Get all generations for a job (if regenerated multiple times)
SELECT ai_model, word_count, generation_cost, generated_at
FROM generation_metadata
WHERE job_id = ?
ORDER BY generated_at DESC;
```

### 3. Cost Monitoring
```sql
-- Total AI costs this month
SELECT 
    COUNT(*) as generations,
    SUM(generation_cost) as total_cost,
    AVG(generation_cost) as avg_cost
FROM generation_metadata
WHERE generated_at >= date('now', 'start of month');
```

### 4. Find Jobs by Company
```sql
-- Check if already applied to this company
SELECT job_title, processed_at, trello_card_url
FROM processed_jobs
WHERE company_name LIKE ?
ORDER BY processed_at DESC;
```

---

## Database Location & Backup

**Primary Database:**
```
data/applications.db
```

**Backup Strategy:**
- Automated daily backups to `data/backups/applications_YYYYMMDD.db`
- Keep last 30 days of backups
- Optional cloud sync (Google Drive, Dropbox)

**Size Estimates:**
- ~100 KB for 100 applications
- ~1 MB for 1,000 applications
- ~10 MB for 10,000 applications

---

## Migration Strategy

### Initial Creation
```python
# src/helper/init_database.py
python src/helper/init_database.py
```

### Schema Updates (Future)
```python
# Version control for schema changes
SCHEMA_VERSION = 1

# Migration files:
# migrations/001_initial_schema.sql
# migrations/002_add_response_tracking.sql
# migrations/003_add_companies_table.sql
```

---

## Next Steps

1. ✅ **Schema Designed** (this document)
2. ⏳ **Implement `src/database.py`** - Python wrapper class
3. ⏳ **Create init script** - `src/helper/init_database.py`
4. ⏳ **Integrate into workflow** - Update `main.py` and `app.py`
5. ⏳ **Add tests** - Database operation tests
6. ⏳ **Test with real data** - Process jobs and verify storage

---

## Example Usage (Preview)

```python
from database import ApplicationDB

db = ApplicationDB()

# 1. Check for duplicate BEFORE scraping/processing
is_duplicate, existing_job = db.check_duplicate(job_url)

if is_duplicate:
    print(f"⚠️  Already processed on {existing_job['processed_at']}")
    print(f"   Company: {existing_job['company_name']}")
    print(f"   Trello: {existing_job['trello_card_url']}")
    
    if not user_confirms_reprocess():
        return  # Skip processing

# 2. Process job (scrape, generate cover letter, create Trello card)
job_data = scrape_stepstone(job_url)
cover_letter = generate_cover_letter(job_data)
trello_card = create_trello_card(job_data)
docx_path = save_docx(cover_letter, job_data)

# 3. Save to database AFTER successful processing
db.save_processed_job(
    source_url=job_url,
    company_name=job_data['company_name'],
    job_title=job_data['job_title'],
    trello_card_id=trello_card['id'],
    trello_card_url=trello_card['url'],
    docx_file_path=docx_path,
    
    # Generation metadata
    ai_model='gpt-4o-mini',
    language='de',
    word_count=189,
    generation_cost=0.0002,
    cover_letter_text=cover_letter
)

# 4. Optional: Get processing history
recent_jobs = db.get_recent_jobs(limit=10)
for job in recent_jobs:
    print(f"{job['processed_at']}: {job['company_name']} - {job['job_title']}")

# 5. Optional: Check AI costs this month
stats = db.get_cost_stats(period='month')
print(f"Processed {stats['count']} jobs this month")
print(f"Total AI cost: ${stats['total_cost']:.4f}")
```

---

**Ready to implement?** Let me know and I'll create the `src/database.py` implementation! 🚀
