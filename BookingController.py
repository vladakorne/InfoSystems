"""
Контроллер для операций чтения над сущностью бронирования.
Вся прикладная логика вынесена сюда и использует репозиторий как модель.
"""

from typing import Any, Dict, Optional, List
from datetime import date
from decimal import Decimal

from BookingRepDBAdapter import BookingRepDBAdapter
from BookingRepDB import BookingRepDB
from BookingRepDBDecorator import (
    ClientIdFilter,
    RoomIdFilter,
    DateRangeFilter,
    StatusFilter,
    PriceRangeFilter,
    BookingRepDBDecorator,
    BookingSorter,
)


class BookingController:
    """Контроллер для операций с бронированиями."""

    def __init__(self, repository: Optional[BookingRepDBAdapter] = None) -> None:
        self.repository: BookingRepDBAdapter = (
            repository
            or BookingRepDBAdapter(
                BookingRepDB()
            )
        )

    def apply_filters(
        self, filters: Dict[str, Any], sort_by: Optional[str], sort_order: Optional[str]
    ) -> BookingRepDBDecorator:
        base_repo = self.repository._db_repo
        decorated = BookingRepDBDecorator(base_repo)

        if filters:
            client_id = filters.get("client_id")
            if client_id is not None:
                decorated.add_filter(ClientIdFilter(int(client_id)))

            room_id = filters.get("room_id")
            if room_id is not None:
                decorated.add_filter(RoomIdFilter(int(room_id)))

            start_date = filters.get("start_date")
            end_date = filters.get("end_date")
            if start_date or end_date:
                start_date_obj = date.fromisoformat(start_date) if start_date else None
                end_date_obj = date.fromisoformat(end_date) if end_date else None
                decorated.add_filter(DateRangeFilter(start_date_obj, end_date_obj))

            status = filters.get("status")
            if status:
                decorated.add_filter(StatusFilter(status))

            min_price = filters.get("min_price")
            max_price = filters.get("max_price")
            if min_price is not None or max_price is not None:
                min_price_decimal = Decimal(str(min_price)) if min_price is not None else None
                max_price_decimal = Decimal(str(max_price)) if max_price is not None else None
                decorated.add_filter(PriceRangeFilter(min_price_decimal, max_price_decimal))

        if sort_by:
            sorters = {
                "check_in": BookingSorter.by_check_in,
                "check_out": BookingSorter.by_check_out,
                "total_sum": BookingSorter.by_total_sum,
                "created_at": BookingSorter.by_created_at,
                "client_id": BookingSorter.by_client_id,
                "room_id": BookingSorter.by_room_id,
                "id": BookingSorter.by_id,
            }
            sorter_factory = sorters.get(sort_by)
            if sorter_factory:
                reverse = sort_order == "desc"
                sorter = sorter_factory(reverse)
                decorated.set_sorter(sorter, reverse)

        return decorated

    def get_bookings_list(
        self,
        page_size: Optional[int] = None,
        page: int = 1,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Dict[str, Any]:
        page = max(page, 1)
        filters = filters or {}
        sort_order = sort_order or "asc"

        need_decorator = bool(filters) or sort_by is not None
        if need_decorator:
            repo_to_use = self.apply_filters(filters, sort_by, sort_order)
            # Получаем Booking объекты из декоратора
            bookings_objects = repo_to_use.get_all()
            total = len(bookings_objects)
        else:
            repo_to_use = self.repository
            total = repo_to_use.get_count()
            bookings_objects = []

        if page_size is None or page_size <= 0:
            if need_decorator:
                data_slice = bookings_objects
            else:
                data_slice = repo_to_use.read_all()
            page_size = total if total > 0 else 1
        else:
            if need_decorator:
                offset = (page - 1) * page_size
                data_slice = bookings_objects[offset : offset + page_size]
            else:
                data_slice = repo_to_use.get_k_n_short_list(page_size, page)

        booking_list = []
        if need_decorator:
            # Booking объекты из декоратора
            for booking in data_slice:
                booking_list.append({
                    "id": booking.id,
                    "client_id": booking.client_id,
                    "room_id": booking.room_id,
                    "check_in": booking.check_in.isoformat() if isinstance(booking.check_in, date) else booking.check_in,
                    "check_out": booking.check_out.isoformat() if isinstance(booking.check_out, date) else booking.check_out,
                    "total_sum": float(booking.total_sum),
                    "status": booking.status,
                    "notes": booking.notes,
                    "created_at": booking.created_at.isoformat() if hasattr(booking.created_at, 'isoformat') else booking.created_at,
                })
        else:
            # Словари из адаптера
            for booking in data_slice:
                booking_list.append({
                    "id": booking["id"],
                    "client_id": booking["client_id"],
                    "room_id": booking["room_id"],
                    "check_in": booking["check_in"],
                    "check_out": booking["check_out"],
                    "total_sum": float(booking["total_sum"]),
                    "status": booking["status"],
                    "notes": booking["notes"],
                    "created_at": booking["created_at"],
                })

        return {
            "items": booking_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "filters_applied": bool(filters),
            "sort_by": sort_by,
            "sort_order": sort_order,
        }

    def get_short_bookings(self, **kwargs) -> Dict[str, Any]:
        """Алиас для get_bookings_list для совместимости."""
        return self.get_bookings_list(**kwargs)

    def get_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        booking = self.repository.get_by_id(booking_id)
        return booking

    def get_client_bookings(self, client_id: int) -> List[Dict[str, Any]]:
        return self.repository.get_by_client_id(client_id)

    def get_room_bookings(self, room_id: int) -> List[Dict[str, Any]]:
        return self.repository.get_by_room_id(room_id)

    def get_active_bookings(self) -> List[Dict[str, Any]]:
        return self.repository.get_active_bookings()

    def get_bookings_for_period(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        return self.repository.get_bookings_for_period(start_date, end_date)

    def get_available_rooms_for_dates(self, check_in: str, check_out: str) -> List[int]:
        return self.repository.get_available_rooms_for_dates(check_in, check_out)

    def check_room_availability(self, room_id: int, check_in: str, check_out: str) -> bool:
        available_rooms = self.get_available_rooms_for_dates(check_in, check_out)
        return room_id in available_rooms

    def calculate_price(self, room_id: int, check_in: str, check_out: str) -> Dict[str, Any]:
        """Расчет стоимости бронирования."""
        # Получаем данные о номере
        from RoomRepDBAdapter import RoomRepDBAdapter
        from RoomRepDB import RoomRepDB
        room_repo = RoomRepDBAdapter(RoomRepDB())
        room = room_repo.get_by_id(room_id)

        if not room:
            raise ValueError("Номер не найден")

        # Рассчитываем количество ночей
        check_in_date = date.fromisoformat(check_in)
        check_out_date = date.fromisoformat(check_out)
        nights = (check_out_date - check_in_date).days

        if nights <= 0:
            raise ValueError("Некорректное количество ночей")

        price_per_night = float(room["price_per_night"])
        total_price = price_per_night * nights

        return {
            "price_per_night": price_per_night,
            "nights": nights,
            "total_price": total_price
        }

    def check_availability(self, room_id: int, check_in: str, check_out: str, exclude_id: int = None) -> bool:
        """Проверяет, доступен ли номер на указанные даты."""
        return self.check_room_availability(room_id, check_in, check_out)