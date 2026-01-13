# Bangla PDF Editor - ANSI Font Issue Summary

## Problem
Edit boxes appear **above the actual text** (misaligned) for ANSI/Bijoy fonts (like SutonnyMJ).

## Current Status
- ✅ Unicode PDFs work perfectly
- ❌ ANSI/Bijoy PDFs have edit box position mismatch

## Key Files

### 1. Backend - PDF Processing
- `backend/utils/pdf_processor.py` - Lines 40-120 (text extraction and bbox correction)
- `backend/app.py` - Main Flask app

### 2. Frontend - Text Box Rendering  
- `frontend/static/js/app.js` - Lines 328-344 (createTextBox function)
- Uses bbox directly: `textBox.style.top = (y0 * scaleFactor) + 'px'`

## Root Cause Found
For ANSI fonts, PyMuPDF returns **wrong bbox Y coordinates**:
- PyMuPDF bbox: `[454.9, 58.0, 510.2, 76.0]`
- Character origin Y (correct baseline): `89.1`
- Should be: `[454.9, 71.1, 510.2, 89.1]` (+13.1px shift)

## Current Fix Attempted
Using character origin from rawdict to correct bbox (lines 76-119 in pdf_processor.py)
But still not working in the UI.

## Diagnostic Data
```python
Word: '‡Mvjvc-K'
Word bbox: [454.9, 58.0, 510.2, 76.0]
Char origin Y: 89.1
Needed correction: +13.1px down
```

The backend correction is being applied but frontend still shows boxes above text.
