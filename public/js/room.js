/**
 * Репозиторий для работы с API номеров с паттерном Наблюдатель
 */
class RoomApiRepository {
    constructor(baseUrl = "/api") {
        this.baseUrl = baseUrl;
        this.subscribers = {
            list: [],        // наблюдатели за загрузкой списка номеров
            detail: [],      // наблюдатели за загрузкой детальной инфо
            deleted: [],     // наблюдатели за удалением
            error: [],       // наблюдатели за ошибками
            filtersChanged: [], // наблюдатели за изменением фильтров
            formClosed: []
        };
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';

        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;

            if (event.data.type === 'room_form_closed' && event.data.success) {
                this.notify('formClosed', event.data);
            }
        });
    }

    subscribe(event, handler) {
        if (this.subscribers[event]) {
            this.subscribers[event].push(handler);
        }
    }

    notify(event, payload) {
        (this.subscribers[event] || []).forEach((handler) => handler(payload));
    }

    async loadList(page = 1, filters = null, sort = null, sortOrder = null) {
        try {
            if (filters !== null) {
                this.currentFilters = filters;
            }
            if (sort !== null) {
                this.currentSort = sort;
            }
            if (sortOrder !== null) {
                this.currentSortOrder = sortOrder || 'asc';
            }

            const params = new URLSearchParams({ page });

            Object.entries(this.currentFilters).forEach(([key, value]) => {
                if (value !== undefined && value !== null && value !== "") {
                    params.append(key, value);
                }
            });

            if (this.currentSort) {
                params.append("sort", this.currentSort);
                params.append("sort_order", this.currentSortOrder);
            }

            const response = await fetch(`${this.baseUrl}/rooms?${params.toString()}`);

            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.error || "Не удалось загрузить список номеров");
            }
            const data = await response.json();
            this.notify("list", data);
        } catch (error) {
            this.notify("error", { message: error.message });
        }
    }

    async loadRoomDetail(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/rooms/${roomId}`);
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("Номер не найден");
                }
                throw new Error("Не удалось загрузить данные номера");
            }
            const data = await response.json();
            this.notify("detail", data);
        } catch (error) {
            this.notify("error", { message: error.message });
        }
    }

    async deleteRoom(roomId) {
        try {
            const response = await fetch(`${this.baseUrl}/rooms/${roomId}`, {
                method: "DELETE",
            });
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.error || "Не удалось удалить номер");
            }
            const data = await response.json();
            this.notify("deleted", { id: roomId, ...data });
        } catch (error) {
            this.notify("error", { message: error.message });
        }
    }

    applyFilters(filters = null, sort = null, sortOrder = null) {
        this.currentFilters = filters || {};
        this.currentSort = sort || '';
        this.currentSortOrder = sortOrder || 'asc';

        this.notify("filtersChanged", {
            filters: this.currentFilters,
            sort: this.currentSort,
            sortOrder: this.currentSortOrder
        });
        return this.loadList(1);
    }

    resetFilters() {
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';

        this.notify("filtersChanged", {
            filters: {},
            sort: '',
            sortOrder: 'asc'
        });
        return this.loadList(1);
    }
}

/**
 * Представление детальной информации о номере
 */
class RoomDetailView {
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
                window.open(`detail_room.html?id=${this.currentId}`, "_blank");
            }
        });
    }

    render(room) {
        this.show(room);
    }

    showLoading(id) {
        this.currentId = id;
        this.titleElement.textContent = "Загружаем данные номера…";
        this.contentElement.innerHTML = `<p class="muted">Получаем данные для номера ID ${id}</p>`;
        this.overlayElement.classList.remove("hidden");
    }

    show(room) {
        this.currentId = room.id;
        this.titleElement.textContent = `Номер ${room.room_number}`;

        const statusText = room.is_available ? "Доступен" : "Занят";
        const statusClass = room.is_available ? "status-available" : "status-unavailable";

        this.contentElement.innerHTML = `
            ${this._detailBlock("ID", room.id)}
            ${this._detailBlock("Номер комнаты", room.room_number)}
            ${this._detailBlock("Вместимость", `${room.capacity} чел.`)}
            ${this._detailBlock("Статус", `<span class="${statusClass}">${statusText}</span>`)}
            ${this._detailBlock("Категория", room.category)}
            ${this._detailBlock("Цена за ночь", `${room.price_per_night} ₽`)}
            ${this._detailBlock("Описание", room.description || "—")}
            ${room.floor ? this._detailBlock("Этаж", room.floor) : ''}
            ${room.area ? this._detailBlock("Площадь", `${room.area} м²`) : ''}
            ${room.equipment ? this._detailBlock("Оборудование", room.equipment) : ''}
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

/**
 * Основной контроллер формы номера
 */
class RoomFormController {
    constructor() {
        this.mode = null;
        this.roomId = null;
        this.isSubmitting = false;
        this.redirectTimer = null;

        this.elements = {
            form: null,
            submitBtn: null,
            cancelBtn: null,
            deleteBtn: null,
            successMessage: null,
            errorMessage: null,
            notFoundMessage: null,
            loading: null,
            loadingText: null
        };
    }

    init(mode, roomId = null) {
        this.mode = mode;
        this.roomId = roomId;

        this._findElements();
        this._setupEventListeners();
        this._loadInitialData().catch(error => {
            console.error('Ошибка при загрузке данных:', error);
            this._showError('Не удалось загрузить данные формы');
        });

        this._toggleDeleteButton();
    }

    _findElements() {
        this.elements = {
            form: document.getElementById('room-form'),
            submitBtn: document.getElementById('submit-btn'),
            cancelBtn: document.getElementById('cancel-btn'),
            deleteBtn: document.getElementById('delete-btn'),
            successMessage: document.getElementById('success-message'),
            errorMessage: document.getElementById('error-message'),
            notFoundMessage: document.getElementById('not-found-message'),
            loading: document.getElementById('loading'),
            loadingText: document.getElementById('loading-text')
        };
    }

    _setupEventListeners() {
        const { form, cancelBtn, deleteBtn } = this.elements;

        form.addEventListener('submit', (e) => this._handleSubmit(e));

        cancelBtn.addEventListener('click', () => {
            window.location.href = 'index.html';
        });

        deleteBtn.addEventListener('click', async () => {
            if (this.roomId) {
                try {
                    await this._handleDelete();
                } catch (error) {
                    console.error('Ошибка при удалении:', error);
                }
            }
        });

        window.addEventListener('beforeunload', () => {
            if (this.redirectTimer) {
                clearTimeout(this.redirectTimer);
            }
        });

        form.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('blur', () => this._validateField(input));
            input.addEventListener('input', () => this._clearFieldError(input));
        });
    }

    _toggleDeleteButton() {
        const { deleteBtn } = this.elements;

        if (this.mode === 'edit' && this.roomId) {
            deleteBtn.classList.remove('hidden');
        } else {
            deleteBtn.classList.add('hidden');
        }
    }

    async _handleDelete() {
        if (!this.roomId) return;

        const confirmed = confirm('Вы уверены, что хотите удалить этот номер? Это действие нельзя отменить.');

        if (!confirmed) return;

        this._resetMessages();

        try {
            const response = await fetch(`/api/rooms/${this.roomId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Номер успешно удален');

                this.redirectTimer = setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);

            } else {
                this._showError(result.message || 'Ошибка при удалении номера');
            }

        } catch (error) {
            console.error('Ошибка при удалении номера:', error);
            this._showError('Ошибка соединения с сервером');
        } finally {
            this._setLoading(false);
        }
    }

    async _loadInitialData() {
        if (this.mode === 'edit' && this.roomId) {
            await this._loadRoomData(this.roomId);
        } else {
            this._showFormReady();
        }
    }

    async _loadRoomData(roomId) {
        this._setLoading(true, 'Загрузка данных номера...');

        try {
            const response = await fetch(`/api/rooms/${roomId}/edit/form`);

            if (response.status === 404) {
                this._showNotFound();
                return;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Ошибка сервера: ${response.status}`);
            }

            const result = await response.json();

            if (result.success === false) {
                throw new Error(result.error || 'Не удалось загрузить данные');
            }

            this._populateForm(result.data || result);
            this._showFormReady();

        } catch (error) {
            console.error('Ошибка при загрузке данных номера:', error);
            this._showError(`Не удалось загрузить данные номера: ${error.message}`);
        } finally {
            this._setLoading(false);
        }
    }

    _populateForm(roomData) {
        console.log('Заполнение формы данными:', roomData);

        document.getElementById('room-id').value = roomData.id || '';

        const fields = ['room_number', 'capacity', 'category', 'price_per_night', 'description', 'floor', 'area', 'equipment'];
        fields.forEach(field => {
            const element = document.getElementById(field);
            if (element && roomData[field] !== undefined) {
                element.value = roomData[field] || '';
            }
        });

        const isAvailableCheckbox = document.getElementById('is_available');
        if (isAvailableCheckbox && roomData.is_available !== undefined) {
            isAvailableCheckbox.checked = roomData.is_available;
        }
    }

    async _handleSubmit(e) {
        e.preventDefault();

        if (this.isSubmitting) return;

        this._resetMessages();
        this._clearAllFieldErrors();

        const formData = new FormData(this.elements.form);
        const roomData = {
            room_number: formData.get('room_number').trim(),
            capacity: formData.get('capacity').trim(),
            is_available: formData.get('is_available') === 'on',
            category: formData.get('category').trim(),
            price_per_night: formData.get('price_per_night').trim(),
            description: formData.get('description').trim(),
            floor: formData.get('floor').trim(),
            area: formData.get('area').trim(),
            equipment: formData.get('equipment').trim()
        };

        const validationErrors = this._validateForm(roomData);
        if (Object.keys(validationErrors).length > 0) {
            this._showFieldErrors(validationErrors);
            this._showError('Пожалуйста, исправьте ошибки в форме');
            return;
        }

        this.isSubmitting = true;
        this._setLoading(true, this.mode === 'add' ? 'Добавление номера...' : 'Сохранение изменений...');

        try {
            let url, method;

            if (this.mode === 'add') {
                url = '/api/rooms/add';
                method = 'POST';
            } else {
                url = `/api/rooms/${this.roomId}/edit`;
                method = 'POST';
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(roomData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Операция выполнена успешно');

                if (this.mode === 'add') {
                    this.elements.form.reset();
                }

                this.redirectTimer = setTimeout(() => {
                    if (window.opener) {
                        window.opener.postMessage({
                            type: 'room_form_closed',
                            action: this.mode,
                            roomId: this.roomId,
                            success: true
                        }, window.location.origin);
                        window.close();
                    } else {
                        localStorage.setItem('rooms_should_refresh', Date.now().toString());
                        window.location.href = 'index.html';
                    }
                }, 2000);

            } else {
                if (result.errors) {
                    this._showFieldErrors(result.errors);
                }
                this._showError(result.message || 'Ошибка при выполнении операции');
            }

        } catch (error) {
            console.error('Ошибка при отправке формы:', error);
            this._showError('Ошибка соединения с сервером');
        } finally {
            this.isSubmitting = false;
            this._setLoading(false);
        }
    }

    _validateForm(data) {
        const errors = {};

        const requiredFields = ['room_number', 'capacity', 'category', 'price_per_night'];
        requiredFields.forEach(field => {
            if (!data[field]) {
                errors[field] = 'Поле обязательно для заполнения';
            }
        });

        if (data.room_number && !/^\d{3}[A-Z]?$/.test(data.room_number)) {
            errors.room_number = 'Номер комнаты должен быть в формате "101" или "101A"';
        }

        if (data.capacity) {
            const capacity = parseInt(data.capacity);
            if (isNaN(capacity) || capacity < 1 || capacity > 10) {
                errors.capacity = 'Вместимость должна быть от 1 до 10 человек';
            }
        }

        if (data.price_per_night) {
            const price = parseFloat(data.price_per_night);
            if (isNaN(price) || price <= 0) {
                errors.price_per_night = 'Цена должна быть положительным числом';
            }
        }

        const validCategories = ["Стандарт", "Люкс", "Эконом", "Студия", "Апартаменты"];
        if (data.category && !validCategories.includes(data.category)) {
            errors.category = `Категория должна быть одной из: ${validCategories.join(', ')}`;
        }

        return errors;
    }

    _validateField(input) {
        const fieldId = input.id;
        const value = input.value.trim();

        if (input.hasAttribute('required') && !value) {
            this._showFieldError(fieldId, 'Поле обязательно для заполнения');
        }
    }

    _clearFieldError(input) {
        if (input.classList.contains('error')) {
            const errorEl = document.getElementById(`${input.id}-error`);
            if (errorEl) {
                input.classList.remove('error');
                errorEl.classList.remove('show');
            }
        }
    }

    _clearAllFieldErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.classList.remove('show');
            el.textContent = '';
        });
        document.querySelectorAll('.form-input.error').forEach(el => {
            el.classList.remove('error');
        });
    }

    _showFieldErrors(errors) {
        Object.entries(errors).forEach(([field, message]) => {
            this._showFieldError(field, message);
        });
    }

    _showFieldError(fieldId, message) {
        const input = document.getElementById(fieldId);
        const errorEl = document.getElementById(`${fieldId}-error`);

        if (input && errorEl) {
            input.classList.add('error');
            errorEl.textContent = message;
            errorEl.classList.add('show');
        }
    }

    _resetMessages() {
        this.elements.successMessage.classList.remove('show');
        this.elements.errorMessage.classList.remove('show');
        this.elements.notFoundMessage.classList.remove('show');
    }

    _showSuccess(message) {
        this.elements.successMessage.textContent = message;
        this.elements.successMessage.classList.add('show');
    }

    _showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorMessage.classList.add('show');
    }

    _showNotFound() {
        this.elements.notFoundMessage.classList.add('show');
        this._disableForm();
    }

    _showFormReady() {
        this.elements.submitBtn.disabled = false;
    }

    _disableForm() {
        this.elements.submitBtn.disabled = true;
        this.elements.form.querySelectorAll('input, textarea, select').forEach(input => {
            input.disabled = true;
        });
    }

    _setLoading(isLoading, text = '') {
        if (isLoading) {
            this.elements.loading.classList.remove('hidden');
            if (text) this.elements.loadingText.textContent = text;
            this.elements.submitBtn.disabled = true;
            this.elements.submitBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; margin: 0 auto;"></div>';
        } else {
            this.elements.loading.classList.add('hidden');
            this.elements.submitBtn.disabled = false;
            this.elements.submitBtn.textContent = this.mode === 'add' ? 'Добавить номер' : 'Сохранить изменения';
        }
    }
}

