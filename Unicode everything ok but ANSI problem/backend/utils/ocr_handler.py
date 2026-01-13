"""
OCR Handler Module
Uses EasyOCR for text detection and recognition
"""

import easyocr
import fitz
from PIL import Image
import numpy as np
import os

class OCRHandler:
    def __init__(self):
        # Initialize EasyOCR reader for Bengali and English
        self.reader = easyocr.Reader(['bn', 'en'], gpu=False)
        
    def detect_text(self, pdf_path, page_number):
        """Detect text using OCR on a specific page"""
        try:
            # Open PDF and get page
            doc = fitz.open(pdf_path)
            page = doc[page_number]
            
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Run OCR
            results = self.reader.readtext(img_array, detail=1)
            
            # Process results - WORD-LEVEL SEGMENTATION
            ocr_results = []
            word_idx = 0
            
            for idx, (bbox, text, confidence) in enumerate(results):
                # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                # Scale back from 2x zoom
                x0, y0 = min(x_coords) / 2, min(y_coords) / 2
                x1, y1 = max(x_coords) / 2, max(y_coords) / 2
                
                # STEP 1: WORD-LEVEL BOUNDING BOX SEGMENTATION
                # Split text into individual words
                words = text.split()
                
                if len(words) <= 1:
                    # Single word or empty - add as is
                    ocr_results.append({
                        'id': f'ocr_{page_number}_{word_idx}',
                        'text': text,
                        'confidence': float(confidence),
                        'bbox': [x0, y0, x1, y1],
                        'language': self._detect_language(text),
                        'is_word': True
                    })
                    word_idx += 1
                else:
                    # Multiple words - estimate individual word bounding boxes
                    line_width = x1 - x0
                    total_chars = sum(len(w) for w in words)
                    char_width = line_width / total_chars if total_chars > 0 else 0
                    
                    current_x = x0
                    for word in words:
                        word_width = len(word) * char_width
                        
                        # Create individual word bbox
                        word_bbox = [
                            current_x,
                            y0,
                            current_x + word_width,
                            y1
                        ]
                        
                        ocr_results.append({
                            'id': f'ocr_{page_number}_{word_idx}',
                            'text': word,
                            'confidence': float(confidence),
                            'bbox': word_bbox,
                            'language': self._detect_language(word),
                            'is_word': True,
                            'parent_line': idx  # Reference to original line
                        })
                        
                        current_x += word_width + char_width  # Add space width
                        word_idx += 1
            
            doc.close()
            return ocr_results
            
        except Exception as e:
            raise Exception(f"OCR detection error: {str(e)}")
    
    def _detect_language(self, text):
        """Detect if text is Bengali or English"""
        # Check for Bengali characters (Unicode range)
        bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        if bengali_chars > len(text) / 2:
            return 'bn'
        return 'en'
    
    @staticmethod
    def scale_coordinates_to_pdf(browser_coords, display_width, display_height, pdf_width, pdf_height):
        """
        STEP 3: HIGH-RESOLUTION COORDINATE MAPPING
        Convert Browser UI Pixels to PDF Points
        
        Scale = Original_PDF_Width / Displayed_Image_Width
        PDF_x = Browser_x * Scale
        PDF_y = Browser_y * Scale
        """
        scale_x = pdf_width / display_width
        scale_y = pdf_height / display_height
        
        return {
            'x': browser_coords['x'] * scale_x,
            'y': browser_coords['y'] * scale_y,
            'width': browser_coords.get('width', 0) * scale_x,
            'height': browser_coords.get('height', 0) * scale_y,
            'scale_x': scale_x,
            'scale_y': scale_y
        }
    
    @staticmethod
    def scale_coordinates_to_browser(pdf_coords, display_width, display_height, pdf_width, pdf_height):
        """
        Convert PDF Points to Browser UI Pixels (inverse operation)
        """
        scale_x = display_width / pdf_width
        scale_y = display_height / pdf_height
        
        return {
            'x': pdf_coords['x'] * scale_x,
            'y': pdf_coords['y'] * scale_y,
            'width': pdf_coords.get('width', 0) * scale_x,
            'height': pdf_coords.get('height', 0) * scale_y
        }
    
    @staticmethod
    def scale_font_size(browser_font_size, pdf_scale):
        """
        Scale font size from browser to PDF coordinates
        Ensures text fits perfectly in original word's footprint
        """
        return browser_font_size * pdf_scale
    
    def enhance_image_for_ocr(self, image):
        """Enhance image quality for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            image = np.mean(image, axis=2).astype(np.uint8)
        
        # Apply basic preprocessing
        # You can add more sophisticated preprocessing here
        return image
