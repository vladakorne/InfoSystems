"""
Адаптер для репозитория бронирований.
Предоставляет единый интерфейс для работы с репозиторием.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

from BookingRepDB import BookingRepDB
from BookingRepDBDecorator import BookingRepDBDecorator


class BookingRepDBAdapter:
    """Адаптер для работы с репозиторием бронирований."""

    def __init__(self, db_repo: Optional[BookingRepDB] = None):
        """Инициализация адаптера."""
        self._db_repo = db_repo or BookingRepDB()

    def get_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Получает бронирование по ID."""
        booking = self._db_repo.get_by_id(booking_id)
        if booking:
            return self._booking_to_dict(booking)
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[Dict[str, Any]]:
        """Пагинация бронирований."""
        bookings = self._db_repo.get_k_n_short_list(k, n)
        return [self._booking_to_dict(booking) for booking in bookings]

    def read_all(self) -> List[Dict[str, Any]]:
        """Получает все бронирования."""
        bookings = self._db_repo.get_all()
        return [self._booking_to_dict(booking) for booking in bookings]

    def get_count(self) -> int:
        """Количество бронирований."""
        return self._db_repo.get_count()

    def add_booking(self, booking_data: Dict[str, Any]) -> bool:
        """Добавляет новое бронирование."""
        from decimal import Decimal
        booking_data["total_sum"] = Decimal(str(booking_data["total_sum"]))
        return self._db_repo.add_booking(booking_data)

    def update_booking(self, booking_id: int, booking_data: Dict[str, Any]) -> bool:
        """Обновляет данные бронирования."""
        from decimal import Decimal
        if "total_sum" in booking_data:
            booking_data["total_sum"] = Decimal(str(booking_data["total_sum"]))
        return self._db_repo.update_booking(booking_id, booking_data)

    def delete_booking(self, booking_id: int) -> bool:
        """Удаляет бронирование по ID."""
        return self._db_repo.delete_booking(booking_id)

    def get_by_client_id(self, client_id: int) -> List[Dict[str, Any]]:
        """Получает все бронирования клиента."""
        bookings = self._db_repo.get_by_client_id(client_id)
        return [self._booking_to_dict(booking) for booking in bookings]

    def get_by_room_id(self, room_id: int) -> List[Dict[str, Any]]:
        """Получает все бронирования номера."""
        bookings = self._db_repo.get_by_room_id(room_id)
        return [self._booking_to_dict(booking) for booking in bookings]

    def get_active_bookings(self) -> List[Dict[str, Any]]:
        """Получает активные бронирования."""
        bookings = self._db_repo.get_active_bookings()
        return [self._booking_to_dict(booking) for booking in bookings]

    def cancel_booking(self, booking_id: int) -> bool:
        """Отменяет бронирование."""
        return self._db_repo.cancel_booking(booking_id)

    def get_bookings_for_period(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Получает бронирования за указанный период."""
        bookings = self._db_repo.get_bookings_for_period(start_date, end_date)
        return [self._booking_to_dict(booking) for booking in bookings]

    def get_available_rooms_for_dates(self, check_in: str, check_out: str) -> List[int]:
        """Получает список ID доступных номеров на указанные даты."""
        return self._db_repo.get_available_rooms_for_dates(check_in, check_out)

    def _booking_to_dict(self, booking) -> Dict[str, Any]:
        """Преобразует объект Booking в словарь."""
        return {
            "id": booking.id,
            "client_id": booking.client_id,
            "room_id": booking.room_id,
            "check_in": booking.check_in.isoformat() if isinstance(booking.check_in, date) else booking.check_in,
            "check_out": booking.check_out.isoformat() if isinstance(booking.check_out, date) else booking.check_out,
            "total_sum": float(booking.total_sum),
            "status": booking.status,
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat() if isinstance(booking.created_at, datetime) else booking.created_at,
            "nights": booking.nights if hasattr(booking, 'nights') else 0,
            "price_per_night": float(booking.price_per_night) if hasattr(booking, 'price_per_night') else 0.0,
        }