/**
 * Представление таблицы номеров
 */
class RoomTableView {
    constructor(tableBody, statusElement) {
        this.tableBody = tableBody;
        this.statusElement = statusElement;

        this.onViewClick = null;
        this.onEditClick = null;
    }

    render(data) {
        this.tableBody.innerHTML = "";

        if (!data.items || data.items.length === 0) {
            this._renderNoData("Номера не найдены");
            this.statusElement.textContent = `Записей: 0`;
        }

        data.items.forEach((room) => {
            const row = this._createRoomRow(room);
            this.tableBody.appendChild(row);
        });

        this.statusElement.textContent = `Показано ${data.items.length} из ${data.total} записей (страница ${data.page})`;
    }

    _createRoomRow(room) {
        const row = document.createElement("tr");

        // ID
        const idCell = document.createElement("td");
        idCell.textContent = room.id;
        row.appendChild(idCell);

        // Номер комнаты
        const roomNumberCell = document.createElement("td");
        roomNumberCell.textContent = room.room_number;
        row.appendChild(roomNumberCell);

        // Категория
        const categoryCell = document.createElement("td");
        categoryCell.textContent = room.category;
        row.appendChild(categoryCell);

        // Вместимость
        const capacityCell = document.createElement("td");
        capacityCell.textContent = room.capacity;
        row.appendChild(capacityCell);

        // Цена за ночь
        const priceCell = document.createElement("td");
        priceCell.textContent = `${room.price_per_night} ₽`;
        row.appendChild(priceCell);

        // Статус
        const statusCell = document.createElement("td");
        const statusText = room.is_available ? "Доступен" : "Занят";
        const statusClass = room.is_available ? "status-available" : "status-unavailable";
        statusCell.innerHTML = `<span class="${statusClass}">${statusText}</span>`;
        row.appendChild(statusCell);

        // Кнопка просмотра
        const viewCell = document.createElement("td");
        const viewButton = document.createElement("button");
        viewButton.className = "btn btn-view";
        viewButton.textContent = "Просмотр";
        viewButton.addEventListener("click", (e) => {
            e.stopPropagation();
            if (this.onViewClick) {
                this.onViewClick(room.id);
            }
        });
        viewCell.appendChild(viewButton);
        row.appendChild(viewCell);

        // Кнопка редактирования
        const editCell = document.createElement("td");
        const editButton = document.createElement("button");
        editButton.className = "btn btn-edit";
        editButton.textContent = "Редактировать";
        editButton.title = "Редактировать";
        editButton.addEventListener("click", (e) => {
            e.stopPropagation();
            if (this.onEditClick) {
                this.onEditClick(room.id);
            }
        });
        editCell.appendChild(editButton);
        row.appendChild(editCell);

        return row;
    }

