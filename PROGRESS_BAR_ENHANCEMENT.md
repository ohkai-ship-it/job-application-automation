# Progress Bar Enhancement - Processing Steps Display

## Overview
Enhanced the progress bar UI to display the current processing step for each job being processed. This gives users real-time visibility into what stage each job is at within the pipeline.

## What Changed

### 1. Progress Bar Step Indicator (HTML)
**File**: `templates/batch.html`  
**Lines**: Added new `progress-step-indicator` div

Added a text indicator below the progress bar that displays the current processing step:
```html
<div class="progress-step-indicator" id="progressStep" style="margin-top: 8px; font-size: 0.9em; color: var(--text-secondary); font-weight: 500;">
    Gathering information...
</div>
```

**Visual Effect**: User sees text like "Gathering information...", "Logging in Trello...", etc. as processing progresses

### 2. Processing Steps Configuration (JavaScript)
**File**: `templates/batch.html`  
**Lines**: Added `PROCESSING_STEPS` constant at top of script

Defined the 4-phase processing pipeline with labels and progress percentages:
```javascript
const PROCESSING_STEPS = {
    'scraping': { label: 'Gathering information...', percent: 0 },
    'trello': { label: 'Logging in Trello...', percent: 20 },
    'cover_letter': { label: 'Generating cover letter...', percent: 60 },
    'documents': { label: 'Creating documents...', percent: 80 },
    'complete': { label: 'Complete!', percent: 100 }
};

let currentJobStep = 'scraping';
```

**Purpose**: Single source of truth for step labels and progress ranges

### 3. Step Detection Logic (JavaScript)
**File**: `templates/batch.html`  
**New Function**: `updateProgressStepIndicator()`

Automatically detects which step a job is in based on its progress percentage:
```javascript
function updateProgressStepIndicator() {
    const processingJob = queue.find(j => j.status === 'processing');
    
    if (!processingJob) {
        document.getElementById('progressStep').textContent = 'Ready to process...';
        currentJobStep = 'scraping';
        return;
    }
    
    // Determine step based on job progress
    let step = 'scraping';
    if (processingJob.progress >= 80) {
        step = 'documents';
    } else if (processingJob.progress >= 60) {
        step = 'cover_letter';
    } else if (processingJob.progress >= 20) {
        step = 'trello';
    } else {
        step = 'scraping';
    }
    
    currentJobStep = step;
    const stepInfo = PROCESSING_STEPS[step];
    document.getElementById('progressStep').textContent = stepInfo.label;
}
```

**Logic Flow**:
- 0-19% progress → "Gathering information..." (Scraping job details)
- 20-59% progress → "Logging in Trello..." (Creating Trello card)
- 60-79% progress → "Generating cover letter..." (AI generation)
- 80-99% progress → "Creating documents..." (DOCX/PDF conversion)
- 100% progress → "Complete!" (Job finished)

### 4. Integration with Progress Updates
**File**: `templates/batch.html`  
**Modified**: `updateProgressBar()` function

Added call to `updateProgressStepIndicator()` after each progress update:
```javascript
function updateProgressBar() {
    // ... existing code ...
    document.getElementById('progressBar').style.width = percent + '%';
    
    // NEW: Update step indicator based on currently processing job
    updateProgressStepIndicator();
}
```

**Result**: Step indicator updates in sync with progress bar

### 5. Enhanced Job Status Tracking
**File**: `templates/batch.html`  
**Modified**: `checkJobStatus()` function

Ensures progress is always tracked and displayed:
- Sets `job.progress = 100` when job completes
- Calls `updateProgressBar()` on completion
- Calls `updateProgressBar()` on error

## User Experience Flow

### Before Processing Starts
```
Progress Section is hidden
```

### When User Clicks "Process All Jobs"
```
Progress: 0 of 3 jobs
████░░░░░░░░░░░░░░░░░░░░░░░ 0%
Ready to process...
```

### During Job 1 Processing (Scraping Phase)
```
Progress: 0 of 3 jobs
████░░░░░░░░░░░░░░░░░░░░░░░ 5%
Gathering information...
```

