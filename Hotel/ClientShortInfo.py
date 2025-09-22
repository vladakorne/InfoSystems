from ClientBase import Client

class ClientShort(Client):
    def __init__(self, *args, **kwargs):
        if kwargs.get("from_client"):
            client = args[0]
            if not isinstance(client, Client):
                raise TypeError("ClientShort.from_client требует объект Client")
            super().__init__(client.surname, client.name, client.patronymic, client.phone)

        elif kwargs.get("from_string"):
            temp_client = Client(args[0], from_string=True)
            super().__init__(temp_client.surname, temp_client.name, temp_client.patronymic, temp_client.phone)
        elif kwargs.get("from_dict"):
            temp_client = Client(args[0], from_dict=True)
            super().__init__(temp_client.surname, temp_client.name, temp_client.patronymic, temp_client.phone)
        elif kwargs.get("from_json"):
            temp_client = Client(args[0], from_json=True)
            super().__init__(temp_client.surname, temp_client.name, temp_client.patronymic, temp_client.phone)
        else:
            raise ValueError("ClientShort можно создать только на основе Client или через from_string/from_dict/from_json")

    def __str__(self):
        initials = f"{self.name[0]}." if self.name else ""
        patronymic_initial = f"{self.patronymic[0]}." if self.patronymic else ""
        return f"ClientShort: {self.surname} {initials}{patronymic_initial}, {self.phone}"

    def __repr__(self):
        return f"ClientShort(surname='{self.surname}', name='{self.name}', patronymic='{self.patronymic}', phone='{self.phone}')"
