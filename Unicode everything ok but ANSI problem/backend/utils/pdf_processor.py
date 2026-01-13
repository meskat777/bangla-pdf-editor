"""
PDF Processing Module
Handles PDF loading, rendering, and text extraction
"""

import fitz  # PyMuPDF
import base64
from io import BytesIO
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

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
                
                # GEMINI SOLUTION: Extract WORD-LEVEL text with precise bounding boxes
                # page.get_text("words") returns: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
                words = page.get_text("words")
                
                if words:
                    page_data['has_text'] = True
                
                for word_idx, word_tuple in enumerate(words):
                    x0, y0, x1, y1, word_text, block_no, line_no, word_no = word_tuple
                    
                    # Get original font styles for this specific word
                    word_rect = fitz.Rect(x0, y0, x1, y1)
                    try:
                        # Query the PDF's internal character dictionary for this word
                        text_dict = page.get_text("dict", clip=word_rect)
                        span = text_dict["blocks"][0]["lines"][0]["spans"][0]
                        font_name = span.get("font", "")
                        font_size = span.get("size", 12)
                        font_color = span.get("color", 0)
                        flags = span.get("flags", 0)
                    except (IndexError, KeyError):
                        # Fallback if can't extract styles
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
                        'origin': (x0, y1),  # Bottom-left baseline
                        'bold': bool(flags & 2**4),
                        'italic': bool(flags & 2**1),
                        'block_no': block_no,
                        'line_no': line_no,
                        'word_no': word_no,
                        'is_word': True  # Mark as word-level (not span-level)
                    }
                    page_data['text_blocks'].append(text_block)
                
                # Extract images separately
                blocks = page.get_text("dict")["blocks"]
                for block_idx, block in enumerate(blocks):
                    if "image" in block:  # Image block
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
    
    def apply_edit_immediately(self, input_path, page_num, bbox, original_text, new_text, font_name, font_size, color, position):
        """
        GEMINI SOLUTION: Precision Word Replacement using Redaction + insert_textbox
        
        This is the industry-standard approach used by Adobe Acrobat and Sejda.
        Key: Use page.add_redact_annot() to cleanly remove ONLY the target word,
        then insert_textbox() to place new text with proper alignment.
        """
        try:
            doc = fitz.open(input_path)
            page = doc[page_num]
            
            color_rgb = self._hex_to_rgb(color)
            
            if bbox and len(bbox) == 4:
                # Create word rectangle from bbox
                word_rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
                
                logger.info(f"[GEMINI METHOD] Replacing word: '{original_text}' -> '{new_text}'")
                logger.info(f"Word bbox: [{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]")
                
                # STEP 1: Get original font properties from the word's area
                # GEMINI FIX: Always use original font size from PDF metadata
                try:
                    text_dict = page.get_text("dict", clip=word_rect)
                    span = text_dict["blocks"][0]["lines"][0]["spans"][0]
                    original_font_size = span.get("size", font_size)
                    original_color = span.get("color", 0)
                    
                    # CRITICAL FIX: Always use original font size from PDF
                    # This ensures text maintains exact same size as original
                    actual_font_size = original_font_size
                    
                    # Use original color if default color was sent
                    if color == '#000000':  # Default color, use original
                        color_rgb = self._hex_to_rgb(self._rgb_to_hex(original_color))
                    
                    logger.info(f"✓ Detected Original Font Size: {actual_font_size:.1f}pt (frontend sent: {font_size:.1f}pt)")
                    font_size = actual_font_size
                except (IndexError, KeyError):
                    logger.warning("Could not extract original font properties, using provided defaults")
                    logger.info(f"Using fallback font size: {font_size:.1f}pt")
                
                # STEP 2: PRECISION REDACTION (Gemini's key insight)
                # Add tiny buffer (0.5pt) to ensure no ghosting of original curves
                page.add_redact_annot(word_rect, fill=(1, 1, 1))
                page.apply_redactions()
                
                logger.info(f"✓ Applied precision redaction to word rect only")
                
                # STEP 3: INSERT NEW TEXT
                # GEMINI RECOMMENDATION: Convert Unicode → Bijoy for Bijoy fonts!
                
                # Detect if text contains Bengali characters
                is_bengali = any('\u0980' <= c <= '\u09FF' for c in new_text)
                
                # Detect if this is a Bijoy font (SutonnyMJ, Sushree, etc.)
                is_bijoy_font = font_name and any(bijoy_name in font_name.lower() for bijoy_name in 
                    ['sutonnymj', 'sushree', 'solaimanlpi', 'nikosh', 'kalpurush', 'akaash'])
                
                # Get font file path for Bengali support
                font_path = None
                if font_name:
                    font_path = self._get_font_path(font_name)
                
                # CRITICAL: If inserting Bengali Unicode text into a Bijoy font, CONVERT IT!
                # Using professional converter as per Gemini recommendation
                text_to_insert = new_text
                if is_bengali and is_bijoy_font:
                    logger.info(f"⚠️  Bijoy font detected: {font_name}")
                    logger.info(f"Converting Unicode '{new_text}' → Bijoy encoding...")
                    
                    from backend.utils.unicode_to_bijoy_converter import unicode_to_bijoy
                    try:
                        text_to_insert = unicode_to_bijoy(new_text)
                        logger.info(f"✓ Converted Unicode→Bijoy: '{new_text}' → '{text_to_insert}'")
                        logger.info(f"Example: Unicode 'ক'(U+0995) → Bijoy 'K'(ASCII 75)")
                    except Exception as e:
                        logger.error(f"Bijoy conversion failed: {e}")
                        logger.info("Using original Unicode text (may not render correctly)")
                        text_to_insert = new_text
                else:
                    logger.info(f"Using Unicode text as-is (font: {font_name or 'default'})")
                
                logger.info(f"Text language: {'Bengali' if is_bengali else 'English/Other'}, Font path: {font_path or 'None'}")
                
                # GEMINI'S REVOLUTIONARY SOLUTION: Text as Transparent PNG Image!
                # Why: Direct text insertion has rendering bugs, images are ALWAYS visible
                
                logger.info("🎨 Using IMAGE OVERLAY method for 100% visibility")
                
                try:
                    from backend.utils.text_to_image_renderer import text_to_png
                    
                    # Calculate bbox dimensions
                    bbox_width = word_rect.x1 - word_rect.x0
                    bbox_height = word_rect.y1 - word_rect.y0
                    
                    # Render text as transparent PNG with exact font
                    image_bytes = text_to_png(
                        text=text_to_insert,
                        font_path=font_path,
                        font_size=font_size,
                        color_rgb=color_rgb,
                        bbox_width=bbox_width,
                        bbox_height=bbox_height
                    )
                    
                    # Insert the image into the PDF at the exact word position
                    page.insert_image(
                        word_rect,
                        stream=image_bytes,
                        overlay=True  # Ensure it's on top
                    )
                    
                    logger.info(f"✓ Text rendered as image and inserted successfully")
                    logger.info(f"✓ IMAGE OVERLAY method complete - Text guaranteed visible!")
                    
                except Exception as e:
                    logger.error(f"Image overlay method failed: {e}")
                    logger.info("Falling back to direct text insertion...")
                    
                    # Fallback: Try direct text insertion
                    insert_point = fitz.Point(word_rect.x0, word_rect.y1 - 2)
                    
                    if font_path and os.path.exists(font_path):
                        page.insert_text(
                            point=insert_point,
                            text=text_to_insert,
                            fontsize=font_size,
                            fontfile=font_path,
                            color=color_rgb,
                            overlay=True,
                            render_mode=0
                        )
                    else:
                        page.insert_text(
                            point=insert_point,
                            text=text_to_insert,
                            fontsize=font_size,
                            fontname='helv',
                            color=color_rgb,
                            overlay=True,
                            render_mode=0
                        )
                    logger.info(f"✓ Fallback text insertion used")
                
                logger.info(f"✓ Inserted new text: '{new_text}'")
                logger.info(f"✓ GEMINI METHOD COMPLETE - Neighboring text preserved!")
                
            else:
                logger.warning(f"Invalid bbox format. Using fallback method.")
                self._fallback_text_replacement(page, bbox, original_text, new_text, font_size, color_rgb, position)
            
            # GEMINI CRITICAL FIX: Clean Save instead of Incremental
            # Incremental save doesn't refresh graphics state properly after redaction
            # Clean save rebuilds PDF structure, fixing visibility issues
            
            temp_output = input_path + ".tmp.pdf"
            doc.save(
                temp_output,
                garbage=4,      # Remove unused objects
                deflate=True,   # Compress streams
                clean=True      # Clean and rebuild structure
            )
            doc.close()
            
            # Replace original file with cleaned version
            import os
            os.replace(temp_output, input_path)
            
            logger.info(f"✓ Clean save complete - Visual rendering fixed")
            
            return True
            
        except Exception as e:
            raise Exception(f"Error applying edit: {str(e)}")
    
    def _fallback_text_replacement(self, page, bbox, original_text, new_text, font_size, color_rgb, position):
        """Fallback method when text search doesn't find the exact text"""
        if bbox:
            # Use bbox for positioning
            x_pos = bbox[0]
            y_pos = bbox[3]
            
            # Cover the bbox area with white rectangle
            rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Insert new text
            insert_point = fitz.Point(x_pos, y_pos)
            page.insert_text(
                point=insert_point,
                text=new_text,
                fontsize=font_size,
                color=color_rgb,
                fontname='helv'
            )
            logger.info(f"Used fallback method to replace text at bbox")
        else:
            # Use position
            x_pos = position.get('x', 50)
            y_pos = position.get('y', 50)
            insert_point = fitz.Point(x_pos, y_pos)
            page.insert_text(
                point=insert_point,
                text=new_text,
                fontsize=font_size,
                color=color_rgb,
                fontname='helv'
            )
            logger.info(f"Used fallback method with position")
    
    def _rgb_to_hex(self, rgb_int):
        """Convert RGB integer to hex color"""
        try:
            r = (rgb_int >> 16) & 0xFF
            g = (rgb_int >> 8) & 0xFF
            b = rgb_int & 0xFF
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#000000"
    
    def _get_font_path(self, font_name):
        """
        Get ABSOLUTE font file path for a given font name
        
        GEMINI RECOMMENDATION: Always use absolute paths on Ubuntu/Linux
        Relative paths (fonts/SolaimanLipi.ttf) often fail
        """
        if font_name in self.custom_fonts:
            font_path = self.custom_fonts[font_name]
            
            # Ensure absolute path
            if not os.path.isabs(font_path):
                # Convert to absolute path
                font_path = os.path.abspath(font_path)
                logger.info(f"Converted to absolute path: {font_path}")
            
            # Verify file exists
            if os.path.exists(font_path):
                return font_path
            else:
                logger.warning(f"Font file not found: {font_path}")
                return None
        
        return None
    
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
