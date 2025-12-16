"""Декораторы для репозиториев клиентов с поддержкой фильтрации и сортировки."""

from typing import Any, Callable, List, Optional
from abc import ABC, abstractmethod
from ClientBase import Client
from ClientRepDB import ClientRepDB
from ClientRepository import ClientRepository
from ClientShortInfo import ClientShort


class ClientFilter(ABC):
    """Абстрактный базовый класс для фильтров клиентов."""

    @abstractmethod
    def apply(self, client: Client) -> bool:
        """Возвращает True, если клиент проходит фильтр."""
        pass


class SurnameFilter(ClientFilter):
    """Фильтр по началу фамилии."""

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix.lower()

    def apply(self, client: Client) -> bool:
        if not self.prefix:
            return True
        return client.surname.lower().startswith(self.prefix)


class NameFilter(ClientFilter):
    """Фильтр по началу имени."""

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix.lower()

    def apply(self, client: Client) -> bool:
        if not self.prefix:
            return True
        return client.name.lower().startswith(self.prefix)


class PatronymicFilter(ClientFilter):
    """Фильтр по началу отчества."""

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix.lower()

    def apply(self, client: Client) -> bool:
        if not self.prefix:
            return True
        return client.patronymic.lower().startswith(self.prefix)


class PhoneFilter(ClientFilter):
    """Фильтр по номеру телефона (подстрока)."""

    def __init__(self, phone_substring: str) -> None:
        self.phone_substring = phone_substring

    def apply(self, client: Client) -> bool:
        if not self.phone_substring:
            return True
        return self.phone_substring in client.phone


class CompositeFilter(ClientFilter):
    """Композитный фильтр, объединяющий несколько фильтров через AND."""

    def __init__(self) -> None:
        self.filters: List[ClientFilter] = []

    def add_filter(self, filter_obj: ClientFilter) -> None:
        """Добавляет фильтр в композит."""
        self.filters.append(filter_obj)

    def apply(self, client: Client) -> bool:
        """Применяет все фильтры через логическое И."""
        for filter_obj in self.filters:
            if not filter_obj.apply(client):
                return False
        return True


class ClientSorter:
    """Фабрика для создания функций сортировки."""

    @staticmethod
    def by_surname(reverse: bool = False) -> Callable[[Client], Any]:
        """Сортировка по фамилии."""
        if reverse:
            return lambda c: c.surname.lower()
        return lambda c: c.surname.lower()

    @staticmethod
    def by_name(reverse: bool = False) -> Callable[[Client], Any]:
        """Сортировка по имени."""
        if reverse:
            return lambda c: c.name.lower()
        return lambda c: c.name.lower()

    @staticmethod
    def by_patronymic(reverse: bool = False) -> Callable[[Client], Any]:
        """Сортировка по отчеству."""
        if reverse:
            return lambda c: c.patronymic.lower()
        return lambda c: c.patronymic.lower()

    @staticmethod
    def by_phone(reverse: bool = False) -> Callable[[Client], Any]:
        """Сортировка по телефону."""
        if reverse:
            return lambda c: c.phone
        return lambda c: c.phone

    @staticmethod
    def by_id(reverse: bool = False) -> Callable[[Client], Any]:
        """Сортировка по ID."""
        if reverse:
            return lambda c: c.id
        return lambda c: c.id


