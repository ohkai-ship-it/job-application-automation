# Progress Bar Fixes - Issue Resolution

## Issues Fixed

### 1. Progress Step Message Not Displaying

**Problem:** The step indicator was showing "Processing..." instead of specific steps like "Gathering Information", "Creating Trello Card", etc.

**Root Cause:** The `job.message` field was not being updated from the backend response in `checkJobStatus()`.

**Solution:** 
- Added `job.message = data.message || 'Processing...';` to capture the message from backend
- Initialized `message: 'Queued...'` when creating new jobs
- Now the frontend captures and displays the exact step from the backend

**Code Changes (templates/batch.html):**

```javascript
// In checkJobStatus() - Line ~1027
} else {
    job.progress = data.progress || 0;
    job.message = data.message || 'Processing...';  // ← NEW: Capture backend message
    // ... rest of code
}
```

**Result:** Progress step now displays:
- ✅ "Gathering Information" (0-15%)
- ✅ "Creating Trello Card" (20-59%)
- ✅ "Generating Cover Letter with AI" (60-79%)
- ✅ "Creating Word document" (80-89%)
- ✅ "Saving PDF" (90-99%)

---

### 2. Job Counter Not Resetting on New Batch

**Problem:** When starting a new batch of URLs, the job counter showed "Job 5 of 7" instead of resetting to "Job 1 of X" for the new batch.

**Root Cause:** The progress bar was counting ALL jobs in the queue (including jobs from previous batches), not just the current batch being processed.

**Solution:**
- Added `currentBatchId` tracker to mark which batch each job belongs to
- Modified `updateProgressBar()` to filter jobs by current batch
- When a new batch starts, a new `currentBatchId` is created
- Progress counter now only shows current batch jobs

**Code Changes (templates/batch.html):**

**Added batch ID tracking:**
```javascript
// Line ~714
let currentBatchId = null;  // Track the current batch of jobs
```

**Set batch ID when processing starts:**
```javascript
// Line ~857
// Create a new batch ID
currentBatchId = `batch_${Date.now()}`;

// Create new job entries
const newJobs = urls.map((url, index) => ({
    // ... other fields ...
    batchId: currentBatchId,  // ← Mark which batch this belongs to
}));
```

**Filter by batch ID in progress bar:**
```javascript
// Line ~1098
function updateProgressBar() {
    // Only count jobs from the current batch
    const batchJobs = queue.filter(j => j.batchId === currentBatchId);
    const total = batchJobs.length;
    const completed = batchJobs.filter(j => j.status === 'completed').length;
    const processingJob = batchJobs.find(j => j.status === 'processing');
    
    // Show job count (e.g., "Job 1 of 3")
    const currentJobNum = completed + (processingJob ? 1 : 0);
    // ... rest of code ...
}
```

**Result:** Job counter now resets with each new batch:
- ✅ First batch: "Job 1 of 5", "Job 2 of 5", etc.
- ✅ Second batch: Counter resets to "Job 1 of 3" (for new batch)
- ✅ All jobs remain in queue for historical reference
- ✅ Only current batch progress is shown

---

## Data Flow

### Message Display Flow

```
Backend (src/app.py)
  ├─ Updates: processing_status[job_id]['message'] = 'Gathering Information'
  └─ Returns in /status/{jobId} response
         ↓
Frontend (checkJobStatus)
  ├─ Receives: response.message = 'Gathering Information'
  ├─ Updates: job.message = response.message  ← NEW
  └─ Triggers: updateProgressBar()
         ↓
updateProgressStepIndicator()
  ├─ Reads: const backendMessage = processingJob.message
  └─ Displays: document.getElementById('progressStep').textContent = backendMessage
         ↓
User Interface
  └─ Shows: "Gathering Information"
```

### Batch Counter Flow

```
User clicks "Process All URLs"
    ↓
currentBatchId = `batch_${Date.now()}`  ← Create unique batch ID
    ↓
Create newJobs with batchId: currentBatchId
    ↓
User processes batch
    ├─ "Job 1 of 5"
    ├─ "Job 2 of 5"
    └─ "Job 5 of 5" ✓ Complete
    ↓
User adds NEW URLs and clicks "Process All" again
    ↓
currentBatchId = `batch_${Date.now()}`  ← NEW batch ID
    ↓
Create newJobs with NEW batchId
    ↓
Progress bar resets: "Job 1 of 3"  ← Only counts new batch jobs
```

---

## Job Object Structure

Each job now includes:

```javascript
{
    id: 'job_1729686453123_0',
    url: 'https://...',
    status: 'processing',        // queued, processing, completed, error
    title: 'Senior Developer',
    company: 'TechCorp',
    message: 'Gathering Information',  // ← NEW: Comes from backend
    progress: 25,                // 0-100
    batchId: 'batch_1729686453123',    // ← NEW: Groups jobs by batch
    createTrello: true,
    generateDocuments: true,
    generatePdf: false,
    targetLanguage: 'auto'
}
```

---

## Testing

✅ All 109 tests pass
✅ No syntax errors
✅ No breaking changes to existing functionality

---

## User Experience Improvements

### Before
- Progress step showed "Processing..."
- Adding new URLs while one batch running would confuse the counter (e.g., "Job 5 of 7")

### After
- Progress step shows exact processing step: "Gathering Information", "Creating Trello Card", etc.
- Adding new URLs resets the counter for the new batch (e.g., "Job 1 of 3")
- Queue history is preserved (old jobs still visible)
- Clear visual separation between batch cycles

---

## Files Modified

- `templates/batch.html`
  - Line ~714: Added `currentBatchId` state variable
  - Line ~857-880: Added batch ID creation and job initialization with batch ID
  - Line ~1025-1027: Added `job.message` capture from backend
  - Line ~1098-1120: Modified `updateProgressBar()` to filter by batch ID

---

## Next Steps

The progress bar now:
1. ✅ Displays exact processing steps from backend
2. ✅ Resets job counter for each new batch
3. ✅ Maintains full queue history
4. ✅ Clearly shows which batch is currently processing
