# Upload Instructions for GitHub

## Step 1: Create Repository
1. Go to: https://github.com/new
2. Repository name: `bangla-pdf-editor`
3. Description: `Bangla PDF Editor with ANSI/Bijoy font support`
4. Make it **Public**
5. **DO NOT** check any initialization options
6. Click **"Create repository"**

## Step 2: Upload These Files
1. After creating the repo, click **"uploading an existing file"**
2. Open this folder in your file manager: `/media/meskat/01D328FD008B4340/Bangla PDF Editor/github_upload/`
3. **SELECT ALL** files and folders in this directory (Ctrl+A)
4. **DRAG AND DROP** them into the GitHub upload area
5. Wait for upload to complete (should be fast - only 155KB)
6. Commit message: `Initial commit - Bangla PDF Editor`
7. Click **"Commit changes"**

## Your Repository Link Will Be:
```
https://github.com/meskat777/bangla-pdf-editor
```

## Message for Gemini:
After uploading, send this to Gemini:

```
I need help fixing an ANSI font positioning bug in my Bangla PDF Editor.

Repository: https://github.com/meskat777/bangla-pdf-editor

ISSUE: Edit boxes appear 13px ABOVE the actual text for ANSI/Bijoy fonts (SutonnyMJ).
- Unicode PDFs: ✅ Perfect alignment
- ANSI PDFs: ❌ Boxes float above text

KEY FILES:
- backend/utils/pdf_processor.py (lines 68-120) - bbox correction
- frontend/static/js/app.js (lines 328-344) - UI rendering

MYSTERY: Backend logs confirm bbox IS corrected (+13.1px shift), but the UI still shows 
misalignment. The corrected bbox doesn't seem to reach the frontend properly.

Can you identify where the corrected bbox data is getting lost between backend and frontend?
```
