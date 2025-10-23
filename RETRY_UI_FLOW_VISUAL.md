# Retry UI Flow - Visual Guide

## State Transitions

### Initial State - Error
```
┌─────────────────────────────────────────────────────┐
│ GETRAS GmbH | Kfz-Mechaniker                        │
├─────────────────────────────────────────────────────┤
│ Status: ⚠️ Cover Letter Failed                      │
│ Message: "Cover letter length out of bounds: 160.. │
│ Actions: [🔄 Retry]                                │
└─────────────────────────────────────────────────────┘
```

### User Clicks Retry
```
Confirmation Dialog:
┌──────────────────────────────────┐
│ Retry cover letter generation?   │
│ [OK]  [Cancel]                   │
└──────────────────────────────────┘
```

### During Retry
```
┌─────────────────────────────────────────────────────┐
│ GETRAS GmbH | Kfz-Mechaniker                        │
├─────────────────────────────────────────────────────┤
│ Status: ⏳ Processing (60%)                          │
│ Message: "Generating Cover Letter with AI (Retry)"  │
│ Progress: [████████░░░░░░░░░░░░░░░░░░░] 60%        │
└─────────────────────────────────────────────────────┘
```

### Success - Completed
```
┌─────────────────────────────────────────────────────┐
│ GETRAS GmbH | Kfz-Mechaniker                        │
├─────────────────────────────────────────────────────┤
│ Status: ✅ Completed                                │
│ Message: "Cover letter generated successfully!"     │
│ Actions: [↓ Word] [📄 PDF] [🔗 Trello]            │
└─────────────────────────────────────────────────────┘
```

## Timeline

```
12:38:00  Job submitted
          ↓
12:38:07  ⚠️ Error: "Cover letter length out of bounds: 160 words"
          Badge shows: "⚠️ Cover Letter Failed"
          Button shows: "🔄 Retry"
          ↓
          User clicks "🔄 Retry"
          ↓
12:38:08  Progress: 60% - "Generating Cover Letter with AI (Retry)"
          ↓
12:38:13  Progress: 80% - "Creating Word document"
          ↓
12:38:16  Progress: 100% - "Cover letter generated successfully!"
          Badge updates: ✅ Completed
          Buttons appear: [↓ Word] [📄 PDF] [🔗 Trello]
          ↓
          User can download Word document
```

## Action Links - State Dependent

### When Status = "⚠️ Cover Letter Failed"
```
Actions: [🔄 Retry]
```
Only retry button shows. No download links.

### When Status = "⏳ Processing"
```
Actions: (disabled - show progress message)
```
No buttons while processing.

### When Status = "✅ Completed"
```
Actions: [↓ Word] [📄 PDF] [🔗 Trello]
```
Download links appear.

**Word Link:**
- Always active if DOCX file exists
- Downloads: `output/cover_letters/...docx`

**PDF Link:**
- Active only if PDF conversion was enabled
- Downloads: `output/cover_letters/...pdf`
- Grayed out if no PDF

**Trello Link:**
- Links to existing Trello card (created during initial processing)
- Always preserved, even on retry

## Progress Indicators

### During Retry Progress

```
Step 1: Start Retry
Progress: 60%
Message: "Generating Cover Letter with AI (Retry)"

Step 2: Generate Document
Progress: 80%
Message: "Creating Word document"

Step 3: Complete
Progress: 100%
Message: "Cover letter generated successfully!"
Status: "✅ Completed"
```

## File Download

### When Clicking Word Link
```
<a href="/download/output/cover_letters/Anschreiben - Kai Voges - 2025-10-23 - GETRAS GmbH.docx" download>
  ↓ Word
</a>
```
Downloads DOCX file to user's computer.

### When Clicking Trello Link
```
<a href="https://trello.com/c/abc123xyz..." target="_blank">
  🔗 Trello
</a>
```
Opens Trello card in new tab (created during initial job processing).

## Error Cases

### Retry Still Fails
```
┌─────────────────────────────────────────────────────┐
│ GETRAS GmbH | Kfz-Mechaniker                        │
├─────────────────────────────────────────────────────┤
│ Status: ⚠️ Cover Letter Failed                      │
│ Message: "Retry failed: Still too short (165 words)"│
│ Actions: [🔄 Retry]                                │
└─────────────────────────────────────────────────────┘
```
Button remains, user can try again.

### Job Not Found
```
Alert: "Error: Job not found in queue"
```
Shouldn't happen in normal operation.

## Summary

✅ **Initial Error** → "⚠️ Cover Letter Failed" with Retry button
✅ **User Clicks Retry** → Confirmation dialog
✅ **During Retry** → Progress bar shows 60% → 100%
✅ **On Success** → "✅ Completed" with download links
✅ **Download Links** → Word, PDF, Trello
✅ **On Failure** → Still shows Retry button for another attempt

**All actions update in real-time without page refresh!**
