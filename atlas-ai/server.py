"""Local server. Binds to localhost and serves only public application files."""
import argparse
from pathlib import Path
from http.server import ThreadingHTTPServer
from api.atlas import handler as API

PUBLIC = Path(__file__).parent / 'public'

class Handler(API):
    def do_GET(self):
        if self.path.startswith('/api/atlas'):
            return super().do_GET()
        name = {'/': 'index.html', '/index.html': 'index.html', '/app.js': 'app.js', '/styles.css': 'styles.css'}.get(self.path.split('?')[0])
        if not name:
            return self.respond(404, {'error': 'Not found'})
        body = (PUBLIC / name).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', {'html': 'text/html', 'js': 'text/javascript', 'css': 'text/css'}[name.split('.')[-1]] + '; charset=utf-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--host', default='127.0.0.1')
    args = parser.parse_args()
    print(f'Atlas AI Studio: http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
