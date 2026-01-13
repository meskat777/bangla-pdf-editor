# Context for Gemini: Bangla PDF Editor - Word-Level Precision Editing Issue

## Problem Summary

I'm building a web-based PDF editor using Python (Flask backend) and Vanilla JavaScript frontend. I have implemented Gemini's previous recommendations but still facing issues.

---

## Current Implementation Status

### ✅ What's Working:
1. **Word-Level Extraction** - Using `page.get_text("words")` from PyMuPDF
2. **Precision Redaction** - Using `page.add_redact_annot(word_rect)` to remove only target word
3. **Unicode→Bijoy Conversion** - Created comprehensive mapping table
4. **Font Detection** - Automatically detects Bijoy vs Unicode fonts
5. **Text Insertion** - Using `insert_textbox()` with `render_mode=0`

### ❌ What's NOT Working:
- **Edited text is inserted but NOT VISIBLE** in the PDF
- Neighboring text IS preserved (word-level precision working)
- Text exists in PDF (can be extracted with `get_text()`)
- But visually invisible/not rendered

---

## Current Code

### 1. Word Extraction (WORKING)
```python
# File: backend/utils/pdf_processor.py - Line ~45

# GEMINI SOLUTION: Use get_text("words") for precise word-level bboxes
words = page.get_text("words")

for word_idx, word_tuple in enumerate(words):
    x0, y0, x1, y1, word_text, block_no, line_no, word_no = word_tuple
    
    # Get original font styles for this specific word
    word_rect = fitz.Rect(x0, y0, x1, y1)
    try:
        text_dict = page.get_text("dict", clip=word_rect)
        span = text_dict["blocks"][0]["lines"][0]["spans"][0]
        font_name = span.get("font", "")
        font_size = span.get("size", 12)
        font_color = span.get("color", 0)
        flags = span.get("flags", 0)
    except (IndexError, KeyError):
        font_name = ""
        font_size = 12
        font_color = 0
        flags = 0
    
    text_block = {
        'id': f"word_{page_num}_{word_idx}",
        'text': word_text,
        'font': font_name,
        'size': round(font_size, 2),
        'color': self._rgb_to_hex(font_color),
        'flags': flags,
        'bbox': [x0, y0, x1, y1],  # Precise word-level bbox
        'origin': (x0, y1),
        'bold': bool(flags & 2**4),
        'italic': bool(flags & 2**1),
        'is_word': True
    }
    page_data['text_blocks'].append(text_block)
```

### 2. Text Editing (PROBLEM HERE - Text Not Visible)
```python
# File: backend/utils/pdf_processor.py - Line ~260

def apply_edit_immediately(self, input_path, page_num, bbox, original_text, new_text, font_name, font_size, color, position):
    """
    GEMINI METHOD: Replace word with precision
    ISSUE: Text inserted but NOT VISIBLE
    """
    try:
        doc = fitz.open(input_path)
        page = doc[page_num]
        
        color_rgb = self._hex_to_rgb(color)
        
        if bbox and len(bbox) == 4:
            word_rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
            
            logger.info(f"[GEMINI METHOD] Replacing word: '{original_text}' -> '{new_text}'")
            
            # STEP 1: Get original font properties
            try:
                text_dict = page.get_text("dict", clip=word_rect)
                span = text_dict["blocks"][0]["lines"][0]["spans"][0]
                original_font_size = span.get("size", font_size)
                original_color = span.get("color", 0)
                
                if font_size == 12:
                    font_size = original_font_size
                if color == '#000000':
                    color_rgb = self._hex_to_rgb(self._rgb_to_hex(original_color))
            except (IndexError, KeyError):
                logger.warning("Could not extract original font properties")
            
            # STEP 2: PRECISION REDACTION (WORKING - removes only target word)
            page.add_redact_annot(word_rect, fill=(1, 1, 1))
            page.apply_redactions()
            logger.info(f"✓ Applied precision redaction")
            
            # STEP 3: DETECT BIJOY FONT AND CONVERT IF NEEDED
            is_bengali = any('\u0980' <= c <= '\u09FF' for c in new_text)
            is_bijoy_font = font_name and any(bijoy_name in font_name.lower() for bijoy_name in 
                ['sutonnymj', 'sushree', 'solaimanlpi', 'nikosh'])
            
            font_path = None
            if font_name:
                font_path = self._get_font_path(font_name)
            
            # Convert Unicode → Bijoy if needed
            text_to_insert = new_text
            if is_bengali and is_bijoy_font:
                from backend.utils.unicode_to_bijoy_converter import unicode_to_bijoy
                text_to_insert = unicode_to_bijoy(new_text)
                logger.info(f"✓ Converted Unicode→Bijoy: '{new_text}' → '{text_to_insert}'")
            
            # STEP 4: INSERT TEXT (PROBLEM - NOT VISIBLE!)
            try:
                rc = page.insert_textbox(
                    word_rect,
                    text_to_insert,
                    fontsize=font_size,
                    fontfile=font_path,
                    color=color_rgb,
                    align=fitz.TEXT_ALIGN_LEFT,
                    render_mode=0  # 0=fill (normal), ensures visibility
                )
                
                if rc >= 0:
                    logger.info(f"✓ insert_textbox succeeded (code: {rc})")
                else:
                    raise Exception(f"Text overflow (code: {rc})")
                    
            except Exception as e:
                logger.warning(f"insert_textbox failed: {e}. Using fallback.")
                
                # FALLBACK: insert_text
                insert_point = fitz.Point(word_rect.x0, word_rect.y1)
                
                if font_path and os.path.exists(font_path):
                    page.insert_text(
                        point=insert_point,
                        text=text_to_insert,
                        fontsize=font_size,
                        fontfile=font_path,
                        color=color_rgb,
                        render_mode=0
                    )
                else:
                    page.insert_text(
                        point=insert_point,
                        text=text_to_insert,
                        fontsize=font_size,
                        fontname='helv',
                        color=color_rgb,
                        render_mode=0
                    )
                logger.info(f"✓ insert_text fallback used")
            
            # STEP 5: SAVE
            doc.save(input_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            doc.close()
            
            logger.info(f"✓ COMPLETE - Neighboring text preserved")
            
        return True
    except Exception as e:
        raise Exception(f"Error applying edit: {str(e)}")
```

