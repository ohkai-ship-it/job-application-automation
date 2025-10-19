# Word Link & Down Arrow - Implementation & Debugging

## What's Currently Happening

### Frontend (batch.html)

```html
<a href="/download/${job.result.files.docx}" class="action-link download">Word</a>
```

With CSS styling:
```css
.action-link.download::before {
    content: '⬇ ';  /* Down arrow */
}
```

### Result
- Down arrow (⬇) appears before the word "Word"
- When clicked, attempts to download the file at `/download/<path>`

---

## The Problem: URL Encoding Issue

### Current Flow

1. **Backend stores file path as:**
   ```
   output/cover_letters/Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx
   ```

2. **Frontend renders link as:**
   ```html
   <a href="/download/output/cover_letters/Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx">
   ```

3. **Browser interprets this as:**
   ```
   /download/output/cover_letters/Anschreiben%20-%20Kai%20Voges%20-%202025-10-19%20-%20Max%20B%C3%B6gl%20Wind%20AG.docx
   ```

4. **Backend tries to find file at:**
   ```
   OUTPUT_DIR / "output/cover_letters/Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx"
   ```

### The Issue

The frontend is sending the full relative path `output/cover_letters/filename.docx`, but the backend is appending it to `OUTPUT_DIR`:

```python
filepath = OUTPUT_DIR / filename
# Results in: OUTPUT_DIR/output/cover_letters/filename.docx
# But file is at: OUTPUT_DIR/cover_letters/filename.docx
# Directory mismatch! ❌
```

---

## Solution: Fix the File Path

### Option 1: Backend Fix (RECOMMENDED)

The backend should receive just the filename, not the full path.

**File:** `src/app.py`

**Current code:**
```python
@app.route('/download/<path:filename>')
def download(filename: str) -> Response:
    """Download generated file"""
    try:
        if filename.startswith('scraped_job_'):
            filepath = DATA_DIR / filename
        else:
            filepath = OUTPUT_DIR / filename
        return send_file(str(filepath), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
```

**Problem:** The backend expects just filename, but frontend sends full path like `output/cover_letters/filename.docx`

**Fix:** Extract just the filename:

```python
@app.route('/download/<path:filename>')
def download(filename: str) -> Response:
    """Download generated file"""
    try:
        # Extract just the filename from the path
        # Example: "output/cover_letters/file.docx" → "file.docx"
        import os
        just_filename = os.path.basename(filename)
        
        # Look in cover_letters directory for most files
        if filename.startswith('scraped_job_'):
            filepath = DATA_DIR / just_filename
        else:
            # Search in output/cover_letters
            filepath = OUTPUT_DIR / 'cover_letters' / just_filename
        
        # Verify file exists
        if not filepath.exists():
            return jsonify({'error': f'File not found: {just_filename}'}), 404
        
        return send_file(str(filepath), as_attachment=True, download_name=just_filename)
    except Exception as e:
        logger.exception(f"Download error: {e}")
        return jsonify({'error': str(e)}), 404
```

### Option 2: Frontend Fix

Change the frontend to send only the filename:

**File:** `templates/batch.html`

**Current:**
```javascript
<a href="/download/${job.result.files.docx}" class="action-link download">Word</a>
```

**Fixed:**
```javascript
<a href="/download/${Path.basename(job.result.files.docx)}" class="action-link download">Word</a>
```

But this requires JavaScript Path utility which isn't available. Better:

```javascript
<a href="/download/${job.result.files.docx.split('/').pop()}" class="action-link download">Word</a>
```

This extracts just the filename from the path.

---

## Recommended Implementation

I recommend **Option 1 (Backend Fix)** because:
1. More robust error handling
2. File path validation
3. Better logging
4. Handles edge cases

Let me apply this fix:

**File:** `src/app.py`  
**Function:** `download()`

Changes:
1. Import `os` module
2. Extract filename from path
3. Add file existence check
4. Add error logging
5. Set proper download name in response

---

## What the Down Arrow Does

**Purpose:** Visual indicator that this is a download link

**CSS Implementation:**
```css
.action-link.download::before {
    content: '⬇ ';  /* Displays before "Word" text */
}
```

**Result:** Users see "⬇ Word" instead of just "Word"

**Why:** Clear visual cue that clicking this will download something

**Alternative icons you could use:**
- `'📥 '` - Download icon
- `'💾 '` - Save icon  
- `'📄 '` - Document icon
- Keep current: `'⬇ '` - Down arrow (good, simple)

---

## Testing Steps

### After Applying Backend Fix

1. **Process a job** and wait for completion
2. **Find the Word link** in the results table
3. **Click the Word link** (⬇ Word)
4. **Verify:**
   - ✅ File downloads to your Downloads folder
   - ✅ Filename is correct and readable
   - ✅ File opens in Word/LibreOffice
   - ✅ Contains the correct cover letter text
   - ✅ Formatting is preserved

### Debug if Download Fails

1. **Open browser DevTools** (F12)
2. **Go to Network tab**
3. **Click the Word link**
4. **Look for the request:**
   - `GET /download/...` should appear
   - Check the Response Status Code:
     - ✅ 200 = Success (file downloaded)
     - ❌ 404 = File not found (path issue)
     - ❌ 500 = Server error (exception in code)
5. **Check Response Preview** for error messages

---

## Implementation Plan

### Step 1: Apply Backend Fix

Update `/download` endpoint in `src/app.py` to:
1. Extract filename from path
2. Look in correct directory
3. Validate file exists
4. Log errors properly
5. Set download filename in headers

### Step 2: Test

1. Process a job
2. Click Word link
3. Verify download works
4. Open file and verify content

### Step 3: Verify

1. Check multiple jobs with different filenames
2. Verify special characters (ö, ä, ü, spaces) work
3. Check error handling (try non-existent file)

---

## Expected Result

**Before:** Download might fail with 404 or incorrect path

**After:** 
- ✅ Word link downloads the correct DOCX file
- ✅ Down arrow (⬇) provides visual indication
- ✅ File opens in Word with cover letter content
- ✅ Filename is readable and descriptive

---

## Code Ready for Implementation

```python
@app.route('/download/<path:filename>')
def download(filename: str) -> Response:
    """Download generated file"""
    try:
        import os
        
        # Extract just the filename from the path
        # Example: "output/cover_letters/file.docx" → "file.docx"
        just_filename = os.path.basename(filename)
        logger.info(f"Download request: filename={filename}, basename={just_filename}")
        
        # Determine directory and filepath
        if filename.startswith('scraped_job_'):
            filepath = DATA_DIR / just_filename
            logger.info(f"  Looking in DATA_DIR: {filepath}")
        else:
            # Most files are in output/cover_letters
            filepath = OUTPUT_DIR / 'cover_letters' / just_filename
            logger.info(f"  Looking in cover_letters: {filepath}")
        
        # Verify file exists before attempting download
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return jsonify({'error': f'File not found: {just_filename}'}), 404
        
        logger.info(f"  Sending file: {filepath}")
        return send_file(
            str(filepath), 
            as_attachment=True,
            download_name=just_filename
        )
    except Exception as e:
        logger.exception(f"Download error for {filename}: {e}")
        return jsonify({'error': str(e)}), 404
```

---

## Would You Like Me To:

1. ✅ Apply the backend fix now?
2. Test it with actual files?
3. Add additional debugging/logging?
4. Change the down arrow icon to something else?

