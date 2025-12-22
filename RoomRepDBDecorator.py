"""
Декораторы для репозитория номеров.
Позволяют динамически добавлять фильтрацию и сортировку.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from decimal import Decimal

from Room import Room
from RoomRepDB import RoomRepDB


class RoomFilter(ABC):
    """Абстрактный базовый класс для фильтров номеров."""

    @abstractmethod
    def filter(self, room: Room) -> bool:
        """Возвращает True, если комната проходит фильтр."""
        pass


class RoomNumberFilter(RoomFilter):
    """Фильтр по номеру комнаты (поиск по подстроке)."""

    def __init__(self, number_substring: str):
        self.number_substring = number_substring.lower()

    def filter(self, room: Room) -> bool:
        return self.number_substring in room.room_number.lower()


class CategoryFilter(RoomFilter):
    """Фильтр по категории номера."""

    def __init__(self, category: str):
        self.category = category

    def filter(self, room: Room) -> bool:
        return room.category == self.category


class CapacityFilter(RoomFilter):
    """Фильтр по вместимости."""

    def __init__(
        self, min_capacity: Optional[int] = None, max_capacity: Optional[int] = None
    ):
        self.min_capacity = min_capacity
        self.max_capacity = max_capacity

    def filter(self, room: Room) -> bool:
        if self.min_capacity is not None and room.capacity < self.min_capacity:
            return False
        if self.max_capacity is not None and room.capacity > self.max_capacity:
            return False
        return True


class AvailabilityFilter(RoomFilter):
    """Фильтр по доступности."""

    def __init__(self, is_available: bool):
        self.is_available = is_available

    def filter(self, room: Room) -> bool:
        return room.is_available == self.is_available


class PriceFilter(RoomFilter):
    """Фильтр по цене."""

    def __init__(
        self, min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None
    ):
        self.min_price = min_price
        self.max_price = max_price

    def filter(self, room: Room) -> bool:
        if self.min_price is not None and room.price_per_night < self.min_price:
            return False
        if self.max_price is not None and room.price_per_night > self.max_price:
            return False
        return True


class RoomSorter:
    """Фабричные методы для создания функций сортировки номеров."""

    @staticmethod
    def by_room_number(reverse: bool = False) -> Callable[[Room], any]:
        """Сортировка по номеру комнаты."""

        def sorter(room: Room) -> str:
            # Извлекаем числовую часть для правильной сортировки
            import re
            match = re.match(r"(\d+)", room.room_number)
            if match:
                return int(match.group(1)).zfill(4) + room.room_number
            return room.room_number

        return lambda rooms: sorted(rooms, key=sorter, reverse=reverse)

    @staticmethod
    def by_price(reverse: bool = False) -> Callable[[Room], any]:
        """Сортировка по цене."""

        def sorter(room: Room) -> Decimal:
            return room.price_per_night

        return lambda rooms: sorted(rooms, key=sorter, reverse=reverse)

    @staticmethod
    def by_capacity(reverse: bool = False) -> Callable[[Room], any]:
        """Сортировка по вместимости."""

        def sorter(room: Room) -> int:
            return room.capacity

        return lambda rooms: sorted(rooms, key=sorter, reverse=reverse)

    @staticmethod
    def by_category(reverse: bool = False) -> Callable[[Room], any]:
        """Сортировка по категории."""

        def sorter(room: Room) -> str:
            return room.category

        return lambda rooms: sorted(rooms, key=sorter, reverse=reverse)

    @staticmethod
    def by_id(reverse: bool = False) -> Callable[[Room], any]:
        """Сортировка по ID."""

        def sorter(room: Room) -> int:
            return room.id

        return lambda rooms: sorted(rooms, key=sorter, reverse=reverse)


class RoomRepDBDecorator:
    """Декоратор для репозитория номеров с поддержкой фильтрации и сортировки."""

    def __init__(self, base_repo: RoomRepDB):
        self._base_repo = base_repo
        self._filters: List[RoomFilter] = []
        self._sorter: Optional[Callable[[List[Room]], List[Room]]] = None

    def add_filter(self, room_filter: RoomFilter) -> None:
        """Добавляет фильтр."""
        self._filters.append(room_filter)

    def set_sorter(
        self, sorter: Callable[[List[Room]], List[Room]], reverse: bool = False
    ) -> None:
        """Устанавливает сортировщик."""
        self._sorter = sorter

    def get_by_id(self, room_id: int) -> Optional[Room]:
        """Получает номер по ID."""
        return self._base_repo.get_by_id(room_id)

    def get_all(self) -> List[Room]:
        """Получает все номера с применением фильтров и сортировки."""
        rooms = self._base_repo.get_all()

        # Применяем фильтры
        for room_filter in self._filters:
            rooms = [r for r in rooms if room_filter.filter(r)]

        # Применяем сортировку
        if self._sorter:
            rooms = self._sorter(rooms)

        return rooms

    def get_k_n_short_list(self, k: int, n: int) -> List[Room]:
        """Пагинация с применением фильтров и сортировки."""
        all_rooms = self.get_all()

        # Пагинация
        offset = (n - 1) * k
        return all_rooms[offset : offset + k]

    def read_all(self) -> List[Room]:
        """Алиас для get_all (для совместимости)."""
        return self.get_all()

    def get_count(self) -> int:
        """Получает количество отфильтрованных номеров."""
        return len(self.get_all())

    def search_rooms(self, filters: dict) -> List[Room]:
        """Поиск номеров (делегируем базовому репозиторию)."""
        return self._base_repo.search_rooms(filters)

    def get_available_rooms(self) -> List[Room]:
        """Получает доступные номера с фильтрами."""
        # Добавляем фильтр доступности, если его еще нет
        has_availability_filter = any(
            isinstance(f, AvailabilityFilter) for f in self._filters
        )

        if not has_availability_filter:
            temp_filter = AvailabilityFilter(True)
            filtered_rooms = [r for r in self.get_all() if temp_filter.filter(r)]
            return filtered_rooms

        return self.get_all()