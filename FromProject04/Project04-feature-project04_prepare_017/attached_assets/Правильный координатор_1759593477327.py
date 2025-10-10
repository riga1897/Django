# ДЕЛАЙТЕ ТАК
class App:
    """Основной класс приложения, orchestrating все компоненты."""

    def __init__(
        self,
        cache: AbstractCache,          # Компонент "Кэш"
        database: AbstractDatabase,    # Компонент "База данных"
        paginator: AbstractPaginator,  # Компонент "Пагинатор"
        logger: AbstractLogger,        # Компонент "Логгер"
        # ... другие зависимости ...
    ) -> None:
        self._cache = cache
        self._database = database
        self._paginator = paginator
        self._logger = logger

    async def get_data(self, query: str):
        # Делегирует работу кэшу и пагинатору
        cached_data = await self._cache.get(query)
        if cached_data:
            return cached_data
        
        data = await self._paginator.fetch(query)
        await self._cache.set(query, data)
        return data

    async def shutdown(self):
        # Делегирует закрытие ресурсов соответствующим компонентам
        await self._database.close()
        await self._cache.close()