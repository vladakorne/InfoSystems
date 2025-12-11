/**
 * Представление таблицы клиентов
 */
class ClientTableView {
    constructor(tableBody, statusElement, refreshButton) {
        this.tableBody = tableBody;
        this.statusElement = statusElement;
        this.refreshButton = refreshButton;

        this.onViewClick = null;
        this.onEditClick = null;
        this.onDeleteClick = null;
        this.onRefreshClick = null;
    }

    render(data) {
        this.tableBody.innerHTML = "";

        if (!data.items || data.items.length === 0) {
            this._renderNoData("Клиенты не найдены");
            this.statusElement.textContent = `Записей: 0`;
            return;
        }

        data.items.forEach((client) => {
            const row = this._createClientRow(client);
            this.tableBody.appendChild(row);
        });

        this.statusElement.textContent = `Показано ${data.items.length} из ${data.total} записей (страница ${data.page})`;
    }

    _createClientRow(client) {
        const row = document.createElement("tr");

        // ID
        const idCell = document.createElement("td");
        idCell.textContent = client.id;
        row.appendChild(idCell);

        // Фамилия
        const surnameCell = document.createElement("td");
        surnameCell.textContent = client.surname;
        row.appendChild(surnameCell);

        // Имя
        const nameCell = document.createElement("td");
        nameCell.textContent = client.name;
        row.appendChild(nameCell);

        // Отчество
        const patronymicCell = document.createElement("td");
        patronymicCell.textContent = client.patronymic;
        row.appendChild(patronymicCell);

        // Телефон
        const phoneCell = document.createElement("td");
        phoneCell.textContent = client.phone;
        row.appendChild(phoneCell);

        // Кнопка просмотра
        const viewCell = document.createElement("td");
        const viewButton = document.createElement("button");
        viewButton.className = "btn btn-view";
        viewButton.textContent = "Просмотр";
        viewButton.addEventListener("click", (e) => {
            e.stopPropagation();
            if (this.onViewClick) {
                this.onViewClick(client.id);
            }
        });
        viewCell.appendChild(viewButton);
        row.appendChild(viewCell);

        // Кнопка редактирования
        const editCell = document.createElement("td");
        const editButton = document.createElement("button");
        editButton.className = "btn btn-edit";
        editButton.textContent = "✏️";
        editButton.title = "Редактировать";
        editButton.addEventListener("click", (e) => {
            e.stopPropagation();
            if (this.onEditClick) {
                this.onEditClick(client.id);
            }
        });
        editCell.appendChild(editButton);

        // Кнопка удаления
        const deleteButton = document.createElement("button");
        deleteButton.className = "btn btn-delete";
        deleteButton.textContent = "🗑️";
        deleteButton.title = "Удалить";
        deleteButton.addEventListener("click", (e) => {
            e.stopPropagation();
            const clientName = `${client.surname} ${client.name} ${client.patronymic}`.trim();
            if (this.onDeleteClick) {
                this.onDeleteClick(client.id, clientName);
            }
        });
        editCell.appendChild(deleteButton);

        row.appendChild(editCell);

        return row;
    }

    _renderNoData(message) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 8;
        cell.className = "no-data";
        cell.innerHTML = `
            <div class="no-data-icon">📋</div>
            <p>${message}</p>
        `;
        row.appendChild(cell);
        this.tableBody.appendChild(row);
    }

    showLoading() {
        this._renderNoData("Загрузка данных...");
        this.statusElement.textContent = "Загрузка...";
    }

    showSuccess(message) {
        const originalText = this.statusElement.textContent;
        this.statusElement.textContent = message;

        setTimeout(() => {
            this.statusElement.textContent = originalText;
        }, 3000);
    }

    showError(message) {
        this.statusElement.textContent = `Ошибка: ${message}`;
        this.statusElement.style.color = "#e74c3c";

        setTimeout(() => {
            this.statusElement.style.color = "";
        }, 5000);
    }
}