""" HTTP сервер с REST API для управления клиентами """

import json                     # модуль для работы с JSON (сериализация/десериализация)
from functools import partial   # функция для частичного применения аргументов, используется для создания обработчика с фиксированными параметрами
from http.server import HTTPServer, SimpleHTTPRequestHandler # базовый HTTP сервер и обработчик для статических файлов
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse # функции для работы с UR

from ClientController import ClientController
from AddClientController import AddClientController
from EditClientController import EditClientController
from DeleteClientController import DeleteClientController

BASE_DIR = Path(__file__).parent    # получает путь к директории, где находится файл server.py
PUBLIC_DIR = BASE_DIR / "public"    # создает путь к директории public


class ClientRequestHandler(SimpleHTTPRequestHandler):
    """HTTP обработчик для единой формы клиента """

    client_controller = ClientController()
    add_client_controller = AddClientController()
    edit_client_controller = EditClientController()
    delete_client_controller = DeleteClientController()

    def __init__(self, *args, directory: str | None = None, **kwargs) -> None:
        directory = directory or str(PUBLIC_DIR) # использует переданную директорию или стандартную
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        """Обработка GET запросов """
        parsed = urlparse(self.path) # разбираем url запроса на компоненты

        if parsed.path == "/api/clients": # обрабатывает список клиентов
            self._handle_clients_list(parsed) # извлекает параметры из URL, вызывает ClientController.get_short_clients(), возвращает JSON с клиентами и пагинацией
            return

        if parsed.path.startswith("/api/clients/"):
            path_parts = parsed.path.rstrip("/").split("/") # удаляем завершаюшие / и разбиваем путь на части

            # формат: /api/clients/{id} - детальная информация
            if len(path_parts) == 4:
                try:
                    client_id = int(path_parts[3]) # преобразовали id в число
                    self._handle_client_detail(client_id) # возвращает JSON со всеми полями клиента
                    return
                except (ValueError, IndexError):
                    pass

            # формат: /api/clients/{id}/edit/form - форма редактирования
            elif (
                len(path_parts) == 6
                and path_parts[4] == "edit"
                and path_parts[5] == "form"
            ):
                try:
                    client_id = int(path_parts[3])  # извлекает айди
                    self._handle_edit_client_form(client_id) # возвращает данные для предзаполнения формы
                    return
                except (ValueError, IndexError):
                    pass

        # отдаем статику
        if parsed.path == "/": # перенаправлям на index, когда захрдим на сервер
            self.path = "/index.html"

        # отдаем форму клиента
        if parsed.path == "/client_form.html": # когда заходим на http://localhost:8000/client_form.html
            self.path = "/client_form.html" # сервер отдает public/client_form.html

        super().do_GET() # вызов родительского метода для статических файлов

    def do_POST(self) -> None:
        """Обработка POST запросов """
        parsed = urlparse(self.path)    # парсинг url

        if parsed.path == "/api/clients/add":
            self._handle_add_client()
            return

        if parsed.path.startswith("/api/clients/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/clients/{id}/edit - обновление клиента
            if len(path_parts) == 5 and path_parts[4] == "edit":
                try:
                    client_id = int(path_parts[3])
                    self._handle_edit_client(client_id)
                    return
                except (ValueError, IndexError):
                    pass

        self.send_error(404, "Endpoint not found") # если путь не найдет - возвращаем ошибку 404

    def do_DELETE(self) -> None:
        """Обработка DELETE запросов """
        parsed = urlparse(self.path)

        if parsed.path.startswith("/api/clients/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/clients/{id}
            if len(path_parts) == 4:
                try:
                    client_id = int(path_parts[3])
                    self._handle_delete_client(client_id)
                    return
                except (ValueError, IndexError):
                    pass

        self.send_error(404, "Endpoint not found")

    # список клиентов
    def _handle_clients_list(self, parsed) -> None:
        query = parse_qs(parsed.query)  # парсит query string в словарь списков
        page = self._safe_int(query.get("page", [1])[0], default=1) # выводим всегда 1 страницу
        page_size_raw = query.get("page_size", [None])[0]           # получаем размер страницы
        page_size = self._safe_int(page_size_raw) if page_size_raw is not None else None

        # извлекаем параметры фильтрации
        filters = self._extract_filters(query)

        # извлекаем параметры сортировки
        sort_by = query.get("sort", [None])[0]
        sort_order = query.get("sort_order", ["asc"])[0]

        # вызываем основной контроллер и отправляем json ответ
        try:
            payload = self.client_controller.get_short_clients(
                page_size=page_size,
                page=page,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            self._send_json(payload)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # детальная информация
    def _handle_client_detail(self, client_id: int) -> None:
        try:
            client = self.client_controller.get_client(client_id)
            if client is None:
                self._send_json({"error": "Клиент не найден"}, status=404)
                return

            # возвращаем старый формат без обертки
            self._send_json(client)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # возврат формы редактирования с данными клиента
    def _handle_edit_client_form(self, client_id: int) -> None:
        try:
            client_data = self.edit_client_controller.get_client_for_edit(client_id)
            if client_data is None:
                print(f"Клиент {client_id} не найден")
                self._send_json({"error": "Клиент не найден"}, status=404)
                return

            # возвращаем старый формат без обертки
            self._send_json(client_data)
        except Exception as e:
            print(f"Ошибка при обработке формы редактирования: {e}")
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # добавление нового клиента
    def _handle_add_client(self) -> None:
        try:
            content_length = int(self.headers["Content-Length"]) # получает длину тела запроса из заголовков
            post_data = self.rfile.read(content_length)          # читает тело запроса из входного потока
            client_data = json.loads(post_data.decode("utf-8"))  # декодирует байты в строку и парсит

            result = self.add_client_controller.add_client(client_data)

            # оставляем новый формат для операций записи
            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200) # успешное добавление
            else:
                self._send_json(result, status=400) # ошибка

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # обновление клиента (как и добавление)
    def _handle_edit_client(self, client_id: int) -> None:
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            client_data = json.loads(post_data.decode("utf-8"))

            result = self.edit_client_controller.update_client(client_id, client_data)

            # оставляем новый формат для операций записи
            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # удаление клиента
    def _handle_delete_client(self, client_id: int) -> None:
        try:
            result = self.delete_client_controller.delete_client(client_id)

            if result["success"]:
                self._send_json(result, status=200)
            else:
                self._send_json(
                    result, status=404 if "не найден" in result["message"] else 400
                )

        except Exception as e:
            self._send_json(
                {"success": False, "message": f"Ошибка сервера: {str(e)}"}, status=500
            )

    # извлечение фильтров
    def _extract_filters(self, query: Dict[str, list[str]]) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}

        surname_prefix = query.get("surname_prefix", [None])[0]
        if surname_prefix:
            filters["surname_prefix"] = surname_prefix

        name_prefix = query.get("name_prefix", [None])[0]
        if name_prefix:
            filters["name_prefix"] = name_prefix

        patronymic_filter = query.get("patronymic_prefix", [None])[0]
        if patronymic_filter in ["yes", "no"]:  # Только допустимые значения
            filters["patronymic_prefix"] = patronymic_filter

        phone_substring = query.get("phone_substring", [None])[0]
        if phone_substring:
            filters["phone_substring"] = phone_substring

        return filters # передаем в контроллер

    # преобразование значения в инт
    def _safe_int(self, value: Any, default: int | None = None) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # отправляем json ответы
    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")  # сериализует объект в JSON строку и кодирует в байты
        self.send_response(status)  # статус код
        self.send_header("Content-Type", "application/json; charset=utf-8") # заголовки ответа
        self.send_header("Access-Control-Allow-Origin", "*")  # разрешает CORS запросы (одобряет запросы между разными доменами)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()  # завершает заголовки
        self.wfile.write(body)  # записывает тело ответа


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    handler = partial(ClientRequestHandler, directory=str(PUBLIC_DIR))
    with HTTPServer((host, port), handler) as httpd:
        print(f"Сервер запущен: http://{host}:{port}")
        print("Формы доступны по:")
        print("Полный просмотр клиента: http://127.0.0.1:8000/detail.html?id=1")
        print("Редактирование: http://127.0.0.1:8000/client_form.html?id=1")
        print("Добавление: http://127.0.0.1:8000/client_form.html")
        print("\nCtrl+C для остановки")
        httpd.serve_forever()   # бесконечный цикл обработки запросов


if __name__ == "__main__":
    run_server()
