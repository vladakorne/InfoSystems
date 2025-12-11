/**
 * Контроллер для управления фильтрацией и сортировкой
 */
class FilterController {
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
        // Обработка отправки формы фильтрации
        this.filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // Обработка сброса фильтров
        this.resetButton.addEventListener('click', () => {
            this.resetFilters();
        });

        // Загружаем сохраненные фильтры из localStorage
        this.loadSavedFilters();
    }

    applyFilters() {
        // Получаем значения из формы
        const filters = {
            surname_prefix: document.getElementById('surname-filter').value.trim(),
            name_prefix: document.getElementById('name-filter').value.trim(),
            patronymic_prefix: document.getElementById('patronymic-filter').value.trim(),
            phone_substring: document.getElementById('phone-filter').value.trim()
        };

        const sortBy = document.getElementById('sort-filter').value;
        const sortOrder = document.getElementById('sort-order').value;

        // Убираем пустые фильтры
        Object.keys(filters).forEach(key => {
            if (!filters[key]) {
                delete filters[key];
            }
        });

        // Сохраняем текущие фильтры
        this.currentFilters = filters;
        this.currentSort = sortBy;
        this.currentSortOrder = sortOrder;

        // Сохраняем в localStorage
        this.saveFilters();

        // Обновляем статус
        this.updateStatus();

        // Применяем фильтры через контроллер
        this.uiController.applyFilters(filters, sortBy, sortOrder);
    }

    resetFilters() {
        // Сбрасываем форму
        this.filterForm.reset();

        // Сбрасываем текущие фильтры
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';

        // Очищаем localStorage
        localStorage.removeItem('clientFilters');
        localStorage.removeItem('clientSort');
        localStorage.removeItem('clientSortOrder');

        // Обновляем статус
        this.updateStatus();

        // Применяем сброс через контроллер
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
                        surname_prefix: 'Фамилия',
                        name_prefix: 'Имя',
                        patronymic_prefix: 'Отчество',
                        phone_substring: 'Телефон'
                    };
                    return `${labels[key]}: "${value}"`;
                }).join(', ');
                parts.push(`Фильтры: ${filterText}`);
            }

            if (hasSort) {
                const sortLabels = {
                    'id': 'ID',
                    'surname': 'Фамилия',
                    'name': 'Имя',
                    'patronymic': 'Отчество',
                    'phone': 'Телефон'
                };
                const direction = sortOrder === 'asc' ? '↑' : '↓';
                parts.push(`Сортировка: ${sortLabels[sort]} ${direction}`);
            }

            statusText = parts.join(' | ');
        }

        this.statusElement.textContent = statusText;
    }

    saveFilters() {
        localStorage.setItem('clientFilters', JSON.stringify(this.currentFilters));
        localStorage.setItem('clientSort', this.currentSort);
        localStorage.setItem('clientSortOrder', this.currentSortOrder);
    }

    loadSavedFilters() {
        try {
            const savedFilters = localStorage.getItem('clientFilters');
            const savedSort = localStorage.getItem('clientSort');
            const savedSortOrder = localStorage.getItem('clientSortOrder');

            if (savedFilters) {
                this.currentFilters = JSON.parse(savedFilters);

                // Заполняем форму сохраненными значениями
                if (this.currentFilters.surname_prefix) {
                    document.getElementById('surname-filter').value = this.currentFilters.surname_prefix;
                }
                if (this.currentFilters.name_prefix) {
                    document.getElementById('name-filter').value = this.currentFilters.name_prefix;
                }
                if (this.currentFilters.patronymic_prefix) {
                    document.getElementById('patronymic-filter').value = this.currentFilters.patronymic_prefix;
                }
                if (this.currentFilters.phone_substring) {
                    document.getElementById('phone-filter').value = this.currentFilters.phone_substring;
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

    getCurrentFilters() {
        return {
            filters: this.currentFilters,
            sort: this.currentSort,
            sortOrder: this.currentSortOrder
        };
    }
}