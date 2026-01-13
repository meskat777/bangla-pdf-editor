# Priority Fixes - Action Plan

**Generated:** January 4, 2026  
**Based on:** Deep Project Analysis

---

## 🎯 Quick Summary

**Total Issues:** 9  
- 🔴 Critical: 2 (Must fix before production)
- 🟡 Medium: 5 (Should fix soon)
- 🟢 Low: 2 (Code quality improvements)

**Estimated Total Fix Time:** 25-35 hours

---

## 🔴 CRITICAL (Fix First)

### 1. Session Management - **4-6 hours**

**Current Problem:**
```python
sessions = {}  # Lost on restart!
```

**Why Critical:**
- All user data lost when server restarts
- Cannot scale to multiple servers
- Not production-ready

**Quick Fix (File-based):**
```python
# backend/session_manager.py
import json
import os
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, session_folder='sessions'):
        self.session_folder = session_folder
        os.makedirs(session_folder, exist_ok=True)
    
    def save(self, session_id, data):
        """Save session to file"""
        filepath = os.path.join(self.session_folder, f'{session_id}.json')
        data['last_updated'] = datetime.now().isoformat()
        with open(filepath, 'w') as f:
            json.dump(data, f)
    
    def load(self, session_id):
        """Load session from file"""
        filepath = os.path.join(self.session_folder, f'{session_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def exists(self, session_id):
        """Check if session exists"""
        filepath = os.path.join(self.session_folder, f'{session_id}.json')
        return os.path.exists(filepath)
    
    def delete(self, session_id):
        """Delete session"""
        filepath = os.path.join(self.session_folder, f'{session_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def cleanup_old_sessions(self, max_age_hours=24):
        """Delete sessions older than max_age_hours"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        for filename in os.listdir(self.session_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(self.session_folder, filename)
                
                # Check file modification time
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff:
                    os.remove(filepath)

# Usage in backend/app.py
session_manager = SessionManager()

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    # ... existing code ...
    session_manager.save(session_id, session_data)
    return jsonify({...})

@app.route('/api/text/edit', methods=['POST'])
def edit_text():
    session_id = request.json.get('session_id')
    if not session_manager.exists(session_id):
        return jsonify({'error': 'Invalid session'}), 404
    
    session = session_manager.load(session_id)
    # ... process ...
    session_manager.save(session_id, session)
```

**Better Solution (Redis):**
```bash
pip install redis
```

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def save_session(session_id, data):
    redis_client.setex(session_id, 3600, json.dumps(data))  # 1 hour TTL

def load_session(session_id):
    data = redis_client.get(session_id)
    return json.loads(data) if data else None
```

**Files to Modify:**
- `backend/app.py` (all session access points)
- Add `backend/session_manager.py` (new file)

---

### 2. CORS Security - **30 minutes**

**Current Problem:**
```python
CORS(app)  # Allows ANY website to access your API!
```

**Why Critical:**
- Security vulnerability
- XSS/CSRF attack vector
- Any malicious site can steal user data

**Fix:**

**Step 1:** Update `config.py`:
```python
class Config:
    # ... existing config ...
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000').split(',')
    CORS_ALLOW_CREDENTIALS = True
```

**Step 2:** Update `backend/app.py`:
```python
# Replace:
CORS(app)

# With:
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": app.config.get('CORS_ORIGINS', ['http://localhost:5000']),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})
```

**Step 3:** Set environment variable:
```bash
# Development
export CORS_ORIGINS="http://localhost:5000,http://127.0.0.1:5000"

# Production
export CORS_ORIGINS="https://yourdomain.com"
```

**Files to Modify:**
- `config.py`
- `backend/app.py`

---

## 🟡 MEDIUM PRIORITY (Fix Soon)

### 3. Add Logging - **2-3 hours**

**Current Problem:**
- Using `print()` statements (5 instances)
- No way to debug production issues
- No audit trail

**Fix:**

**Step 1:** Create `backend/logger.py`:
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Setup application logging"""
    
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info('Bangla PDF Editor startup')
    
    return app.logger
```

