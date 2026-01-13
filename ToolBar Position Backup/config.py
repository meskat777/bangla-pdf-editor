"""
Configuration file for Bangla PDF Editor
"""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables only

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Folders
    UPLOAD_FOLDER = 'uploads'
    SESSION_FOLDER = 'sessions'
    EXPORT_FOLDER = 'exports'
    FONTS_FOLDER = 'fonts'
    
    # Session
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    AUTO_CLEANUP = True
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
    
    # OCR
    OCR_LANGUAGES = ['bn', 'en']  # Bengali and English
    OCR_GPU = False  # Set to True if GPU available
    
    # PDF Processing
    DEFAULT_DPI = 150
    MAX_DPI = 300
    MIN_DPI = 72
    
    # Server
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Use stronger secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Disable auto-reload
    TEMPLATES_AUTO_RELOAD = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
