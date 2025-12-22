"""Booking - модель бронирования номера"""

from datetime import date, datetime
from decimal import Decimal


class Booking:
    """Класс для хранения информации о бронировании."""

    def __init__(self, *args, **kwargs):
        """Инициализирует бронирование из различных источников."""
        if kwargs.get("from_string"):
            if not args:
                raise ValueError(
                    "Для from_string необходимо передать строку первым аргументом."
                )
            parts = [p.strip() for p in args[0].split(",")]
            while len(parts) < 7:
                parts.append("")
            self._init_fields(*parts[:7])

        elif kwargs.get("from_dict"):
            if not args or not isinstance(args[0], dict):
                raise ValueError(
                    "Для from_dict необходимо передать dict первым аргументом."
                )
            data = args[0]
            self._init_fields(
                data.get("id"),
                data.get("client_id"),
                data.get("room_id"),
                data.get("check_in"),
                data.get("check_out"),
                data.get("total_sum"),
                data.get("status", "confirmed"),
                data.get("notes", ""),
            )

        else:
            # Прямая инициализация параметрами
            if len(args) >= 6:
                self._init_fields(*args[:8])
            else:
                # Если переданы именованные параметры
                self._init_fields(
                    kwargs.get("id"),
                    kwargs.get("client_id"),
                    kwargs.get("room_id"),
                    kwargs.get("check_in"),
                    kwargs.get("check_out"),
                    kwargs.get("total_sum"),
                    kwargs.get("status", "confirmed"),
                    kwargs.get("notes", ""),
                )

    def _init_fields(
        self,
        id_value,
        client_id,
        room_id,
        check_in,
        check_out,
        total_sum,
        status="confirmed",
        notes="",
    ):
        """Инициализирует поля бронирования."""
        self._id = self.validate_id(id_value)
        self._client_id = self.validate_id(client_id, "ID клиента")
        self._room_id = self.validate_id(room_id, "ID номера")
        self._check_in = self.validate_date(check_in, "Дата заезда")
        self._check_out = self.validate_date(check_out, "Дата выезда")
        self._validate_dates(self._check_in, self._check_out)
        self._total_sum = self.validate_price(total_sum, "Общая сумма")
        self._status = self.validate_status(status)
        self._notes = notes if notes else ""
        self._created_at = datetime.now()

    @staticmethod
    def validate_required(value, field_name: str):
        """Проверяет что значение не пустое."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Поле '{field_name}' не может быть пустым!")
        return value

    @staticmethod
    def validate_id(id_value, field_name="ID"):
        """Валидирует ID."""
        if id_value is None:
            raise ValueError(f"{field_name} не может быть пустым!")
        try:
            id_int = int(id_value)
            if id_int < 0:
                raise ValueError(f"{field_name} не может быть отрицательным числом!")
            return id_int
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"{field_name} должен быть неотрицательным целым числом!"
            ) from exc

    @staticmethod
    def validate_date(date_value, field_name: str):
        """Валидирует дату."""
        date_value = Booking.validate_required(date_value, field_name)

        if isinstance(date_value, date):
            return date_value
        elif isinstance(date_value, datetime):
            return date_value.date()
        elif isinstance(date_value, str):
            try:
                # Пробуем разные форматы даты
                for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y.%m.%d"):
                    try:
                        return datetime.strptime(date_value.strip(), fmt).date()
                    except ValueError:
                        continue
                raise ValueError
            except ValueError as exc:
                raise ValueError(
                    f"Некорректный формат даты для '{field_name}'. "
                    f"Используйте YYYY-MM-DD, DD.MM.YYYY или DD/MM/YYYY"
                ) from exc
        else:
            raise ValueError(f"Некорректный тип данных для '{field_name}'")

    @staticmethod
    def _validate_dates(check_in: date, check_out: date):
        """Проверяет корректность дат бронирования."""
        if check_out <= check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда!")
        # Максимальная длительность бронирования - 30 дней
        if (check_out - check_in).days > 30:
            raise ValueError("Максимальная длительность бронирования - 30 дней!")

    @staticmethod
    def validate_price(price, field_name: str):
        """Валидирует сумму."""
        price = Booking.validate_required(price, field_name)
        try:
            price_decimal = Decimal(str(price))
            if price_decimal < 0:
                raise ValueError(f"{field_name} не может быть отрицательной!")
            return price_decimal
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{field_name} должна быть числом!") from exc

    @staticmethod
    def validate_status(status: str):
        """Валидирует статус бронирования."""
        status = str(status).strip().lower()
        valid_statuses = ["confirmed", "cancelled", "completed", "pending"]
        if status not in valid_statuses:
            raise ValueError(
                f"Статус должен быть одним из: {', '.join(valid_statuses)}"
            )
        return status

    # Свойства (properties)
    @property
    def id(self):
        """Возвращает ID бронирования."""
        return self._id

    @id.setter
    def id(self, value):
        """Устанавливает ID бронирования."""
        self._id = self.validate_id(value, "ID бронирования")

    @property
    def client_id(self):
        """Возвращает ID клиента."""
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        """Устанавливает ID клиента."""
        self._client_id = self.validate_id(value, "ID клиента")

    @property
    def room_id(self):
        """Возвращает ID номера."""
        return self._room_id

    @room_id.setter
    def room_id(self, value):
        """Устанавливает ID номера."""
        self._room_id = self.validate_id(value, "ID номера")

    @property
    def check_in(self):
        """Возвращает дату заезда."""
        return self._check_in

    @check_in.setter
    def check_in(self, value):
        """Устанавливает дату заезда."""
        self._check_in = self.validate_date(value, "Дата заезда")
        self._validate_dates(self._check_in, self._check_out)

    @property
    def check_out(self):
        """Возвращает дату выезда."""
        return self._check_out

    @check_out.setter
    def check_out(self, value):
        """Устанавливает дату выезда."""
        self._check_out = self.validate_date(value, "Дата выезда")
        self._validate_dates(self._check_in, self._check_out)

    @property
    def total_sum(self):
        """Возвращает общую сумму."""
        return self._total_sum

    @total_sum.setter
    def total_sum(self, value):
        """Устанавливает общую сумму."""
        self._total_sum = self.validate_price(value, "Общая сумма")

    @property
    def status(self):
        """Возвращает статус бронирования."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Устанавливает статус бронирования."""
        self._status = self.validate_status(value)

    @property
    def notes(self):
        """Возвращает заметки."""
        return self._notes

    @notes.setter
    def notes(self, value: str):
        """Устанавливает заметки."""
        self._notes = str(value) if value else ""

    @property
    def created_at(self):
        """Возвращает дату создания бронирования."""
        return self._created_at

    @property
    def nights(self) -> int:
        """Возвращает количество ночей."""
        return (self.check_out - self.check_in).days

    @property
    def price_per_night(self) -> Decimal:
        """Возвращает ценю за ночь (если количество ночей > 0)."""
        if self.nights > 0:
            return self.total_sum / self.nights
        return Decimal("0")

    def cancel(self):
        """Отменяет бронирование."""
        self.status = "cancelled"

    def complete(self):
        """Завершает бронирование."""
        self.status = "completed"

    def is_active(self) -> bool:
        """Проверяет, активно ли бронирование."""
        return self.status == "confirmed"

    def __str__(self):
        """Возвращает строковое представление бронирования."""
        status_translation = {
            "confirmed": "Подтверждено",
            "cancelled": "Отменено",
            "completed": "Завершено",
            "pending": "Ожидание",
        }
        status_text = status_translation.get(self.status, self.status)
        return (
            f"Booking [ID: {self.id}]: Клиент {self.client_id} → Номер {self.room_id} "
            f"({self.check_in} - {self.check_out}, {self.nights} ночей) - "
            f"{self.total_sum} ₽ - {status_text}"
        )

    def __repr__(self):
        """Возвращает техническое представление бронирования."""
        return (
            f"Booking(id={self.id}, client_id={self.client_id}, "
            f"room_id={self.room_id}, check_in={self.check_in}, "
            f"check_out={self.check_out}, total_sum={self.total_sum}, "
            f"status='{self.status}', notes='{self.notes}', "
            f"created_at={self.created_at})"
        )
