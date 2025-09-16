from ClientBase import Client

class ClientShort(Client):

    def __init__(self, surname: str, name: str, phone: str):
        super().__init__(surname, name, phone)

    @classmethod
    def from_base(cls, client_base: Client):
        return cls(client_base.surname, client_base.name, client_base.phone)

    def __str__(self):
        initials = f"{self.name[0]}." if self.name else ""
        return f"ClientShort: {self.surname} {initials}, {self.phone}"

    def __repr__(self):
        return f"ClientShort(surname='{self.surname}', name='{self.name}', phone='{self.phone}')"
