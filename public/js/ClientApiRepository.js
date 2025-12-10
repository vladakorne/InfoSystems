class ClientApiRepository {
    constructor(baseUrl = "/api") {
        this.baseUrl = baseUrl;
        this.observers = {
            clientsLoaded: [],    // наблюдатели за загрузкой списка клиентов
            clientLoaded: [],     // наблюдатели за загрузкой детальной информации
            clientDeleted: [],    // наблюдатели за удалением
            errorOccurred: []     // наблюдатели за ошибками
        };
    }

    subscribe(event, handler) {
        if (!this.observers[event]) {
            console.warn(`Неизвестное событие: ${event}`);
            return;
        }
        this.observers[event].push(handler);
    }

    _notify(event, data) {
        if (!this.observers[event]) {
            console.warn(`Попытка уведомить неизвестное событие: ${event}`);
            return;
        }
        this.observers[event].forEach(handler => handler(data));
    }

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

     async deleteClient(clientId) {
        try {
            console.log(`Удаление клиента ${clientId}...`);
            const response = await fetch(`${this.baseUrl}/clients/${clientId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `Ошибка сервера: ${response.status}`);
            }

            console.log('Клиент успешно удален:', result);

            // Уведомляем об успешном удалении
            this._notify('clientDeleted', {
                clientId: clientId,
                message: result.message,
                success: true
            });

            return result;

        } catch (error) {
            console.error(`Ошибка при удалении клиента ${clientId}:`, error);
            this._notify('errorOccurred', {
                type: 'client_delete',
                message: error.message,
                context: { clientId }
            });
            throw error;
        }
    }
}