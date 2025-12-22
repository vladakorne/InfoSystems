"""
Контроллер для добавления нового бронирования.
Отдельный контроллер для формы добавления.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from Booking import Booking
from BookingRepDBAdapter import BookingRepDBAdapter
from BookingRepDB import BookingRepDB
from RoomRepDBAdapter import RoomRepDBAdapter
from RoomRepDB import RoomRepDB
from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB


class AddBookingController:
    """Контроллер для управления формой добавления бронирования."""

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

    def validate_booking_data(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует данные бронирования.
        Возвращает словарь с ошибками или пустой словарь если валидация прошла успешно.
        """
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
                # Проверяем существование клиента
                client = self.client_repository.get_by_id(client_id)
                if not client:
                    errors["client_id"] = "Клиент не найден"
        except (ValueError, TypeError) as e:
            errors["client_id"] = "Некорректный ID клиента"

        # Валидация номера
        try:
            if "room_id" in booking_data and booking_data["room_id"]:
                room_id = int(booking_data["room_id"])
                # Проверяем существование номера
                room = self.room_repository.get_by_id(room_id)
                if not room:
                    errors["room_id"] = "Номер не найден"
                elif not room["is_available"]:
                    errors["room_id"] = "Номер недоступен"
        except (ValueError, TypeError) as e:
            errors["room_id"] = "Некорректный ID номера"

        # Валидация дат
        try:
            check_in = booking_data.get("check_in")
            check_out = booking_data.get("check_out")

            if check_in and check_out:
                check_in_date = date.fromisoformat(check_in) if isinstance(check_in, str) else check_in
                check_out_date = date.fromisoformat(check_out) if isinstance(check_out, str) else check_out

                # Валидация с использованием метода из Booking
                Booking._validate_dates(check_in_date, check_out_date)

                # Проверяем доступность номера на даты
                if "room_id" in booking_data and booking_data["room_id"]:
                    room_id = int(booking_data["room_id"])
                    # Здесь можно добавить проверку через booking_repository
        except ValueError as e:
            errors["dates"] = str(e)
        except Exception as e:
            errors["dates"] = "Некорректный формат дат"

        return errors

    def calculate_total_price(self, room_id: int, check_in: str, check_out: str) -> Decimal:
        """Рассчитывает общую стоимость бронирования."""
        try:
            room = self.room_repository.get_by_id(room_id)
            if not room:
                raise ValueError("Номер не найден")

            check_in_date = date.fromisoformat(check_in)
            check_out_date = date.fromisoformat(check_out)
            nights = (check_out_date - check_in_date).days

            if nights <= 0:
                raise ValueError("Некорректное количество ночей")

            price_per_night = Decimal(str(room["price_per_night"]))
            return price_per_night * nights

        except Exception as e:
            raise ValueError(f"Ошибка расчета стоимости: {str(e)}")

    def add_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавляет новое бронирование.
        Возвращает результат операции с сообщением об успехе или ошибках.
        """
        # Проверяем валидацию
        validation_errors = self.validate_booking_data(booking_data)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "message": "Ошибки валидации данных",
            }

        try:
            # Рассчитываем стоимость
            total_sum = self.calculate_total_price(
                int(booking_data["room_id"]),
                booking_data["check_in"],
                booking_data["check_out"]
            )

            # Подготавливаем данные для репозитория
            repo_data = {
                "client_id": int(booking_data["client_id"]),
                "room_id": int(booking_data["room_id"]),
                "check_in": booking_data["check_in"],
                "check_out": booking_data["check_out"],
                "total_sum": total_sum,
                "status": booking_data.get("status", "confirmed"),
                "notes": booking_data.get("notes", "").strip(),
            }

            # Добавляем бронирование через репозиторий
            success = self.booking_repository.add_booking(repo_data)

            if success:
                return {"success": True, "message": "Бронирование успешно создано"}
            else:
                return {"success": False, "message": "Не удалось создать бронирование"}

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Произошла ошибка: {str(e)}"}

    def get_empty_booking_form(self) -> Dict[str, Any]:
        """Возвращает шаблон пустой формы для бронирования."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

        return {
            "client_id": "",
            "room_id": "",
            "check_in": tomorrow,
            "check_out": day_after_tomorrow,
            "notes": "",
        }