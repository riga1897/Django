from django.contrib import messages
from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def contacts(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # Лог обработки
        print(f"Сообщение от {name}: {message}. Phone: {phone}")

        messages.success(request, f"Спасибо, {name}! Ваше сообщение получено.")

        # Стандартный редирект (код 302)
        # return redirect("/")

    return render(request, "contacts.html")
