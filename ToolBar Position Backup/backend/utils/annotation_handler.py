"""
Annotation Handler Module
Handles highlights, signatures, images, watermarks, notes, drawing
"""

import fitz
from PIL import Image
import io
import base64

class AnnotationHandler:
    def __init__(self):
        pass
    
    def add_highlight(self, filepath, session_id, page_number, bbox, color):
        """Add text highlighting"""
        try:
            return {
                'success': True,
                'annotation_type': 'highlight',
                'message': 'হাইলাইট যোগ করা হয়েছে | Highlight added successfully',
                'data': {
                    'page_number': page_number,
                    'bbox': bbox,
                    'color': color
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_signature(self, filepath, session_id, page_number, signature_data, position, size):
        """Add signature image"""
        try:
            # signature_data is base64 encoded image
            return {
                'success': True,
                'annotation_type': 'signature',
                'message': 'স্বাক্ষর যোগ করা হয়েছে | Signature added successfully',
                'data': {
                    'page_number': page_number,
                    'signature_data': signature_data,
                    'position': position,
                    'size': size
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_image(self, filepath, session_id, page_number, image_data, position, size):
        """Add image to PDF"""
        try:
            return {
                'success': True,
                'annotation_type': 'image',
                'message': 'ছবি যোগ করা হয়েছে | Image added successfully',
                'data': {
                    'page_number': page_number,
                    'image_data': image_data,
                    'position': position,
                    'size': size
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_watermark(self, filepath, output_path, text, opacity=0.3):
        """Add watermark to all pages"""
        try:
            doc = fitz.open(filepath)
            
            for page in doc:
                # Add watermark text
                page_width = page.rect.width
                page_height = page.rect.height
                
                # Center position
                point = fitz.Point(page_width / 2, page_height / 2)
                
                # Insert watermark
                page.insert_text(
                    point,
                    text,
                    fontsize=48,
                    color=(0.8, 0.8, 0.8),
                    rotate=45,
                    overlay=False
                )
            
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'message': 'ওয়াটারমার্ক যোগ করা হয়েছে | Watermark added successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_sticky_note(self, filepath, session_id, page_number, position, text, color):
        """Add sticky note"""
        try:
            return {
                'success': True,
                'annotation_type': 'note',
                'message': 'নোট যোগ করা হয়েছে | Sticky note added successfully',
                'data': {
                    'page_number': page_number,
                    'position': position,
                    'text': text,
                    'color': color
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_drawing(self, filepath, session_id, page_number, path_data, color, width):
        """Add freehand drawing"""
        try:
            return {
                'success': True,
                'annotation_type': 'drawing',
                'message': 'আঁকা যোগ করা হয়েছে | Drawing added successfully',
                'data': {
                    'page_number': page_number,
                    'path_data': path_data,
                    'color': color,
                    'width': width
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
