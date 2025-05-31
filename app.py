#!/usr/bin/env python3
"""
Twitter Space Downloader API
A Flask-based API for downloading Twitter/X Spaces using yt-dlp
"""

import os
import re
import json
import logging
import tempfile
import smtplib
import hashlib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
import yt_dlp
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend integration

# Configuration
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), 'twitter_spaces')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class TwitterSpaceDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best[ext=m4a]/best[ext=mp3]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'extract_flat': False,
            'writeinfojson': False,
            'extractaudio': True,
            'audioformat': 'mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
    def normalize_twitter_url(self, url):
        """Normalize Twitter/X URLs to ensure compatibility"""
        # Handle t.co redirects and convert x.com to twitter.com for yt-dlp compatibility
        url = url.strip()
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Convert x.com to twitter.com for better compatibility
        url = url.replace('x.com', 'twitter.com')
        
        return url
    
    def validate_twitter_space_url(self, url):
        """Validate if the URL is a valid Twitter Space URL"""
        patterns = [
            r'https?://(www\.)?(twitter\.com|x\.com)/i/spaces/[a-zA-Z0-9]+',
            r'https?://(www\.)?(twitter\.com|x\.com)/.+/status/\d+',
            r'https?://t\.co/.+'
        ]
        
        return any(re.match(pattern, url) for pattern in patterns)
    
    def generate_safe_filename(self, title):
        """Generate a safe filename from the space title"""
        if not title:
            title = "twitter_space"
        
        # Remove or replace invalid characters
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        safe_title = safe_title.strip().replace(' ', '_')
        
        # Limit length and add hash for uniqueness
        url_hash = hashlib.md5(title.encode()).hexdigest()[:8]
        safe_title = safe_title[:30] + f"_{url_hash}"
        
        return f"{safe_title}.mp3"
    
    def download_space_audio(self, url):
        """Actually download the Twitter Space audio file"""
        try:
            url = self.normalize_twitter_url(url)
            
            if not self.validate_twitter_space_url(url):
                raise ValueError("Invalid Twitter Space URL")
            
            logger.info(f"Starting download for Space: {url}")
            
            # First, extract info to get title
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("Could not extract Space information")
                
                # Check if it contains audio
                if 'entries' in info:
                    space_info = info['entries'][0] if info['entries'] else None
                else:
                    space_info = info
                
                if not space_info:
                    raise ValueError("No Space found in the provided URL")
                
                title = space_info.get('title', 'Twitter Space')
                author = space_info.get('uploader', 'Unknown')
                duration = self.format_duration(space_info.get('duration'))
                thumbnail = space_info.get('thumbnail', '')
            
            # Generate safe filename
            filename = self.generate_safe_filename(title)
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                logger.info(f"File already exists: {filename}")
                return {
                    'title': title,
                    'author': author,
                    'duration': duration,
                    'thumbnail': thumbnail,
                    'filename': filename,
                    'filepath': filepath,
                    'download_url': f'/download/{filename}',
                    'filesize': self.format_filesize(os.path.getsize(filepath))
                }
            
            # Configure yt-dlp for actual download
            download_opts = self.ydl_opts.copy()
            download_opts['outtmpl'] = filepath.replace('.mp3', '.%(ext)s')
            
            # Download the audio
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                logger.info(f"Downloading Space audio: {title}")
                ydl.download([url])
            
            # Check if download was successful
            if not os.path.exists(filepath):
                # Sometimes the extension might be different, look for the file
                base_name = filepath.replace('.mp3', '')
                for ext in ['.mp3', '.m4a', '.webm', '.mp4']:
                    alt_path = base_name + ext
                    if os.path.exists(alt_path):
                        # Rename to .mp3
                        os.rename(alt_path, filepath)
                        break
                else:
                    raise ValueError("Download completed but file not found")
            
            logger.info(f"Successfully downloaded: {filename}")
            
            return {
                'title': title,
                'author': author,
                'duration': duration,
                'thumbnail': thumbnail,
                'filename': filename,
                'filepath': filepath,
                'download_url': f'/download/{filename}',
                'filesize': self.format_filesize(os.path.getsize(filepath))
            }
                
        except Exception as e:
            logger.error(f"Error downloading Space: {str(e)}")
            raise ValueError(f"Failed to download Space: {str(e)}")

    def extract_space_info(self, url):
        """Extract Space information without downloading (legacy method)"""
        try:
            url = self.normalize_twitter_url(url)
            
            if not self.validate_twitter_space_url(url):
                raise ValueError("Invalid Twitter Space URL")
            
            # Extract info only
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("Could not extract Space information")
                
                # Check if it contains audio
                if 'entries' in info:
                    # It's a playlist, get the first entry
                    space_info = info['entries'][0] if info['entries'] else None
                else:
                    space_info = info
                
                if not space_info:
                    raise ValueError("No Space found in the provided URL")
                
                # Extract available formats (audio only)
                formats = []
                if 'formats' in space_info and space_info['formats']:
                    # Filter for audio formats only
                    audio_formats = {}
                    for fmt in space_info['formats']:
                        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':  # Audio only
                            quality = self.get_audio_quality_label(fmt)
                            # Get current format file size
                            try:
                                current_size = int(fmt.get('filesize') or 0)
                            except Exception:
                                current_size = 0
                            try:
                                prev_size = int(audio_formats[quality].get('raw_filesize', 0)) if quality in audio_formats else 0
                            except Exception:
                                prev_size = 0
                            # Keep the format with larger file size (better quality)
                            if quality not in audio_formats or current_size > prev_size:
                                audio_formats[quality] = {
                                    'format_id': fmt.get('format_id', ''),
                                    'url': fmt.get('url', ''),
                                    'ext': 'mp3',  # Convert all to MP3
                                    'quality': quality,
                                    'filesize': self.format_filesize(fmt.get('filesize')),
                                    'raw_filesize': current_size,
                                    'filename': f"{self.sanitize_filename(space_info.get('title', 'space'))}.mp3"
                                }
                    
                    # Convert to list without raw_filesize
                    formats = [{k: v for k, v in f.items() if k != 'raw_filesize'} for f in audio_formats.values()]
                
                # If no formats found, try the direct URL
                if not formats and space_info.get('url'):
                    formats.append({
                        'format_id': 'direct',
                        'url': space_info['url'],
                        'ext': 'mp3',
                        'quality': 'Standard Quality',
                        'filesize': self.format_filesize(space_info.get('filesize')),
                        'filename': f"{self.sanitize_filename(space_info.get('title', 'space'))}.mp3"
                    })
                
                return {
                    'title': space_info.get('title', 'Twitter Space'),
                    'author': space_info.get('uploader', 'Unknown'),
                    'duration': self.format_duration(space_info.get('duration')),
                    'thumbnail': space_info.get('thumbnail', ''),
                    'formats': formats[:3] if formats else []  # Limit to 3 formats
                }
                
        except Exception as e:
            logger.error(f"Error extracting Space info: {str(e)}")
            raise ValueError(f"Failed to extract Space information: {str(e)}")
    
    def get_audio_quality_label(self, fmt):
        """Generate a human-readable audio quality label"""
        abr = fmt.get('abr')  # Audio bitrate
        asr = fmt.get('asr')  # Audio sample rate
        
        if abr:
            if abr >= 320:
                return "High Quality (320kbps)"
            elif abr >= 256:
                return "High Quality (256kbps)"
            elif abr >= 192:
                return "Good Quality (192kbps)"
            elif abr >= 128:
                return "Standard Quality (128kbps)"
            else:
                return f"Basic Quality ({int(abr)}kbps)"
        elif asr:
            if asr >= 48000:
                return "High Quality (48kHz)"
            elif asr >= 44100:
                return "CD Quality (44.1kHz)"
            else:
                return "Standard Quality"
        else:
            return "Standard Quality"
    
    def process_space_download(self, url, email):
        """Process Space download and send email notification"""
        try:
            # Extract Space info
            space_info = self.extract_space_info(url)
            
            # In a real implementation, you would:
            # 1. Add the download job to a queue
            # 2. Process the download in the background
            # 3. Send email when complete
            
            # For MVP, we'll simulate the process
            logger.info(f"Processing Space download for: {space_info['title']} -> {email}")
            
            # Simulate email sending
            self.send_notification_email(email, space_info)
            
            return {
                'success': True,
                'message': 'Your Space download request has been queued',
                'space_info': space_info
            }
            
        except Exception as e:
            logger.error(f"Error processing Space download: {str(e)}")
            raise ValueError(f"Failed to process Space download: {str(e)}")
    
    def send_notification_email(self, email, space_info):
        """Send download notification email (simulated for MVP)"""
        # In a real implementation, you would configure SMTP settings
        # and send actual emails with download links
        logger.info(f"Simulating email to {email} for Space: {space_info['title']}")
        
        # For MVP, we just log the email content
        email_content = f"""
        Subject: Your Twitter Space Download is Ready!
        
        Hi there!
        
        Your Twitter Space download is ready:
        
        Title: {space_info['title']}
        Author: {space_info['author']}
        Duration: {space_info['duration']}
        
        Download Link: [This would be a real download link in production]
        
        Thank you for using our Twitter Space Downloader!
        """
        
        logger.info(f"Email content:\n{email_content}")
        return True

    def format_filesize(self, size):
        """Format file size in human readable format"""
        if not size:
            return "Unknown size"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def format_duration(self, duration):
        """Format duration in human readable format"""
        if not duration:
            return "Unknown"
        
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def sanitize_filename(self, filename):
        """Sanitize filename for safe download"""
        if not filename:
            return "space"
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip().replace(' ', '_')
        return filename[:50]  # Limit length