**Step 2:** Update `backend/app.py`:
```python
from logger import setup_logging

app = Flask(__name__, ...)
logger = setup_logging(app)

# Replace all print() with:
logger.info("Message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

**Step 3:** Replace all `print()` statements:
```bash
# Find all print statements:
grep -rn "print(" backend/
```

**Files to Modify:**
- Add `backend/logger.py`
- `backend/app.py` (2 print statements)
- `backend/utils/pdf_processor.py` (2 print statements)
- `backend/utils/bijoy_unicode_converter.py` (1 print statement)

---

### 4. Resource Cleanup - **2-3 hours**

**Current Problem:**
```python
doc = fitz.open(filepath)
# ... operations ...
# Sometimes missing: doc.close()
```

**Why Important:**
- Memory leaks
- File handle exhaustion
- Server crashes under load

**Fix:** Use context managers everywhere

**Example changes in `backend/utils/pdf_processor.py`:**

```python
# Before:
def process_pdf(self, filepath, session_id):
    doc = fitz.open(filepath)
    pages = []
    # ... process pages ...
    doc.close()  # Sometimes forgotten!
    return data

# After:
def process_pdf(self, filepath, session_id):
    with fitz.open(filepath) as doc:
        pages = []
        # ... process pages ...
        return data  # Automatically closes
