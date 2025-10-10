# abstractions/context.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestContext:
    """Контекст выполнения, содержащий информацию об источнике запроса."""
    source_id: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None


# implementations/api_client.py
class ApiClient:
    async def fetch_data(self, ctx: RequestContext, query: str):
        # Логируем с контекстом
        self._logger.info("Запрос к API", extra={"source_id": ctx.source_id})
        # Можно добавить source_id как заголовок запроса
        headers = {'X-Source-ID': ctx.source_id}
        ...


# core/app.py
class App:
    async def process_data(self, query: str, source_id: str):
        # Создаем контекст один раз в точке входа
        ctx = RequestContext(source_id=source_id)
        
        data = await self.api_client.fetch_data(ctx, query)
        cached = await self.cache.get(ctx, query) 
        result = self.deduplicator.deduplicate(ctx, data)
        return result