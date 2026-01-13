# Architecture Documentation - Bangla PDF Editor

## 🏗️ System Architecture

### Overview
The Bangla PDF Editor follows a **secure client-server architecture** where all PDF processing, OCR, and manipulation happens exclusively on the backend server. The frontend is a thin client that only handles user interactions and displays results.

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   HTML UI    │  │     CSS      │  │  JavaScript   │     │
│  │  (index.html)│  │  (style.css) │  │   (app.js)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                          │                                  │
│                    HTTP/HTTPS                               │
└─────────────────────────┼────────────────────────────────────┘
                          │
                    REST API (JSON)
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                      BACKEND SERVER                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Flask Application (app.py)                │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │              API Routes & Endpoints              │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────┐          │
│  │                                                │          │
│  ▼                                                ▼          │
│ ┌──────────────────┐                  ┌──────────────────┐  │
│ │   PDF Processor  │                  │   OCR Handler    │  │
│ │  (PyMuPDF/fitz)  │                  │   (EasyOCR)      │  │
│ └──────────────────┘                  └──────────────────┘  │
│          │                                      │            │
│          ▼                                      ▼            │
│ ┌──────────────────┐                  ┌──────────────────┐  │
│ │   Text Editor    │                  │  Page Manager    │  │
│ │                  │                  │                  │  │
│ └──────────────────┘                  └──────────────────┘  │
│          │                                      │            │
│          ▼                                      ▼            │
│ ┌──────────────────┐                  ┌──────────────────┐  │
│ │ Annotation Tool  │                  │  Doc Operations  │  │
│ │                  │                  │  (Merge/Split)   │  │
│ └──────────────────┘                  └──────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              File System Storage                       │ │
│  │  • uploads/    - Temporary uploaded files              │ │
│  │  • sessions/   - Session data & modifications          │ │
│  │  • exports/    - Generated/edited PDFs                 │ │
│  │  • fonts/      - Bangla & custom fonts                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 Directory Structure

```
bangla-pdf-editor/
│
├── backend/                      # Server-side application
│   ├── app.py                   # Main Flask application & routes
│   ├── api/                     # Additional API endpoints
│   │   ├── __init__.py
│   │   └── routes.py           # Extended API routes
│   └── utils/                   # Processing modules
│       ├── __init__.py
│       ├── pdf_processor.py    # PDF loading & rendering
│       ├── ocr_handler.py      # OCR text detection
│       ├── text_editor.py      # Text editing operations
│       ├── page_manager.py     # Page operations
│       ├── annotation_handler.py # Annotations & drawings
│       └── document_operations.py # Merge/split/export
│
├── frontend/                    # Client-side application
│   ├── templates/
│   │   └── index.html          # Main UI template
│   └── static/
│       ├── css/
│       │   └── style.css       # Application styles
│       └── js/
│           └── app.js          # Client-side logic
│
├── fonts/                       # Font files
│   ├── *.ttf                   # TrueType fonts
│   └── *.otf                   # OpenType fonts
│
├── uploads/                     # Temporary uploads
├── sessions/                    # Session storage
├── exports/                     # Generated files
│
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
├── DEPLOYMENT.md               # Deployment guide
├── ARCHITECTURE.md             # This file
└── .gitignore                  # Git ignore rules
```

---

## 🔄 Request Flow

### 1. PDF Upload Flow
```
User clicks upload
    │
    ▼
Frontend sends file via FormData
    │
    ▼
Backend receives POST /api/upload
    │
    ├──> Validate file (PDF only, size limit)
    │
    ├──> Generate session ID (UUID)
    │
    ├──> Save to uploads/ directory
    │
    ├──> PDFProcessor.process_pdf()
    │    ├──> Open with PyMuPDF
    │    ├──> Extract text blocks with formatting
    │    ├──> Detect fonts, sizes, colors
    │    └──> Return structured data
    │
    ├──> Store session data
    │
    └──> Return JSON response
         ├── session_id
         ├── pdf_data (pages, text_blocks, metadata)
         └── success message
              │
              ▼
Frontend receives response
    │
    ├──> Store session_id
    ├──> Render first page
    ├──> Create text box overlays
    └──> Enable editing buttons
```

