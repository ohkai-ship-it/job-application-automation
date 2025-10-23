# Delete Feature - Quick Summary

## What We Need (Backend Functions)

### 1. **TrelloConnect.delete_trello_card(card_id: str) → bool**
- Location: `src/trello_connect.py`
- Uses: Trello REST API `DELETE /1/cards/{card_id}`
- Returns: True if successful, False otherwise

### 2. **ApplicationDB.delete_job(job_id: str) → bool**
- Location: `src/database.py`
- Uses: SQLite `DELETE FROM processed_jobs WHERE job_id = ?`
- Returns: True if found and deleted, False if not found

### 3. **delete_generated_files(docx_file: str, pdf_file: str) → Dict**
- Location: New `src/file_manager.py` OR add to `src/main.py`
- Uses: Python's `os.remove()` for file deletion
- Returns: `{'docx': bool, 'pdf': bool}` showing what was deleted

### 4. **Flask Route: /delete/<job_id> (POST)**
- Location: `src/app.py`
- Orchestrates: Calls Trello delete → file delete → DB delete
- Returns: JSON `{'success': bool, 'deleted': {...}}`

### 5. **Frontend: deleteJob(jobId) JavaScript function**
- Location: `templates/batch.html`
- Shows: Confirmation dialog with job details
- Calls: POST /delete/{job_id}
- Updates: Removes row from queue table

---

## Data Already Available

✅ **Trello Card URL:** `result.get('trello_card')` → format: `https://trello.com/c/{CARD_ID}`
✅ **Generated Files:** `result['files']['docx']`, `result['files']['pdf']`
✅ **Job ID:** `processing_status[job_id]`
✅ **Database Record:** Can query by job_id or URL

---

## Reference Code Patterns

### Delete Trello Card (Pattern from helper scripts)
```python
import requests
from src.utils.trello import TRELLO_API_BASE, get_auth_params

resp = requests.delete(
    f"{TRELLO_API_BASE}/cards/{card_id}",
    params=get_auth_params(),
    timeout=30
)
success = resp.status_code == 200
```

### Delete Files (OS module)
```python
import os
os.remove(file_path)  # Raises exception if file not found
```

### Delete DB Record (SQLite)
```python
cursor.execute("DELETE FROM processed_jobs WHERE job_id = ?", (job_id,))
success = cursor.rowcount > 0  # Returns 1 if deleted, 0 if not found
```

---

## Implementation Checklist

- [ ] **Backend Phase:**
  - [ ] Add `delete_trello_card()` to TrelloConnect class
  - [ ] Add `delete_job()` to ApplicationDB class
  - [ ] Add `/delete/<job_id>` POST endpoint in app.py
  - [ ] Extract card ID from trello_card URL (parse or store separately)

- [ ] **Frontend Phase:**
  - [ ] Add Delete column header in table
  - [ ] Add Delete button to HTML row template
  - [ ] Add `deleteJob()` JavaScript function
  - [ ] Add confirmation dialog with job details
  - [ ] Update queue display after deletion

- [ ] **Testing:**
  - [ ] Test Trello card deletion
  - [ ] Test file deletion (DOCX/PDF)
  - [ ] Test database record deletion
  - [ ] Test UI update after deletion
  - [ ] Run all 109 tests to verify no regressions

---

## Next Steps
Ready to implement! Which phase should we start with?
1. **Backend functions first** (Trello, Database, Files)
2. **Flask endpoint** (orchestration)
3. **Frontend UI & button** (user interaction)
