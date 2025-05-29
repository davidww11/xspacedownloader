#!/usr/bin/env python3
"""
Health check endpoint for Vercel deployment
"""

from datetime import datetime
from flask import jsonify

def handler(request):
    """Health check handler"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    return (jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'platform': 'vercel'
    }), 200, headers) 