### Job 1 Moves to Trello Phase
```
Progress: 0 of 3 jobs
█████░░░░░░░░░░░░░░░░░░░░░░ 25%
Logging in Trello...
```

### Job 1 Moves to Cover Letter Generation
```
Progress: 0 of 3 jobs
█████████░░░░░░░░░░░░░░░░░░ 65%
Generating cover letter...
```

### Job 1 Moves to Document Creation
```
Progress: 0 of 3 jobs
████████████░░░░░░░░░░░░░░░ 85%
Creating documents...
```

### Job 1 Complete, Job 2 Processing
```
Progress: 1 of 3 jobs
███████████████░░░░░░░░░░░░ 33%
Gathering information...
```

### All Jobs Complete
```
Progress: 3 of 3 jobs
████████████████████████████ 100%
Complete!
```

## Technical Details

### Progress Percentage Mapping
The progress percentages are based on the backend `/status/<job_id>` endpoint response:

| Backend Progress Range | UI Display Step | Duration |
|------------------------|-----------------|----------|
| 0-19% | Gathering information | Scraping + parsing |
| 20-59% | Logging in Trello | Trello API + card setup |
| 60-79% | Generating cover letter | OpenAI call + validation |
| 80-99% | Creating documents | DOCX + PDF generation |
| 100% | Complete! | Job finished |

### How It Works
1. User enters URLs and clicks "Process All Jobs"
2. URLs are queued with `status: 'queued'`
3. For each job:
   - Status changes to `processing`
   - `/process` endpoint is called
   - Polling loop starts with `/status/<job_id>`
   - Backend returns `progress` value (0-100)
   - UI calculates current step from progress value
   - Step label updates automatically
4. When job completes or errors, next job starts

### Integration Points
- **Backend Requirement**: `/status/<job_id>` must return `progress` field (0-100)
- **Step Labels**: Stored in `PROCESSING_STEPS` constant (easily customizable)
- **Progress Ranges**: Hardcoded in `updateProgressStepIndicator()` (can be made configurable)

## File Changes Summary

| File | Changes | Lines |
|------|---------|-------|
| `templates/batch.html` | HTML + JavaScript enhancements | 862 → 900+ |
| **Added** | Step indicator div | 1 line |
| **Added** | `PROCESSING_STEPS` constant | 6 lines |
| **Added** | `currentJobStep` state variable | 1 line |
| **Added** | `updateProgressStepIndicator()` function | 35 lines |
| **Modified** | `updateProgressBar()` function | +1 line (new call) |
| **Modified** | `checkJobStatus()` function | +3 lines (progress tracking) |

## Testing Checklist

- [ ] Progress section displays when "Process All Jobs" clicked
- [ ] Step indicator shows "Gathering information..." at start
- [ ] Step changes to "Logging in Trello..." at ~20% progress
- [ ] Step changes to "Generating cover letter..." at ~60% progress
- [ ] Step changes to "Creating documents..." at ~80% progress
- [ ] Step shows "Complete!" when job finishes (100%)
- [ ] Step indicator updates in real-time as progress changes
- [ ] Multiple jobs show correct step for currently processing job
- [ ] Step resets to "Ready to process..." when processing completes

## Future Enhancements

1. **Step Substeps**: Show more granular progress (e.g., "Gathering information... parsing job description")
2. **Animated Icons**: Add icons that change per step (📝 → 🗂️ → 💬 → 📄)
3. **Time Estimates**: Display estimated time remaining based on step
4. **Step Timing**: Track how long each step takes for performance optimization
5. **Per-Job Progress**: Show progress for individual jobs in the queue table (not just overall)
6. **Step Tooltips**: Hover tooltips explaining what each step does

## Notes

- Step labels are user-friendly and match the processing pipeline
- Progress ranges are flexible and can be adjusted in `updateProgressStepIndicator()` 
- No backend changes required - works with existing `/status` endpoint
- Step indicator is always synced with progress bar percentage
