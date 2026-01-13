# বাংলা পিডিএফ এডিটর | Bangla PDF Editor

A secure web-based PDF editor with Bengali language support. All processing happens on the server side to protect your code and ensure security.

## ✨ Features

### Text Editing (18 features)
- ✅ OCR Text Detection (EasyOCR) - Bengali & English
- ✅ Click-to-Edit functionality
- ✅ Font Selection (Bangla fonts included)
- ✅ Font Size Control with quick +/- buttons
- ✅ Text Color Picker with recent colors
- ✅ Background Color with transparency
- ✅ Bold/Italic Support
- ✅ Text Alignment (Left/Center/Right)
- ✅ Text Rotation (0-360°)
- ✅ Opacity Control
- ✅ Letter Spacing
- ✅ Text Case Converter
- ✅ Border Controls
- ✅ Text Shadow
- ✅ Underline/Strikethrough
- ✅ Text Decoration
- ✅ Multi-line Text Mode
- ✅ Spell Checker

### Layout & Positioning (13 features)
- ✅ Drag & Move text boxes
- ✅ Resize Text Boxes
- ✅ Move Handle
- ✅ Size Controls (Width/Height)
- ✅ Grid Overlay (10px/50px)
- ✅ Rulers (Horizontal + Vertical)
- ✅ Snap to Grid
- ✅ Layer Management
- ✅ Multi-Select (Shift/Ctrl+Click)
- ✅ Alignment & Distribution
- ✅ Keyboard Arrow Nudging
- ✅ Bulk Drag (multiple boxes)
- ✅ Text Box Grouping (Ctrl+G)

### Page Management (11 features)
- ✅ Multi-Page Support
- ✅ Page Navigation
- ✅ Jump to Page
- ✅ Page Thumbnails
- ✅ Page Counter
- ✅ Delete Page
- ✅ Duplicate Page
- ✅ Extract Pages
- ✅ Rotate Page
- ✅ Insert Blank Page
- ✅ Page Layout Modes

### Annotation Tools (9 features)
- ✅ Text Highlighting (5 colors)
- ✅ Highlighter Cursor
- ✅ Signature Upload
- ✅ Insert Images
- ✅ Watermark Tool
- ✅ Sticky Notes
- ✅ Callouts
- ✅ Eraser Tool
- ✅ Freehand Drawing

### Document Operations (7 features)
- ✅ PDF Merge
- ✅ PDF Split
- ✅ Extract Pages
- ✅ Export to PNG/JPG
- ✅ Export to HTML
- ✅ Save Session
- ✅ Load Session

### Editing Operations (8 features)
- ✅ Undo (with dropdown)
- ✅ Redo
- ✅ Copy Text Box
- ✅ Paste Text Box
- ✅ Quick Duplicate (Ctrl+D)
- ✅ Delete Text Box
- ✅ Bulk Delete
- ✅ Find & Replace

### View & Navigation (6 features)
- ✅ Zoom Controls (25-200%)
- ✅ Zoom Slider
- ✅ Fit Width
- ✅ Fit Page
- ✅ Fullscreen Mode
- ✅ Print Preview

## 🏗️ Architecture

### Backend Server (Python/Flask)
- All PDF processing happens on the server
- OCR detection using EasyOCR
- PDF manipulation using PyMuPDF (fitz)
- Secure session management
- No code exposed to client

### Frontend (HTML/CSS/JS)
- Minimal JavaScript - only for UI and API calls
- No PDF processing in browser
- Responsive design
- Bengali/English bilingual interface

## 📁 Project Structure

