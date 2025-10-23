# Testing Guide - Processing Options

## 5 Processing Mode Combinations

### Mode 1: Trello Only ✓
**Checkboxes:**
- ✓ Create Trello Cards
- ☐ Generate Documents
- ☐ Generate PDF

**Expected Results:**
- Trello card created with job data
- No Word document generated
- No PDF generated
- Progress: "Processing" → "Created Trello card"

**Backend Call:**
```python
process_job_posting(
    url="...",
    create_trello_card=True,
    generate_cover_letter=False,
    generate_pdf=False
)
```

---

### Mode 2: Documents Only ✓
**Checkboxes:**
- ☐ Create Trello Cards
- ✓ Generate Documents
- ☐ Generate PDF (disabled, grayed out)

**Expected Results:**
- No Trello card created
- Word document generated (`output/cover_letters/cover_letter_*.docx`)
- No PDF generated
- Progress: "Processing" → "Generated cover letter"

**Backend Call:**
```python
process_job_posting(
    url="...",
    create_trello_card=False,
    generate_cover_letter=True,
    generate_pdf=False
)
```

**This is the DEFAULT mode** (Documents checkbox starts checked)

---

### Mode 3: Documents + PDF ✓
**Checkboxes:**
- ☐ Create Trello Cards
- ✓ Generate Documents
- ✓ Generate PDF (enabled when Documents checked)

**Expected Results:**
- No Trello card created
- Word document generated (`output/cover_letters/cover_letter_*.docx`)
- PDF generated from Word (`output/cover_letters/cover_letter_*.pdf`)
- Progress: "Processing" → "Generated cover letter" → "Generated PDF"

**Backend Call:**
```python
process_job_posting(
    url="...",
    create_trello_card=False,
    generate_cover_letter=True,
    generate_pdf=True
)
```

---

### Mode 4: Trello + Documents ✓
**Checkboxes:**
- ✓ Create Trello Cards
- ✓ Generate Documents
- ☐ Generate PDF (optional)

**Expected Results:**
- Trello card created
- Word document generated
- No PDF generated
- Progress: "Processing" → "Created Trello card" → "Generated cover letter"

**Backend Call:**
```python
process_job_posting(
    url="...",
    create_trello_card=True,
    generate_cover_letter=True,
    generate_pdf=False
)
```

---

### Mode 5: Trello + Documents + PDF ✓
**Checkboxes:**
- ✓ Create Trello Cards
- ✓ Generate Documents
- ✓ Generate PDF

**Expected Results:**
- Trello card created with job data and link to documents
- Word document generated
- PDF generated from Word
- Progress: "Processing" → "Created Trello card" → "Generated cover letter" → "Generated PDF"

**Backend Call:**
```python
process_job_posting(
    url="...",
    create_trello_card=True,
    generate_cover_letter=True,
    generate_pdf=True
)
```

**This is the FULL workflow** (all three enabled)

---

## Error Cases

### Case: No Options Selected ✗
**Checkboxes:**
- ☐ Create Trello Cards
- ☐ Generate Documents
- ☐ Generate PDF (disabled)

**Expected Behavior:**
1. Red error message appears: "Select at least one option above"
2. Browser alert shows: "At least one processing option must be selected!"
3. Processing is blocked
4. **No network request sent**
5. No progress bar shown

**Why This Works:**
- Validation happens in `processAllJobs()` BEFORE any fetch calls
- Error prevents wasting user's time and API quota

---

### Case: PDF Selected But Documents Not Selected ✗
**User tries to:**
1. Uncheck "Generate Documents"
2. Check "Generate PDF"

**Expected Behavior:**
- Step 2 fails: PDF checkbox cannot be clicked
- Visual indicator: PDF checkbox is grayed out (0.5 opacity)
- Cannot be checked when Documents is unchecked

**Why This Works:**
- JavaScript event listener on Documents checkbox controls PDF state
- If Documents is unchecked, PDF is disabled and unchecked
- If Documents is checked, PDF is enabled and user can choose

---

## Testing Steps

### Quick Test (5 minutes)

1. **Start Flask app:**
   ```powershell
   .venv\Scripts\python.exe src/app.py
   ```

2. **Open browser:**
   ```
   http://127.0.0.1:5000/batch
   ```

3. **Prepare URLs:** Copy 2-3 URLs from below
   ```
   https://www.linkedin.com/jobs/view/3915544631/
   https://www.linkedin.com/jobs/view/3915544632/
   ```

4. **Test Mode 2 (DEFAULT - Documents):**
   - Paste URLs
   - Verify "Generate Documents" is checked
   - Verify "Create Trello Cards" is unchecked
   - Verify "Generate PDF" is disabled (grayed out)
   - Click "Process All Jobs"
   - Watch progress bar move through: Processing → Generated cover letter
   - Verify files appear in `output/cover_letters/`

5. **Test Mode 4 (Trello + Documents):**
   - Paste different URLs
   - Check "Create Trello Cards"
   - Check "Generate Documents"
   - Verify "Generate PDF" is now enabled
   - Don't check PDF
   - Click "Process All Jobs"
   - Watch both operations complete

### Comprehensive Test (15 minutes)

