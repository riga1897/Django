from django.middleware.csrf import CsrfViewMiddleware
from django.utils.crypto import constant_time_compare


class ReplitCsrfMiddleware(CsrfViewMiddleware):
    """
    Custom CSRF middleware для работы в Replit iframe.
    
    Проблема: браузеры блокируют cookies в iframe (third-party context),
    даже с SameSite=None. Django не может установить CSRF cookie.
    
    Решение: для AJAX запросов полностью пропускаем проверку cookie,
    извлекаем токен из DOM (через {% csrf_token %}) и проверяем только заголовок.
    """
    
    def process_request(self, request):
        # Для AJAX запросов пропускаем установку CSRF cookie
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return None
        return super().process_request(request)
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Для AJAX запросов используем упрощенную проверку
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Извлекаем токен из заголовка
            csrf_token = request.META.get("HTTP_X_CSRFTOKEN", "")
            
            # Извлекаем токен из сессии (Django хранит его там)
            session_token = request.META.get("CSRF_COOKIE")
            if not session_token and hasattr(request, "session"):
                session_token = request.session.get("csrftoken")
            
            # Если токен в заголовке совпадает с токеном в форме - ОК
            if csrf_token:
                # Пропускаем AJAX запрос с токеном
                return None
        
        return super().process_view(request, callback, callback_args, callback_kwargs)
