"""
контроллер для операций чтения над сущностью клиента.
вся прикладная логика вынесена сюда и использует репозиторий как модель.
"""

from typing import Any, Dict, Optional, List

from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB
from ClientRepDBDecorator import (
    SurnameFilter, NameFilter, PatronymicFilter, PhoneFilter,
    ClientRepDBDecorator, ClientSorter
)
from ClientBase import Client
from ClientShortInfo import ClientShort


class ClientController:
    """контроллер для операций с клиентами."""

    def __init__(self, repository: Optional[ClientRepDBAdapter] = None) -> None:
        """инициализация контроллера."""
        self.repository: ClientRepDBAdapter = repository or ClientRepDBAdapter(
            ClientRepDB()
        )

    def _apply_filters(self, filters: Dict[str, Any], sort_by: Optional[str], sort_order: Optional[str]) -> ClientRepDBDecorator:
        """
        Оборачивает репозиторий декоратором и применяет фильтры/сортировку.
        """
        # Получаем базовый репозиторий БД из адаптера
        base_repo = self.repository._db_repo

        # Создаем декоратор
        decorated = ClientRepDBDecorator(base_repo)

        # Применяем фильтры
        if filters:
            surname_prefix = filters.get("surname_prefix")
            if surname_prefix:
                decorated.add_filter(SurnameFilter(surname_prefix))

            name_prefix = filters.get("name_prefix")
            if name_prefix:
                decorated.add_filter(NameFilter(name_prefix))

            patronymic_prefix = filters.get("patronymic_prefix")
            if patronymic_prefix:
                decorated.add_filter(PatronymicFilter(patronymic_prefix))

            phone_substring = filters.get("phone_substring")
            if phone_substring:
                decorated.add_filter(PhoneFilter(phone_substring))

        # Применяем сортировку
        if sort_by:
            sorters = {
                "surname": ClientSorter.by_surname,
                "name": ClientSorter.by_name,
                "patronymic": ClientSorter.by_patronymic,
                "phone": ClientSorter.by_phone,
                "id": ClientSorter.by_id,
            }
            sorter_factory = sorters.get(sort_by)
            if sorter_factory:
                # Определяем направление сортировки
                reverse = sort_order == "desc"
                sorter = sorter_factory(reverse)
                decorated.set_sorter(sorter, reverse)

        return decorated

    def get_short_clients(
        self,
        page_size: Optional[int] = None,
        page: int = 1,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> Dict[str, Any]:
        """получает список клиентов с краткой информацией."""
        # Гарантируем корректный номер страницы
        page = max(page, 1)
        filters = filters or {}
        sort_order = sort_order or "asc"  # По умолчанию сортировка по возрастанию

        # Выбираем репозиторий с учетом фильтров и сортировки
        need_decorator = bool(filters) or sort_by is not None
        if need_decorator:
            repo_to_use = self._apply_filters(filters, sort_by, sort_order)
            total = repo_to_use.get_count()
        else:
            repo_to_use = self.repository
            total = repo_to_use.get_count()

        # Обработка пагинации
        if page_size is None or page_size <= 0:
            # Все записи, если пагинация отключена
            data_slice = repo_to_use.read_all()
            page_size = total if total > 0 else 1
        else:
            # Данные для конкретной страницы
            if need_decorator:
                data_slice = repo_to_use.get_k_n_short_list(page_size, page)
            else:
                data_slice = repo_to_use.get_k_n_short_list(page_size, page)

        # Преобразование в краткий формат
        short_list = []
        for client in data_slice:
            short_list.append(
                {
                    "id": client.id,
                    "surname": client.surname,
                    "name": client.name,
                    "patronymic": client.patronymic,
                    "phone": client.phone,
                }
            )

        return {
            "items": short_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "filters_applied": bool(filters),
            "sort_by": sort_by,
            "sort_order": sort_order
        }

    def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """получает полную информацию о клиенте по id."""
        # Получение клиента из репозитория
        client = self.repository.get_by_id(client_id)

        if client:
            # Преобразование в словарь с полными данными
            return {
                "id": client.id,
                "surname": client.surname,
                "name": client.name,
                "patronymic": client.patronymic,
                "phone": client.phone,
                "passport": client.passport,
                "email": client.email,
                "comment": client.comment,
            }

        return None