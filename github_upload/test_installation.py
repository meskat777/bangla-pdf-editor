#!/usr/bin/env python3
"""
Test Installation Script for Bangla PDF Editor
Run this to verify all dependencies are installed correctly
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing Python package imports...\n")
    
    packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'fitz': 'PyMuPDF',
        'easyocr': 'EasyOCR',
        'PIL': 'Pillow',
        'werkzeug': 'Werkzeug',
        'numpy': 'NumPy'
    }
    
    failed = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name:20} - OK")
        except ImportError as e:
            print(f"❌ {name:20} - FAILED")
            failed.append(name)
    
    print()
    
    if failed:
        print(f"❌ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully!")
        return True

def test_directories():
    """Test if all required directories exist"""
    import os
    
    print("\n🔍 Testing directory structure...\n")
    
    directories = [
        'backend',
        'backend/utils',
        'backend/api',
        'frontend',
        'frontend/templates',
        'frontend/static',
        'frontend/static/css',
        'frontend/static/js',
        'fonts',
        'uploads',
        'sessions',
        'exports'
    ]
    
    failed = []
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory:30} - OK")
        else:
            print(f"❌ {directory:30} - MISSING")
            failed.append(directory)
    
    print()
    
    if failed:
        print(f"❌ Missing directories: {', '.join(failed)}")
        return False
    else:
        print("✅ All directories exist!")
        return True

def test_files():
    """Test if all required files exist"""
    import os
    
    print("\n🔍 Testing required files...\n")
    
    files = [
        'backend/app.py',
        'backend/utils/pdf_processor.py',
        'backend/utils/ocr_handler.py',
        'backend/utils/text_editor.py',
        'frontend/templates/index.html',
        'frontend/static/css/style.css',
        'frontend/static/js/app.js',
        'config.py',
        'run.py',
        'requirements.txt'
    ]
    
    failed = []
    
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file:40} - OK")
        else:
            print(f"❌ {file:40} - MISSING")
            failed.append(file)
    
    print()
    
    if failed:
        print(f"❌ Missing files: {', '.join(failed)}")
        return False
    else:
        print("✅ All required files exist!")
        return True

def test_fonts():
    """Test if Bangla fonts are available"""
    import os
    
    print("\n🔍 Testing Bangla fonts...\n")
    
    fonts_dir = 'fonts'
    
    if not os.path.exists(fonts_dir):
        print(f"❌ Fonts directory not found!")
        return False
    
    font_files = [f for f in os.listdir(fonts_dir) 
                  if f.lower().endswith(('.ttf', '.otf'))]
    
    if font_files:
        print(f"✅ Found {len(font_files)} font files:")
        for font in font_files[:10]:  # Show first 10
            print(f"   - {font}")
        if len(font_files) > 10:
            print(f"   ... and {len(font_files) - 10} more")
        return True
    else:
        print(f"❌ No font files found in {fonts_dir}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("  Bangla PDF Editor - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("Directory Structure", test_directories()))
    results.append(("Required Files", test_files()))
    results.append(("Bangla Fonts", test_fonts()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    print()
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("🎉 All tests passed! Your installation is complete.")
        print()
        print("Next steps:")
        print("  1. Run: python run.py")
        print("  2. Open: http://localhost:5000")
        print("  3. Upload a PDF and start editing!")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print()
        print("Common fixes:")
        print("  - Run: pip install -r requirements.txt")
        print("  - Verify all files are extracted correctly")
        return 1

if __name__ == '__main__':
    sys.exit(main())
