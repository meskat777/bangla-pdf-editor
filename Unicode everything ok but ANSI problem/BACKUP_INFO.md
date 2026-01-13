# Backup: Unicode everything ok but ANSI problem

**Date:** 2026-01-13 10:10:00

## Status

✅ **Working Features:**
- Unicode PDF editing works perfectly
- Edit boxes appear in correct positions for Unicode PDFs
- Download button fixed and working
- Close button added and working
- Save functionality working with absolute paths

❌ **Known Issue:**
- **ANSI/Bijoy PDF edit boxes appear in wrong positions**
- The problem is in text extraction phase (lines 40-84 in pdf_processor.py)
- `page.get_text("words")` returns incorrect bbox coordinates for ANSI fonts
- PyMuPDF misinterprets ANSI/Bijoy character encoding

## Technical Details

### Root Cause:
- PyMuPDF's `page.get_text("words")` correctly extracts bbox for Unicode fonts
- For ANSI/Bijoy fonts, it returns wrong coordinates
- The positioning method itself is identical for both types
- Input data (bbox) is incorrect for ANSI fonts

### Method Used:
- **GEMINI METHOD:** Precision Word Replacement with Image Overlay
- Unicode → Bijoy conversion implemented
- Text rendered as transparent PNG image
- Redaction + image insertion approach

## Files Backed Up:
- backend/ (complete)
- frontend/ (complete)
- config.py
- requirements.txt
- run.py

## Next Steps:
Need to fix bbox extraction for ANSI fonts in `process_pdf()` method.
