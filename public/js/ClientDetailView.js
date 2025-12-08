class ClientDetailView {
    constructor(overlayElement, contentElement, closeButton, openTabButton, titleElement) {
        this.overlayElement = overlayElement;
        this.contentElement = contentElement;
        this.closeButton = closeButton;
        this.openTabButton = openTabButton;
        this.titleElement = titleElement;
        this.currentId = null;


        this.closeButton.addEventListener("click", () => this.hide());
        this.overlayElement.addEventListener("click", (event) => {
            if (event.target === this.overlayElement) {
                this.hide();
            }
        });
        this.openTabButton.addEventListener("click", () => {
            if (this.currentId) {
                window.open(`detail.html?id=${this.currentId}`, "_blank");
            }
        });
    }

    showLoading(id) {
        this.currentId = id;
        this.titleElement.textContent = "Загружаем данные клиента…";
        this.contentElement.innerHTML = `<p class="muted">Получаем данные для клиента ID ${id}</p>`;
        this.overlayElement.classList.remove("hidden");
    }

    show(client) {
        this.currentId = client.id;
        this.titleElement.textContent = `${client.surname} ${client.name}`;
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
        this.overlayElement.classList.remove("hidden");
    }

    hide() {
        this.overlayElement.classList.add("hidden");
    }

    _detailBlock(label, value) {
        return `
            <div class="detail__item">
                <p class="detail__label">${label}</p>
                <p class="detail__value">${value}</p>
            </div>
        `;
    }
}