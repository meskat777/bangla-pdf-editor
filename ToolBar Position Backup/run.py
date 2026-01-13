#!/usr/bin/env python3
"""
Bangla PDF Editor - Startup Script
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app
from config import config

if __name__ == '__main__':
    # Get environment
    env = os.environ.get('FLASK_ENV', 'development')
    app_config = config.get(env, config['default'])
    
    print("=" * 50)
    print("বাংলা পিডিএফ এডিটর | Bangla PDF Editor")
    print("=" * 50)
    print(f"Environment: {env}")
    print(f"Debug Mode: {app_config.DEBUG}")
    print(f"Server: http://{app_config.HOST}:{app_config.PORT}")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run server
    app.run(
        host=app_config.HOST,
        port=app_config.PORT,
        debug=app_config.DEBUG
    )
