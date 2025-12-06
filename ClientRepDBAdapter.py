"""Адаптер между репозиторием клиентов и базой данных."""

from typing import List

from ClientBase import Client
from ClientRepDB import ClientRepDB
from ClientRepository import ClientRepository


class ClientRepDBAdapter(ClientRepository):
    """Класс-адаптер для работы с клиентами через базу данных."""

    def __init__(self, db_repo: ClientRepDB):
        """Инициализирует адаптер с указанным репозиторием базы данных."""
        self._db_repo = db_repo
        # вызывает конструктор базового ClientRepository
        super().__init__("database")

    def load(self) -> None:
        """Загружает список клиентов из базы данных."""
        count = self._db_repo.get_count()
        self._clients = (
            self._db_repo.get_k_n_short_list(count, 1)
            if count > 0
            else []  # получаем все записи если они есть, иначе пустой список
        )

    def save(self) -> None:
        """Сохраняет данные клиентов. Сохраняется напрямую в бд"""
        # метод оставлен пустым, так как данные сохраняются напрямую в базу данных
        # при каждом изменении через соответствующие методы

    def read_all(self) -> List[Client]:
        """Возвращает всех клиентов из базы данных."""
        self.load()
        return (
            self._clients.copy()
        )  # возвращает копию внутреннего списка для защиты от внешних изменений

    def write_all(self, clients: List[Client]) -> None:
        """Перезаписывает всех клиентов в базе данных."""
        # получаем текущий список клиентов из базы данных
        current_clients = self._db_repo.get_k_n_short_list(self._db_repo.get_count(), 1)
        # удаляем всех существующих клиентов
        for client in current_clients:
            self._db_repo.delete_client(client.id)

        # добавляем новых клиентов
        for client in clients:
            self._db_repo.add_client(
                {
                    "surname": client.surname,
                    "name": client.name,
                    "patronymic": client.patronymic,
                    "phone": client.phone,
                    "passport": client.passport,
                    "email": client.email,
                    "comment": client.comment,
                }
            )
        # обновляем локальный кэш клиентов
        self._clients = clients.copy()

    def get_by_id(self, client_id: int) -> Client | None:
        """Возвращает клиента по идентификатору."""
        return self._db_repo.get_by_id(
            client_id
        )  # прямое делегирование метода в ClientRepDB

    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        """Возвращает k клиентов со страницы n (краткая информация)."""
        return self._db_repo.get_k_n_short_list(
            k, n
        )  # делегирование метода пагинации в базу данных

    def add_client(self, client_data: dict) -> bool:
        """Добавляет нового клиента в базу данных."""
        result = self._db_repo.add_client(client_data)
        self.load()
        return result

    def update_client(self, client_id: int, client_data: dict) -> bool:
        """Обновляет данные клиента по ID."""
        result = self._db_repo.update_client(client_id, client_data)
        self.load()
        return result

    def delete_client(self, client_id: int) -> bool:
        """Удаляет клиента по ID."""
        result = self._db_repo.delete_client(client_id)
        self.load()  # обновляет локальный кэш после удаления
        return result

    def get_count(self) -> int:
        """Возвращает количество клиентов."""
        return (
            self._db_repo.get_count()
        )  # делегирование запроса количества записей в базу данных