Test all 5 modes by:
1. For each mode above, gather 1-2 test URLs
2. Paste URLs, select appropriate checkboxes
3. Click "Process All Jobs"
4. Verify expected outputs
5. Check backend logs for correct flow

### Edge Case Tests (10 minutes)

1. **Empty URLs:** Click Process without pasting anything
   - Expected: Error message "Please paste job URLs first"

2. **Uncheck Documents then check PDF:**
   - Expected: PDF checkbox stays disabled

3. **Process one batch with Documents, second with Trello:**
   - Expected: Each uses its own stored settings

4. **Check all three boxes and process:**
   - Expected: All three operations complete successfully

---

## Observation Checklist

### UI Behavior
- [ ] PDF checkbox disabled (gray, not clickable) when Documents unchecked
- [ ] PDF checkbox enabled (clickable, normal opacity) when Documents checked
- [ ] Error message shows when trying to process with no options
- [ ] Error message goes away when at least one option checked
- [ ] Each job in queue shows its own status independently

### Backend Behavior
- [ ] Correct files generated based on checkboxes
- [ ] Trello cards appear in board when checked
- [ ] Word documents appear in `output/` when checked
- [ ] PDF files appear alongside Word docs when checked
- [ ] No files generated when unchecked

### Progress Indication
- [ ] Progress bar shows for each job
- [ ] Progress messages correspond to operations (Trello, Documents, PDF)
- [ ] Status updates correctly after each step
- [ ] Final status shows success or error

### Network Traffic
- [ ] Correct parameters sent in fetch request (use DevTools Network tab)
- [ ] Backend returns 200 status for valid requests
- [ ] Backend returns 400 status for invalid requests (no options)

---

## File Locations for Verification

**After running Mode 2 (Documents Only):**
```
output/
├── cover_letters/
│   ├── cover_letter_[timestamp].txt
│   └── cover_letter_[timestamp].docx
└── scraped_jobs/
    └── job_[timestamp].json
```

**After running Mode 3 (Documents + PDF):**
```
output/
├── cover_letters/
│   ├── cover_letter_[timestamp].txt
│   ├── cover_letter_[timestamp].docx
│   └── cover_letter_[timestamp].pdf
└── scraped_jobs/
    └── job_[timestamp].json
```

**After running Mode 1 (Trello Only):**
```
# Check Trello board directly (no files in output/)
# Card should appear in "Leads" list with:
- Job title as card name
- Company name in description
- Link to job posting
- Checklist from template
```

---

## Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| PDF checkbox won't enable | Documents is unchecked | Check "Generate Documents" first |
| Nothing happens when processing | No progress bar, no errors | Check "Create Trello Cards" OR "Generate Documents" is selected |
| No files generated | Processed but no output | Check that "Generate Documents" was checked |
| Trello card not created | Only documents generated | Check that "Create Trello Cards" was checked |
| Error: "At least one processing option" | Cannot start processing | Select at least one checkbox before clicking Process |

---

## Expected Processing Times

**Per Job:**
- Scraping: 2-5 seconds
- Trello card creation: 1-2 seconds
- Cover letter generation (AI): 5-15 seconds
- Document generation (Word): 1-2 seconds
- PDF conversion: 2-5 seconds

**Total for one job:**
- Mode 1 (Trello only): ~3-7 seconds
- Mode 2 (Documents only): ~8-22 seconds
- Mode 3 (Documents + PDF): ~10-27 seconds
- Mode 4 (Trello + Documents): ~11-29 seconds
- Mode 5 (All three): ~13-34 seconds

**For 3-5 jobs in batch:**
- Multiply per-job time by job count
- Note: 3-second polite delay added between jobs

---

## Success Criteria

All 5 of the following must be true:

1. ✅ Mode 1 (Trello Only) works without errors
2. ✅ Mode 2 (Documents Only) works without errors
3. ✅ Mode 3 (Documents + PDF) works without errors
4. ✅ Mode 4 (Trello + Documents) works without errors
5. ✅ Mode 5 (All Three) works without errors

**Bonus tests:**
6. ✅ Error message appears when no options selected
7. ✅ PDF checkbox cannot be selected when Documents unchecked
8. ✅ All tests still pass: `pytest -q` returns 109/109

---

## Logging for Debugging

If something goes wrong, check these logs:

**Browser Console (F12):**
- JavaScript errors
- Network request details
- Response payload from backend

**Terminal (Flask output):**
```
[DEBUG] create_trello_card=True
[DEBUG] generate_cover_letter=True  
[DEBUG] generate_pdf=True
[INFO] Processing job posting...
[INFO] Created Trello card
[INFO] Generated cover letter
[INFO] Generated PDF
```

**Code Files Generated:**
- Check timestamps in `output/` folder
- Verify file sizes are reasonable
- Open documents to verify content

---

## Next Steps After Testing

If all tests pass:
1. ✅ Commit to feature branch: `git commit -am "feat: Implement flexible processing options"`
2. ✅ Push to remote: `git push origin feature/ui-ux-improvements`
3. ✅ Create PR to merge into master
4. ✅ Mark issue as resolved

If tests fail:
1. Document the failure
2. Check backend logs for errors
3. File issue with specific error message
4. Revert and debug

---

**Expected Result:** All 5 modes work flawlessly with correct file generation and Trello card creation. ✅
