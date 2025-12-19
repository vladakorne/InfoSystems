/**
 * Основной контроллер формы клиента
 * Управляет логикой формы, валидацией и взаимодействием с API
 */
class ClientFormController {
    constructor() {
        this.mode = null; // режим работы (добавление/редактирование)
        this.clientId = null;
        //this.form = null;
        this.isSubmitting = false; // флаг для предотвращения двойной отправки формы
        this.redirectTimer = null; // таймер для автоматического перенаправления после успешной операции

        // ссылки на DOM элементы
        this.elements = {
            form: null,             // элеент формы
            submitBtn: null,        // кнопки
            cancelBtn: null,
            deleteBtn: null,
            successMessage: null,   // элементы сообщений
            errorMessage: null,
            notFoundMessage: null,
            loading: null,          // элементы загрузки
            loadingText: null
        };
    }


     //Инициализация контроллера
     //@param {string} mode - Режим работы ('add' или 'edit')
     //@param {number|null} clientId - ID клиента для редактирования
    init(mode, clientId = null) {
        // сохранение параметров в св-х класса
        this.mode = mode;
        this.clientId = clientId;

        // находим DOM элементы
        this._findElements();

        // настраиваем обработчики событий
        this._setupEventListeners();

        // загружаем данные если нужно (в режиме редактирования)
        this._loadInitialData().catch(error => {
            console.error('Ошибка при загрузке данных:', error);
            this._showError('Не удалось загрузить данные формы');
        });

        // показываем кнопку удаления (в режиме редактирования)
        this._toggleDeleteButton();
    }

    // Поиск DOM элементов
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

    // Настройка обработчиков событий
    _setupEventListeners() {
        const { form, cancelBtn, deleteBtn } = this.elements; // деструктуризация для удобного доступа к элементам

        // обработка отправки формы
        form.addEventListener('submit', (e) => this._handleSubmit(e));

        // обработка отмены
        cancelBtn.addEventListener('click', () => {
            window.location.href = 'index.html';
        });

        // обработка удаления
        deleteBtn.addEventListener('click', async () => {
            if (this.clientId) {
                try {
                    await this._handleDelete();
                } catch (error) {
                    console.error('Ошибка при удалении:', error);
                }
            }
        });

        // очистка таймера при уходе/перезагрузке со страницы
        window.addEventListener('beforeunload', () => {
            if (this.redirectTimer) {
                clearTimeout(this.redirectTimer);
            }
        });

        // валидация при потере фокуса (blur) и очистка ошибок при вводе (input)
        form.querySelectorAll('.form-input').forEach(input => {
            input.addEventListener('blur', () => this._validateField(input));
            input.addEventListener('input', () => this._clearFieldError(input));
        });
    }

    // управление кнопкой удаления
    _toggleDeleteButton() {
        const { deleteBtn } = this.elements;

        // показываем кнопку удаления только в режиме редактирования
        if (this.mode === 'edit' && this.clientId) {
            deleteBtn.classList.remove('hidden');
        } else {
            deleteBtn.classList.add('hidden');
        }
    }

