/**
 * Репозиторий для работы с API клиентов с паттерном Наблюдатель
 */
class ClientApiRepository {
    constructor(baseUrl = "/api") {
        this.baseUrl = baseUrl;
        this.subscribers = {
            list: [],
            detail: [],
            deleted: [],
            error: [],
            filtersChanged: []  // Новое событие для изменения фильтров
        };
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';
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

            // Добавляем параметры фильтрации
            Object.entries(this.currentFilters).forEach(([key, value]) => {
                if (value !== undefined && value !== null && value !== "") {
                    params.append(key, value);
                }
            });

            // Добавляем параметры сортировки
            if (this.currentSort) {
                params.append("sort", this.currentSort);
                params.append("sort_order", this.currentSortOrder);
            }

            const response = await fetch(`${this.baseUrl}/clients?${params.toString()}`);
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.error || "Не удалось загрузить список клиентов");
            }
            const data = await response.json();
            this.notify("list", data);
            return data;
        } catch (error) {
            this.notify("error", { message: error.message });
            throw error;
        }
    }

    async loadClientDetail(clientId) {
        try {
            const response = await fetch(`${this.baseUrl}/clients/${clientId}`);
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error("Клиент не найден");
                }
                throw new Error("Не удалось загрузить данные клиента");
            }
            const data = await response.json();
            this.notify("detail", data);
            return data;
        } catch (error) {
            this.notify("error", { message: error.message });
            throw error;
        }
    }

    async deleteClient(clientId) {
        try {
            const response = await fetch(`${this.baseUrl}/clients/${clientId}`, {
                method: "DELETE",
            });
            if (!response.ok) {
                const payload = await response.json().catch(() => ({}));
                throw new Error(payload.error || "Не удалось удалить клиента");
            }
            const data = await response.json();
            this.notify("deleted", { id: clientId, ...data });
            return data;
        } catch (error) {
            this.notify("error", { message: error.message });
            throw error;
        }
    }

    // Новый метод для применения фильтров без смены страницы
    applyFilters(filters = null, sort = null, sortOrder = null) {
        this.currentFilters = filters || {};
        this.currentSort = sort || '';
        this.currentSortOrder = sortOrder || 'asc';
        this.notify("filtersChanged", {
            filters: this.currentFilters,
            sort: this.currentSort,
            sortOrder: this.currentSortOrder
        });
        return this.loadList(1); // Возвращаемся на первую страницу
    }

    // Новый метод для сброса фильтров
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

    getCurrentFilters() {
        return {
            filters: this.currentFilters,
            sort: this.currentSort,
            sortOrder: this.currentSortOrder
        };
    }
}