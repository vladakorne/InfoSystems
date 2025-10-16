import psycopg2
from typing import List, Optional
from ClientBase import Client
from ClientShortInfo import ClientShort


class ClientRepDB:
    def __init__(self, db_name: str, host: str, port: int, user: str, password: str):
        self._db_name = db_name
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self.create_table()

    def get_connection(self):
        # Соединение с бд
        return psycopg2.connect(
            dbname=self._db_name,
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password
        )

    def create_table(self):
    # Создание таблицы clients
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id SERIAL PRIMARY KEY,
                        surname VARCHAR(100) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        patronymic VARCHAR(100),
                        phone VARCHAR(20) NOT NULL,
                        passport VARCHAR(20),
                        email VARCHAR(100),
                        comment TEXT
                    );
                """)
                conn.commit()
        finally:
            conn.close()

    # a
    def get_by_id(self, client_id: int) -> Optional[Client]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, surname, name, patronymic, phone, passport, email, comment
                    FROM clients WHERE id = %s;
                """, (client_id,))
                row = cursor.fetchone()
                if row:
                    return Client(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                return None
        finally:
            conn.close()

    # b
    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                offset = (n - 1) * k
                cursor.execute("""
                    SELECT id, surname, name, patronymic, phone
                    FROM clients
                    ORDER BY id
                    LIMIT %s OFFSET %s;
                """, (k, offset))
                rows = cursor.fetchall()
                return [ClientShort(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        finally:
            conn.close()

    # c
    def add_client(self, client: Client) -> int:
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO clients (surname, name, patronymic, phone, passport, email, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (client.surname, client.name, client.patronymic, client.phone,
                      client.passport, client.email, client.comment))
                new_id = cursor.fetchone()[0]
                conn.commit()
                return new_id
        finally:
            conn.close()

    # d
    def replace_by_id(self, client_id: int, client: Client) -> bool:
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE clients
                    SET surname=%s, name=%s, patronymic=%s, phone=%s, passport=%s, email=%s, comment=%s
                    WHERE id=%s;
                """, (client.surname, client.name, client.patronymic, client.phone,
                      client.passport, client.email, client.comment, client_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    # e
    def delete_by_id(self, client_id: int) -> bool:
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM clients WHERE id=%s;", (client_id,))
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
        finally:
            conn.close()

    # f
    def get_count(self) -> int:
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM clients;")
                return cursor.fetchone()[0]
        finally:
            conn.close()
