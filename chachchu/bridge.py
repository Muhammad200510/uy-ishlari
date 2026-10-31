"""iPhone / Apple Shortcuts uchun oddiy HTTP 'bridge'.

iPhone'dan POST /ask {"text": "..."} yuboriladi, javob {"reply": "..."} qaytadi.
Bu rejim HEADLESS — tasdiq so'ramaydi, shuning uchun xavfli amallar (buyruq, post)
avtomatik rad etiladi. Faqat xavfsiz, auto_allow amallar bajariladi.

Xavfsizlik: har bir so'rovda X-Token header config.json dagi bridge.token ga mos
kelishi shart.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .assistant import build_brain
from .config import Config


def make_handler(cfg: Config):
    brain = build_brain(cfg, headless=True)
    expected_token = cfg.get("bridge", "token", default="")

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send(200, {"status": "ok", "name": cfg.name})
            else:
                self._send(404, {"error": "topilmadi"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/ask":
                self._send(404, {"error": "topilmadi"})
                return

            token = self.headers.get("X-Token", "")
            if not expected_token or token != expected_token:
                self._send(401, {"error": "noto'g'ri yoki yo'q token"})
                return

            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b"{}"
                data = json.loads(raw.decode("utf-8"))
                text = (data.get("text") or "").strip()
            except Exception as exc:  # noqa: BLE001
                self._send(400, {"error": f"noto'g'ri JSON: {exc}"})
                return

            if not text:
                self._send(400, {"error": "'text' maydoni bo'sh"})
                return

            try:
                reply = brain.ask(text)
            except Exception as exc:  # noqa: BLE001
                self._send(500, {"error": str(exc)})
                return

            self._send(200, {"reply": reply})

        def log_message(self, *args) -> None:  # jim bo'lsin
            pass

    return Handler


def run_bridge(cfg: Config) -> None:
    host = cfg.get("bridge", "host", default="0.0.0.0")
    port = int(cfg.get("bridge", "port", default=8787))
    if not cfg.get("bridge", "token", default=""):
        print("⚠️  OGOHLANTIRISH: bridge.token bo'sh. config.json da maxfiy token qo'ying!")
    handler = make_handler(cfg)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"🌉 Bridge ishga tushdi: http://{host}:{port}  (POST /ask, header: X-Token)")
    print("   To'xtatish uchun Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBridge to'xtatildi.")
        server.shutdown()
