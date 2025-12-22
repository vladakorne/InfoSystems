"""
Декораторы для репозитория бронирований.
Позволяют динамически добавлять фильтрацию и сортировку.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from datetime import date, datetime
from decimal import Decimal

from Booking import Booking
from BookingRepDB import BookingRepDB


class BookingFilter(ABC):
    """Абстрактный базовый класс для фильтров бронирований."""

    @abstractmethod
    def filter(self, booking: Booking) -> bool:
        """Возвращает True, если бронирование проходит фильтр."""
        pass


class ClientIdFilter(BookingFilter):
    """Фильтр по ID клиента."""

    def __init__(self, client_id: int):
        self.client_id = client_id

    def filter(self, booking: Booking) -> bool:
        return booking.client_id == self.client_id


class RoomIdFilter(BookingFilter):
    """Фильтр по ID номера."""

    def __init__(self, room_id: int):
        self.room_id = room_id

    def filter(self, booking: Booking) -> bool:
        return booking.room_id == self.room_id


class DateRangeFilter(BookingFilter):
    """Фильтр по диапазону дат."""

    def __init__(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        self.start_date = start_date
        self.end_date = end_date

    def filter(self, booking: Booking) -> bool:
        if self.start_date and booking.check_out < self.start_date:
            return False
        if self.end_date and booking.check_in > self.end_date:
            return False
        return True


class StatusFilter(BookingFilter):
    """Фильтр по статусу бронирования."""

    def __init__(self, status: str):
        self.status = status

    def filter(self, booking: Booking) -> bool:
        return booking.status == self.status


class PriceRangeFilter(BookingFilter):
    """Фильтр по диапазону суммы."""

    def __init__(
        self, min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None
    ):
        self.min_price = min_price
        self.max_price = max_price

    def filter(self, booking: Booking) -> bool:
        if self.min_price is not None and booking.total_sum < self.min_price:
            return False
        if self.max_price is not None and booking.total_sum > self.max_price:
            return False
        return True


class BookingSorter:
    """Фабричные методы для создания функций сортировки бронирований."""

    @staticmethod
    def by_check_in(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по дате заезда."""

        def sorter(booking: Booking) -> date:
            return booking.check_in

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)

    @staticmethod
    def by_check_out(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по дате выезда."""

        def sorter(booking: Booking) -> date:
            return booking.check_out

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)

    @staticmethod
    def by_total_sum(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по общей сумме."""

        def sorter(booking: Booking) -> Decimal:
            return booking.total_sum

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)

    @staticmethod
    def by_created_at(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по дате создания."""

        def sorter(booking: Booking) -> datetime:
            return booking.created_at

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)

    @staticmethod
    def by_client_id(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по ID клиента."""

        def sorter(booking: Booking) -> int:
            return booking.client_id

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)

    @staticmethod
    def by_room_id(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по ID номера."""

        def sorter(booking: Booking) -> int:
            return booking.room_id

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)

    @staticmethod
    def by_id(reverse: bool = False) -> Callable[[Booking], any]:
        """Сортировка по ID."""

        def sorter(booking: Booking) -> int:
            return booking.id

        return lambda bookings: sorted(bookings, key=sorter, reverse=reverse)


class BookingRepDBDecorator:
    """Декоратор для репозитория бронирований с поддержкой фильтрации и сортировки."""

    def __init__(self, base_repo: BookingRepDB):
        self._base_repo = base_repo
        self._filters: List[BookingFilter] = []
        self._sorter: Optional[Callable[[List[Booking]], List[Booking]]] = None

    def add_filter(self, booking_filter: BookingFilter) -> None:
        """Добавляет фильтр."""
        self._filters.append(booking_filter)

    def set_sorter(
        self, sorter: Callable[[List[Booking]], List[Booking]], reverse: bool = False
    ) -> None:
        """Устанавливает сортировщик."""
        self._sorter = sorter

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Получает бронирование по ID."""
        return self._base_repo.get_by_id(booking_id)

    def get_all(self) -> List[Booking]:
        """Получает все бронирования с применением фильтров и сортировки."""
        bookings = self._base_repo.get_all()

        # Применяем фильтры
        for booking_filter in self._filters:
            bookings = [b for b in bookings if booking_filter.filter(b)]

        # Применяем сортировку
        if self._sorter:
            bookings = self._sorter(bookings)

        return bookings

    def get_k_n_short_list(self, k: int, n: int) -> List[Booking]:
        """Пагинация с применением фильтров и сортировки."""
        all_bookings = self.get_all()

        # Пагинация
        offset = (n - 1) * k
        return all_bookings[offset : offset + k]

    def read_all(self) -> List[Booking]:
        """Алиас для get_all (для совместимости)."""
        return self.get_all()

    def get_count(self) -> int:
        """Получает количество отфильтрованных бронирований."""
        return len(self.get_all())

    def get_by_client_id(self, client_id: int) -> List[Booking]:
        """Получает бронирования клиента с фильтрами."""
        # Добавляем фильтр клиента, если его еще нет
        has_client_filter = any(isinstance(f, ClientIdFilter) for f in self._filters)

        if not has_client_filter:
            temp_filter = ClientIdFilter(client_id)
            filtered_bookings = [b for b in self.get_all() if temp_filter.filter(b)]
            return filtered_bookings

        return self.get_all()

    def get_by_room_id(self, room_id: int) -> List[Booking]:
        """Получает бронирования номера с фильтрами."""
        # Добавляем фильтр номера, если его еще нет
        has_room_filter = any(isinstance(f, RoomIdFilter) for f in self._filters)

        if not has_room_filter:
            temp_filter = RoomIdFilter(room_id)
            filtered_bookings = [b for b in self.get_all() if temp_filter.filter(b)]
            return filtered_bookings

        return self.get_all()

    def get_active_bookings(self) -> List[Booking]:
        """Получает активные бронирования с фильтрами."""
        # Добавляем фильтр статуса, если его еще нет
        has_status_filter = any(isinstance(f, StatusFilter) for f in self._filters)

        if not has_status_filter:
            temp_filter = StatusFilter("confirmed")
            filtered_bookings = [b for b in self.get_all() if temp_filter.filter(b)]
            return filtered_bookings

        return self.get_all()
