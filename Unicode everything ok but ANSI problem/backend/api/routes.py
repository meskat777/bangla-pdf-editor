"""
Additional API Routes for extended features
"""

from flask import Blueprint, request, jsonify, send_file
import os

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Import utility modules
from utils.page_manager import PageManager
from utils.annotation_handler import AnnotationHandler
from utils.document_operations import DocumentOperations

page_manager = PageManager()
annotation_handler = AnnotationHandler()
doc_operations = DocumentOperations()

@api.route('/page/add', methods=['POST'])
def add_page():
    """Add a blank page to PDF"""
    try:
        data = request.json
        session_id = data.get('session_id')
        page_number = data.get('page_number', -1)
        
        # Implementation handled by page_manager
        result = page_manager.add_page(
            data.get('filepath'),
            data.get('output_path'),
            page_number
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/page/delete', methods=['POST'])
def delete_page():
    """Delete a page from PDF"""
    try:
        data = request.json
        
        result = page_manager.delete_page(
            data.get('filepath'),
            data.get('output_path'),
            data.get('page_number')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/page/rotate', methods=['POST'])
def rotate_page():
    """Rotate a page"""
    try:
        data = request.json
        
        result = page_manager.rotate_page(
            data.get('filepath'),
            data.get('output_path'),
            data.get('page_number'),
            data.get('rotation', 90)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/page/duplicate', methods=['POST'])
def duplicate_page():
    """Duplicate a page"""
    try:
        data = request.json
        
        result = page_manager.duplicate_page(
            data.get('filepath'),
            data.get('output_path'),
            data.get('page_number')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/annotation/highlight', methods=['POST'])
def add_highlight():
    """Add text highlighting"""
    try:
        data = request.json
        
        result = annotation_handler.add_highlight(
            data.get('filepath'),
            data.get('session_id'),
            data.get('page_number'),
            data.get('bbox'),
            data.get('color', '#ffff00')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/annotation/signature', methods=['POST'])
def add_signature():
    """Add signature"""
    try:
        data = request.json
        
        result = annotation_handler.add_signature(
            data.get('filepath'),
            data.get('session_id'),
            data.get('page_number'),
            data.get('signature_data'),
            data.get('position'),
            data.get('size')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/annotation/image', methods=['POST'])
def add_image():
    """Add image to PDF"""
    try:
        data = request.json
        
        result = annotation_handler.add_image(
            data.get('filepath'),
            data.get('session_id'),
            data.get('page_number'),
            data.get('image_data'),
            data.get('position'),
            data.get('size')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/annotation/watermark', methods=['POST'])
def add_watermark():
    """Add watermark to PDF"""
    try:
        data = request.json
        
        result = annotation_handler.add_watermark(
            data.get('filepath'),
            data.get('output_path'),
            data.get('text'),
            data.get('opacity', 0.3)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/annotation/note', methods=['POST'])
def add_sticky_note():
    """Add sticky note"""
    try:
        data = request.json
        
        result = annotation_handler.add_sticky_note(
            data.get('filepath'),
            data.get('session_id'),
            data.get('page_number'),
            data.get('position'),
            data.get('text'),
            data.get('color', '#ffff00')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/annotation/draw', methods=['POST'])
def add_drawing():
    """Add freehand drawing"""
    try:
        data = request.json
        
        result = annotation_handler.add_drawing(
            data.get('filepath'),
            data.get('session_id'),
            data.get('page_number'),
            data.get('path_data'),
            data.get('color', '#000000'),
            data.get('width', 2)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/document/merge', methods=['POST'])
def merge_pdfs():
    """Merge multiple PDFs"""
    try:
        data = request.json
        
        result = doc_operations.merge_pdfs(
            data.get('pdf_files', []),
            data.get('output_path')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/document/split', methods=['POST'])
def split_pdf():
    """Split PDF at specified pages"""
    try:
        data = request.json
        
        result = doc_operations.split_pdf(
            data.get('filepath'),
            data.get('output_dir'),
            data.get('split_points', [])
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/document/export/images', methods=['POST'])
def export_to_images():
    """Export PDF pages as images"""
    try:
        data = request.json
        
        result = doc_operations.export_to_images(
            data.get('filepath'),
            data.get('output_dir'),
            data.get('format', 'PNG'),
            data.get('dpi', 150)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/document/export/html', methods=['POST'])
def export_to_html():
    """Export PDF to HTML"""
    try:
        data = request.json
        
        result = doc_operations.export_to_html(
            data.get('filepath'),
            data.get('output_path')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/session/save', methods=['POST'])
def save_session():
    """Save editing session"""
    try:
        data = request.json
        
        result = doc_operations.save_session(
            data.get('session_data'),
            data.get('session_path')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/session/load', methods=['POST'])
def load_session():
    """Load editing session"""
    try:
        data = request.json
        
        result = doc_operations.load_session(
            data.get('session_path')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
