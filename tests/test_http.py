import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from webserver import make_handler


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / "static"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0),
                                        make_handler(lambda p: {"ok": p.get("value")}, root))
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body, headers or {})
        response = conn.getresponse()
        result = (response.status, response.read(), dict(response.getheaders()))
        conn.close()
        return result

    def test_static_page_and_headers(self):
        status, body, headers = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"<!doctype html>", body)
        self.assertIn("Content-Security-Policy", headers)

    def test_json_request(self):
        status, body, _ = self.request("POST", "/api/analyze", '{"value":42}',
                                       {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"ok": 42})

    def test_malformed_and_non_object_json(self):
        for body in ("{", "[]", "null"):
            self.assertEqual(self.request("POST", "/api/analyze", body,
                             {"Content-Type": "application/json"})[0], 400)

    def test_unsupported_media(self):
        self.assertEqual(self.request("POST", "/api/analyze", "test")[0], 415)

    def test_cross_origin_rejected(self):
        self.assertEqual(self.request("POST", "/api/analyze", "{}",
                         {"Content-Type": "application/json", "Origin": "https://example.com"})[0], 403)

    def test_bad_host_and_traversal(self):
        self.assertEqual(self.request("GET", "/", headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request("GET", "/../analyzer.py")[0], 404)

    def test_oversized_request(self):
        self.assertEqual(self.request("POST", "/api/analyze", "{}",
                         {"Content-Type": "application/json", "Content-Length": "800001"})[0], 413)
