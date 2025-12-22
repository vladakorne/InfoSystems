"""
Контроллер для редактирования существующего номера.
Отдельный контроллер для формы редактирования.
"""

from typing import Dict, Any, Optional
from decimal import Decimal

from Room import Room
from RoomRepDBAdapter import RoomRepDBAdapter
from RoomRepDB import RoomRepDB


class EditRoomController:
    """Контроллер для управления формой редактирования номера."""

    def __init__(self, repository: Optional[RoomRepDBAdapter] = None) -> None:
        self.repository: RoomRepDBAdapter = repository or RoomRepDBAdapter(
            RoomRepDB()
        )

    def get_room_for_edit(self, room_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные номера для редактирования."""
        try:
            room = self.repository.get_by_id(room_id)

            if room:
                result = {
                    "id": room["id"],
                    "room_number": room["room_number"],
                    "capacity": room["capacity"],
                    "is_available": room["is_available"],
                    "category": room["category"],
                    "price_per_night": float(room["price_per_night"]),
                    "description": room["description"],
                }
                return result
            else:
                print(f"Номер {room_id} не найден")
                return None

        except Exception as e:
            print(f"Ошибка при получении номера {room_id} для редактирования: {e}")
            return None

    def validate_room_data(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидирует данные номера при редактировании."""
        errors = {}

        # Валидация обязательных полей
        required_fields = ["room_number", "capacity", "category", "price_per_night"]
        for field in required_fields:
            value = room_data.get(field, "")
            if not value or not str(value).strip():
                errors[field] = "Поле обязательно для заполнения"

        # Валидация номера комнаты
        try:
            room_number = room_data.get("room_number", "").strip()
            if room_number:
                Room.validate_room_number(room_number)
        except ValueError as e:
            errors["room_number"] = str(e)

        # Валидация вместимости
        try:
            capacity = room_data.get("capacity")
            if capacity:
                Room.validate_capacity(capacity)
        except ValueError as e:
            errors["capacity"] = str(e)

        # Валидация категории
        try:
            category = room_data.get("category", "").strip()
            if category:
                Room.validate_category(category)
        except ValueError as e:
            errors["category"] = str(e)

        # Валидация цены
        try:
            price = room_data.get("price_per_night")
            if price:
                price_decimal = Decimal(str(price))
                Room.validate_price(price_decimal)
        except ValueError as e:
            errors["price_per_night"] = str(e)

        # Валидация доступности
        is_available = room_data.get("is_available")
        if is_available is not None:
            try:
                Room.validate_boolean(is_available, "Доступность")
            except ValueError as e:
                errors["is_available"] = str(e)

        print(f"Результат валидации номера: {errors}")
        return errors

    def update_room(
        self, room_id: int, room_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновляет данные номера.
        Возвращает результат операции с сообщением об успехе или ошибках.
        """

        # Проверяем существование номера
        existing_room = self.repository.get_by_id(room_id)
        if not existing_room:
            print(f"Номер {room_id} не найден в репозитории")
            return {"success": False, "message": f"Номер с ID {room_id} не найден"}

        print(f"Существующий номер найден: {existing_room}")

        # Проверяем валидацию
        validation_errors = self.validate_room_data(room_data)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "message": "Ошибки валидации данных",
            }

        try:
            # Подготавливаем данные для репозитория
            repo_data = {
                "room_number": room_data["room_number"].strip(),
                "capacity": int(room_data["capacity"]),
                "is_available": room_data.get("is_available", True),
                "category": room_data["category"].strip(),
                "price_per_night": Decimal(str(room_data["price_per_night"])),
                "description": room_data.get("description", "").strip(),
            }
            print(f"Данные номера изменены")

            # Обновляем номер через репозиторий
            success = self.repository.update_room(room_id, repo_data)

            if success:
                return {"success": True, "message": "Данные номера успешно обновлены"}
            else:
                return {
                    "success": False,
                    "message": "Не удалось обновить данные номера",
                }

        except ValueError as e:
            print(f"ValueError при обновлении: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"Исключение при обновлении номера {room_id}: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Произошла ошибка: {str(e)}"}