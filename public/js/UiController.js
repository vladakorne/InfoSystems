/**
 * Основной контроллер пользовательского интерфейса
 */
class UiController {
    constructor(repository, tableView, detailView, addButton = null) {
        // сохранение зависимостей в свойствах класса.
        this.repository = repository;   // модель данных ClientApiRepository
        this.tableView = tableView;     // представление таблицы ClientTableView
        this.detailView = detailView;   // ClientDetailView
        this.addButton = addButton;     // кнопка добавления

        this.refreshRequested = false;
    }

    init() {
        // запускаем все связывания и загрузку данных
        this._bindRepositoryEvents(); // вызвали приватные поля для настройки связей между компонентами
        this._bindTableViewEvents();

        if (this.addButton) { // обработка кнопки добавления
            this.addButton.addEventListener("click", () => this._openAddWindow()); // переходим на другой экран
        }
        this.refresh(); // загрузка данных
    }

    // метод управления фильтрами
    applyFilters(filters, sort, sortOrder) {
        this.repository.loadList(1, filters, sort, sortOrder);
        this.refreshRequested = true; // данные обновились => флаг true
    }

    // сброс всех фильтров
    resetFilters() {
        this.repository.resetFilters();
        this.refreshRequested = true;
    }

    _bindRepositoryEvents() {
        //связывание событий репозитория
        this.repository.subscribe("list", (data) => { // подписка
            this.tableView.render(data);
            if (this.refreshRequested) { // проверяем флаг обновления
                this.tableView.showSuccess("Данные обновлены");
                this.refreshRequested = false;
            }
        });

        this.repository.subscribe("formClosed", (data) => {
            console.log("Форма закрыта, обновляем список:", data);
            this.refresh(); // обновляем список без перезагрузки страницы
        });

        this.repository.subscribe("detail", (client) => { // обработка показа детальной инфы
            this.detailView.show(client);
        });

        this.repository.subscribe("deleted", (payload) => { // обработка удаления
            this.tableView.showSuccess(payload.message || "Клиент удален"); // сообщение из ответа или устанровленное
            this.refresh(); // обновили список
        });

        this.repository.subscribe("error", (payload) => { // показываем ошибку в статусной строке
            this.tableView.showError(payload.message);
        });

    }

    // связывание событий таблицы
    _bindTableViewEvents() {
        this.tableView.onViewClick = (clientId) => { // обработка клика "просмотр"
            this.repository.loadClientDetail(clientId); // загрузка клиента по id
        };

        this.tableView.onEditClick = (clientId) => { // обработка "редактировать"
            window.location.href = `client_form.html?id=${clientId}`;         };

        this.tableView.onDeleteClick = (clientId, clientName) => {
            if (confirm(`Вы уверены, что хотите удалить клиента "${clientName}"?`)) { // нативное окно для подтверждения
                this.repository.deleteClient(clientId); // если подверждено, то удаляем
            }
        };
    }

    // управление окнами
    _openAddWindow() {
        window.location.href = "client_form.html"; // Перенаправление на форму без параметра ID
    }

    // обновление
    refresh() {
        this.repository.loadList(1);
        this.tableView.showLoading();
        this.refreshRequested = true;
    }
}