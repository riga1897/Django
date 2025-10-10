"""
Middleware для проверки активности пользователя.
"""

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class CheckUserActiveMiddleware:
    """
    Middleware для проверки активности аутентифицированного пользователя.

    Если пользователь заблокирован (is_active=False), выполняется logout
    и перенаправление на страницу входа с сообщением.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            messages.error(request, "Ваш аккаунт заблокирован. Обратитесь к администратору.")
            return redirect(reverse("login"))

        response = self.get_response(request)
        return response
