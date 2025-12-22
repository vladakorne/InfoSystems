"""
Контроллер для удаления бронирований.
Отдельный контроллер для операции удаления.
"""

from typing import Dict, Any

from BookingRepDBAdapter import BookingRepDBAdapter
from BookingRepDB import BookingRepDB


class DeleteBookingController:
    """Контроллер для управления удалением бронирования."""

    def __init__(self, repository=None):
        """Инициализация контроллера удаления."""
        self.repository = repository or BookingRepDBAdapter(BookingRepDB())

    def delete_booking(self, booking_id: int) -> Dict[str, Any]:
        """
        Удаляет бронирование по ID.

        Args:
            booking_id: ID бронирования для удаления

        Returns:
            Словарь с результатом операции
        """
        print(f"Удаление бронирования {booking_id}...")

        try:
            # Проверяем существование бронирования
            existing_booking = self.repository.get_by_id(booking_id)
            if not existing_booking:
                print(f"Бронирование {booking_id} не найден")
                return {
                    "success": False,
                    "message": f"Бронирование с ID {booking_id} не найден",
                }

            print(f"Найден бронирование для удаления: {existing_booking}")

            # Выполняем удаление
            success = self.repository.delete_booking(booking_id)

            if success:
                print(f"Бронирование {booking_id} успешно удален")
                return {
                    "success": True,
                    "message": f"Бронирование с ID {booking_id} успешно удален",
                }
            else:
                print(f"Не удалось удалить бронирование {booking_id}")
                return {
                    "success": False,
                    "message": f"Не удалось удалить бронирование с ID {booking_id}",
                }

        except Exception as e:
            print(f"Ошибка при удалении бронирования {booking_id}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Произошла ошибка при удалении: {str(e)}",
            }