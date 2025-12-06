"""ClientShort"""

import json
import re


class ClientShort:
    """Класс для хранения краткой информации о клиенте."""

    def __init__(self, *args, **kwargs):
        """Инициализирует клиента из различных источников."""
        if kwargs.get("from_string"):
            if not args:
                raise ValueError(
                    "Для from_string необходимо передать строку первым аргументом."
                )
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 5:
                parts.append("")
            self._init_short_fields(*parts[:5])

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError(
                    "Для from_dict необходимо передать dict первым аргументом."
                )
            data = args[0]
            self._init_short_fields(
                data.get("id"),
                data.get("surname"),
                data.get("name"),
                data.get("patronymic", ""),
                data.get("phone"),
            )

        elif kwargs.get("from_json"):
            if not args:
                raise ValueError(
                    "Для from_json необходимо передать JSON-строку первым аргументом."
                )
            try:
                data = json.loads(args[0])
            except json.JSONDecodeError as e:
                raise ValueError(f"Некорректный JSON: {e}") from e
            if not isinstance(data, dict):
                raise ValueError("JSON должен содержать объект (dict).")
            super().__init__(
                data, from_dict=True
            )  # Исправлено: super() вместо self.__init__

        else:
            self._init_short_fields(*args)

    def _init_short_fields(self, id_value, surname, name, patronymic="", phone=None):
        """Инициализирует краткие поля клиента."""
        self._id = self.validate_id(id_value)
        self._surname = self.validate_fio(surname, "Фамилия")
        self._name = self.validate_fio(name, "Имя")
        self._phone = self.validate_phone(phone)
        self._patronymic = (
            self.validate_fio(patronymic, "Отчество") if patronymic else ""
        )

    @staticmethod
    def validate_required(value, field_name: str):
        """Проверяет что значение не пустое."""
        if not value or not str(value).strip():
            raise ValueError(f"Поле '{field_name}' не может быть пустым!")
        return value

    @staticmethod
    def validate_fio(value: str, field_name: str):
        """Валидирует ФИО."""
        value = ClientShort.validate_required(value, field_name)
        if not re.match(r"^[А-Яа-яЁёA-Za-z]+$", value):
            raise ValueError(f"{field_name} должно содержать только буквы!")
        return value

    @staticmethod
    def validate_phone(phone: str):
        """Валидирует номер телефона."""
        phone = ClientShort.validate_required(phone, "Телефон")
        phone = str(phone)
        if not re.match(r"^\+?\d{7,11}$", phone):
            raise ValueError(
                "Телефон должен содержать только цифры и '+', длиной от 7 до 11 символов!"
            )
        return phone

    @staticmethod
    def validate_id(id_value):
        """Валидирует ID клиента."""
        if id_value is None:
            raise ValueError("ID не может быть пустым!")
        try:
            id_int = int(id_value)
            if id_int < 0:
                raise ValueError("ID не может быть отрицательным числом!")
            return id_int
        except (ValueError, TypeError) as exc:
            raise ValueError("ID должен быть неотрицательным целым числом!") from exc

    @property
    def id(self):
        """Возвращает ID клиента."""
        return self._id

    @id.setter
    def id(self, value):
        """Устанавливает ID клиента."""
        self._id = self.validate_id(value)

    @property
    def surname(self):
        """Возвращает фамилию клиента."""
        return self._surname

    @surname.setter
    def surname(self, value: str):
        """Устанавливает фамилию клиента."""
        self._surname = self.validate_fio(value, "Фамилия")

    @property
    def name(self):
        """Возвращает имя клиента."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Устанавливает имя клиента."""
        self._name = self.validate_fio(value, "Имя")

    @property
    def patronymic(self):
        """Возвращает отчество клиента."""
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value: str):
        """Устанавливает отчество клиента."""
        self._patronymic = self.validate_fio(value, "Отчество") if value else ""

    @property
    def phone(self):
        """Возвращает телефон клиента."""
        return self._phone

    @phone.setter
    def phone(self, value: str):
        """Устанавливает телефон клиента."""
        self._phone = self.validate_phone(value)

    def __str__(self):
        """Возвращает строковое представление клиента."""
        initials = f"{self.name[0]}." if self.name else ""
        patronymic_initial = f"{self.patronymic[0]}." if self.patronymic else ""
        return (
            f"ClientShort [ID: {self.id}]: {self.surname} "
            f"{initials}{patronymic_initial}, {self.phone}"
        )

    def __repr__(self):
        """Возвращает техническое представление клиента."""
        return (
            f"ClientShort(id={self.id}, surname='{self.surname}', "
            f"name='{self.name}', patronymic='{self.patronymic}',"
            f" phone='{self.phone}')"
        )
