# Stepstone Attachment Timeout Analysis

## Problem Statement

When processing **Stepstone job postings**, the Trello card creation encounters timeouts when adding the "Ausschreibung" (job posting) attachment:

```
HTTPSConnectionPool(host='api.trello.com', port=443): Read timed out. (read timeout=10)
Error adding attachment 'Ausschreibung': [timeout error]
```

This timeout **does NOT occur with LinkedIn postings**.

## Root Cause Analysis

### Stepstone URL Characteristics
Stepstone URLs are significantly longer and more complex than LinkedIn URLs:
- **Example format**: `https://www.stepstone.de/stellenangebote--[TITLE]--[NUMBER]-inline.html`
- **Typical length**: 120-200+ characters
- **Special characters**: Multiple hyphens, special encoding for job titles

### LinkedIn URL Characteristics  
LinkedIn URLs are much shorter and simpler:
- **Example format**: `https://www.linkedin.com/jobs/view/[JOB_ID]/`
- **Typical length**: 40-60 characters
- **Characters**: Minimal special characters

### Why This Matters for Trello API

When Trello receives an attachment URL via POST `/cards/{id}/attachments`:
1. Trello **validates the URL** by attempting to fetch it
2. Trello **downloads metadata** about the page (title, description, etc.)
3. Long URLs and complex page structure can cause:
   - **Slow server response** from Stepstone
   - **Trello timeout** while waiting for metadata extraction (10 second timeout)
   - **Read timeout** during response processing

**LinkedIn URLs** being shorter and from a faster CDN don't trigger this timeout.

## Evidence

From the logs:
```
2025-10-23 06:33:02 | WARNING | HTTP POST timeout, retrying...
2025-10-23 06:33:04 | ERROR | HTTP POST failed after 3 retries: Read timed out
```

The fact that LinkedIn doesn't show this error suggests:
1. LinkedIn URLs are either shorter or resolve faster
2. LinkedIn pages are simpler and fetch metadata quicker
3. Stepstone's server response time exceeds Trello's expectations

## Solutions

### Option 1: Shorten Stepstone URLs ✅ RECOMMENDED
Use Trello's native `idempotency_key` and store the full URL in a custom field instead:

```python
# Store URL in custom field (no timeout risk)
# Use shortened URL or job ID as attachment link
```

**Pros:**
- Avoids Trello timeout entirely
- Cleaner Trello card
- URL stored safely in custom fields

**Cons:**
- URL not visible as clickable attachment

### Option 2: Skip Stepstone Attachments
Disable attachment addition for Stepstone URLs (don't do this - loses data):

```python
if 'stepstone' not in source_url.lower():
    add_attachment()
```

**Cons:**
- Loses valuable source link
- Inconsistent UX between sources

### Option 3: Increase Timeout
Increase HTTP request timeout for Trello attachment requests:

```python
timeout=30  # instead of 10
```

**Pros:**
- Simple fix

**Cons:**
- User experience delays
- May still timeout on slow connections
- Doesn't address root cause

### Option 4: Use Trello's Shortened URL Service
Leverage Trello's URL shortening or embed links differently:

```python
# Use Trello's bitly-like URL shortening
payload = {
    'name': name,
    'url': shorten_url(url_to_attach)  # Via service
}
```

**Cons:**
- Requires external service
- Added complexity

## Recommended Implementation

**Option 1 + Option 3 (Hybrid Approach):**

1. **Increase timeout to 15-20 seconds** for better reliability
2. **Store full URL in custom field** "Source URL" for reference
3. **Add attachment with job ID only** instead of full URL

```python
def _add_attachments(self, card_id: str, job_data: Dict[str, Any]) -> None:
    source_url = job_data.get('source_url', '')
    
    if source_url:
        # Store full URL in custom field (no timeout risk)
        # This is already done in _set_custom_fields()
        
        # For attachment, use job ID link (much shorter, no timeout)
        if 'stepstone' in source_url.lower():
            # Extract job ID from Stepstone URL
            match = re.search(r'--(\d+)-inline\.html', source_url)
            if match:
                job_id = match.group(1)
                # Create short Stepstone link
                short_url = f"https://www.stepstone.de/stellenangebote/--{job_id}-inline.html"
                attachments_to_add.append(('Ausschreibung', short_url))
        elif 'linkedin' in source_url.lower():
            # LinkedIn URLs are already short
            attachments_to_add.append(('Ausschreibung', source_url))
        else:
            # Generic handler
            attachments_to_add.append(('Ausschreibung', source_url))
    
    # Increase timeout for reliability
    resp = self.requester(
        'POST',
        url,
        params=self.auth_params,
        json=payload,
        timeout=20  # Increased from 10
    )
```

## Alternative: Remove Attachment, Use Custom Field Only

Since we already store URLs in custom fields, we could:
1. **Remove attachment addition entirely** (eliminates timeout)
2. **Ensure custom "Source URL" field is set** (already done)
3. **Users access link from field, not attachment**

This is actually cleaner and avoids all Trello API timing issues.

## Testing Plan

1. **Test with current implementation** (expect Stepstone timeout)
2. **Implement timeout increase** (should reduce failures)
3. **Test with shortened URLs** (should eliminate failures)
4. **Monitor Trello API response times** (log timing data)

## Files Affected

- `src/trello_connect.py`: `_add_attachments()` method (lines 447-490)
- `src/utils/http_utils.py`: Timeout configuration

## Related Issues

- Trello API has strict 10-second timeout for attachment metadata extraction
- Stepstone URLs trigger expensive metadata fetches on Stepstone's servers
- LinkedIn URLs are served from fast CDN with quick metadata

## Recommendation

**Go with Option 1 (Recommended):**
- Increase timeout to 20 seconds
- This gives Stepstone more time to respond
- Maintains current functionality
- Minimal code change
- Preserves user experience (clickable attachments)

**Future improvement:** Move URLs to custom fields and remove attachments entirely for even more reliability.
