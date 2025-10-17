# Figma AI Prompt for Job Application Automation UI

## Prompt for Figma AI

```
Create a modern, professional web application interface for a job application automation tool. The design should be clean, efficient, and focused on productivity.

**Main Screen: Job Processing Dashboard**

Design a single-page web application with the following components:

1. **Header Section**
   - App title: "Job Application Automation"
   - Subtitle: "Streamline your job search with AI-powered cover letters"
   - Color scheme: Professional blues and grays (primary: #2563eb, secondary: #64748b, background: #f8fafc)
   - Include a small status indicator showing "OpenAI Connected" with a green dot

2. **URL Input Section** (Top Priority)
   - Large, prominent text area for entering multiple Stepstone job URLs
   - Placeholder text: "Paste Stepstone job URLs here (one per line)..."
   - Height: 150px minimum
   - Add a "Paste from Clipboard" button next to the text area
   - Include a counter below showing "0 URLs entered"

3. **Action Buttons** (Horizontal Row)
   - Primary button: "Process All Jobs" (large, blue, prominent)
   - Secondary button: "Clear All" (smaller, gray)
   - Tertiary button: "Add to Queue" (outlined style)
   - All buttons should have rounded corners (8px) and subtle shadows

4. **Processing Queue Table**
   - Clean table with columns: Job Title | Company | Status | Actions
   - Status should use color-coded badges:
     - "Queued" = gray
     - "Processing" = yellow/amber with spinner icon
     - "Completed" = green with checkmark
     - "Error" = red with error icon
   - Actions column: Small "Download DOCX" button and "View in Trello" link
   - Empty state message: "No jobs in queue. Add URLs above to get started."

5. **Progress Indicator**
   - Progress bar showing overall completion (0/10 jobs processed)
   - Display: "Processing: 3 of 10 jobs..."
   - Smooth animated progress bar with gradient

6. **Results Summary Panel** (Right Sidebar - 30% width)
   - Card-style panel with rounded corners
   - Statistics:
     - "✓ 8 Cover Letters Generated"
     - "✓ 8 Trello Cards Created"
     - "⚠ 2 Errors"
   - Recent files list (last 5 generated DOCXs)
   - "View All Outputs" link at bottom

7. **Settings/Options Bar** (Bottom)
   - Checkbox: "Generate PDF" (currently disabled, grayed out)
   - Checkbox: "Create Trello Cards" (checked by default)
   - Checkbox: "Open files after generation"
   - Dropdown: "Language: Auto-detect / German / English"

**Design Guidelines:**
- Use Inter or similar modern sans-serif font
- Generous white space and padding (16px-24px between sections)
- Subtle shadows for depth (box-shadow: 0 1px 3px rgba(0,0,0,0.1))
- Rounded corners throughout (4px-8px)
- Responsive design: minimum width 1024px, centered layout with max-width 1400px
- Use icons from Lucide or Heroicons style (simple line icons)
- All interactive elements should have hover states (slightly darker/lighter)

**Accessibility:**
- High contrast text (WCAG AA compliant)
- Clear focus states for keyboard navigation
- Proper spacing for touch targets (minimum 44px height for buttons)

Create this as a single frame named "Job Processing Dashboard - Desktop View"
```

---

## Alternative: Simplified Component-First Approach

If the full dashboard is too complex, start with this simpler prompt:

```
Create a professional URL input component for a job application tool:

**Component: Multi-URL Input Card**

Design a clean card component (600px wide, auto height) with:

1. Card header: "Add Job Postings" with a small Stepstone logo icon
2. Large textarea (500px wide, 120px tall) with placeholder: "Paste Stepstone URLs here..."
3. URL counter badge in top-right: "3 URLs" in a blue pill shape
4. Two buttons at bottom:
   - Primary: "Process Jobs" (blue, #2563eb)
   - Secondary: "Clear" (gray, #94a3b8)
5. Small help text: "Paste one URL per line. We'll create Trello cards and cover letters for each."

Style:
- White background with subtle border (#e2e8f0)
- Rounded corners (12px)
- Drop shadow: 0 2px 8px rgba(0,0,0,0.08)
- Padding: 24px
- Font: Inter or system-ui
- Professional, clean, minimal

Name the component: "URL Input Card"
```

---

## What to Do After Figma AI Generates the Design

1. **Review the generated design** - Check if it matches the requirements
2. **Copy the Figma file URL** - Get the shareable link (must be set to "Anyone with link can view")
3. **Extract the File ID** - From URL: `https://www.figma.com/file/FILE_ID_HERE/...`
4. **Add to your `.env` file**:
   ```
   FIGMA_FILE_ID=your_file_id_here
   ```
5. **Run the test script**:
   ```powershell
   python src/helper/test_figma_connection.py
   ```

---

## Expected Output from Figma AI

Figma AI should create:
- ✅ A complete frame with all specified components
- ✅ Proper spacing and alignment
- ✅ Color palette applied consistently
- ✅ Interactive component variants (normal, hover, disabled states)
- ✅ Auto-layout containers for responsive behavior

If Figma AI creates something unexpected, you can:
1. Iterate with refined prompts
2. Manually adjust specific elements
3. Ask for specific component variations

---

## Next Steps in Our Workflow

1. You paste the prompt into Figma AI
2. Figma AI generates the design
3. You share the Figma file URL with me
4. I extract the component data using our `figma_client.py`
5. I generate HTML/CSS code from the Figma components
6. We review the generated code together
7. We integrate the best parts into `templates/index.html`

This approach gives you 70-80% of the UI code automatically! 🚀
