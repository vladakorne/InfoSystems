from ClientRepDB import ClientRepDB
from typing import List, Callable
from ClientBase import Client
from ClientRepository import ClientRepository
from ClientShortInfo import ClientShort


class ClientRepDBDecorator:
    def __init__(self, db_repo: ClientRepDB,
                 filter_func: Callable[[Client], bool] = None,
                 sort_key: Callable[[Client], any] = None):
        self._db_repo = db_repo
        self._filter_func = filter_func
        self._sort_key = sort_key

    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        total_count = self._db_repo.get_count()
        clients = self._db_repo.get_k_n_short_list(total_count, 1)

        if self._filter_func:
            clients = list(filter(self._filter_func, clients))

        if self._sort_key:
            clients.sort(key=self._sort_key)

        start_index = (n - 1) * k
        if start_index >= len(clients):
            return []

        end_index = start_index + k
        return clients[start_index:end_index]

    def get_count(self) -> int:
        total_count = self._db_repo.get_count()
        clients = self._db_repo.get_k_n_short_list(total_count, 1)

        if self._filter_func:
            clients = list(filter(self._filter_func, clients))

        return len(clients)


class ClientRepFileDecorator:
    def __init__(self, file_repo: ClientRepository,
                 filter_func: Callable[[Client], bool] = None,
                 sort_key: Callable[[Client], any] = None):
        self._file_repo = file_repo
        self._filter_func = filter_func
        self._sort_key = sort_key

    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        clients = self._file_repo.read_all()

        if self._filter_func:
            clients = list(filter(self._filter_func, clients))

        if self._sort_key:
            clients.sort(key=self._sort_key)

        start_index = (n - 1) * k
        if start_index >= len(clients):
            return []

        end_index = start_index + k
        page_clients = clients[start_index:end_index]

        return [ClientShort(c.id, c.surname, c.name, c.patronymic, c.phone) for c in page_clients]

    def get_count(self) -> int:
        clients = self._file_repo.read_all()

        if self._filter_func:
            clients = list(filter(self._filter_func, clients))

        return len(clients)
