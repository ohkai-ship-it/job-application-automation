# Word Link Path Fix - "Can't Find the Path" Error ✅

## The Problem

When clicking the "⬇ Word" link to download a cover letter, you got an error:
```
"File not found: Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx"
```

**Root Cause**: Flask was looking for files in the wrong directory.

When `python src/app.py` runs, the working directory is not the project root—it's where you execute the command from. But the code was using **relative paths**:
```python
OUTPUT_DIR = Path(get_str('OUTPUT_DIR', 'output'))  # ❌ Relative!
DATA_DIR = Path(get_str('DATA_DIR', 'data'))        # ❌ Relative!
```

This meant Flask looked for files here:
```
wherever/you/ran/from/output/cover_letters/file.docx  ❌ WRONG!
```

But files are actually here:
```
C:\Users\Kai\OneDrive\Documents\04 Themen\Tech\Programmierung\VS Code\Python\job-application-automation\output\cover_letters\file.docx  ✅ CORRECT!
```

---

## The Fix

Changed the paths to be **absolute** by calculating them relative to the script location:

```python
# OLD (Relative - broke when running from different directory)
OUTPUT_DIR = Path(get_str('OUTPUT_DIR', 'output'))
DATA_DIR = Path(get_str('DATA_DIR', 'data'))

# NEW (Absolute - works from anywhere)
APP_ROOT = Path(__file__).parent.parent  # Go up from src/ to project root
OUTPUT_DIR = Path(get_str('OUTPUT_DIR', str(APP_ROOT / 'output')))
DATA_DIR = Path(get_str('DATA_DIR', str(APP_ROOT / 'data')))
```

**How it works:**
- `__file__` = `C:\...\src\app.py` (location of this script)
- `.parent` = `C:\...\src` (the src directory)
- `.parent.parent` = `C:\...` (the project root)
- `APP_ROOT / 'output'` = `C:\...\output` (absolute path)

Now Flask finds files correctly **no matter where you run the command from**.

---

## What Changed

**File:** `src/app.py` (Lines 45-48)

```diff
- # Paths configuration
- OUTPUT_DIR = Path(get_str('OUTPUT_DIR', 'output'))
- DATA_DIR = Path(get_str('DATA_DIR', 'data'))

+ # Paths configuration (relative to project root, not src/)
+ APP_ROOT = Path(__file__).parent.parent  # Go up from src/ to project root
+ OUTPUT_DIR = Path(get_str('OUTPUT_DIR', str(APP_ROOT / 'output')))
+ DATA_DIR = Path(get_str('DATA_DIR', str(APP_ROOT / 'data')))
```

---

## Testing the Fix

### Step 1: Restart Flask
Stop the old instance (if running) and start fresh:
```powershell
python src/app.py
```

You should see output like:
```
App initialized successfully
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 2: Open the UI
- Open browser: http://localhost:5000/batch

### Step 3: Process a Job
1. Enter a job URL (or use a previous result)
2. Click **Process** (or **Process All**)
3. Wait for completion
4. Check results table

### Step 4: Test Word Link
1. Find a completed job in the results
2. Click the **⬇ Word** link
3. **Verify:**
   - ✅ File downloads immediately
   - ✅ No error message appears
   - ✅ Filename shows correctly in Downloads folder
   - ✅ File opens in Word/LibreOffice with cover letter text

### Step 5: Check Server Logs (Debug)
In your terminal running Flask, you should see:
```
INFO: Download request: filename=output/cover_letters/Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx, basename=Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx
INFO:   Looking in cover_letters: /full/path/to/output/cover_letters/Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx
INFO:   Sending file: /full/path/to/output/cover_letters/Anschreiben - Kai Voges - 2025-10-19 - Max Bögl Wind AG.docx
```

If you see this, the fix is working! ✅

---

## Why This Matters

This fix ensures:
- ✅ Word link works from any directory
- ✅ Trello link still works (unaffected)
- ✅ File downloads have correct names
- ✅ Cover letters are accessible to users
- ✅ No more "can't find the path" errors

---

## Expected Behavior After Fix

| Action | Before | After |
|--------|--------|-------|
| Click ⬇ Word | ❌ Error: "File not found" | ✅ File downloads |
| Filename | N/A | ✅ `Anschreiben - Kai Voges - 2025-10-19 - Company.docx` |
| Open file | N/A | ✅ Cover letter content visible |

---

## If It Still Doesn't Work

1. **Check Flask is running** - Terminal should show `Running on http://127.0.0.1:5000`
2. **Check file exists** - Look in `output/cover_letters/` folder
3. **Check logs** - Look for path info in terminal output
4. **Restart Flask** - Stop and run `python src/app.py` again
5. **Clear cache** - Hard refresh browser (Ctrl+Shift+R on Windows)

---

## Status

✅ **FIXED** - Word link should now work correctly!

The download endpoint will find files in the correct location regardless of where Flask is started from.

