# 🚀 Quick Start Guide - Bangla PDF Editor

## ⚡ Get Started in 5 Minutes

### Step 1: Prerequisites Check
```bash
# Check Python version (3.8+ required)
python --version

# Check pip
pip --version
```

### Step 2: Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Note**: First-time installation will download EasyOCR models (~100MB each for Bengali and English). This is one-time only.

### Step 3: Run the Application
```bash
# Simple way
python run.py

# Or directly
python backend/app.py
```

### Step 4: Open in Browser
```
http://localhost:5000
```

---

## 📝 First PDF Edit

### 1. Upload a PDF
- Click **"📤 পিডিএফ আপলোড করুন"** button
- Select your PDF file
- Wait for processing (OCR will detect all text)

### 2. Edit Text
- Click on any text in the PDF
- Edit panel opens on the right
- Modify:
  - Text content
  - Font (includes Bangla fonts from `/fonts` folder)
  - Size (6-72)
  - Color
  - Style (Bold, Italic, Underline)
  - Alignment
- Click **"✓ প্রয়োগ করুন"** to apply

### 3. Add New Text
- Click **"➕ টেক্সট যোগ করুন"**
- Type your text (supports Bangla)
- Click **"যোগ করুন"**
- Text appears at center of page

### 4. Save & Download
- Click **"💾 সংরক্ষণ করুন"** to save changes
- Click **"⬇️ ডাউনলোড করুন"** to download edited PDF

---

## 🎮 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |
| `Ctrl + S` | Save |
| `Escape` | Close panels |
| `←` / `→` | Previous/Next page |
| `+` / `-` | Zoom in/out |

---

## 📂 Project Structure Overview

```
bangla-pdf-editor/
├── backend/           # Server code (Python/Flask)
├── frontend/          # UI files (HTML/CSS/JS)
├── fonts/            # Your Bangla fonts (already included)
├── uploads/          # Temporary uploaded PDFs
├── sessions/         # Session data
├── exports/          # Generated PDFs
├── run.py            # Start here!
└── requirements.txt  # Dependencies
```

---

## ✨ Key Features Quick Reference

### Text Editing
- ✅ Click-to-edit any text
- ✅ Font selection (753+ fonts in `/fonts`)
- ✅ Size, color, style controls
- ✅ Bold, italic, underline
- ✅ Alignment (left/center/right)

### Page Management
- ✅ Multi-page support
- ✅ Page navigation
- ✅ Thumbnails
- ✅ Add/delete pages
- ✅ Rotate pages

### Annotations
- ✅ Highlighting
- ✅ Signatures
- ✅ Images
- ✅ Watermarks
- ✅ Freehand drawing

### Document Operations
- ✅ Merge PDFs
- ✅ Split PDFs
- ✅ Export to images (PNG/JPG)
- ✅ Export to HTML

---

## 🔧 Configuration

### Change Port
Edit `config.py`:
```python
PORT = 8080  # Change from default 5000
```

### Increase Upload Size
Edit `config.py`:
```python
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
```

### Add More Fonts
Simply copy `.ttf` or `.otf` files to `/fonts` directory. They'll be automatically available!

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution**: Change port in `config.py` or kill existing process
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "OCR not detecting Bengali"
**Solution**: Wait for EasyOCR models to download on first run (automatic). Check internet connection.

### Issue: "Fonts not showing"
**Solution**: 
1. Verify `.ttf`/`.otf` files are in `/fonts` folder
2. Restart the server
3. Refresh browser

### Issue: "Upload fails"
**Solution**:
1. Check file is PDF (not image)
2. File size < 50MB
3. Check disk space in `/uploads` folder

---

## 🎯 Next Steps

### For Users
1. Read `README.md` for complete feature list
2. Try different features (merge, split, annotations)
3. Explore keyboard shortcuts

### For Developers
1. Read `ARCHITECTURE.md` to understand design
2. Read `DEPLOYMENT.md` for production setup
3. Customize `config.py` for your needs

### For Production
1. Follow `DEPLOYMENT.md` guide
2. Setup Nginx + Gunicorn
3. Enable HTTPS with SSL
4. Configure automatic backups

---

## 📞 Support

### Debug Mode
Run with debug logging:
```bash
FLASK_ENV=development python run.py
```

### Check Logs
Logs appear in console. For production, configure logging in `backend/app.py`.

### Verify Installation
```bash
# Test Python imports
python -c "import flask, fitz, easyocr, PIL; print('All imports OK')"

# Check folder permissions
ls -la uploads/ sessions/ exports/
```

---

## 🌟 Tips & Tricks

### 1. Batch Editing
- Select multiple text boxes (Shift+Click)
- Apply same style to all

### 2. Quick Font Size
- Use **+/-** buttons next to size input
- Keyboard shortcuts coming soon

### 3. Recent Colors
- Your last used colors are automatically saved
- Quick access in color picker

### 4. Undo/Redo
- Unlimited undo/redo per session
- Use `Ctrl+Z` and `Ctrl+Y`

### 5. Session Recovery
- Your work is auto-saved every 30 seconds
- Close and reopen anytime

---

## 📊 Performance Tips

### For Large PDFs
1. Reduce DPI in settings (default: 150)
2. Process one page at a time
3. Increase system RAM

### For Better OCR
1. Use high-quality scanned PDFs
2. Ensure good contrast
3. Wait for complete processing

### For Faster Loading
1. Clear old files from `/uploads` and `/exports`
2. Use SSD for storage
3. Enable caching (see `DEPLOYMENT.md`)

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Server starts without errors
- [ ] Browser opens at `http://localhost:5000`
- [ ] Can upload a PDF file
- [ ] OCR detects text (wait ~10 seconds)
- [ ] Can click and edit text
- [ ] Can save and download
- [ ] Bangla fonts display correctly
- [ ] All buttons are functional

---

## 🎉 You're Ready!

Your Bangla PDF Editor is now running. Start editing PDFs with full Bengali language support!

**Remember**: All processing happens on the server. Your code is 100% secure and never exposed to the browser.

---

**Enjoy editing! বাংলা পিডিএফ এডিটর ব্যবহার করার জন্য ধন্যবাদ!**