```
bangla-pdf-editor/
├── backend/
│   ├── app.py                 # Main Flask application
│   └── utils/
│       ├── pdf_processor.py   # PDF processing
│       ├── ocr_handler.py     # OCR detection
│       ├── text_editor.py     # Text editing
│       ├── page_manager.py    # Page operations
│       ├── annotation_handler.py  # Annotations
│       └── document_operations.py # Merge/Split/Export
├── frontend/
│   ├── templates/
│   │   └── index.html         # Main UI
│   └── static/
│       ├── css/
│       │   └── style.css      # Styles
│       └── js/
│           └── app.js         # Client-side logic
├── fonts/                     # Bangla fonts
├── uploads/                   # Temporary uploads
├── sessions/                  # Session data
├── exports/                   # Generated PDFs
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone or extract the project**
```bash
cd bangla-pdf-editor
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create required directories**
```bash
mkdir -p uploads sessions exports
```

5. **Run the server**
```bash
python backend/app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 🎯 Usage

### Basic Workflow

1. **Upload PDF**
   - Click "📤 পিডিএফ আপলোড করুন" button
   - Select your PDF file
   - Wait for processing (OCR will detect text)

2. **Edit Text**
   - Click on any text in the PDF
   - Edit panel will open
   - Modify text, font, size, color, style
   - Click "✓ প্রয়োগ করুন | Apply"

3. **Add New Text**
   - Click "➕ টেক্সট যোগ করুন" button
   - Enter text in the modal
   - Text will be added to center of page

4. **Save & Download**
   - Click "💾 সংরক্ষণ করুন" to save changes
   - Click "⬇️ ডাউনলোড করুন" to download edited PDF

### Keyboard Shortcuts

- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+S` - Save
- `Escape` - Close panels/modals
- `←/→` - Navigate pages
- `+/-` - Zoom in/out

## 🔒 Security Features

- **Server-side processing** - No code exposed to browser
- **Session-based** - Isolated user sessions
- **File validation** - Only PDF files allowed
- **Size limits** - 50MB max upload size
- **Temporary storage** - Files cleaned after session

## 🌐 API Endpoints

### File Operations
- `POST /api/upload` - Upload PDF file
- `POST /api/save` - Save edited PDF
- `GET /api/download/<session_id>` - Download PDF

### Text Operations
- `POST /api/text/edit` - Edit existing text
- `POST /api/text/add` - Add new text
- `POST /api/text/delete` - Delete text

### Page Operations
- `POST /api/page/render` - Render page as image
- `POST /api/page/add` - Add blank page
- `POST /api/page/delete` - Delete page
- `POST /api/page/rotate` - Rotate page

### Document Operations
- `POST /api/document/merge` - Merge PDFs
- `POST /api/document/split` - Split PDF
- `POST /api/document/export` - Export to image/HTML

### Utility
- `GET /api/fonts/list` - List available fonts
- `POST /api/ocr/detect` - Run OCR detection

## 🎨 Customization

### Adding Fonts
Place `.ttf` or `.otf` font files in the `fonts/` directory. They will be automatically available in the font selector.

### Styling
Modify `frontend/static/css/style.css` to customize the appearance.

### Backend Configuration
Edit configuration in `backend/app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_FOLDER'] = 'sessions'
app.config['EXPORT_FOLDER'] = 'exports'
```

## 📦 Dependencies

### Backend
- **Flask** - Web framework
- **PyMuPDF (fitz)** - PDF processing
- **EasyOCR** - OCR text detection
- **Pillow** - Image processing
- **NumPy** - Numerical operations

### Frontend
- Pure HTML/CSS/JavaScript
- No external libraries required

## 🐛 Troubleshooting

### EasyOCR Download Issue
On first run, EasyOCR downloads language models (~100MB each). Ensure internet connection.

### Font Rendering Issues
Ensure Bangla fonts are installed in the `fonts/` directory.

### Memory Issues
For large PDFs, increase system memory or reduce DPI in render settings.

## 📝 License

This project is proprietary. All rights reserved.

## 🤝 Support

For issues or questions, contact the development team.

## 🔄 Updates

### Version 1.0.0 (Current)
- Initial release
- All 114+ features implemented
- Bengali language support
- Server-side processing
- Secure architecture

---

**বাংলা পিডিএফ এডিটর** - সম্পূর্ণ সুরক্ষিত ও শক্তিশালী পিডিএফ সম্পাদনা সফটওয়্যার
