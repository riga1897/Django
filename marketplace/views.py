from typing import Any
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView, View

from marketplace.models import Product

from .forms import ContactForm, ProductForm


class ModalLoginRequiredMixin(LoginRequiredMixin):
    """Mixin для редиректа на модалку логина вместо отдельной страницы"""

    def handle_no_permission(self) -> HttpResponse:  # type: ignore[override]
        """Редирект на главную с открытием модалки логина"""
        next_url = self.request.get_full_path()  # type: ignore[attr-defined]

        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},  # type: ignore[attr-defined]
            require_https=self.request.is_secure(),  # type: ignore[attr-defined]
        ):
            next_url = "/"

        query_params = {"next": next_url, "show_login_modal": "1"}
        return redirect(f"/?{urlencode(query_params)}")


class ProductsListView(ListView):  # type: ignore[type-arg]
    model = Product
    template_name = "marketplace/products_list.html"
    context_object_name = "products"

    def get_queryset(self) -> QuerySet[Product]:  # type: ignore[override]
        """
        Фильтрация товаров:
        - Неавторизованные: только опубликованные
        - Staff/модераторы: все товары
        - Обычные пользователи: опубликованные ИЛИ свои собственные
        """
        user = self.request.user
        if user.is_authenticated and (
            user.is_staff or user.groups.filter(name="Модератор продуктов").exists()
        ):  # type: ignore[attr-defined]
            # Staff или модераторы видят все продукты
            return Product.objects.all()  # type: ignore[attr-defined]
        elif user.is_authenticated:
            # Авторизованные пользователи видят опубликованные ИЛИ свои собственные
            return Product.objects.filter(Q(is_published=True) | Q(owner=user))  # type: ignore[attr-defined]
        else:
            # Неавторизованные видят только опубликованные
            return Product.objects.filter(is_published=True)  # type: ignore[attr-defined]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Проверяем, является ли пользователь модератором
            context["is_moderator"] = (
                user.is_staff or user.groups.filter(name="Модератор продуктов").exists()
            )  # type: ignore[attr-defined]
        else:
            context["is_moderator"] = False
        return context


#    def products_list(request):
#     products = Product.objects.all()
#     context = {"products": products}
#     return render(request, "marketplace/products_list.html", context)


class ProductDetailView(DetailView):
    model = Product
    template_name = "marketplace/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Проверяем, является ли пользователь модератором
            context["is_moderator"] = user.is_staff or user.groups.filter(name="Модератор продуктов").exists()  # type: ignore[attr-defined]
        else:
            context["is_moderator"] = False
        return context


#     def product_detail(request, product_id):
#     product = Product.objects.get(id=product_id)
#     context = {"product": product}
#     return render(request, "marketplace/product_detail.html", context)


class ContactsView(FormView):  # type: ignore[type-arg]
    template_name = "marketplace/contacts.html"
    form_class = ContactForm
    success_url = reverse_lazy("marketplace:contacts")

    def form_valid(self, form: Any) -> HttpResponse:  # type: ignore[override]
        # Данные из формы
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        message = form.cleaned_data["message"]

        # Логика обработки (можно добавить отправку email, сохранение в БД и т.д.)
        print(f"Сообщение от {name} ({email}): '{message}'")

        # Сообщение об успехе
        messages.success(self.request, f"Спасибо, {name}! Ваше сообщение получено.")
        return super().form_valid(form)


class ProductCreateView(ModalLoginRequiredMixin, CreateView):  # type: ignore[type-arg]
    model = Product
    form_class = ProductForm
    template_name = "marketplace/product_form.html"
    success_url = reverse_lazy("marketplace:products_list")

    def get_form(self, form_class: Any = None) -> Any:
        """Скрыть поле owner от обычных пользователей"""
        form = super().get_form(form_class)
        user = self.request.user
        # Только модераторы могут выбирать владельца
        if not (
            user.is_staff or user.groups.filter(name="Модератор продуктов").exists()
        ):  # type: ignore[attr-defined]
            form.fields.pop("owner", None)
        return form

    def form_valid(self, form: Any) -> HttpResponse:  # type: ignore[override]
        # Назначаем владельца перед сохранением, если он не указан
        if not form.cleaned_data.get("owner"):
            form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductUpdateView(ModalLoginRequiredMixin, UpdateView):  # type: ignore[type-arg]
    model = Product
    form_class = ProductForm
    template_name = "marketplace/product_form.html"

    def get_form(self, form_class: Any = None) -> Any:
        """Модератор видит только owner, обычный владелец - все поля кроме owner"""
        form = super().get_form(form_class)
        user = self.request.user
        is_owner = self.object.owner == user
        is_moderator = user.is_staff or user.groups.filter(name="Модератор продуктов").exists()  # type: ignore[attr-defined]

        if is_moderator:
            # Модератор может изменять только владельца (даже если он сам владелец)
            fields_to_remove = [field for field in form.fields if field != "owner"]
            for field in fields_to_remove:
                form.fields.pop(field)
        elif is_owner:
            # Обычный владелец (не модератор) может редактировать все поля, кроме owner
            form.fields.pop("owner", None)

        return form

    def get_queryset(self) -> Any:
        """Владелец может редактировать свой продукт, модератор - любой"""
        user = self.request.user
        if user.is_staff or user.groups.filter(name="Модератор продуктов").exists():  # type: ignore[attr-defined]
            # Модераторы видят все продукты
            return Product.objects.all()  # type: ignore[attr-defined]
        else:
            # Обычный пользователь видит только свои
            return Product.objects.filter(owner=user)  # type: ignore[attr-defined,misc]

    def get_success_url(self) -> str:
        return str(reverse_lazy("marketplace:product_detail", kwargs={"pk": self.object.pk}))


class ProductDeleteView(ModalLoginRequiredMixin, DeleteView):  # type: ignore[type-arg]
    model = Product
    template_name = "marketplace/product_confirm_delete.html"
    success_url = reverse_lazy("marketplace:products_list")

    def get_queryset(self) -> QuerySet[Product]:  # type: ignore[override]
        """Владелец ИЛИ модератор с группой 'Модератор продуктов' может удалить"""
        user = self.request.user
        if user.groups.filter(name="Модератор продуктов").exists():  # type: ignore[attr-defined]
            # Модератор видит все продукты
            return Product.objects.all()  # type: ignore[attr-defined]
        else:
            # Обычный пользователь видит только свои
            return Product.objects.filter(owner=user)  # type: ignore[attr-defined,misc]


class ProductTogglePublishView(LoginRequiredMixin, View):
    """Переключение статуса публикации продукта (для владельца или модератора)"""

    def post(self, request: Any, pk: int) -> HttpResponse:
        product = get_object_or_404(Product, pk=pk)

        # Проверка: пользователь должен быть владельцем ИЛИ иметь разрешение модератора
        user = request.user
        is_owner = product.owner == user
        is_moderator = user.has_perm("marketplace.can_unpublish_product")

        if not (is_owner or is_moderator):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("У вас нет прав для изменения статуса публикации этого товара")

        product.is_published = not product.is_published
        product.save()
        return redirect("marketplace:products_list")
