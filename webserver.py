"""Loopback-only demo HTTP server with bounded JSON requests and no content logging."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = 800_000


def make_handler(analyze, static_root):
    static_root = Path(static_root)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, body, content_type="application/json; charset=utf-8"):
            data = json.dumps(body, ensure_ascii=True).encode() if isinstance(body, dict) else body
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; script-src 'self'; style-src 'self'; "
                             "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)

        def valid_host(self):
            port = self.server.server_address[1]
            return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

        def do_GET(self):
            if not self.valid_host():
                return self.respond(403, {"error": "Use the localhost address printed at startup."})
            if self.path == "/health":
                return self.respond(200, {"status": "ok"})
            allowed = {"/": ("index.html", "text/html; charset=utf-8"),
                       "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                       "/style.css": ("style.css", "text/css; charset=utf-8")}
            if self.path not in allowed:
                return self.respond(404, {"error": "Not found"})
            name, mime = allowed[self.path]
            return self.respond(200, (static_root / name).read_bytes(), mime)

        def do_POST(self):
            if not self.valid_host():
                return self.respond(403, {"error": "Invalid host."})
            origin = self.headers.get("Origin")
            if origin and origin != "http://" + self.headers.get("Host", ""):
                return self.respond(403, {"error": "Cross-origin requests are not supported."})
            if self.path != "/api/analyze":
                return self.respond(404, {"error": "Not found"})
            if self.headers.get_content_type() != "application/json":
                return self.respond(415, {"error": "Send application/json."})
            if self.headers.get("Transfer-Encoding"):
                return self.respond(400, {"error": "Chunked requests are not supported."})
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return self.respond(400, {"error": "Invalid Content-Length."})
            if length <= 0 or length > MAX_BODY:
                return self.respond(413, {"error": "Request is empty or too large."})
            self.connection.settimeout(5)
            try:
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("JSON body must be an object.")
                result = analyze(payload)
            except (ValueError, UnicodeError, TypeError) as error:
                return self.respond(400, {"error": str(error)})
            except TimeoutError:
                return self.respond(408, {"error": "Request timed out."})
            return self.respond(200, result)

    return Handler


def serve(handler, port):
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"Open http://127.0.0.1:{port} (Ctrl+C to stop)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
