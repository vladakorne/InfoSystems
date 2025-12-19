""" Контроллер для добавления нового клиента """

from typing import Dict, Any, Optional

from ClientBase import Client
from ClientShortInfo import ClientShort
from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB


class AddClientController:
    """Контроллер для управления формой добавления клиента"""

    def __init__(self, repository: Optional[ClientRepDBAdapter] = None) -> None: # конструктор с опц пар - репозиторий
        self.repository: ClientRepDBAdapter = repository or ClientRepDBAdapter(
            ClientRepDB()
        ) # если репозиторий не передан, то создаем новый ClientRepDBAdapter с ClientRepDB

    def validate_client_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Валидирует данные клиента
        Возвращает словарь с ошибками или пустой словарь если валидация прошла успешно """
        errors = {}

        # валидация обязательных полей ФИО
        required_fields = ["surname", "name", "phone"]
        for field in required_fields:
            value = client_data.get(field, "")
            if not value or not str(value).strip():
                errors[field] = "Поле обязательно для заполнения"

        # валидация ФИО с использованием методов из ClientShortInfo
        try:
            if "surname" in client_data and client_data["surname"].strip():
                ClientShort.validate_fio(client_data["surname"].strip(), "Фамилия")
        except ValueError as e:
            errors["surname"] = str(e)

        try:
            if "name" in client_data and client_data["name"].strip():
                ClientShort.validate_fio(client_data["name"].strip(), "Имя")
        except ValueError as e:
            errors["name"] = str(e)

        try:
            patronymic = client_data.get("patronymic", "")
            if patronymic and str(patronymic).strip():
                ClientShort.validate_fio(patronymic.strip(), "Отчество")
        except ValueError as e:
            errors["patronymic"] = str(e)

        try:
            if "phone" in client_data and client_data["phone"]:
                ClientShort.validate_phone(client_data["phone"].strip())
        except ValueError as e:
            errors["phone"] = str(e)

        try:
            passport = client_data.get("passport", "")
            if passport and str(passport).strip():
                Client.validate_passport(passport.strip())
        except ValueError as e:
            errors["passport"] = str(e)

        try:
            email = client_data.get("email", "")
            if email and str(email).strip():
                Client.validate_email(email.strip())
        except ValueError as e:
            errors["email"] = str(e)

        return errors

    def add_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Добавляет нового клиента
        Возвращает результат операции с сообщением об успехе или ошибках  """

        validation_errors = self.validate_client_data(client_data)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "message": "Ошибки валидации данных",
            }

        try:
            # подготавливаем данные для репозитория : удаление пробелов, преобразование пустых строк в None
            repo_data = {
                "surname": client_data["surname"].strip(),
                "name": client_data["name"].strip(),
                "patronymic": client_data.get("patronymic", "").strip(),
                "phone": client_data["phone"].strip(),
                "passport": client_data.get("passport", "").strip() or None,
                "email": client_data.get("email", "").strip() or None,
                "comment": client_data.get("comment", "").strip(),
            }

            # добавляем клиента через репозиторий
            success = self.repository.add_client(repo_data)

            if success:
                return {"success": True, "message": "Клиент успешно добавлен"}
            else:
                return {"success": False, "message": "Не удалось добавить клиента"}

        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Произошла ошибка: {str(e)}"}

    def get_empty_client_form(self) -> Dict[str, Any]:
        """возвращает шаблон пустой формы для клиента."""
        return {
            "surname": "",
            "name": "",
            "patronymic": "",
            "phone": "",
            "passport": "",
            "email": "",
            "comment": "",
        }
