#!/usr/bin/env python3
"""
Tiny transparent proxy for TransPerth API.
Just forwards requests with the required headers — no data processing.
The HTML does all the aggregation and rendering.
"""
import http.server
import urllib.request
import urllib.parse
import ssl
import os

PORT = 8080
API_BASE = 'https://www.transperth.wa.gov.au/API/'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'ModuleId': '5111',
    'TabId': '248',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.transperth.wa.gov.au/Timetables/Live-Train-Times',
    'Accept': 'application/json',
}

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            target = API_BASE + self.path[5:]  # self.path preserves %20 encoding
            req = urllib.request.Request(target, headers=HEADERS)
            ctx = ssl.create_default_context()
            try:
                with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(data)
            except urllib.error.HTTPError as e:
                # Pass through the upstream status code and body
                body = e.read() if e.fp else b'{}'
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(f'{{"error":"{e}"}}'.encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        if '/api/' in str(args[0]):
            super().log_message(format, *args)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f'\n  🚂 TransPerth Live Map Proxy')
    print(f'  Serving on http://localhost:{PORT}')
    print(f'  Press Ctrl+C to stop\n')
    http.server.test(HandlerClass=Handler, port=PORT)
