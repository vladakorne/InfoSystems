/**
 * Контроллер для управления фильтрацией и сортировкой
 */
class FilterController {
    constructor(filterForm, resetButton, statusElement, uiController) {
        this.filterForm = filterForm; //HTML форма с полями фильтрации
        this.resetButton = resetButton; // сброс
        this.statusElement = statusElement; // элемент отображения статуса фильтра/сортировки
        this.uiController = uiController; // контроллер для передачи команд
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';
    }

    init() {
        // обработка отправки формы фильтрации
        this.filterForm.addEventListener('submit', (e) => {
            e.preventDefault(); // предотвращаем перезагрузку страницы
            this.applyFilters(); // применяем фильтры
        });

        // обработка сброса фильтров
        this.resetButton.addEventListener('click', () => {
            this.resetFilters();
        });

        // загружаем сохраненные фильтры из localStorage
        this.loadSavedFilters();
    }

    applyFilters() {
        // получаем значения из формы
        // через поиск элемеентов получаем значения полей, удаляем по краям пробелы
        const filters = {
            surname_prefix: document.getElementById('surname-filter').value.trim(),
            name_prefix: document.getElementById('name-filter').value.trim(),
            patronymic_prefix: document.getElementById('patronymic-filter').value,
            phone_substring: document.getElementById('phone-filter').value.trim()
        };

        // получаем сортировку
        const sortBy = document.getElementById('sort-filter').value;
        const sortOrder = document.getElementById('sort-order').value;

        // убираем пустые фильтры
        Object.keys(filters).forEach(key => { // получаем массив ключей объекта и перебираем каждый ключ
            if (!filters[key]) {
                delete filters[key]; // удаляет св-во из объекта, если значение пустое
            }
        });

        // сохраняем текущие фильтры
        this.currentFilters = filters;
        this.currentSort = sortBy;
        this.currentSortOrder = sortOrder;

        // сохраняем в localStorage
        this.saveFilters();

        // обновляем статус
        this.updateStatus();

        // применяем фильтры через контроллер
        this.uiController.applyFilters(filters, sortBy, sortOrder);
    }

    resetFilters() {
        // сбрасываем форму
        this.filterForm.reset();

        // сбрасываем текущие фильтры
        this.currentFilters = {};
        this.currentSort = '';
        this.currentSortOrder = 'asc';

        // очищаем localStorage
        localStorage.removeItem('clientFilters');
        localStorage.removeItem('clientSort');
        localStorage.removeItem('clientSortOrder');

        // обновляем статус
        this.updateStatus();

        // применяем сброс через контроллер
        this.uiController.resetFilters();
    }

    updateStatus() {
        // получаем текущие параметтры для формирования статуса
        const filters = this.currentFilters;
        const sort = this.currentSort;
        const sortOrder = this.currentSortOrder;

        const activeFilters = Object.entries(filters).filter(([_, value]) => value);  //преобразует объект в массив пар [ключ, значение], фильтруем пары, игнорируем первое знач
        const hasFilters = activeFilters.length > 0;
        const hasSort = !!sort;

        let statusText = ''; // переменная статуса

        if (!hasFilters && !hasSort) {
            statusText = 'Фильтры не применены';
        } else {
            const parts = [];

            if (hasFilters) {
                const filterText = activeFilters.map(([key, value]) => {
                    const labels = { // маппинг API ключей на русские названия
                        surname_prefix: 'Фамилия',
                        name_prefix: 'Имя',
                        patronymic_prefix: 'Отчество',
                        phone_substring: 'Телефон'
                    };
                    if (key === 'patronymic_prefix') {
                        return `${labels[key]}: ${value === 'yes' ? 'есть' : 'нет'}`;
                    }
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

        this.statusElement.textContent = statusText; // установка в элемент статуса
    }

    // сохранение текущих параметров
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
                this.currentFilters = JSON.parse(savedFilters); // строку преобразовали обратно в объект

                // заполняем форму сохраненными значениями
                if (this.currentFilters.surname_prefix) {
                    document.getElementById('surname-filter').value = this.currentFilters.surname_prefix;
                }
                if (this.currentFilters.name_prefix) {
                    document.getElementById('name-filter').value = this.currentFilters.name_prefix;
                }
                if (this.currentFilters.patronymic_prefix) {
                    // Устанавливаем значение select
                    const patronymicSelect = document.getElementById('patronymic-filter');
                    patronymicSelect.value = this.currentFilters.patronymic_prefix;
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
}