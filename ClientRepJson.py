"""Реализация репозитория клиентов в формате JSON."""

import json
import os
from typing import List

from ClientBase import Client
from ClientRepository import ClientRepository


class ClientRepJson(ClientRepository):
    """Реализация ClientRepository для хранения клиентов в JSON-файле."""

    def read_all(self) -> List[Client]:
        """Считывает всех клиентов из JSON-файла."""
        if not os.path.exists(self.path):  # если нет файла, то возвращаем пустой список
            return []

        with open(
            self.path, "r", encoding="utf-8"
        ) as f:  # открываем файл в режиме чтения
            try:
                data = json.load(f)  # загрузка данных из файла
                if isinstance(data, dict):  # проверяем тип данных
                    data = [data]  # преобразовываем слоаварь в список
                return [
                    Client(d, from_dict=True) for d in data
                ]  # в цикле по элементам данных создается объект из словаря
            except (
                json.JSONDecodeError
            ):  # при ошибке декодирования возвращаем пустой список
                return []

    def write_all(self) -> None:
        """Сохраняет всех клиентов в JSON-файл."""
        data = [
            {
                "id": c.id,
                "surname": c.surname,
                "name": c.name,
                "patronymic": c.patronymic,
                "phone": c.phone,
                "passport": c.passport,
                "email": c.email,
                "comment": c.comment,
            }
            for c in self.clients  # выполняем действия для каждого элемента
        ]
        with open(
            self.path, "w", encoding="utf-8"
        ) as f:  # открываем файл в режиме записи
            json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=False)
