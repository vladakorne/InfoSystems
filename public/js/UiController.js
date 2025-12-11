/**
 * Основной контроллер пользовательского интерфейса
 */
class UiController {
    constructor(repository, tableView, detailView, addButton = null) {
        this.repository = repository;
        this.tableView = tableView;
        this.detailView = detailView;
        this.addButton = addButton;
        this.addWindow = null;
        this.refreshRequested = false;
    }

    init() {
        this._bindRepositoryEvents();
        this._bindTableViewEvents();
        this._bindDetailViewEvents();

        if (this.addButton) {
            this.addButton.addEventListener("click", () => this._openAddWindow());
        }

        this.refresh();
    }

    applyFilters(filters, sort, sortOrder) {
        this.repository.loadList(1, filters, sort, sortOrder);
        this.refreshRequested = true;
    }

    resetFilters() {
        this.repository.resetFilters();
        this.refreshRequested = true;
    }

    _bindRepositoryEvents() {
        this.repository.subscribe("list", (data) => {
            this.tableView.render(data);
            if (this.refreshRequested) {
                this.tableView.showSuccess("Данные обновлены");
                this.refreshRequested = false;
            }
        });

        this.repository.subscribe("detail", (client) => {
            // ВАЖНО: вызываем show() вместо render()
            this.detailView.show(client);
        });

        this.repository.subscribe("deleted", (payload) => {
            this.tableView.showSuccess(payload.message || "Клиент удален");
            this.refresh();
        });

        this.repository.subscribe("error", (payload) => {
            this.tableView.showError(payload.message);
        });

        // Обработка изменения фильтров
        this.repository.subscribe("filtersChanged", (payload) => {
            console.log("Фильтры изменены:", payload);
        });
    }

    _bindTableViewEvents() {
        this.tableView.onViewClick = (clientId) => {
            this.repository.loadClientDetail(clientId);
        };

        this.tableView.onEditClick = (clientId) => {
            window.location.href = `client_form.html?id=${clientId}`;
        };

        this.tableView.onDeleteClick = (clientId, clientName) => {
            if (confirm(`Вы уверены, что хотите удалить клиента "${clientName}"?`)) {
                this.repository.deleteClient(clientId);
            }
        };

        this.tableView.onRefreshClick = () => {
            this.refresh();
        };
    }

    _bindDetailViewEvents() {
        this.detailView.onClose = () => {
            this.detailView.hide();
        };

        this.detailView.onOpenTab = (clientId) => {
            window.open(`detail.html?id=${clientId}`, "_blank");
        };
    }

    _openAddWindow() {
        window.location.href = "client_form.html";
    }

    refresh() {
        this.repository.loadList(1);
        this.tableView.showLoading();
        this.refreshRequested = true;
    }
}