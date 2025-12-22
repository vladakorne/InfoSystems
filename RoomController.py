"""
Контроллер для операций чтения над сущностью номера.
Вся прикладная логика вынесена сюда и использует репозиторий как модель.
"""

from typing import Any, Dict, Optional, List
from decimal import Decimal

from RoomRepDBAdapter import RoomRepDBAdapter
from RoomRepDB import RoomRepDB
from RoomRepDBDecorator import (
    RoomNumberFilter,
    CategoryFilter,
    CapacityFilter,
    AvailabilityFilter,
    PriceFilter,
    RoomRepDBDecorator,
    RoomSorter,
)


class RoomController:
    """Контроллер для операций с номерами."""

    def __init__(self, repository: Optional[RoomRepDBAdapter] = None) -> None:
        """Инициализация контроллера."""
        self.repository: RoomRepDBAdapter = (
                repository
                or RoomRepDBAdapter(  # опциональный параметр для внедрения зависимости
            RoomRepDB()  # если репозиторий не передан, то создается стандартный
        )
        )

    def apply_filters(
            self, filters: Dict[str, Any], sort_by: Optional[str], sort_order: Optional[str]
    ) -> RoomRepDBDecorator:
        """Динамически добавляет функциональность (фильтры, сортировку) к объекту, не меняя его структуру."""

        base_repo = self.repository._db_repo  # получаем базовый репозиторий БД из адаптера для декорирования

        decorated = RoomRepDBDecorator(base_repo)  # создает экземпляр декоратора, оборачивающего базовый репозиторий

        # фильтры добавляются только если параметры переданы
        if filters:
            room_number_substring = filters.get("room_number_substring")
            if room_number_substring:
                decorated.add_filter(RoomNumberFilter(room_number_substring))

            category = filters.get("category")
            if category:
                decorated.add_filter(CategoryFilter(category))

            min_capacity = filters.get("min_capacity")
            max_capacity = filters.get("max_capacity")
            if min_capacity is not None or max_capacity is not None:
                decorated.add_filter(CapacityFilter(min_capacity, max_capacity))

            is_available = filters.get("is_available")
            if is_available is not None:
                decorated.add_filter(AvailabilityFilter(is_available))

            min_price = filters.get("min_price")
            max_price = filters.get("max_price")
            if min_price is not None or max_price is not None:
                # Преобразуем в Decimal
                min_price_decimal = Decimal(str(min_price)) if min_price is not None else None
                max_price_decimal = Decimal(str(max_price)) if max_price is not None else None
                decorated.add_filter(PriceFilter(min_price_decimal, max_price_decimal))

        # сортировка
        if sort_by:
            sorters = {  # словарь маппинга имени поля на фабричный метод сортировки
                "room_number": RoomSorter.by_room_number,
                "price": RoomSorter.by_price,
                "capacity": RoomSorter.by_capacity,
                "category": RoomSorter.by_category,
                "id": RoomSorter.by_id,
            }
            sorter_factory = sorters.get(sort_by)  # получаем фабрику по имени поля
            if sorter_factory:
                # определяем направление сортировки
                reverse = sort_order == "desc"  # (asc/desc)
                sorter = sorter_factory(reverse)  # каждая сортировка - отдельная стратегия
                decorated.set_sorter(sorter, reverse)  # применяем к декоратору

        return decorated  # возвращаем декорированный репозиторий

    def get_rooms_list(
            self,
            page_size: Optional[int] = None,
            page: int = 1,
            filters: Optional[Dict[str, Any]] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Получает список номеров с краткой информацией."""

        # гарантируем корректный номер страницы
        page = max(page, 1)  # страница не может быть < 1
        filters = filters or {}  # гарантируем, что filters - словарь
        sort_order = sort_order or "asc"  # по умолчанию сортировка по возрастанию

        # выбираем репозиторий с учетом фильтров и сортировки
        need_decorator = bool(filters) or sort_by is not None
        if need_decorator:
            repo_to_use = self.apply_filters(filters, sort_by, sort_order)
            # Получаем Room объекты из декоратора
            rooms_objects = repo_to_use.get_all()
            total = len(rooms_objects)
        else:
            repo_to_use = self.repository
            total = repo_to_use.get_count()
            rooms_objects = []

        # Обработка пагинации
        if page_size is None or page_size <= 0:
            if need_decorator:
                data_slice = rooms_objects
            else:
                data_slice = repo_to_use.read_all()
            page_size = total if total > 0 else 1
        else:
            if need_decorator:
                offset = (page - 1) * page_size
                data_slice = rooms_objects[offset: offset + page_size]
            else:
                data_slice = repo_to_use.get_k_n_short_list(page_size, page)

        # преобразуем в словари для JSON
        room_list = []
        if need_decorator:
            # Room объекты из декоратора
            for room in data_slice:
                room_list.append({
                    "id": room.id,
                    "room_number": room.room_number,
                    "capacity": room.capacity,
                    "is_available": room.is_available,
                    "category": room.category,
                    "price_per_night": float(room.price_per_night),
                    "description": room.description,
                })
        else:
            # Словари из адаптера
            for room in data_slice:
                room_list.append({
                    "id": room["id"],
                    "room_number": room["room_number"],
                    "capacity": room["capacity"],
                    "is_available": room["is_available"],
                    "category": room["category"],
                    "price_per_night": float(room["price_per_night"]),
                    "description": room["description"],
                })

        return {
            "items": room_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "filters_applied": bool(filters),
            "sort_by": sort_by,
            "sort_order": sort_order,
        }

    def get_short_rooms(self, **kwargs) -> Dict[str, Any]:
        """Алиас для get_rooms_list для совместимости."""
        return self.get_rooms_list(**kwargs)

    def get_room(self, room_id: int) -> Optional[Dict[str, Any]]:
        """Получает полную информацию о номере по id."""
        return self.repository.get_by_id(room_id)

    def get_available_rooms(self, check_in: str, check_out: str) -> List[Dict[str, Any]]:
        """Получает доступные номера на указанные даты."""
        # Здесь нужно реализовать логику проверки доступности через BookingController
        # Пока возвращаем все доступные номера
        filters = {"is_available": True}
        result = self.get_rooms_list(filters=filters, page_size=None, page=1)
        return result["items"]

    def update_room_availability(self, room_id: int, is_available: bool) -> Dict[str, Any]:
        """Обновляет доступность номера."""
        try:
            room = self.repository.get_by_id(room_id)
            if not room:
                return {"success": False, "message": f"Номер с ID {room_id} не найден"}

            # Обновляем номер
            success = self.repository.update_room(room_id, {"is_available": is_available})

            if success:
                return {"success": True, "message": f"Доступность номера {room_id} обновлена"}
            else:
                return {"success": False, "message": "Не удалось обновить доступность"}

        except Exception as e:
            return {"success": False, "message": f"Ошибка сервера: {str(e)}"}

    def search_rooms(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ищет номера по расширенным фильтрам."""
        return self.repository.search_rooms(filters)