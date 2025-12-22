"""Реализация репозитория бронирований в базе данных PostgreSQL."""

from typing import List, Optional

# from datetime import date, datetime

from ClientRepDB import DatabaseConnection
from Booking import Booking


class BookingRepDB:
    """Репозиторий для работы с бронированиями в базе данных."""

    def __init__(self):
        self._db = DatabaseConnection()

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Получает бронирование по ID."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            WHERE id = %s
            """,
            (booking_id,),
        )
        if rows:
            r = rows[0]
            return Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
        return None

    def get_all(self) -> List[Booking]:
        """Получает все бронирования."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            ORDER BY created_at DESC
            """
        )
        return [
            Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_k_n_short_list(self, k: int, n: int) -> List[Booking]:
        """Пагинация бронирований."""
        offset = (n - 1) * k
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            ORDER BY created_at DESC
                LIMIT %s
            OFFSET %s
            """,
            (k, offset),
        )
        return [
            Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_by_client_id(self, client_id: int) -> List[Booking]:
        """Получает все бронирования клиента."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            WHERE client_id = %s
            ORDER BY check_in DESC
            """,
            (client_id,),
        )
        return [
            Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_by_room_id(self, room_id: int) -> List[Booking]:
        """Получает все бронирования номера."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            WHERE room_id = %s
            ORDER BY check_in DESC
            """,
            (room_id,),
        )
        return [
            Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_active_bookings(self) -> List[Booking]:
        """Получает активные бронирования (confirmed)."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            WHERE status = 'confirmed'
            ORDER BY check_in
            """
        )
        return [
            Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def add_booking(self, booking_data: dict) -> bool:
        """Добавляет новое бронирование."""

        # Проверка доступности номера на даты
        check_availability = self._db.execute_query(
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
            (
                booking_data["room_id"],
                booking_data["check_out"],
                booking_data["check_in"],
                booking_data["check_in"],
                booking_data["check_out"],
                booking_data["check_in"],
                booking_data["check_out"],
            ),
        )

        if check_availability and check_availability[0][0] > 0:
            raise ValueError("Номер уже забронирован на указанные даты!")

        # Проверка, что клиент и номер существуют
        client_exists = self._db.execute_query(
            "SELECT COUNT(*) FROM clients WHERE id = %s",
            (booking_data["client_id"],),
        )

        if not client_exists or client_exists[0][0] == 0:
            raise ValueError(f"Клиент с ID {booking_data['client_id']} не найден!")

        room_exists = self._db.execute_query(
            "SELECT COUNT(*) FROM rooms WHERE id = %s AND is_available = TRUE",
            (booking_data["room_id"],),
        )

        if not room_exists or room_exists[0][0] == 0:
            raise ValueError(
                f"Номер с ID {booking_data['room_id']} не найден или недоступен!"
            )

        # Добавление
        self._db.execute_insert(
            """
            INSERT INTO bookings
            (client_id, room_id, check_in, check_out,
             total_sum, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (
                booking_data["client_id"],
                booking_data["room_id"],
                booking_data["check_in"],
                booking_data["check_out"],
                booking_data["total_sum"],
                booking_data.get("status", "confirmed"),
                booking_data.get("notes", ""),
            ),
        )

        return True

    def update_booking(self, booking_id: int, booking_data: dict) -> bool:
        """Обновляет бронирование. Возвращает True, если обновлён."""

        # При обновлении дат проверяем доступность (исключая текущее бронирование)
        if "check_in" in booking_data or "check_out" in booking_data:
            check_availability = self._db.execute_query(
                """
                SELECT COUNT(*)
                FROM bookings
                WHERE room_id = %s
                  AND id != %s
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
                (
                    booking_data.get("room_id", self.get_by_id(booking_id).room_id),
                    booking_id,
                    booking_data.get("check_out", self.get_by_id(booking_id).check_out),
                    booking_data.get("check_in", self.get_by_id(booking_id).check_in),
                    booking_data.get("check_in", self.get_by_id(booking_id).check_in),
                    booking_data.get("check_out", self.get_by_id(booking_id).check_out),
                    booking_data.get("check_in", self.get_by_id(booking_id).check_in),
                    booking_data.get("check_out", self.get_by_id(booking_id).check_out),
                ),
            )

            if check_availability and check_availability[0][0] > 0:
                raise ValueError("Номер уже забронирован на указанные даты!")

        # Обновление
        update_fields = []
        params = []

        if "client_id" in booking_data:
            update_fields.append("client_id=%s")
            params.append(booking_data["client_id"])

        if "room_id" in booking_data:
            update_fields.append("room_id=%s")
            params.append(booking_data["room_id"])

        if "check_in" in booking_data:
            update_fields.append("check_in=%s")
            params.append(booking_data["check_in"])

        if "check_out" in booking_data:
            update_fields.append("check_out=%s")
            params.append(booking_data["check_out"])

        if "total_sum" in booking_data:
            update_fields.append("total_sum=%s")
            params.append(booking_data["total_sum"])

        if "status" in booking_data:
            update_fields.append("status=%s")
            params.append(booking_data["status"])

        if "notes" in booking_data:
            update_fields.append("notes=%s")
            params.append(booking_data.get("notes", ""))

        # Добавляем updated_at и ID
        update_fields.append("updated_at=CURRENT_TIMESTAMP")
        params.append(booking_id)

        if not update_fields:
            return False

        query = f"""
        UPDATE bookings SET
            {', '.join(update_fields)}
        WHERE id=%s
        """

        rows_affected = self._db.execute_update(query, tuple(params))
        return rows_affected > 0

    def delete_booking(self, booking_id: int) -> bool:
        """Удаление бронирования по ID."""
        rows_affected = self._db.execute_delete(
            "DELETE FROM bookings WHERE id=%s",
            (booking_id,),
        )
        return rows_affected > 0

    def get_count(self) -> int:
        """Количество бронирований."""
        rows = self._db.execute_query("SELECT COUNT(*) FROM bookings")
        return rows[0][0] if rows else 0

    def cancel_booking(self, booking_id: int) -> bool:
        """Отменяет бронирование (меняет статус на cancelled)."""
        rows_affected = self._db.execute_update(
            """
            UPDATE bookings
            SET status     = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND status = 'confirmed'
            """,
            (booking_id,),
        )
        return rows_affected > 0

    def get_bookings_for_period(self, start_date: str, end_date: str) -> List[Booking]:
        """Получает бронирования за указанный период."""
        rows = self._db.execute_query(
            """
            SELECT id,
                   client_id,
                   room_id,
                   check_in,
                   check_out,
                   total_sum,
                   status,
                   notes,
                   created_at
            FROM bookings
            WHERE (
                      (check_in BETWEEN %s AND %s) OR
                      (check_out BETWEEN %s AND %s) OR
                      (check_in <= %s AND check_out >= %s)
                      )
            ORDER BY check_in
            """,
            (start_date, end_date, start_date, end_date, start_date, end_date),
        )
        return [
            Booking(
                {
                    "id": r[0],
                    "client_id": r[1],
                    "room_id": r[2],
                    "check_in": r[3],
                    "check_out": r[4],
                    "total_sum": r[5],
                    "status": r[6],
                    "notes": r[7],
                },
                from_dict=True,
            )
            for r in rows
        ]

    def get_available_rooms_for_dates(self, check_in: str, check_out: str) -> List[int]:
        """Получает список ID доступных номеров на указанные даты."""
        rows = self._db.execute_query(
            """
            SELECT r.id
            FROM rooms r
            WHERE r.is_available = TRUE
              AND r.id NOT IN (SELECT b.room_id
                               FROM bookings b
                               WHERE b.status
                != 'cancelled'
              AND (
                (b.check_in <= %s
              AND b.check_out >= %s)
               OR
                (b.check_in <= %s
              AND b.check_out >= %s)
               OR
                (%s <= b.check_in
              AND %s >= b.check_out)
                )
                )
            ORDER BY r.room_number
            """,
            (check_out, check_in, check_in, check_out, check_in, check_out),
        )
        return [r[0] for r in rows] if rows else []
