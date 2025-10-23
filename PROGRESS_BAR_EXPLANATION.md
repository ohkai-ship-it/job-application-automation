# Progress Bar Update Flow - Complete Explanation

## 📊 High-Level Flow

```
User clicks "Process All"
        ↓
processAllJobs() creates job queue
        ↓
processNextJob() processes first queued job
        ↓
(Continuously polls backend via checkJobStatus)
        ↓
updateProgressBar() updates display every 1 second
        ↓
User sees live progress update
```

---

## 🔄 Detailed Step-by-Step Process

### 1️⃣ **Initial Setup** (`processAllJobs()` - Line 801)

When you click "Process All URLs":

```javascript
// Create job objects from URLs
const newJobs = urls.map((url, index) => ({
    id: `job_${Date.now()}_${index}`,
    url: url.trim(),
    status: 'queued',           // ← Initially queued
    title: 'Loading...',
    company: 'Loading...',
    progress: 0,                // ← 0% progress
    createTrello: true,
    generateDocuments: true,
    generatePdf: true,
    targetLanguage: 'auto'
}));

queue = queue.concat(newJobs);
processNextJob();              // ← Start processing
```

**Result:** Queue has jobs with `status='queued'` and `progress=0`

---

### 2️⃣ **Processing a Job** (`processNextJob()` - Line 898)

```javascript
async function processNextJob() {
    const job = queue.find(j => j.status === 'queued');
    
    if (!job) {
        // All jobs done
        return;
    }
    
    job.status = 'processing';  // ← Mark as processing
    job.jobId = response.jobId; // ← Store backend job ID
    
    // Immediately poll for status
    checkJobStatus(job);
}
```

**Result:** First queued job becomes `status='processing'`, polling starts

---

### 3️⃣ **Polling Backend** (`checkJobStatus()` - Line 987)

Every 1 second, frontend asks backend: "What's the status of job X?"

```javascript
async function checkJobStatus(job) {
    const response = await fetch(`/status/${job.jobId}`);
    const data = await response.json();
    
    console.log(`[${job.id}] Status:`, data); // Shows progress updates
    
    if (data.status === 'complete') {
        // Job finished
        job.status = 'completed';
        job.progress = 100;       // ← Set to 100%
        results.completed++;
        processNextJob();          // ← Process next job
        
    } else if (data.status === 'error') {
        // Job failed
        job.status = 'error';
        results.errors++;
        processNextJob();          // ← Skip to next job
        
    } else {
        // Job still processing
        job.progress = data.progress || 0;  // ← Update progress %
        
        // Update title/company as soon as available
        if (data.job_title && job.title === 'Loading...') {
            job.title = data.job_title;     // ← Show job title
        }
        if (data.company_name && job.company === 'Loading...') {
            job.company = data.company_name; // ← Show company
        }
        
        setTimeout(() => checkJobStatus(job), 1000);  // ← Poll again in 1s
    }
}
```

**Key Updates from Backend:**
- `data.progress`: Current progress % (0-100)
- `data.job_title`: Job title scraped from posting
- `data.company_name`: Company name scraped
- `data.status`: 'processing', 'complete', or 'error'

---

### 4️⃣ **Updating Progress Bar** (`updateProgressBar()` - Line 1092)

Every time `checkJobStatus()` gets new data, it calls `updateProgressBar()`:

```javascript
function updateProgressBar() {
    // Calculate statistics
    const total = queue.length;                              // Total jobs
    const completed = queue.filter(j => j.status === 'completed').length;  // Done
    const processingJob = queue.find(j => j.status === 'processing');      // Current
    
    // Show: "Job 1 of 3", "Job 2 of 3", etc.
    const currentJobNum = completed + (processingJob ? 1 : 0);
    document.getElementById('jobsProcessing').textContent = currentJobNum;
    document.getElementById('jobsTotal').textContent = total;
    
    // Progress bar = CURRENT JOB'S progress percentage (0-100%)
    const jobProgress = processingJob ? (processingJob.progress || 0) : 100;
    document.getElementById('progressPercent').textContent = jobProgress;
    document.getElementById('progressBar').style.width = jobProgress + '%';
    
    // Update step indicator (scraping → trello → documents → pdf)
    updateProgressStepIndicator();
}
```

**What it displays:**
- `jobsProcessing`: Current job number (e.g., "1")
- `jobsTotal`: Total jobs (e.g., "3")
- `progressPercent`: Current job's progress (e.g., "45")
- `progressBar.width`: Visual bar width (e.g., "45%")

---

### 5️⃣ **Step Indicator** (`updateProgressStepIndicator()` - Line 1108)

Shows which step the current job is at:

