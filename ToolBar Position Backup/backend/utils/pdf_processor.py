"""
PDF Processing Module
Handles PDF loading, rendering, and text extraction
"""

import fitz  # PyMuPDF
import base64
from io import BytesIO
from PIL import Image
import os

class PDFProcessor:
    def __init__(self, config):
        self.config = config
        self.custom_fonts = {}
        self._load_custom_fonts()
        
    def process_pdf(self, filepath, session_id):
        """Process PDF and extract all text elements with metadata"""
        try:
            doc = fitz.open(filepath)
            pdf_data = {
                'num_pages': doc.page_count,
                'pages': [],
                'metadata': doc.metadata
            }
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_data = {
                    'page_number': page_num,
                    'width': page.rect.width,
                    'height': page.rect.height,
                    'text_blocks': [],
                    'images': [],
                    'has_text': False
                }
                
                # Extract text blocks with formatting
                blocks = page.get_text("dict")["blocks"]
                
                for block_idx, block in enumerate(blocks):
                    if "lines" in block:  # Text block
                        page_data['has_text'] = True
                        for line_idx, line in enumerate(block["lines"]):
                            for span_idx, span in enumerate(line["spans"]):
                                text_block = {
                                    'id': f"text_{page_num}_{block_idx}_{line_idx}_{span_idx}",
                                    'text': span["text"],
                                    'font': span["font"],
                                    'size': round(span["size"], 2),
                                    'color': self._rgb_to_hex(span["color"]),
                                    'flags': span["flags"],  # Bold, italic info
                                    'bbox': span["bbox"],  # [x0, y0, x1, y1]
                                    'origin': span["origin"],
                                    'bold': bool(span["flags"] & 2**4),
                                    'italic': bool(span["flags"] & 2**1),
                                }
                                page_data['text_blocks'].append(text_block)
                    
                    elif "image" in block:  # Image block
                        page_data['images'].append({
                            'id': f"img_{page_num}_{block_idx}",
                            'bbox': block["bbox"],
                            'width': block.get("width", 0),
                            'height': block.get("height", 0)
                        })
                
                pdf_data['pages'].append(page_data)
            
            doc.close()
            return pdf_data
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def render_page(self, filepath, page_number, zoom=1.0):
        """Render a page as base64 encoded image"""
        try:
            doc = fitz.open(filepath)
            page = doc[page_number]
            
            # Render page to pixmap
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PNG
            img_data = pix.tobytes("png")
            
            # Convert to base64
            base64_data = base64.b64encode(img_data).decode('utf-8')
            
            doc.close()
            
            return f"data:image/png;base64,{base64_data}"
            
        except Exception as e:
            raise Exception(f"Error rendering page: {str(e)}")
    
    def save_pdf(self, input_path, output_path, modifications):
        """Apply all modifications and save PDF"""
        try:
            doc = fitz.open(input_path)
            
            # Group modifications by type and apply
            for mod in modifications:
                mod_type = mod['type']
                mod_data = mod['data']
                page_num = mod_data.get('page_number', 0)
                
                if page_num >= doc.page_count:
                    continue
                
                page = doc[page_num]
                
                if mod_type == 'text_delete':
                    # Delete original text using redaction
                    bbox = mod_data.get('bbox')
                    if bbox:
                        rect = fitz.Rect(bbox[0] - 1, bbox[1] - 1, bbox[2] + 1, bbox[3] + 1)
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                
                elif mod_type == 'text_edit':
                    # For text edit: redact old text, add new
                    bbox = mod_data.get('bbox')
                    if bbox:
                        # Redact (permanently remove) original text
                        rect = fitz.Rect(bbox[0] - 1, bbox[1] - 1, bbox[2] + 1, bbox[3] + 1)
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                        page.apply_redactions()
                    
                    # Add new text
                    text = mod_data.get('new_text')
                    position = mod_data.get('position', {})
                    font_name = mod_data.get('font', 'helv')
                    font_size = mod_data.get('font_size', 12)
                    color = self._hex_to_rgb(mod_data.get('color', '#000000'))
                    
                    # Insert new text at position
                    point = fitz.Point(position.get('x', 50), position.get('y', 50))
                    page.insert_text(
                        point,
                        text,
                        fontsize=font_size,
                        color=color,
                        fontname=font_name
                    )
                
                elif mod_type == 'text_add':
                    # Add new text only
                    text = mod_data.get('text')
                    position = mod_data.get('position', {})
                    font_name = mod_data.get('font', 'helv')
                    font_size = mod_data.get('font_size', 12)
                    color = self._hex_to_rgb(mod_data.get('color', '#000000'))
                    
                    # Insert text
                    point = fitz.Point(position.get('x', 50), position.get('y', 50))
                    page.insert_text(
                        point,
                        text,
                        fontsize=font_size,
                        color=color,
                        fontname=font_name
                    )
                
                elif mod_type == 'annotation':
                    # Add annotations
                    self._add_annotation(page, mod_data)
            
            # Save the modified PDF
            doc.save(output_path)
            doc.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error saving PDF: {str(e)}")
    
    def _load_custom_fonts(self):
        """Load custom fonts from fonts directory"""
        try:
            fonts_dir = self.config.get('FONTS_FOLDER', 'fonts')
            if os.path.exists(fonts_dir):
                for font_file in os.listdir(fonts_dir):
                    if font_file.lower().endswith(('.ttf', '.otf')):
                        font_path = os.path.join(fonts_dir, font_file)
                        font_name = os.path.splitext(font_file)[0]
                        self.custom_fonts[font_name] = font_path
        except Exception as e:
            print(f"Error loading custom fonts: {e}")
    
    def _get_font_for_text(self, font_name, text):
        """Get appropriate font for text, prioritizing custom fonts for Bengali"""
        # Check if text contains Bengali characters
        has_bengali = any('\u0980' <= c <= '\u09FF' for c in text)
        
        if has_bengali:
            # Try to find a matching custom Bengali font
            if font_name in self.custom_fonts:
                return ('custom', self.custom_fonts[font_name])
            
            # Try to find any Bengali font
            for name, path in self.custom_fonts.items():
                if any(keyword in name.lower() for keyword in ['kohinoor', 'bangla', 'bengali', 'solaiman', 'kalpurush']):
                    return ('custom', path)
        
        # Fallback to system font
        return ('system', font_name)
    
    def apply_edit_immediately(self, input_path, page_num, bbox, new_text, font_name, font_size, color, position):
        """Apply a single edit immediately and update the file"""
        try:
            doc = fitz.open(input_path)
            page = doc[page_num]
            
            # NEW APPROACH: Redact (permanently remove) the original text
            if bbox:
                # Create redaction annotation to remove text
                rect = fitz.Rect(bbox[0] - 1, bbox[1] - 1, bbox[2] + 1, bbox[3] + 1)
                page.add_redact_annot(rect, fill=(1, 1, 1))  # White fill
                # Apply all redactions
                page.apply_redactions()
            
            # Add new text with proper font handling
            color_rgb = self._hex_to_rgb(color)
            
            # Use bbox position for more accurate placement
            # Position text at the baseline (bottom-left of bbox)
            if bbox:
                # Use the original bbox position for accurate placement
                x_pos = bbox[0]
                y_pos = bbox[3]  # Bottom of bbox (baseline for text)
            else:
                x_pos = position.get('x', 50)
                y_pos = position.get('y', 50)
            
            point = fitz.Point(x_pos, y_pos)
            
            # Get appropriate font
            font_type, font_ref = self._get_font_for_text(font_name, new_text)
            
            if font_type == 'custom':
                # Use custom font file
                try:
                    # Insert text with custom font
                    fontbuffer = open(font_ref, "rb").read()
                    page.insert_text(
                        point,
                        new_text,
                        fontsize=font_size,
                        color=color_rgb,
                        fontfile=font_ref
                    )
                except Exception as e:
                    print(f"Error with custom font, using fallback: {e}")
                    # Fallback to system font
                    page.insert_text(
                        point,
                        new_text,
                        fontsize=font_size,
                        color=color_rgb,
                        fontname='helv'
                    )
            else:
                # Use system font
                page.insert_text(
                    point,
                    new_text,
                    fontsize=font_size,
                    color=color_rgb,
                    fontname=font_ref if font_ref else 'helv'
                )
            
            # Save back to same file
            doc.save(input_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            doc.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error applying edit: {str(e)}")
    
    def _rgb_to_hex(self, rgb_int):
        """Convert RGB integer to hex color"""
        try:
            r = (rgb_int >> 16) & 0xFF
            g = (rgb_int >> 8) & 0xFF
            b = rgb_int & 0xFF
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#000000"
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple (0-1 range)"""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            return (r, g, b)
        except:
            return (0, 0, 0)
    
    def _add_annotation(self, page, data):
        """Add annotation to page"""
        annotation_type = data.get('annotation_type')
        
        if annotation_type == 'highlight':
            bbox = data.get('bbox')
            if bbox:
                highlight = page.add_highlight_annot(bbox)
                highlight.update()
        
        elif annotation_type == 'note':
            position = data.get('position')
            text = data.get('text')
            if position:
                point = fitz.Point(position['x'], position['y'])
                page.add_text_annot(point, text)
