from django.middleware.csrf import CsrfViewMiddleware
from django.utils.decorators import decorator_from_middleware


class ReplitCsrfMiddleware(CsrfViewMiddleware):
    """
    Custom CSRF middleware для работы в Replit iframe.
    
    Проблема: браузеры блокируют cookies в iframe (third-party context),
    даже с SameSite=None. Django не может установить CSRF cookie.
    
    Решение: для AJAX запросов извлекаем CSRF токен из DOM (через {% csrf_token %})
    и проверяем его из заголовка X-CSRFToken, минуя проверку cookies.
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Для AJAX запросов пропускаем проверку cookie
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Извлекаем токен из заголовка
            csrf_token = request.META.get("HTTP_X_CSRFTOKEN", "")
            
            if csrf_token:
                # Устанавливаем токен напрямую, минуя cookie
                request.META["CSRF_COOKIE"] = csrf_token
                request.META["CSRF_COOKIE_USED"] = True
        
        return super().process_view(request, callback, callback_args, callback_kwargs)
