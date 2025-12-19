/**
 * Репозиторий для работы с API клиентов с паттерном Наблюдатель
 */
class ClientApiRepository {
    // класс репозиторий, который инкапсулирует всю логику работы с API клиентов
    constructor(baseUrl = "/api") { //станавливаем базовый URL API
        this.baseUrl = baseUrl;
        this.subscribers = { // инициализация подписок
            list: [],        // наблюдатели за загрузкой списка клиентов
            detail: [],      // наблюдатели за загрузкой детальной инфо
            deleted: [],     // наблюдатели за удалением
            error: [],       // наблюдатели за ошибками
            filtersChanged: [] // наблюдатели за изменением фильтров
        };
        // состояние репозитория (фильтров нет, сортирвоки нет, сортировка по умолчанию возрастание)
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';
        this.subscribers.formClosed = [];

        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;

            if (event.data.type === 'form_closed' && event.data.success) {
                this.notify('formClosed', event.data);
            }
        });
    }

    // регистрация обработчика для определения события
    subscribe(event, handler) { //имя события и обработчик
        if (this.subscribers[event]) { // гарантируем, что событие существует
            this.subscribers[event].push(handler);
        }
    }

    // уведомление подписчиков
    notify(event, payload) { // имя события и данные для передачи обработчикам
        (this.subscribers[event] || []).forEach((handler) => handler(payload)); // вызываем каждый обработчик с данными
    }

    // асинхронный метод загрузки клиентов с пагинацией, фильтрацией и сортировкой
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
            } // обновили парметры, если они не null

            const params = new URLSearchParams({ page }); // объект для query-параметров URL

            //добавление фильтров в параметры запроса
            Object.entries(this.currentFilters).forEach(([key, value]) => { // предобразуем объект фильров в [ключ,значение]
                if (value !== undefined && value !== null && value !== "") { // пустые значения игнорируем
                    params.append(key, value); // добавляем параметр в url
                }
            });

            // добавляем параметры сортировки
            if (this.currentSort) {
                params.append("sort", this.currentSort);
                params.append("sort_order", this.currentSortOrder);
            }

            const response = await fetch(`${this.baseUrl}/clients?${params.toString()}`); // нативное выполнение HTTP GET запроса к AP
           // обработка ошибкоа
            if (!response.ok) { // если статус не успешен
                const payload = await response.json().catch(() => ({})); // получаем json c сервера, при ошибке-пустой объект
                throw new Error(payload.error || "Не удалось загрузить список клиентов");
            }
            const data = await response.json(); // поулчаем ответ в формате json
            this.notify("list", data); // уведомляем подписчиков события list
        } catch (error) {
            this.notify("error", { message: error.message }); // уведомление об ошибке
        }
    }

    async loadClientDetail(clientId) {
        try {
            const response = await fetch(`${this.baseUrl}/clients/${clientId}`); // выполняет HTTP GET запрос к эндпоинту /api/clients/{id} для получения детальной информации.
            if (!response.ok) {
                if (response.status === 404) { // конкретная обработка ошибки 404
                    throw new Error("Клиент не найден");
                }
                throw new Error("Не удалось загрузить данные клиента");
            }
            const data = await response.json(); //парсим json ответ с сервера
            this.notify("detail", data); // уведомлем подписчиков detail
        } catch (error) {
            this.notify("error", { message: error.message }); // уведомлем подписчиков error
        }
    }

    async deleteClient(clientId) {
        try {
            const response = await fetch(`${this.baseUrl}/clients/${clientId}`, { // нативно выполняет HTTP DELETE запрос для удаления клиента
                method: "DELETE", // вместо GET, который стоит по умолчанию
            }); // CRUD операция Delete
            if (!response.ok) { // пытаемся получить JSON с сообщением об ошибке от сервера
                const payload = await response.json().catch(() => ({})); // безопасная обработка, если сервер не вернул JSON
                throw new Error(payload.error || "Не удалось удалить клиента");
            }
            const data = await response.json(); // парсим успешеый ответ
            this.notify("deleted", { id: clientId, ...data }); // уведомляем подписчиков и передаем id + данные от сервера для автоматического обновления списка
        } catch (error) {
            this.notify("error", { message: error.message });
        }
    }

    applyFilters(filters = null, sort = null, sortOrder = null) {
        // синхронный метод для установки фильтров и сортировки с последующей загрузкой данных
        this.currentFilters = filters || {};
        this.currentSort = sort || '';
        this.currentSortOrder = sortOrder || 'asc';

        this.notify("filtersChanged", { // уведомление об изменении фильтров
            filters: this.currentFilters,
            sort: this.currentSort,
            sortOrder: this.currentSortOrder
        });
        /// filtersChanged позволяет ui компонентам обновить состояние
        return this.loadList(1); // автоматически возвращаем страницу с примененными фильтрами
    }

    resetFilters() {  // сброс фильтров
        // очищаем состояния
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';

        this.notify("filtersChanged", {
            filters: {},
            sort: '',
            sortOrder: 'asc'
        }); // уведомляем подписчиков о сбросе
        return this.loadList(1); // перезагружаем данные
    }
}