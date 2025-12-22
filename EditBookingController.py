"""
Контроллер для редактирования существующего бронирования.
Отдельный контроллер для формы редактирования.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from Booking import Booking
from BookingRepDBAdapter import BookingRepDBAdapter
from BookingRepDB import BookingRepDB
from RoomRepDBAdapter import RoomRepDBAdapter
from RoomRepDB import RoomRepDB
from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB


class EditBookingController:
    """Контроллер для управления формой редактирования бронирования."""

    def __init__(self,
                 booking_repository: Optional[BookingRepDBAdapter] = None,
                 room_repository: Optional[RoomRepDBAdapter] = None,
                 client_repository: Optional[ClientRepDBAdapter] = None) -> None:
        self.booking_repository: BookingRepDBAdapter = booking_repository or BookingRepDBAdapter(
            BookingRepDB()
        )
        self.room_repository: RoomRepDBAdapter = room_repository or RoomRepDBAdapter(
            RoomRepDB()
        )
        self.client_repository: ClientRepDBAdapter = client_repository or ClientRepDBAdapter(
            ClientRepDB()
        )

    def get_booking_for_edit(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные бронирования для редактирования."""
        try:
            booking = self.booking_repository.get_by_id(booking_id)

            if booking:
                result = {
                    "id": booking["id"],
                    "client_id": booking["client_id"],
                    "room_id": booking["room_id"],
                    "check_in": booking["check_in"],
                    "check_out": booking["check_out"],
                    "total_sum": booking["total_sum"],
                    "status": booking["status"],
                    "notes": booking["notes"],
                }
                return result
            else:
                print(f"Бронирование {booking_id} не найден")
                return None

        except Exception as e:
            print(f"Ошибка при получении бронирования {booking_id} для редактирования: {e}")
            return None

    def validate_booking_data(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидирует данные бронирования при редактировании."""
        errors = {}

        # Валидация обязательных полей
        required_fields = ["client_id", "room_id", "check_in", "check_out"]
        for field in required_fields:
            value = booking_data.get(field)
            if not value:
                errors[field] = "Поле обязательно для заполнения"

        # Валидация клиента
        try:
            if "client_id" in booking_data and booking_data["client_id"]:
                client_id = int(booking_data["client_id"])
                client = self.client_repository.get_by_id(client_id)
                if not client:
                    errors["client_id"] = "Клиент не найден"
        except (ValueError, TypeError) as e:
            errors["client_id"] = "Некорректный ID клиента"

        # Валидация номера
        try:
            if "room_id" in booking_data and booking_data["room_id"]:
                room_id = int(booking_data["room_id"])
                room = self.room_repository.get_by_id(room_id)
                if not room:
                    errors["room_id"] = "Номер не найден"
        except (ValueError, TypeError) as e:
            errors["room_id"] = "Некорректный ID номера"

        # Валидация дат
        try:
            check_in = booking_data.get("check_in")
            check_out = booking_data.get("check_out")

            if check_in and check_out:
                check_in_date = date.fromisoformat(check_in) if isinstance(check_in, str) else check_in
                check_out_date = date.fromisoformat(check_out) if isinstance(check_out, str) else check_out

                Booking._validate_dates(check_in_date, check_out_date)
        except ValueError as e:
            errors["dates"] = str(e)
        except Exception as e:
            errors["dates"] = "Некорректный формат дат"

        # Валидация статуса
        status = booking_data.get("status")
        if status:
            try:
                Booking.validate_status(status)
            except ValueError as e:
                errors["status"] = str(e)

        print(f"Результат валидации бронирования: {errors}")
        return errors

    def update_booking(
            self, booking_id: int, booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновляет данные бронирования.
        Возвращает результат операции с сообщением об успехе или ошибках.
        """

        # Проверяем существование бронирования
        existing_booking = self.booking_repository.get_by_id(booking_id)
        if not existing_booking:
            print(f"Бронирование {booking_id} не найден в репозитории")
            return {"success": False, "message": f"Бронирование с ID {booking_id} не найден"}

        print(f"Существующее бронирование найдено: {existing_booking}")

        # Проверяем валидацию
        validation_errors = self.validate_booking_data(booking_data)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "message": "Ошибки валидации данных",
            }

        try:
            # Если меняются даты или номер, пересчитываем стоимость
            if ("room_id" in booking_data or
                    "check_in" in booking_data or
                    "check_out" in booking_data):

                room_id = booking_data.get("room_id", existing_booking["room_id"])
                check_in = booking_data.get("check_in", existing_booking["check_in"])
                check_out = booking_data.get("check_out", existing_booking["check_out"])

                # Расчет новой стоимости
                room = self.room_repository.get_by_id(int(room_id))
                if not room:
                    return {"success": False, "message": "Номер не найден"}

                check_in_date = date.fromisoformat(check_in)
                check_out_date = date.fromisoformat(check_out)
                nights = (check_out_date - check_in_date).days

                if nights <= 0:
                    return {"success": False, "message": "Некорректное количество ночей"}

                price_per_night = Decimal(str(room["price_per_night"]))
                total_sum = price_per_night * nights

                booking_data["total_sum"] = float(total_sum)

            # Подготавливаем данные для репозитория
            repo_data = {
                "client_id": int(booking_data.get("client_id", existing_booking["client_id"])),
                "room_id": int(booking_data.get("room_id", existing_booking["room_id"])),
                "check_in": booking_data.get("check_in", existing_booking["check_in"]),
                "check_out": booking_data.get("check_out", existing_booking["check_out"]),
                "total_sum": Decimal(str(booking_data.get("total_sum", existing_booking["total_sum"]))),
                "status": booking_data.get("status", existing_booking["status"]),
                "notes": booking_data.get("notes", existing_booking.get("notes", "")).strip(),
            }
            print(f"Данные бронирования изменены")

            # Обновляем бронирование через репозиторий
            success = self.booking_repository.update_booking(booking_id, repo_data)

            if success:
                return {"success": True, "message": "Данные бронирования успешно обновлены"}
            else:
                return {
                    "success": False,
                    "message": "Не удалось обновить данные бронирования",
                }

        except ValueError as e:
            print(f"ValueError при обновлении: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"Исключение при обновлении бронирования {booking_id}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Произошла ошибка: {str(e)}"}

    def update_booking_status(self, booking_id: int, status: str) -> Dict[str, Any]:
        """Обновляет статус бронирования."""
        try:
            # Проверяем существование бронирования
            existing_booking = self.booking_repository.get_by_id(booking_id)
            if not existing_booking:
                return {"success": False, "message": f"Бронирование с ID {booking_id} не найден"}

            # Валидируем статус
            try:
                Booking.validate_status(status)
            except ValueError as e:
                return {"success": False, "message": str(e)}

            # Обновляем статус
            success = self.booking_repository.update_booking(booking_id, {"status": status})

            if success:
                return {"success": True, "message": f"Статус бронирования {booking_id} обновлен"}
            else:
                return {"success": False, "message": "Не удалось обновить статус"}

        except Exception as e:
            return {"success": False, "message": f"Ошибка сервера: {str(e)}"}