```javascript
function updateProgressStepIndicator() {
    const processingJob = queue.find(j => j.status === 'processing');
    
    if (!processingJob) {
        document.getElementById('progressStep').textContent = 'Ready to process...';
        return;
    }
    
    // Map progress % to processing step
    let step = 'scraping';          // 0-20%
    if (processingJob.progress >= 80) {
        step = 'documents';         // 80%+
    } else if (processingJob.progress >= 60) {
        step = 'generating pdf';    // 60-80%
    } else if (processingJob.progress >= 40) {
        step = 'trello card';       // 40-60%
    }
    
    document.getElementById('progressStep').textContent = `Currently ${step}...`;
}
```

**Progress Stages:**
- 0-20%: "Currently scraping..."
- 40-60%: "Currently creating trello card..."
- 60-80%: "Currently generating pdf..."
- 80%+: "Currently generating documents..."
- 100%: Process moves to next job

---

## 🔁 Complete Polling Cycle (Repeats Every Second)

```
┌─────────────────────────────────────────────────────────┐
│  Every 1 second (while processing):                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. checkJobStatus(job)                                │
│     └─> Fetch `/status/{jobId}` from backend          │
│                                                         │
│  2. Backend returns:                                    │
│     {                                                   │
│       status: 'processing',                             │
│       progress: 45,           ← % complete              │
│       job_title: '...',       ← Data from scraping      │
│       company_name: '...'     ← Data from scraping      │
│     }                                                   │
│                                                         │
│  3. Update job object:                                 │
│     job.progress = 45                                   │
│     job.title = 'Senior Developer'                     │
│     job.company = 'TechCorp'                           │
│                                                         │
│  4. updateQueueDisplay()                               │
│     └─> Refresh queue table with new data              │
│                                                         │
│  5. updateProgressBar()                                │
│     └─> Update:                                        │
│         - Progress bar width (45%)                     │
│         - Job number (e.g., "1 of 3")                 │
│         - Step indicator ("Currently trello card...") │
│                                                         │
│  6. Schedule next poll:                                │
│     setTimeout(() => checkJobStatus(job), 1000ms)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📈 Example Timeline

```
TIME    JOB         STATUS      PROGRESS    STEP
────────────────────────────────────────────────────────
0s      Job 1       processing  0%          scraping
1s      Job 1       processing  15%         scraping
2s      Job 1       processing  25%         scraping (title/company appear)
3s      Job 1       processing  45%         creating trello
4s      Job 1       processing  65%         generating pdf
5s      Job 1       processing  85%         generating documents
6s      Job 1       processing  95%         generating documents
7s      Job 1       processing  100%        ✓ completed
        ↓
        Job 2       processing  0%          scraping
8s      Job 2       processing  20%         scraping
9s      Job 2       processing  40%         creating trello
...
```

---

## 🔗 Data Flow Diagram

```
                    Backend (Flask)
                    ═══════════════
                    /status/{jobId}
                           ↑
                           │ (Polls every 1s)
                           │
                    Frontend (JavaScript)
                    ══════════════════════
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    checkJobStatus()   updateQueueDisplay() updateProgressBar()
        │                  │                  │
        │ Gets            │ Refreshes       │ Updates
        │ progress        │ job table       │ bar %
        │ title           │ status badges   │ step text
        │ company         │ action links    │ job count
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    HTML Display
                    (User sees live updates)
```

---

## ⚙️ Key Mechanisms

### 1. **Polling Frequency**
- Normal: Every 1 second (`setTimeout(..., 1000)`)
- On error: Every 2 seconds (`setTimeout(..., 2000)`)
- Stops when: Job status is 'complete' or 'error'

### 2. **Progress Calculation**
- **Per-Job**: Backend calculates and returns progress % for current step
- **Overall**: Frontend shows "Job X of Y" (not cumulative %)
- **Visual**: Progress bar only shows *current* job's progress, not all jobs

### 3. **Data Updates**
- Job title/company update **as soon as scraping completes**
- No need to wait for full job completion
- "Loading..." placeholder replaced with real data mid-processing

### 4. **Queue Persistence**
- Completed jobs stay in queue for review
- Users can see full processing history
- Cancelled jobs show red "Cancelled" badge

---

## 🎯 Summary

The progress bar works by:

1. **Backend processes job** and updates internal status/progress
2. **Frontend polls backend** every 1 second asking "What's the status?"
3. **Backend responds** with current progress %, current step, scraped data
4. **Frontend updates UI**: Progress bar, job title, company, step indicator
5. **Repeat until** job completes or errors
6. **Move to next job** and repeat from step 2

This creates a **real-time feedback loop** showing users exactly what's happening without page refreshes!
