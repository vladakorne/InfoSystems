/**
 * Репозиторий для работы с API бронирований с паттерном Наблюдатель
 */
class BookingApiRepository {
    constructor(baseUrl = "/api") {
        this.baseUrl = baseUrl;
        this.subscribers = {
            list: [],        // наблюдатели за загрузкой списка бронирований
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

            if (event.data.type === 'booking_form_closed' && event.data.success) {
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

            const response = await fetch(`${this.baseUrl}/bookings?${params.toString()}`);

            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.error || "Не удалось загрузить список бронирований");
            }
            const data = await response.json();
            this.notify("list", data);
        } catch (error) {
            this.notify("error", { message: error.message });
        }
    }

    async loadBookingDetail(bookingId) {
        try {
            const response = await fetch(`${this.baseUrl}/bookings/${bookingId}`);
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("Бронирование не найдено");
                }
                throw new Error("Не удалось загрузить данные бронирования");
            }
            const data = await response.json();
            this.notify("detail", data);
        } catch (error) {
            this.notify("error", { message: error.message });
        }
    }

    async deleteBooking(bookingId) {
        try {
            const response = await fetch(`${this.baseUrl}/bookings/${bookingId}`, {
                method: "DELETE",
            });
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.error || "Не удалось удалить бронирование");
            }
            const data = await response.json();
            this.notify("deleted", { id: bookingId, ...data });
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

    async getClients() {
        try {
            const response = await fetch(`${this.baseUrl}/clients/all`);
            if (!response.ok) {
                throw new Error("Не удалось загрузить список клиентов");
            }
            const data = await response.json();
            return data.items || [];
        } catch (error) {
            console.error('Ошибка при загрузке клиентов:', error);
            return [];
        }
    }

    async getRooms() {
        try {
            const response = await fetch(`${this.baseUrl}/rooms/all`);
            if (!response.ok) {
                throw new Error("Не удалось загрузить список номеров");
            }
            const data = await response.json();
            return data.items || [];
        } catch (error) {
            console.error('Ошибка при загрузке номеров:', error);
            return [];
        }
    }
}

/**
 * Представление детальной информации о бронировании
 */
