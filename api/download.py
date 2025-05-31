#!/usr/bin/env python3
"""
Vercel Serverless Function for Twitter Spaces Download API
"""

import os
import re
import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterSpaceDownloader:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'noplaylist': True,
            'extract_flat': False,
        }
    
    def normalize_twitter_url(self, url):
        """Normalize Twitter/X URLs to ensure compatibility"""
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        url = url.replace('x.com', 'twitter.com')
        return url
    
    def validate_twitter_space_url(self, url):
        """Validate if the URL is a valid Twitter Spaces URL"""
        patterns = [
            r'https?://(www\.)?(twitter\.com|x\.com)/i/spaces/\w+',
            r'https?://(www\.)?(twitter\.com|x\.com)/.+/status/\d+',
            r'https?://t\.co/.+'
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    def extract_space_info(self, url):
        """Extract Twitter Spaces information without downloading"""
        try:
            url = self.normalize_twitter_url(url)
            
            if not self.validate_twitter_space_url(url):
                raise ValueError("Invalid Twitter Spaces URL. Please provide a valid Twitter Spaces link.")
            
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("Could not extract Twitter Spaces information")
                
                if 'entries' in info:
                    space_info = info['entries'][0] if info['entries'] else None
                else:
                    space_info = info
                
                if not space_info:
                    raise ValueError("No Twitter Spaces found in the provided URL")
                
                formats = []
                if 'formats' in space_info and space_info['formats']:
                    # 使用字典来存储每个分辨率的最佳格式
                    quality_formats = {}
                    for fmt in space_info['formats']:
                        # For Spaces, prioritize audio-only formats but also include video formats
                        if fmt.get('acodec') != 'none':  # Audio formats for Spaces
                            quality = self.get_audio_quality_label(fmt)
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
                                    'filename': f"{self.sanitize_filename(space_info.get('title', 'twitter_space'))}.{fmt.get('ext', 'mp4')}"
                                }
                    
                    # 将去重后的格式添加到列表中（去掉raw_filesize字段）
                    formats = [{k: v for k, v in f.items() if k != 'raw_filesize'} for f in quality_formats.values()]
                
                # If no formats found, try the direct URL
                if not formats and space_info.get('url'):
                    formats.append({
                        'format_id': 'direct',
                        'url': space_info['url'],
                        'ext': space_info.get('ext', 'mp4'),
                        'quality': 'Standard Audio',
                        'filesize': self.format_filesize(space_info.get('filesize')),
                        'filename': f"{self.sanitize_filename(space_info.get('title', 'twitter_space'))}.{space_info.get('ext', 'mp4')}"
                    })
                
                return {
                    'title': space_info.get('title', 'Twitter Space'),
                    'author': space_info.get('uploader', 'Unknown'),
                    'duration': self.format_duration(space_info.get('duration')),
                    'thumbnail': space_info.get('thumbnail', ''),
                    'formats': formats[:5] if formats else []
                }
                
        except Exception as e:
            logger.error(f"Error extracting Twitter Spaces info: {str(e)}")
            raise ValueError(f"Failed to extract Twitter Spaces information: {str(e)}")
    
    def get_audio_quality_label(self, fmt):
        """Generate a human-readable audio quality label for Spaces"""
        abr = fmt.get('abr')  # Audio bitrate
        acodec = fmt.get('acodec', '')
        
        if abr:
            if abr >= 320:
                return "High Quality Audio (320kbps)"
            elif abr >= 192:
                return "Standard Audio (192kbps)"
            elif abr >= 128:
                return "Good Audio (128kbps)"
            else:
                return f"Audio ({int(abr)}kbps)"
        elif 'mp4a' in acodec or 'aac' in acodec:
            return "AAC Audio"
        elif 'mp3' in acodec:
            return "MP3 Audio"
        else:
            return "Standard Audio"
    
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
            return "twitter_space"
        
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip().replace(' ', '_')
        return filename[:50]

# Initialize downloader
downloader = TwitterSpaceDownloader()

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(b'')

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not data or 'url' not in data:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Twitter Spaces URL is required'}).encode('utf-8'))
                return
            
            url = data['url']
            format_type = data.get('format', 'mp4')
            
            logger.info(f"Processing Twitter Spaces download request for: {url}")
            
            space_info = downloader.extract_space_info(url)
            
            if not space_info['formats']:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'No downloadable Twitter Spaces formats found'}).encode('utf-8'))
                return
            
            logger.info(f"Successfully extracted Twitter Spaces info: {space_info['title']}")
            
            self._set_headers(200)
            self.wfile.write(json.dumps(space_info).encode('utf-8'))
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Internal server error occurred while processing Twitter Spaces'}).encode('utf-8'))

    def do_GET(self):
        self._set_headers(405)
        self.wfile.write(json.dumps({'error': 'Method not allowed'}).encode('utf-8')) 