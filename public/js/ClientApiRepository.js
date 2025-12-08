/**
 Репозиторий клиентов для взаимодействия с серверным API.
 */
class ClientApiRepository {
    constructor(baseUrl = "/api") {
        this.baseUrl = baseUrl;
        this.observers = {
            clientsLoaded: [],    // наблюдатели за загрузкой списка клиентов
            clientLoaded: [],     // наблюдатели за загрузкой детальной информации
            errorOccurred: []     // наблюдатели за ошибками
        };
    }

    /**
     * Регистрирует наблюдателя для указанного события
     * @param {string} event - Событие для подписки
     * @param {function} handler - Функция-обработчик
     */
    subscribe(event, handler) {
        if (!this.observers[event]) {
            console.warn(`Неизвестное событие: ${event}`);
            return;
        }
        this.observers[event].push(handler);
    }

    /**
     * Уведомляет всех наблюдателей о событии
     * @param {string} event - Тип события
     * @param {any} data - Данные для передачи наблюдателям
     */
    _notify(event, data) {
        if (!this.observers[event]) {
            console.warn(`Попытка уведомить неизвестное событие: ${event}`);
            return;
        }
        this.observers[event].forEach(handler => handler(data));
    }

    /**
     * Загружает список клиентов с пагинацией
     * @param {number} page - Номер страницы (начинается с 1)
     * @param {number|null} pageSize - Количество клиентов на странице
     */
    async loadClients(page = 1, pageSize = null) {
        try {
            console.log(`Загрузка клиентов, страница ${page}...`);
            let url = `${this.baseUrl}/clients?page=${page}`;
            if (pageSize !== null) {
                url += `&page_size=${pageSize}`;
            }

            const response = await fetch(url);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Ошибка сервера: ${response.status}`);
            }

            const clientsData = await response.json();
            console.log('Получены данные клиентов:', clientsData);
            this._notify('clientsLoaded', clientsData);

        } catch (error) {
            console.error('Ошибка при загрузке списка клиентов:', error);
            this._notify('errorOccurred', {
                type: 'clients_list',
                message: error.message,
                context: { page, pageSize }
            });
        }
    }

    /**
     * Загружает детальную информацию о клиенте по ID
     * @param {number} clientId - ID клиента
     */
    async loadClientDetails(clientId) {
        try {
            console.log(`Загрузка деталей клиента ${clientId}...`);
            const response = await fetch(`${this.baseUrl}/clients/${clientId}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Клиент с ID ${clientId} не найден`);
            }

            const clientDetails = await response.json();
            console.log('Получены детали клиента:', clientDetails);
            this._notify('clientLoaded', clientDetails);

        } catch (error) {
            console.error(`Ошибка при загрузке клиента ${clientId}:`, error);
            this._notify('errorOccurred', {
                type: 'client_details',
                message: error.message,
                context: { clientId }
            });
        }
    }

    /**
     * Удаляет наблюдателя из указанного события
     * @param {string} event - Событие
     * @param {function} handler - Функция-обработчик для удаления
     */
    unsubscribe(event, handler) {
        if (!this.observers[event]) {
            console.warn(`Неизвестное событие для отписки: ${event}`);
            return;
        }
        const index = this.observers[event].indexOf(handler);
        if (index !== -1) {
            this.observers[event].splice(index, 1);
        }
    }

    /**
     * Очищает всех наблюдателей для всех событий
     */
    clearObservers() {
        Object.keys(this.observers).forEach(event => {
            this.observers[event] = [];
        });
    }
}