"""Реализация репозитория клиентов в формате YAML."""

import yaml
import os
from typing import List

from ClientBase import Client
from ClientRepository import ClientRepository


class ClientRepYaml(ClientRepository):
    """Реализация ClientRepository для хранения клиентов в YAML-файле."""

    def read_all(self) -> List[Client]:
        """Считывает всех клиентов из YAML-файла."""
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)  # загрузка данных
                if isinstance(data, dict):  # проверем тип данных
                    data = [data]  # преобразовываем слоаварь в список
                return [
                    Client(d, from_dict=True) for d in data
                ]  # в цикле по элементам данных создается объект из словаря
            except yaml.YAMLError:
                return []

    def write_all(self) -> None:
        """Сохраняет всех клиентов в YAML-файл."""
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
        with open(self.path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
