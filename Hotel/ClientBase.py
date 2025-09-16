class Client:
  def __init__(self, surname: str, name: str, phone: str,
                 patronymic: str = "", passport: str = None, 
                 email: str = None, comment: str = ""):
        self._surname = surname
        self._name = name
        self._patronymic = patronymic
        self._passport = passport
        self._phone = phone 
        self._email = email
        self._comment = comment

    @property
    def surname(self): 
        return self._surname

    @surname.setter
    def surname(self, value: str):
        self._surname = value

    @property
    def name(self): 
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def patronymic(self): 
        return self._patronymic

    @patronymic.setter
    def patronymic(self, value: str):
        self._patronymic = value

    @property
    def passport(self): 
        return self._passport

    @passport.setter
    def passport(self, value: str):
        self._passport = value

    @property
    def phone(self): 
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = value

    @property
    def email(self): 
        return self._email

    @email.setter
    def email(self, value: str):
        self._email = value

    @property
    def comment(self): 
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value
