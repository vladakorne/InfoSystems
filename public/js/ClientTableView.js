/**
 * Представление таблицы клиентов - отвечает только за отображение данных
 */
class ClientTableView {
    constructor(tableBody, statusElement) { // элемент таблицы, элемент для отображения статуса
        this.tableBody = tableBody;
        this.statusElement = statusElement;

        // инициалицъзация callback-функций (наблюдатель)
        this.onViewClick = null; // клик просмотра
        this.onEditClick = null; // клик редактирования
        // this.onDeleteClick = null;
    }

    render(data) { // очищает таблицу перед отрисовкой новых данных
        this.tableBody.innerHTML = "";  // быстрый способ очистить содержимое

        if (!data.items || data.items.length === 0) {  // проверяем массив items
            this._renderNoData("Клиенты не найдены");
            this.statusElement.textContent = `Записей: 0`;
        }

        // итерация по массиву клиентов и создание строк таблицы
        data.items.forEach((client) => {    // перебор всех элементов массива
            const row = this._createClientRow(client); // создание DOM-элемента строки
            this.tableBody.appendChild(row);   // добавление строки в таблицу
        });

        this.statusElement.textContent = `Показано ${data.items.length} из ${data.total} записей (страница ${data.page})`;  // обновление статус строки
    }

    // создание строки таблицы
    _createClientRow(client) {
        const row = document.createElement("tr");

        // ячейка ID
        const idCell = document.createElement("td"); // создали элемент ячейки
        idCell.textContent = client.id; // безопасно установили текст
        row.appendChild(idCell);    // добавили ячейку в строку

        // ячейка Фамилия
        const surnameCell = document.createElement("td");
        surnameCell.textContent = client.surname;
        row.appendChild(surnameCell);

        // ячейка Имя
        const nameCell = document.createElement("td");
        nameCell.textContent = client.name;
        row.appendChild(nameCell);

        // ячейка Отчество
        const patronymicCell = document.createElement("td");
        patronymicCell.textContent = client.patronymic;
        row.appendChild(patronymicCell);

        // ячейка Телефон
        const phoneCell = document.createElement("td");
        phoneCell.textContent = client.phone;
        row.appendChild(phoneCell);

        // Кнопка просмотра
        const viewCell = document.createElement("td");
        const viewButton = document.createElement("button");
        viewButton.className = "btn btn-view"; // установка css классов
        viewButton.textContent = "Просмотр";
        viewButton.addEventListener("click", (e) => { // обработчик клика
            e.stopPropagation(); // предотвращение всплытия события
            if (this.onViewClick) { // проверка наличия обработчика
                this.onViewClick(client.id); // вызов callback с ID клиента
            }
        });
        viewCell.appendChild(viewButton); // добавление кнопки в ячейку
        row.appendChild(viewCell); // ячейку добавили в строку

        // Кнопка редактирования
        const editCell = document.createElement("td");
        const editButton = document.createElement("button");
        editButton.className = "btn btn-edit";
        editButton.textContent = "Редактировать";
        editButton.title = "Редактировать";
        editButton.addEventListener("click", (e) => {
            e.stopPropagation();
            if (this.onEditClick) {
                this.onEditClick(client.id);
            }
        });
        editCell.appendChild(editButton);

        // Кнопка удаления
        // const deleteButton = document.createElement("button");
        // deleteButton.className = "btn btn-delete";
        // deleteButton.textContent = "Удалить";
        // deleteButton.title = "Удалить";
        // deleteButton.addEventListener("click", (e) => {
        //     e.stopPropagation();
        //     const clientName = `${client.surname} ${client.name} ${client.patronymic}`.trim();
        //     if (this.onDeleteClick) {
        //         this.onDeleteClick(client.id, clientName);
        //     }
        // });
        // editCell.appendChild(deleteButton);

        row.appendChild(editCell);
        return row; // возврат полностью собранной строки таблицы вызывающему коду
    }

    // методы разных состояний
    _renderNoData(message) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 7; // 8 если добавить удаление
        cell.className = "no-data";
        cell.innerHTML = `
            <p>${message}</p>
        `; // использование HTML
        row.appendChild(cell);
        this.tableBody.appendChild(row);
    }

    showLoading() {
        this._renderNoData("Загрузка данных...");
        this.statusElement.textContent = "Загрузка...";
    }

    showSuccess(message) { // показ временного успешного сообщения:
        const originalText = this.statusElement.textContent; // сохранение исходного текста статуса
        this.statusElement.textContent = message;

        setTimeout(() => {
            this.statusElement.textContent = originalText;
        }, 3000); // автоматическое восстановление через 3 секунды
    }

    showError(message) {  // сообщение об ошибке
        this.statusElement.textContent = `Ошибка: ${message}`;
        this.statusElement.style.color = "#e74c3c";

        setTimeout(() => {
            this.statusElement.style.color = "";
        }, 5000); // восстановление через 5 секунд
    }
}