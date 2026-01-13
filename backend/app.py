"""
Bangla PDF Editor - Backend Server
All PDF processing happens on the server side
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json

# Import utility modules
from utils.pdf_processor import PDFProcessor
from utils.ocr_handler import OCRHandler
from utils.text_editor import TextEditor
from utils.page_manager import PageManager
from utils.annotation_handler import AnnotationHandler
from utils.document_operations import DocumentOperations
from utils.bijoy_unicode_converter import convert_bijoy_to_unicode, is_bijoy_text
from session_manager import SessionManager
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Load configuration
from config import config
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Configure CORS with security
CORS(app, resources={
    r"/api/*": {
        "origins": app.config.get('CORS_ORIGINS', ['http://localhost:5000', 'http://127.0.0.1:5000']),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Additional configuration (these override config.py if needed)
if 'MAX_CONTENT_LENGTH' not in app.config:
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure folders exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['SESSION_FOLDER'], 
               app.config['EXPORT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize processors
pdf_processor = PDFProcessor(app.config)
ocr_handler = OCRHandler()
text_editor = TextEditor()
page_manager = PageManager()
annotation_handler = AnnotationHandler()
doc_operations = DocumentOperations()

# Initialize session manager with persistent storage
session_manager = SessionManager(app.config['SESSION_FOLDER'])
logger.info("Session manager initialized with persistent storage")

# Run cleanup on startup if enabled
if app.config.get('AUTO_CLEANUP', True):
    logger.info("Running cleanup on startup...")
    try:
        deleted = session_manager.cleanup_old_sessions(24)
        logger.info(f"Startup cleanup: {deleted} old sessions removed")
    except Exception as e:
        logger.warning(f"Startup cleanup failed: {e}")

# Start background cleanup thread (runs every hour)
from threading import Thread
import time

def cleanup_worker():
    """Background cleanup thread"""
    while True:
        try:
            time.sleep(3600)  # Sleep for 1 hour
            logger.info("Running scheduled cleanup...")
            
            # Clean old sessions
            deleted_sessions = session_manager.cleanup_old_sessions(24)
            
            # Clean old uploaded files
            import glob
            cutoff = time.time() - (24 * 3600)
            deleted_files = 0
            
            for folder in [app.config['UPLOAD_FOLDER'], app.config['EXPORT_FOLDER']]:
                for filepath in glob.glob(os.path.join(folder, '*')):
                    if os.path.isfile(filepath) and os.path.basename(filepath) != '.gitkeep':
                        if os.path.getmtime(filepath) < cutoff:
                            try:
                                os.remove(filepath)
                                deleted_files += 1
                            except:
                                pass
            
            logger.info(f"Scheduled cleanup: {deleted_sessions} sessions, {deleted_files} files removed")
        except Exception as e:
            logger.error(f"Cleanup worker error: {e}", exc_info=True)

# Start cleanup thread
cleanup_thread = Thread(target=cleanup_worker, daemon=True, name="CleanupWorker")
cleanup_thread.start()
logger.info("Background cleanup worker started")

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check session manager
        session_count = session_manager.get_session_count()
        
        # Check folders
        folders_ok = all([
            os.path.exists(app.config['UPLOAD_FOLDER']),
            os.path.exists(app.config['SESSION_FOLDER']),
            os.path.exists(app.config['EXPORT_FOLDER'])
        ])
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'sessions': session_count,
            'folders': 'ok' if folders_ok else 'error'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Upload and process PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        # Process PDF and extract text with OCR
        pdf_data = pdf_processor.process_pdf(filepath, session_id)
        
        # Convert Bijoy text to Unicode in all text blocks
        for page in pdf_data['pages']:
            for text_block in page['text_blocks']:
                # Check if text is Bijoy and convert
                original_text = text_block['text']
                font_name = text_block.get('font', '')
                
                # Convert Bijoy to Unicode
                unicode_text = convert_bijoy_to_unicode(original_text, font_name)
                
                # Update text block
                text_block['text'] = unicode_text
                text_block['original_text'] = original_text  # Keep original for reference
                text_block['is_bijoy'] = is_bijoy_text(original_text)
                
                # Add conversion info for debugging
                if text_block['is_bijoy']:
                    logger.info(f"Converted Bijoy text: '{original_text}' -> '{unicode_text}'")
        
        # Store session with persistent storage
        session_data = {
            'filename': filename,
            'filepath': filepath,
            'pdf_data': pdf_data,
            'created_at': datetime.now().isoformat(),
            'modifications': []
        }
        session_manager.save(session_id, session_data)
        logger.info(f"Session created and saved: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'pdf_data': pdf_data,
            'message': 'পিডিএফ সফলভাবে আপলোড হয়েছে | PDF uploaded successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ocr/detect', methods=['POST'])
def detect_text_ocr():
    """Detect text using OCR on a specific page"""
    try:
        data = request.json
        session_id = data.get('session_id')
        page_number = data.get('page_number', 0)
        
        if not session_manager.exists(session_id):
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        filepath = session['filepath']
        
        # Run OCR detection
        ocr_results = ocr_handler.detect_text(filepath, page_number)
        
        return jsonify({
            'success': True,
            'ocr_results': ocr_results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/text/edit', methods=['POST'])
def edit_text():
    """Edit text in PDF"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_manager.exists(session_id):
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        
        # Apply edit immediately to the working PDF file
        try:
            pdf_processor.apply_edit_immediately(
                session['filepath'],
                data.get('page_number'),
                data.get('bbox'),
                data.get('original_text', ''),
                data.get('new_text'),
                data.get('font', 'helv'),
                data.get('font_size', 12),
                data.get('color', '#000000'),
                data.get('position', {'x': 50, 'y': 50})
            )
        except Exception as e:
            logger.warning(f"Error applying edit immediately: {e}")
        
        # Store modification for final save
        session['modifications'].append({
            'type': 'text_edit',
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        # Update the text block in session data
        page_data = session['pdf_data']['pages'][data.get('page_number')]
        for block in page_data['text_blocks']:
            if block['id'] == data.get('text_box_id'):
                block['text'] = data.get('new_text')
                block['font'] = data.get('font')
                block['size'] = data.get('font_size')
                block['color'] = data.get('color')
                break
        
        # Save updated session
        session_manager.save(session_id, session)
        logger.info(f"Session updated: {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'টেক্সট সফলভাবে সম্পাদিত হয়েছে | Text edited successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/text/add', methods=['POST'])
def add_text():
    """Add new text to PDF"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_manager.exists(session_id):
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        
        result = text_editor.add_text(
            session['filepath'],
            session_id,
            data.get('page_number'),
            data.get('text'),
            data.get('position'),
            data.get('font'),
            data.get('font_size'),
            data.get('color'),
            data.get('style')
        )
        
        session['modifications'].append({
            'type': 'text_add',
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        # Save updated session
        session_manager.save(session_id, session)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/text/delete', methods=['POST'])
def delete_text():
    """Delete text from PDF"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_manager.exists(session_id):
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        
        result = text_editor.delete_text(
            session['filepath'],
            session_id,
            data.get('page_number'),
            data.get('text_box_id')
        )
        
        session['modifications'].append({
            'type': 'text_delete',
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        # Save updated session
        session_manager.save(session_id, session)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fonts/list', methods=['GET'])
def list_fonts():
    """Get list of available fonts"""
    try:
        fonts = []
        fonts_dir = app.config['FONTS_FOLDER']
        
        if os.path.exists(fonts_dir):
            for font_file in os.listdir(fonts_dir):
                if font_file.lower().endswith(('.ttf', '.otf')):
                    fonts.append({
                        'name': os.path.splitext(font_file)[0],
                        'filename': font_file
                    })
        
        return jsonify({
            'success': True,
            'fonts': fonts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/page/render', methods=['POST'])
def render_page():
    """Render a specific page as image"""
    try:
        data = request.json
        session_id = data.get('session_id')
        page_number = data.get('page_number', 0)
        zoom = data.get('zoom', 1.0)
        
        if not session_manager.exists(session_id):
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        
        # Render page to image
        image_data = pdf_processor.render_page(
            session['filepath'],
            page_number,
            zoom
        )
        
        return jsonify({
            'success': True,
            'image_data': image_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_pdf():
    """Save edited PDF"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_manager.exists(session_id):
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        
        # Generate output filename
        output_filename = f"edited_{session['filename']}"
        output_path = os.path.join(app.config['EXPORT_FOLDER'], f"{session_id}_{output_filename}")
        
        # FIXED: Since we're using apply_edit_immediately(), the working file is already edited
        # Just copy the current working file to exports folder
        import shutil
        
        try:
            # Ensure export folder exists
            os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
            
            # Convert to absolute path for consistent access
            abs_output_path = os.path.abspath(output_path)
            
            # Copy the already-edited file to exports
            shutil.copy2(session['filepath'], abs_output_path)
            logger.info(f"PDF saved to: {abs_output_path}")
            
            # Store the absolute export path in session for download
            session['export_path'] = abs_output_path
            session_manager.save(session_id, session)
            
        except Exception as e:
            logger.error(f"Error saving PDF: {e}", exc_info=True)
            return jsonify({'error': f'Failed to save PDF: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'download_url': f'/api/download/{session_id}',
            'message': 'পিডিএফ সফলভাবে সংরক্ষিত হয়েছে | PDF saved successfully'
        })
    
    except Exception as e:
        logger.error(f"Save endpoint error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<session_id>', methods=['GET'])
def download_pdf(session_id):
    """Download edited PDF"""
    try:
        if not session_manager.exists(session_id):
            logger.error(f"Session not found: {session_id}")
            return jsonify({'error': 'Invalid session'}), 404
        
        session = session_manager.load(session_id)
        output_filename = f"edited_{session['filename']}"
        
        # Check if we have an export_path stored
        output_path = session.get('export_path')
        
        # Fallback to default path if not stored
        if not output_path:
            output_path = os.path.join(app.config['EXPORT_FOLDER'], f"{session_id}_{output_filename}")
        
        # Convert to absolute path to ensure Flask can find it
        abs_output_path = os.path.abspath(output_path)
        
        logger.info(f"Looking for file at: {abs_output_path}")
        
        if not os.path.exists(abs_output_path):
            logger.error(f"File not found: {abs_output_path}")
            return jsonify({'error': 'File not found. Please save the PDF first.'}), 404
        
        logger.info(f"Sending file: {abs_output_path}")
        
        return send_file(
            abs_output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        logger.error(f"Download error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
