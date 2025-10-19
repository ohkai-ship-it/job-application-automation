# Quick Reference - Early Display Fix

## The Problem (What You Saw)
- Queue showed "Loading..." for entire job processing duration
- Job title and company only appeared when job completed
- Misleading to users (looked like nothing was happening)

## The Fix (What We Did)
1. **Wait 0.5s after early scrape** so frontend can poll and get the data
2. **Show progress at 10%** to indicate extraction happened
3. **Simplify frontend logic** to make it actually work
4. **Add logging** to debug if needed

## How to Test (30 seconds)

```bash
# 1. Start Flask
python .\src\app.py

# 2. Open browser
http://localhost:5000/batch

# 3. Process a job
Enter URL → Click Process

# 4. Watch queue table
- First 1-2 seconds: Shows "Loading..."
- After 1-2 seconds: Shows "Senior Developer" and "Tech Corp"
- Throughout processing: Still shows real values
```

## Expected Timeline

| Time | What Happens |
|------|--------------|
| 0s | Job starts, shows "Loading..." |
| 1-2s | Data extracted, shows real title/company |
| 5-20s | Trello card being created |
| 20-25s | Cover letter and documents generated |
| 25s | Complete! |

## How to Debug

### If still showing "Loading..."

1. **Hard refresh page**
   ```
   Ctrl+Shift+R
   ```

2. **Open console (F12) and look for**
   ```
   [job_1730...] Status: { job_title: 'Senior Developer', company_name: 'Tech Corp', ... }
   ```
   If you see real values in console but not in table, it's a frontend rendering issue.

3. **Check server logs for**
   ```
   ✓ Early extraction SUCCESS: Tech Corp - Senior Developer
   ```
   If NOT there, early scrape is failing.

### If you see errors

Look for these in terminal where Flask is running:
```
[job_id] Early scrape failed (will retry)
[job_id] Early scrape exception: ...
```

## Files Changed

1. **`src/app.py`** - Backend timing and logging
2. **`templates/batch.html`** - Frontend update logic

## Success Indicators

✅ Job title shows within 1-2 seconds  
✅ Company shows within 1-2 seconds  
✅ Both visible throughout (not just at end)  
✅ Progress bar shows 4 phases  
✅ Works for Stepstone AND LinkedIn  
✅ Multiple jobs work independently  

---

That's it! Simple timing fix that makes a big UX difference. 🚀

