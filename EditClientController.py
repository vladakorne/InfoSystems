""" Контроллер для редактирования существующего клиента """

from typing import Dict, Any, Optional

from ClientBase import Client
from ClientShortInfo import ClientShort
from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB

class EditClientController:
    """Контроллер для управления формой редактирования клиента."""

    def __init__(self, repository: Optional[ClientRepDBAdapter] = None) -> None:
        self.repository: ClientRepDBAdapter = repository or ClientRepDBAdapter(
            ClientRepDB()
        ) # если репозиторий не передан, то создаем новый ClientRepDBAdapter с ClientRepDB

    def get_client_for_edit(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные клиента для редактирования."""
        try:
            client = self.repository.get_by_id(client_id)

            if client:
                result = {
                    "id": client.id,
                    "surname": client.surname,
                    "name": client.name,
                    "patronymic": client.patronymic or "",
                    "phone": client.phone,
                    "passport": client.passport or "",
                    "email": client.email or "",
                    "comment": client.comment or "",
                }
                return result # возвращаем словарь данных, чтобы заполнять форму
            else:
                print(f"Клиент {client_id} не найден")
                return None

        except Exception as e:
            print(f"Ошибка при получении клиента {client_id} для редактирования: {e}")
            return None

    def validate_client_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Валидирует данные клиента при редактировании """
        errors = {}

        # валидация обязательных полей
        required_fields = ["surname", "name", "phone"]
        for field in required_fields:
            value = client_data.get(field, "")
            if not value or not str(value).strip():
                errors[field] = "Поле обязательно для заполнения"

        try:
            surname = client_data.get("surname", "").strip()
            if surname:
                ClientShort.validate_fio(surname, "Фамилия")
        except ValueError as e:
            errors["surname"] = str(e)

        try:
            name = client_data.get("name", "").strip()
            if name:
                ClientShort.validate_fio(name, "Имя")
        except ValueError as e:
            errors["name"] = str(e)

        try:
            patronymic = client_data.get("patronymic", "").strip()
            if patronymic:
                ClientShort.validate_fio(patronymic, "Отчество")
        except ValueError as e:
            errors["patronymic"] = str(e)

        try:
            phone = client_data.get("phone", "").strip()
            if phone:
                ClientShort.validate_phone(phone)
        except ValueError as e:
            errors["phone"] = str(e)

        try:
            passport = client_data.get("passport", "").strip()
            if passport:
                Client.validate_passport(passport)
        except ValueError as e:
            errors["passport"] = str(e)

        try:
            email = client_data.get("email", "").strip()
            if email:
                Client.validate_email(email)
        except ValueError as e:
            errors["email"] = str(e)

        print(f"Результат валидации: {errors}")
        return errors

    def update_client(
        self, client_id: int, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """ Обновляет данные клиента """

        # проверяем существование клиента
        existing_client = self.repository.get_by_id(client_id)
        if not existing_client:
            print(f"Клиент {client_id} не найден")
            return {"success": False, "message": f"Клиент с ID {client_id} не найден"}

        print(f"Существующий клиент найден: {existing_client}")

        # проверяем валидацию
        validation_errors = self.validate_client_data(client_data)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "message": "Ошибки валидации данных",
            }

        try:
            # подготавливаем данные для репозитория
            repo_data = {
                "surname": client_data["surname"].strip(),
                "name": client_data["name"].strip(),
                "patronymic": client_data.get("patronymic", "").strip(),
                "phone": client_data["phone"].strip(),
                "passport": client_data.get("passport", "").strip() or None,
                "email": client_data.get("email", "").strip() or None,
                "comment": client_data.get("comment", "").strip(),
            }
            print(f"Данные изменены")

            # обновляем клиента через репозиторий
            success = self.repository.update_client(client_id, repo_data)

            # обработка ошибок валидации
            if success:
                return {"success": True, "message": "Данные клиента успешно обновлены"}
            else:
                return {"success": False, "message": "Не удалось обновить данные клиента",}

        # обработка всех остальных исключений:
        except ValueError as e:
            print(f"ValueError при обновлении: {e}")
            return {"success": False, "message": str(e)}
        except Exception as e:
            print(f"Исключение при обновлении клиента {client_id}: {e}")
            return {"success": False, "message": f"Произошла ошибка: {str(e)}"}
