"""Room - модель номера в отеле"""

import re
from decimal import Decimal


class Room:
    """Класс для хранения информации о номере в отеле."""

    def __init__(self, *args, **kwargs):
        """Инициализирует номер из различных источников."""
        if kwargs.get("from_string"):
            if not args:
                raise ValueError(
                    "Для from_string необходимо передать строку первым аргументом."
                )
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 7:
                parts.append("")
            self._init_fields(*parts[:7])

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError(
                    "Для from_dict необходимо передать dict первым аргументом."
                )
            data = args[0]
            self._init_fields(
                data.get("id"),
                data.get("room_number"),
                data.get("capacity"),
                data.get("is_available"),
                data.get("category"),
                data.get("price_per_night"),
                data.get("description", ""),
            )

        else:
            # Прямая инициализация параметрами
            if len(args) >= 6:
                self._init_fields(*args[:7])
            else:
                # Если переданы именованные параметры
                self._init_fields(
                    kwargs.get("id"),
                    kwargs.get("room_number"),
                    kwargs.get("capacity"),
                    kwargs.get("is_available"),
                    kwargs.get("category"),
                    kwargs.get("price_per_night"),
                    kwargs.get("description", ""),
                )

    def _init_fields(
        self,
        id_value,
        room_number,
        capacity,
        is_available,
        category,
        price_per_night,
        description="",
    ):
        """Инициализирует поля номера."""
        self._id = self.validate_id(id_value)
        self._room_number = self.validate_room_number(room_number)
        self._capacity = self.validate_capacity(capacity)
        self._is_available = self.validate_boolean(is_available, "Доступность")
        self._category = self.validate_category(category)
        self._price_per_night = self.validate_price(price_per_night)
        self._description = description if description else ""

    @staticmethod
    def validate_required(value, field_name: str):
        """Проверяет что значение не пустое."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Поле '{field_name}' не может быть пустым!")
        return value

    @staticmethod
    def validate_id(id_value):
        """Валидирует ID номера."""
        if id_value is None:
            raise ValueError("ID не может быть пустым!")
        try:
            id_int = int(id_value)
            if id_int < 0:
                raise ValueError("ID не может быть отрицательным числом!")
            return id_int
        except (ValueError, TypeError) as exc:
            raise ValueError("ID должен быть неотрицательным целым числом!") from exc

    @staticmethod
    def validate_room_number(room_number: str):
        """Валидирует номер комнаты."""
        room_number = Room.validate_required(room_number, "Номер комнаты")
        room_number = str(room_number).strip()
        if not re.match(r"^\d{3}[A-Z]?$", room_number):
            raise ValueError("Номер комнаты должен быть в формате '101' или '101A'!")
        return room_number

    @staticmethod
    def validate_capacity(capacity):
        """Валидирует вместимость номера."""
        capacity = Room.validate_required(capacity, "Вместимость")
        try:
            capacity_int = int(capacity)
            if capacity_int < 1 or capacity_int > 10:
                raise ValueError("Вместимость должна быть от 1 до 10 человек!")
            return capacity_int
        except (ValueError, TypeError) as exc:
            raise ValueError("Вместимость должна быть целым числом!") from exc

    @staticmethod
    def validate_boolean(value, field_name: str):
        """Валидирует булево значение."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ["true", "1", "yes", "да", "доступен"]:
                return True
            elif value_lower in ["false", "0", "no", "нет", "занят"]:
                return False
        elif isinstance(value, int):
            return bool(value)
        raise ValueError(f"Поле '{field_name}' должно быть булевым значением!")

    @staticmethod
    def validate_category(category: str):
        """Валидирует категорию номера."""
        category = Room.validate_required(category, "Категория")
        category = str(category).strip()
        valid_categories = ["Стандарт", "Люкс", "Эконом", "Студия", "Апартаменты"]
        if category not in valid_categories:
            raise ValueError(
                f"Категория должна быть одной из: {', '.join(valid_categories)}"
            )
        return category

    @staticmethod
    def validate_price(price):
        """Валидирует цену за ночь."""
        price = Room.validate_required(price, "Цена за ночь")
        try:
            price_decimal = Decimal(str(price))
            if price_decimal <= 0:
                raise ValueError("Цена должна быть положительным числом!")
            return price_decimal
        except (ValueError, TypeError) as exc:
            raise ValueError("Цена должна быть числом!") from exc

    # Свойства (properties)
    @property
    def id(self):
        """Возвращает ID номера."""
        return self._id

    @id.setter
    def id(self, value):
        """Устанавливает ID номера."""
        self._id = self.validate_id(value)

    @property
    def room_number(self):
        """Возвращает номер комнаты."""
        return self._room_number

    @room_number.setter
    def room_number(self, value: str):
        """Устанавливает номер комнаты."""
        self._room_number = self.validate_room_number(value)

    @property
    def capacity(self):
        """Возвращает вместимость номера."""
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        """Устанавливает вместимость номера."""
        self._capacity = self.validate_capacity(value)

    @property
    def is_available(self):
        """Возвращает доступность номера."""
        return self._is_available

    @is_available.setter
    def is_available(self, value):
        """Устанавливает доступность номера."""
        self._is_available = self.validate_boolean(value, "Доступность")

    @property
    def category(self):
        """Возвращает категорию номера."""
        return self._category

    @category.setter
    def category(self, value: str):
        """Устанавливает категорию номера."""
        self._category = self.validate_category(value)

    @property
    def price_per_night(self):
        """Возвращает цену за ночь."""
        return self._price_per_night

    @price_per_night.setter
    def price_per_night(self, value):
        """Устанавливает цену за ночь."""
        self._price_per_night = self.validate_price(value)

    @property
    def description(self):
        """Возвращает описание номера."""
        return self._description

    @description.setter
    def description(self, value: str):
        """Устанавливает описание номера."""
        self._description = str(value) if value else ""

    def calculate_total_price(self, nights: int) -> Decimal:
        """Рассчитывает общую стоимость за указанное количество ночей."""
        if nights <= 0:
            raise ValueError("Количество ночей должно быть положительным числом!")
        return self.price_per_night * nights

    def __str__(self):
        """Возвращает строковое представление номера."""
        status = "Доступен" if self.is_available else "Занят"
        return (
            f"Room [ID: {self.id}]: №{self.room_number} "
            f"({self.category}, {self.capacity} чел.) - "
            f"{self.price_per_night} ₽/ночь - {status}"
        )

    def __repr__(self):
        """Возвращает техническое представление номера."""
        return (
            f"Room(id={self.id}, room_number='{self.room_number}', "
            f"capacity={self.capacity}, is_available={self.is_available}, "
            f"category='{self.category}', price_per_night={self.price_per_night}, "
            f"description='{self.description}')"
        )
