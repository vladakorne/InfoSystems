"""
Адаптер для репозитория номеров.
Предоставляет единый интерфейс для работы с репозиторием.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal

from RoomRepDB import RoomRepDB
from RoomRepDBDecorator import RoomRepDBDecorator


class RoomRepDBAdapter:
    """Адаптер для работы с репозиторием номеров."""

    def __init__(self, db_repo: Optional[RoomRepDB] = None):
        """Инициализация адаптера."""
        self._db_repo = db_repo or RoomRepDB()

    def get_by_id(self, room_id: int) -> Optional[Dict[str, Any]]:
        """Получает номер по ID."""
        room = self._db_repo.get_by_id(room_id)
        if room:
            return self._room_to_dict(room)
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[Dict[str, Any]]:
        """Пагинация номеров."""
        rooms = self._db_repo.get_k_n_short_list(k, n)
        return [self._room_to_dict(room) for room in rooms]

    def read_all(self) -> List[Dict[str, Any]]:
        """Получает все номера."""
        rooms = self._db_repo.get_all()
        return [self._room_to_dict(room) for room in rooms]

    def get_count(self) -> int:
        """Количество номеров."""
        return self._db_repo.get_count()

    def add_room(self, room_data: Dict[str, Any]) -> bool:
        """Добавляет новый номер."""
        from decimal import Decimal
        room_data["price_per_night"] = Decimal(str(room_data["price_per_night"]))
        return self._db_repo.add_room(room_data)

    def update_room(self, room_id: int, room_data: Dict[str, Any]) -> bool:
        """Обновляет данные номера."""
        from decimal import Decimal
        if "price_per_night" in room_data:
            room_data["price_per_night"] = Decimal(str(room_data["price_per_night"]))
        return self._db_repo.update_room(room_id, room_data)

    def delete_room(self, room_id: int) -> bool:
        """Удаляет номер по ID."""
        return self._db_repo.delete_room(room_id)

    def search_rooms(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ищет номера по фильтрам."""
        from decimal import Decimal
        if "min_price" in filters:
            filters["min_price"] = Decimal(str(filters["min_price"]))
        if "max_price" in filters:
            filters["max_price"] = Decimal(str(filters["max_price"]))

        rooms = self._db_repo.search_rooms(filters)
        return [self._room_to_dict(room) for room in rooms]

    def get_available_rooms(self) -> List[Dict[str, Any]]:
        """Получает все доступные номера."""
        rooms = self._db_repo.get_available_rooms()
        return [self._room_to_dict(room) for room in rooms]

    def update_availability(self, room_id: int, is_available: bool) -> bool:
        """Обновляет статус доступности номера."""
        return self._db_repo.update_availability(room_id, is_available)

    def _room_to_dict(self, room) -> Dict[str, Any]:
        """Преобразует объект Room в словарь."""
        return {
            "id": room.id,
            "room_number": room.room_number,
            "capacity": room.capacity,
            "is_available": room.is_available,
            "category": room.category,
            "price_per_night": float(room.price_per_night),
            "description": room.description,
            "floor": getattr(room, 'floor', None),
            "area": getattr(room, 'area', None),
            "equipment": getattr(room, 'equipment', None),
        }