### 3. Unicode to Bijoy Converter (WORKING)
```python
# File: backend/utils/unicode_to_bijoy_converter.py

class UnicodeToBijoyConverter:
    def __init__(self):
        self.unicode_to_bijoy_map = {
            'আ': 'Av', 'ক': 'K', 'ম': 'g', 'ি': 'w',
            'ক্ষ': '±', 'ত্র': '°', 'ক্র': '²',
            # ... comprehensive mapping table
        }
    
    def convert(self, unicode_text):
        # Converts "আমি" → "Avgw" for Bijoy fonts
        result = []
        i = 0
        while i < len(unicode_text):
            # Try 3-char, 2-char, then 1-char matches
            if i + 2 < len(unicode_text):
                three_char = unicode_text[i:i+3]
                if three_char in self.unicode_to_bijoy_map:
                    result.append(self.unicode_to_bijoy_map[three_char])
                    i += 3
                    continue
            # ... similar for 2-char and 1-char
        return ''.join(result)
```

---

## Test Results

### What I've Verified:
1. ✅ **Word extraction works** - 21 individual words extracted (not lines)
2. ✅ **Redaction works** - Only target word removed, neighbors preserved
3. ✅ **Conversion works** - "আমি" → "Avgw" correctly
4. ✅ **Text exists** - `page.get_text()` shows "REPLACED" in the PDF
5. ❌ **Text NOT VISIBLE** - PDF viewers show blank space where text should be

### Logs Show:
```
[GEMINI METHOD] Replacing word: 'World' -> 'REPLACED'
Word bbox: [132.0, 84.9, 166.7, 104.2]
✓ Applied precision redaction
✓ insert_textbox succeeded (code: 0)
✓ Inserted new text: 'REPLACED'
✓ COMPLETE - Neighboring text preserved
```

But visually: The PDF shows "Hello _______ Test" (blank where REPLACED should be)

---

## Environment

- **OS:** Ubuntu 24.04
- **Python:** 3.12
- **PyMuPDF (fitz):** 1.23.5
- **Backend:** Flask 2.3.3
- **Frontend:** Vanilla JavaScript

---

## Files Structure

```
backend/
├── app.py                          # Flask routes
├── utils/
│   ├── pdf_processor.py            # Main processing (ISSUE HERE)
│   ├── unicode_to_bijoy_converter.py  # Converter (working)
│   └── bijoy_unicode_converter.py  # Reverse converter
frontend/
├── static/js/app.js                # Client-side code
└── templates/index.html            # UI
```

---

## Questions for Gemini

1. **Why is inserted text invisible?**
   - `render_mode=0` should make it visible
   - Text exists in PDF structure
   - But not rendered visually

2. **Is there something wrong with:**
   - The redaction approach?
   - The text insertion after redaction?
   - Font file handling?
   - PDF save method?

3. **Alternative approaches?**
   - Should I modify the PDF content stream directly?
   - Use different PyMuPDF methods?
   - Different workflow entirely?

4. **For Bijoy fonts specifically:**
   - Is the Unicode→Bijoy conversion correct?
   - Should I handle font embedding differently?
   - Any special considerations?

---

## What I Need

A solution to make the inserted text **VISIBLE** while:
- ✅ Keeping word-level precision (working)
- ✅ Keeping neighbor preservation (working)
- ✅ Supporting both Unicode and Bijoy fonts
- ✅ Working in print preview

Please provide specific PyMuPDF code examples if possible.

---

## Additional Context

- **Previous attempt:** Used `draw_rect()` to cover text - same issue
- **Previous attempt:** Used `search_for()` to find text - didn't help visibility
- **Previous attempt:** Tried different `render_mode` values - no change
- **Font paths:** Using absolute paths as recommended
- **Incremental save:** Using `incremental=True` to preserve structure

Thank you for your help!
