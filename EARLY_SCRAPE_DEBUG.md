# Early Scrape Debugging Guide

## Issue Identified

The job_title and company_name are being updated at the END of processing, not at the beginning.

## What Changed in This Fix

### 1. Simplified Frontend Logic
**File**: `templates/batch.html` (Lines 823-831)

**Before** (complex logic with multiple conditions):
```javascript
if (data.job_title && !job.title.startsWith('Loading') && job.title !== 'Unknown') {
    job.title = data.job_title;
} else if (data.job_title && job.title === 'Loading...') {
    job.title = data.job_title;
}
```

**After** (simple and direct):
```javascript
if (data.job_title && job.title === 'Loading...') {
    job.title = data.job_title;
}
if (data.company_name && job.company === 'Loading...') {
    job.company = data.company_name;
}
```

### 2. Enhanced Backend Logging
**File**: `src/app.py` (Lines 155-189)

Added detailed logging at each step:
- `[job_id] Starting early scrape...`
- `[job_id] Detected source: {source}`
- `[job_id] Early scrape returned data: True/False`
- `[job_id] ✓ Early extraction: {company} - {title}`
- `[job_id] Status now: {status dict}`

### 3. Added Debug Logging in Frontend
**File**: `templates/batch.html` (Line 809)

Added `console.log` to see what status is being returned:
```javascript
console.log(`[${job.id}] Status:`, data); // DEBUG
```

## How to Test & Debug

### Step 1: Open Browser Console
1. Open http://localhost:5000/batch
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Keep it open while processing

### Step 2: Process a Job
1. Enter a Stepstone or LinkedIn URL
2. Click **Process**
3. Watch the browser console for messages

### Step 3: Look for Debug Output

**Expected console output:**
```
[job_1730899200000_0] Status: {
  status: "processing"
  message: "Gathering information..."
  progress: 0
  job_title: ""
  company_name: ""
  url: "https://..."
}

[job_1730899200000_0] Status: {
  status: "processing"
  message: "Gathering information..."
  progress: 19
  job_title: "Senior Developer"      ← Should appear here!
  company_name: "Tech Corp"          ← Should appear here!
  url: "https://..."
}
```

### Step 4: Check Server Logs

Run Flask and watch the terminal:
```
python .\src\app.py
```

**Expected server output:**
```
[job_20251019_125302] Starting background processing for: https://...
[job_20251019_125302] Starting early scrape...
[job_20251019_125302] Detected source: stepstone
[job_20251019_125302] Early scrape returned data: True
[job_20251019_125302] ✓ Early extraction: Tech Corp - Senior Developer
[job_20251019_125302] Status now: {'status': 'processing', 'message': 'Gathering information...', 'progress': 0, 'job_title': 'Senior Developer', 'company_name': 'Tech Corp', 'url': '...'}
```

## Debugging Checklist

- [ ] **Frontend console shows job_title and company_name in status** (Step 3)
- [ ] **Server logs show "✓ Early extraction"** message (Step 4)
- [ ] **Queue table updates title/company within 1-2 seconds**
- [ ] **Works for both Stepstone AND LinkedIn URLs**
- [ ] **Progress bar still shows all 4 phases**

## If It's Still Not Working

### Check 1: Is the early scrape running?
Look for `[job_id] Starting early scrape...` in server logs.
- If NOT there: Background thread might not be starting
- If there: Continue to Check 2

### Check 2: Is the scraper returning data?
Look for `Early scrape returned data: True` or `False` in server logs.
- If `False`: Scraper might be failing silently
- If `True`: Continue to Check 3

### Check 3: Is the status being updated?
Look for `✓ Early extraction:` in server logs.
- If NOT there: Exception might be caught silently
- If there: Check frontend logic in Check 4

### Check 4: Is the frontend receiving the data?
Check browser console:
- Does `data.job_title` exist in the first status check? (1-2 seconds in)
- Is it empty string `""` or actual value like `"Senior Developer"`?

### Check 5: Browser cache issue?
Hard refresh the page: **Ctrl+Shift+R** (Windows)
- Browser might be caching old JavaScript

### Check 6: Flask restart needed?
Stop Flask (Ctrl+C) and restart:
```powershell
python .\src\app.py
```

## Key Files to Check

If debugging further:

1. **Backend scraping**: `src/scraper.py` (Stepstone) and `src/linkedin_scraper.py` (LinkedIn)
   - Check that `job_title` and `company_name` keys are being set

2. **Frontend status checking**: `templates/batch.html` (lines 798-830)
   - Check that fields are being read correctly from `data` object

3. **Status endpoint**: `src/app.py` (lines 276-282)
   - Check that `/status/<job_id>` returns correct data

## Next Steps if Issue Persists

1. Run a single job and monitor logs closely
2. Check that scraper functions are being imported correctly
3. Verify early scrape isn't throwing an exception
4. Check if `processing_status[job_id]` is being updated properly
5. Verify frontend polling is receiving the correct JSON structure

---

## Status

This debug guide helps identify where the early scrape data is being lost:
- ✅ Frontend logic simplified
- ✅ Backend logging enhanced
- ✅ Console debugging enabled

Now test and check the console/logs to see where the data is disappearing!

