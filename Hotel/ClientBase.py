class Client:
    def __init__(self, surname: str, name: str, phone: str,
                   patronymic: str = "", passport: str = None, 
                   email: str = None, comment: str = ""):
          self._surname = self.validate_fio(surname, "Фамилия")
          self._name = self.validate_fio(name, "Имя")
          self._patronymic = self.validate_fio(patronymic, "Отчество") if patronymic else ""
          self._passport = self.validate_passport(passport)
          self._phone = self.validate_phone(phone)
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
        self._patronymic = self.validate_fio(value, "Отчество) if value else ""

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
        self._comment = value
