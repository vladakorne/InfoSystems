from ClientShortInfo import ClientShort
from ClientBase import Client
import os


def main():
    print("=== Тестирование ClientShort (родительский класс) ===")

    cs1 = ClientShort("Иванов", "Иван", "", "+79998887766")
    print("Базовый клиент (ClientShort):", cs1)
    print("Базовый клиент (__repr__):", repr(cs1))

    cs2 = ClientShort("Петров, Петр,, +79995554433", from_string=True)
    print("Из строки (ClientShort):", cs2)

    cs3 = ClientShort({
        "surname": "Сидоров",
        "name": "Алексей",
        "patronymic": "Петрович",
        "phone": "+79994443322"
    }, from_dict=True)
    print("Из словаря (ClientShort):", cs3)

    print("\n=== Тестирование Client (наследник) ===")


    c1 = Client("Иванов", "Иван", "",
                "+79998887766", "1234567890",
                "ivan@mail.ru", "VIP клиент")
    print("Полный клиент:", c1)
    print("Полный клиент (__repr__):", repr(c1))

    c2 = Client("Петров, Петр,, +79995554433, 1234567890, test@mail.ru, Постоянный клиент",
                from_string=True)
    print("Из строки:", c2)

    c3 = Client({
        "surname": "Иванов",
        "name": "Иван",
        "patronymic": "Сергеевич",
        "phone": "+79998887766",
        "passport": "1234567890",
        "email": "ivan@mail.ru",
        "comment": "VIP клиент"
    }, from_dict=True)
    print("Из словаря:", c3)

    json_str = '{"surname": "Орлов", "name": "Алексей", "patronymic": "Сергеевич", "phone": "+79996665544", "passport": "0987654321"}'
    c4 = Client(json_str, from_json=True)
    print("Из JSON-строки:", c4)


    c5 = Client(cs1, from_client_short=True, passport="1111222233", email="test@mail.ru", comment="Новый клиент")
    print("Client из ClientShort:", c5)


    json_path = "/Users/vlados/PycharmProjects/Hotel/clients.json"
    if os.path.exists(json_path):
        clients_from_json = Client.read_clients_from_json(json_path)
        for idx, client in enumerate(clients_from_json, 1):
            print(f"Из JSON-файла {idx}:", client)

    txt_path = "/Users/vlados/PycharmProjects/Hotel/clients.txt"
    if os.path.exists(txt_path):
        clients_from_txt = Client.read_clients_from_txt(txt_path)
        for idx, client in enumerate(clients_from_txt, 1):
            print(f"Из TXT-файла {idx}:", client)

    print("\n=== Тестирование создания краткая версия ===")

    s1 = ClientShort(c1.surname, c1.name, c1.patronymic, c1.phone)
    print("ClientShort из Client:", s1)


    s2 = ClientShort(c2.surname, c2.name, c2.patronymic, c2.phone)
    print("ClientShort из Client:", s2)

    print("\n=== Тестирование сравнения клиентов ===")
    print("client1 == client2:", c1.equals(c2))
    print("client1 == client3:", c1.equals(c3))

if __name__ == "__main__":
    main()
