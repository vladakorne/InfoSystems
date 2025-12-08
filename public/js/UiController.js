class UiController {
    constructor(repository, tableView, detailView) {
        this.repository = repository;
        this.tableView = tableView;
        this.detailView = detailView;

        console.log('UiController создан');
    }


    init() {
        console.log('Начало инициализации UiController');

        // Привязываем обработчик выбора клиента
        this.tableView.bindSelect((id) => {
            console.log('Выбран клиент с ID:', id);
            this.detailView.showLoading(id);
            this.repository.loadClientDetails(id);
        });

        // Привязываем обработчик обновления
        this.tableView.bindRefresh(() => {
            console.log('Запрос на обновление списка клиентов');
            this.repository.loadClients();
        });

        // Подписываемся на события репозитория
        this.repository.subscribe("clientsLoaded", (payload) => {
            console.log('Событие: clientsLoaded', payload);
            this.tableView.render(payload);
        });

        this.repository.subscribe("clientLoaded", (client) => {
            console.log('Событие: clientLoaded', client);
            this.detailView.show(client);
        });

        this.repository.subscribe("errorOccurred", (error) => {
            console.error('Событие: errorOccurred', error);
            if (error.type === 'clients_list') {
                this.tableView.showStatus(`Ошибка: ${error.message}`);
            } else {
                this.detailView.showError(error.message);
            }
        });

        // Загружаем начальные данные
        console.log('Запуск загрузки клиентов...');
        this.repository.loadClients();

        console.log('UiController инициализирован успешно');
    }
}