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

            super().__init__(
                client_short.id,
                client_short.surname,
                client_short.name,
                client_short.patronymic,
                client_short.phone
            )
            self._passport = self.validate_passport(kwargs.get("passport"))
            self._email = self.validate_email(kwargs.get("email")) if kwargs.get("email") else None
            self._comment = kwargs.get("comment", "")

        elif kwargs.get("from_string"):
            if not args:
                raise ValueError("Для from_string необходимо передать строку первым аргументом")
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 8:
                parts.append("")

            super().__init__(*parts[:5])
            self._passport = self.validate_passport(parts[5]) if parts[5] else None
            self._email = self.validate_email(parts[6]) if parts[6] else None
            self._comment = parts[7] or ""

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError("Для from_dict необходимо передать dict первым аргументом")
            data = args[0]

            super().__init__(
                data.get("id"),
                data.get("surname"),
                data.get("name"),
                data.get("patronymic", ""),
                data.get("phone")
            )
            self._passport = self.validate_passport(data.get("passport"))
            self._email = self.validate_email(data.get("email")) if data.get("email") else None
            self._comment = data.get("comment", "")

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
            if len(args) < 5:
                raise ValueError("Недостаточно аргументов для базовой инициализации")
            super().__init__(*args[:5])
            passport = args[5] if len(args) > 5 else None
            email = args[6] if len(args) > 6 else None
            comment = args[7] if len(args) > 7 else ""
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
        return f"Client [ID: {self.id}]: {self.surname} {self.name} {self.patronymic}".strip()

    def __repr__(self):
        return (f"Client(id={self.id}, surname='{self.surname}', name='{self.name}', "
                f"patronymic='{self.patronymic}', phone='{self.phone}', "
                f"passport='{self.passport}', email='{self.email}', comment='{self.comment}')")

class Client_rep_json:
    def __init__(self, path):
        self.path = path
        self.clients = self.read_all()

    # a
    def read_all(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    data = [data]
                return [Client(d, from_dict=True) for d in data]
            except json.JSONDecodeError:
                return []

    # b
    def write_all(self):
        data = [
            {
                "id": c.id,
                "surname": c.surname,
                "name": c.name,
                "patronymic": c.patronymic,
                "phone": c.phone,
                "passport": c.passport,
                "email": c.email,
                "comment": c.comment
            }
            for c in self.clients
        ]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # c
    def get_by_id(self, client_id):
        for client in self.clients:
            if client.id == client_id:
                return client
        return None

    # d
    def get_k_n_short_list(self, k, n):
        start = (n - 1) * k
        end = start + k
        slice_clients = self.clients[start:end]
        return [
            ClientShort(c.id, c.surname, c.name, c.patronymic, c.phone)
            for c in slice_clients
        ]

    # e
    def sort_by_surname(self):
        self.clients.sort(key=lambda c: c.surname)
        self.write_all()

    # f
    def add_client(self, client: Client):
        new_id = max((c.id for c in self.clients), default=0) + 1
        client.id = new_id
        self.clients.append(client)
        self.write_all()
        return new_id

    # g
    def replace_by_id(self, client_id, new_client: Client):
        for i, client in enumerate(self.clients):
            if client.id == client_id:
                new_client.id = client_id
                self.clients[i] = new_client
                self.write_all()
                return True
        raise ValueError(f"Клиент с ID {client_id} не найден")

    # h
    def delete_by_id(self, client_id):
        for i, client in enumerate(self.clients):
            if client.id == client_id:
                del self.clients[i]
                self.write_all()
                return True
        raise ValueError(f"Клиент с ID {client_id} не найден")

    # i
    def get_count(self):
        return len(self.clients)
