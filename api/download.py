#!/usr/bin/env python3
"""
Vercel Serverless Function for Twitter Video Download API
"""

import os
import re
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class TwitterVideoDownloader:
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
            
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("Could not extract video information")
                
                if 'entries' in info:
                    video_info = info['entries'][0] if info['entries'] else None
                else:
                    video_info = info
                
                if not video_info:
                    raise ValueError("No video found in the provided URL")
                
                formats = []
                if 'formats' in video_info and video_info['formats']:
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            quality = self.get_quality_label(fmt)
                            formats.append({
                                'format_id': fmt.get('format_id', ''),
                                'url': fmt.get('url', ''),
                                'ext': fmt.get('ext', 'mp4'),
                                'quality': quality,
                                'filesize': self.format_filesize(fmt.get('filesize')),
                                'filename': f"{self.sanitize_filename(video_info.get('title', 'video'))}.{fmt.get('ext', 'mp4')}"
                            })
                
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
                    'formats': formats[:5] if formats else []
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
        
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip().replace(' ', '_')
        return filename[:50]

# Initialize downloader
downloader = TwitterVideoDownloader()

def handler(request):
    """Vercel serverless function handler"""
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                return (jsonify({'error': 'URL is required'}), 400, headers)
            
            url = data['url']
            format_type = data.get('format', 'mp4')
            
            logger.info(f"Processing download request for: {url}")
            
            video_info = downloader.extract_video_info(url)
            
            if not video_info['formats']:
                return (jsonify({'error': 'No downloadable video formats found'}), 404, headers)
            
            logger.info(f"Successfully extracted video info: {video_info['title']}")
            
            return (jsonify(video_info), 200, headers)
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return (jsonify({'error': str(e)}), 400, headers)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return (jsonify({'error': 'Internal server error occurred'}), 500, headers)
    
    return (jsonify({'error': 'Method not allowed'}), 405, headers) 