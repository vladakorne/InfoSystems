"""
server.py - Обновленный для работы с единой формой
"""
import json
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

from ClientController import ClientController
from AddClientController import AddClientController
from EditClientController import EditClientController

BASE_DIR = Path(__file__).parent
PUBLIC_DIR = BASE_DIR / "public"


class ClientRequestHandler(SimpleHTTPRequestHandler):
    """HTTP обработчик для единой формы клиента."""

    client_controller = ClientController()
    add_client_controller = AddClientController()
    edit_client_controller = EditClientController()

    def __init__(self, *args, directory: str | None = None, **kwargs) -> None:
        directory = directory or str(PUBLIC_DIR)
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        # print(f"GET {self.path}")


        if parsed.path == "/api/clients":
            self._handle_clients_list(parsed)
            return

        if parsed.path.startswith("/api/clients/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # Формат: /api/clients/{id} - детальная информация
            if len(path_parts) == 4:
                try:
                    client_id = int(path_parts[3])
                    self._handle_client_detail(client_id)
                    return
                except (ValueError, IndexError):
                    pass

            # Формат: /api/clients/{id}/edit/form - форма редактирования
            elif len(path_parts) == 6 and path_parts[4] == "edit" and path_parts[5] == "form":
                try:
                    client_id = int(path_parts[3])
                    self._handle_edit_client_form(client_id)
                    return
                except (ValueError, IndexError):
                    pass

        # Отдаем статику
        if parsed.path == "/":
            self.path = "/index.html"

        # Отдаем форму клиента
        if parsed.path == "/client_form.html":
            self.path = "/client_form.html"

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        # print(f"POST {self.path}")

        if parsed.path == "/api/clients/add":
            self._handle_add_client()
            return

        if parsed.path.startswith("/api/clients/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # Формат: /api/clients/{id}/edit - обновление клиента
            if len(path_parts) == 5 and path_parts[4] == "edit":
                try:
                    client_id = int(path_parts[3])
                    self._handle_edit_client(client_id)
                    return
                except (ValueError, IndexError):
                    pass

        self.send_error(404, "Endpoint not found")

    def _redirect_to_client_form(self, parsed) -> None:
        """Перенаправляет со старых URL на новую форму."""
        query = parse_qs(parsed.query)
        client_id = query.get('id', [None])[0]

        if parsed.path == "/client_form.html" or not client_id:
            new_url = "/client_form.html"
        else:
            new_url = f"/client_form.html?id={client_id}"

        self.send_response(302)
        self.send_header('Location', new_url)
        self.end_headers()

    def _handle_clients_list(self, parsed) -> None:
        query = parse_qs(parsed.query)
        page = self._safe_int(query.get("page", [1])[0], default=1)
        page_size_raw = query.get("page_size", [None])[0]
        page_size = self._safe_int(page_size_raw) if page_size_raw is not None else None

        try:
            payload = self.client_controller.get_short_clients(page_size=page_size, page=page)
            # Возвращаем старый формат без обертки
            self._send_json(payload)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    def _handle_client_detail(self, client_id: int) -> None:
        try:
            client = self.client_controller.get_client(client_id)
            if client is None:
                self._send_json({"error": "Клиент не найден"}, status=404)
                return

            # Возвращаем старый формат без обертки
            self._send_json(client)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    def _handle_edit_client_form(self, client_id: int) -> None:
        """Возвращает форму редактирования с данными клиента."""
        try:
            client_data = self.edit_client_controller.get_client_for_edit(client_id)
            if client_data is None:
                print(f"Клиент {client_id} не найден")
                self._send_json({"error": "Клиент не найден"}, status=404)
                return

            # Возвращаем старый формат без обертки
            self._send_json(client_data)
        except Exception as e:
            print(f"Ошибка при обработке формы редактирования: {e}")
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    def _handle_add_client(self) -> None:
        """Обрабатывает добавление нового клиента."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            client_data = json.loads(post_data.decode('utf-8'))

            result = self.add_client_controller.add_client(client_data)

            # Оставляем новый формат для операций записи
            if result['success']:
                self._send_json(result, status=201)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    def _handle_edit_client(self, client_id: int) -> None:
        """Обрабатывает обновление данных клиента."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            client_data = json.loads(post_data.decode('utf-8'))

            result = self.edit_client_controller.update_client(client_id, client_data)

            # Оставляем новый формат для операций записи
            if result['success']:
                self._send_json(result, status=200)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

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


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    handler = partial(ClientRequestHandler, directory=str(PUBLIC_DIR))
    with HTTPServer((host, port), handler) as httpd:
        print(f"Сервер запущен: http://{host}:{port}")
        print("Формы доступны по:")
        print("  • Добавление: http://127.0.0.1:8000/client_form.html")
        print("  • Редактирование: http://127.0.0.1:8000/client_form.html?id=1")
        print("\nCtrl+C для остановки")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()