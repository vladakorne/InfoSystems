/**
 * Основной контроллер формы клиента
 * Управляет логикой формы, валидацией и взаимодействием с API
 */
class ClientFormController {
    constructor() {
        this.mode = null;
        this.clientId = null;
        this.form = null;
        this.isSubmitting = false;
        this.redirectTimer = null;

        // Ссылки на DOM элементы
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

    /**
     * Инициализация контроллера
     * @param {string} mode - Режим работы ('add' или 'edit')
     * @param {number|null} clientId - ID клиента для редактирования
     */
    init(mode, clientId = null) {
        this.mode = mode;
        this.clientId = clientId;

        // Находим DOM элементы
        this._findElements();

        // Настраиваем обработчики событий
        this._setupEventListeners();

        // Загружаем данные если нужно
        this._loadInitialData();

        // Показываем кнопку удаления в режиме редактирования
        this._toggleDeleteButton();
    }

    /**
     * Поиск DOM элементов
     * @private
     */
    _findElements() {
        this.elements = {
            form: document.getElementById('client-form'),
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

    /**
     * Настройка обработчиков событий
     * @private
     */
    _setupEventListeners() {
        const { form, cancelBtn, deleteBtn } = this.elements;

        // Обработка отправки формы
        form.addEventListener('submit', (e) => this._handleSubmit(e));

        // Обработка отмены
        cancelBtn.addEventListener('click', () => {
            window.location.href = 'index.html';
        });

        // Обработка удаления
        deleteBtn.addEventListener('click', () => {
            if (this.clientId) {
                this._handleDelete();
            }
        });

        // Очистка таймера при уходе со страницы
        window.addEventListener('beforeunload', () => {
            if (this.redirectTimer) {
                clearTimeout(this.redirectTimer);
            }
        });

        // Валидация в реальном времени
        form.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('blur', () => this._validateField(input));
            input.addEventListener('input', () => this._clearFieldError(input));
        });
    }

    _toggleDeleteButton() {
        const { deleteBtn } = this.elements;

        // Показываем кнопку удаления только в режиме редактирования
        if (this.mode === 'edit' && this.clientId) {
            deleteBtn.classList.remove('hidden');
        } else {
            deleteBtn.classList.add('hidden');
        }
    }

    /**
     * Обработка удаления клиента
     * @private
     */
    async _handleDelete() {
        if (!this.clientId) return;

        // Подтверждение удаления
        const confirmed = confirm('Вы уверены, что хотите удалить этого клиента? Это действие нельзя отменить.');

        if (!confirmed) return;

        this._resetMessages();
        this._setLoading(true, 'Удаление клиента...');

        try {
            const response = await fetch(`/api/clients/${this.clientId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Клиент успешно удален');

                // Перенаправление на главную страницу через 2 секунды
                this.redirectTimer = setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);

            } else {
                this._showError(result.message || 'Ошибка при удалении клиента');
            }

        } catch (error) {
            console.error('Ошибка при удалении клиента:', error);
            this._showError('Ошибка соединения с сервером');
        } finally {
            this._setLoading(false);
        }
    }

    /**
     * Загрузка начальных данных
     * @private
     */
    async _loadInitialData() {
        if (this.mode === 'edit' && this.clientId) {
            await this._loadClientData(this.clientId);
        } else {
            // В режиме добавления просто показываем пустую форму
            this._showFormReady();
        }
    }

    /**
     * Загрузка данных клиента для редактирования
     * @param {number} clientId - ID клиента
     * @private
     */
    async _loadClientData(clientId) {
        this._setLoading(true, 'Загрузка данных клиента...');

        try {
            console.log(`Загрузка данных клиента ${clientId}...`);
            const response = await fetch(`/api/clients/${clientId}/edit/form`);

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

            // Заполняем форму данными
            this._populateForm(result.data || result);
            this._showFormReady();

        } catch (error) {
            console.error('Ошибка при загрузке данных клиента:', error);
            this._showError(`Не удалось загрузить данные клиента: ${error.message}`);
        } finally {
            this._setLoading(false);
        }
    }

    /**
     * Заполнение формы данными
     * @param {Object} clientData - Данные клиента
     * @private
     */
    _populateForm(clientData) {
        console.log('Заполнение формы данными:', clientData);

        // Устанавливаем ID клиента в скрытое поле
        document.getElementById('client-id').value = clientData.id || '';

        // Заполняем поля формы
        const fields = ['surname', 'name', 'patronymic', 'phone', 'passport', 'email', 'comment'];
        fields.forEach(field => {
            const element = document.getElementById(field);
            if (element && clientData[field] !== undefined) {
                element.value = clientData[field] || '';
            }
        });
    }

    /**
     * Обработка отправки формы
     * @param {Event} e - Событие отправки формы
     * @private
     */
    async _handleSubmit(e) {
        e.preventDefault();

        if (this.isSubmitting) return;

        this._resetMessages();
        this._clearAllFieldErrors();

        // Собираем данные формы
        const formData = new FormData(this.elements.form);
        const clientData = {
            surname: formData.get('surname').trim(),
            name: formData.get('name').trim(),
            patronymic: formData.get('patronymic').trim(),
            phone: formData.get('phone').trim(),
            passport: formData.get('passport').trim(),
            email: formData.get('email').trim(),
            comment: formData.get('comment').trim()
        };

        // Валидация на клиенте
        const validationErrors = this._validateForm(clientData);
        if (Object.keys(validationErrors).length > 0) {
            this._showFieldErrors(validationErrors);
            this._showError('Пожалуйста, исправьте ошибки в форме');
            return;
        }

        this.isSubmitting = true;
        this._setLoading(true, this.mode === 'add' ? 'Добавление клиента...' : 'Сохранение изменений...');

        try {
            let url, method;

            if (this.mode === 'add') {
                url = '/api/clients/add';
                method = 'POST';
            } else {
                url = `/api/clients/${this.clientId}/edit`;
                method = 'POST';
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(clientData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Операция выполнена успешно');

                // Очищаем форму в режиме добавления
                if (this.mode === 'add') {
                    this.elements.form.reset();
                }

                // Автоматическое перенаправление через 3 секунды
                this.redirectTimer = setTimeout(() => {
                    window.location.href = 'index.html';
                }, 3000);

            } else {
                // Обработка ошибок валидации с сервера
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

    /**
     * Валидация формы на клиенте
     * @param {Object} data - Данные формы
     * @returns {Object} Объект с ошибками
     * @private
     */
    _validateForm(data) {
        const errors = {};

        // Проверка обязательных полей
        const requiredFields = ['surname', 'name', 'phone'];
        requiredFields.forEach(field => {
            if (!data[field]) {
                errors[field] = 'Поле обязательно для заполнения';
            }
        });

        // Проверка телефона (базовая)
        if (data.phone && !/^[+]?\d{7,15}$/.test(data.phone.replace(/\s+/g, ''))) {
            errors.phone = 'Некорректный формат телефона';
        }

        // Проверка паспорта
        if (data.passport && !/^\d{10}$/.test(data.passport)) {
            errors.passport = 'Паспорт должен содержать ровно 10 цифр';
        }

        // Проверка email
        if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
            errors.email = 'Некорректный формат email';
        }

        return errors;
    }

    /**
     * Валидация отдельного поля
     * @param {HTMLElement} input - Поле ввода
     * @private
     */
    _validateField(input) {
        const fieldId = input.id;
        const value = input.value.trim();

        if (input.hasAttribute('required') && !value) {
            this._showFieldError(fieldId, 'Поле обязательно для заполнения');
        }
    }

    /**
     * Очистка ошибки поля
     * @param {HTMLElement} input - Поле ввода
     * @private
     */
    _clearFieldError(input) {
        if (input.classList.contains('error')) {
            const errorEl = document.getElementById(`${input.id}-error`);
            if (errorEl) {
                input.classList.remove('error');
                errorEl.classList.remove('show');
            }
        }
    }

    /**
     * Очистка всех ошибок полей
     * @private
     */
    _clearAllFieldErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.classList.remove('show');
            el.textContent = '';
        });
        document.querySelectorAll('.form-input.error').forEach(el => {
            el.classList.remove('error');
        });
    }

    /**
     * Показать ошибки полей
     * @param {Object} errors - Объект с ошибками {field: message}
     * @private
     */
    _showFieldErrors(errors) {
        Object.entries(errors).forEach(([field, message]) => {
            this._showFieldError(field, message);
        });
    }

    /**
     * Показать ошибку конкретного поля
     * @param {string} fieldId - ID поля
     * @param {string} message - Сообщение об ошибке
     * @private
     */
    _showFieldError(fieldId, message) {
        const input = document.getElementById(fieldId);
        const errorEl = document.getElementById(`${fieldId}-error`);

        if (input && errorEl) {
            input.classList.add('error');
            errorEl.textContent = message;
            errorEl.classList.add('show');
        }
    }

    /**
     * Сброс всех сообщений
     * @private
     */
    _resetMessages() {
        this.elements.successMessage.classList.remove('show');
        this.elements.errorMessage.classList.remove('show');
        this.elements.notFoundMessage.classList.remove('show');
    }

    /**
     * Показать сообщение об успехе
     * @param {string} message - Сообщение
     * @private
     */
    _showSuccess(message) {
        this.elements.successMessage.textContent = message;
        this.elements.successMessage.classList.add('show');
    }

    /**
     * Показать сообщение об ошибке
     * @param {string} message - Сообщение
     * @private
     */
    _showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorMessage.classList.add('show');
    }

    /**
     * Показать сообщение "не найдено"
     * @private
     */
    _showNotFound() {
        this.elements.notFoundMessage.classList.add('show');
        this._disableForm();
    }

    /**
     * Показать, что форма готова
     * @private
     */
    _showFormReady() {
        // Активируем кнопку отправки
        this.elements.submitBtn.disabled = false;
    }

    /**
     * Отключить форму
     * @private
     */
    _disableForm() {
        this.elements.submitBtn.disabled = true;
        this.elements.form.querySelectorAll('input, textarea').forEach(input => {
            input.disabled = true;
        });
    }

    /**
     * Установить состояние загрузки
     * @param {boolean} isLoading - Загружается ли
     * @param {string} text - Текст загрузки
     * @private
     */
    _setLoading(isLoading, text = '') {
        if (isLoading) {
            this.elements.loading.classList.remove('hidden');
            if (text) this.elements.loadingText.textContent = text;
            this.elements.submitBtn.disabled = true;
            this.elements.submitBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; margin: 0 auto;"></div>';
        } else {
            this.elements.loading.classList.add('hidden');
            this.elements.submitBtn.disabled = false;
            this.elements.submitBtn.textContent = this.mode === 'add' ? 'Добавить клиента' : 'Сохранить изменения';
        }
    }
}