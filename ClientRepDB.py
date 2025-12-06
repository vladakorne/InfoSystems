"""Реализация репозитория клиентов в базе данных PostgreSQL."""

from typing import List

import psycopg2

from ClientBase import Client
from ClientShortInfo import ClientShort

DB_CONFIG = {  # константа с настройками бд
    "db_name": "clientdb",
    "host": "localhost",
    "port": 5432,
    "user": "vlados",
    "password": "4523",
}


class DatabaseConnection:
    """Подключениек базе данных PostgreSQL."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize_connection()
        return cls._instance

    def initialize_connection(self) -> None:
        """Инициализация параметров подключения и создание таблицы."""
        self._db_name = DB_CONFIG["db_name"]
        self._host = DB_CONFIG["host"]
        self._port = DB_CONFIG["port"]
        self._user = DB_CONFIG["user"]
        self._password = DB_CONFIG["password"]
        self.create_table()

    def get_connection(self):
        """Возвращает соединение с базой данных."""
        return psycopg2.connect(
            dbname=self._db_name,
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
        )

    def create_table(self) -> None:
        """Создает таблицу clients, если она не существует."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS clients (
                        id SERIAL PRIMARY KEY,
                        surname VARCHAR(100) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        patronymic VARCHAR(100),
                        phone VARCHAR(20) NOT NULL,
                        passport VARCHAR(20),
                        email VARCHAR(255),
                        comment TEXT
                    );
                    """
                )
                conn.commit()
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Выполняет SELECT-запрос и возвращает список кортежей."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()
                return []
        finally:
            conn.close()

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Выполняет INSERT-запрос с RETURNING id и возвращает новый id."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return (
                    cursor.fetchone()[0]
                    if "RETURNING" in query.upper()
                    else cursor.rowcount
                )
        finally:
            conn.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Выполняет UPDATE-запрос и возвращает количество затронутых строк."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()

    def execute_delete(self, query: str, params: tuple = None) -> int:
        """Выполняет DELETE-запрос и возвращает количество удалённых строк."""
        return self.execute_update(query, params)


class ClientRepDB:
    """Репозиторий для работы с клиентами в базе данных."""

    def __init__(self):
        self._db = DatabaseConnection()

    def get_by_id(self, client_id: int) -> Client | None:
        """Получаем клиента по ID"""
        rows = self._db.execute_query(
            """
            SELECT id, surname, name, patronymic, phone, passport, email, comment
            FROM clients WHERE id = %s
            """,
            (client_id,),
        )
        if rows:
            r = rows[0]
            return Client(
                {
                    "id": r[0],
                    "surname": r[1],
                    "name": r[2],
                    "patronymic": r[3],
                    "phone": r[4],
                    "passport": r[5],
                    "email": r[6],
                    "comment": r[7],
                },
                from_dict=True,
            )
        return None

    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        """Пагинация"""
        offset = (n - 1) * k
        rows = self._db.execute_query(
            """
            SELECT id, surname, name, patronymic, phone
            FROM clients
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (k, offset),
        )
        return [ClientShort(*r) for r in rows]

    def add_client(self, client_data: dict) -> bool:
        """Добавляет нового клиента."""

        # Проверка дубликатов
        existing_clients = self._db.execute_query(
            """
            SELECT surname, name, patronymic, phone, passport, email, comment
            FROM clients
            """
        )

        temp_tuple = (
            client_data["surname"],
            client_data["name"],
            client_data.get("patronymic"),
            client_data["phone"],
            client_data.get("passport"),
            client_data.get("email"),
            client_data.get("comment", ""),
        )

        for row in existing_clients:
            if tuple(row) == temp_tuple:
                raise ValueError("Клиент с такими данными уже существует!")

        # Добавление
        self._db.execute_insert(
            """
            INSERT INTO clients
                (surname, name, patronymic, phone, passport, email, comment)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            temp_tuple,
        )

        return True

    def update_client(self, client_id: int, client_data: dict) -> bool:
        """Обновляет клиента. Возвращает True, если обновлён."""
        # Проверка дубликатов
        existing_clients = self._db.execute_query(
            """
            SELECT surname, name, patronymic, phone, passport, email, comment
            FROM clients WHERE id != %s
            """,
            (client_id,),
        )

        temp_tuple = (
            client_data["surname"],
            client_data["name"],
            client_data.get("patronymic"),
            client_data["phone"],
            client_data.get("passport"),
            client_data.get("email"),
            client_data.get("comment", ""),
        )

        for row in existing_clients:
            if tuple(row) == temp_tuple:
                raise ValueError("Клиент с такими данными уже существует!")

        # Обновление
        rows_affected = self._db.execute_update(
            """
            UPDATE clients SET
                surname=%s,
                name=%s,
                patronymic=%s,
                phone=%s,
                passport=%s,
                email=%s,
                comment=%s
            WHERE id=%s
            """,
            temp_tuple + (client_id,),
        )

        return rows_affected > 0

    def delete_client(self, client_id: int) -> bool:
        """Удаление клиента по ID"""
        rows_affected = self._db.execute_delete(
            "DELETE FROM clients WHERE id=%s",
            (client_id,),
        )
        return rows_affected > 0

    def get_count(self) -> int:
        """Количество клиентов"""
        rows = self._db.execute_query("SELECT COUNT(*) FROM clients")
        return rows[0][0] if rows else 0
