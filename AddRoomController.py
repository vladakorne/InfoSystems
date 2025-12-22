"""
Контроллер для добавления нового номера.
Отдельный контроллер для формы добавления.
"""

from typing import Dict, Any, Optional
from decimal import Decimal

from Room import Room
from RoomRepDBAdapter import RoomRepDBAdapter
from RoomRepDB import RoomRepDB


class AddRoomController:
    """Контроллер для управления формой добавления номера."""

    def __init__(self, repository: Optional[RoomRepDBAdapter] = None) -> None:
        self.repository: RoomRepDBAdapter = repository or RoomRepDBAdapter(
            RoomRepDB()
        )

    def validate_room_data(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует данные номера.
        Возвращает словарь с ошибками или пустой словарь если валидация прошла успешно.
        """
        errors = {}

        # Валидация обязательных полей
        required_fields = ["room_number", "capacity", "category", "price_per_night"]
        for field in required_fields:
            value = room_data.get(field, "")
            if not value or not str(value).strip():
                errors[field] = "Поле обязательно для заполнения"

        # Валидация номера комнаты с использованием метода из Room
        try:
            if "room_number" in room_data and room_data["room_number"].strip():
                Room.validate_room_number(room_data["room_number"].strip())
        except ValueError as e:
            errors["room_number"] = str(e)

        # Валидация вместимости с использованием метода из Room
        try:
            if "capacity" in room_data and room_data["capacity"]:
                Room.validate_capacity(room_data["capacity"])
        except ValueError as e:
            errors["capacity"] = str(e)

        # Валидация категории с использованием метода из Room
        try:
            if "category" in room_data and room_data["category"].strip():
                Room.validate_category(room_data["category"].strip())
        except ValueError as e:
            errors["category"] = str(e)

        # Валидация цены с использованием метода из Room
        try:
            if "price_per_night" in room_data and room_data["price_per_night"]:
                # Преобразуем в Decimal для валидации
                price = Decimal(str(room_data["price_per_night"]))
                Room.validate_price(price)
        except ValueError as e:
            errors["price_per_night"] = str(e)

        # Валидация доступности
        is_available = room_data.get("is_available")
        if is_available is not None:
            try:
                Room.validate_boolean(is_available, "Доступность")
            except ValueError as e:
                errors["is_available"] = str(e)

        return errors

    def add_room(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Добавляет новый номер.
        Возвращает результат операции с сообщением об успехе или ошибках.
        """
        print(f"Данные номера получены: {room_data}")  # Добавляем лог

        # Проверяем валидацию
        validation_errors = self.validate_room_data(room_data)
        print(f"Результат валидации: {validation_errors}")  # Добавляем лог

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
                "floor": room_data.get("floor"),
                "area": room_data.get("area"),
                "equipment": room_data.get("equipment", "").strip(),
            }
            print(f"Данные для репозитория: {repo_data}")  # Добавляем лог

            # Добавляем номер через репозиторий
            success = self.repository.add_room(repo_data)

            if success:
                return {
                    "success": True,
                    "message": "Номер успешно добавлен",
                    "room_id": success if isinstance(success, int) else None
                }
            else:
                return {
                    "success": False,
                    "message": "Не удалось добавить номер"
                }

        except ValueError as e:
            print(f"ValueError при добавлении номера: {e}")  # Добавляем лог
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"Исключение при добавлении номера: {e}")  # Добавляем лог
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Произошла ошибка: {str(e)}"}

    def get_empty_room_form(self) -> Dict[str, Any]:
        """Возвращает шаблон пустой формы для номера."""
        return {
            "room_number": "",
            "capacity": "",
            "is_available": True,
            "category": "Стандарт",
            "price_per_night": "",
            "description": "",
            "floor": "",
            "area": "",
            "equipment": "",
        }