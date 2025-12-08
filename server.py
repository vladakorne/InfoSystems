import json
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

from ClientController import ClientController

BASE_DIR = Path(__file__).parent
PUBLIC_DIR = BASE_DIR / "public"


class ClientRequestHandler(SimpleHTTPRequestHandler):
    """HTTP обработчик: отдает статику и API на основе контроллера."""

    controller = ClientController()

    def __init__(self, *args, directory: str | None = None, **kwargs) -> None:
        directory = directory or str(PUBLIC_DIR)
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/clients":
            self._handle_clients_list(parsed)
            return

        if parsed.path.startswith("/api/clients/"):
            self._handle_client_detail(parsed)
            return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def _handle_clients_list(self, parsed) -> None:
        query = parse_qs(parsed.query)
        page = self._safe_int(query.get("page", [1])[0], default=1)
        page_size_raw = query.get("page_size", [None])[0]
        page_size = self._safe_int(page_size_raw) if page_size_raw is not None else None

        payload = self.controller.get_short_clients(page_size=page_size, page=page)
        self._send_json(payload)

    def _handle_client_detail(self, parsed) -> None:
        try:
            client_id = int(parsed.path.rstrip("/").split("/")[-1])
        except ValueError:
            self._send_json({"error": "Некорректный идентификатор клиента"}, status=400)
            return

        client = self.controller.get_client(client_id)
        if client is None:
            self._send_json({"error": "Клиент не найден"}, status=404)
            return

        self._send_json(client)

    def _safe_int(self, value: Any, default: int | None = None) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        """Тише лог, чтобы не захламлять вывод."""
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    handler = partial(ClientRequestHandler, directory=str(PUBLIC_DIR))
    with HTTPServer((host, port), handler) as httpd:
        print(f"Сервер запущен: http://{host}:{port}")
        print("Ctrl+C для остановки")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()