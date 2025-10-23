# Progress Steps - Visual Reference

## Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    JOB PROCESSING PIPELINE                       │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─ 0-15%  ┌────────────────────────────────────┐
  │         │ Gathering Information              │
  │         │ - Scraping job posting             │
  │         │ - Extracting job details           │
  │         │ - Finding company info             │
  │         └────────────────────────────────────┘
  │
  ├─ 20-59% ┌────────────────────────────────────┐
  │         │ Creating Trello Card               │
  │         │ - Connecting to Trello             │
  │         │ - Creating card                    │
  │         │ - Setting fields & labels          │
  │         │ - Copying checklists               │
  │         └────────────────────────────────────┘
  │
  ├─ 60-79% ┌────────────────────────────────────┐
  │         │ Generating Cover Letter with AI    │
  │         │ - Loading CV PDFs                  │
  │         │ - Calling OpenAI API               │
  │         │ - Validating word count            │
  │         │ - Saving to file                   │
  │         └────────────────────────────────────┘
  │
  ├─ 80-89% ┌────────────────────────────────────┐
  │         │ Creating Word document             │
  │         │ - Loading template                 │
  │         │ - Inserting cover letter           │
  │         │ - Formatting document              │
  │         │ - Saving DOCX                      │
  │         └────────────────────────────────────┘
  │
  ├─ 90-99% ┌────────────────────────────────────┐
  │         │ Saving PDF                         │
  │         │ - Converting DOCX to PDF           │
  │         │ - Validating PDF                   │
  │         │ - Saving to output folder          │
  │         └────────────────────────────────────┘
  │
  └─ 100%   Complete! ✓
```

## Progress Bar Display

```
┌─────────────────────────────────────────┐
│  Job 1 of 3                             │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 35%
│  Gathering Information                  │
│                                         │
│  TechCorp - Senior Developer            │
│  📍 Berlin, Germany                     │
│  Status: processing                     │
└─────────────────────────────────────────┘
```

## Status Badges

```
┌──────────────┬──────────────────────────────────┐
│  Status      │  Badge Color                     │
├──────────────┼──────────────────────────────────┤
│  processing  │  🔵 Blue (animated)              │
│  completed   │  🟢 Green                        │
│  error       │  🔴 Red                          │
│  cancelled   │  ⚫ Gray with "Cancel" text      │
│  queued      │  ⚪ Gray                         │
└──────────────┴──────────────────────────────────┘
```

## Message Updates

### Frontend → Backend Communication

```
Frontend (batch.html)
  │
  ├─ Process All URLs clicked
  │   └─ POST /process (URL, create_trello, generate_documents, generate_pdf)
  │
  └─ Poll Status (every 1 second)
      └─ GET /status/{jobId}

Backend (app.py)
  │
  ├─ Receive POST /process
  │   └─ Start background thread with job_id
  │
  └─ Process in Background
      ├─ Initialize: message = "Gathering Information"
      ├─ Scrape: Keep polling backend
      ├─ Update: message = "Creating Trello Card"
      ├─ Create card
      ├─ Update: message = "Generating Cover Letter with AI"
      ├─ Generate cover letter
      ├─ Update: message = "Creating Word document"
      ├─ Generate DOCX
      ├─ Update: message = "Saving PDF"
      ├─ Convert to PDF
      └─ Complete: status = 'complete'
```

### Response Format

```javascript
GET /status/{jobId}
↓
{
  "status": "processing",
  "message": "Creating Trello Card",        // ← This is shown to user
  "url": "https://jobs.stepstone.de/...",
  "progress": 45,                           // ← 0-100%
  "job_title": "Senior Developer",
  "company_name": "TechCorp",
  "paused": false
}
```

## Timing

```
ELAPSED TIME    PROGRESS    MESSAGE
─────────────────────────────────────────────────────
0 seconds       0%          Gathering Information
1 second        5%          Gathering Information
2 seconds       10%         Gathering Information
3 seconds       15%         Gathering Information
4 seconds       20%         Creating Trello Card         ← Step changed
5 seconds       30%         Creating Trello Card
...
8 seconds       50%         Creating Trello Card
...
10 seconds      60%         Generating Cover Letter...  ← Step changed
11 seconds      65%         Generating Cover Letter...
...
15 seconds      80%         Creating Word document       ← Step changed
16 seconds      85%         Creating Word document
...
18 seconds      90%         Saving PDF                   ← Step changed
19 seconds      95%         Saving PDF
...
21 seconds      100%        Complete!                    ← Done
```

## How Step Names are Determined

```
┌──────────────────────────────────────────────┐
│ Backend Control (Source of Truth)            │
├──────────────────────────────────────────────┤
│                                              │
│ processing_status[job_id]['message']         │
│          ↓ JSON Response                     │
│ {                                            │
│   "message": "Creating Trello Card"          │
│ }                                            │
│          ↓ Polling                           │
├──────────────────────────────────────────────┤
│ Frontend Display (Consumer)                  │
├──────────────────────────────────────────────┤
│                                              │
│ job.message = "Creating Trello Card"         │
│ processingJob.message (from checkJobStatus)  │
│          ↓ In updateProgressStepIndicator    │
│ document.getElementById('progressStep')      │
│          .textContent = backendMessage       │
│                                              │
│ USER SEES: "Creating Trello Card"            │
└──────────────────────────────────────────────┘
```

## Code Flow Diagram

```
checkJobStatus()
  │
  ├─ Fetch /status/{jobId}
  │   └─ Response includes: message, progress, status
  │
  ├─ Update job object
  │   ├─ job.message = response.message
  │   ├─ job.progress = response.progress
  │   └─ job.status = response.status
  │
  ├─ updateQueueDisplay()
  │   └─ Show job title, company, status
  │
  └─ updateProgressBar()
      └─ updateProgressStepIndicator()
          └─ const backendMessage = processingJob.message
             document.getElementById('progressStep').textContent = backendMessage
             
             USER SEES: "Creating Trello Card"
```

## Integration Points

| Component | Step Name | Action |
|-----------|-----------|--------|
| Scraper | "Gathering Information" | `scrape_job_posting()` |
| Trello API | "Creating Trello Card" | `create_card_from_job_data()` |
| OpenAI | "Generating Cover Letter with AI" | `generate_cover_letter()` |
| Word Generator | "Creating Word document" | `generate_from_template()` |
| PDF Converter | "Saving PDF" | `convert_to_pdf()` or docx2pdf |
