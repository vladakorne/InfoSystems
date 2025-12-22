"""
контроллер для операций чтения над сущностью клиента.
вся прикладная логика вынесена сюда и использует репозиторий как модель.
"""

from typing import Any, Dict, Optional

from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB
from ClientRepDBDecorator import (
    SurnameFilter,
    NameFilter,
    PatronymicFilter,
    PhoneFilter,
    ClientRepDBDecorator,
    ClientSorter,
)


class ClientController:
    """контроллер для операций с клиентами."""

    def __init__(self, repository: Optional[ClientRepDBAdapter] = None) -> None:
        """инициализация контроллера."""
        self.repository: ClientRepDBAdapter = (
            repository
            or ClientRepDBAdapter(  # опциаональный параметр для внедрения зависимости
                ClientRepDB()  # если репозиторий не передан. то создается стандтарный
            )
        )

    def apply_filters(
        self, filters: Dict[str, Any], sort_by: Optional[str], sort_order: Optional[str]
    ) -> ClientRepDBDecorator:
        """Динамически добавляет функциональность (фильтры, сортировку) к объекту, не меняя его структуру."""

        base_repo = (
            self.repository._db_repo
        )  # получаем базовый репозиторий БД из адаптера для декорирования

        decorated = ClientRepDBDecorator(
            base_repo
        )  # создает экземпляр декоратора, оборачивающего базовый репозиторий

        # фильтры добавляются только если параметры переданы
        if filters:
            surname_prefix = filters.get("surname_prefix")
            if surname_prefix:
                decorated.add_filter(SurnameFilter(surname_prefix))

            name_prefix = filters.get("name_prefix")
            if name_prefix:
                decorated.add_filter(NameFilter(name_prefix))

            patronymic_prefix = filters.get("patronymic_prefix")
            if patronymic_prefix:
                if patronymic_prefix == "yes" or patronymic_prefix == "no":
                    decorated.add_filter(PatronymicFilter(patronymic_prefix))

            phone_substring = filters.get("phone_substring")
            if phone_substring:
                decorated.add_filter(PhoneFilter(phone_substring))

        # сортировкa
        if sort_by:
            sorters = {  # словарь маппинга имени поля на фабричный метод сортировки
                "surname": ClientSorter.by_surname,
                "name": ClientSorter.by_name,
                "patronymic": ClientSorter.by_patronymic,
                "phone": ClientSorter.by_phone,
                "id": ClientSorter.by_id,
            }
            sorter_factory = sorters.get(sort_by)  # получаем фабрику по имени поля
            if sorter_factory:
                # определяем направление сортировки
                reverse = sort_order == "desc"  # (asc/desc)
                sorter = sorter_factory(
                    reverse
                )  # каждая сортировка - отдельная стратегия
                decorated.set_sorter(sorter, reverse)  # применяем к декоратору

        return decorated  # возвращаем декорированный репозиторий

    def get_short_clients(
        self,
        page_size: Optional[int] = None,
        page: int = 1,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[
        str, Any
    ]:  # метод получения списка клиентов с поддержкой: пагинации, фильтрации и сортировки
        """получает список клиентов с краткой информацией."""

        # гарантируем корректный номер страницы
        page = max(page, 1)  # страница не может быть < 1
        filters = (
            filters or {}
        )  # гарантируем, что filters - словарь (фильтры не установлены)
        sort_order = sort_order or "asc"  # по умолчанию сортировка по возрастанию

        # выбираем репозиторий с учетом фильтров и сортировки
        need_decorator = (
            bool(filters) or sort_by is not None
        )  # нужен ли декоратор (если есть фильтры или сортировка)
        if need_decorator:
            repo_to_use = self.apply_filters(
                filters, sort_by, sort_order
            )  # создаем декорированный репозиторий через apply_filters
            total = repo_to_use.get_count()
        else:
            repo_to_use = self.repository  # используем обычный репозиторий
            total = (
                repo_to_use.get_count()
            )  # получаем общее количество (уже отфильтрованных) записей

        # Обработка пагинации
        if page_size is None or page_size <= 0:
            # если page_size не задан или ≤0: возвращаем все записи
            data_slice = repo_to_use.read_all()
            page_size = total if total > 0 else 1
        else:
            data_slice = repo_to_use.get_k_n_short_list(
                page_size, page
            )  # получаем срез через get_k_n_short_list

        # преобразует объекты ClientShort в словари для JSON-сериализации
        # подготовка данных для передачи по сети
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

        # формируем ответ
        return {
            "items": short_list,  # данные клиента
            "total": total,  # кол-во после фильтрации
            "page": page,
            "page_size": page_size,  # даннные пагинации
            "filters_applied": bool(filters),
            "sort_by": sort_by,
            "sort_order": sort_order,  # инфа о сортировке
        }

    def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """получает полную информацию о клиенте по id."""

        client = self.repository.get_by_id(
            client_id
        )  # получение клиента из репозитория

        if client:  # если клиент найден, преобразует его в словарь с всеми полями
            # преобразование в словарь с полными данными
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
