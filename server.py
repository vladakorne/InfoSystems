"""HTTP сервер с REST API для управления клиентами, номерами и бронированиями"""

import json  # модуль для работы с JSON (сериализация/десериализация)
from functools import (
    partial,
)  # функция для частичного применения аргументов, используется для создания обработчика с фиксированными параметрами
from http.server import (
    HTTPServer,
    SimpleHTTPRequestHandler,
)  # базовый HTTP сервер и обработчик для статических файлов
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse  # функции для работы с UR

from ClientController import ClientController
from AddClientController import AddClientController
from EditClientController import EditClientController
from DeleteClientController import DeleteClientController

# Импортируем контроллеры для Room
from RoomController import RoomController
from AddRoomController import AddRoomController
from EditRoomController import EditRoomController
from DeleteRoomController import DeleteRoomController

# Импортируем контроллеры для Booking
from BookingController import BookingController
from AddBookingController import AddBookingController
from EditBookingController import EditBookingController
from DeleteBookingController import DeleteBookingController

BASE_DIR = Path(
    __file__
).parent  # получает путь к директории, где находится файл server.py
PUBLIC_DIR = BASE_DIR / "public"  # создает путь к директории public


class UnifiedRequestHandler(SimpleHTTPRequestHandler):
    """HTTP обработчик для всех сущностей: клиентов, номеров и бронирований"""

    # Инициализация контроллеров для всех сущностей
    client_controller = ClientController()
    add_client_controller = AddClientController()
    edit_client_controller = EditClientController()
    delete_client_controller = DeleteClientController()

    room_controller = RoomController()
    add_room_controller = AddRoomController()
    edit_room_controller = EditRoomController()
    delete_room_controller = DeleteRoomController()

    booking_controller = BookingController()
    add_booking_controller = AddBookingController()
    edit_booking_controller = EditBookingController()
    delete_booking_controller = DeleteBookingController()

    def __init__(self, *args, directory: str | None = None, **kwargs) -> None:
        directory = directory or str(
            PUBLIC_DIR
        )  # использует переданную директорию или стандартную
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        """Обработка GET запросов"""
        parsed = urlparse(self.path)  # разбираем url запроса на компоненты

        if parsed.path == "/api/clients":  # обрабатывает список клиентов
            self._handle_clients_list(
                parsed
            )  # извлекает параметры из URL, вызывает ClientController.get_short_clients(), возвращает JSON с клиентами и пагинацией
            return

        if parsed.path.startswith("/api/clients/"):
            path_parts = parsed.path.rstrip("/").split(
                "/"
            )  # удаляем завершаюшие / и разбиваем путь на части

            # формат: /api/clients/{id} - детальная информация
            if len(path_parts) == 4:
                try:
                    client_id = int(path_parts[3])  # преобразовали id в число
                    self._handle_client_detail(
                        client_id
                    )  # возвращает JSON со всеми полями клиента
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
                    self._handle_edit_client_form(
                        client_id
                    )  # возвращает данные для предзаполнения формы
                    return
                except (ValueError, IndexError):
                    pass

        elif parsed.path == "/api/rooms":  # обрабатывает список номеров
            self._handle_rooms_list(parsed)
            return

        elif parsed.path.startswith("/api/rooms/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/rooms/{id} - детальная информация
            if len(path_parts) == 4:
                try:
                    room_id = int(path_parts[3])
                    self._handle_room_detail(room_id)
                    return
                except (ValueError, IndexError):
                    pass

            # формат: /api/rooms/{id}/edit/form - форма редактирования
            elif (
                len(path_parts) == 6
                and path_parts[4] == "edit"
                and path_parts[5] == "form"
            ):
                try:
                    room_id = int(path_parts[3])
                    self._handle_edit_room_form(room_id)
                    return
                except (ValueError, IndexError):
                    pass

            # формат: /api/rooms/available - доступные номера
            elif len(path_parts) == 5 and path_parts[4] == "available":
                self._handle_available_rooms(parsed)
                return

        elif parsed.path == "/api/bookings":  # обрабатывает список бронирований
            self._handle_bookings_list(parsed)
            return

        elif parsed.path.startswith("/api/bookings/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/bookings/{id} - детальная информация
            if len(path_parts) == 4:
                try:
                    booking_id = int(path_parts[3])
                    self._handle_booking_detail(booking_id)
                    return
                except (ValueError, IndexError):
                    pass

            # формат: /api/bookings/{id}/edit/form - форма редактирования
            elif (
                len(path_parts) == 6
                and path_parts[4] == "edit"
                and path_parts[5] == "form"
            ):
                try:
                    booking_id = int(path_parts[3])
                    self._handle_edit_booking_form(booking_id)
                    return
                except (ValueError, IndexError):
                    pass

        elif parsed.path == "/api/clients/all":
            # Получение всех клиентов для выпадающих списков
            self._handle_all_clients()
            return

        elif parsed.path == "/api/rooms/all":
            # Получение всех номеров для выпадающих списков
            self._handle_all_rooms()
            return

        # отдаем статику
        if parsed.path == "/":  # перенаправлям на index, когда захрдим на сервер
            self.path = "/index.html"

        # отдаем форму клиента
        if parsed.path == "/client_form.html":  # когда заходим на http://localhost:8000/client_form.html
            self.path = "/client_form.html"  # сервер отдает public/client_form.html

        # отдаем форму номера
        if parsed.path == "/room_form.html":
            self.path = "/room_form.html"

        # отдаем форму бронирования
        if parsed.path == "/booking_form.html":
            self.path = "/booking_form.html"

        # отдаем детальную страницу номера
        if parsed.path == "/detail_room.html":
            self.path = "/detail_room.html"

        # отдаем детальную страницу бронирования
        if parsed.path == "/detail_booking.html":
            self.path = "/detail_booking.html"

        elif parsed.path == "/api/clients/all":
            self._handle_all_clients()
            return

        elif parsed.path == "/api/rooms/all":
            self._handle_all_rooms()
            return

        super().do_GET()  # вызов родительского метода для статических файлов

    def do_POST(self) -> None:
        """Обработка POST запросов"""
        parsed = urlparse(self.path)  # парсинг url

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

        elif parsed.path == "/api/rooms/add":
            self._handle_add_room()
            return

        elif parsed.path.startswith("/api/rooms/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/rooms/{id}/edit - обновление номера
            if len(path_parts) == 5 and path_parts[4] == "edit":
                try:
                    room_id = int(path_parts[3])
                    self._handle_edit_room(room_id)
                    return
                except (ValueError, IndexError):
                    pass

        elif parsed.path == "/api/bookings/add":
            self._handle_add_booking()
            return

        elif parsed.path.startswith("/api/bookings/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/bookings/{id}/edit - обновление бронирования
            if len(path_parts) == 5 and path_parts[4] == "edit":
                try:
                    booking_id = int(path_parts[3])
                    self._handle_edit_booking(booking_id)
                    return
                except (ValueError, IndexError):
                    pass

        self.send_error(
            404, "Endpoint not found"
        )  # если путь не найдет - возвращаем ошибку 404

    def do_DELETE(self) -> None:
        """Обработка DELETE запросов"""
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

        elif parsed.path.startswith("/api/rooms/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/rooms/{id}
            if len(path_parts) == 4:
                try:
                    room_id = int(path_parts[3])
                    self._handle_delete_room(room_id)
                    return
                except (ValueError, IndexError):
                    pass

        elif parsed.path.startswith("/api/bookings/"):
            path_parts = parsed.path.rstrip("/").split("/")

            # формат: /api/bookings/{id}
            if len(path_parts) == 4:
                try:
                    booking_id = int(path_parts[3])
                    self._handle_delete_booking(booking_id)
                    return
                except (ValueError, IndexError):
                    pass

        self.send_error(404, "Endpoint not found")

    # список клиентов
    def _handle_clients_list(self, parsed) -> None:
        query = parse_qs(parsed.query)  # парсит query string в словарь списков
        page = self._safe_int(
            query.get("page", [1])[0], default=1
        )  # выводим всегда 1 страницу
        page_size_raw = query.get("page_size", [None])[0]  # получаем размер страницы
        page_size = self._safe_int(page_size_raw) if page_size_raw is not None else None

        # извлекаем параметры фильтрации
        filters = self._extract_client_filters(query)

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

    # детальная информация клиента
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
            content_length = int(
                self.headers["Content-Length"]
            )  # получает длину тела запроса из заголовков
            post_data = self.rfile.read(
                content_length
            )  # читает тело запроса из входного потока
            client_data = json.loads(
                post_data.decode("utf-8")
            )  # декодирует байты в строку и парсит

            result = self.add_client_controller.add_client(client_data)

            # оставляем новый формат для операций записи
            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200)  # успешное добавление
            else:
                self._send_json(result, status=400)  # ошибка

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

    # получение всех клиентов для выпадающих списков
    def _handle_all_clients(self):
        """Получение всех клиентов для выпадающих списков"""
        try:
            # Используем контроллер для получения всех клиентов без пагинации
            payload = self.client_controller.get_short_clients(
                page_size=None,
                page=1,
                filters={}
            )
            self._send_json(payload)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # список номеров
    def _handle_rooms_list(self, parsed) -> None:
        query = parse_qs(parsed.query)
        page = self._safe_int(query.get("page", [1])[0], default=1)
        page_size_raw = query.get("page_size", [None])[0]
        page_size = self._safe_int(page_size_raw) if page_size_raw is not None else None

        # извлекаем параметры фильтрации для номеров
        filters = self._extract_room_filters(query)

        # извлекаем параметры сортировки
        sort_by = query.get("sort", [None])[0]
        sort_order = query.get("sort_order", ["asc"])[0]

        try:
            payload = self.room_controller.get_rooms_list(
                page_size=page_size,
                page=page,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            self._send_json(payload)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # детальная информация номера
    def _handle_room_detail(self, room_id: int) -> None:
        try:
            room = self.room_controller.get_room(room_id)
            if room is None:
                self._send_json({"error": "Номер не найден"}, status=404)
                return

            self._send_json(room)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # возврат формы редактирования с данными номера
    def _handle_edit_room_form(self, room_id: int) -> None:
        try:
            room_data = self.edit_room_controller.get_room_for_edit(room_id)
            if room_data is None:
                print(f"Номер {room_id} не найден")
                self._send_json({"error": "Номер не найден"}, status=404)
                return

            self._send_json(room_data)
        except Exception as e:
            print(f"Ошибка при обработке формы редактирования номера: {e}")
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # добавление нового номера
    def _handle_add_room(self) -> None:
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            room_data = json.loads(post_data.decode("utf-8"))

            result = self.add_room_controller.add_room(room_data)

            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # обновление номера
    def _handle_edit_room(self, room_id: int) -> None:
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            room_data = json.loads(post_data.decode("utf-8"))

            result = self.edit_room_controller.update_room(room_id, room_data)

            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # удаление номера
    def _handle_delete_room(self, room_id: int) -> None:
        try:
            result = self.delete_room_controller.delete_room(room_id)

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

    # получение доступных номеров на даты
    def _handle_available_rooms(self, parsed) -> None:
        try:
            query = parse_qs(parsed.query)
            check_in = query.get("check_in", [None])[0]
            check_out = query.get("check_out", [None])[0]

            if not check_in or not check_out:
                self._send_json({"error": "Необходимо указать check_in и check_out"}, status=400)
                return

            # Здесь нужно реализовать логику получения доступных номеров
            # Пока возвращаем все доступные номера
            filters = {"is_available": True}
            result = self.room_controller.get_rooms_list(filters=filters, page_size=None, page=1)
            self._send_json(result["items"])

        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # получение всех номеров для выпадающих списков
    def _handle_all_rooms(self):
        """Получение всех номеров для выпадающих списков"""
        try:
            # Используем контроллер для получения всех номеров без пагинации
            payload = self.room_controller.get_rooms_list(
                page_size=None,
                page=1,
                filters={}
            )
            self._send_json(payload)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # список бронирований
    def _handle_bookings_list(self, parsed) -> None:
        query = parse_qs(parsed.query)
        page = self._safe_int(query.get("page", [1])[0], default=1)
        page_size_raw = query.get("page_size", [None])[0]
        page_size = self._safe_int(page_size_raw) if page_size_raw is not None else None

        # извлекаем параметры фильтрации для бронирований
        filters = self._extract_booking_filters(query)

        # извлекаем параметры сортировки
        sort_by = query.get("sort", [None])[0]
        sort_order = query.get("sort_order", ["asc"])[0]

        try:
            payload = self.booking_controller.get_bookings_list(
                page_size=page_size,
                page=page,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            self._send_json(payload)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # детальная информация бронирования
    def _handle_booking_detail(self, booking_id: int) -> None:
        try:
            booking = self.booking_controller.get_booking(booking_id)
            if booking is None:
                self._send_json({"error": "Бронирование не найдено"}, status=404)
                return

            self._send_json(booking)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # возврат формы редактирования с данными бронирования
    def _handle_edit_booking_form(self, booking_id: int) -> None:
        try:
            booking_data = self.edit_booking_controller.get_booking_for_edit(booking_id)
            if booking_data is None:
                print(f"Бронирование {booking_id} не найдено")
                self._send_json({"error": "Бронирование не найдено"}, status=404)
                return

            self._send_json(booking_data)
        except Exception as e:
            print(f"Ошибка при обработке формы редактирования бронирования: {e}")
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # добавление нового бронирования
    def _handle_add_booking(self) -> None:
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            booking_data = json.loads(post_data.decode("utf-8"))

            result = self.add_booking_controller.add_booking(booking_data)

            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # обновление бронирования
    def _handle_edit_booking(self, booking_id: int) -> None:
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            booking_data = json.loads(post_data.decode("utf-8"))

            result = self.edit_booking_controller.update_booking(booking_id, booking_data)

            if result["success"]:
                result["redirect_url"] = "index.html"
                self._send_json(result, status=200)
            else:
                self._send_json(result, status=400)

        except json.JSONDecodeError:
            self._send_json({"error": "Неверный формат JSON"}, status=400)
        except Exception as e:
            self._send_json({"error": f"Ошибка сервера: {str(e)}"}, status=500)

    # удаление бронирования
    def _handle_delete_booking(self, booking_id: int) -> None:
        try:
            result = self.delete_booking_controller.delete_booking(booking_id)

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

    # извлечение фильтров для клиентов
    def _extract_client_filters(self, query: Dict[str, list[str]]) -> Dict[str, Any]:
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

        return filters  # передаем в контроллер

    # извлечение фильтров для номеров
    def _extract_room_filters(self, query: Dict[str, list[str]]) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}

        room_number_substring = query.get("room_number_substring", [None])[0]
        if room_number_substring:
            filters["room_number_substring"] = room_number_substring

        category = query.get("category", [None])[0]
        if category:
            filters["category"] = category

        min_capacity = query.get("min_capacity", [None])[0]
        if min_capacity:
            filters["min_capacity"] = int(min_capacity)

        max_capacity = query.get("max_capacity", [None])[0]
        if max_capacity:
            filters["max_capacity"] = int(max_capacity)

        is_available = query.get("is_available", [None])[0]
        if is_available is not None:
            filters["is_available"] = is_available.lower() == 'true'

        min_price = query.get("min_price", [None])[0]
        if min_price:
            filters["min_price"] = float(min_price)

        max_price = query.get("max_price", [None])[0]
        if max_price:
            filters["max_price"] = float(max_price)

        return filters

    # извлечение фильтров для бронирований
    def _extract_booking_filters(self, query: Dict[str, list[str]]) -> Dict[str, Any]:
        filters: Dict[str, Any] = {}

        client_id = query.get("client_id", [None])[0]
        if client_id:
            filters["client_id"] = int(client_id)

        room_id = query.get("room_id", [None])[0]
        if room_id:
            filters["room_id"] = int(room_id)

        status = query.get("status", [None])[0]
        if status:
            filters["status"] = status

        start_date = query.get("start_date", [None])[0]
        if start_date:
            filters["start_date"] = start_date

        end_date = query.get("end_date", [None])[0]
        if end_date:
            filters["end_date"] = end_date

        min_price = query.get("min_price", [None])[0]
        if min_price:
            filters["min_price"] = float(min_price)

        max_price = query.get("max_price", [None])[0]
        if max_price:
            filters["max_price"] = float(max_price)

        return filters

    # преобразование значения в инт
    def _safe_int(self, value: Any, default: int | None = None) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    # отправляем json ответы
    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode(
            "utf-8"
        )  # сериализует объект в JSON строку и кодирует в байты
        self.send_response(status)  # статус код
        self.send_header(
            "Content-Type", "application/json; charset=utf-8"
        )  # заголовки ответа
        self.send_header(
            "Access-Control-Allow-Origin", "*"
        )  # разрешает CORS запросы (одобряет запросы между разными доменами)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()  # завершает заголовки
        self.wfile.write(body)  # записывает тело ответа


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    handler = partial(UnifiedRequestHandler, directory=str(PUBLIC_DIR))
    with HTTPServer((host, port), handler) as httpd:
        print(f"Сервер запущен: http://{host}:{port}")

        print("\nCtrl+C для остановки")
        httpd.serve_forever()  # бесконечный цикл обработки запросов


if __name__ == "__main__":
    run_server()