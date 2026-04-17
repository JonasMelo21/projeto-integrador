#!/usr/bin/env python3
"""Proxy server para contornar CORS durante desenvolvimento"""
import http.server
import socketserver
import urllib.request
import json
import sys
import os

PORT = 5173
BACKEND_URL = "http://localhost:8000"

class CORSProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            # Proxy API requests
            backend_path = self.path.replace('/api/', '/api/')
            url = BACKEND_URL + backend_path
            
            try:
                response = urllib.request.urlopen(url)
                data = response.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            # Serve static files
            super().do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

if __name__ == "__main__":
    os.chdir("/home/jonasmelo/projectsandstudies/Projeto Integrador III 2.0/frontend")
    
    with socketserver.TCPServer(("", PORT), CORSProxyHandler) as httpd:
        print(f"🚀 Servidor proxy rodando em http://localhost:{PORT}")
        print(f"   Arquivos estáticos: /frontend/")
        print(f"   Proxy API: /api/* -> http://localhost:8000/api/*")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Servidor encerrado")
