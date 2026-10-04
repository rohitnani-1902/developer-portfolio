import hmac
import json
import os
import time
import threading
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from atlas_backend.core import InputError, model_config, run

_lock = threading.Lock()
_active = 0
_recent = []

class handler(BaseHTTPRequestHandler):
    def respond(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        configured = bool(model_config())
        # A shared server token is required for billable generation on hosted instances.
        self.respond(200, {'ok': True, 'ai_configured': configured, 'ai_available': configured and (not os.getenv('VERCEL') or bool(os.getenv('ATLAS_ACCESS_TOKEN'))), 'version': '1.0.0'})

    def do_POST(self):
        global _active
        active = False
        try:
            if urlparse(self.path).path != '/api/atlas':
                return self.respond(404, {'error': 'Not found'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.respond(415, {'error': 'Send JSON content.'})
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 1000000:
                return self.respond(413, {'error': 'Request is empty or exceeds 1 MB.'})
            origin = self.headers.get('Origin')
            if origin and urlparse(origin).netloc != self.headers.get('Host'):
                return self.respond(403, {'error': 'Cross-origin requests are not allowed.'})
            payload = json.loads(self.rfile.read(size))
            if isinstance(payload, dict) and payload.get('ai'):
                token = os.getenv('ATLAS_ACCESS_TOKEN', '')
                if (os.getenv('VERCEL') and not token) or (token and not hmac.compare_digest(self.headers.get('X-Atlas-Token', ''), token)):
                    return self.respond(403, {'error': 'AI synthesis requires the workspace access token. Local analysis is available.'})
                with _lock:
                    now = time.monotonic()
                    _recent[:] = [t for t in _recent if now - t < 60]
                    if _active >= 2 or len(_recent) >= 6:
                        return self.respond(429, {'error': 'AI request limit reached. Please retry shortly.'})
                    _active += 1
                    _recent.append(now)
                    active = True
            self.respond(200, run(payload))
        except (InputError, ValueError, UnicodeDecodeError):
            self.respond(400, {'error': 'Invalid input. Use up to 12 text sources, 50,000 characters each, and a task under 2,000 characters.'})
        except RuntimeError as error:
            self.respond(502, {'error': str(error)})
        except Exception:
            self.respond(500, {'error': 'The request could not be completed.'})
        finally:
            if active:
                with _lock:
                    _active -= 1

    def log_message(self, *args):
        pass
