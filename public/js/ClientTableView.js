class ClientTableView {
    constructor(bodyElement, statusElement, refreshButton) {
        this.bodyElement = bodyElement;
        this.statusElement = statusElement;
        this.refreshButton = refreshButton;
        this.onSelect = () => {};

        console.log('ClientTableView инициализирован');
    }


    bindSelect(handler) {
        console.log('Установлен обработчик выбора клиента');
        this.onSelect = handler;
    }

    bindRefresh(handler) {
        if (this.refreshButton) {
            this.refreshButton.addEventListener("click", () => {
                console.log('Клик по кнопке обновления');
                handler();
            });
        }
    }

    render(payload) {
        console.log('Отрисовка таблицы с данными:', payload);

        const { items = [], total = 0, page = 1, page_size: pageSize = items.length } = payload;
        this.bodyElement.innerHTML = "";

        if (items.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 6;
            cell.innerHTML = `
                <div class="no-data">
                    <div class="no-data-icon">📭</div>
                    <p>Клиенты не найдены</p>
                    <p style="font-size: 12px; margin-top: 10px;">Попробуйте добавить клиентов</p>
                </div>
            `;
            row.appendChild(cell);
            this.bodyElement.appendChild(row);
        } else {
            items.forEach((item) => {
                const row = document.createElement("tr");
                row.dataset.id = item.id;

                // Отображаем полное отчество, а не только инициалы
                const patronymic = item.patronymic || "";

                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.surname || "—"}</td>
                    <td>${item.name || "—"}</td>
                    <td>${patronymic || "—"}</td>
                    <td>${item.phone || "—"}</td>
                    <td>
                        <button class="btn-view" data-id="${item.id}">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="currentColor"/>
                            </svg>
                            Просмотр
                        </button>
                    </td>
                `;

                // Добавляем обработчик на кнопку
                const viewButton = row.querySelector('.btn-view');
                viewButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    console.log('Клик по кнопке просмотра клиента ID:', item.id);
                    this.onSelect(item.id);
                });

                this.bodyElement.appendChild(row);
            });
        }

        // Обновляем статус
        const totalText = total === 0 ? "Нет клиентов" :
                         total === 1 ? "1 клиент" :
                         `${total} клиентов`;
        const totalPages = Math.ceil(total / pageSize) || 1;
        this.statusElement.textContent = `${totalText} • Страница ${page} из ${totalPages}`;

        console.log('Таблица отрисована успешно');
    }

    showStatus(message) {
        console.log('Обновление статуса:', message);
        this.statusElement.textContent = message;
    }
}