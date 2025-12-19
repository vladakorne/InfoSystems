/**
 * Представление детальной информации о клиенте - View компонент
 */
class ClientDetailView {
    constructor(overlayElement, contentElement, closeButton, openTabButton, titleElement) { // зависимости передаются извне
        // сохраняем ссылки на dom элементы в свойствах экземпляра класса
        this.overlayElement = overlayElement; // полупрозрачный фон
        this.contentElement = contentElement; // содержимое модального окна
        this.closeButton = closeButton;
        this.openTabButton = openTabButton;
        this.titleElement = titleElement; // элемент заголовка
        this.currentId = null; // id выбранного клиента


        this.closeButton.addEventListener("click", () => this.hide()); // используется стрелочная функция для сохранения контекста this
        this.overlayElement.addEventListener("click", (event) => {
            if (event.target === this.overlayElement) { // проверка, что клик на фон
                this.hide();
            }
        }); // если кликаем на фон, то окно закрывается без сохранения

        this.openTabButton.addEventListener("click", () => { // открытие в новом окне
            if (this.currentId) {
                window.open(`detail.html?id=${this.currentId}`, "_blank"); // URL с параметром запроса открыть в новой вкладке
            }
        });
    }

    // Добавляем метод render для совместимости с др компонентами
    render(client) {
        this.show(client); // делегирует вызов основному методу show()
    }

    showLoading(id) {
        this.currentId = id;
        this.titleElement.textContent = "Загружаем данные клиента…";
        this.contentElement.innerHTML = `<p class="muted">Получаем данные для клиента ID ${id}</p>`; // установка содержимого с сообщением о загрузке (приглушенный текст)
        this.overlayElement.classList.remove("hidden"); // показ модального окна (удаляем css класса, который скрывает элемент)
    }

    // отображение данных
    show(client) {
        this.currentId = client.id;
        this.titleElement.textContent = `${client.surname} ${client.name}`; // заголовок: имя фамилия
        // генерация HTML
        this.contentElement.innerHTML = `
            ${this._detailBlock("ID", client.id)}
            ${this._detailBlock("Фамилия", client.surname)}
            ${this._detailBlock("Имя", client.name)}
            ${this._detailBlock("Отчество", client.patronymic || "—")}
            ${this._detailBlock("Телефон", client.phone)}
            ${this._detailBlock("Паспорт", client.passport || "—")}
            ${this._detailBlock("Email", client.email || "—")}
            ${this._detailBlock("Комментарий", client.comment || "—")}
        `;
        this.overlayElement.classList.remove("hidden");
    }

    showError(message) {
        this.titleElement.textContent = "Ошибка";
        this.contentElement.innerHTML = `<p class="muted">${message}</p>`;
        this.overlayElement.classList.remove("hidden"); // показываем модальное окно с ошибкой
    }

    hide() {
        this.overlayElement.classList.add("hidden"); // css класс для скрытия
    }

    // приватный метод для генерации детального обзора
    _detailBlock(label, value) { // не строгая инкапсуляция
        // возвращает название-значение поля
        return `
            <div class="detail__item">
                <p class="detail__label">${label}</p> 
                <p class="detail__value">${value}</p> 
            </div>
        `;
    }
}