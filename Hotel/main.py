from ClientShortInfo import ClientShort
from ClientBase import Client
from ClientRepJson import ClientRepJson
from ClientRepYaml import ClientRepYaml
from ClientRepDB import ClientRepDB
from ClientRepDBAdapter import ClientRepDBAdapter
import os


def main():
    # print("=== Тестирование ClientShort (родительский класс) ===")
    #
    # cs1 = ClientShort(1, "Иванов", "Иван", "", "+79998887766")
    # print("Базовый клиент:", cs1)
    # print("Repr:", repr(cs1))
    #
    # cs2 = ClientShort("2, Петров, Петр,, +79995554433", from_string=True)
    # print("Из строки:", cs2)
    #
    # cs3 = ClientShort({
    #     "id": 3,
    #     "surname": "Сидоров",
    #     "name": "Алексей",
    #     "patronymic": "Петрович",
    #     "phone": "+79994443322"
    # }, from_dict=True)
    # print("Из словаря:", cs3)
    #
    # print("\n=== Тестирование Client (наследник) ===")
    #
    # c1 = Client(1, "Иванов", "Иван", "", "+79998887766", "1234567890", "ivan@mail.ru", "VIP клиент")
    # print("Полный клиент:", c1)
    # print("Repr:", repr(c1))
    #
    # c2 = Client("2, Петров, Петр,, +79995554433, 1234567890, test@mail.ru, Постоянный клиент", from_string=True)
    # print("Из строки:", c2)
    #
    # c3 = Client({
    #     "id": 3,
    #     "surname": "Иванов",
    #     "name": "Иван",
    #     "patronymic": "Сергеевич",
    #     "phone": "+79998887766",
    #     "passport": "1234567890",
    #     "email": "ivan@mail.ru",
    #     "comment": "VIP клиент"
    # }, from_dict=True)
    # print("Из словаря:", c3)
    #
    # c4 = Client(cs1, from_client_short=True, passport="1111222233", email="test@mail.ru", comment="Новый клиент")
    # print("Из ClientShort:", c4)
    #
    # txt_path = "/Users/vlados/PycharmProjects/Hotel/clients.txt"
    # json_path = "/Users/vlados/PycharmProjects/Hotel/clients.json"
    #
    # if os.path.exists(txt_path):
    #     clients_from_txt = Client.read_clients_from_txt(txt_path)
    #     for idx, client in enumerate(clients_from_txt, 1):
    #         print(f"Из TXT-файла {idx}:", client)
    #
    # if os.path.exists(json_path):
    #     clients_from_json = Client.read_clients_from_json(json_path)
    #     for idx, client in enumerate(clients_from_json, 1):
    #         print(f"Из JSON-файла {idx}:", client)
    #
    # print("\n=== Сравнение клиентов ===")
    # print("client2 == client2:", c2.equals(c2))
    # print("client1 == client3:", c1.equals(c3))

    print("\n=== ТЕСТИРОВАНИЕ РЕПОЗИТОРИЕВ ===")
    json_file = "/Users/vlados/PycharmProjects/Hotel/clients.json"
    yaml_file = "/Users/vlados/PycharmProjects/Hotel/clients.yaml"


    # JSON репозиторий
    print("\n=== ТЕСТИРОВАНИЕ ClientRepJson ===")

    repo_json = ClientRepJson(json_file)
    print(f"Количество клиентов: {repo_json.get_count()}")

    if repo_json.get_count() > 0:
        print("\nВсе клиенты до операций")
        for client in repo_json.clients:
            print(f"ID: {client.id}, {client.surname} {client.name} {client.patronymic}")
    else:
        print("В репозитории нет клиентов")

    print("\nДобавление нового клиента")
    new_client = Client(0, "Добавленный", "Клиент", "", "+79990001122",
                        "9999999999", "xxxx@mail.ru", "")
    new_id = repo_json.add_client(new_client)
    print(f"Добавлен клиент с ID: {new_id}")
    print(f"Количество клиентов после добавления: {repo_json.get_count()}")

    print("\nЗамена клиента по ID")
    updated_client = Client(0, "Замененный", "Клиент", "", "+79990003344",
                            "0000000000", "xxxxa@mail.ru", "")
    if repo_json.replace_by_id(2, updated_client):
        print("Клиент с ID 2 успешно заменен")
    else:
        print("Клиент с ID 2 не найден для замены")

    print("\nУдаление клиента по ID")
    if repo_json.delete_by_id(3):
        print("Клиент с ID 3 успешно удален")
    else:
        print("Клиент с ID 3 не найден для удаления")
    print(f"Количество клиентов после удаления: {repo_json.get_count()}")

    print("\nСортировка по фамилии")
    repo_json.sort_by_surname()
    print("Отсортированный список клиентов (JSON):")
    for c in repo_json.clients:
        print(f"  ID: {c.id}, {c.surname} {c.name}")

    print("\nПоиск клиента по ID")
    found_client = repo_json.get_by_id(1)
    if found_client:
        print(f"Найден клиент: ID={found_client.id}, {found_client.surname} {found_client.name}")
    else:
        print("Клиент с ID 1 не найден")

    print("\nПостраничный вывод кратких записей")
    short_list = repo_json.get_k_n_short_list(3, 1)
    for i, s in enumerate(short_list, 1):
        print(f"  {i}. {s}")


    # YAML репозиторий
    print("\n=== ТЕСТИРОВАНИЕ ClientRepYaml ===")

    repo_yaml = ClientRepYaml(yaml_file)
    print(f"Количество клиентов: {repo_yaml.get_count()}")

    if repo_yaml.get_count() > 0:
        print("\nВсе клиенты до операций")
        for client in repo_yaml.clients:
            print(f"ID: {client.id}, {client.surname} {client.name}")
    else:
        print("В репозитории нет клиентов")

    print("\nДобавление нового клиента")
    new_client = Client(0, "Добавленный", "Клиент", "", "+79990005566",
                        "9999999999", "xxxx@mail.ru", "")
    new_id = repo_yaml.add_client(new_client)
    print(f"Добавлен клиент с ID: {new_id}")
    print(f"Количество клиентов после добавления: {repo_yaml.get_count()}")

    print("\nСортировка по фамилии")
    repo_yaml.sort_by_surname()
    print("Отсортированный список клиентов (YAML):")
    for c in repo_yaml.clients:
        print(f"  ID: {c.id}, {c.surname} {c.name}")


    # ТЕСТИРОВАНИЕ ClientRepDB + Adapter
    print("\n=== ТЕСТИРОВАНИЕ ClientRepDB и ClientRepDBAdapter ===")

    db_repo = ClientRepDB()
    repo_adapter = ClientRepDBAdapter(db_repo)

    clients_to_add = [
        Client(0, "Иванов", "Иван", "Иванович", "+79998887766", "1234567890", "ivan@mail.ru", "Постоянный клиент"),
        Client(0, "Петров", "Пётр", "Сергеевич", "+79991234567", "9876543210", "petr@mail.ru", "Заказывал 2 раза"),
        Client(0, "Сидорова", "Анна", "Владимировна", "+79991112233", "1122334455", "anna@mail.ru", "Новый клиент"),
        Client(0, "Кузнецов", "Алексей", "Игоревич", "+79990001122", "5566778899", "alex@mail.ru", "VIP"),
        Client(0, "Смирнова", "Мария", "Андреевна", "+79995556677", "4455667788", "maria@mail.ru", "Скидка 10%"),
        Client(0, "Егоров", "Дмитрий", "Павлович", "+79997778899", "3344556677", "dmitry@mail.ru",
               "Постоянный покупатель"),
        Client(0, "Николаева", "Ольга", "Викторовна", "+79993334455", "2233445566", "olga@mail.ru",
               "Рекомендована клиентом"),
    ]

    print("\nДобавляем клиентов в базу данных:")
    for c in clients_to_add:
        new_client = repo_adapter.add_client({
            "surname": c.surname,
            "name": c.name,
            "patronymic": c.patronymic,
            "phone": c.phone,
            "passport": c.passport,
            "email": c.email,
            "comment": c.comment,
        })
        print(f"  Добавлен: {new_client.surname} {new_client.name} (ID={new_client.id})")

    total_count = repo_adapter.get_count()
    print(f"\nВсего клиентов в БД: {total_count}")

    print("\nПостраничный вывод (5 клиентов со второй страницы):")
    for s in repo_adapter.get_k_n_short_list(5, 2):
        print(f"  - {s.surname} {s.name} ({s.phone})")

    print("\nПоиск клиента с ID=3")
    client = repo_adapter.get_by_id(3)
    if client:
        print(f"Найден: {client.surname} {client.name}, {client.phone}")
    else:
        print("Клиент не найден")

    print("\nУдаление последнего клиента")
    if repo_adapter.delete_client(total_count):
        print(f"Клиент с ID={total_count} удалён")
    else:
        print("Удаление не удалось")

    print(f"\nОставшееся количество клиентов: {repo_adapter.get_count()}")

    print("\nСортировка по фамилии (DB):")
    sorted_clients = repo_adapter.sort_by_surname()
    for c in sorted_clients:
        print(f"  - {c.surname} {c.name}")


if __name__ == "__main__":
    main()
