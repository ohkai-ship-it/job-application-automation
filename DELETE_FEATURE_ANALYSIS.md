# Delete Feature - Backend Analysis

## Overview
To implement a "Delete" column/action in the queue table, we need to:
1. Delete the database record (if exists)
2. Delete generated files (DOCX, PDF)
3. Delete the Trello card (if exists)
4. Update the UI

---

## Backend Functions/Methods Needed

### 1. **Trello Card Deletion**
**File:** `src/trello_connect.py`
**Current Methods:** None exist - need to create
**Reference Implementation:** `delete_toll_collect_card.py` & `delete_cards_from_list.py`

**Trello API Method:**
```python
DELETE /1/cards/{card_id}
```

**Implementation Pattern (from helper scripts):**
```python
import requests
from src.utils.trello import TRELLO_API_BASE, get_auth_params

def delete_trello_card(card_id: str) -> bool:
    """Delete a Trello card by ID"""
    auth = get_auth_params()
    delete_url = f"{TRELLO_API_BASE}/cards/{card_id}"
    resp = requests.delete(delete_url, params=auth, timeout=30)
    return resp.status_code == 200
```

**Where to add:** `TrelloConnect` class in `src/trello_connect.py`

---

### 2. **File Deletion**
**Files to Delete:**
- DOCX cover letter: `output/cover_letters/Anschreiben - Kai Voges - YYYY-MM-DD - Company.docx`
- PDF cover letter: Same path with `.pdf` extension
- JSON (optional): `data/scraped_job_*.json`

**Implementation:**
```python
import os
from pathlib import Path

def delete_generated_files(job_data: dict, docx_file: str = None, pdf_file: str = None) -> Dict[str, bool]:
    """Delete generated files for a job"""
    results = {'docx': False, 'pdf': False}
    
    # Delete DOCX if provided
    if docx_file and os.path.exists(docx_file):
        try:
            os.remove(docx_file)
            results['docx'] = True
        except Exception as e:
            logger.error(f"Failed to delete DOCX: {e}")
    
    # Delete PDF if provided
    if pdf_file and os.path.exists(pdf_file):
        try:
            os.remove(pdf_file)
            results['pdf'] = True
        except Exception as e:
            logger.error(f"Failed to delete PDF: {e}")
    
    return results
```

**Where to add:** Create new file `src/file_manager.py` or add to `src/main.py`

---

### 3. **Database Record Deletion**
**File:** `src/database.py` class `ApplicationDB`
**Current Methods:** `save_processed_job()`, `get_job_by_id()`, etc.
**Need to create:** `delete_job_by_url()` or `delete_job_by_id()`

**Implementation Pattern:**
```python
def delete_job(self, job_id: str = None, source_url: str = None) -> bool:
    """
    Delete a job record from the database.
    
    Args:
        job_id: Job ID (primary lookup)
        source_url: Source URL (fallback lookup)
    
    Returns:
        True if deleted, False if not found
    """
    with self._get_connection() as conn:
        cursor = conn.cursor()
        
        if job_id:
            cursor.execute("DELETE FROM processed_jobs WHERE job_id = ?", (job_id,))
        elif source_url:
            cursor.execute("DELETE FROM processed_jobs WHERE source_url = ?", (source_url,))
        else:
            return False
        
        return cursor.rowcount > 0
```

**Where to add:** `ApplicationDB` class in `src/database.py`

---

### 4. **Flask Endpoint for Deletion**
**File:** `src/app.py`
**Current Routes:** `/process`, `/status/<job_id>`, `/retry-cover-letter/<job_id>`
**Need to create:** `/delete/<job_id>` (POST)

