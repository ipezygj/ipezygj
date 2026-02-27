""" 
The Alpha API - Craftsman Edition.
Serves the latest signals from signals_output.json.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class AlphaAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/signals':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if os.path.exists('signals_output.json'):
                with open('signals_output.json', 'r') as f:
                    # Luetaan viimeisimmät 10 signaalia
                    lines = f.readlines()
                    signals = [json.loads(line) for line in lines[-10:]]
                    self.wfile.write(json.dumps(signals).encode())
            else:
                self.wfile.write(json.dumps({"status": "waiting for data"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_api_server(port=8888):
    server = HTTPServer(('0.0.0.0', port), AlphaAPIHandler)
    print(f"📡 [API SERVER] Alpha Feed live at http://localhost:{port}/signals")
    server.serve_forever()

if __name__ == "__main__":
    run_api_server()
