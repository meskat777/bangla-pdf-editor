"""
Diagnose why ANSI bbox correction is inconsistent
"""
import fitz
import sys

def diagnose_word_bbox(pdf_path, page_num=0):
    """Analyze a specific word's bbox extraction"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    print(f"Analyzing page {page_num}")
    print(f"Page size: {page.rect.width} x {page.rect.height}\n")
    
    # Get all words
    words = page.get_text("words")
    
    # Find a SutonnyMJ word to analyze
    for word in words[:10]:
        x0, y0, x1, y1, text, block_no, line_no, word_no = word
        word_rect = fitz.Rect(x0, y0, x1, y1)
        
        # Get font info
        try:
            text_dict = page.get_text("dict", clip=word_rect)
            span = text_dict["blocks"][0]["lines"][0]["spans"][0]
            font_name = span.get("font", "")
        except:
            font_name = ""
        
        is_bijoy = 'sutonnymj' in font_name.lower()
        
        if is_bijoy:
            print(f"=" * 80)
            print(f"ANALYZING WORD: '{text}'")
            print(f"Original bbox: [{x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f}]")
            print(f"Font: {font_name}")
            print(f"=" * 80)
            
            # Get rawdict data
            raw_dict = page.get_text("rawdict", clip=word_rect)
            
            if raw_dict.get("blocks"):
                for block_idx, block in enumerate(raw_dict["blocks"]):
                    print(f"\nBlock {block_idx}:")
                    if block.get("lines"):
                        for line_idx, line in enumerate(block["lines"]):
                            print(f"  Line {line_idx}:")
                            if line.get("spans"):
                                for span_idx, span in enumerate(line["spans"]):
                                    print(f"    Span {span_idx}:")
                                    print(f"      Font: {span.get('font')}")
                                    print(f"      Size: {span.get('size')}")
                                    print(f"      Bbox: {span.get('bbox')}")
                                    
                                    chars = span.get("chars", [])
                                    print(f"      Characters ({len(chars)} total):")
                                    for char_idx, char in enumerate(chars):
                                        origin = char.get("origin", [0, 0])
                                        bbox = char.get("bbox", [0, 0, 0, 0])
                                        c = char.get("c", "?")
                                        print(f"        [{char_idx}] '{c}' (U+{ord(c):04X})")
                                        print(f"             bbox: {bbox}")
                                        print(f"             origin: {origin}")
                                        print(f"             height: {bbox[3] - bbox[1]:.1f}")
            
            print("\n" + "=" * 80)
            
            # Only analyze first Bijoy word
            break
    
    doc.close()

if __name__ == "__main__":
    import os
    
    # Find uploaded PDF
    if os.path.exists("backend/uploads"):
        files = [f for f in os.listdir("backend/uploads") if f.endswith('.pdf')]
        if files:
            pdf_path = os.path.join("backend/uploads", files[0])
            diagnose_word_bbox(pdf_path)
        else:
            print("No PDF found")
    else:
        print("uploads folder not found")