**Implementation Pattern:**
```python
@app.route('/delete/<job_id>', methods=['POST'])
def delete_job(job_id: str):
    """Delete a job, its files, and Trello card"""
    try:
        # Get job info from processing_status (if still in queue)
        job_info = processing_status.get(job_id, {})
        
        # Get result data if job already completed
        result = job_info.get('result', {})
        
        # 1. Delete Trello card
        trello_card_id = result.get('trello_card_id')
        trello_deleted = False
        if trello_card_id:
            trello = TrelloConnect()
            trello_deleted = trello.delete_trello_card(trello_card_id)
        
        # 2. Delete generated files
        files_deleted = delete_generated_files(
            docx_file=result.get('files', {}).get('docx'),
            pdf_file=result.get('files', {}).get('pdf')
        )
        
        # 3. Delete database record
        db = ApplicationDB()
        db.delete_job(job_id=job_id)
        
        # 4. Clean up from processing_status
        if job_id in processing_status:
            del processing_status[job_id]
        
        return jsonify({
            'success': True,
            'deleted': {
                'trello_card': trello_deleted,
                'files': files_deleted,
                'database': True
            }
        })
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Where to add:** New route in `src/app.py` after `/retry-cover-letter/<job_id>` route

---

### 5. **Frontend JavaScript Function**
**File:** `templates/batch.html`
**Need to add:** Delete button + confirmation dialog + AJAX call

**Implementation Pattern:**
```javascript
function deleteJob(jobId) {
    const job = queue.find(j => j.jobId === jobId);
    if (!job) {
        alert('Job not found');
        return;
    }
    
    // Confirmation
    const confirmMsg = `Delete this job?\n\n${job.company}\n${job.title}\n\nThis will remove:\n- Database record\n- Generated files\n- Trello card`;
    if (!confirm(confirmMsg)) return;
    
    fetch(`/delete/${jobId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            // Remove from queue
            queue = queue.filter(j => j.jobId !== jobId);
            updateQueueDisplay();
            updateStats();
            alert('Job deleted successfully');
        } else {
            alert('Error: ' + (data.error || 'Failed to delete'));
        }
    })
    .catch(err => {
        console.error('Delete failed:', err);
        alert('Error: ' + err.message);
    });
}
```

---

## Data Flow for Delete Operation

```
User clicks "Delete" button on row
    ↓
JavaScript confirmation dialog
    ↓
POST /delete/{job_id}
    ├─ Get job_id from processing_status or database
    ├─ Delete Trello card via API (if exists)
    ├─ Delete DOCX file (if exists)
    ├─ Delete PDF file (if exists)
    ├─ Delete database record
    └─ Remove from processing_status
    ↓
Return success/failure JSON
    ↓
JavaScript updates UI:
    ├─ Remove row from table
    ├─ Update job counter
    └─ Show success message
```

---

## Data Structures to Store

### In `processing_status[job_id]`
Current structure needs to include:
```python
{
    'job_id': 'job_20251023_130144',
    'url': 'https://stepstone.de/...',
    'status': 'completed',
    'result': {
        'company': 'Patrick Reichelt',
        'title': 'Kfz-Mechatroniker',
        'location': 'Berlin',
        'trello_card_id': '68fa028ff8fc4080ad84f4ee',  # ← ADD THIS
        'trello_card': 'https://trello.com/c/68fa028ff8fc4080ad84f4ee',
        'files': {
            'docx': 'output/cover_letters/Anschreiben - Kai Voges - 2025-10-23 - Patrick Reichelt.docx',
            'pdf': 'output/cover_letters/Anschreiben - Kai Voges - 2025-10-23 - Patrick Reichelt.pdf',
            'is_duplicate': False
        }
    }
}
```

### Key Storage Points:
1. **Trello Card ID:** Currently stored as `result.get('trello_card')` but we need the card ID separately
2. **File Paths:** Already stored in `result['files']`
3. **Job ID:** Already stored in `processing_status[job_id]`

---

## Database Query for Delete

```sql
DELETE FROM processed_jobs WHERE job_id = ?;
```

Returns `rowcount = 1` if successful, `0` if not found.

---

## Summary of Changes Needed

| Component | Action | File |
|-----------|--------|------|
| **Backend - Trello** | Add `delete_trello_card()` method | `src/trello_connect.py` |
| **Backend - Files** | Add `delete_generated_files()` function | `src/file_manager.py` (new) |
| **Backend - Database** | Add `delete_job()` method | `src/database.py` |
| **Backend - Flask** | Add `/delete/<job_id>` endpoint | `src/app.py` |
| **Frontend - JS** | Add `deleteJob()` function | `templates/batch.html` |
| **Frontend - HTML** | Add Delete column header | `templates/batch.html` |
| **Frontend - Table** | Add Delete button to each row | `templates/batch.html` |

---

## Implementation Priority

1. **Phase 1 (Required):**
   - Add `delete_trello_card()` to TrelloConnect
   - Add `delete_job()` to ApplicationDB
   - Add `/delete/<job_id>` endpoint
   - Add Delete button UI and `deleteJob()` JS function

2. **Phase 2 (Optional):**
   - Create `file_manager.py` for centralized file ops
   - Store `trello_card_id` separately in `processing_status`
   - Add soft-delete (archive instead of hard-delete)

3. **Phase 3 (Future):**
   - Add undo/recovery feature
   - Add bulk delete
   - Add delete history/audit log
