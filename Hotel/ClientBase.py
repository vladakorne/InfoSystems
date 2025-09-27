import re
import json
import os
from ClientShortInfo import ClientShort

class Client(ClientShort):
    def __init__(self, *args, **kwargs):
        if kwargs.get("from_client_short"):
            client_short = args[0]
            if not isinstance(client_short, ClientShort):
                raise TypeError("Client.from_client_short требует объект ClientShort")
            passport = kwargs.get("passport")
            email = kwargs.get("email")
            comment = kwargs.get("comment", "")

            self._init_full_fields(
                client_short.surname,
                client_short.name,
                client_short.patronymic,
                client_short.phone,
                passport,
                email,
                comment
            )

        elif kwargs.get("from_string"):
            if not args:
                raise ValueError("Для from_string необходимо передать строку первым аргументом")
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 7:
                parts.append("")
            self._init_full_fields(*parts[:7])

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError("Для from_dict необходимо передать dict первым аргументом")
            data = args[0]
            self._init_full_fields(
                data.get("surname"),
                data.get("name"),
                data.get("patronymic", ""),
                data.get("phone"),
                data.get("passport"),
                data.get("email"),
                data.get("comment", "")
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
            self._init_full_fields(*args)

    def _init_full_fields(self, surname: str, name: str, patronymic: str = "",
                          phone: str = None, passport: str = None, email: str = None, comment: str = ""):

        super()._init_short_fields(surname, name, patronymic, phone)
        self._passport = self.validate_passport(passport)
        self._email = self.validate_email(email) if email else None
        self._comment = comment or ""

    @staticmethod
    def validate_passport(passport: str):
        if not passport:
            return None
        passport_clean = str(passport).replace(" ", "")
        pattern = r"^\d{10}$"
        if not re.match(pattern, passport_clean):
            raise ValueError("Паспорт должен состоять ровно из 10 цифр!")
        return passport_clean

    @staticmethod
    def validate_email(email: str):
        if not email:
            return None
        pattern = r"^(?!\.)[A-Za-z0-9](?:[A-Za-z0-9._%+-]*)@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if ".." in email:
            raise ValueError("Email не может содержать подряд идущие точки!")
        if not re.match(pattern, email):
            raise ValueError("Некорректный формат email!")
        return email

    @property
    def passport(self):
        return self._passport

    @passport.setter
    def passport(self, value: str):
        self._passport = self.validate_passport(value)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value: str):
        self._email = self.validate_email(value) if value else None

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value or ""

    @staticmethod
    def read_clients_from_txt(path):
        clients = []
        if not os.path.exists(path):
            print(f"Файл {path} не найден!")
            return clients
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        clients.append(Client(line, from_string=True))
                    except Exception as e:
                        print(f"Ошибка при чтении строки '{line}': {e}")
        return clients

    @staticmethod
    def read_clients_from_json(path):
        clients = []
        if not os.path.exists(path):
            print(f"Файл {path} не найден!")
            return clients
        with open(path, "r", encoding="utf-8") as f:
            try:
                data_list = json.load(f)
                if isinstance(data_list, dict):
                    data_list = [data_list]
                for data in data_list:
                    clients.append(Client(data, from_dict=True))
            except Exception as e:
                print(f"Ошибка при чтении JSON {path}: {e}")
        return clients

    def equals(self, other):
        if not isinstance(other, Client):
            return False
        return (
                self.surname == other.surname and
                self.name == other.name and
                self.patronymic == other.patronymic and
                self.passport == other.passport and
                self.phone == other.phone and
                self.email == other.email and
                self.comment == other.comment
        )

    def __str__(self):
        return f"Client: {self.surname} {self.name} {self.patronymic}".strip()

    def __repr__(self):
        return (f"Client(surname='{self.surname}', name='{self.name}', "
                f"patronymic='{self.patronymic}', phone='{self.phone}', "
                f"passport='{self.passport}', email='{self.email}', comment='{self.comment}')")
