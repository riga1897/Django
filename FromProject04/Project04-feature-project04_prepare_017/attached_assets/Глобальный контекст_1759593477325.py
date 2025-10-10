# context.py
import contextvars

current_context: contextvars.ContextVar[Optional[RequestContext]] = contextvars.ContextVar(
    'current_context', default=None
)


# decorators.py
def with_context(ctx: RequestContext):
    """Декоратор для установки контекста выполнения."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            token = current_context.set(ctx)
            try:
                return await func(*args, **kwargs)
            finally:
                current_context.reset(token)
        return async_wrapper
    return decorator


# implementations/cache.py
class Cache:
    async def get(self, key: str):
        # Получаем контекст из глобальной переменной контекста
        ctx = current_context.get()
        if ctx is None:
            raise RuntimeError("Контекст не установлен")
            
        scoped_key = f"{ctx.source_id}:{key}"
        return await self._backend.get(scoped_key)


# core/app.py
class App:
    @with_context(RequestContext(source_id="source_alpha"))  # Контекст устанавливается здесь
    async def process_data_alpha(self, query: str):
        data = await self.api_client.fetch_data(query)  # Методы сами достают source_id из контекста
        return await self.cache.get(query)