### 2. Text Editing Flow
```
User clicks on text
    │
    ▼
Frontend shows edit panel
    │
    ▼
User modifies text/font/style
    │
    ▼
User clicks "Apply"
    │
    ▼
Frontend sends POST /api/text/edit
    │
    └──> {session_id, page_number, text_box_id, 
          new_text, font, font_size, color, style}
    │
    ▼
Backend receives request
    │
    ├──> Validate session
    │
    ├──> TextEditor.edit_text()
    │    └──> Store modification in session
    │
    └──> Return success response
              │
              ▼
Frontend receives response
    │
    └──> Re-render page with changes
```

### 3. Save & Download Flow
```
User clicks "Save"
    │
    ▼
Frontend sends POST /api/save
    │
    └──> {session_id}
    │
    ▼
Backend processes
    │
    ├──> Load original PDF
    │
    ├──> Apply all modifications
    │    ├── Delete original text (white overlay)
    │    ├── Insert new text with formatting
    │    ├── Add annotations
    │    └── Apply page operations
    │
    ├──> Save to exports/ directory
    │
    └──> Return download URL
              │
              ▼
User clicks "Download"
    │
    ▼
Frontend opens GET /api/download/{session_id}
    │
    ▼
Backend sends file
```

---

## 🔐 Security Architecture

### 1. No Code Exposure
- **All processing on server**: No PDF manipulation code in browser
- **API only**: Frontend only makes REST calls
- **No client-side libraries**: No PDF.js, no client-side OCR

### 2. Session Management
```python
sessions = {
    'session_id': {
        'filename': 'original.pdf',
        'filepath': 'uploads/uuid_original.pdf',
        'pdf_data': {...},
        'created_at': '2024-01-04T00:00:00',
        'modifications': [...]
    }
}
```

### 3. File Validation
- Extension check: `.pdf` only
- Size limit: 50MB max
- Secure filename: `secure_filename()` from Werkzeug
- Unique naming: UUID prefix

### 4. Access Control
- Session-based isolation
- No direct file access
- Automatic cleanup (optional)

---

## 🎨 Frontend Architecture

### Minimal JavaScript Philosophy
The frontend uses vanilla JavaScript with NO external libraries for PDF processing.

**What JavaScript DOES:**
- ✅ Handle user interactions (clicks, inputs)
- ✅ Make API calls (fetch)
- ✅ Display server-rendered images
- ✅ Update UI based on responses
- ✅ Manage application state

**What JavaScript DOES NOT:**
- ❌ Parse PDF files
- ❌ Render PDF content
- ❌ Process images
- ❌ Run OCR
- ❌ Manipulate PDF structure

### State Management
```javascript
const AppState = {
    sessionId: null,        // Current session
    pdfData: null,          // PDF metadata from server
    currentPage: 0,         // Current page index
    zoom: 1.0,             // Zoom level
    selectedTextBox: null,  // Selected text for editing
    modifications: [],      // Local modification tracking
    undoStack: [],         // Undo history
    redoStack: []          // Redo history
};
```

---

## ⚙️ Backend Architecture

### 1. PDF Processor (`pdf_processor.py`)
```python
class PDFProcessor:
    def process_pdf(filepath, session_id):
        """
        - Open PDF with PyMuPDF
        - Extract all text blocks with metadata
        - Return structured data
        """
    
    def render_page(filepath, page_number, zoom):
        """
        - Render page as high-quality image
        - Return base64 encoded PNG
        """
    
    def save_pdf(input_path, output_path, modifications):
        """
        - Apply all modifications
        - Generate final PDF
        """
```

### 2. OCR Handler (`ocr_handler.py`)
```python
class OCRHandler:
    def __init__():
        """Initialize EasyOCR with Bengali & English"""
        self.reader = easyocr.Reader(['bn', 'en'])
    
    def detect_text(pdf_path, page_number):
        """
        - Render page to image
        - Run OCR detection
        - Return text with bounding boxes
        """
```