```

**Files to Fix:**
- `backend/utils/pdf_processor.py` (8 places)
- `backend/utils/ocr_handler.py` (2 places)
- `backend/utils/page_manager.py` (5 places)
- `backend/utils/annotation_handler.py` (3 places)

**Quick script to find issues:**
```bash
grep -n "fitz.open" backend/utils/*.py | grep -v "with"
```

---

### 5. File Cleanup Mechanism - **2-3 hours**

**Current Problem:**
- 11 test PDFs in uploads (7MB)
- No automatic cleanup
- Will grow indefinitely

**Fix:**

**Step 1:** Create `cleanup.py`:
```python
#!/usr/bin/env python3
"""
Cleanup old files from uploads, sessions, and exports
"""

import os
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_old_files(folder, max_age_hours=24):
    """Delete files older than max_age_hours"""
    if not os.path.exists(folder):
        return
    
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    deleted_count = 0
    deleted_size = 0
    
    for filename in os.listdir(folder):
        if filename == '.gitkeep':
            continue
            
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff:
                size = os.path.getsize(filepath)
                os.remove(filepath)
                deleted_count += 1
                deleted_size += size
                logger.info(f"Deleted: {filename} ({size/1024:.1f}KB)")
    
    if deleted_count > 0:
        logger.info(f"Cleanup complete: {deleted_count} files, {deleted_size/1024/1024:.1f}MB freed")
    
    return deleted_count

if __name__ == '__main__':
    print("=" * 50)
    print("File Cleanup Utility")
    print("=" * 50)
    
    folders = [
        ('backend/uploads', 24),
        ('backend/sessions', 24),
        ('backend/exports', 48),
        ('uploads', 24),
        ('exports', 48),
    ]
    
    for folder, max_age in folders:
        print(f"\nCleaning {folder} (files older than {max_age}h)...")
        count = cleanup_old_files(folder, max_age)
        print(f"  Deleted: {count} files")
```

**Step 2:** Add to cron (Linux/Mac):
```bash
# Run cleanup every hour
0 * * * * cd /path/to/project && python3 cleanup.py >> logs/cleanup.log 2>&1
```

**Step 3:** Or add to app startup:
```python
# backend/app.py
from threading import Thread
import time

def cleanup_worker():
    """Background cleanup thread"""
    while True:
        time.sleep(3600)  # Every hour
        cleanup_old_files('backend/uploads', 24)
        cleanup_old_files('backend/exports', 48)

# Start cleanup thread
Thread(target=cleanup_worker, daemon=True).start()
```

---

### 6. Handle Stub API Routes - **20-40 hours OR 1 hour**

**Current Problem:**
16 API routes don't actually do anything:
- Page operations
- Annotations  
- Document operations
- Session save/load

**Option A: Implement them** (20-40 hours)
- Complete all 16 features
- Fully functional PDF editor

**Option B: Remove them** (1 hour - Recommended for now)
- Remove unused routes from `backend/api/routes.py`
- Mark as "future features" in documentation
- Focus on core functionality first

**Recommendation:** Option B for now, implement later as needed.

```python
# backend/api/routes.py
# Comment out or remove all stub routes

# Keep only working routes in backend/app.py:
# - /api/upload
# - /api/text/edit
# - /api/text/add
# - /api/text/delete
# - /api/save
# - /api/download
```

---

## 🟢 LOW PRIORITY (Code Quality)

### 7. Session Validation Decorator - **15 minutes**

**Benefit:** DRY principle, cleaner code

```python
# backend/decorators.py
from functools import wraps
from flask import request, jsonify

def require_session(session_manager):
    """Decorator to validate session"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.json or {}
            session_id = data.get('session_id')
            
            if not session_id or not session_manager.exists(session_id):
                return jsonify({'error': 'Invalid session'}), 404
            
            return f(session_id=session_id, *args, **kwargs)
        return decorated_function
    return decorator

# Usage:
@app.route('/api/text/edit', methods=['POST'])
@require_session(session_manager)
def edit_text(session_id):
    # session_id already validated!
    session = session_manager.load(session_id)
    ...
```

---

### 8. Add Docstrings - **2-3 hours**

Add missing docstrings to all classes and functions:

```python
def process_pdf(self, filepath, session_id):
    """
    Process PDF file and extract text with metadata.
    
    Args:
        filepath (str): Path to PDF file
        session_id (str): Unique session identifier
    
    Returns:
        dict: PDF data including pages, text blocks, and metadata
    
    Raises:
        Exception: If PDF processing fails
    """
    ...
```

---

## 📋 Implementation Order

### Week 1 (Critical):
1. ✅ **Day 1-2:** Implement session management (4-6 hours)
2. ✅ **Day 2:** Fix CORS configuration (30 minutes)
3. ✅ **Day 2-3:** Add logging infrastructure (2-3 hours)

### Week 2 (Important):
4. ✅ **Day 1-2:** Add resource cleanup (2-3 hours)
5. ✅ **Day 2-3:** Implement file cleanup (2-3 hours)
6. ✅ **Day 3:** Handle stub routes (1 hour to remove)

### Week 3 (Nice to Have):
7. ✅ **Day 1:** Add session decorator (15 minutes)
8. ✅ **Day 1-2:** Add docstrings (2-3 hours)
9. ✅ **Day 2-3:** Add unit tests

---

## 🧪 Testing After Fixes

### Test Session Management:
```bash
# Test persistence
1. Upload a PDF
2. Restart server
3. Try to edit the PDF (should still work!)
```

### Test CORS:
```bash
# Test from different origin
curl -H "Origin: http://evil.com" \
     -X POST http://localhost:5000/api/upload
# Should be blocked!
```

### Test File Cleanup:
```bash
python3 cleanup.py
# Check logs/cleanup.log
```

### Test Resource Cleanup:
```bash
# Monitor file handles
lsof -p $(pgrep -f "python.*app.py") | grep pdf | wc -l
# Should decrease after operations
```

---

## 📊 Before vs After

### Before Fixes:
- ❌ Sessions lost on restart
- ❌ CORS vulnerability
- ❌ Memory leaks
- ❌ Files accumulate forever
- ❌ No logging

**Production Ready:** 🔴 **NO** (6/10)

### After Fixes:
- ✅ Persistent sessions
- ✅ Secure CORS
- ✅ Proper resource cleanup
- ✅ Automatic file cleanup
- ✅ Full logging

**Production Ready:** ✅ **YES** (8.5/10)

---

## 💡 Quick Wins (Do Today!)

These take less than 30 minutes each:

1. **Fix CORS** (30 min)
2. **Add .env support** (10 min)
3. **Add health check endpoint** (5 min)
4. **Update .gitignore for logs/** (1 min)

```python
# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })
```

---

## 📝 Checklist

Use this to track your progress:

### Critical (Must Do):
- [ ] Implement persistent session storage
- [ ] Fix CORS configuration
- [ ] Add logging infrastructure

### Important (Should Do):
- [ ] Add resource cleanup (context managers)
- [ ] Implement file cleanup mechanism
- [ ] Remove or implement stub API routes

### Nice to Have:
- [ ] Add session validation decorator
- [ ] Add docstrings to functions
- [ ] Add unit tests
- [ ] Add .env support
- [ ] Add health check endpoint

---

**Total Estimated Time:** 15-25 hours (excluding stub implementations)

**Priority:** Start with Critical fixes (Days 1-3)

**Goal:** Production-ready in 2-3 weeks!

