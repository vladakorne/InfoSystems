from typing import List, Callable
from ClientBase import Client
from ClientRepDB import ClientRepDB


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

