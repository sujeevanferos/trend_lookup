#!/usr/bin/env python3
"""
Simple HTTP server for EvolveX
Serves:
- UI from /ui/dist/index.html at root (/)
- Static assets from /ui/dist/assets/
- JSON outputs from /output/ directory
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from pathlib import Path

class EvolveXHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        super().__init__(*args, directory="/app", **kwargs)
    
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def translate_path(self, path):
        """Override to serve UI and outputs correctly"""
        # Remove query string
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Serve output JSON files
        if path.startswith('/output/'):
            return os.path.join('/app', path.lstrip('/'))
        
        # Serve UI assets
        if path.startswith('/assets/'):
            return os.path.join('/app/ui/dist', path.lstrip('/'))
        
        # Serve index.html for root and all other routes (SPA)
        return '/app/ui/dist/index.html'

if __name__ == '__main__':
    port = 8000
    print(f"🚀 EvolveX Server starting on http://0.0.0.0:{port}")
    print(f"   UI: http://localhost:{port}/")
    print(f"   API: http://localhost:{port}/output/")
    
    httpd = HTTPServer(('0.0.0.0', port), EvolveXHandler)
    httpd.serve_forever()
