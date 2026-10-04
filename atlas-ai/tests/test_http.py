import json
import sys
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Handler

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, path, payload=None, headers=None):
        request = urllib.request.Request(self.url + path, data=json.dumps(payload).encode() if payload is not None else None, headers=headers or {'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, response.read(), response.headers
        except urllib.error.HTTPError as error:
            return error.code, error.read(), error.headers

    def test_health_static_and_private_files(self):
        self.assertEqual(self.request('/api/atlas')[0], 200)
        status, _, headers = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn("script-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/api/core.py')[0], 404)
        self.assertEqual(self.request('/../server.py')[0], 404)

    def test_analysis_contract(self):
        status, body, _ = self.request('/api/atlas', {'mode': 'research', 'question': 'orchard', 'documents': [{'name': 'note', 'text': 'Orchard telemetry.'}]})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['engine'], 'local')

    def test_invalid_json_type_and_origin(self):
        self.assertEqual(self.request('/api/atlas', {'mode': 'other'})[0], 400)
        self.assertEqual(self.request('/api/atlas', {}, {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('/api/atlas', {}, {'Content-Type': 'application/json', 'Origin': 'https://other.example'})[0], 403)

    def test_hosted_ai_requires_token(self):
        with patch.dict('os.environ', {'VERCEL': '1', 'ATLAS_ACCESS_TOKEN': ''}):
            status, _, _ = self.request('/api/atlas', {'mode': 'code', 'ai': True})
            self.assertEqual(status, 403)

if __name__ == '__main__':
    unittest.main()
