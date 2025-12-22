"""
Контроллер для удаления номеров.
Отдельный контроллер для операции удаления.
"""

from typing import Dict, Any

from RoomRepDBAdapter import RoomRepDBAdapter
from RoomRepDB import RoomRepDB


class DeleteRoomController:
    """Контроллер для управления удалением номера."""

    def __init__(self, repository=None):
        """Инициализация контроллера удаления."""
        self.repository = repository or RoomRepDBAdapter(RoomRepDB())

    def delete_room(self, room_id: int) -> Dict[str, Any]:
        """
        Удаляет номер по ID.

        Args:
            room_id: ID номера для удаления

        Returns:
            Словарь с результатом операции
        """
        print(f"Удаление номера {room_id}...")

        try:
            # Проверяем существование номера
            existing_room = self.repository.get_by_id(room_id)
            if not existing_room:
                print(f"Номер {room_id} не найден")
                return {
                    "success": False,
                    "message": f"Номер с ID {room_id} не найден",
                }

            print(f"Найден номер для удаления: {existing_room}")

            # Выполняем удаление
            success = self.repository.delete_room(room_id)

            if success:
                print(f"Номер {room_id} успешно удален")
                return {
                    "success": True,
                    "message": f"Номер с ID {room_id} успешно удален",
                }
            else:
                print(f"Не удалось удалить номер {room_id}")
                return {
                    "success": False,
                    "message": f"Не удалось удалить номер с ID {room_id}",
                }

        except Exception as e:
            print(f"Ошибка при удалении номера {room_id}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Произошла ошибка при удалении: {str(e)}",
            }