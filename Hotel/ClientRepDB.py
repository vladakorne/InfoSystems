import psycopg2
from typing import List
from ClientBase import Client
from ClientShortInfo import ClientShort

DB_CONFIG = {
    'db_name': 'clientdb',
    'host': 'localhost',
    'port': 5432,
    'user': 'vlados',
    'password': '4523'
}

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.initialize_connection()
        return cls._instance

    def initialize_connection(self):
        # Настройки соединения
        self._db_name = DB_CONFIG['db_name']
        self._host = DB_CONFIG['host']
        self._port = DB_CONFIG['port']
        self._user = DB_CONFIG['user']
        self._password = DB_CONFIG['password']
        # Создание таблицы при инициализации
        self.create_table()

    def get_connection(self):
        return psycopg2.connect(
            dbname=self._db_name,
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password
        )

    def create_table(self):
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
                        email VARCHAR(255),
                        comment TEXT
                    );
                """)
                conn.commit()
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """SELECT-запросы возвращают список кортежей"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
                return []
        finally:
            conn.close()

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """INSERT-запрос с RETURNING id возвращает новый id"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.fetchone()[0] if 'RETURNING' in query.upper() else cursor.rowcount
        finally:
            conn.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """UPDATE-запрос возвращает количество затронутых строк"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()

    def execute_delete(self, query: str, params: tuple = None) -> int:
        """DELETE-запрос возвращает количество удалённых строк"""
        return self.execute_update(query, params)



class ClientRepDB:
    def __init__(self):
        self._db = DatabaseConnection()

    # a
    def get_by_id(self, client_id: int) -> Client | None:
        rows = self._db.execute_query("""
            SELECT id, surname, name, patronymic, phone, passport, email, comment
            FROM clients WHERE id = %s
        """, (client_id,))
        if rows:
            r = rows[0]
            return Client({
                "id": r[0],
                "surname": r[1],
                "name": r[2],
                "patronymic": r[3],
                "phone": r[4],
                "passport": r[5],
                "email": r[6],
                "comment": r[7]
            }, from_dict=True)
        return None


    # b
    def get_k_n_short_list(self, k: int, n: int) -> List[ClientShort]:
        offset = (n - 1) * k
        rows = self._db.execute_query("""
                                      SELECT id, surname, name, patronymic, phone
                                      FROM clients
                                      ORDER BY id
                                          LIMIT %s
                                      OFFSET %s
                                      """, (k, offset))
        return [ClientShort(r[0], r[1], r[2], r[3], r[4]) for r in rows]


    # c
    def add_client(self, client_data: dict) -> Client:
        new_id = self._db.execute_insert("""
            INSERT INTO clients (surname, name, patronymic, phone, passport, email, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            client_data['surname'],
            client_data['name'],
            client_data.get('patronymic'),
            client_data['phone'],
            client_data.get('passport'),
            client_data.get('email'),
            client_data.get('comment', "")
        ))
        return Client({
            "id": new_id,
            "surname": client_data['surname'],
            "name": client_data['name'],
            "patronymic": client_data.get('patronymic'),
            "phone": client_data['phone'],
            "passport": client_data.get('passport'),
            "email": client_data.get('email'),
            "comment": client_data.get('comment', "")
        }, from_dict=True)

    # d
    def update_client(self, client_id: int, client_data: dict) -> Client | None:
        rows_affected = self._db.execute_update("""
            UPDATE clients
            SET surname=%s, name=%s, patronymic=%s, phone=%s, passport=%s, email=%s, comment=%s
            WHERE id=%s
        """, (
            client_data['surname'],
            client_data['name'],
            client_data.get('patronymic'),
            client_data['phone'],
            client_data.get('passport'),
            client_data.get('email'),
            client_data.get('comment', ""),
            client_id
        ))
        if rows_affected > 0:
            return self.get_by_id(client_id)
        return None

    # e
    def delete_client(self, client_id: int) -> bool:
        rows_affected = self._db.execute_delete("""
            DELETE FROM clients WHERE id=%s
        """, (client_id,))
        return rows_affected > 0


    # f
    def get_count(self) -> int:
        rows = self._db.execute_query("SELECT COUNT(*) FROM clients")
        return rows[0][0] if rows else 0
