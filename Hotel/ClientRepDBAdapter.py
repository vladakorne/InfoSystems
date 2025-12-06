from ClientRepository import *
from ClientRepDB import *


class ClientRepDBAdapter(ClientRepository):
    def __init__(self, db_repo: ClientRepDB):
        self._db_repo = db_repo
        super().__init__("database")

    def load(self) -> None:
        count = self._db_repo.get_count()
        self._clients = self._db_repo.get_k_n_short_list(count, 1) if count > 0 else []

    def save(self) -> None:
        pass

    def read_all(self) -> List[Client]:
        self.load()
        return self._clients.copy()

    def write_all(self, clients: List[Client]) -> None:
        current_clients = self._db_repo.get_k_n_short_list(self._db_repo.get_count(), 1)
        for client in current_clients:
            self._db_repo.delete_client(client.id)

        for client in clients:
            self._db_repo.add_client({
                'surname': client.surname,
                'name': client.name,
                'patronymic': client.patronymic,
                'phone': client.phone,
                'passport': client.passport,
                'email': client.email,
                'comment': client.comment
            })
        self._clients = clients.copy()

    def get_by_id(self, client_id: int) -> Client | None:
        return self._db_repo.get_by_id(client_id)

    def add_client(self, client_data: dict) -> Client:
        client = self._db_repo.add_client(client_data)
        self.load()
        return client

    def update_client(self, client_id: int, client_data: dict) -> Client | None:
        result = self._db_repo.update_client(client_id, client_data)
        self.load()
        return result

    def delete_client(self, client_id: int) -> bool:
        result = self._db_repo.delete_client(client_id)
        self.load()
        return result

    def get_count(self) -> int:
        return self._db_repo.get_count()

    def sort_by_surname(self) -> List[Client]:
        count = self._db_repo.get_count()
        self._clients = self._db_repo.get_k_n_short_list(count, 1) if count > 0 else []
        self._clients.sort(key=lambda x: x.surname)
        return self._clients.copy()
