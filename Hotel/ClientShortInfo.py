import re
import json

class ClientShort:
    def __init__(self, *args, **kwargs):
        self._id = None
        self._surname = None
        self._name = None
        self._patronymic = None
        self._phone = None

        if kwargs.get("from_string"):
            if not args:
                raise ValueError("Для from_string необходимо передать строку первым аргументом")
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 5:
                parts.append("")
            self._init_short_fields(*parts[:5])

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError("Для from_dict необходимо передать dict первым аргументом")
            data = args[0]
            self._init_short_fields(
                data.get("id"),
                data.get("surname"),
                data.get("name"),
                data.get("patronymic", ""),
                data.get("phone")
            )

        elif kwargs.get("from_json"):
            if not args:
                raise ValueError("Для from_json необходимо передать JSON-строку первым аргументом")
            try:
                data = json.loads(args[0])
            except json.JSONDecodeError as e:
                raise ValueError(f"Некорректный JSON: {e}")
            if not isinstance(data, dict):
                raise ValueError("JSON должен содержать объект (dict)")

            self.__init__(data, from_dict=True)

        else:
            self._init_short_fields(*args)

    def _init_short_fields(self, id_value, surname: str, name: str, patronymic: str = "", phone: str = None):
        self._id = self.validate_id(id_value)
        self._surname = self.validate_fio(surname, "Фамилия")
        self._name = self.validate_fio(name, "Имя")
        self._phone = self.validate_phone(phone)
        self._patronymic = self.validate_fio(patronymic, "Отчество") if patronymic else ""

    @staticmethod
    def validate_required(value, field_name: str):
        if not value or not str(value).strip():
            raise ValueError(f"Поле '{field_name}' не может быть пустым!")
        return value

    @staticmethod
    def validate_fio(value: str, field_name: str):
        value = ClientShort.validate_required(value, field_name)
        pattern = r"^[А-Яа-яЁёA-Za-z]+$"
        if not re.match(pattern, value):
            raise ValueError(f"{field_name} должно содержать только буквы!")
        return value

    @staticmethod
    def validate_phone(phone: str):
        phone = ClientShort.validate_required(phone, "Телефон")
        phone = str(phone)
        pattern = r"^\+?\d{7,11}$"
        if not re.match(pattern, phone):
            raise ValueError("Телефон должен содержать только цифры и '+' (от 7 до 11 символов)!")
        return phone

    @staticmethod
    def validate_id(id_value):
        if id_value is None:
            raise ValueError("ID не может быть пустым!")
        try:
            id_int = int(id_value)
            if id_int < 0:
                raise ValueError("ID не может быть отрицательным числом!")
            return id_int
        except (ValueError, TypeError):
            raise ValueError("ID должен быть неотрицательным целым числом!")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = self.validate_id(value)

    @property
    def surname(self):
        return self._surname

    @surname.setter
    def surname(self, value: str):
        self._surname = self.validate_fio(value, "Фамилия")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = self.validate_fio(value, "Имя")

    @property
    def patronymic(self):
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value: str):
        self._patronymic = self.validate_fio(value, "Отчество") if value else ""

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = self.validate_phone(value)

    def __str__(self):
        initials = f"{self.name[0]}." if self.name else ""
        patronymic_initial = f"{self.patronymic[0]}." if self.patronymic else ""
        return f"ClientShort [ID: {self.id}]: {self.surname} {initials}{patronymic_initial}, {self.phone}"

    def __repr__(self):
        return f"ClientShort(id={self.id}, surname='{self.surname}', name='{self.name}', patronymic='{self.patronymic}', phone='{self.phone}')"