class ClientRepDBDecorator:
    """Декоратор для ClientRepDB с гибкой фильтрацией и сортировкой."""

    def __init__(self, db_repo: ClientRepDB):
        self._db_repo = db_repo
        self._filters: CompositeFilter = CompositeFilter()
        self._sorter: Optional[Callable[[Client], Any]] = None
        self._reverse_sort: bool = False

    def add_filter(self, filter_obj: ClientFilter) -> None:
        """Добавляет фильтр."""
        self._filters.add_filter(filter_obj)

    def set_sorter(
        self, sorter: Callable[[Client], Any], reverse: bool = False
    ) -> None:
        """Устанавливает функцию сортировки и направление."""
        self._sorter = sorter
        self._reverse_sort = reverse

    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        """Возвращает список k клиентов со страницы n с фильтрацией и сортировкой."""
        # Загружаем всех клиентов из БД
        total_count = self._db_repo.get_count()
        all_clients: List[Client] = self._db_repo.get_k_n_short_list(total_count, 1)

        # Применяем фильтры
        filtered_clients = [c for c in all_clients if self._filters.apply(c)]

        # Применяем сортировку, если установлена
        if self._sorter:
            filtered_clients.sort(key=self._sorter, reverse=self._reverse_sort)

        # Применяем пагинацию
        start_index = (n - 1) * k
        if start_index >= len(filtered_clients):
            return []

        end_index = start_index + k
        return filtered_clients[start_index:end_index]

    def get_count(self) -> int:
        """Возвращает количество клиентов, прошедших фильтрацию."""
        total_count = self._db_repo.get_count()
        all_clients: List[Client] = self._db_repo.get_k_n_short_list(total_count, 1)

        filtered_clients = [c for c in all_clients if self._filters.apply(c)]
        return len(filtered_clients)

    def read_all(self) -> List[Client]:
        """Возвращает всех клиентов с применением фильтров и сортировки."""
        total_count = self._db_repo.get_count()
        all_clients: List[Client] = self._db_repo.get_k_n_short_list(total_count, 1)

        # Применяем фильтры
        filtered_clients = [c for c in all_clients if self._filters.apply(c)]

        # Применяем сортировку, если установлена
        if self._sorter:
            filtered_clients.sort(key=self._sorter, reverse=self._reverse_sort)

        return filtered_clients


class ClientRepFileDecorator:
    """Декоратор для ClientRepository с встроенной фильтрацией и сортировкой."""

    def __init__(self, file_repo: ClientRepository):
        self._file_repo = file_repo
        self._filters: CompositeFilter = CompositeFilter()
        self._sorter: Optional[Callable[[Client], Any]] = None
        self._reverse_sort: bool = False

    def add_filter(self, filter_obj: ClientFilter) -> None:
        """Добавляет фильтр."""
        self._filters.add_filter(filter_obj)

    def set_sorter(
        self, sorter: Callable[[Client], Any], reverse: bool = False
    ) -> None:
        """Устанавливает функцию сортировки и направление."""
        self._sorter = sorter
        self._reverse_sort = reverse

    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        """Возвращает список k клиентов со страницы n с фильтрацией и сортировкой."""
        # Загружаем всех клиентов из файлового репозитория
        all_clients: List[Client] = self._file_repo.read_all()

        # Применяем фильтры
        filtered_clients = [c for c in all_clients if self._filters.apply(c)]

        # Применяем сортировку, если установлена
        if self._sorter:
            filtered_clients.sort(key=self._sorter, reverse=self._reverse_sort)

        # Применяем пагинацию
        start_index = (n - 1) * k
        if start_index >= len(filtered_clients):
            return []

        end_index = start_index + k
        page_clients = filtered_clients[start_index:end_index]

        # Конвертируем в ClientShort
        return [
            ClientShort(c.id, c.surname, c.name, c.patronymic, c.phone)
            for c in page_clients
        ]

    def get_count(self) -> int:
        """Возвращает количество клиентов, прошедших фильтрацию."""
        all_clients: List[Client] = self._file_repo.read_all()
        filtered_clients = [c for c in all_clients if self._filters.apply(c)]
        return len(filtered_clients)

    def read_all(self) -> List[Client]:
        """Возвращает всех клиентов с применением фильтров и сортировки."""
        all_clients: List[Client] = self._file_repo.read_all()

        # Применяем фильтры
        filtered_clients = [c for c in all_clients if self._filters.apply(c)]

        # Применяем сортировку, если установлена
        if self._sorter:
            filtered_clients.sort(key=self._sorter, reverse=self._reverse_sort)

        return filtered_clients
