"""
Text to Image Renderer for PDF Editing
Gemini's Recommended Solution: Render text as transparent PNG for 100% visibility

This solves the text insertion visibility issue by converting text to an image
that can be reliably overlaid on the PDF using insert_image().
"""

from PIL import Image, ImageDraw, ImageFont
import io
import os
import logging

logger = logging.getLogger(__name__)


class TextToImageRenderer:
    """
    Render text as a transparent PNG image for PDF insertion
    
    Why this works (Gemini's insight):
    - Direct text insertion has rendering/embedding bugs
    - Images are ALWAYS visible in PDFs
    - Using exact font file ensures perfect match
    """
    
    def __init__(self):
        self.dpi = 300  # High resolution for crisp text
    
    def render_text_to_image(self, text, font_path, font_size, color_rgb, bbox_width, bbox_height):
        """
        Render text as a transparent PNG image
        
        Args:
            text (str): Text to render
            font_path (str): Absolute path to font file
            font_size (float): Font size in points
            color_rgb (tuple): (r, g, b) color values (0-1 range)
            bbox_width (float): Width of bounding box in points
            bbox_height (float): Height of bounding box in points
            
        Returns:
            bytes: PNG image data as bytes
        """
        try:
            # Convert points to pixels (at 300 DPI)
            # 1 point = 1/72 inch, at 300 DPI: 1 point = 300/72 ≈ 4.17 pixels
            scale_factor = self.dpi / 72.0
            
            img_width = int(bbox_width * scale_factor)
            img_height = int(bbox_height * scale_factor)
            scaled_font_size = int(font_size * scale_factor)
            
            logger.info(f"Creating image: {img_width}x{img_height}px, font size: {scaled_font_size}px")
            
            # Create transparent image (RGBA)
            image = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            # Load font
            try:
                if font_path and os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, scaled_font_size)
                    logger.info(f"Loaded custom font: {font_path}")
                else:
                    # Fallback to default font
                    font = ImageFont.load_default()
                    logger.warning("Using default font (custom font not found)")
            except Exception as e:
                logger.error(f"Font loading error: {e}")
                font = ImageFont.load_default()
            
            # Convert color from 0-1 range to 0-255
            r = int(color_rgb[0] * 255)
            g = int(color_rgb[1] * 255)
            b = int(color_rgb[2] * 255)
            text_color = (r, g, b, 255)  # Fully opaque
            
            # Calculate text position (vertically centered, left-aligned with small padding)
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = 2  # Small left padding
                y = (img_height - text_height) // 2
            except:
                # Fallback positioning
                x = 2
                y = img_height // 4
            
            # Draw text
            draw.text((x, y), text, font=font, fill=text_color)
            
            logger.info(f"✓ Text rendered: '{text}' at ({x}, {y})")
            
            # Convert to PNG bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)
            
            logger.info(f"✓ PNG created: {len(img_bytes.getvalue())} bytes")
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Error rendering text to image: {str(e)}")
            raise
    
    def render_text_simple(self, text, font_size, color_rgb=(0, 0, 0)):
        """
        Simplified rendering without font file (using default font)
        Useful for fallback scenarios
        """
        try:
            # Estimate size based on font size and text length
            char_width = font_size * 0.6  # Approximate
            img_width = int(len(text) * char_width * 4)  # Scale for DPI
            img_height = int(font_size * 5)  # Scale for DPI
            
            image = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            
            font = ImageFont.load_default()
            
            r = int(color_rgb[0] * 255)
            g = int(color_rgb[1] * 255)
            b = int(color_rgb[2] * 255)
            text_color = (r, g, b, 255)
            
            draw.text((2, img_height // 4), text, font=font, fill=text_color)
            
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Simple rendering error: {e}")
            raise


# Global renderer instance
_renderer = TextToImageRenderer()


def text_to_png(text, font_path, font_size, color_rgb, bbox_width, bbox_height):
    """
    Helper function: Convert text to PNG image
    
    Usage:
        from backend.utils.text_to_image_renderer import text_to_png
        image_bytes = text_to_png('Hello', '/path/to/font.ttf', 14, (0,0,0), 50, 20)
    """
    return _renderer.render_text_to_image(text, font_path, font_size, color_rgb, bbox_width, bbox_height)


def text_to_png_simple(text, font_size, color_rgb=(0, 0, 0)):
    """Simplified version without font file"""
    return _renderer.render_text_simple(text, font_size, color_rgb)
