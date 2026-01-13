"""
Test script to analyze ANSI vs Unicode bbox extraction
"""
import fitz
import sys

def analyze_pdf_text_extraction(pdf_path):
    """Analyze how PyMuPDF extracts text from ANSI/Bijoy vs Unicode PDFs"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {pdf_path}")
    print(f"{'='*80}\n")
    
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    print(f"Page dimensions: {page.rect.width} x {page.rect.height}")
    
    # Method 1: get_text("words")
    print("\n[METHOD 1] get_text('words') - Standard extraction:")
    words = page.get_text("words")
    for i, word in enumerate(words[:5]):  # First 5 words
        x0, y0, x1, y1, text, block_no, line_no, word_no = word
        print(f"  Word {i}: '{text}'")
        print(f"    bbox: [{x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f}]")
        print(f"    width: {x1-x0:.1f}, height: {y1-y0:.1f}")
        
        # Check character encoding
        print(f"    chars: {[f'{c}(U+{ord(c):04X})' for c in text[:3]]}")
        
        # Get detailed info for this word
        try:
            word_rect = fitz.Rect(x0, y0, x1, y1)
            text_dict = page.get_text("dict", clip=word_rect)
            span = text_dict["blocks"][0]["lines"][0]["spans"][0]
            font_name = span.get("font", "")
            font_size = span.get("size", 0)
            
            print(f"    font: {font_name}, size: {font_size:.1f}")
            
            # Detect if Bijoy/ANSI font
            is_bijoy = any(name in font_name.lower() for name in 
                ['sutonnymj', 'sushree', 'solaimanlpi', 'nikosh', 'kalpurush'])
            print(f"    is_bijoy: {is_bijoy}")
        except:
            print(f"    (could not get font info)")
    
    # Method 2: get_text("rawdict") for raw PDF data
    print("\n[METHOD 2] get_text('rawdict') - Raw PDF structure:")
    try:
        raw_dict = page.get_text("rawdict")
        if raw_dict.get("blocks"):
            first_block = raw_dict["blocks"][0]
            if first_block.get("lines"):
                first_line = first_block["lines"][0]
                if first_line.get("spans"):
                    first_span = first_line["spans"][0]
                    print(f"  Raw span data:")
                    print(f"    bbox: {first_span.get('bbox')}")
                    print(f"    font: {first_span.get('font')}")
                    print(f"    text: {first_span.get('text')}")
                    print(f"    chars: {first_span.get('chars', [])[:3]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Method 3: Check font encoding
    print("\n[METHOD 3] Font Analysis:")
    try:
        fonts = page.get_fonts()
        print(f"  Total fonts: {len(fonts)}")
        for font in fonts[:3]:
            xref, name, ftype, encoding = font[:4]
            print(f"    {name}: type={ftype}, encoding={encoding}")
            
            # Check if it's a Bijoy font
            is_ansi = encoding == '' or encoding == 'Ansi'
            print(f"      ANSI font: {is_ansi}")
    except Exception as e:
        print(f"  Error: {e}")
    
    doc.close()

if __name__ == "__main__":
    # Test with uploaded PDFs
    import os
    
    test_files = []
    
    # Find test PDFs
    if os.path.exists("backend/uploads"):
        files = [f for f in os.listdir("backend/uploads") if f.endswith('.pdf')]
        if files:
            test_files.append(os.path.join("backend/uploads", files[0]))
    
    if os.path.exists("test.pdf"):
        test_files.append("test.pdf")
    
    if not test_files:
        print("No PDF files found to test")
        sys.exit(1)
    
    for pdf_path in test_files[:2]:  # Test first 2 PDFs
        analyze_pdf_text_extraction(pdf_path)