### 3. Text Editor (`text_editor.py`)
```python
class TextEditor:
    def edit_text(...):
        """Store edit information for later application"""
    
    def add_text(...):
        """Add new text to PDF"""
    
    def delete_text(...):
        """Mark text for deletion"""
```

### 4. Modular Design
Each utility module is independent and can be:
- Tested separately
- Updated without affecting others
- Replaced with different implementations
- Extended with new features

---

## 🔌 API Design

### RESTful Principles
- **Resource-based URLs**: `/api/text/edit`, `/api/page/rotate`
- **HTTP methods**: POST for modifications, GET for retrieval
- **JSON format**: All requests/responses in JSON
- **Consistent responses**: All return `{success: bool, ...}`

### Error Handling
```python
try:
    # Operation
    return jsonify({'success': True, ...})
except Exception as e:
    return jsonify({'success': False, 'error': str(e)}), 500
```

### Bilingual Messages
```python
'message': 'পিডিএফ সফলভাবে আপলোড হয়েছে | PDF uploaded successfully'
```

---

## 📊 Data Flow

### Text Block Structure
```json
{
    "id": "text_0_1_2_3",
    "text": "বাংলা টেক্সট",
    "font": "Kohinoor-Bold",
    "size": 14.5,
    "color": "#000000",
    "bbox": [100, 200, 300, 220],
    "bold": true,
    "italic": false
}
```

### Page Data Structure
```json
{
    "page_number": 0,
    "width": 595,
    "height": 842,
    "text_blocks": [...],
    "images": [...],
    "has_text": true
}
```

### Modification Structure
```json
{
    "type": "text_edit",
    "timestamp": "2024-01-04T00:00:00",
    "data": {
        "page_number": 0,
        "text_box_id": "text_0_1_2_3",
        "new_text": "New text",
        "font": "helv",
        "font_size": 12,
        "color": "#000000"
    }
}
```

---

## 🚀 Performance Considerations

### 1. Lazy Loading
- Pages rendered on-demand
- OCR only when requested
- Thumbnails loaded asynchronously

### 2. Caching Strategy
- Server-side image caching
- Session data in memory
- Font preloading

### 3. Optimization
- Image compression for rendering
- Efficient PDF parsing
- Minimal data transfer

### 4. Scalability
- Stateless API design
- Session storage can be moved to Redis/Database
- Horizontal scaling possible

---

## 🧪 Testing Strategy

### Unit Tests
```python
# test_pdf_processor.py
def test_process_pdf():
    processor = PDFProcessor(config)
    result = processor.process_pdf('test.pdf', 'session123')
    assert result['num_pages'] > 0
```

### Integration Tests
```python
# test_api.py
def test_upload_endpoint():
    response = client.post('/api/upload', data={'file': file})
    assert response.status_code == 200
    assert 'session_id' in response.json
```

### Load Tests
```python
# Using Locust
from locust import HttpUser, task

class PDFEditorUser(HttpUser):
    @task
    def upload_pdf(self):
        self.client.post('/api/upload', files={'file': pdf_file})
```

---

## 🔄 Future Enhancements

### 1. Real-time Collaboration
- WebSocket support
- Multi-user editing
- Change synchronization

### 2. Advanced OCR
- Table detection
- Form recognition
- Layout analysis

### 3. AI Features
- Auto-correction
- Translation
- Smart suggestions

### 4. Cloud Storage
- S3 integration
- Google Drive support
- Dropbox sync

---

## 📚 Technology Stack

### Backend
- **Flask**: Web framework
- **PyMuPDF (fitz)**: PDF processing
- **EasyOCR**: Optical character recognition
- **Pillow**: Image manipulation
- **NumPy**: Numerical operations

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling & animations
- **Vanilla JavaScript**: Logic & interactions
- **Canvas API**: Display rendering

### Infrastructure
- **Python 3.8+**: Runtime
- **Gunicorn**: WSGI server (production)
- **Nginx**: Reverse proxy (production)
- **Docker**: Containerization (optional)

---

**This architecture ensures maximum security, performance, and maintainability while keeping your code protected from client-side exposure.**
