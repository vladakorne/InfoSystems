from abc import ABC, abstractmethod
from ClientShortInfo import ClientShort
from ClientBase import Client

class ClientRepository(ABC):
    def __init__(self, path):
        self.path = path
        self.clients = []
        self.clients = self.read_all()

    @abstractmethod
    def read_all(self):
        pass

    @abstractmethod
    def write_all(self):
        pass

    # c
    def get_by_id(self, client_id):
        for client in self.clients:
            if client.id == client_id:
                return client
        return None

    # d
    def get_k_n_short_list(self, k, n):
        start = (n - 1) * k
        end = start + k
        slice_clients = self.clients[start:end]
        return [
            ClientShort(c.id, c.surname, c.name, c.patronymic, c.phone)
            for c in slice_clients
        ]

    # e
    def sort_by_surname(self):
        self.clients.sort(key=lambda c: c.surname)
        self.write_all()

    # f
    def add_client(self, client: Client):
        new_id = max((c.id for c in self.clients), default=0) + 1
        client.id = new_id
        self.clients.append(client)
        self.write_all()
        return new_id

    # g
    def replace_by_id(self, client_id, new_client: Client):
        for i, client in enumerate(self.clients):
            if client.id == client_id:
                new_client.id = client_id
                self.clients[i] = new_client
                self.write_all()
                return True
        raise ValueError(f"Клиент с ID {client_id} не найден")

    # h
    def delete_by_id(self, client_id):
        for i, client in enumerate(self.clients):
            if client.id == client_id:
                del self.clients[i]
                self.write_all()
                return True
        raise ValueError(f"Клиент с ID {client_id} не найден")

    # i
    def get_count(self):
        return len(self.clients)
