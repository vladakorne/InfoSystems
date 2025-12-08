"""
контроллер для операций чтения над сущностью клиента.
вся прикладная логика вынесена сюда и использует репозиторий как модель.
"""

from typing import Any, Dict, Optional, List

from ClientRepDBAdapter import ClientRepDBAdapter
from ClientRepDB import ClientRepDB
from ClientBase import Client
from ClientShortInfo import ClientShort


class ClientController:
    """контроллер для операций с клиентами."""

    def __init__(self, repository: Optional[ClientRepDBAdapter] = None) -> None:
        """ инициализация контроллера. """
        self.repository: ClientRepDBAdapter = repository or ClientRepDBAdapter(ClientRepDB())

    def get_short_clients(
            self, page_size: Optional[int] = None, page: int = 1
    ) -> Dict[str, Any]:
        """ получает список клиентов с краткой информацией. """
        # гарантируем корректный номер страницы
        page = max(page, 1)

        # общее количество клиентов
        total = self.repository.get_count()

        # обработка пагинации
        if page_size is None or page_size <= 0:
            # все записи, если пагинация отключена
            data_slice = self.repository.read_all()
            page_size = total if total > 0 else 1
        else:
            # данные для конкретной страницы
            data_slice = self.repository.get_k_n_short_list(page_size, page)

        # преобразование в краткий формат
        short_list = []
        for client in data_slice:
            short_list.append({
                "id": client.id,
                "surname": client.surname,
                "name": client.name,
                "patronymic": client.patronymic,
                "phone": client.phone,
            })

        return {
            "items": short_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """получает полную информацию о клиенте по id."""
        # получение клиента из репозитория
        client = self.repository.get_by_id(client_id)

        if client:
            # преобразование в словарь с полными данными
            return {
                "id": client.id,
                "surname": client.surname,
                "name": client.name,
                "patronymic": client.patronymic,
                "phone": client.phone,
                "passport": client.passport,
                "email": client.email,
                "comment": client.comment,
            }

        return None