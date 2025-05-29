#!/usr/bin/env python3
"""
Health check endpoint for Vercel deployment
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(b'')

    def do_GET(self):
        self._set_headers(200)
        response = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'platform': 'vercel'
        }
        self.wfile.write(json.dumps(response).encode('utf-8')) 