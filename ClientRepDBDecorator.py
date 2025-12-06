"""Декораторы для репозиториев клиентов с поддержкой фильтрации и сортировки."""

from typing import Any, Callable, List

from ClientBase import Client
from ClientRepDB import ClientRepDB
from ClientRepository import ClientRepository
from ClientShortInfo import ClientShort


class ClientRepDBDecorator:
    """Декоратор для ClientRepDB с встроенной фильтрацией и сортировкой."""

    def __init__(self, db_repo: ClientRepDB):
        self._db_repo = db_repo  # объект репозитория бд
        self._filter_func: Callable[
            [Client], bool
        ] = lambda c: c.surname.lower().startswith(
            "И"
        )  # фильтр
        self._sort_key: Callable[[Client], Any] = (
            lambda c: c.name.lower()
        )  # сортировка по имени

    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        """Возвращает список k клиентов со страницы n с фильтрацией и сортировкой."""
        total_count = self._db_repo.get_count()
        clients: List[Client] = self._db_repo.get_k_n_short_list(
            total_count, 1
        )  # загрузили клиентов из бд

        clients = list(filter(self._filter_func, clients))  # применили фильтр
        # filter() возвращает итератор, который преобразуем в список

        clients.sort(key=self._sort_key)

        start_index = (n - 1) * k
        if start_index >= len(clients):
            return []

        end_index = start_index + k
        return clients[start_index:end_index]

    def get_count(self) -> int:
        """Возвращает количество клиентов, прошедших фильтрацию."""
        total_count = self._db_repo.get_count()
        clients: List[Client] = self._db_repo.get_k_n_short_list(total_count, 1)

        clients = list(filter(self._filter_func, clients))

        return len(clients)


class ClientRepFileDecorator:
    """Декоратор для ClientRepository с встроенной фильтрацией и сортировкой."""

    def __init__(self, file_repo: ClientRepository):
        self._file_repo = file_repo
        self._filter_func: Callable[[Client], bool] = lambda c: (
            c.surname.startswith("И") or c.phone[2:5] == "929"
        )
        self._sort_key: Callable[[Client], Any] = lambda c: c.surname.lower()

    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        """Возвращает список k клиентов со страницы n с фильтрацией и сортировкой."""
        clients: List[Client] = self._file_repo.read_all()

        clients = list(filter(self._filter_func, clients))

        clients.sort(key=self._sort_key)

        start_index = (n - 1) * k
        if start_index >= len(clients):
            return []

        end_index = start_index + k
        page_clients = clients[start_index:end_index]

        return [
            ClientShort(c.id, c.surname, c.name, c.patronymic, c.phone)
            for c in page_clients
        ]

    def get_count(self) -> int:
        """Возвращает количество клиентов, прошедших фильтрацию."""
        clients: List[Client] = self._file_repo.read_all()
        clients = list(filter(self._filter_func, clients))
        return len(clients)
