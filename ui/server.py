"""Optional local chat UI for answer(). Standard library only.

    python -m ui.server            # then open http://127.0.0.1:8000
"""
import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.answer import answer_with_trace  # noqa: E402
from src.index import get_index  # noqa: E402

PAGE = (Path(__file__).parent / "index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html; charset=utf-8")
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if self.path != "/api/ask":
            return self._send(404, b'{"error":"not found"}')
        try:
            n = int(self.headers.get("Content-Length", 0))
            question = (json.loads(self.rfile.read(n) or b"{}").get("question") or "").strip()
            if not question:
                return self._send(400, b'{"error":"empty question"}')
            result, trace = answer_with_trace(question)
            meta = {k: trace.get(k) for k in ("verify", "grounding", "turns", "cost_usd", "duration_ms")}
            self._send(200, json.dumps({"result": result, "meta": meta}).encode())
        except Exception as e:
            traceback.print_exc()
            self._send(500, json.dumps({"error": str(e)}).encode())

    def log_message(self, fmt, *args):
        sys.stderr.write("[ui] " + fmt % args + "\n")


def main():
    port = int(os.getenv("PORT", "8000"))
    print("Loading index (first run builds it)...", file=sys.stderr)
    get_index()
    print(f"Chat UI on http://127.0.0.1:{port}", file=sys.stderr)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
