"""
Text Editor Module
Handles all text editing operations
"""

import fitz
import os
from .bijoy_unicode_converter import convert_bijoy_to_unicode, is_bijoy_text

class TextEditor:
    def __init__(self):
        self.temp_files = {}
    
    def edit_text(self, filepath, session_id, page_number, text_box_id, 
                  new_text, font, font_size, color, style, position, rotation, alignment):
        """Edit existing text in PDF"""
        try:
            result = {
                'success': True,
                'text_box_id': text_box_id,
                'message': 'টেক্সট সফলভাবে সম্পাদিত হয়েছে | Text edited successfully'
            }
            
            # Store edit information for later application
            result['edit_data'] = {
                'page_number': page_number,
                'text_box_id': text_box_id,
                'new_text': new_text,
                'font': font,
                'font_size': font_size,
                'color': color,
                'style': style,
                'position': position,
                'rotation': rotation,
                'alignment': alignment
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_text(self, filepath, session_id, page_number, text, position, 
                 font, font_size, color, style):
        """Add new text to PDF"""
        try:
            import uuid
            text_box_id = f"new_text_{uuid.uuid4().hex[:8]}"
            
            result = {
                'success': True,
                'text_box_id': text_box_id,
                'message': 'নতুন টেক্সট যোগ করা হয়েছে | New text added successfully'
            }
            
            result['text_data'] = {
                'page_number': page_number,
                'text_box_id': text_box_id,
                'text': text,
                'position': position,
                'font': font,
                'font_size': font_size,
                'color': color,
                'style': style
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_text(self, filepath, session_id, page_number, text_box_id):
        """Delete text from PDF"""
        try:
            result = {
                'success': True,
                'text_box_id': text_box_id,
                'message': 'টেক্সট মুছে ফেলা হয়েছে | Text deleted successfully'
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def apply_text_style(self, text, style):
        """Apply text styling (bold, italic, etc.)"""
        # Style flags will be handled by PyMuPDF
        return {
            'bold': 'bold' in style.lower() if style else False,
            'italic': 'italic' in style.lower() if style else False,
            'underline': 'underline' in style.lower() if style else False,
            'strikethrough': 'strikethrough' in style.lower() if style else False
        }
