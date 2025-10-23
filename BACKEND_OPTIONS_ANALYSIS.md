# Backend Options Analysis - Processing Modes

## Current Backend Architecture

### What the Backend Currently Does (Always)

1. **Scrapes the job posting** ✓ Always done
2. **Creates a Trello card** ✓ Always done (unconditional)
3. **Generates cover letter** ✓ Always done (if not disabled by placeholder mode)
4. **Generates Word document** ✓ Always done after cover letter
5. **Optionally generates PDF** (conditional on `generate_pdf` parameter)

### Current Function Signature

```python
def process_job_posting(
    url: str,
    generate_cover_letter: bool = True,
    generate_pdf: bool = False,
    skip_duplicate_check: bool = False
) -> Dict[str, Any]:
```

**Current limitations:**
- No parameter to skip Trello card creation
- No parameter to skip document generation
- Cover letter generation is tied to document generation (both always happen together)
- Only PDF generation is optional

### Current API Endpoint

**POST /process**

```json
{
  "url": "https://...",
  "create_trello_card": true,  // Currently accepted but IGNORED!
  "generate_pdf": false         // Currently respected
}
```

**Issue:** The `create_trello_card` parameter is read by app.py but never passed to `process_job_posting()` and therefore has NO EFFECT.

---

## Proposed Architecture (Per Your Requirements)

### Rule 1: Conditional Processing
- User can choose to create **Trello card** (Y/N)
- User can choose to generate **Documents/Cover Letter** (Y/N)
- At least ONE must be selected, or show error "Nothing to process"

### Rule 2: Document Generation Hierarchy
- If "Generate Documents" is selected:
  - **Always** generate Word cover letter (.docx)
  - **Optionally** generate PDF (.pdf) - controlled by separate checkbox
- If "Generate Documents" is NOT selected:
  - Do NOT generate Word or PDF

### Processing Modes

| Mode | Trello | Word | PDF | Use Case |
|------|--------|------|-----|----------|
| 1    | ✓      | ✗    | ✗   | Just organize in Trello (quick collection) |
| 2    | ✗      | ✓    | ✗   | Just generate Word document (batch cover letters) |
| 3    | ✗      | ✓    | ✓   | Generate Word + PDF (both documents) |
| 4    | ✓      | ✓    | ✗   | Full workflow - organize + Word document |
| 5    | ✓      | ✓    | ✓   | Full workflow - organize + Word + PDF |
| None | ✗      | ✗    | ✗   | **ERROR: At least one option required** |

---

## Required Backend Changes

### 1. Update `process_job_posting()` Function Signature

```python
def process_job_posting(
    url: str,
    generate_cover_letter: bool = True,    # NEW: will generate Word
    generate_pdf: bool = False,             # EXISTING: conditional PDF
    create_trello_card: bool = True,        # NEW: optional Trello
    skip_duplicate_check: bool = False
) -> Dict[str, Any]:
```

### 2. Update Processing Logic

**Key changes needed:**

- **Skip Trello step** (line ~185-200) if `create_trello_card=False`
  - Return early if Trello fails only when enabled
  - Skip to cover letter if Trello is disabled

- **Skip document generation** (line ~310-350) if `generate_cover_letter=False`
  - Skip both cover letter text AND Word document generation
  - PDF generation already conditional on `generate_pdf`

- **Return structure** should reflect what was actually generated:
  ```python
  return {
      'status': 'success',
      'files_generated': {
          'trello_card': card if create_trello_card else None,
          'word_document': docx_file if generate_cover_letter else None,
          'pdf_document': pdf_file if (generate_cover_letter and generate_pdf) else None
      },
      'job_data': job_data,
      # ... existing fields
  }
  ```

### 3. Update app.py `/process` Route

**Pass new parameters correctly:**

```python
def process_in_background(
    job_id: str, 
    url: str, 
    create_trello_card: bool = True,    # Pass this
    generate_documents: bool = True,    # NEW: controls Word doc generation
    generate_pdf: bool = False          # Optional PDF
) -> None:
    # ...
    result = process_job_posting(
        url,
        generate_cover_letter=generate_documents,  # Controls Word generation
        generate_pdf=generate_pdf,                 # Controls PDF generation
        create_trello_card=create_trello_card      # Controls Trello card
    )
```

### 4. Validation in app.py

Add validation before processing:

```python
@app.route('/process', methods=['POST'])
def process() -> Response:
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    create_trello = data.get('create_trello_card', False)
    generate_documents = data.get('generate_documents', False)
    generate_pdf = data.get('generate_pdf', False)
    
    # NEW: Validation - at least one option must be selected
    if not create_trello and not generate_documents:
        return jsonify({
            'error': 'At least one of "Create Trello Card" or "Generate Documents" must be selected'
        }), 400
    
    # PDF only makes sense if generating documents
    if generate_pdf and not generate_documents:
        generate_pdf = False  # Silently ignore orphaned PDF flag
    
    # ... rest of the function
```

---

## Files to Modify

1. **src/main.py**
   - Add `create_trello_card` parameter to `process_job_posting()`
   - Add conditional logic to skip Trello step
   - Add conditional logic to skip document generation
   - Update return structure to reflect what was generated

2. **src/app.py**
   - Update `/process` route to accept both parameters
   - Add validation (at least one option must be selected)
   - Pass parameters correctly to `process_job_posting()`
   - Update `process_in_background()` function signature
   - Handle result structure properly

3. **templates/batch.html** (UI changes - described separately)
   - Change checkboxes to match new logic
   - Add validation before submit
   - Show/hide PDF option based on "Generate Documents" state

---

## Return Value Structure (Updated)

### Success Response

```python
{
    'status': 'success',
    'files_generated': {
        'trello_card': {
            'id': '...',
            'shortUrl': 'https://trello.com/c/...',
            'name': 'Company - Job Title'
        } if create_trello_card else None,
        
        'word_document': 'output/cover_letters/Cover letter - Name - Date - Company.docx' if generate_documents else None,
        
        'pdf_document': 'output/cover_letters/Cover letter - Name - Date - Company.pdf' if (generate_documents and generate_pdf) else None
    },
    'job_data': { ... },
    'messages': ['Trello card created', 'Word document generated', 'PDF generated']
}
```

### Error Response

```python
{
    'error': 'At least one of "Create Trello Card" or "Generate Documents" must be selected'
}
```

---

## Implementation Priority

1. **High Priority:** Modify `process_job_posting()` in main.py
   - Add conditional Trello creation
   - Add conditional document generation

2. **High Priority:** Modify app.py validation and parameters
   - Add validation rule
   - Pass correct parameters

3. **Medium Priority:** Update return structure
   - Make it clear what was generated
   - Frontend needs to know what files are available

4. **UI Changes:** (described in separate document)
   - Update checkbox layout
   - Update validation messages
   - Update download links

---

## Testing Scenarios

After implementation, test all 5 modes:

1. ✓ Trello only (no docs)
2. ✓ Word only (no Trello)
3. ✓ Word + PDF (no Trello)
4. ✓ Trello + Word (no PDF)
5. ✓ Trello + Word + PDF (full workflow)
6. ✗ Nothing selected (should show error)
7. ✗ PDF only without Word (should be disabled or silently converted to "Word only")

---

## Summary

**Current state:** Backend forces Trello + Word generation always. PDF is optional.

**Desired state:** All three options independent (with logical constraints):
- Trello: optional
- Word document: optional (but if selected, always includes Word + optional PDF)
- PDF: only available when Word is selected

**Why:** More flexible for different use cases:
- Just organizing in Trello
- Just generating cover letters without Trello
- Full end-to-end workflow with all three
