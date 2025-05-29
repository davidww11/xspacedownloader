#!/usr/bin/env python3
"""
Simple runner script for the Twitter Video Downloader
"""

import os
import sys
import subprocess

def check_and_install_dependencies():
    """Check if development dependencies are installed, and install if missing"""
    try:
        import flask
        import yt_dlp
        import flask_cors
        return True
    except ImportError as e:
        print(f"⚠️  Missing development dependency: {e}")
        print("\n🔧 Installing development dependencies...")
        
        # Try to install development dependencies
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-dev.txt'])
            print("✅ Development dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("\n❌ Failed to install dependencies automatically.")
            print("Please install dependencies manually:")
            print("  pip install -r requirements-dev.txt")
            print("\nOr install individual packages:")
            print("  pip install Flask Flask-CORS yt-dlp requests Werkzeug")
            return False

if __name__ == '__main__':
    # Check and install dependencies if needed
    if not check_and_install_dependencies():
        sys.exit(1)
    
    # Import after ensuring dependencies are available
    try:
        from app import app
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("Please ensure all dependencies are installed correctly.")
        sys.exit(1)
    
    # Configure Flask to serve static files
    app.static_folder = '.'
    app.static_url_path = ''
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Twitter Video Downloader on http://localhost:{port}")
    print("📁 Make sure your HTML files are in the current directory")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use!")
            print("Try using a different port:")
            print(f"  PORT=8000 python3 run.py")
            print("\nOr on macOS, disable AirPlay Receiver in System Preferences > Sharing")
        else:
            print(f"❌ Failed to start server: {e}")
        sys.exit(1) 