"""ClientRepository"""

from abc import ABC, abstractmethod
from typing import List

from ClientBase import Client
from ClientShortInfo import ClientShort


class ClientRepository(ABC):
    """Абстрактный класс репозитория клиентов."""

    def __init__(self, path: str):
        self.path = path
        self.clients: List[Client] = []
        self.clients = self.read_all()

    @abstractmethod  # декоратор, указывающий что метод должен быть реализован в дочерних классах
    def read_all(self) -> List[Client]:
        """Считывает всех клиентов из источника данных."""

    @abstractmethod
    def write_all(self) -> None:
        """Сохраняет всех клиентов в источник данных."""

    def get_by_id(self, client_id: int) -> Client | None:
        """Возвращает клиента по его ID или None, если не найден."""
        for client in self.clients:
            if client.id == client_id:
                return client
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        """Возвращает список из k клиентов со страницы n."""
        sorted_clients = sorted(self.clients, key=lambda x: x.id)
        start = (n - 1) * k
        end = start + k
        slice_clients = sorted_clients[start:end]
        return [
            ClientShort(c.id, c.surname, c.name, c.patronymic, c.phone)
            for c in slice_clients
        ]

    def sort_by_surname(self) -> None:
        """Сортирует список клиентов по фамилии и сохраняет изменения."""
        self.clients.sort(key=lambda c: c.surname)
        self.write_all()

    def add_client(self, client: Client) -> bool:
        """Добавляет нового клиента"""
        for existing in self.clients:  # цикл проверки по существующим клиентам
            if existing.equals(client):  # проверка дубликатов
                raise ValueError("Клиент с такими данными уже существует!")
        new_id = max((c.id for c in self.clients), default=0) + 1
        client.id = new_id  # присвоили новый id и добавили в список
        self.clients.append(client)
        self.write_all()
        return True

    def update_client(self, client_id: int, new_client: Client) -> bool:
        """Заменяет клиента по ID новым клиентом.
        Возвращает True при успешной замене."""
        for i, client in enumerate(self.clients):
            if client.id == client_id:
                for existing in self.clients:
                    if existing.id != client_id and existing.equals(new_client):
                        raise ValueError("Клиент с такими данными уже существует!")
                new_client.id = client_id
                self.clients[i] = new_client
                self.write_all()
                return True
        raise ValueError(f"Клиент с ID {client_id} не найден")

    def delete_client(self, client_id: int) -> bool:
        """Удаляет клиента по ID.
        Возвращает True при успешном удалении."""
        for i, client in enumerate(self.clients):  # цикл с индексом
            if client.id == client_id:
                del self.clients[i]
                self.write_all()
                return True
        raise ValueError(f"Клиент с ID {client_id} не найден")

    # def delete_client_test(self, client_id: int) -> bool:
    #     for i in range (len(self.clients)):
    #         client = self.clients[i]
    #         if client.id == client_id:
    #             del self.clients[i]
    #             self.write_all()
    #             return True

    def get_count(self) -> int:
        """Возвращает количество клиентов в репозитории."""
        return len(self.clients)
