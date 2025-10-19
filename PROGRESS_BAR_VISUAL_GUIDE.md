# Progress Bar Step Indicator - Visual Guide

## UI Layout

### Progress Bar Section (When Processing)

```
┌─────────────────────────────────────────────────────────────────┐
│ Processing: 1 of 3                                           15% │
├─────────────────────────────────────────────────────────────────┤
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ Logging in Trello...                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Processing Pipeline & Progress Ranges

```
Job Processing Lifecycle:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  0%           20%           40%           60%           80%  100%│
│  │             │             │             │             │   │   │
│  └─────────────┼─────────────┼─────────────┼─────────────┼───┤   │
│                │             │             │             │   │   │
│  Scraping  Trello        Cover Letter   Documents   Complete!  │
│  (0-19%)   (20-59%)      (60-79%)       (80-99%)    (100%)     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Stage-by-Stage Display Examples

### Stage 1: Initial Queue Ready
```
Progress Bar Section Hidden
(Shown only when processing starts)
```

### Stage 2: Processing Started (Job 1/3)
```
Processing: 0 of 3 jobs                                         0%

████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Gathering information...
```

**What's Happening**:
- Backend is scraping job data from URL
- Parsing job title, company, description, location
- Extracting job details and structure
- Progress: 0-19%

### Stage 3: Trello Integration (Job 1/3)
```
Processing: 0 of 3 jobs                                        22%

███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Logging in Trello...
```

**What's Happening**:
- Backend is connecting to Trello API
- Creating new card in job board
- Setting custom fields (Source, Location, Salary, etc.)
- Copying checklist from template
- Progress: 20-59%

### Stage 4: Cover Letter Generation (Job 1/3)
```
Processing: 0 of 3 jobs                                        65%

███████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Generating cover letter...
```

**What's Happening**:
- Backend is calling OpenAI API
- Analyzing job description and CV
- Generating personalized cover letter (180-240 words)
- Language detection (German/English)
- Seniority level detection
- Validating word count
- Progress: 60-79%

### Stage 5: Document Creation (Job 1/3)
```
Processing: 0 of 3 jobs                                        85%

███████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Creating documents...
```

**What's Happening**:
- Backend is generating DOCX from template
- Replacing placeholders with cover letter text
- Preserving formatting and styling
- Converting to PDF (if enabled)
- Saving files to output directory
- Progress: 80-99%

### Stage 6: Job Complete, Moving to Job 2/3
```
Processing: 1 of 3 jobs                                        33%

███████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Gathering information...
```

**What's Happening**:
- Job 1 completed successfully
- Files saved and added to results
- Now processing Job 2
- Back to gathering information for new URL

### Stage 7: Multiple Jobs Processing Pattern

```
Job 1: Complete (added to results)   ✅
Job 2: Processing (50% progress)     🔄
Job 3: Queued                        ⏳

Display Shows:
Processing: 1 of 3 jobs                                        50%
███████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Generating cover letter...
```

### Stage 8: All Jobs Complete
```
Processing: 3 of 3 jobs                                       100%

████████████████████████████████████████████████████████████████

Complete!
```

**Result**:
- All 3 jobs processed
- Files downloaded/available
- Stats updated: 3 cover letters, 3 Trello cards, 0 errors

## Real-Time Updates

### Update Frequency
- Progress bar: Updates every 1 second
- Step indicator: Updates when job progress changes by ≥20%
- Queue table: Updates every 1 second
- Stats: Updated when job completes/fails

### Update Sequence
1. Job moves to "processing" status
2. Poll `/status/<job_id>` every 1 second
3. Backend returns `progress` (0-100)
4. UI calculates current step from progress
5. Update progress bar and step text
6. Repeat until job completes

## Code Implementation

### Step Detection Algorithm
```javascript
// Progress value from backend
const progress = 25;  // Example: Trello phase

// Auto-detect step
let step = 'scraping';  // Default

if (progress >= 80) {
    step = 'documents';           // "Creating documents..."
} else if (progress >= 60) {
    step = 'cover_letter';        // "Generating cover letter..."
} else if (progress >= 20) {
    step = 'trello';              // "Logging in Trello..."
} else {
    step = 'scraping';            // "Gathering information..."
}

// Display step label
const label = PROCESSING_STEPS[step].label;
// Result: "Logging in Trello..."
```

### State Management
```javascript
// Global state
let queue = [];           // All jobs
let processing = false;   // Processing flag
let currentJobStep = 'scraping';  // Current step

// Per-job tracking
queue = [
    {
        id: 'job_1234567890_0',
        url: 'https://stepstone.de/...',
        status: 'processing',      // queued, processing, completed, error
        progress: 25,              // 0-100 from backend
        title: 'Loading...',
        company: 'Loading...'
    },
    // ... more jobs
];
```

## Integration with Backend

### Expected Backend Response Format

**During Processing**:
```json
{
    "status": "processing",
    "progress": 45,
    "job_id": "abc123",
    "message": "Processing cover letter..."
}
```

**On Completion**:
```json
{
    "status": "complete",
    "progress": 100,
    "job_id": "abc123",
    "result": {
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "files": {
            "txt": "/output/cover_letters/abc123.txt",
            "docx": "/output/cover_letters/abc123.docx",
            "pdf": "/output/cover_letters/abc123.pdf"
        },
        "trello_card": "https://trello.com/c/abc123xyz"
    }
}
```

**On Error**:
```json
{
    "status": "error",
    "progress": 50,
    "job_id": "abc123",
    "message": "Failed to generate cover letter"
}
```

## Testing Scenarios

### Test 1: Single Job Processing
```
Input: 1 URL
Expected: Progress goes 0% → 100% with all steps shown
Step sequence: Gathering → Trello → Cover Letter → Documents → Complete
```

### Test 2: Multiple Jobs
```
Input: 3 URLs
Expected: 
- Job 1: All steps shown
- Job 1 completes, Job 2 starts
- Progress = 33% (1 of 3 done)
- Job 2: All steps shown
- Job 3: Completes entire pipeline
- Progress = 100% (3 of 3 done)
```

### Test 3: Long Running Job
```
Input: 1 complex URL
Expected:
- Step indicator updates as progress changes
- Progress bar smoothly fills
- Step text updates every ~1 second
- Completes successfully
```

### Test 4: Job Error
```
Input: 1 invalid URL
Expected:
- Starts with "Gathering information..."
- Error occurs during scraping (progress ~10%)
- Status badge changes to "error"
- Next job starts processing
- Error counted in stats
```

## Customization

### Changing Step Labels
Edit `PROCESSING_STEPS` in batch.html:
```javascript
const PROCESSING_STEPS = {
    'scraping': { label: 'Custom Scraping Label...', percent: 0 },
    // ... edit as needed
};
```

### Adjusting Progress Ranges
Edit thresholds in `updateProgressStepIndicator()`:
```javascript
if (processingJob.progress >= 80) {  // Change 80 to different value
    step = 'documents';
} else if (processingJob.progress >= 60) {  // Change 60
    step = 'cover_letter';
} else if (processingJob.progress >= 20) {  // Change 20
    step = 'trello';
}
```

### Adding New Steps
1. Add to `PROCESSING_STEPS` constant
2. Add new condition in step detection
3. Update progress ranges in backend
