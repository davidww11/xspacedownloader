#!/usr/bin/env python3
"""
Twitter Video Downloader API
A Flask-based API for downloading Twitter/X videos using yt-dlp
"""

import os
import re
import json
import logging
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend integration

# Configuration
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), 'twitter_downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class TwitterVideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'extract_flat': False,
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
    
    def validate_twitter_url(self, url):
        """Validate if the URL is a valid Twitter video URL"""
        patterns = [
            r'https?://(www\.)?(twitter\.com|x\.com)/.+/status/\d+',
            r'https?://t\.co/.+'
        ]
        
        return any(re.match(pattern, url) for pattern in patterns)
    
    def extract_video_info(self, url):
        """Extract video information without downloading"""
        try:
            url = self.normalize_twitter_url(url)
            
            if not self.validate_twitter_url(url):
                raise ValueError("Invalid Twitter URL")
            
            # Extract info only
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("Could not extract video information")
                
                # Check if it contains video
                if 'entries' in info:
                    # It's a playlist, get the first video
                    video_info = info['entries'][0] if info['entries'] else None
                else:
                    video_info = info
                
                if not video_info:
                    raise ValueError("No video found in the provided URL")
                
                # Extract available formats
                formats = []
                if 'formats' in video_info and video_info['formats']:
                    # 使用字典来存储每个分辨率的最佳格式
                    quality_formats = {}
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':  # Only video formats
                            quality = self.get_quality_label(fmt)
                            # 获取当前格式的文件大小，确保为数字
                            try:
                                current_size = int(fmt.get('filesize') or 0)
                            except Exception:
                                current_size = 0
                            try:
                                prev_size = int(quality_formats[quality].get('raw_filesize', 0)) if quality in quality_formats else 0
                            except Exception:
                                prev_size = 0
                            # 如果这个分辨率还没有记录，或者当前格式的文件大小更大（质量更好），则更新
                            if quality not in quality_formats or current_size > prev_size:
                                quality_formats[quality] = {
                                    'format_id': fmt.get('format_id', ''),
                                    'url': fmt.get('url', ''),
                                    'ext': fmt.get('ext', 'mp4'),
                                    'quality': quality,
                                    'filesize': self.format_filesize(fmt.get('filesize')),
                                    'raw_filesize': current_size,
                                    'filename': f"{self.sanitize_filename(video_info.get('title', 'video'))}.{fmt.get('ext', 'mp4')}"
                                }
                    
                    # 将去重后的格式添加到列表中（去掉raw_filesize字段）
                    formats = [{k: v for k, v in f.items() if k != 'raw_filesize'} for f in quality_formats.values()]
                
                # If no formats found, try the direct URL
                if not formats and video_info.get('url'):
                    formats.append({
                        'format_id': 'direct',
                        'url': video_info['url'],
                        'ext': video_info.get('ext', 'mp4'),
                        'quality': 'Standard Quality',
                        'filesize': self.format_filesize(video_info.get('filesize')),
                        'filename': f"{self.sanitize_filename(video_info.get('title', 'video'))}.{video_info.get('ext', 'mp4')}"
                    })
                
                return {
                    'title': video_info.get('title', 'Twitter Video'),
                    'author': video_info.get('uploader', 'Unknown'),
                    'duration': self.format_duration(video_info.get('duration')),
                    'thumbnail': video_info.get('thumbnail', ''),
                    'formats': formats[:5] if formats else []  # Limit to 5 formats
                }
                
        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            raise ValueError(f"Failed to extract video information: {str(e)}")
    
    def get_quality_label(self, fmt):
        """Generate a human-readable quality label"""
        height = fmt.get('height')
        width = fmt.get('width')
        
        if height:
            if height >= 1080:
                return "1080p HD"
            elif height >= 720:
                return "720p HD"
            elif height >= 480:
                return "480p"
            elif height >= 360:
                return "360p"
            else:
                return f"{height}p"
        elif width:
            if width >= 1920:
                return "1080p HD"
            elif width >= 1280:
                return "720p HD"
            else:
                return "Standard Quality"
        else:
            return "Standard Quality"
    
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
        
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def sanitize_filename(self, filename):
        """Sanitize filename for safe download"""
        if not filename:
            return "video"
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip().replace(' ', '_')
        return filename[:50]  # Limit length

# Initialize downloader
downloader = TwitterVideoDownloader()

@app.route('/')
def home():
    """Serve the main page"""
    return app.send_static_file('index.html')

@app.route('/test')
def test_page():
    """Serve the test page"""
    return app.send_static_file('test.html')

@app.route('/debug')
def debug_page():
    """Serve the debug page"""
    return app.send_static_file('debug.html')

@app.route('/api/download', methods=['POST'])
def download_video():
    """API endpoint to process video download requests"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        format_type = data.get('format', 'mp4')
        
        logger.info(f"Processing download request for: {url}")
        
        # Extract video information
        video_info = downloader.extract_video_info(url)
        
        if not video_info['formats']:
            return jsonify({'error': 'No downloadable video formats found'}), 404
        
        logger.info(f"Successfully extracted video info: {video_info['title']}")
        
        return jsonify(video_info)
        
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
    
    logger.info(f"Starting Twitter Video Downloader API on port {port}")
    logger.info(f"Download directory: {DOWNLOAD_DIR}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 