    // обработка удаления клиента
    async _handleDelete() {
        if (!this.clientId) return; // проверка наличия клиента

        // подтверждение удаления
        const confirmed = confirm('Вы уверены, что хотите удалить этого клиента? Это действие нельзя отменить.');

        if (!confirmed) return; // если отказ - выходим

        this._resetMessages();
        this._setLoading(true, 'Удаление клиента...');

        try {
            const response = await fetch(`/api/clients/${this.clientId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            }); // отправка DELETE запроса на сервер

            const result = await response.json();  // ответ от сервера

            if (response.ok && result.success) {
                this._showSuccess(result.message || 'Клиент успешно удален');

                // перенаправление на главную страницу через 2 секунды
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

     // загрузка начальных данных
    async _loadInitialData() {
        // если режим редактирования - загружает данные клиента, иначе показывает пустую форму
        if (this.mode === 'edit' && this.clientId) {
            await this._loadClientData(this.clientId);
        } else {
            // в режиме добавления просто показываем пустую форму
            this._showFormReady();
        }
    }

     // загрузка данных клиента для редактирования
    async _loadClientData(clientId) {
        this._setLoading(true, 'Загрузка данных клиента...');

        try {
            const response = await fetch(`/api/clients/${clientId}/edit/form`); // GET запрос для получения данных клиента

            if (response.status === 404) {
                this._showNotFound();
                return;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Ошибка сервера: ${response.status}`);
            }

            // проверка бизнес-логики успеха в ответе сервера
            const result = await response.json();

            if (result.success === false) {
                throw new Error(result.error || 'Не удалось загрузить данные');
            }

            // заполняем форму данными
            this._populateForm(result.data || result);
            this._showFormReady(); // активация кнопки отправки

        } catch (error) {
            console.error('Ошибка при загрузке данных клиента:', error);
            this._showError(`Не удалось загрузить данные клиента: ${error.message}`);
        } finally {
            this._setLoading(false);
        }
    }

    // заполнение формы данными
    _populateForm(clientData) {
        console.log('Заполнение формы данными:', clientData);

        // устанавливаем ID клиента в скрытое поле для отправки на сервер
        document.getElementById('client-id').value = clientData.id || '';

        // заполняем поля формы
        const fields = ['surname', 'name', 'patronymic', 'phone', 'passport', 'email', 'comment'];
        fields.forEach(field => {
            const element = document.getElementById(field);
            if (element && clientData[field] !== undefined) {
                element.value = clientData[field] || '';
            }
        });
    }

    // обработка отправки формы
    async _handleSubmit(e) {
        e.preventDefault();

        if (this.isSubmitting) return;

        // сбросили все сообщения и ошибки
        this._resetMessages();
        this._clearAllFieldErrors();

        // собираем данные формы с удалением лишних пробелов (trim())
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

        // валидация на клиенте
        const validationErrors = this._validateForm(clientData);
        if (Object.keys(validationErrors).length > 0) {
            this._showFieldErrors(validationErrors);
            this._showError('Пожалуйста, исправьте ошибки в форме');
            return;
        }

        this.isSubmitting = true;
        this._setLoading(true, this.mode === 'add' ? 'Добавление клиента...' : 'Сохранение изменений...');

        try {
            //определение URL и метода HTTP в зависимости от режима
            let url, method;

            if (this.mode === 'add') {
                url = '/api/clients/add';
                method = 'POST';
            } else {
                url = `/api/clients/${this.clientId}/edit`;
                method = 'POST';
            }

            // отправляем данные на сервер
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

                // очищаем форму в режиме добавления
                if (this.mode === 'add') {
                    this.elements.form.reset();
                }

                // Автоматическое перенаправление через 3 секунды
                this.redirectTimer = setTimeout(() => {
                    // отправляем сообщение родительскому окну об обновлении
                    if (window.opener) {
                        // если открыто как всплывающее окно
                        window.opener.postMessage({
                            type: 'form_closed',
                            action: this.mode, // 'add' или 'edit'
                            clientId: this.clientId,
                            success: true
                        }, window.location.origin);
                        window.close();
                    } else {
                        // если отдельная вкладка
                        // сообщаем через localStorage о необходимости обновления
                        localStorage.setItem('clients_should_refresh', Date.now().toString());
                        window.location.href = 'index.html';
                    }
                }, 2000);

            } else {
                // обработка ошибок валидации с сервера
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

    // доп валидация на ux
    _validateForm(data) {
        const errors = {};

        const requiredFields = ['surname', 'name', 'phone'];
        requiredFields.forEach(field => {
            if (!data[field]) {
                errors[field] = 'Поле обязательно для заполнения';
            }
        });

        if (data.phone && !/^[+]?\d{7,11}$/.test(data.phone.replace(/\s+/g, ''))) {
            errors.phone = 'Некорректный формат телефона';
        }

        if (data.passport && !/^\d{10}$/.test(data.passport)) {
            errors.passport = 'Паспорт должен содержать ровно 10 цифр';
        }

        if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
            errors.email = 'Некорректный формат email';
        }

        return errors;
    }


     //Валидация отдельного поля - @param {HTMLElement} input - Поле ввода
    _validateField(input) {
        const fieldId = input.id;
        const value = input.value.trim();

        if (input.hasAttribute('required') && !value) {
            this._showFieldError(fieldId, 'Поле обязательно для заполнения');
        }
    }

    // очистка ошибки поля
    _clearFieldError(input) {
        if (input.classList.contains('error')) {
            const errorEl = document.getElementById(`${input.id}-error`);
            if (errorEl) {
                input.classList.remove('error');
                errorEl.classList.remove('show');
            }
        }
    }

     // очистка всех ошибок полей
    _clearAllFieldErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.classList.remove('show');
            el.textContent = '';
        });
        document.querySelectorAll('.form-input.error').forEach(el => {
            el.classList.remove('error');
        });
    }

    // показывает ошибки полей - @param {Object} errors - Объект с ошибками {field: message}
    _showFieldErrors(errors) {
        Object.entries(errors).forEach(([field, message]) => {
            this._showFieldError(field, message);
        });
    }

     // показывает ошибку конкретного поля - @param {string} fieldId - ID поля
     // @param {string} message - Сообщение об ошибке
    _showFieldError(fieldId, message) {
        const input = document.getElementById(fieldId);
        const errorEl = document.getElementById(`${fieldId}-error`);

        if (input && errorEl) {
            input.classList.add('error');
            errorEl.textContent = message;
            errorEl.classList.add('show');
        }
    }

     // сброс всех сообщений
    _resetMessages() {
        this.elements.successMessage.classList.remove('show');
        this.elements.errorMessage.classList.remove('show');
        this.elements.notFoundMessage.classList.remove('show');
    }

    // сообщение об успехе
    _showSuccess(message) {
        this.elements.successMessage.textContent = message;
        this.elements.successMessage.classList.add('show');
    }

    // сообщение об ошибке
    _showError(message) {
        this.elements.errorMessage.textContent = message;
        this.elements.errorMessage.classList.add('show');
    }

    // сообщение "не найдено"
    _showNotFound() {
        this.elements.notFoundMessage.classList.add('show');
        this._disableForm();
    }

    _showFormReady() {
        // Активируем кнопку отправки
        this.elements.submitBtn.disabled = false;
    }

    // отключаем форму при ошибке "не найден"
    _disableForm() {
        this.elements.submitBtn.disabled = true;
        this.elements.form.querySelectorAll('input, textarea').forEach(input => {
            input.disabled = true;
        });
    }

     // установка состояние загрузки
     // @param {boolean} isLoading - Загружается ли
     // @param {string} text - Текст загрузки
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