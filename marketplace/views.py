from django.contrib import messages
from django.shortcuts import render

from marketplace.models import Product


def products_list(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "marketplace/products_list.html", context)


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, "marketplace/product_detail.html", context)


def contacts(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Лог обработки
        print(f"Сообщение от {name}: '{message}'. E-mail: {email}")

        messages.success(request, f"Спасибо, {name}! Ваше сообщение получено.")

    return render(request, "marketplace/contacts.html")