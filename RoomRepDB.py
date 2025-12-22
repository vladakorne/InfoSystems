"""Реализация репозитория номеров в базе данных PostgreSQL."""

from typing import List, Optional, Dict, Any

from ClientRepDB import DatabaseConnection
from Room import Room


class RoomRepDB:
    """Репозиторий для работы с номерами в базе данных."""

    def __init__(self):
        self._db = DatabaseConnection()

    def get_by_id(self, room_id: int) -> Optional[Room]:
        """Получает номер по ID."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   room_number,
                   capacity,
                   is_available,
                   category,
                   price_per_night,
                   description
            FROM rooms
            WHERE id = %s
            """,
            (room_id,),
        )
        if rows:
            r = rows[0]
            return Room(
                {
                    "id": r[0],
                    "room_number": r[1],
                    "capacity": r[2],
                    "is_available": r[3],
                    "category": r[4],
                    "price_per_night": r[5],
                    "description": r[6],
                },
                from_dict=True,
            )
        return None

    def get_by_room_number(self, room_number: str) -> Optional[Room]:
        """Получает номер по номеру комнаты."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   room_number,
                   capacity,
                   is_available,
                   category,
                   price_per_night,
                   description
            FROM rooms
            WHERE room_number = %s
            """,
            (room_number,),
        )
        if rows:
            r = rows[0]
            return Room(
                {
                    "id": r[0],
                    "room_number": r[1],
                    "capacity": r[2],
                    "is_available": r[3],
                    "category": r[4],
                    "price_per_night": r[5],
                    "description": r[6],
                },
                from_dict=True,
            )
        return None

    def get_all(self) -> List[Room]:
        """Получает все номера."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   room_number,
                   capacity,
                   is_available,
                   category,
                   price_per_night,
                   description
            FROM rooms
            ORDER BY room_number
            """
        )
        return [
            Room(
                {
                    "id": r[0],
                    "room_number": r[1],
                    "capacity": r[2],
                    "is_available": r[3],
                    "category": r[4],
                    "price_per_night": r[5],
                    "description": r[6],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_k_n_short_list(self, k: int, n: int) -> List[Room]:
        """Пагинация номеров."""
        offset = (n - 1) * k
        rows = self._db.execute_query(
            """
            SELECT id,
                   room_number,
                   capacity,
                   is_available,
                   category,
                   price_per_night,
                   description
            FROM rooms
            ORDER BY id
                LIMIT %s
            OFFSET %s
            """,
            (k, offset),
        )
        return [
            Room(
                {
                    "id": r[0],
                    "room_number": r[1],
                    "capacity": r[2],
                    "is_available": r[3],
                    "category": r[4],
                    "price_per_night": r[5],
                    "description": r[6],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_available_rooms(self) -> List[Room]:
        """Получает все доступные номера."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   room_number,
                   capacity,
                   is_available,
                   category,
                   price_per_night,
                   description
            FROM rooms
            WHERE is_available = TRUE
            ORDER BY room_number
            """
        )
        return [
            Room(
                {
                    "id": r[0],
                    "room_number": r[1],
                    "capacity": r[2],
                    "is_available": r[3],
                    "category": r[4],
                    "price_per_night": r[5],
                    "description": r[6],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def add_room(self, room_data: dict) -> bool:
        """Добавляет новый номер."""

        # Проверка дубликатов по номеру комнаты
        existing_rooms = self._db.execute_query(
            """
            SELECT room_number
            FROM rooms
            WHERE room_number = %s
            """,
            (room_data["room_number"],),
        )

        if existing_rooms:
            raise ValueError(f"Номер {room_data['room_number']} уже существует!")

        # Добавление
        self._db.execute_insert(
            """
            INSERT INTO rooms
            (room_number, capacity, is_available, category,
             price_per_night, description)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (
                room_data["room_number"],
                room_data["capacity"],
                room_data.get("is_available", True),
                room_data["category"],
                room_data["price_per_night"],
                room_data.get("description", ""),
            ),
        )

        return True

    def update_room(self, room_id: int, room_data: dict) -> bool:
        """Обновляет номер. Возвращает True, если обновлён."""

        # Проверка дубликатов по номеру комнаты (исключая текущий номер)
        existing_rooms = self._db.execute_query(
            """
            SELECT room_number
            FROM rooms
            WHERE room_number = %s
              AND id != %s
            """,
            (room_data["room_number"], room_id),
        )

        if existing_rooms:
            raise ValueError(f"Номер {room_data['room_number']} уже существует!")

        # Обновление
        rows_affected = self._db.execute_update(
            """
            UPDATE rooms
            SET room_number=%s,
                capacity=%s,
                is_available=%s,
                category=%s,
                price_per_night=%s,
                description=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                room_data["room_number"],
                room_data["capacity"],
                room_data.get("is_available", True),
                room_data["category"],
                room_data["price_per_night"],
                room_data.get("description", ""),
                room_id,
            ),
        )

        return rows_affected > 0

    def delete_room(self, room_id: int) -> bool:
        """Удаление номера по ID."""
        rows_affected = self._db.execute_delete(
            "DELETE FROM rooms WHERE id=%s",
            (room_id,),
        )
        return rows_affected > 0

    def get_count(self) -> int:
        """Количество номеров."""
        rows = self._db.execute_query("SELECT COUNT(*) FROM rooms")
        return rows[0][0] if rows else 0

    def search_rooms(self, filters: Dict[str, Any]) -> List[Room]:
        """Ищет номера по фильтрам."""

        query = """
                SELECT id, \
                       room_number, \
                       capacity, \
                       is_available,
                       category, \
                       price_per_night, \
                       description
                FROM rooms
                WHERE 1 = 1 \
                """
        params = []

        # Динамическое построение запроса
        if filters.get("room_number"):
            query += " AND room_number ILIKE %s"
            params.append(f"%{filters['room_number']}%")

        if filters.get("category"):
            query += " AND category = %s"
            params.append(filters["category"])

        if "min_capacity" in filters:
            query += " AND capacity >= %s"
            params.append(filters["min_capacity"])

        if "max_capacity" in filters:
            query += " AND capacity <= %s"
            params.append(filters["max_capacity"])

        if filters.get("is_available") is not None:
            query += " AND is_available = %s"
            params.append(filters["is_available"])

        if "min_price" in filters:
            query += " AND price_per_night >= %s"
            params.append(filters["min_price"])

        if "max_price" in filters:
            query += " AND price_per_night <= %s"
            params.append(filters["max_price"])

        query += " ORDER BY room_number"

        rows = self._db.execute_query(query, tuple(params))

        return [
            Room(
                {
                    "id": r[0],
                    "room_number": r[1],
                    "capacity": r[2],
                    "is_available": r[3],
                    "category": r[4],
                    "price_per_night": r[5],
                    "description": r[6],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def update_availability(self, room_id: int, is_available: bool) -> bool:
        """Обновляет статус доступности номера."""
        rows_affected = self._db.execute_update(
            """
            UPDATE rooms
            SET is_available = %s,
                updated_at   = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (is_available, room_id),
        )
        return rows_affected > 0

    def is_room_available_for_dates(
        self, room_id: int, check_in: str, check_out: str
    ) -> bool:
        """Проверяет, доступен ли номер на указанные даты."""
        rows = self._db.execute_query(
            """
            SELECT COUNT(*)
            FROM bookings
            WHERE room_id = %s
              AND status != 'cancelled'
              AND (
                (check_in <= %s
              AND check_out >= %s)
               OR
                (check_in <= %s
              AND check_out >= %s)
               OR
                (%s <= check_in
              AND %s >= check_out)
                )
            """,
            (room_id, check_out, check_in, check_in, check_out, check_in, check_out),
        )

        if rows and rows[0][0] > 0:
            return False

        # Также проверяем, что номер вообще доступен
        room = self.get_by_id(room_id)
        return room is not None and room.is_available
