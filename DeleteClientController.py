"""
Контроллер для удаления клиентов.
Отдельный контроллер для операции удаления.
"""

from typing import Dict, Any

from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB


class DeleteClientController:
    """Контроллер для управления удалением клиента."""

    def __init__(self, repository=None):
        """Инициализация контроллера удаления."""
        self.repository = repository or ClientRepDBAdapter(ClientRepDB())

    def delete_client(self, client_id: int) -> Dict[str, Any]:
        """
        Удаляет клиента по ID.

        Args:
            client_id: ID клиента для удаления

        Returns:
            Словарь с результатом операции
        """
        print(f"Удаление клиента {client_id}...")

        try:
            # Проверяем существование клиента
            existing_client = self.repository.get_by_id(client_id)
            if not existing_client:
                print(f"Клиент {client_id} не найден")
                return {
                    "success": False,
                    "message": f"Клиент с ID {client_id} не найден",
                }

            print(f"Найден клиент для удаления: {existing_client}")

            # Выполняем удаление
            success = self.repository.delete_client(client_id)

            if success:
                print(f"Клиент {client_id} успешно удален")
                return {
                    "success": True,
                    "message": f"Клиент с ID {client_id} успешно удален",
                }
            else:
                print(f"Не удалось удалить клиента {client_id}")
                return {
                    "success": False,
                    "message": f"Не удалось удалить клиента с ID {client_id}",
                }

        except Exception as e:
            print(f"Ошибка при удалении клиента {client_id}: {e}")
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "message": f"Произошла ошибка при удалении: {str(e)}",
            }
