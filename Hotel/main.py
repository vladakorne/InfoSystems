from ClientBase import Client
from ClientShortInfo import ClientShort

def test_txt():
    filepath = "/Users/vlados/Desktop/clients.txt"
    print(f"\nЧтение из TXT")
    client = Client.from_txt(filepath)
    print(client)
    print(repr(client))
    return client

def test_excel():
    filepath = "/Users/vlados/Desktop/clients.xlsx"
    print(f"\nЧтение из Excel:")
    client = Client.from_excel(filepath)
    print(client)
    print(repr(client))
    return client

def main():
    client1 = Client(
        surname="Петров",
        name="Петр",
        patronymic="Петрович",
        passport="0319005633",
        phone="+79298221931",
        email="ivanov@mail.ru",
        comment="VIP клиент"
    )

    client2 = Client(
        surname="Петров",
        name="Петр",
        patronymic="Петрович",
        passport="0319005633",
        phone="+79298221931",
        email="ivanov@mail.ru",
        comment="VIP клиент"
    )

    client3 = Client(
        surname="Иванов",
        name="Иван",
        patronymic="Иванович",
        passport="1234567890",
        phone="+79998887766",
        email="ivanov@mail.ru",
        comment="Новый клиент"
    )

    print("Проверка сравнения клиентов:")
    print("client1 = client2:", client1.equals(client2))
    print("client1 = client3:", client1.equals(client3))

    short_client = ClientShort.from_base(client1)
    print("\nКлиент (полная версия)")
    print(client1)
    print(repr(client1))

    print("\nКлиент (краткая версия)")
    print(short_client)
    print(repr(short_client))

    txt_client = test_txt()
    excel_client = test_excel()

    print("\nСравнение клиента из TXT и Excel:")
    print("txt_client == excel_client:", txt_client.equals(excel_client))

if __name__ == "__main__":
    main()
