
import mimetypes
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from solver import solve_payload

ROOT = Path(__file__).parent
HOST = "127.0.0.1"
PORT = 8000

mimetypes.add_type("font/ttf", ".ttf")  # not in every platform's mime table
mimetypes.add_type("text/x-python", ".py")  # the page fetches solver.py to run it


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        # the page solves in the browser now, but this endpoint still answers
        # so the two paths can be compared against each other
        if self.path.rstrip("/") != "/api/solve":
            self.send_error(404, "unknown endpoint")
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "expected a JSON body")
            return

        words = [w for w in (payload.get("words") or []) if isinstance(w, str)]
        self.send_json(solve_payload(payload.get("grid") or "", words))

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # so edits show up on refresh
        super().end_headers()

    def log_message(self, *_args):
        pass  # the server does not need to narrate every request


if __name__ == "__main__":
    print(f"Running at http://{HOST}:{PORT}")
    with ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
        httpd.serve_forever()