class BookingDetailView {
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
                window.open(`detail_booking.html?id=${this.currentId}`, "_blank");
            }
        });
    }

    render(booking) {
        this.show(booking);
    }

    showLoading(id) {
        this.currentId = id;
        this.titleElement.textContent = "Загружаем данные бронирования…";
        this.contentElement.innerHTML = `<p class="muted">Получаем данные для бронирования ID ${id}</p>`;
        this.overlayElement.classList.remove("hidden");
    }

    show(booking) {
        this.currentId = booking.id;
        this.titleElement.textContent = `Бронирование #${booking.id}`;

        const statusText = this.getStatusText(booking.status);
        const statusClass = this.getStatusClass(booking.status);

        this.contentElement.innerHTML = `
            ${this._detailBlock("ID", booking.id)}
            ${this._detailBlock("Клиент ID", booking.client_id)}
            ${this._detailBlock("Номер ID", booking.room_id)}
            ${this._detailBlock("Дата заезда", booking.check_in)}
            ${this._detailBlock("Дата выезда", booking.check_out)}
            ${this._detailBlock("Ночей", (new Date(booking.check_out) - new Date(booking.check_in)) / (1000 * 60 * 60 * 24))}
            ${this._detailBlock("Общая сумма", `${booking.total_sum} ₽`)}
            ${this._detailBlock("Статус", `<span class="${statusClass}">${statusText}</span>`)}
            ${booking.notes ? this._detailBlock("Заметки", booking.notes) : ''}
            ${booking.created_at ? this._detailBlock("Дата создания", new Date(booking.created_at).toLocaleString()) : ''}
        `;
        this.overlayElement.classList.remove("hidden");
    }

    getStatusText(status) {
        const statusMap = {
            'confirmed': 'Подтверждено',
            'cancelled': 'Отменено',
            'completed': 'Завершено',
            'pending': 'Ожидание'
        };
        return statusMap[status] || status;
    }

    getStatusClass(status) {
        const classMap = {
            'confirmed': 'status-confirmed',
            'cancelled': 'status-cancelled',
            'completed': 'status-completed',
            'pending': 'status-pending'
        };
        return classMap[status] || '';
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
 * Основной контроллер формы бронирования
 */
class BookingFormController {
    constructor() {
        this.mode = null;
        this.bookingId = null;
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

    async init(mode, bookingId = null) {
        this.mode = mode;
        this.bookingId = bookingId;

        this._findElements();
        this._setupEventListeners();

        // Загружаем клиентов и номера для выпадающих списков
        await this._loadDropdownData();

        await this._loadInitialData().catch(error => {
            console.error('Ошибка при загрузке данных:', error);
            this._showError('Не удалось загрузить данные формы');
        });

        this._toggleDeleteButton();
    }

    _findElements() {
        this.elements = {
            form: document.getElementById('booking-form'),
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
            if (this.bookingId) {
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

        // Изменение дат - пересчет стоимости
        const checkInInput = document.getElementById('check_in');
        const checkOutInput = document.getElementById('check_out');
        const roomIdSelect = document.getElementById('room_id');

        if (checkInInput && checkOutInput && roomIdSelect) {
            const recalculatePrice = () => {
                this._calculateAndDisplayPrice();
            };

            checkInInput.addEventListener('change', recalculatePrice);
            checkOutInput.addEventListener('change', recalculatePrice);
            roomIdSelect.addEventListener('change', recalculatePrice);
        }

        form.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('blur', () => this._validateField(input));
            input.addEventListener('input', () => this._clearFieldError(input));
        });
    }

    async _loadDropdownData() {
        try {
            // Загружаем клиентов
            const clientsResponse = await fetch('/api/clients/all');
            if (clientsResponse.ok) {
                const clientsData = await clientsResponse.json();
                const clientSelect = document.getElementById('client_id');
                if (clientSelect && clientsData.items) {
                    clientSelect.innerHTML = '<option value="">Выберите клиента</option>';
                    clientsData.items.forEach(client => {
                        const option = document.createElement('option');
                        option.value = client.id;
                        option.textContent = `${client.surname} ${client.name} (ID: ${client.id})`;
                        clientSelect.appendChild(option);
                    });
                } else {
                    console.error('Некорректный формат данных клиентов:', clientsData);
                }
            } else {
                console.error('Ошибка при загрузке клиентов:', clientsResponse.status);
            }

            // Загружаем номера
            const roomsResponse = await fetch('/api/rooms/all');
            if (roomsResponse.ok) {
                const roomsData = await roomsResponse.json();
                const roomSelect = document.getElementById('room_id');
                if (roomSelect && roomsData.items) {
                    roomSelect.innerHTML = '<option value="">Выберите номер</option>';
                    roomsData.items.forEach(room => {
                        const option = document.createElement('option');
                        option.value = room.id;
                        option.textContent = `Номер ${room.room_number} (${room.category}, ${room.price_per_night} ₽)`;
                        option.dataset.price = room.price_per_night;
                        roomSelect.appendChild(option);
                    });
                } else {
                    console.error('Некорректный формат данных номеров:', roomsData);
                }
            } else {
                console.error('Ошибка при загрузке номеров:', roomsResponse.status);
            }
        } catch (error) {
            console.error('Ошибка при загрузке данных для выпадающих списков:', error);
        }
    }

    async _calculateAndDisplayPrice() {
        const checkIn = document.getElementById('check_in')?.value;
        const checkOut = document.getElementById('check_out')?.value;
        const roomId = document.getElementById('room_id')?.value;

        if (!checkIn || !checkOut || !roomId) {
            return;
        }

        try {
            const roomSelect = document.getElementById('room_id');
            const selectedOption = roomSelect.options[roomSelect.selectedIndex];
            const pricePerNight = parseFloat(selectedOption.dataset.price);

            if (!isNaN(pricePerNight) && pricePerNight > 0) {
                const checkInDate = new Date(checkIn);
                const checkOutDate = new Date(checkOut);
                const nights = Math.max(0, (checkOutDate - checkInDate) / (1000 * 60 * 60 * 24));
                const totalPrice = pricePerNight * nights;

                // Обновляем поле общей суммы
                const totalSumInput = document.getElementById('total_sum');
                if (totalSumInput) {
                    totalSumInput.value = totalPrice.toFixed(2);
                }

                // Показываем информацию о стоимости
                const priceInfo = document.getElementById('price-info');
                if (priceInfo) {
                    priceInfo.textContent = `Цена за ночь: ${pricePerNight} ₽ × ${nights} ночей = ${totalPrice.toFixed(2)} ₽`;
                    priceInfo.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Ошибка при расчете стоимости:', error);
        }
    }

    _toggleDeleteButton() {
        const { deleteBtn } = this.elements;

        if (this.mode === 'edit' && this.bookingId) {
            deleteBtn.classList.remove('hidden');
        } else {
            deleteBtn.classList.add('hidden');
        }
    }

    async _handleDelete() {
        if (!this.bookingId) return;

        const confirmed = confirm('Вы уверены, что хотите удалить это бронирование? Это действие нельзя отменить.');

        if (!confirmed) return;

        this._resetMessages();
        this._setLoading(true, 'Удаление бронирования...');

        try {
            const response = await fetch(`/api/bookings/${this.bookingId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Бронирование успешно удалено');

                this.redirectTimer = setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);

            } else {
                this._showError(result.message || 'Ошибка при удалении бронирования');
            }

        } catch (error) {
            console.error('Ошибка при удалении бронирования:', error);
            this._showError('Ошибка соединения с сервером');
        } finally {
            this._setLoading(false);
        }
    }

    async _loadInitialData() {
        if (this.mode === 'edit' && this.bookingId) {
            await this._loadBookingData(this.bookingId);
        } else {
            this._showFormReady();
            // Устанавливаем даты по умолчанию для нового бронирования
            this._setDefaultDates();
        }
    }

    _setDefaultDates() {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        const dayAfterTomorrow = new Date(today);
        dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 2);

        const checkInInput = document.getElementById('check_in');
        const checkOutInput = document.getElementById('check_out');

        if (checkInInput) {
            checkInInput.value = tomorrow.toISOString().split('T')[0];
        }
        if (checkOutInput) {
            checkOutInput.value = dayAfterTomorrow.toISOString().split('T')[0];
        }
    }

    async _loadBookingData(bookingId) {
        this._setLoading(true, 'Загрузка данных бронирования...');

        try {
            const response = await fetch(`/api/bookings/${bookingId}/edit/form`);

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
            console.error('Ошибка при загрузке данных бронирования:', error);
            this._showError(`Не удалось загрузить данные бронирования: ${error.message}`);
        } finally {
            this._setLoading(false);
        }
    }

    _populateForm(bookingData) {
        console.log('Заполнение формы данными:', bookingData);

        document.getElementById('booking-id').value = bookingData.id || '';

        const fields = ['client_id', 'room_id', 'check_in', 'check_out', 'total_sum', 'status', 'notes'];
        fields.forEach(field => {
            const element = document.getElementById(field);
            if (element && bookingData[field] !== undefined) {
                if (field === 'check_in' || field === 'check_out') {
                    // Форматируем дату для input type="date"
                    const date = new Date(bookingData[field]);
                    element.value = date.toISOString().split('T')[0];
                } else {
                    element.value = bookingData[field] || '';
                }
            }
        });

        // После заполнения пересчитываем стоимость
        setTimeout(() => this._calculateAndDisplayPrice(), 100);
    }

    async _handleSubmit(e) {
        e.preventDefault();

        if (this.isSubmitting) return;

        this._resetMessages();
        this._clearAllFieldErrors();

        const formData = new FormData(this.elements.form);
        const bookingData = {
            client_id: formData.get('client_id').trim(),
            room_id: formData.get('room_id').trim(),
            check_in: formData.get('check_in').trim(),
            check_out: formData.get('check_out').trim(),
            total_sum: formData.get('total_sum').trim(),
            status: formData.get('status').trim(),
            notes: formData.get('notes').trim()
        };

        const validationErrors = this._validateForm(bookingData);
        if (Object.keys(validationErrors).length > 0) {
            this._showFieldErrors(validationErrors);
            this._showError('Пожалуйста, исправьте ошибки в форме');
            return;
        }

        this.isSubmitting = true;
        this._setLoading(true, this.mode === 'add' ? 'Добавление бронирования...' : 'Сохранение изменений...');

        try {
            let url, method;

            if (this.mode === 'add') {
                url = '/api/bookings/add';
                method = 'POST';
            } else {
                url = `/api/bookings/${this.bookingId}/edit`;
                method = 'POST';
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookingData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Операция выполнена успешно');

                if (this.mode === 'add') {
                    this.elements.form.reset();
                    this._setDefaultDates();
                }

                this.redirectTimer = setTimeout(() => {
                    if (window.opener) {
                        window.opener.postMessage({
                            type: 'booking_form_closed',
                            action: this.mode,
                            bookingId: this.bookingId,
                            success: true
                        }, window.location.origin);
                        window.close();
                    } else {
                        localStorage.setItem('bookings_should_refresh', Date.now().toString());
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

        const requiredFields = ['client_id', 'room_id', 'check_in', 'check_out', 'total_sum', 'status'];
        requiredFields.forEach(field => {
            if (!data[field]) {
                errors[field] = 'Поле обязательно для заполнения';
            }
        });

        if (data.check_in && data.check_out) {
            const checkInDate = new Date(data.check_in);
            const checkOutDate = new Date(data.check_out);

            if (checkOutDate <= checkInDate) {
                errors.check_out = 'Дата выезда должна быть позже даты заезда';
            }

            const maxDays = 30;
            const daysDifference = (checkOutDate - checkInDate) / (1000 * 60 * 60 * 24);
            if (daysDifference > maxDays) {
                errors.check_out = `Максимальная длительность бронирования - ${maxDays} дней`;
            }
        }

        if (data.total_sum) {
            const price = parseFloat(data.total_sum);
            if (isNaN(price) || price <= 0) {
                errors.total_sum = 'Сумма должна быть положительным числом';
            }
        }

        const validStatuses = ["confirmed", "cancelled", "completed", "pending"];
        if (data.status && !validStatuses.includes(data.status)) {
            errors.status = `Статус должен быть одним из: ${validStatuses.join(', ')}`;
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
            this.elements.submitBtn.textContent = this.mode === 'add' ? 'Добавить бронирование' : 'Сохранить изменения';
        }
    }
}

/**
 * Представление таблицы бронирований
 */
class BookingTableView {
    constructor(tableBody, statusElement) {
        this.tableBody = tableBody;
        this.statusElement = statusElement;

        this.onViewClick = null;
        this.onEditClick = null;
    }

    render(data) {
        this.tableBody.innerHTML = "";

        if (!data.items || data.items.length === 0) {
            this._renderNoData("Бронирования не найдены");
            this.statusElement.textContent = `Записей: 0`;
        }

        data.items.forEach((booking) => {
            const row = this._createBookingRow(booking);
            this.tableBody.appendChild(row);
        });

        this.statusElement.textContent = `Показано ${data.items.length} из ${data.total} записей (страница ${data.page})`;
    }

    _createBookingRow(booking) {
        const row = document.createElement("tr");

        // ID
        const idCell = document.createElement("td");
        idCell.textContent = booking.id;
        row.appendChild(idCell);

        // ID клиента
        const clientCell = document.createElement("td");
        clientCell.textContent = booking.client_id;
        row.appendChild(clientCell);

        // ID номера
        const roomCell = document.createElement("td");
        roomCell.textContent = booking.room_id;
        row.appendChild(roomCell);

        // Дата заезда
        const checkInCell = document.createElement("td");
        checkInCell.textContent = booking.check_in;
        row.appendChild(checkInCell);

        // Дата выезда
        const checkOutCell = document.createElement("td");
        checkOutCell.textContent = booking.check_out;
        row.appendChild(checkOutCell);

        // Сумма
        const sumCell = document.createElement("td");
        sumCell.textContent = `${booking.total_sum} ₽`;
        row.appendChild(sumCell);

        // Статус
        const statusCell = document.createElement("td");
        const statusText = this.getStatusText(booking.status);
        const statusClass = this.getStatusClass(booking.status);
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
                this.onViewClick(booking.id);
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
                this.onEditClick(booking.id);
            }
        });
        editCell.appendChild(editButton);
        row.appendChild(editCell);

        return row;
    }

    getStatusText(status) {
        const statusMap = {
            'confirmed': 'Подтверждено',
            'cancelled': 'Отменено',
            'completed': 'Завершено',
            'pending': 'Ожидание'
        };
        return statusMap[status] || status;
    }

    getStatusClass(status) {
        const classMap = {
            'confirmed': 'status-confirmed',
            'cancelled': 'status-cancelled',
            'completed': 'status-completed',
            'pending': 'status-pending'
        };
        return classMap[status] || '';
    }

    _renderNoData(message) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 9;
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
 * Контроллер для управления фильтрацией и сортировкой бронирований
 */
class BookingFilterController {
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
            client_id: document.getElementById('client-id-filter').value.trim() || undefined,
            room_id: document.getElementById('room-id-filter').value.trim() || undefined,
            status: document.getElementById('status-filter').value || undefined,
            start_date: document.getElementById('start-date-filter').value || undefined,
            end_date: document.getElementById('end-date-filter').value || undefined,
            min_price: document.getElementById('min-price-booking-filter').value.trim() || undefined,
            max_price: document.getElementById('max-price-booking-filter').value.trim() || undefined
        };

        const sortBy = document.getElementById('booking-sort-filter').value;
        const sortOrder = document.getElementById('booking-sort-order').value;

        Object.keys(filters).forEach(key => {
            if (!filters[key]) {
                delete filters[key];
            }
        });

        // Преобразуем числовые значения
        if (filters.client_id) filters.client_id = parseInt(filters.client_id);
        if (filters.room_id) filters.room_id = parseInt(filters.room_id);
        if (filters.min_price) filters.min_price = parseFloat(filters.min_price);
        if (filters.max_price) filters.max_price = parseFloat(filters.max_price);

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

        localStorage.removeItem('bookingFilters');
        localStorage.removeItem('bookingSort');
        localStorage.removeItem('bookingSortOrder');

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
                        client_id: 'Клиент ID',
                        room_id: 'Номер ID',
                        status: 'Статус',
                        start_date: 'Дата с',
                        end_date: 'Дата по',
                        min_price: 'Мин. сумма',
                        max_price: 'Макс. сумма'
                    };

                    if (key === 'status') {
                        const statusMap = {
                            'confirmed': 'Подтверждено',
                            'cancelled': 'Отменено',
                            'completed': 'Завершено',
                            'pending': 'Ожидание'
                        };
                        return `${labels[key]}: ${statusMap[value] || value}`;
                    }
                    if (key.includes('_date')) {
                        return `${labels[key]}: ${new Date(value).toLocaleDateString()}`;
                    }
                    return `${labels[key]}: ${value}`;
                }).join(', ');
                parts.push(`Фильтры: ${filterText}`);
            }

            if (hasSort) {
                const sortLabels = {
                    'id': 'ID',
                    'check_in': 'Дата заезда',
                    'check_out': 'Дата выезда',
                    'total_sum': 'Сумма',
                    'created_at': 'Дата создания'
                };
                const direction = sortOrder === 'asc' ? '↑' : '↓';
                parts.push(`Сортировка: ${sortLabels[sort]} ${direction}`);
            }

            statusText = parts.join(' | ');
        }

        this.statusElement.textContent = statusText;
    }

    saveFilters() {
        localStorage.setItem('bookingFilters', JSON.stringify(this.currentFilters));
        localStorage.setItem('bookingSort', this.currentSort);
        localStorage.setItem('bookingSortOrder', this.currentSortOrder);
    }

    loadSavedFilters() {
        try {
            const savedFilters = localStorage.getItem('bookingFilters');
            const savedSort = localStorage.getItem('bookingSort');
            const savedSortOrder = localStorage.getItem('bookingSortOrder');

            if (savedFilters) {
                this.currentFilters = JSON.parse(savedFilters);

                if (this.currentFilters.client_id) {
                    document.getElementById('client-id-filter').value = this.currentFilters.client_id;
                }
                if (this.currentFilters.room_id) {
                    document.getElementById('room-id-filter').value = this.currentFilters.room_id;
                }
                if (this.currentFilters.status) {
                    document.getElementById('status-filter').value = this.currentFilters.status;
                }
                if (this.currentFilters.start_date) {
                    document.getElementById('start-date-filter').value = this.currentFilters.start_date;
                }
                if (this.currentFilters.end_date) {
                    document.getElementById('end-date-filter').value = this.currentFilters.end_date;
                }
                if (this.currentFilters.min_price) {
                    document.getElementById('min-price-booking-filter').value = this.currentFilters.min_price;
                }
                if (this.currentFilters.max_price) {
                    document.getElementById('max-price-booking-filter').value = this.currentFilters.max_price;
                }
            }

            if (savedSort) {
                this.currentSort = savedSort;
                document.getElementById('booking-sort-filter').value = savedSort;
            }

            if (savedSortOrder) {
                this.currentSortOrder = savedSortOrder;
                document.getElementById('booking-sort-order').value = savedSortOrder;
            }

            this.updateStatus();
        } catch (e) {
            console.error('Ошибка загрузки сохраненных фильтров:', e);
        }
    }
}

/**
 * Основной контроллер пользовательского интерфейса для бронирований
 */
class BookingUiController {
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
            console.log("Форма бронирования закрыта, обновляем список:", data);
            this.refresh();
        });

        this.repository.subscribe("detail", (booking) => {
            this.detailView.show(booking);
        });

        this.repository.subscribe("deleted", (payload) => {
            this.tableView.showSuccess(payload.message || "Бронирование удалено");
            this.refresh();
        });

        this.repository.subscribe("error", (payload) => {
            this.tableView.showError(payload.message);
        });
    }

    _bindTableViewEvents() {
        this.tableView.onViewClick = (bookingId) => {
            this.repository.loadBookingDetail(bookingId);
        };

        this.tableView.onEditClick = (bookingId) => {
            window.location.href = `booking_form.html?id=${bookingId}`;
        };
    }

    _openAddWindow() {
        window.location.href = "booking_form.html";
    }

    refresh() {
        this.repository.loadList(1);
        this.tableView.showLoading();
        this.refreshRequested = true;
    }
}