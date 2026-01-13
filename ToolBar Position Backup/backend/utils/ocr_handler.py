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
            
            # Process results
            ocr_results = []
            for idx, (bbox, text, confidence) in enumerate(results):
                # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                # Scale back from 2x zoom
                x0, y0 = min(x_coords) / 2, min(y_coords) / 2
                x1, y1 = max(x_coords) / 2, max(y_coords) / 2
                
                ocr_results.append({
                    'id': f'ocr_{page_number}_{idx}',
                    'text': text,
                    'confidence': float(confidence),
                    'bbox': [x0, y0, x1, y1],
                    'language': self._detect_language(text)
                })
            
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
    
    def enhance_image_for_ocr(self, image):
        """Enhance image quality for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            image = np.mean(image, axis=2).astype(np.uint8)
        
        # Apply basic preprocessing
        # You can add more sophisticated preprocessing here
        return image
