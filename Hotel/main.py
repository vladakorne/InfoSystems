from ClientShortInfo import ClientShort
from ClientBase import Client
from ClientRepJson import Client_rep_json
from ClientRepYaml import Client_rep_yaml
import os


def main():
    print("=== Тестирование ClientShort (родительский класс) ===")

    cs1 = ClientShort(1, "Иванов", "Иван", "", "+79998887766")
    print("Базовый клиент:", cs1)
    print("Repr:", repr(cs1))

    cs2 = ClientShort("2, Петров, Петр,, +79995554433", from_string=True)
    print("Из строки:", cs2)

    cs3 = ClientShort({
        "id": 3,
        "surname": "Сидоров",
        "name": "Алексей",
        "patronymic": "Петрович",
        "phone": "+79994443322"
    }, from_dict=True)
    print("Из словаря:", cs3)

    print("\n=== Тестирование Client (наследник) ===")

    c1 = Client(1, "Иванов", "Иван", "", "+79998887766", "1234567890", "ivan@mail.ru", "VIP клиент")
    print("Полный клиент:", c1)
    print("Repr:", repr(c1))

    c2 = Client("2, Петров, Петр,, +79995554433, 1234567890, test@mail.ru, Постоянный клиент", from_string=True)
    print("Из строки:", c2)

    c3 = Client({
        "id": 3,
        "surname": "Иванов",
        "name": "Иван",
        "patronymic": "Сергеевич",
        "phone": "+79998887766",
        "passport": "1234567890",
        "email": "ivan@mail.ru",
        "comment": "VIP клиент"
    }, from_dict=True)
    print("Из словаря:", c3)

    c4 = Client(cs1, from_client_short=True, passport="1111222233", email="test@mail.ru", comment="Новый клиент")
    print("Из ClientShort:", c4)

    txt_path = "/Users/vlados/PycharmProjects/Hotel/clients.txt"
    json_path = "/Users/vlados/PycharmProjects/Hotel/clients.json"

    if os.path.exists(txt_path):
        clients_from_txt = Client.read_clients_from_txt(txt_path)
        for idx, client in enumerate(clients_from_txt, 1):
            print(f"Из TXT-файла {idx}:", client)

    if os.path.exists(json_path):
        clients_from_json = Client.read_clients_from_json(json_path)
        for idx, client in enumerate(clients_from_json, 1):
            print(f"Из JSON-файла {idx}:", client)

    print("\n=== Сравнение клиентов ===")
    print("client2 == client2:", c2.equals(c2))
    print("client1 == client3:", c1.equals(c3))

    print("\n=== ТЕСТИРОВАНИЕ РЕПОЗИТОРИЕВ ===")
    json_file = "/Users/vlados/PycharmProjects/Hotel/clients.json"
    yaml_file = "/Users/vlados/PycharmProjects/Hotel/clients.yaml"

    print("\n=== ТЕСТИРОВАНИЕ ClientRepJson ===")

    repo_json = Client_rep_json(json_file)
    print(f"Количество клиентов: {repo_json.get_count()}")

    if repo_json.get_count() > 0:
        print("\nВсе клиенты до операций")
        for client in repo_json.clients:
            print(f"ID: {client.id}, {client.surname} {client.name} {client.patronymic}")
    else:
        print("В репозитории нет клиентов")

    print("\nДобавление нового клиента")
    new_client = Client(0, "Добавленный", "клиент", "", "+79990001122",
                        "9999999999", "xxxx@mail.ru", "")
    new_id = repo_json.add_client(new_client)
    print(f"Добавлен клиент с ID: {new_id}")
    print(f"Количество клиентов после добавления: {repo_json.get_count()}")

    print("\nЗамена клиента по ID")
    try:
        updated_client = Client(0, "Замененный", "клиент", "", "+79990003344",
                                "0000000000", "xxxxa@mail.ru", "")
        if repo_json.replace_by_id(2, updated_client):
            print("Клиент с ID 2 успешно заменен")
        else:
            print("Клиент с ID 2 не найден для замены")
    except ValueError as e:
        print(f"Ошибка при замене: {e}")

    print("\nУдаление клиента по ID")
    try:
        if repo_json.delete_by_id(3):
            print("Клиент с ID 3 успешно удален")
        else:
            print("Клиент с ID 3 не найден для удаления")
        print(f"Количество клиентов после удаления: {repo_json.get_count()}")
    except ValueError as e:
        print(f"Ошибка при удалении: {e}")

    print("\nСортировка по фамилии")
    repo_json.sort_by_surname()
    print("Клиенты отсортированы по фамилии")

    print("\nПоиск клиента по ID")
    found_client = repo_json.get_by_id(1)
    if found_client:
        print(f"Найден клиент: ID: {found_client.id}, {found_client.surname} {found_client.name}")
    else:
        print("Клиент с ID 1 не найден")

    print("\nПостраничный вывод кратких записей")
    short_list = repo_json.get_k_n_short_list(3, 1)
    print(f"Краткий список (3 клиента, страница 1): получено {len(short_list)} клиентов")
    for i, s in enumerate(short_list, 1):
        print(f"  {i}. {s}")

    print("\nПолучение количества элементов")
    print(f"Общее количество клиентов: {repo_json.get_count()}")

    print("\nФинальное состояние JSON репозитория")
    for client in repo_json.clients:
        print(f"ID: {client.id}, {client.surname} {client.name} {client.patronymic}, Телефон: {client.phone}")

    print("\n===ТЕСТИРОВАНИЕ ClientRepYaml ===")

    repo_yaml = Client_rep_yaml(yaml_file)
    print("YAML репозиторий создан")
    print(f"Количество клиентов: {repo_yaml.get_count()}")

    if repo_yaml.get_count() > 0:
        print("\nВсе клиенты до операций")
        for client in repo_yaml.clients:
            print(f"ID: {client.id}, {client.surname} {client.name} {client.patronymic}")
    else:
        print("В репозитории нет клиентов")

    print("\nДобавление нового клиента")
    new_client = Client(0, "Добавленный", "клиент", "", "+79990005566",
                        "9999999999", "xxxx@mail.ru", "")
    new_id = repo_yaml.add_client(new_client)
    print(f"Добавлен клиент с ID: {new_id}")
    print(f"Количество клиентов после добавления: {repo_yaml.get_count()}")

    print("\nЗамена клиента по ID")
    try:
        updated_client = Client(0, "Замененный", "клиент", "", "+79990007788",
                                "0000000000", "xxxxa@mail.ru", "")
        if repo_yaml.replace_by_id(2, updated_client):
            print("Клиент с ID 2 успешно заменен")
        else:
            print("Клиент с ID 2 не найден для замены")
    except ValueError as e:
        print(f"Ошибка при замене: {e}")

    print("\nУдаление клиента по ID")
    try:
        if repo_yaml.delete_by_id(3):
            print("Клиент с ID 3 успешно удален")
        else:
            print("Клиент с ID 3 не найден для удаления")
        print(f"Количество клиентов после удаления: {repo_yaml.get_count()}")
    except ValueError as e:
        print(f"Ошибка при удалении: {e}")

    print("\nСортировка по фамилии")
    repo_yaml.sort_by_surname()
    print("Клиенты отсортированы по фамилии")

    print("\nПоиск клиента по ID")
    found_client = repo_yaml.get_by_id(1)
    if found_client:
        print(f"Найден клиент: ID: {found_client.id}, {found_client.surname} {found_client.name}")
    else:
        print("Клиент с ID 1 не найден")

    print("\nПостраничный вывод кратких записей")
    short_list = repo_yaml.get_k_n_short_list(2, 1)
    print(f"Краткий список (2 клиента, страница 1): получено {len(short_list)} клиентов")
    for i, s in enumerate(short_list, 1):
        print(f"  {i}. {s}")

    print("\nПолучение количества элементов")
    print(f"Общее количество клиентов: {repo_yaml.get_count()}")

    print("\nФинальное состояние YAML репозитория")
    for client in repo_yaml.clients:
        print(f"ID: {client.id}, {client.surname} {client.name} {client.patronymic}, Телефон: {client.phone}")

if __name__ == "__main__":
    main()