    _renderNoData(message) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 8;
        cell.className = "no-data";
        cell.innerHTML = `
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

/**
 * Контроллер для управления фильтрацией и сортировкой номеров
 */
class RoomFilterController {
    constructor(filterForm, resetButton, statusElement, uiController) {
        this.filterForm = filterForm;
        this.resetButton = resetButton;
        this.statusElement = statusElement;
        this.uiController = uiController;
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';
    }

    init() {
        this.filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        this.resetButton.addEventListener('click', () => {
            this.resetFilters();
        });

        this.loadSavedFilters();
    }

    applyFilters() {
        const filters = {
            room_number_substring: document.getElementById('room-number-filter').value.trim(),
            category: document.getElementById('category-filter').value,
            min_capacity: document.getElementById('min-capacity-filter').value.trim() || undefined,
            max_capacity: document.getElementById('max-capacity-filter').value.trim() || undefined,
            is_available: document.getElementById('availability-filter').value || undefined,
            min_price: document.getElementById('min-price-filter').value.trim() || undefined,
            max_price: document.getElementById('max-price-filter').value.trim() || undefined
        };

        const sortBy = document.getElementById('sort-filter').value;
        const sortOrder = document.getElementById('sort-order').value;

        Object.keys(filters).forEach(key => {
            if (!filters[key]) {
                delete filters[key];
            }
        });

        if (filters.is_available === 'all') {
            delete filters.is_available;
        } else if (filters.is_available === 'available') {
            filters.is_available = true;
        } else if (filters.is_available === 'unavailable') {
            filters.is_available = false;
        }

        this.currentFilters = filters;
        this.currentSort = sortBy;
        this.currentSortOrder = sortOrder;

        this.saveFilters();
        this.updateStatus();
        this.uiController.applyFilters(filters, sortBy, sortOrder);
    }

    resetFilters() {
        this.filterForm.reset();
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';

        localStorage.removeItem('roomFilters');
        localStorage.removeItem('roomSort');
        localStorage.removeItem('roomSortOrder');

        this.updateStatus();
        this.uiController.resetFilters();
    }

    updateStatus() {
        const filters = this.currentFilters;
        const sort = this.currentSort;
        const sortOrder = this.currentSortOrder;

        const activeFilters = Object.entries(filters).filter(([_, value]) => value);
        const hasFilters = activeFilters.length > 0;
        const hasSort = !!sort;

        let statusText = '';

        if (!hasFilters && !hasSort) {
            statusText = 'Фильтры не применены';
        } else {
            const parts = [];

            if (hasFilters) {
                const filterText = activeFilters.map(([key, value]) => {
                    const labels = {
                        room_number_substring: 'Номер',
                        category: 'Категория',
                        min_capacity: 'Мин. вместимость',
                        max_capacity: 'Макс. вместимость',
                        is_available: 'Доступность',
                        min_price: 'Мин. цена',
                        max_price: 'Макс. цена'
                    };

                    if (key === 'is_available') {
                        return `${labels[key]}: ${value === true ? 'доступен' : 'занят'}`;
                    }
                    if (key.includes('capacity') || key.includes('price')) {
                        return `${labels[key]}: ${value}`;
                    }
                    return `${labels[key]}: "${value}"`;
                }).join(', ');
                parts.push(`Фильтры: ${filterText}`);
            }

            if (hasSort) {
                const sortLabels = {
                    'id': 'ID',
                    'room_number': 'Номер',
                    'price': 'Цена',
                    'capacity': 'Вместимость',
                    'category': 'Категория'
                };
                const direction = sortOrder === 'asc' ? '↑' : '↓';
                parts.push(`Сортировка: ${sortLabels[sort]} ${direction}`);
            }

            statusText = parts.join(' | ');
        }

        this.statusElement.textContent = statusText;
    }

    saveFilters() {
        localStorage.setItem('roomFilters', JSON.stringify(this.currentFilters));
        localStorage.setItem('roomSort', this.currentSort);
        localStorage.setItem('roomSortOrder', this.currentSortOrder);
    }

    loadSavedFilters() {
        try {
            const savedFilters = localStorage.getItem('roomFilters');
            const savedSort = localStorage.getItem('roomSort');
            const savedSortOrder = localStorage.getItem('roomSortOrder');

            if (savedFilters) {
                this.currentFilters = JSON.parse(savedFilters);

                if (this.currentFilters.room_number_substring) {
                    document.getElementById('room-number-filter').value = this.currentFilters.room_number_substring;
                }
                if (this.currentFilters.category) {
                    document.getElementById('category-filter').value = this.currentFilters.category;
                }
                if (this.currentFilters.min_capacity) {
                    document.getElementById('min-capacity-filter').value = this.currentFilters.min_capacity;
                }
                if (this.currentFilters.max_capacity) {
                    document.getElementById('max-capacity-filter').value = this.currentFilters.max_capacity;
                }
                if (this.currentFilters.is_available !== undefined) {
                    const value = this.currentFilters.is_available === true ? 'available' : 'unavailable';
                    document.getElementById('availability-filter').value = value;
                }
                if (this.currentFilters.min_price) {
                    document.getElementById('min-price-filter').value = this.currentFilters.min_price;
                }
                if (this.currentFilters.max_price) {
                    document.getElementById('max-price-filter').value = this.currentFilters.max_price;
                }
            }

            if (savedSort) {
                this.currentSort = savedSort;
                document.getElementById('sort-filter').value = savedSort;
            }

            if (savedSortOrder) {
                this.currentSortOrder = savedSortOrder;
                document.getElementById('sort-order').value = savedSortOrder;
            }

            this.updateStatus();
        } catch (e) {
            console.error('Ошибка загрузки сохраненных фильтров:', e);
        }
    }
}

/**
 * Основной контроллер пользовательского интерфейса для номеров
 */
class RoomUiController {
    constructor(repository, tableView, detailView, addButton = null) {
        this.repository = repository;
        this.tableView = tableView;
        this.detailView = detailView;
        this.addButton = addButton;
        this.refreshRequested = false;
    }

    init() {
        this._bindRepositoryEvents();
        this._bindTableViewEvents();

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

        this.repository.subscribe("formClosed", (data) => {
            console.log("Форма номера закрыта, обновляем список:", data);
            this.refresh();
        });

        this.repository.subscribe("detail", (room) => {
            this.detailView.show(room);
        });

        this.repository.subscribe("deleted", (payload) => {
            this.tableView.showSuccess(payload.message || "Номер удален");
            this.refresh();
        });

        this.repository.subscribe("error", (payload) => {
            this.tableView.showError(payload.message);
        });
    }

    _bindTableViewEvents() {
        this.tableView.onViewClick = (roomId) => {
            this.repository.loadRoomDetail(roomId);
        };

        this.tableView.onEditClick = (roomId) => {
            window.location.href = `room_form.html?id=${roomId}`;
        };
    }

    _openAddWindow() {
        window.location.href = "room_form.html";
    }

    refresh() {
        this.repository.loadList(1);
        this.tableView.showLoading();
        this.refreshRequested = true;
    }
}