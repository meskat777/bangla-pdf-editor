"""
Page Manager Module
Handles page operations: add, delete, rotate, extract, arrange
"""

import fitz
import os

class PageManager:
    def __init__(self):
        pass
    
    def add_page(self, filepath, output_path, page_number=-1, page_size=(595, 842)):
        """Add a blank page to PDF"""
        try:
            doc = fitz.open(filepath)
            
            # Insert blank page
            if page_number == -1:
                page_number = doc.page_count
            
            doc.new_page(page_number, width=page_size[0], height=page_size[1])
            
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'message': 'নতুন পৃষ্ঠা যোগ করা হয়েছে | New page added successfully',
                'page_number': page_number
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_page(self, filepath, output_path, page_number):
        """Delete a page from PDF"""
        try:
            doc = fitz.open(filepath)
            
            if page_number < 0 or page_number >= doc.page_count:
                return {'success': False, 'error': 'Invalid page number'}
            
            doc.delete_page(page_number)
            
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'message': 'পৃষ্ঠা মুছে ফেলা হয়েছে | Page deleted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rotate_page(self, filepath, output_path, page_number, rotation):
        """Rotate a page (90, 180, 270 degrees)"""
        try:
            doc = fitz.open(filepath)
            page = doc[page_number]
            
            page.set_rotation(rotation)
            
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'message': 'পৃষ্ঠা ঘোরানো হয়েছে | Page rotated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def duplicate_page(self, filepath, output_path, page_number):
        """Duplicate a page"""
        try:
            doc = fitz.open(filepath)
            
            if page_number < 0 or page_number >= doc.page_count:
                return {'success': False, 'error': 'Invalid page number'}
            
            # Copy page
            doc.copy_page(page_number, page_number + 1)
            
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'message': 'পৃষ্ঠা অনুলিপি করা হয়েছে | Page duplicated successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_pages(self, filepath, output_path, page_range):
        """Extract specific pages to new PDF"""
        try:
            doc = fitz.open(filepath)
            new_doc = fitz.open()
            
            for page_num in page_range:
                if 0 <= page_num < doc.page_count:
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return {
                'success': True,
                'message': 'পৃষ্ঠা নিষ্কাশন সফল হয়েছে | Pages extracted successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rearrange_pages(self, filepath, output_path, page_order):
        """Rearrange pages in specified order"""
        try:
            doc = fitz.open(filepath)
            new_doc = fitz.open()
            
            for page_num in page_order:
                if 0 <= page_num < doc.page_count:
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return {
                'success': True,
                'message': 'পৃষ্ঠা পুনর্বিন্যাস করা হয়েছে | Pages rearranged successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
