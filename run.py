#!/usr/bin/env python3
"""
Simple runner script for the Twitter Video Downloader
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Check if dependencies are installed
    try:
        import flask
        import yt_dlp
        import flask_cors
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Configure Flask to serve static files
    app.static_folder = '.'
    app.static_url_path = ''
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Twitter Video Downloader on http://localhost:{port}")
    print("📁 Make sure your HTML files are in the current directory")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 