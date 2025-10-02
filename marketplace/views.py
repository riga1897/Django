from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView, DetailView

from marketplace.models import Product
from .forms import ContactForm


class ProductsListView(ListView):
    model = Product
    # app_name/<model_name>_<action>
    # context = {"object_list": products}
    template_name = "marketplace/products_list.html"
    context_object_name = "products"


#    def products_list(request):
#     products = Product.objects.all()
#     context = {"products": products}
#     return render(request, "marketplace/products_list.html", context)

class ProductDetailView(DetailView):
    model = Product
    template_name = "marketplace/product_detail.html"
    context_object_name = "product"


#     def product_detail(request, product_id):
#     product = Product.objects.get(id=product_id)
#     context = {"product": product}
#     return render(request, "marketplace/product_detail.html", context)


class ContactsView(FormView):
    template_name = "marketplace/contacts.html"
    form_class = ContactForm
    success_url = reverse_lazy('marketplace:contacts')

    def form_valid(self, form):
        # Данные из формы
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        # Логика обработки (можно добавить отправку email, сохранение в БД и т.д.)
        print(f"Сообщение от {name} ({email}): '{message}'")

        # Сообщение об успехе
        messages.success(self.request, f"Спасибо, {name}! Ваше сообщение получено.")
        return super().form_valid(form)

# def contacts(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         message = request.POST.get("message")
#
#         # Лог обработки
#         print(f"Сообщение от {name}: '{message}'. E-mail: {email}")
#
#         messages.success(request, f"Спасибо, {name}! Ваше сообщение получено.")
#
#     return render(request, "marketplace/contacts.html")
