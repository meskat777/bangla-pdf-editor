"""
Document Operations Module
Handles PDF merge, split, export operations
"""

import fitz
import os
from PIL import Image

class DocumentOperations:
    def __init__(self):
        pass
    
    def merge_pdfs(self, pdf_files, output_path):
        """Merge multiple PDFs into one"""
        try:
            result_doc = fitz.open()
            
            for pdf_file in pdf_files:
                doc = fitz.open(pdf_file)
                result_doc.insert_pdf(doc)
                doc.close()
            
            result_doc.save(output_path)
            result_doc.close()
            
            return {
                'success': True,
                'message': 'পিডিএফ একত্রিত করা হয়েছে | PDFs merged successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def split_pdf(self, filepath, output_dir, split_points):
        """Split PDF at specified pages"""
        try:
            doc = fitz.open(filepath)
            output_files = []
            
            # Add start and end points
            split_points = [0] + sorted(split_points) + [doc.page_count]
            
            for i in range(len(split_points) - 1):
                start = split_points[i]
                end = split_points[i + 1]
                
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
                
                output_file = os.path.join(output_dir, f"split_{i+1}.pdf")
                new_doc.save(output_file)
                new_doc.close()
                
                output_files.append(output_file)
            
            doc.close()
            
            return {
                'success': True,
                'message': 'পিডিএফ বিভক্ত করা হয়েছে | PDF split successfully',
                'output_files': output_files
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_to_images(self, filepath, output_dir, format='PNG', dpi=150):
        """Export PDF pages as images"""
        try:
            doc = fitz.open(filepath)
            output_files = []
            
            zoom = dpi / 72  # Standard PDF DPI is 72
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=mat)
                
                output_file = os.path.join(output_dir, f"page_{page_num + 1}.{format.lower()}")
                
                if format.upper() == 'PNG':
                    pix.save(output_file)
                else:
                    # Convert to PIL Image for JPEG
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.save(output_file, format)
                
                output_files.append(output_file)
            
            doc.close()
            
            return {
                'success': True,
                'message': f'পিডিএফ {format} তে রপ্তানি করা হয়েছে | PDF exported to {format} successfully',
                'output_files': output_files
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_to_html(self, filepath, output_path):
        """Export PDF to HTML"""
        try:
            doc = fitz.open(filepath)
            html_content = "<html><head><meta charset='utf-8'></head><body>"
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text("html")
                html_content += f"<div class='page' data-page='{page_num + 1}'>{text}</div>"
            
            html_content += "</body></html>"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            doc.close()
            
            return {
                'success': True,
                'message': 'পিডিএফ HTML তে রপ্তানি করা হয়েছে | PDF exported to HTML successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def save_session(self, session_data, session_path):
        """Save editing session"""
        try:
            import json
            
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'message': 'সেশন সংরক্ষিত হয়েছে | Session saved successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_session(self, session_path):
        """Load editing session"""
        try:
            import json
            
            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return {
                'success': True,
                'message': 'সেশন লোড করা হয়েছে | Session loaded successfully',
                'session_data': session_data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
