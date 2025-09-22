import re
import json
import os

class Client:
    def __init__(self, *args, **kwargs):
        if kwargs.get("from_string"):
            if not args:
                raise ValueError("Для from_string необходимо передать строку первым аргументом")
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 7:
                parts.append("")
            self._init_fields(*parts[:7])

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError("Для from_dict необходимо передать dict первым аргументом")
            data = args[0]
            self._init_fields(
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
            self._init_fields(*args)

    def _init_fields(self, surname: str, name: str, patronymic: str = "",
                     phone: str = None, passport: str = None, email: str = None, comment: str = ""):
        self._surname = self.validate_fio(surname, "Фамилия")
        self._name = self.validate_fio(name, "Имя")
        self._phone = self.validate_phone(phone)

        self._patronymic = self.validate_fio(patronymic, "Отчество") if patronymic else ""
        self._passport = self.validate_passport(passport)
        self._email = self.validate_email(email) if email else None
        self._comment = comment or ""


    @staticmethod
    def validate_required(value, field_name: str):
        if not value or not str(value).strip():
            raise ValueError(f"Поле '{field_name}' не может быть пустым!")
        return value

    @staticmethod
    def validate_fio(value: str, field_name: str):
        value = Client.validate_required(value, field_name)
        pattern = r"^[А-Яа-яЁёA-Za-z]+$"
        if not re.match(pattern, value):
            raise ValueError(f"{field_name} должно содержать только буквы!")
        return value

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
    def validate_phone(phone: str):
        phone = Client.validate_required(phone, "Телефон")
        phone = str(phone)
        pattern = r"^\+?\d{7,11}$"
        if not re.match(pattern, phone):
            raise ValueError("Телефон должен содержать только цифры и '+' (от 7 до 11 символов)!")
        return phone

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
    def passport(self): 
        return self._passport

    @passport.setter
    def passport(self, value: str):
        self._passport = self.validate_passport(value)

    @property
    def phone(self): 
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = self.validate_phone(value)

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

    
    def equals(self, other, by_all_fields=True):
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
                f"patronymic='{self.patronymic}', passport='{self.passport}', "
                f"phone='{self.phone}', email='{self.email}', comment='{self.comment}')")