# Initialize downloader
downloader = TwitterSpaceDownloader()

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_file('static/images/logo.svg', mimetype='image/svg+xml')

@app.route('/')
def home():
    """Serve the main page"""
    return send_file('index.html')

@app.route('/test')
def test_page():
    """Serve the test page"""
    return app.send_static_file('test.html')

@app.route('/debug')
def debug_page():
    """Serve the debug page"""
    return app.send_static_file('debug.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Serve downloaded audio files"""
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(DOWNLOAD_DIR, safe_filename)
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            abort(404)
        
        logger.info(f"Serving file: {safe_filename}")
        return send_file(filepath, as_attachment=True, download_name=safe_filename)
        
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        abort(500)

@app.route('/api/process-space', methods=['POST'])
def process_space():
    """API endpoint to process Space download requests"""
    try:
        data = request.get_json()
        if not data or 'url' not in data or 'email' not in data:
            return jsonify({'error': 'URL and email are required'}), 400
        
        url = data['url']
        email = data['email']
        
        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        logger.info(f"Processing Space download request for: {url} -> {email}")
        
        # Process the Space download
        result = downloader.process_space_download(url, email)
        
        logger.info(f"Successfully queued Space download: {result['space_info']['title']}")
        
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    """Legacy API endpoint - redirects to space processing"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        
        logger.info(f"Legacy endpoint called for: {url}")
        
        # Extract Space information for legacy compatibility
        space_info = downloader.extract_space_info(url)
        
        logger.info(f"Successfully extracted Space info: {space_info['title']}")
        
        return jsonify(space_info)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/api/download-space', methods=['POST'])
def download_space_direct():
    """API endpoint to download Twitter Spaces and provide download links"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        
        logger.info(f"Processing direct Space download for: {url}")
        
        # Download the Space audio file
        result = downloader.download_space_audio(url)
        
        logger.info(f"Successfully downloaded Space: {result['title']}")
        
        # Return the local download information
        return jsonify({
            'title': result['title'],
            'author': result['author'],
            'duration': result['duration'],
            'thumbnail': result['thumbnail'],
            'formats': [{
                'format_id': 'mp3',
                'url': result['download_url'],
                'ext': 'mp3',
                'quality': 'High Quality (192kbps)',
                'filesize': result['filesize'],
                'filename': result['filename']
            }]
        })
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Twitter Space Downloader API on port {port}")
    logger.info(f"Download directory: {DOWNLOAD_DIR}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 