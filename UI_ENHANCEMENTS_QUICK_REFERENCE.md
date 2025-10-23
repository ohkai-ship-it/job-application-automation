# UI Enhancements - Quick Reference

## Feature 1: Scrollable Queue Table

**What Changed**: Queue table now stays at fixed height with vertical scrolling instead of expanding.

**Max Height**: 450px
**Scrollbar**: Custom styled (purple gradient)
**Header**: Sticky (stays visible while scrolling)

**When to Use**: When processing more than 8 jobs at once.

---

## Feature 2: Clickable Links

### Job Title Link
- **Opens**: Original job posting (the Stepstone page)
- **In**: New tab
- **Icon/Visual**: Purple text with underline on hover

### Company Name Link
- **Opens**: Company website
- **In**: New tab
- **Icon/Visual**: Purple text with underline on hover

**Data Sources**:
- `source_url`: Comes from the job scraper (the Stepstone URL you provided)
- `company_page_url`: Searched automatically using DuckDuckGo if not in job posting

**Browser**: Check job data in network response (`/status/<job_id>`) to see these URLs

---

## Feature 3: Collapsible Settings

**Default State**: Expanded (settings visible)

**How to Collapse**: Click on "⚙️ Settings" header anywhere

**Visual Indicator**: Arrow (▼) on the right side
- Points down (▼) = Expanded
- Points left (◀) = Collapsed

**Animation**: 0.3 seconds smooth collapse/expand

**Use Case**: 
- Default: All settings visible for new users
- Collapsed: Power users who know their settings can save space
- State NOT saved (resets on page refresh)

---

## CSS Classes Reference

### Queue Table
```css
.queue-table-wrapper {
    max-height: 450px;
    overflow-y: auto;
    overflow-x: auto;
}
```

### Table Links
```css
.table-link {
    color: #667eea;           /* Primary purple */
    border-bottom: 1px dotted;
}
.table-link:hover {
    color: #764ba2;           /* Dark purple */
}
```

### Settings Collapsible
```css
.settings-header {
    cursor: pointer;
}
.settings-content {
    max-height: 500px;
    transition: max-height 0.3s ease;
}
.settings-content.collapsed {
    max-height: 0;
}
```

---

## JavaScript Functions

### Toggle Settings Panel
```javascript
toggleSettings(headerElement)
```
- Called when clicking settings header
- Toggles `.collapsed` class on header and content
- CSS handles animation

---

## Backend Data Flow

```
User submits URL
    ↓
/process endpoint
    ↓
Scraper extracts job_data
    - Gets source_url (job posting URL)
    - If no company_page_url in posting:
      → _find_company_page_url() searches DuckDuckGo
    - Stores in job_data dict
    ↓
Status response includes:
    - result.source_url
    - result.company_page_url
    ↓
Frontend uses to create links in queue table
```

---

## Troubleshooting

### Links showing as plain text?
- Check that job has completed (status = 'completed')
- Verify `job.result.source_url` and `job.result.company_page_url` exist
- Check browser console for errors

### Settings panel not collapsing?
- Check that `.settings-header` has `onclick="toggleSettings(this)"`
- Verify CSS classes are applied
- Check console for JavaScript errors

### Table not scrolling?
- Verify more than 8 jobs in queue (or less than 450px viewport)
- Check `.queue-table-wrapper` has `max-height: 450px`
- Check `overflow-y: auto` is set

---

## Performance Notes

- ✅ No new external dependencies
- ✅ Web search only happens once per job (cached)
- ✅ CSS animations are GPU accelerated
- ✅ No layout thrashing

---

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Scrolling | ✅ | ✅ | ✅ | ✅ |
| Sticky header | ✅ | ✅ | ✅ | ✅ |
| CSS transitions | ✅ | ✅ | ✅ | ✅ |
| Flexbox/Grid | ✅ | ✅ | ✅ | ✅ |

---

## Future Ideas

1. **Remember collapse state**: Save to localStorage
2. **Mobile-optimized**: Auto-collapse on small screens
3. **Keyboard shortcuts**: K to collapse, arrows to navigate
4. **Bulk actions**: Multi-select jobs with checkboxes
5. **Sort/Filter**: Click column headers to sort queue
6. **Export**: Download queue as CSV
7. **Preview tooltips**: Hover job title to see first 100 chars of description

